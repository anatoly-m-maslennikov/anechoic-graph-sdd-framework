"""Private, single-build Orchestrator for the pinned beta Worker."""
from __future__ import annotations

import http.client
import json
import os
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

from .abort import AbortJobs, WorkerAborted
from .flow import Flow, safe_target
from .generation import (
    MAX_WARM_DELTA_PATHS,
    DeltaRequiresReconciliation,
    GenerationBaseChanged,
    admit_generation,
    confirm_reuse,
    parse_worker_result,
    read_reuse,
    ticket_delta_paths,
    wait_build,
    worker_request,
)
from .jobs import ENGINE, FIELDS, Jobs
from .lifecycle import LifecycleJobs
from .retry import CurrentnessRetry
from .server import Handler, Server, main
from .warm_worker import validated_result as warm_result

__all__ = ["GenerationJobs", "Handler", "Server"]


class GenerationJobs(AbortJobs, LifecycleJobs, Jobs):
    def __init__(self, instance_id, binding, database_socket, watch_code=False,
                 worker_socket=None, worker_load_seconds=None):
        super().__init__(instance_id)
        if not isinstance(binding, dict) or set(binding) != FIELDS - {"instance_id"}:
            raise ValueError("Invalid binding fields")
        if not all(isinstance(value, str) and value for value in binding.values()):
            raise ValueError("Invalid binding values")
        self.binding = binding
        self.database_socket = database_socket
        self.worker_socket = worker_socket
        self.worker_load_seconds = worker_load_seconds
        self.worker_mode = None
        self.stopping = threading.Event()
        self.process = None
        self.warm_capture = None
        self.aborted_run = None
        from .watcher import SourceWatcher
        root = Path(binding["root"])
        self.watcher = SourceWatcher(root, root / binding["control_root"], watch_code=watch_code)
        self.thread = None
        self.pending = None
        self.inflight = None
        self.lifecycle_job = None
        self.generation_reuse = None
        self.flow = None
        self.flow_context = None

    def start(self):
        self.watcher.start()
        self.thread = threading.Thread(target=self._watch, daemon=True)
        self.thread.start()

    def close(self):
        self.stopping.set()
        with self.lock:
            for job in (self.pending, self.inflight, self.lifecycle_job):
                if job is not None:
                    job["event"].set()
        self.watcher.close()
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
            if job is not None and job["target"] != target:
                return 409, {"error": {"code": "build_active", "message": "Another refresh is active"}}
            if job is None:
                job = self.pending = {"event": threading.Event(), "outcome": None, "target": target, "requests": [], "omitted_requests": 0}
                self.watcher.queue.put({})
            request_time = time.time()
            if job is self.inflight and self.flow is not None:
                self.flow.input("rebuild_request", target=safe_target(target), detail={"coalesced": True}, at=request_time, trigger=False)
            elif len(job["requests"]) < 200:
                job["requests"].append(request_time)
            else:
                job["omitted_requests"] += 1
        return self._wait_build(job)

    def _wait_build(self, job):
        return wait_build(job, None)

    def _watch(self):
        retry = CurrentnessRetry()
        self.generation_reuse = read_reuse(self.database_socket, self.instance_id)
        self.flow_context = {"startup": True}
        retry.observe(self._generate(startup=True))
        while not self.stopping.is_set():
            changes = self.watcher.changes(0.1)
            due = retry.ready()
            if changes or due:
                with self.lock:
                    if self.stopping.is_set():
                        return
                    lifecycle = self.lifecycle_job
                    job = None if lifecycle is not None else self.pending
                    if lifecycle is None:
                        self.pending = None
                    self.inflight = job
                if lifecycle is not None and not any(changes):
                    outcome = self._execute_lifecycle(lifecycle)
                    with self.lock:
                        lifecycle["outcome"] = outcome
                        self.lifecycle_job = None
                        lifecycle["event"].set()
                        if self.pending is not None:
                            self.watcher.queue.put({})
                elif any(changes) or due or job is not None:
                    self.flow_context = {"job": job, "changes": changes if job is None else (), "retry": due}
                    outcome = self._generate(job["target"] if job is not None else None,
                                             changes=changes if job is None else ())
                    retry.observe(outcome)
                    with self.lock:
                        if job is not None:
                            job["outcome"] = outcome
                            job["event"].set()
                        self.inflight = None
                        if self.lifecycle_job is not None:
                            self.watcher.queue.put({})
                        flow, self.flow = self.flow, None
                    if flow is not None:
                        flow.finish(outcome)

    def _flow_effect(self, name, **values):
        if self.flow is not None:
            targets = {"worker_request": "C69", "worker_started": "C69",
                       "generation_admission": "C71", "generation_reuse_check": "C71",
                       "generation_reuse_write": "C68.generation_reuse"}
            self.flow.add("effect", name, target=targets[name], **values)

    def _run_worker(self, directory, reuse, paths):
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
        env = {key: value for key, value in os.environ.items() if key != "PYTHONHOME"}
        env["PYTHONPATH"] = str(ENGINE)
        env["ANECHOIC_BETA_WORKER_PARENT_PID"] = str(os.getpid())
        with self.lock:
            if self.stopping.is_set():
                raise RuntimeError("Orchestrator is stopping")
            try:
                process = subprocess.Popen(
                [sys.executable, "-B", "-P", "-m", "WORKERS_beta_C69.WORKERS_beta_C69__shared",
                 "--generation-dir", directory], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, text=True, cwd=ENGINE, env=env, start_new_session=True)
            except Exception:
                self._flow_effect("worker_started", outcome="failed")
                raise
            self._flow_effect("worker_started", outcome="succeeded")
            self.process = process
        try:
            stdout, stderr = process.communicate(json.dumps(request))
        finally:
            with self.lock:
                self.process = None
                aborted = self.active is not None and self.aborted_run == self.active.get("run_id")
        if aborted:
            raise WorkerAborted("Worker aborted")
        if process.returncode:
            raise RuntimeError("Worker failed: " + stderr[-2048:])
        if stderr:
            sys.stderr.write(stderr[-8192:])
        result = parse_worker_result(stdout, reuse, paths, request.get("structure"))
        self.worker_mode = "cold"
        return result

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

    def _attempt_generation(self, target, reuse, paths=None):
        with tempfile.TemporaryDirectory(prefix="anechoic-generation-") as temporary:
            directory = str(Path(temporary).resolve(strict=True))
            started = time.monotonic()
            result = self._run_worker(directory, reuse, paths)
            captured = time.monotonic()
            witness = result.get("reuse", reuse)
            if result.get("reuse", True) is None:
                del result["reuse"]
            effect = "generation_reuse_check" if "unchanged" in result else "generation_admission"
            try:
                admitted = (confirm_reuse(self.database_socket, self.instance_id, result) if "unchanged" in result
                            else admit_generation(self.database_socket, self.instance_id, directory, result, target))
            except Exception:
                self._flow_effect(effect, outcome="failed")
                raise
            if effect == "generation_admission":
                self._flow_effect(effect, outcome="succeeded", detail={"reuse_proof_present": witness is not None})
            else:
                self._flow_effect(effect, outcome="succeeded")
            admitted.update(worker_seconds=captured - started, admission_seconds=time.monotonic() - captured)
            if "paths" in result:
                admitted["delta_path_count"] = len(result["paths"])
        if "snapshot" in result and "paths" not in result:
            self.unconfirmed_lifecycle_write = False
        if witness is not None:
            self.generation_reuse = {key: value for key, value in witness.items() if key != "carrier_hashes"}
            self.generation_reuse["base_generation"] = admitted["generation"]
            self._flow_effect("generation_reuse_write", outcome="succeeded", detail={"state": "stored"})
        return {"state": "succeeded", **admitted}

    def _start_flow(self, target, changes, startup):
        self.flow = Flow(self.instance_id, self.database_socket)
        context, self.flow_context = self.flow_context or {}, None
        job = context.get("job")
        if context.get("startup") or startup:
            self.flow.input("startup")
        if job is not None:
            for index, at in enumerate(job["requests"]):
                self.flow.input("rebuild_request", target=safe_target(target),
                                detail={"coalesced": index > 0}, at=at, trigger=index == 0)
            job["requests"].clear()
            self.flow.omitted += job["omitted_requests"]
        file_inputs = []
        for change in context.get("changes", changes):
            if change:
                index = self.flow.add("input", "file_change", causes=[],
                                      detail={"event_type": change.get("event_type")})
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

    def _generate(self, target=None, *, changes=(), startup=False):
        with self.lock:
            job = self._start_flow(target, changes, startup)
            self.active = {"state": "running", "started_at": time.time(), "run_id": self.flow.run_id}
            self.aborted_run = None
            self.worker_mode = None
        reuse = self.generation_reuse if target is None and (startup or any(changes)) else None
        self.generation_reuse = None
        self._flow_effect("generation_reuse_write", outcome="succeeded", detail={"state": "cleared"})
        outcome = {"state": "failed", "code": "generation_failed"}
        try:
            paths = ticket_delta_paths(self.binding, changes) if reuse is not None else None
            try:
                outcome = self._attempt_generation(target, reuse, paths)
            except GenerationBaseChanged:
                outcome = self._attempt_generation(target, None)
            except DeltaRequiresReconciliation:
                outcome = self._attempt_generation(target, {key: value for key, value in reuse.items()
                                                            if key != "carrier_hashes"})
        except WorkerAborted:
            outcome = {"state": "aborted", "code": "worker_aborted", "message": "Worker aborted"}
        except (OSError, ValueError, TypeError, KeyError, RuntimeError, http.client.HTTPException) as error:
            outcome["message"] = str(error)[-2048:]
        finally:
            with self.lock:
                self.latest = {**self.active, **outcome, "finished_at": time.time()}
                if self.worker_mode is not None:
                    self.latest["worker_mode"] = self.worker_mode
                self.active = None
                flow = self.flow
                if job is None:
                    self.flow = None
            if job is None:
                flow.finish(outcome)
        return outcome
if __name__ == "__main__":
    raise SystemExit(main())
