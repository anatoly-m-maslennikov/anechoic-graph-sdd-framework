"""Load deferred Archive carriers while live generation work continues."""

import http.client
from hashlib import sha256 as sha256
import json as json
import os
from pathlib import Path as Path
import signal
import threading
import time
from uuid import uuid4

from ORCHESTRATOR_beta_C68.archive_operations.archive_capture_plan import ArchiveCapturePlan
from ORCHESTRATOR_beta_C68.archive_operations.archive_publication import ArchivePublication
from ORCHESTRATOR_beta_C68.abort import WorkerAborted as WorkerAborted
from ORCHESTRATOR_beta_C68.jobs import _Run
from ORCHESTRATOR_beta_C68.generation.generation import (
    DeltaRequiresReconciliation as DeltaRequiresReconciliation,
    WorkerIngestionFailure as WorkerIngestionFailure,
    admit_generation as admit_generation,
    read_reuse,
)
from ORCHESTRATOR_beta_C68.generation.worker.checkpoint.startup_checkpoint import archive_checkpoint, compatible_checkpoint
from ORCHESTRATOR_beta_C68.watching.poll_coverage.watcher_diagnostics import emit_record as emit_record

_ARCHIVE_ERRORS = (
    OSError,
    ValueError,
    TypeError,
    KeyError,
    RuntimeError,
    http.client.HTTPException,
)
_ARCHIVE_FENCE_MESSAGE = "Archive watcher coverage was lost during capture"
ARCHIVE_RECONCILIATION = "archive_reconciliation"


class ArchiveInputsChanged(RuntimeError):
    """The archive population changed during a capture."""


class ArchiveCoverageLost(RuntimeError):
    """The watcher cannot establish archive currentness."""


class ArchiveJobs(ArchiveCapturePlan, ArchivePublication):
    def _initialize_archive(self):
        self.deferred_archive = None
        self.archive_run = self.archive_process = None
        self.archive_thread = self.archive_result = None
        self.archive_dirty = False
        self.archive_reconciliation_pending = False
        self.archive_watching = False
        self.live_generation = None

    def _run_archive(self):
        if (
            self.skip_archives
            or self.startup_capture
            or self.startup_replay
            or self.stopping.is_set()
        ):
            return
        if self.archive_thread is not None:
            if self.archive_thread.is_alive():
                return
            self.archive_thread = None
            self._finish_archive()
        if self.deferred_archive is None and self.archive_watching:
            return
        if self.archive_run is not None and not self.archive_dirty:
            return
        with self.lock:
            self.archive_dirty = False
            if self.deferred_archive is not None:
                self.archive_run = _Run(
                    state="running", started_at=time.time(), run_id=uuid4().hex
                )
            self.archive_thread = threading.Thread(
                target=self._capture_archive,
                args=(self.deferred_archive,),
                daemon=True,
            )
            self.archive_thread.start()

    def _capture_archive(self, deferred):
        try:
            self.watcher.start_ticket_watch()
            if not self.watcher.watch_archives():
                raise ArchiveCoverageLost(
                    "Archive watcher coverage is unavailable"
                )
            self.archive_watching = True
            if deferred is not None:
                checkpoint = deferred.get("checkpoint")
                source = deferred.get("checkpoint_source")
                checkpoint = self._capture_checkpoint(
                    source, checkpoint, deferred
                )
                endpoints, result = self._archive_snapshot(
                    deferred["endpoints"], checkpoint, deferred
                )
                replace = deferred.get("replace") or (
                    source is not None and checkpoint is None
                )
                if self.stopping.is_set():
                    if (
                        temporary := result.pop("_archive_temp", None)
                    ) is not None:
                        temporary.cleanup()
                    return
                self.archive_result = (
                    endpoints,
                    result | {"replace": True} if replace else result,
                )
        except _ARCHIVE_ERRORS as error:
            self.archive_result = error
        finally:
            self.watcher.queue.put({})

    def _capture_checkpoint(self, source, checkpoint, deferred):
        if source is not None:
            record = read_reuse(
                self.database_socket, self.instance_id, scope="archive"
            )
            candidate = (
                record.model_dump(exclude_unset=True)
                if record is not None
                else None
            )
            if (
                compatible_checkpoint(candidate)
                and candidate["inputs"] == source["inputs"]
            ):
                checkpoint = archive_checkpoint(candidate)
                checkpoint["endpoints"] = deferred["endpoints"]
        return checkpoint

    def _finish_archive(self):
        result, self.archive_result = self.archive_result, None
        try:
            self._finish_archive_result(result)
        finally:
            if (
                isinstance(result, tuple)
                and (temporary := result[1].pop("_archive_temp", None))
                is not None
            ):
                temporary.cleanup()

    def _close_archive(self):
        with self.lock:
            self._stop_archive()
        if self.archive_thread is not None:
            self.archive_thread.join(1)
            if not self.archive_thread.is_alive() and isinstance(
                self.archive_result, tuple
            ):
                if (
                    temporary := self.archive_result[1].pop(
                        "_archive_temp", None
                    )
                ) is not None:
                    temporary.cleanup()

    def _stop_archive(self):
        if (
            self.archive_process is not None
            and self.archive_process.poll() is None
        ):
            try:
                os.killpg(self.archive_process.pid, signal.SIGKILL)
            except ProcessLookupError:
                return False
            return True
        return False
