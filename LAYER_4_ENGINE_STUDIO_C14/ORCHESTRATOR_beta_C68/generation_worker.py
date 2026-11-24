"""Communicate with managed cold and warm Workers."""
import json
import os
import subprocess
import sys

from .abort import WorkerAborted
from .generation import MAX_WARM_DELTA_PATHS, parse_worker_result, worker_failure, worker_request
from .jobs import ENGINE
from .warm_worker import validated_result as warm_result
from .watcher_diagnostics import emit_record, report_graph_restart


class GenerationWorker:
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
        request.update(options)
        stdout = self._communicate_worker(directory, request)
        result = parse_worker_result(stdout, reuse, paths, request.get("structure"),
                                     foreground=options.get("foreground", False))
        self.worker_mode = "cold"
        return result

    def _communicate_worker(self, directory, request, *, archive=False):
        env = {key: value for key, value in os.environ.items() if key != "PYTHONHOME"}
        env["PYTHONPATH"] = str(ENGINE)
        env["ANECHOIC_BETA_WORKER_PARENT_PID"] = str(os.getpid())
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
                self._flow_effect("worker_started", outcome="succeeded")
            setattr(self, slot, process)
        try:
            stdout, stderr = process.communicate(json.dumps(request))
        finally:
            with self.lock:
                setattr(self, slot, None)
                aborted = (self.archive_run["state"] == "aborting" if archive else
                           self.active is not None and self.aborted_run == self.active.get("run_id"))
        if aborted:
            raise WorkerAborted("Worker aborted")
        run = self.archive_run if archive else self.active
        run_id = (run or {}).get("run_id")
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
