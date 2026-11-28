"""Private, single-build Orchestrator for the pinned beta Worker."""

from __future__ import annotations

import http as http
from http import client as client
import os as os
import tempfile as tempfile
import threading
import time as time
from pathlib import Path

from ORCHESTRATOR_beta_C68.generation.generation_requests import GenerationRequests
from ORCHESTRATOR_beta_C68.generation.generation_live_capture import GenerationLiveCapture
from ORCHESTRATOR_beta_C68.generation.generation_flow import GenerationFlow
from .abort import AbortJobs, WorkerAborted as WorkerAborted
from ORCHESTRATOR_beta_C68.generation.worker.flow import Flow as Flow, safe_target as safe_target
from ORCHESTRATOR_beta_C68.generation.generation import (
    CompilerColumnsChanged as CompilerColumnsChanged,
    DeltaRequiresReconciliation,
    GenerationBaseChanged as GenerationBaseChanged,
    WorkerIngestionFailure,
    admit_generation as admit_generation,
    confirm_reuse as confirm_reuse,
    live_reuse as live_reuse,
    read_reuse,
    replace_ingestion_issues as replace_ingestion_issues,
    ticket_delta_paths as ticket_delta_paths,
    wait_build as wait_build,
)
from ORCHESTRATOR_beta_C68.archive_operations.archive_jobs import (
    ARCHIVE_RECONCILIATION as ARCHIVE_RECONCILIATION,
    ArchiveCoverageLost,
    ArchiveInputsChanged,
    ArchiveJobs,
)
from ORCHESTRATOR_beta_C68.generation.worker.generation_worker import (
    GENERATION_ERRORS as GENERATION_ERRORS,
    ForegroundCoverageLost as ForegroundCoverageLost,
    ForegroundInputsChanged as ForegroundInputsChanged,
    GenerationWorker,
)
from .jobs import (
    FIELDS,
    Jobs,
    QueuedJobs,
    _GenerationJob as _GenerationJob,
    _Run as _Run,
)
from ORCHESTRATOR_beta_C68.lifecycle.lifecycle import LifecycleJobs
from ORCHESTRATOR_beta_C68.watching.retry import (
    COVERAGE_RECOVERED as COVERAGE_RECOVERED,
    CurrentnessRetry as CurrentnessRetry,
    source_changed as source_changed,
)
from .server import Handler, Server, main
from ORCHESTRATOR_beta_C68.generation.worker.checkpoint.startup_checkpoint import (
    CHECKPOINT_FIELDS as CHECKPOINT_FIELDS,
    ReuseRecord as ReuseRecord,
)
from ORCHESTRATOR_beta_C68.generation.startup_graph import StartupGraphJobs
from ORCHESTRATOR_beta_C68.watching.poll_coverage.watcher_diagnostics import (
    FOREGROUND_FENCE_MESSAGE as FOREGROUND_FENCE_MESSAGE,
    emit_record as emit_record,
)
from ORCHESTRATOR_beta_C68.watching.watcher_poll import PollComplete

__all__ = [
    "ArchiveCoverageLost",
    "ArchiveInputsChanged",
    "DeltaRequiresReconciliation",
    "GenerationJobs",
    "Handler",
    "PollComplete",
    "Server",
    "WorkerIngestionFailure",
]


class GenerationJobs(
    GenerationRequests,
    GenerationLiveCapture,
    GenerationFlow,
    ArchiveJobs,
    StartupGraphJobs,
    GenerationWorker,
    AbortJobs,
    LifecycleJobs,
    QueuedJobs,
    Jobs,
):
    def __init__(
        self,
        instance_id,
        binding,
        database_socket,
        watch_code=False,
        worker_socket=None,
        worker_load_seconds=None,
        *,
        skip_archives=False,
    ):
        super().__init__(instance_id)
        if not isinstance(binding, dict) or set(binding) != FIELDS - {
            "instance_id"
        }:
            raise ValueError("Invalid binding fields")
        if not all(
            isinstance(value, str) and value for value in binding.values()
        ):
            raise ValueError("Invalid binding values")
        self.binding = binding
        self.database_socket = database_socket
        self.worker_socket = worker_socket
        self.worker_load_seconds = worker_load_seconds
        self.skip_archives = skip_archives
        self.worker_mode = None
        self.stopping = threading.Event()
        self.process = self.warm_capture = self.aborted_run = None
        from ORCHESTRATOR_beta_C68.watching.watcher import SourceWatcher

        root = Path(binding["root"])
        self.watcher = SourceWatcher(
            root,
            root / binding["control_root"],
            watch_code=watch_code,
            defer_archives=True,
        )
        self.thread = None
        self.pending = self.inflight = self.generation_reuse = None
        self.flow = self.flow_context = None
        self.startup_capture = False
        self._initialize_archive()
        self._initialize_startup_graph()

    def start(self):
        self.watcher.start()
        self.startup_capture = self.startup_replay = self.graph_queued = True
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
        self._close_startup_graph()
        with self.lock:
            try:
                self._stop_worker()
            except OSError:
                pass
        if self.thread is not None and self.thread.is_alive():
            self.thread.join(1)

    def _watch(self):
        self.generation_reuse = read_reuse(
            self.database_socket, self.instance_id, scope="foreground"
        )
        self._watch_queue()


if __name__ == "__main__":
    raise SystemExit(main())
