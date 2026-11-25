"""Basic worker job and private socket connection."""
import http.client
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import threading
import time

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, InstanceOf

from .retry import CurrentnessRetry

ENGINE = Path(__file__).resolve().parents[1]
FIELDS = {"instance_id", "root", "control_root", "manifest_path", "manifest_sha256", "project_prefix"}
DEADLINE_SECONDS = 120


def operation_timeout(seconds):
    return (None if os.getenv("ANECHOIC_TEST_IMAGE_DEADLINES") == "0"
            else seconds)


class _Run(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid", validate_assignment=True)

    state: str
    started_at: float
    run_id: str | None = None
    finished_at: float | None = None
    code: str | None = None
    message: str | None = None
    retrying: bool | None = None
    generation: str | None = None
    kind: str | None = None
    result_ids: dict[str, str] | None = None
    worker_seconds: float | None = None
    admission_seconds: float | None = None
    delta_path_count: int | None = None
    worker_mode: str | None = None


class _GenerationJob(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid", validate_assignment=True, arbitrary_types_allowed=True)
    event: threading.Event = Field(default_factory=threading.Event)
    outcome: Any = None
    target: str | None
    requests: list[float] = Field(default_factory=list)
    omitted_requests: int = 0


class _LifecycleJob(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid", validate_assignment=True, arbitrary_types_allowed=True)
    event: threading.Event = Field(default_factory=threading.Event)
    outcome: Any = None
    deadline: float | None
    started: bool = False
    name: str
    arguments: InstanceOf[dict]


class LifecycleCoveragePending(Exception):
    """A recovery or file-change batch may still precede the write."""


class Jobs:
    def __init__(self, instance_id):
        self.instance_id = instance_id
        self.lock = threading.Lock()
        self.active = None
        self.latest = None
        self.lifecycle_job = None
        self.startup_replay = False

    def health(self):
        with self.lock:
            return {"instance_id": self.instance_id, "pid": os.getpid(),
                    "lifecycle_active": self.lifecycle_job is not None,
                    "startup_replay_pending": self.startup_replay}

    def status(self):
        with self.lock:
            return {"active": self.active.model_dump(exclude_unset=True) if self.active else None,
                    "latest": self.latest.model_dump(exclude_unset=True) if self.latest else None}

    def build(self, request):
        if not isinstance(request, dict) or set(request) != FIELDS:
            return 400, {"error": {"code": "invalid_request", "message": "Invalid build fields"}}
        if request["instance_id"] != self.instance_id:
            return 409, {"error": {"code": "instance_mismatch", "message": "Instance does not match"}}
        with self.lock:
            if self.active is not None:
                return 409, {"error": {"code": "build_active", "message": "A build is already active"}}
            self.active = _Run(state="running", started_at=time.time())
        outcome = {"state": "failed", "code": "internal_error"}
        try:
            binding = {key: value for key, value in request.items() if key != "instance_id"}
            env = {key: value for key, value in os.environ.items() if key != "PYTHONHOME"}
            env["PYTHONPATH"] = str(ENGINE)
            process = subprocess.run(
                [sys.executable, "-B", "-P", "-m", "WORKERS_beta_C69.WORKERS_beta_C69__shared"],
                input=json.dumps(binding), text=True, capture_output=True,
                timeout=operation_timeout(DEADLINE_SECONDS), cwd=ENGINE,
                env=env, check=False)
            if process.returncode:
                raise RuntimeError("Worker failed: " + process.stderr[:2048])
            snapshot = json.loads(process.stdout)
            if not isinstance(snapshot, dict):
                raise ValueError("Worker returned an invalid snapshot")
            outcome = {"state": "succeeded"}
            return 200, {"result": snapshot}
        except subprocess.TimeoutExpired:
            outcome = {"state": "failed", "code": "worker_timeout"}
            return 504, {"error": {"code": "worker_timeout", "message": "Worker deadline exceeded"}}
        except (OSError, ValueError, RuntimeError) as error:
            outcome = {"state": "failed", "code": "worker_failed"}
            return 502, {"error": {"code": "worker_failed", "message": str(error)[:2048]}}
        finally:
            with self.lock:
                self.latest = _Run(**(self.active.model_dump(exclude_unset=True) | outcome), finished_at=time.time())
                self.active = None


class QueuedJobs:
    def _watch_queue(self):
        retry = CurrentnessRetry()
        self.flow_context = {"startup": True}
        outcome = self._generate(startup=True)
        retry.observe(outcome)
        if outcome["state"] == "succeeded":
            self._replay_startup(retry)
        self._run_archive()
        while not self.stopping.is_set():
            self.watcher.restore_foreground()
            batch = self.watcher.changes(0.1)
            changes = self._partition_archive_changes([change for change in batch if change])
            due = retry.ready()
            if batch or due or self.lifecycle_job is not None:
                with self.lock:
                    if self.stopping.is_set():
                        return
                    lifecycle = self.lifecycle_job
                    job = None if lifecycle is not None else self.pending
                    if lifecycle is None:
                        self.pending = None
                    self.inflight = job
                if lifecycle is not None and not changes and retry.due is None:
                    self._run_queued_lifecycle(lifecycle)
                elif any(changes) or due or job is not None:
                    self._run_queued_generation(retry, job, changes, due)
            self._run_archive()
            self._run_startup_graph()

    def _run_queued_lifecycle(self, job):
        try:
            outcome = self._execute_lifecycle(job)
        except LifecycleCoveragePending:
            return
        with self.lock:
            if self.lifecycle_job is job:
                job.outcome = outcome
                self.lifecycle_job = None
                job.event.set()
                if self.pending is not None:
                    self.watcher.queue.put({})

    def _replay_startup(self, retry):
        if self.stopping.is_set():
            return
        changes = self._partition_archive_changes([change for change in self.watcher.changes(0) if change])
        finished = True
        if changes:
            outcome = self._generate(changes=changes)
            retry.observe(outcome)
            finished = outcome["state"] == "succeeded"
        with self.lock:
            self.startup_replay = not finished
            if self.pending is not None:
                self.watcher.queue.put({})

    def _run_queued_generation(self, retry, job, changes, due):
        self.flow_context = {"job": job, "changes": changes if job is None else (), "retry": due}
        outcome = self._generate(job.target if job is not None else None,
                                 changes=changes if job is None else ())
        retry.observe(outcome)
        with self.lock:
            if job is not None:
                job.outcome = outcome
                job.event.set()
            self.inflight = None
            if self.lifecycle_job is not None:
                self.watcher.queue.put({})
            flow, self.flow = self.flow, None
        if flow is not None:
            flow.finish(outcome)
        if self.startup_replay and outcome["state"] == "succeeded":
            self._replay_startup(retry)


class UnixConnection(http.client.HTTPConnection):
    def __init__(self, path):
        super().__init__("localhost", timeout=operation_timeout(30))
        self.path = path

    def connect(self):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.settimeout(self.timeout)
        self.sock.connect(self.path)


