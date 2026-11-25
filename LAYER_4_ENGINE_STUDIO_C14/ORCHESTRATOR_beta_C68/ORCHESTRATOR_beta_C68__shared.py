"""Private, single-build Orchestrator for the pinned beta Worker."""
from __future__ import annotations

import http.client
import os
import tempfile
import threading
import time
from pathlib import Path

from .abort import AbortJobs, WorkerAborted
from .flow import Flow, safe_target
from .generation import (
    DeltaRequiresReconciliation,
    GenerationBaseChanged,
    WorkerIngestionFailure,
    admit_generation,
    confirm_reuse,
    read_reuse,
    replace_ingestion_issues,
    ticket_delta_paths,
    wait_build,
)
from .archive_jobs import ARCHIVE_RECONCILIATION, ArchiveCoverageLost, ArchiveInputsChanged, ArchiveJobs
from .generation_worker import (
    GENERATION_ERRORS,
    ForegroundCoverageLost,
    ForegroundInputsChanged,
    GenerationWorker,
)
from .jobs import FIELDS, Jobs, QueuedJobs, _GenerationJob, _Run
from .lifecycle import LifecycleJobs
from .retry import COVERAGE_RECOVERED, CurrentnessRetry as CurrentnessRetry, source_changed
from .server import Handler, Server, main
from .startup_checkpoint import CHECKPOINT_FIELDS, ReuseRecord
from .watcher_diagnostics import FOREGROUND_FENCE_MESSAGE, emit_record
from .watcher_poll import PollComplete

__all__ = [
    "ArchiveCoverageLost", "ArchiveInputsChanged", "DeltaRequiresReconciliation",
    "GenerationJobs", "Handler", "PollComplete", "Server", "WorkerIngestionFailure",
]


class GenerationJobs(ArchiveJobs, GenerationWorker, AbortJobs, LifecycleJobs, QueuedJobs, Jobs):
    def __init__(self, instance_id, binding, database_socket, watch_code=False,
                 worker_socket=None, worker_load_seconds=None, *, skip_archives=False):
        super().__init__(instance_id)
        if not isinstance(binding, dict) or set(binding) != FIELDS - {"instance_id"}:
            raise ValueError("Invalid binding fields")
        if not all(isinstance(value, str) and value for value in binding.values()):
            raise ValueError("Invalid binding values")
        self.binding = binding
        self.database_socket = database_socket
        self.worker_socket = worker_socket
        self.worker_load_seconds = worker_load_seconds
        self.skip_archives = skip_archives
        self.worker_mode = None
        self.stopping = threading.Event()
        self.process = None
        self.warm_capture = None
        self.aborted_run = None
        from .watcher import SourceWatcher
        root = Path(binding["root"])
        self.watcher = SourceWatcher(root, root / binding["control_root"], watch_code=watch_code,
                                     defer_archives=True)
        self.thread = None
        self.pending = None
        self.inflight = None
        self.generation_reuse = None
        self.flow = None
        self.flow_context = None
        self.startup_capture = False
        self._initialize_archive()

    def start(self):
        self.watcher.start()
        self.startup_capture = self.startup_replay = True
        self.thread = threading.Thread(target=self._watch, daemon=True)
        self.thread.start()

    def close(self):
        self.stopping.set()
        with self.lock:
            for job in (self.pending, self.inflight, self.lifecycle_job):
                if job is not None:
                    job.event.set()
        self.watcher.close()
        self._close_archive()
        with self.lock:
            try:
                self._stop_worker()
            except OSError:
                pass
        if self.thread is not None and self.thread.is_alive():
            self.thread.join(1)

    def build(self, request):
        if not isinstance(request, dict) or set(request) not in (FIELDS, FIELDS | {"refresh_target"}):
            return 400, {"error": {"code": "invalid_request", "message": "Invalid build fields"}}
        target = request.get("refresh_target")
        if "refresh_target" in request and (not isinstance(target, str) or not target):
            return 400, {"error": {"code": "invalid_request", "message": "Invalid refresh target"}}
        if request["instance_id"] != self.instance_id:
            return 409, {"error": {"code": "instance_mismatch", "message": "Instance does not match"}}
        if {key: request[key] for key in FIELDS - {"instance_id"}} != self.binding:
            return 409, {"error": {"code": "binding_mismatch", "message": "Binding does not match"}}
        with self.lock:
            if self.stopping.is_set():
                return 503, {"error": {"code": "orchestrator_stopping", "message": "Orchestrator is stopping"}}
            job = self.inflight or self.pending
            if job is not None and job.target != target:
                return 409, {"error": {"code": "build_active", "message": "Another refresh is active"}}
            if job is None:
                job = self.pending = _GenerationJob(target=target)
                self.watcher.queue.put({})
            request_time = time.time()
            if job is self.inflight and self.flow is not None:
                self.flow.input("rebuild_request", target=safe_target(target), detail={"coalesced": True}, at=request_time, trigger=False)
            elif len(job.requests) < 200:
                job.requests.append(request_time)
            else:
                job.omitted_requests += 1
        return self._wait_build(job)

    def _wait_build(self, job):
        return wait_build(job, None)

    def _watch(self):
        self.generation_reuse = read_reuse(self.database_socket, self.instance_id)
        self._watch_queue()

    def _flow_effect(self, name, **values):
        if self.flow is not None:
            targets = {"worker_request": "C69", "worker_started": "C69",
                       "generation_admission": "C71", "generation_reuse_check": "C71",
                       "generation_reuse_write": "C68.generation_reuse"}
            self.flow.add("effect", name, target=targets[name], **values)

    def _attempt_generation(self, target, reuse, paths=None, *, reconciliation=False, strict=False):
        with tempfile.TemporaryDirectory(prefix="anechoic-generation-") as temporary:
            directory = str(Path(temporary).resolve(strict=True))
            started = time.monotonic()
            explicit = target is not None or self.inflight is not None
            if explicit or (self.skip_archives and self.startup_capture):
                reuse = paths = None
            if self.skip_archives and paths and any(self._is_archive_path(str(Path(self.binding["root"]) / path))
                                                    for path in paths):
                paths = None
            result, reuse, options = self._capture_generation(
                directory, reuse, paths, explicit=explicit, reconciliation=reconciliation, strict=strict)
            deferred = result.pop("deferred_archive", None)
            if self.skip_archives:
                deferred = None
            if deferred is None and options.get("incremental") and not self.skip_archives:
                deferred = self._restart_archive(reuse, result)
            if deferred and (deferred["roots"] or deferred["snapshot"]["atoms"]
                             or deferred["snapshot"].get("ingestion_issues") or "checkpoint" in deferred):
                result["archive_pending"] = True
            if self.skip_archives and "paths" in result and any(
                    atom["status_group"] == "Archived" for atom in result["snapshot"]["atoms"]):
                raise DeltaRequiresReconciliation("Archived Atom requires foreground capture")
            if self.deferred_archive and paths is not None and deferred is None and self._needs_foreground(result):
                raise DeltaRequiresReconciliation("Archive paths require foreground capture")
            captured = time.monotonic()
            witness = result.get("reuse", reuse)
            if result.get("reuse", True) is None:
                del result["reuse"]
            admitted = self._admit_live_result(directory, result, target, witness)
            admitted.update(worker_seconds=captured - started, admission_seconds=time.monotonic() - captured)
            if "paths" in result:
                admitted["delta_path_count"] = len(result["paths"])
        self._accept_live_generation(admitted["generation"], result, deferred)
        if witness is not None:
            self.generation_reuse = ReuseRecord.model_validate({
                **{key: value for key, value in witness.items() if key not in CHECKPOINT_FIELDS},
                "base_generation": admitted["generation"]})
            self._flow_effect("generation_reuse_write", outcome="succeeded", detail={"state": "stored"})
        return {"state": "succeeded", **admitted}

    def _admit_live_result(self, directory, result, target, witness):
        unchanged = "unchanged" in result
        effect = "generation_reuse_check" if unchanged else "generation_admission"
        timed = self.startup_capture and os.environ.get("ANECHOIC_STARTUP_TIMING") == "1"
        if timed:
            from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import mark_startup_timing
        try:
            admitted = (confirm_reuse(self.database_socket, self.instance_id, result) if unchanged
                        else admit_generation(self.database_socket, self.instance_id, directory, result, target))
        except Exception:
            self._flow_effect(effect, outcome="failed")
            raise
        if timed and "kind" in admitted:
            archive = "disabled" if self.skip_archives else "deferred" if result.get("archive_pending") is True else "none"
            mark_startup_timing("non_archived_load_ended", mode=admitted["kind"], archive=archive)
        if unchanged:
            self._flow_effect(effect, outcome="succeeded")
            self._record_ingestion_issues("build", [])
        else:
            self._flow_effect(effect, outcome="succeeded", detail={"reuse_proof_present": witness is not None})
        return admitted

    def _start_flow(self, target, changes, startup):
        self.flow = Flow(self.instance_id, self.database_socket)
        context, self.flow_context = self.flow_context or {}, None
        job = context.get("job")
        if context.get("startup") or startup:
            self.flow.input("startup")
        if job is not None:
            for index, at in enumerate(job.requests):
                self.flow.input("rebuild_request", target=safe_target(target),
                                detail={"coalesced": index > 0}, at=at, trigger=index == 0)
            job.requests.clear()
            self.flow.omitted += job.omitted_requests
        file_inputs = []
        for change in context.get("changes", changes):
            if change:
                observed_at = change.get("observed_at")
                detail = {"event_type": change.get("event_type")}
                if observed_at is not None:
                    detail["timestamp_source"] = "watcher"
                index = self.flow.add("input", "file_change", causes=[], detail=detail, at=observed_at)
                if index is not None:
                    file_inputs.append(index)
        if file_inputs:
            trigger = self.flow.add("trigger", "file_change", causes=file_inputs)
            if trigger is not None:
                self.flow.causes.append(trigger)
        if context.get("retry"):
            self.flow.input("retry_due")
        if context.get("lifecycle"):
            self.flow.input("lifecycle_refresh")
        return job

    def _generation_reuse(self, target, changes, startup):
        reuse = self.generation_reuse if target is None and (startup or any(changes)) else None
        if self.startup_capture and not startup and target is None and self.inflight is None and reuse is None:
            reuse = read_reuse(self.database_socket, self.instance_id)
        return reuse.model_dump(exclude_unset=True) if isinstance(reuse, ReuseRecord) else reuse

    def _generate(self, target=None, *, changes=(), startup=False):
        with self.lock:
            job = self._start_flow(target, changes, startup)
            self.active = _Run(state="running", started_at=time.time(), run_id=self.flow.run_id)
            self.aborted_run = None
            self.worker_mode = None
        reuse = self._generation_reuse(target, changes, startup)
        self.generation_reuse = None
        self._flow_effect("generation_reuse_write", outcome="succeeded", detail={"state": "cleared"})
        outcome = {"state": "failed", "code": "generation_failed"}
        try:
            outcome = self._attempt_with_recovery(target, reuse, changes)
        except WorkerAborted:
            outcome = {"state": "aborted", "code": "worker_aborted", "message": "Worker aborted"}
        except GENERATION_ERRORS as error:
            outcome["message"] = str(error)[-2048:]
            if (self.startup_capture or self.startup_replay) and source_changed(outcome):
                outcome["retrying"] = True
            self._record_ingestion_failure(error.__cause__ if isinstance(error, ForegroundInputsChanged) else error)
        finally:
            with self.lock:
                self.latest = _Run(**(self.active.model_dump(exclude_unset=True) | outcome), finished_at=time.time())
                if self.worker_mode is not None:
                    self.latest.worker_mode = self.worker_mode
                self.active = None
                flow = self.flow
                if job is None:
                    self.flow = None
            if job is None:
                flow.finish(outcome)
        return outcome

    def _attempt_with_recovery(self, target, reuse, changes):
        paths = ticket_delta_paths(self.binding, changes) if reuse is not None and not self.startup_capture else None
        event_types = {change.get("event_type") for change in changes if change}
        try:
            try:
                if ARCHIVE_RECONCILIATION in event_types:
                    outcome = self._attempt_generation(target, reuse, reconciliation=True, strict=True)
                elif COVERAGE_RECOVERED in event_types:
                    outcome = self._attempt_generation(target, None, strict=True)
                else:
                    outcome = self._attempt_generation(target, reuse, paths)
            except GenerationBaseChanged:
                outcome = self._attempt_generation(target, None)
            except DeltaRequiresReconciliation:
                if reuse is None:
                    raise
                witness = {key: value for key, value in reuse.items() if key not in CHECKPOINT_FIELDS}
                outcome = self._attempt_generation(target, witness, reconciliation=True)
        except ForegroundCoverageLost:
            if self.stopping.is_set():
                raise WorkerAborted("Worker aborted")
            outcome = self._attempt_generation(target, None, strict=True)
        return outcome

    def _record_ingestion_failure(self, error):
        message = str(error)[-8192:] or type(error).__name__
        if message != FOREGROUND_FENCE_MESSAGE:
            severity = "ERROR" if self.startup_capture and not isinstance(error, (ValueError, WorkerIngestionFailure)) else "WARNING"
            emit_record(severity, "generation_failed", "generation", "failed", (self.active.run_id if self.active else None))
        if isinstance(error, WorkerIngestionFailure):
            self._record_ingestion_issues(error.diagnostic["source"], error.diagnostic["issues"],
                                          model_diagnostics=error.model_diagnostics)
            return
        self._record_ingestion_issues("build", [{
            "relative_path": None, "code": "generation_failed", "message": message,
            "atom_ref": None, "related_paths": [],
        }])

    def _record_ingestion_issues(self, source, issues, *, model_diagnostics=None):
        try:
            options = {} if model_diagnostics is None else {"model_diagnostics": model_diagnostics}
            replace_ingestion_issues(self.database_socket, self.instance_id, source, issues, **options)
        except (OSError, RuntimeError, http.client.HTTPException):
            emit_record("WARNING", "ingestion_issues_unavailable", "record_ingestion_issues", "degraded",
                        (self.active.run_id if self.active else None), details={"source": source})
if __name__ == "__main__":
    raise SystemExit(main())
