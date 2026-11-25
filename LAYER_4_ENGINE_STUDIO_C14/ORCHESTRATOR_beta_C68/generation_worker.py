"""Communicate with managed cold and warm Workers."""
import http.client
import json
import os
import subprocess
import sys
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from .abort import WorkerAborted
from .generation import MAX_WARM_DELTA_PATHS, parse_worker_result, read_accepted_model, worker_failure, worker_request
from .jobs import ENGINE, operation_timeout
from .warm_worker import validated_result as warm_result
from .warm_worker_process import process_environment
from .watcher_diagnostics import FOREGROUND_FENCE_MESSAGE, emit_record, report_graph_restart


GENERATION_ERRORS = (OSError, ValueError, TypeError, KeyError, RuntimeError, http.client.HTTPException)
_TIMING_PREFIX = "ANECHOIC_STARTUP_TIMING "
_SCAN_MODES = ("foreground_capture", "foreground_hashes")
_TIMING_MODES = {
    "model_ready": ("built", "reused"),
    "structure_ready": ("built", "reused"),
    "realization_graph_ready": ("built", "reused", "disabled"),
    "scan_started": _SCAN_MODES,
}
_SCAN_COUNTS = {"census_ns", "guarded_read_ns", "stream_ns", "sha256_ns", "carrier_count", "bytes_read"}
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
            valid = fields == {"mode"} and self.mode in _TIMING_MODES[self.phase]
        elif self.phase == "scan_metrics":
            valid = self.mode in _SCAN_MODES and fields == _SCAN_COUNTS | {"mode"}
        elif self.phase == "non_archived_load_started":
            valid = (not fields or (fields == {"mode"} and self.mode == "foreground_capture")
                     or fields in (_DELTA_COUNTS, _CHECKPOINT_COUNTS))
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
        record = json.loads(line[len(_TIMING_PREFIX):], object_pairs_hook=_unique_timing_fields)
        return _WorkerTiming.model_validate(record)
    except (ValueError, RecursionError, UnicodeEncodeError, ValidationError):
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
                except (OSError, ValueError):
                    pass
        else:
            remainder.append(line)
    return "\n".join(remainder)


class ForegroundCoverageLost(ValueError):
    pass


class ForegroundInputsChanged(ValueError):
    pass


class GenerationWorker:
    def _capture_generation(self, directory, reuse, paths, *, explicit, reconciliation, strict):
        options, epoch = (({}, None) if reconciliation and not self.skip_archives else
                          self._capture_options(reuse, paths, explicit=explicit))
        replay = self.thread is not None and not (explicit or strict)
        if strict:
            epoch = None
            if options:
                options["watcher_guarded"] = False
                options.pop("incremental", None)
        elif replay and epoch is None and paths is not None:
            raise ForegroundCoverageLost(FOREGROUND_FENCE_MESSAGE)
        elif replay and epoch is not None and paths is None and options.get("foreground") and self.watcher.watch_code:
            options["replay_graph"] = True
        if self.startup_capture and not options.get("incremental") and not reconciliation:
            reuse = None
        timeout = operation_timeout(45)
        run_id = self.active.run_id if self.active else None
        queued = self.watcher.foreground_events() if replay and epoch is not None else None
        try:
            result = self._run_worker(directory, reuse, paths, **options)
        except WorkerAborted:
            raise
        except GENERATION_ERRORS as error:
            if queued is not None and not self.stopping.is_set():
                if self.watcher.replay_fence(epoch, timeout=timeout, run_id=run_id) is not True:
                    raise ForegroundCoverageLost(FOREGROUND_FENCE_MESSAGE) from error
                if self.watcher.foreground_events() != queued:
                    raise ForegroundInputsChanged(FOREGROUND_FENCE_MESSAGE) from error
            raise
        if self.stopping.is_set():
            raise WorkerAborted("Worker aborted")
        if epoch is not None:
            fence = self.watcher.replay_fence if replay else self.watcher.capture_fence
            if fence(epoch, timeout=timeout, run_id=run_id) is not True:
                error = ForegroundCoverageLost if replay else ValueError
                raise error(FOREGROUND_FENCE_MESSAGE)
        return result, reuse, options

    def _run_worker(self, directory, reuse, paths, **options):
        if self.worker_socket and paths is not None and len(paths) <= MAX_WARM_DELTA_PATHS:
            try:
                result = self._run_warm_worker(reuse, paths)
            except Exception:
                self._flow_effect("worker_request", outcome="failed")
                raise
            self._flow_effect("worker_request", outcome="succeeded" if result is not None else "unavailable")
            if result is not None:
                self.worker_mode = "warm"
                return result
        request = worker_request(self.binding, self.database_socket, self.instance_id, reuse, paths)
        request["batch_full"] = True
        request["model_source"] = {"accepted_model": read_accepted_model(self.database_socket, self.instance_id)}
        request.update(options)
        stdout = self._communicate_worker(directory, request)
        result = parse_worker_result(stdout, reuse, paths, request.get("structure"),
                                     foreground=options.get("foreground", False))
        self.worker_mode = "cold"
        return result

    def _communicate_worker(self, directory, request, *, archive=False):
        env = process_environment()
        env["ANECHOIC_BETA_WORKER_PARENT_PID"] = str(os.getpid())
        timed = env.get("ANECHOIC_STARTUP_TIMING") == "1"
        if timed:
            from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import mark_startup_timing
        slot = "archive_process" if archive else "process"
        with self.lock:
            if self.stopping.is_set():
                raise RuntimeError("Orchestrator is stopping")
            try:
                process = subprocess.Popen(
                [sys.executable, "-B", "-P", "-m", "WORKERS_beta_C69.WORKERS_beta_C69__shared",
                 "--generation-dir", directory], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, text=True, cwd=ENGINE, env=env, start_new_session=True)
            except Exception:
                if not archive:
                    self._flow_effect("worker_started", outcome="failed")
                raise
            if not archive:
                if timed:
                    mark_startup_timing("worker_started", mode="cold")
                self._flow_effect("worker_started", outcome="succeeded")
            setattr(self, slot, process)
        try:
            stdout, stderr = process.communicate(json.dumps(request))
        finally:
            with self.lock:
                setattr(self, slot, None)
                aborted = (self.archive_run.state == "aborting" if archive else
                           self.active is not None and self.aborted_run == self.active.run_id)
        if aborted:
            raise WorkerAborted("Worker aborted")
        run_id = getattr(self.archive_run if archive else self.active, "run_id", None)
        if timed:
            stderr = _forward_startup_timing(stderr)
        if not archive:
            stderr = report_graph_restart(stderr, run_id)
        if process.returncode:
            detail = stderr.rstrip().rsplit("\n", 1)[-1][-2048:] or f"exit status {process.returncode}"
            raise worker_failure(stdout, detail, run_id=run_id)
        if stderr.strip():
            emit_record("WARNING", "worker_stderr_present", "capture", "degraded", run_id,
                        details={"phase": "archive" if archive else "foreground"})
        return stdout

    def _run_warm_worker(self, reuse, paths):
        try:
            return warm_result(self.worker_socket, self.worker_load_seconds, self.binding,
                               reuse, paths, self._register_warm_capture)
        finally:
            with self.lock:
                self.warm_capture = None
                if self.aborted_run is not None:
                    self.worker_mode = "warm"
                    raise WorkerAborted("Worker aborted")
