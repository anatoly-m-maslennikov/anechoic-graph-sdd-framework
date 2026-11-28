"""Communicate with managed cold and warm Workers."""

import http.client
import json
import os
from pathlib import Path as Path
import subprocess
import sys
import tempfile as tempfile
from typing import Annotated

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    model_validator,
)

from ORCHESTRATOR_beta_C68.generation.worker.generation_worker_capture import GenerationWorkerCapture
from ORCHESTRATOR_beta_C68.abort import WorkerAborted
from ORCHESTRATOR_beta_C68.archive_operations.archive_jobs import (
    ArchiveCoverageLost as ArchiveCoverageLost,
    ArchiveInputsChanged as ArchiveInputsChanged,
    _ARCHIVE_FENCE_MESSAGE as _ARCHIVE_FENCE_MESSAGE,
)
from ORCHESTRATOR_beta_C68.generation.generation import (
    MAX_WARM_DELTA_PATHS as MAX_WARM_DELTA_PATHS,
    DeltaRequiresReconciliation,
    read_accepted_model as read_accepted_model,
    read_reuse,
    worker_failure,
    worker_request as worker_request,
)
from ORCHESTRATOR_beta_C68.generation.worker.worker_reply import (
    parse_worker_result as parse_worker_result,
)
from ORCHESTRATOR_beta_C68.jobs import ENGINE, operation_timeout as operation_timeout
from ORCHESTRATOR_beta_C68.generation.worker.checkpoint.startup_checkpoint import compatible_checkpoint as compatible_checkpoint
from ORCHESTRATOR_beta_C68.generation.worker.warm_worker import validated_result as warm_result
from ORCHESTRATOR_beta_C68.generation.worker.worker_reply import parse_archive_result as parse_archive_result
from ORCHESTRATOR_beta_C68.generation.worker.worker_reply import parse_worker_data as parse_worker_data
from ORCHESTRATOR_beta_C68.peers.warm_worker_process import process_environment
from ORCHESTRATOR_beta_C68.watching.poll_coverage.watcher_diagnostics import (
    FOREGROUND_FENCE_MESSAGE,
    emit_record,
    report_graph_restart,
)


GENERATION_ERRORS = (
    OSError,
    ValueError,
    TypeError,
    KeyError,
    RuntimeError,
    http.client.HTTPException,
)
_TIMING_PREFIX = "ANECHOIC_STARTUP_TIMING "
_SCAN_MODES = ("foreground_capture", "foreground_hashes")
_TIMING_MODES = {
    "model_ready": ("built", "reused"),
    "structure_ready": ("built", "reused"),
    "realization_graph_ready": ("built", "reused", "disabled"),
    "scan_started": _SCAN_MODES,
}
_SCAN_COUNTS = {
    "census_ns",
    "guarded_read_ns",
    "stream_ns",
    "sha256_ns",
    "carrier_count",
    "bytes_read",
}
_DELTA_COUNTS = {"changed_paths", "comparison_ns"}
_CHECKPOINT_COUNTS = _DELTA_COUNTS | {"checkpoint_validation_ns"}


def _unique_timing_fields(pairs):
    fields = dict(pairs)
    if len(fields) != len(pairs):
        raise ValueError("Duplicate timing field")
    return fields


_Counter = Annotated[int, Field(ge=0, lt=2**63)]


class _WorkerTiming(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)
    phase: str
    timestamp_ns: Annotated[int, Field(gt=0, lt=2**63)]
    mode: str | None = None
    census_ns: _Counter | None = None
    guarded_read_ns: _Counter | None = None
    stream_ns: _Counter | None = None
    sha256_ns: _Counter | None = None
    carrier_count: _Counter | None = None
    bytes_read: _Counter | None = None
    changed_paths: _Counter | None = None
    comparison_ns: _Counter | None = None
    checkpoint_validation_ns: _Counter | None = None

    @model_validator(mode="after")
    def exact_shape(self):
        fields = self.model_fields_set - {"phase", "timestamp_ns"}
        if any(getattr(self, name) is None for name in fields):
            raise ValueError("Null timing field")
        if self.phase in _TIMING_MODES:
            valid = (
                fields == {"mode"} and self.mode in _TIMING_MODES[self.phase]
            )
        elif self.phase == "scan_metrics":
            valid = self.mode in _SCAN_MODES and fields == _SCAN_COUNTS | {
                "mode"
            }
        elif self.phase == "non_archived_load_started":
            valid = (
                not fields
                or (fields == {"mode"} and self.mode == "foreground_capture")
                or fields in (_DELTA_COUNTS, _CHECKPOINT_COUNTS)
            )
        else:
            valid = False
        if not valid:
            raise ValueError("Invalid timing marker")
        return self


def _parse_worker_timing(line):
    if not line.startswith(_TIMING_PREFIX):
        return None
    try:
        if len(line.encode("utf-8")) > 1024:
            return None
        record = json.loads(
            line[len(_TIMING_PREFIX) :],
            object_pairs_hook=_unique_timing_fields,
        )
        return _WorkerTiming.model_validate(record)
    except ValueError, RecursionError, UnicodeEncodeError, ValidationError:
        return None


def _forward_startup_timing(stderr):
    remainder = []
    stream = sys.stderr
    for line in stderr.split("\n"):
        if _parse_worker_timing(line) is not None:
            if stream is not None:
                try:
                    stream.write(line + "\n")
                    stream.flush()
                except OSError, ValueError:
                    pass
        else:
            remainder.append(line)
    return "\n".join(remainder)


class ForegroundCoverageLost(ValueError):
    pass


class ForegroundInputsChanged(ValueError):
    pass


class GenerationWorker(GenerationWorkerCapture):
    def _flow_effect(self, name, **values):
        if self.flow is not None:
            targets = {
                "worker_request": "C69",
                "worker_started": "C69",
                "generation_admission": "C71",
                "generation_reuse_check": "C71",
                "generation_reuse_write": "C68.generation_reuse",
            }
            self.flow.add("effect", name, target=targets[name], **values)

    def health(self):
        status = super().health()
        status["watcher_active"] = (
            self.thread is not None
            and self.thread.is_alive()
            and self.watcher.capture_epoch() is not None
        )
        return status

    def _recover_watcher_coverage(self, target):
        if self.watcher.capture_epoch() is None:
            raise ForegroundCoverageLost(FOREGROUND_FENCE_MESSAGE)
        checkpoint = read_reuse(self.database_socket, self.instance_id)
        reuse = (
            checkpoint.model_dump(exclude_unset=True)
            if checkpoint is not None
            else None
        )
        self.graph_queued = True
        try:
            return self._attempt_generation(
                target, reuse, recover_coverage=True
            )
        except DeltaRequiresReconciliation:
            return self._attempt_generation(
                target, None, recover_coverage=True
            )

    def _communicate_worker(
        self, directory, request, *, archive=False, graph=False
    ):
        env = process_environment()
        env["ANECHOIC_BETA_WORKER_PARENT_PID"] = str(os.getpid())
        timed = env.get("ANECHOIC_STARTUP_TIMING") == "1"
        slot = (
            "archive_process"
            if archive
            else "graph_process"
            if graph
            else "process"
        )
        process = self._start_cold_worker(directory, env, timed, slot)
        try:
            stdout, stderr = process.communicate(json.dumps(request))
        finally:
            with self.lock:
                setattr(self, slot, None)
                aborted = (
                    self.archive_run.state == "aborting"
                    if archive
                    else not graph
                    and self.active is not None
                    and self.aborted_run == self.active.run_id
                )
        if aborted:
            raise WorkerAborted("Worker aborted")
        run = self.archive_run if archive else None if graph else self.active
        run_id = getattr(run, "run_id", None)
        return self._worker_output(
            process, stdout, stderr, timed, archive, graph, run_id
        )

    def _worker_output(
        self, process, stdout, stderr, timed, archive, graph, run_id
    ):
        if timed:
            stderr = _forward_startup_timing(stderr)
        if not archive:
            stderr = report_graph_restart(stderr, run_id)
        if process.returncode:
            detail = (
                stderr.rstrip().rsplit("\n", 1)[-1][-2048:]
                or f"exit status {process.returncode}"
            )
            raise worker_failure(stdout, detail, run_id=run_id)
        if stderr.strip():
            emit_record(
                "WARNING",
                "worker_stderr_present",
                "capture",
                "degraded",
                run_id,
                details={
                    "phase": "archive"
                    if archive
                    else "graph"
                    if graph
                    else "foreground"
                },
            )
        return stdout

    def _start_cold_worker(self, directory, env, timed, slot):
        foreground = slot == "process"
        with self.lock:
            if self.stopping.is_set():
                raise RuntimeError("Orchestrator is stopping")
            try:
                process = subprocess.Popen(
                    [
                        sys.executable,
                        "-B",
                        "-P",
                        "-m",
                        "WORKERS_beta_C69.WORKERS_beta_C69__shared",
                        "--generation-dir",
                        directory,
                    ],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    cwd=ENGINE,
                    env=env,
                    start_new_session=True,
                )
            except Exception:
                if foreground:
                    self._flow_effect("worker_started", outcome="failed")
                raise
            if foreground:
                if timed:
                    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.sources.sources__shared import (
                        mark_startup_timing,
                    )

                    mark_startup_timing("worker_started", mode="cold")
                self._flow_effect("worker_started", outcome="succeeded")
            setattr(self, slot, process)
        return process

    def _run_warm_worker(self, reuse, paths):
        try:
            return warm_result(
                self.worker_socket,
                self.worker_load_seconds,
                self.binding,
                reuse,
                paths,
                self._register_warm_capture,
            )
        finally:
            with self.lock:
                self.warm_capture = None
                if self.aborted_run is not None:
                    self.worker_mode = "warm"
                    raise WorkerAborted("Worker aborted")
