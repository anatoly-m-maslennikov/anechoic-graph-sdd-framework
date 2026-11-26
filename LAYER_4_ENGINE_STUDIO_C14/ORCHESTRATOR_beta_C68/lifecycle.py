"""Serialized lifecycle worker invocation for the managed generation lane."""
import http.client
from hashlib import sha256
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
from time import monotonic
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from .generation import admit_generation, read_structure
from .jobs import ENGINE, FIELDS, LifecycleCoveragePending, _LifecycleJob, operation_timeout
from .lifecycle_queries import (
    archive_versions_available, lifecycle_context, needs_exact_archive, requires_project_capture, ticket_allocation,
)
from .warm_worker import WarmLifecycleUnavailable, run_lifecycle

LIFECYCLE_DEADLINE_SECONDS = 300
LIFECYCLE_WAIT_SECONDS = 610
LIFECYCLE_TOOLS = frozenset({"atom_lifecycle_create_draft", "atom_lifecycle_update",
                             "atom_lifecycle_promote_draft", "atom_lifecycle_change_status", "atom_lifecycle_archive",
                             "atom_lifecycle_direct_update", "atom_lifecycle_create_asset"})


class ArchiveHistoryPending(ValueError):
    """The operation requires more than the admitted Archive version checkpoint."""


class _NativeLifecycle(BaseModel):
    model_config = ConfigDict(strict=True, extra="allow", hide_input_in_errors=True)
    outcome: str
    effects: list[Any] = Field(default_factory=list)
    warnings: list[Any] = Field(default_factory=list)
    errors: list[Any] = Field(default_factory=list)
    requested_input: dict[str, dict[str, Any]] = Field(default_factory=dict)


class _LifecycleReply(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid", hide_input_in_errors=True)
    lifecycle: _NativeLifecycle
    delta: dict[str, Any] | None
    projection_error: str | None


def _new_component_task(job):
    args = job.arguments
    if job.name != "atom_lifecycle_create_draft" or set(args) != {"newAtom"}:
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
        if self.skip_archives:
            return 409, {"error": {"code": "archive_disabled", "message": "Lifecycle requires archived Atom history"}}
        archive_versions = self.deferred_archive is not None and self._archive_versions_available()
        with self.lock:
            if self.stopping.is_set():
                return 503, {"error": {"code": "orchestrator_stopping", "message": "Orchestrator is stopping"}}
            if self.startup_replay:
                return 409, {"error": {"code": "startup_replay_pending", "message": "Project startup replay is pending"}}
            if self.startup_capture or self.deferred_archive is not None and not archive_versions:
                return 409, {"error": {"code": "archive_pending", "message": "Archived Atom history is incomplete"}}
            if self.lifecycle_job is not None:
                return 409, {"error": {"code": "lifecycle_active", "message": "Another lifecycle operation is active"}}
            timeout = operation_timeout(LIFECYCLE_WAIT_SECONDS)
            job = self.lifecycle_job = _LifecycleJob(
                deadline=None if timeout is None else monotonic() + timeout,
                name=request["name"], arguments=request["arguments"], archive_versions=archive_versions)
            self.watcher.queue.put({})
        return self._await_lifecycle(job)

    def _archive_versions_available(self):
        try:
            return archive_versions_available(self.database_socket, self.instance_id)
        except (OSError, ValueError, TypeError, KeyError, http.client.HTTPException):
            return False

    def _await_lifecycle(self, job):
        deadline = job.deadline
        job.event.wait(None if deadline is None else max(0, deadline - monotonic()))
        with self.lock:
            if job.outcome is not None:
                return 200, {"result": job.outcome}
            if self.stopping.is_set():
                status, code, message = 503, "orchestrator_stopping", "Orchestrator stopped"
            else:
                status, code, message = 504, "lifecycle_deadline_exceeded", "Lifecycle deadline exceeded"
            if job.started:
                return status, {"error": {"code": "write_outcome_unknown", "message": message + "; outcome is unknown"}}
            if self.lifecycle_job is job:
                self.lifecycle_job = None
                if self.pending is not None:
                    self.watcher.queue.put({})
        return status, {"error": {"code": code, "message": message + "; no lifecycle write was attempted"}}

    def _run_lifecycle(self, job, base_generation, structure_sha256, facts):
        request = {"binding": self.binding, "name": job.name, "base_generation": base_generation,
                   "structure_sha256": structure_sha256, "arguments": job.arguments, **facts}
        if facts and self.worker_socket is not None:
            try:
                outcome = run_lifecycle(self.worker_socket, self.worker_load_seconds, request,
                                        self._register_warm_capture,
                                        operation_timeout(LIFECYCLE_DEADLINE_SECONDS))
            finally:
                with self.lock:
                    self.warm_capture = None
        else:
            outcome = self._run_cold_lifecycle(request)
        try:
            if not isinstance(outcome, dict):
                raise ValueError
            return _LifecycleReply.model_validate(outcome)
        except (ValueError, ValidationError):
            raise ValueError("Lifecycle worker returned an invalid outcome") from None

    def _run_cold_lifecycle(self, request):
        if self.skip_archives:
            raise RuntimeError("archive_disabled: Lifecycle requires archived Atom history")
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
            stdout, stderr = process.communicate(
                json.dumps(request),
                timeout=operation_timeout(LIFECYCLE_DEADLINE_SECONDS),
            )
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

    def _lifecycle_inputs(self, job):
        if self.startup_replay:
            raise ValueError("Project startup replay is pending")
        archive_pending = self.deferred_archive is not None
        if self.startup_capture or archive_pending and not job.archive_versions:
            raise ArchiveHistoryPending("Archived Atom history is incomplete")
        reuse = self.generation_reuse
        if reuse is None:
            raise ValueError("An admitted generation is required for lifecycle writes")
        if self.unconfirmed_lifecycle_write:
            raise ValueError("Lifecycle requires admission of the preceding write")
        self._require_lifecycle_coverage()
        reuse = reuse.model_dump(exclude_unset=True)
        base = reuse["base_generation"]
        if _new_component_task(job):
            structure = read_structure(self.database_socket, self.instance_id, reuse)
            if structure is None:
                raise ValueError("An admitted Structure is required for lifecycle writes")
            number, labels = ticket_allocation(self.database_socket, self.instance_id, base,
                                               self.binding["project_prefix"], archive_versions=job.archive_versions)
            facts = {"max_number": number, "component_ids": list(structure["components"]),
                     "manifest_ref": structure["project"]["ref"], "ticket_labels": labels,
                     "endpoints": reuse["endpoints"]}
            return base, structure, {"indexed_task": facts}
        context = lifecycle_context(self.database_socket, self.instance_id, base, self.binding["project_prefix"],
                                    job.name, job.arguments, archive_versions=job.archive_versions)
        structure = context["structure"]
        full_capture = requires_project_capture(job, context, self.binding["control_root"])
        if archive_pending and (full_capture or needs_exact_archive(job, context)):
            raise ArchiveHistoryPending("Archived Atom history is incomplete")
        if full_capture:
            return base, structure, {}
        return base, structure, {"lifecycle_context": {**context, "endpoints": reuse["endpoints"]}}

    def _require_lifecycle_coverage(self, *, dispatched=False):
        """Check the queue after the epoch so newly restored coverage cannot bypass recovery."""
        managed = self.thread is not None or self.watcher.observer is not None
        if managed and (self.watcher.capture_epoch(dispatched=dispatched) is None or not self.watcher.queue.empty()):
            raise LifecycleCoveragePending()

    def _begin_lifecycle_write(self, job):
        with self.lock:
            deadline = job.deadline
            if (self.stopping.is_set() or self.lifecycle_job is not job
                    or (deadline is not None and monotonic() >= deadline)):
                return False
            self._require_lifecycle_coverage(dispatched=True)
            job.started = True
            return True

    def _execute_lifecycle(self, job):
        try:
            base, structure, facts = self._lifecycle_inputs(job)
        except ArchiveHistoryPending as error:
            return {"lifecycle": {"outcome": "failed", "errors": [{"code": "archive_pending", "message": str(error)}]},
                    "write_state": "known", "projection": {"state": "ready"}}
        except (OSError, ValueError, TypeError, KeyError, http.client.HTTPException) as error:
            return {"lifecycle": {"outcome": "failed"}, "write_state": "known",
                    "projection": self._projection_failure(error)}
        lock = self.watcher.managed_write
        if not lock.acquire(blocking=False):
            raise LifecycleCoveragePending()
        try:
            if not self._begin_lifecycle_write(job):
                return None
            return self._write_lifecycle(job, base, structure, facts)
        finally:
            lock.release()

    def _write_lifecycle(self, job, base, structure, facts):
        try:
            canonical = json.dumps(structure, sort_keys=True, separators=(",", ":")).encode()
            archive_epoch = self.watcher.capture_epoch(archive=True)
            reply = self._run_lifecycle(job, base, sha256(canonical).hexdigest(), facts)
        except WarmLifecycleUnavailable as error:
            return {"lifecycle": {"outcome": "failed"}, "write_state": "known",
                    "projection": self._projection_failure(error)}
        except (OSError, ValueError, TypeError, RuntimeError) as error:
            self.unconfirmed_lifecycle_write = True
            return {"lifecycle": None, "write_state": "unknown",
                    "projection": self._projection_failure(error)}
        lifecycle = reply.lifecycle.model_dump(exclude_unset=True)
        projection = {"state": "ready", "generation": base}
        if reply.projection_error is not None:
            projection = self._projection_failure(reply.projection_error)
        elif reply.delta is not None:
            projection = self._admit_lifecycle_delta(reply.delta, base)
            if projection["state"] == "ready":
                self._acknowledge_lifecycle(lifecycle.get("effects", []), archive_epoch)
        uncertain = any(error.get("code") == "effect_uncertain" for error in lifecycle.get("errors", []))
        if projection["state"] != "ready" and (uncertain or lifecycle.get("effects")):
            self.unconfirmed_lifecycle_write = True
        return {"lifecycle": lifecycle, "write_state": "known", "projection": projection}

    def _acknowledge_lifecycle(self, effects, archive_epoch):
        if self.deferred_archive is not None:
            root = Path(self.binding["root"])
            self.archive_dirty |= any(self._is_archive_path(root / effect["target"]) for effect in effects)
        self.watcher.acknowledge(effects, archive_epoch=archive_epoch)

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
            self.live_generation = self.generation_reuse.base_generation = admitted["generation"]
            self._flow_effect("generation_admission", outcome="succeeded")
            outcome = {"state": "succeeded", **admitted, "delta_path_count": len(delta["paths"])}
            return {"state": "ready", "generation": admitted["generation"]}
        except (OSError, ValueError, TypeError, KeyError, RuntimeError, http.client.HTTPException) as error:
            self._flow_effect("generation_admission", outcome="failed")
            return self._projection_failure(error)
        finally:
            self.flow.finish(outcome)
            self.flow = None

