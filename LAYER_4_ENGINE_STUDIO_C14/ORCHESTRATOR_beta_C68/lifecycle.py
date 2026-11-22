"""Serialized lifecycle worker invocation for the managed generation lane."""
import json
import os
import signal
import subprocess
import sys
import threading

from .jobs import ENGINE, FIELDS

LIFECYCLE_DEADLINE_SECONDS = 300
LIFECYCLE_WAIT_SECONDS = 610
LIFECYCLE_TOOLS = frozenset({"atom_lifecycle_create_draft", "atom_lifecycle_update",
                             "atom_lifecycle_promote_draft", "atom_lifecycle_change_status", "atom_lifecycle_archive"})


class LifecycleJobs:
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

    def _run_lifecycle(self, job):
        env = {key: value for key, value in os.environ.items() if key != "PYTHONHOME"}
        env["PYTHONPATH"] = str(ENGINE)
        with self.lock:
            if self.stopping.is_set():
                raise RuntimeError("Orchestrator is stopping")
            process = subprocess.Popen(
                [sys.executable, "-B", "-P", "-m", "WORKERS_beta_C69.lifecycle_worker"],
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, cwd=ENGINE, env=env, start_new_session=True)
            self.process = process
        try:
            stdout, stderr = process.communicate(json.dumps({"binding": self.binding, "name": job["name"],
                                                            "arguments": job["arguments"]}),
                                                 timeout=LIFECYCLE_DEADLINE_SECONDS)
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
        outcome = json.loads(stdout)
        if not isinstance(outcome, dict) or not isinstance(outcome.get("outcome"), str):
            raise ValueError("Lifecycle worker returned an invalid outcome")
        return outcome

    def _execute_lifecycle(self, job):
        lifecycle = None
        try:
            lifecycle = self._run_lifecycle(job)
        except (OSError, ValueError, TypeError, RuntimeError) as error:
            sys.stderr.write("Lifecycle write outcome unknown: " + str(error)[-2048:] + "\n")
        generation = self._generate()
        if generation["state"] == "succeeded":
            projection = {"state": "ready", "generation": generation["generation"]}
        else:
            projection = {"state": "failed", "error": {"code": "projection_refresh_failed",
                          "message": generation.get("message", "Generation failed")}}
        return {"lifecycle": lifecycle, "write_state": "known" if lifecycle is not None else "unknown",
                "projection": projection}

