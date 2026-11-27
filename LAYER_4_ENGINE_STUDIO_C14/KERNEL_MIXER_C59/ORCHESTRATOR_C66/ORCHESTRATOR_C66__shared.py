"""Run short-lived compiler workers for one admitted Project."""

import subprocess
from threading import Lock
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict


class _WorkerRun(BaseModel):
    model_config = ConfigDict(
        strict=True, extra="forbid", validate_assignment=True
    )

    id: str
    kind: Literal["model_build", "structure_refresh"]
    pid: int | None
    status: Literal["running", "failed", "completed", "timed_out", "cancelled"]
    returncode: int | None = None


class Orchestrator:
    """Track active workers and the latest terminal run of each kind."""

    def __init__(self):
        self._lock = Lock()
        self._active = {}
        self._latest = {}
        self._processes = {}
        self._cancelled = set()
        self._stopped = False

    def worker_runs(self):
        """Return independent JSON-compatible snapshots of worker state."""
        with self._lock:
            return {
                "active": [
                    run.model_dump(exclude_unset=True)
                    for run in self._active.values()
                ],
                "latest": [
                    run.model_dump(exclude_unset=True)
                    for run in self._latest.values()
                ],
            }

    def stop(self):
        """Stop active children and reject future launches."""
        with self._lock:
            self._stopped = True
            for run_id, process in self._processes.items():
                if process.poll() is None:
                    process.kill()
                    self._cancelled.add(run_id)

    def _start(self, run, command, cwd, env):
        with self._lock:
            if self._stopped:
                raise RuntimeError("Orchestrator is stopped")
            try:
                process = subprocess.Popen(
                    command,
                    cwd=cwd,
                    env=env,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
            except OSError:
                run.status = "failed"
                self._latest[run.kind] = run
                raise
            run.pid = process.pid
            self._active[run.id] = run
            self._processes[run.id] = process
        return process

    def run_worker(self, kind, command, *, cwd, env, timeout):
        "Run a trusted compiler command with the runtime's process settings."
        if kind not in ("model_build", "structure_refresh"):
            raise ValueError(f"Unknown worker kind: {kind}")
        run = _WorkerRun(id=uuid4().hex, kind=kind, pid=None, status="running")
        process = self._start(run, command, cwd, env)
        status = "failed"
        try:
            try:
                stdout, stderr = process.communicate(timeout=timeout)
            except subprocess.TimeoutExpired as error:
                process.kill()
                error.stdout, error.stderr = process.communicate()
                status = "timed_out"
                raise
            except BaseException:
                process.kill()
                process.wait()
                raise
            status = "completed" if process.returncode == 0 else "failed"
            return subprocess.CompletedProcess(
                command, process.returncode, stdout, stderr
            )
        finally:
            with self._lock:
                if run.id in self._cancelled:
                    status = "cancelled"
                    self._cancelled.remove(run.id)
                run.status = status
                if process.returncode is not None:
                    run.returncode = process.returncode
                del self._active[run.id]
                del self._processes[run.id]
                self._latest[kind] = run
