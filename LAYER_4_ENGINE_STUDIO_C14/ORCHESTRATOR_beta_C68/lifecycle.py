"""Serialized lifecycle worker invocation for the managed generation lane."""
import http.client
from hashlib import sha256
import json
import os
import signal
import subprocess
import sys
import threading

from .generation import admit_generation, read_structure, ticket_allocation
from .jobs import ENGINE, FIELDS
from .warm_worker import WarmLifecycleUnavailable, run_lifecycle

LIFECYCLE_DEADLINE_SECONDS = 300
LIFECYCLE_WAIT_SECONDS = 610
LIFECYCLE_TOOLS = frozenset({"atom_lifecycle_create_draft", "atom_lifecycle_update",
                             "atom_lifecycle_promote_draft", "atom_lifecycle_change_status", "atom_lifecycle_archive",
                             "atom_lifecycle_direct_update", "atom_lifecycle_create_asset"})


def _new_component_task(job):
    args = job["arguments"]
    if job["name"] != "atom_lifecycle_create_draft" or set(args) != {"newAtom"}:
        return False
    values = args["newAtom"]
    if not isinstance(values, dict) or values.get("template") not in ("task", "epic"):
        return False
    container = values.get("container")
    return isinstance(container, dict) and set(container) == {"component"}


class LifecycleJobs:
    unconfirmed_lifecycle_write = False

    def lifecycle(self, request):
        if (not isinstance(request, dict) or set(request) != FIELDS | {"name", "arguments"}
                or not isinstance(request["name"], str) or request["name"] not in LIFECYCLE_TOOLS or not isinstance(request["arguments"], dict)):
            return 400, {"error": {"code": "invalid_request", "message": "Invalid lifecycle fields"}}
        if request["instance_id"] != self.instance_id:
            return 409, {"error": {"code": "instance_mismatch", "message": "Instance does not match"}}
        if {key: request[key] for key in FIELDS - {"instance_id"}} != self.binding:
            return 409, {"error": {"code": "binding_mismatch", "message": "Binding does not match"}}
        with self.lock:
            if self.stopping.is_set():
                return 503, {"error": {"code": "orchestrator_stopping", "message": "Orchestrator is stopping"}}
            if self.lifecycle_job is not None:
                return 409, {"error": {"code": "lifecycle_active", "message": "Another lifecycle operation is active"}}
            job = self.lifecycle_job = {"event": threading.Event(), "outcome": None,
                                        "name": request["name"], "arguments": request["arguments"]}
            self.watcher.queue.put({})
        if not job["event"].wait(LIFECYCLE_WAIT_SECONDS):
            return 504, {"error": {"code": "write_outcome_unknown", "message": "Lifecycle deadline exceeded; outcome is unknown"}}
        if job["outcome"] is None:
            return 503, {"error": {"code": "write_outcome_unknown", "message": "Orchestrator stopped; outcome is unknown"}}
        return 200, {"result": job["outcome"]}

    def _run_lifecycle(self, job, base_generation, structure_sha256, indexed_task=None):
        request = {"binding": self.binding, "name": job["name"], "base_generation": base_generation,
                   "structure_sha256": structure_sha256, "arguments": job["arguments"]}
        if indexed_task is not None:
            request["indexed_task"] = indexed_task
        if indexed_task is not None and self.worker_socket is not None:
            try:
                outcome = run_lifecycle(self.worker_socket, self.worker_load_seconds, request,
                                        self._register_warm_capture, LIFECYCLE_DEADLINE_SECONDS)
            finally:
                with self.lock:
                    self.warm_capture = None
        else:
            outcome = self._run_cold_lifecycle(request)
        if (not isinstance(outcome, dict) or set(outcome) != {"lifecycle", "delta", "projection_error"}
                or not isinstance(outcome["lifecycle"], dict)
                or not isinstance(outcome["lifecycle"].get("outcome"), str)):
            raise ValueError("Lifecycle worker returned an invalid outcome")
        return outcome

    def _run_cold_lifecycle(self, request):
        env = {key: value for key, value in os.environ.items() if key != "PYTHONHOME"}
        env["PYTHONPATH"] = str(ENGINE)
        env["ANECHOIC_BETA_WORKER_PARENT_PID"] = str(os.getpid())
        with self.lock:
            if self.stopping.is_set():
                raise RuntimeError("Orchestrator is stopping")
            process = subprocess.Popen(
                [sys.executable, "-B", "-P", "-m", "WORKERS_beta_C69.lifecycle_worker"],
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, cwd=ENGINE, env=env, start_new_session=True)
            self.process = process
        try:
            stdout, stderr = process.communicate(json.dumps(request), timeout=LIFECYCLE_DEADLINE_SECONDS)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.communicate()
            raise RuntimeError("Lifecycle worker deadline exceeded")
        finally:
            with self.lock:
                self.process = None
        if process.returncode:
            raise RuntimeError("Lifecycle worker failed: " + stderr[-2048:])
        return json.loads(stdout)

    def _execute_lifecycle(self, job):
        reuse = self.generation_reuse
        structure = read_structure(self.database_socket, self.instance_id, reuse)
        if structure is None:
            return {"lifecycle": {"outcome": "failed"}, "write_state": "known",
                    "projection": self._projection_failure("An admitted generation is required for lifecycle writes")}
        base = reuse["base_generation"]
        indexed_task = None
        if _new_component_task(job):
            try:
                if self.unconfirmed_lifecycle_write:
                    raise ValueError("Ticket allocation requires admission of the preceding write")
                number, labels = ticket_allocation(self.database_socket, self.instance_id, base,
                                                   self.binding["project_prefix"])
                indexed_task = {"max_number": number, "component_ids": list(structure["components"]),
                                "manifest_ref": structure["project"]["ref"], "ticket_labels": labels,
                                "endpoints": reuse["endpoints"]}
            except (OSError, ValueError, TypeError, KeyError, http.client.HTTPException) as error:
                return {"lifecycle": {"outcome": "failed"}, "write_state": "known",
                        "projection": self._projection_failure(error)}
        try:
            canonical = json.dumps(structure, sort_keys=True, separators=(",", ":")).encode()
            reply = self._run_lifecycle(job, base, sha256(canonical).hexdigest(), indexed_task)
        except WarmLifecycleUnavailable as error:
            return {"lifecycle": {"outcome": "failed"}, "write_state": "known",
                    "projection": self._projection_failure(error)}
        except (OSError, ValueError, TypeError, RuntimeError) as error:
            self.unconfirmed_lifecycle_write = True
            return {"lifecycle": None, "write_state": "unknown",
                    "projection": self._projection_failure(error)}
        lifecycle = reply["lifecycle"]
        projection = {"state": "ready", "generation": base}
        if reply["projection_error"] is not None:
            projection = self._projection_failure(reply["projection_error"])
        elif reply["delta"] is not None:
            projection = self._admit_lifecycle_delta(reply["delta"], base)
            if projection["state"] == "ready":
                self.watcher.acknowledge(lifecycle.get("effects", []))
        uncertain = any(error.get("code") == "effect_uncertain" for error in lifecycle.get("errors", []))
        if projection["state"] != "ready" and (uncertain or lifecycle.get("effects")):
            self.unconfirmed_lifecycle_write = True
        return {"lifecycle": lifecycle, "write_state": "known", "projection": projection}

    @staticmethod
    def _projection_failure(error):
        return {"state": "failed", "error": {"code": "projection_refresh_failed", "message": str(error)[-2048:]}}

    def _admit_lifecycle_delta(self, delta, base):
        self.flow_context = {"lifecycle": True}
        self._start_flow(None, (), False)
        outcome = {"state": "failed", "code": "projection_refresh_failed"}
        try:
            if (not isinstance(delta, dict) or "paths" not in delta or delta.get("base_generation") != base):
                raise ValueError("Invalid lifecycle delta")
            admitted = admit_generation(self.database_socket, self.instance_id, None, delta, None)
            self.generation_reuse["base_generation"] = admitted["generation"]
            self._flow_effect("generation_admission", outcome="succeeded")
            outcome = {"state": "succeeded", **admitted, "delta_path_count": len(delta["paths"])}
            return {"state": "ready", "generation": admitted["generation"]}
        except (OSError, ValueError, TypeError, KeyError, RuntimeError, http.client.HTTPException) as error:
            self._flow_effect("generation_admission", outcome="failed")
            return self._projection_failure(error)
        finally:
            self.flow.finish(outcome)
            self.flow = None

