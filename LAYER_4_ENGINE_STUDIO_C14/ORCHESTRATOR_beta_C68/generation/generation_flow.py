"""Sequence generation flows, retries and diagnostics."""

from http.client import HTTPException
import time

from ORCHESTRATOR_beta_C68.abort import WorkerAborted
from ORCHESTRATOR_beta_C68.archive_operations.archive_jobs import ARCHIVE_RECONCILIATION
from ORCHESTRATOR_beta_C68.generation.worker.flow import Flow, safe_target
from ORCHESTRATOR_beta_C68.generation.generation import replace_ingestion_issues, ticket_delta_paths
from ORCHESTRATOR_beta_C68.generation.generation_admission import (
    CompilerColumnsChanged,
    DeltaRequiresReconciliation,
    GenerationBaseChanged,
    WorkerIngestionFailure,
)
from ORCHESTRATOR_beta_C68.generation.worker.generation_worker import (
    GENERATION_ERRORS,
    ForegroundCoverageLost,
    ForegroundInputsChanged,
)
from ORCHESTRATOR_beta_C68.jobs import _Run
from ORCHESTRATOR_beta_C68.watching.retry import COVERAGE_RECOVERED, source_changed
from ORCHESTRATOR_beta_C68.generation.worker.checkpoint.startup_checkpoint import CHECKPOINT_FIELDS, ReuseRecord
from ORCHESTRATOR_beta_C68.watching.poll_coverage.watcher_diagnostics import FOREGROUND_FENCE_MESSAGE, emit_record


class GenerationFlow:
    def _start_flow(self, target, changes, startup):
        self.flow = Flow(self.instance_id, self.database_socket)
        context, self.flow_context = self.flow_context or {}, None
        job = context.get("job")
        if context.get("startup") or startup:
            self.flow.input("startup")
        if job is not None:
            for index, at in enumerate(job.requests):
                self.flow.input(
                    "rebuild_request",
                    target=safe_target(target),
                    detail={"coalesced": index > 0},
                    at=at,
                    trigger=index == 0,
                )
            job.requests.clear()
            self.flow.omitted += job.omitted_requests
        self._add_file_inputs(context.get("changes", changes))
        if context.get("retry"):
            self.flow.input("retry_due")
        if context.get("lifecycle"):
            self.flow.input("lifecycle_refresh")
        return job

    def _add_file_inputs(self, changes):
        file_inputs = []
        for change in changes:
            if change:
                observed_at = change.get("observed_at")
                detail = {"event_type": change.get("event_type")}
                if observed_at is not None:
                    detail["timestamp_source"] = "watcher"
                index = self.flow.add(
                    "input",
                    "file_change",
                    causes=[],
                    detail=detail,
                    at=observed_at,
                )
                if index is not None:
                    file_inputs.append(index)
        if file_inputs:
            trigger = self.flow.add(
                "trigger", "file_change", causes=file_inputs
            )
            if trigger is not None:
                self.flow.causes.append(trigger)

    def _generation_reuse(self, target, changes, startup):
        reuse = (
            self.generation_reuse
            if (
                target == "realization_graph"
                or target is None
                and (startup or any(changes))
            )
            else None
        )
        if (
            self.startup_capture
            and not startup
            and target is None
            and self.inflight is None
            and reuse is None
        ):
            from ORCHESTRATOR_beta_C68.generation.generation import (
                read_reuse,
            )

            reuse = read_reuse(
                self.database_socket, self.instance_id, scope="foreground"
            )
        return (
            reuse.model_dump(exclude_unset=True)
            if isinstance(reuse, ReuseRecord)
            else reuse
        )

    def _generate(self, target=None, *, changes=(), startup=False):
        with self.lock:
            job = self._start_flow(target, changes, startup)
            self.active = _Run(
                state="running",
                started_at=time.time(),
                run_id=self.flow.run_id,
            )
            self.aborted_run = None
            self.worker_mode = None
        reuse = self._generation_reuse(target, changes, startup)
        self.generation_reuse = None
        self._flow_effect(
            "generation_reuse_write",
            outcome="succeeded",
            detail={"state": "cleared"},
        )
        outcome = {"state": "failed", "code": "generation_failed"}
        try:
            outcome = self._attempt_with_recovery(target, reuse, changes)
        except WorkerAborted:
            outcome = {
                "state": "aborted",
                "code": "worker_aborted",
                "message": "Worker aborted",
            }
        except GENERATION_ERRORS as error:
            outcome["message"] = str(error)[-2048:]
            if isinstance(error, ForegroundCoverageLost):
                outcome["code"] = "watcher_coverage_lost"
            if (
                self.startup_capture or self.startup_replay
            ) and source_changed(outcome):
                outcome["retrying"] = True
            self._record_ingestion_failure(
                error.__cause__
                if isinstance(error, ForegroundInputsChanged)
                else error
            )
        finally:
            self._finish_generation(target, reuse, job, outcome)
        return outcome

    def _finish_generation(self, target, reuse, job, outcome):
        if (
            target == "realization_graph"
            and self.generation_reuse is None
            and reuse is not None
        ):
            self.generation_reuse = ReuseRecord.model_validate(reuse)
        with self.lock:
            self.latest = _Run(
                **(self.active.model_dump(exclude_unset=True) | outcome),
                finished_at=time.time(),
            )
            if self.worker_mode is not None:
                self.latest.worker_mode = self.worker_mode
            self.active = None
            flow = self.flow
            if job is None:
                self.flow = None
        if job is None:
            flow.finish(outcome)

    def _attempt_with_recovery(self, target, reuse, changes):
        paths = (
            ticket_delta_paths(self.binding, changes)
            if reuse is not None and not self.startup_capture
            else None
        )
        event_types = {
            change.get("event_type") for change in changes if change
        }
        try:
            if ARCHIVE_RECONCILIATION in event_types:
                self.archive_reconciliation_pending = False
                return self._attempt_generation(
                    target, reuse, reconciliation=True, strict=True
                )
            if COVERAGE_RECOVERED in event_types:
                return self._recover_watcher_coverage(target)
            return self._attempt_generation(target, reuse, paths)
        except GenerationBaseChanged, CompilerColumnsChanged:
            if target == "realization_graph":
                raise
            return self._attempt_generation(
                target,
                None,
                recover_coverage=COVERAGE_RECOVERED in event_types,
            )
        except DeltaRequiresReconciliation:
            if reuse is None:
                raise
            witness = {
                key: value
                for key, value in reuse.items()
                if key not in CHECKPOINT_FIELDS
            }
            return self._attempt_generation(
                target, witness, reconciliation=True
            )
        except ForegroundCoverageLost:
            if self.stopping.is_set():
                raise WorkerAborted("Worker aborted") from None
            raise

    def _record_ingestion_failure(self, error):
        message = str(error)[-8192:] or type(error).__name__
        if message != FOREGROUND_FENCE_MESSAGE:
            severity = (
                "ERROR"
                if self.startup_capture
                and not isinstance(error, (ValueError, WorkerIngestionFailure))
                else "WARNING"
            )
            emit_record(
                severity,
                "generation_failed",
                "generation",
                "failed",
                (self.active.run_id if self.active else None),
            )
        if isinstance(error, WorkerIngestionFailure):
            self._record_ingestion_issues(
                error.diagnostic["source"],
                error.diagnostic["issues"],
                model_diagnostics=error.model_diagnostics,
            )
            return
        self._record_ingestion_issues(
            "build",
            [
                {
                    "relative_path": None,
                    "code": "generation_failed",
                    "message": message,
                    "atom_ref": None,
                    "related_paths": [],
                }
            ],
        )

    def _record_ingestion_issues(
        self, source, issues, *, model_diagnostics=None
    ):
        try:
            options = (
                {}
                if model_diagnostics is None
                else {"model_diagnostics": model_diagnostics}
            )
            replace_ingestion_issues(
                self.database_socket,
                self.instance_id,
                source,
                issues,
                **options,
            )
        except OSError, RuntimeError, HTTPException:
            emit_record(
                "WARNING",
                "ingestion_issues_unavailable",
                "record_ingestion_issues",
                "degraded",
                (self.active.run_id if self.active else None),
                details={"source": source},
            )
