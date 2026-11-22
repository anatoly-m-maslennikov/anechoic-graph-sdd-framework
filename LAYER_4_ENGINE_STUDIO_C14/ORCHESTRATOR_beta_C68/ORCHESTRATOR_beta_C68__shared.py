"""Private, single-build Orchestrator for the pinned beta Worker."""
from __future__ import annotations

import argparse
import json
import http.client
import os
from pathlib import Path
import socketserver
import signal
import subprocess
import sys
import threading
import tempfile
import time
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlsplit

from .jobs import ENGINE, FIELDS, Jobs, UnixConnection
from .lifecycle import LifecycleJobs
from .retry import CurrentnessRetry

GENERATION_DEADLINE_SECONDS = 150
MANAGED_BUILD_WAIT_SECONDS = 2 * GENERATION_DEADLINE_SECONDS + 10
MAX_REQUEST_BYTES = 65536


class GenerationJobs(LifecycleJobs, Jobs):
    def __init__(self, instance_id, binding, database_socket, watch_code=False):
        super().__init__(instance_id)
        if not isinstance(binding, dict) or set(binding) != FIELDS - {"instance_id"}:
            raise ValueError("Invalid binding fields")
        if not all(isinstance(value, str) and value for value in binding.values()):
            raise ValueError("Invalid binding values")
        self.binding = binding
        self.database_socket = database_socket
        self.stopping = threading.Event()
        self.process = None
        from .watcher import SourceWatcher
        root = Path(binding["root"])
        self.watcher = SourceWatcher(root, root / binding["control_root"], watch_code=watch_code)
        self.thread = None
        self.pending = None
        self.inflight = None
        self.lifecycle_job = None

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
            if self.process is not None:
                try:
                    os.killpg(self.process.pid, signal.SIGKILL)
                except ProcessLookupError:
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
                job = self.pending = {"event": threading.Event(), "outcome": None, "target": target}
                self.watcher.queue.put({})
        return self._wait_build(job)

    def _wait_build(self, job):
        if not job["event"].wait(MANAGED_BUILD_WAIT_SECONDS):
            return 504, {"error": {"code": "generation_timeout", "message": "Generation deadline exceeded"}}
        outcome = job["outcome"]
        if outcome is None:
            return 503, {"error": {"code": "orchestrator_stopping", "message": "Orchestrator is stopping"}}
        if outcome["state"] != "succeeded":
            return 502, {"error": {"code": outcome["code"], "message": outcome.get("message", "Generation failed")}}
        result = {"generation": outcome["generation"]}
        if job["target"] is not None:
            result["result_ids"] = outcome["result_ids"]
        return 200, {"result": result}

    def _watch(self):
        retry = CurrentnessRetry()
        retry.observe(self._generate())
        while not self.stopping.is_set():
            changes = self.watcher.changes(0.1)
            if changes or retry.ready():
                with self.lock:
                    if self.stopping.is_set():
                        return
                    lifecycle = self.lifecycle_job
                    job = None if lifecycle is not None else self.pending
                    if lifecycle is None:
                        self.pending = None
                    self.inflight = job
                if lifecycle is not None:
                    outcome = self._execute_lifecycle(lifecycle)
                    projection = outcome["projection"]
                    retry.observe({"state": "succeeded"} if projection["state"] == "ready" else
                                  {"state": "failed", "message": projection["error"]["message"]})
                    with self.lock:
                        lifecycle["outcome"] = outcome
                        self.lifecycle_job = None
                        lifecycle["event"].set()
                        if self.pending is not None:
                            self.watcher.queue.put({})
                else:
                    outcome = self._generate(job["target"] if job is not None else None)
                    retry.observe(outcome)
                    with self.lock:
                        if job is not None:
                            job["outcome"] = outcome
                            job["event"].set()
                        self.inflight = None
                        if self.lifecycle_job is not None:
                            self.watcher.queue.put({})

    def _run_worker(self, directory):
        env = {key: value for key, value in os.environ.items() if key != "PYTHONHOME"}
        env["PYTHONPATH"] = str(ENGINE)
        with self.lock:
            if self.stopping.is_set():
                raise RuntimeError("Orchestrator is stopping")
            process = subprocess.Popen(
                [sys.executable, "-B", "-P", "-m", "WORKERS_beta_C69.WORKERS_beta_C69__shared",
                 "--generation-dir", directory], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, text=True, cwd=ENGINE, env=env, start_new_session=True)
            self.process = process
        try:
            stdout, stderr = process.communicate(json.dumps(self.binding), timeout=GENERATION_DEADLINE_SECONDS)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.communicate()
            raise RuntimeError("Worker deadline exceeded")
        finally:
            with self.lock:
                self.process = None
        if process.returncode:
            raise RuntimeError("Worker failed: " + stderr[-2048:])
        if stderr:
            sys.stderr.write(stderr[-8192:])
        result = json.loads(stdout)
        if not isinstance(result, dict) or set(result) != {"snapshot", "receipt", "graph"}:
            raise ValueError("Worker returned invalid generation")
        return result

    def _admit(self, directory, result, target=None):
        payload = {"instance_id": self.instance_id, **result,
                   "model": (Path(directory) / "model.json").read_bytes().decode("utf-8"),
                   "structure": (Path(directory) / "structure.json").read_bytes().decode("utf-8")}
        if target is not None:
            payload["refresh_target"] = target
        connection = UnixConnection(self.database_socket)
        try:
            connection.request("PUT", "/generation", json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                               {"Content-Type": "application/json"})
            response = connection.getresponse()
            body = response.read()
            if response.status != 200:
                raise RuntimeError("Kernel rejected generation: " + body.decode("utf-8", "replace")[:2048])
            result = json.loads(body)["result"]
            if target is not None:
                if not isinstance(result["generation"], str) or not isinstance(result["result_ids"], dict):
                    raise ValueError("Kernel returned invalid generation result")
                return {"generation": result["generation"], "result_ids": result["result_ids"]}
            return result["generation"]
        finally:
            connection.close()

    def _generate(self, target=None):
        with self.lock:
            self.active = {"state": "running", "started_at": time.time()}
        outcome = {"state": "failed", "code": "generation_failed"}
        try:
            with tempfile.TemporaryDirectory(prefix="anechoic-generation-") as temporary:
                directory = str(Path(temporary).resolve(strict=True))
                result = self._run_worker(directory)
                generation = self._admit(directory, result, target) if target is not None else self._admit(directory, result)
                outcome = ({"state": "succeeded", **generation} if target is not None
                           else {"state": "succeeded", "generation": generation})
        except (OSError, ValueError, TypeError, KeyError, RuntimeError, http.client.HTTPException) as error:
            outcome["message"] = str(error)[-2048:]
        finally:
            with self.lock:
                self.latest = {**self.active, **outcome, "finished_at": time.time()}
                self.active = None
        return outcome


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def respond(self, status, body):
        data = json.dumps(body, ensure_ascii=False, separators=(",", ":")).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        url = urlsplit(self.path)
        if url.path == "/health" and not url.query:
            return self.respond(200, {"result": {"instance_id": self.server.jobs.instance_id, "pid": os.getpid()}})
        if url.path == "/jobs/worker-runs":
            query = parse_qs(url.query, keep_blank_values=True)
            if query != {"instance_id": [self.server.jobs.instance_id]}:
                return self.respond(409, {"error": {"code": "instance_mismatch", "message": "Instance does not match"}})
            return self.respond(200, {"result": self.server.jobs.status()})
        self.respond(404, {"error": {"code": "not_found", "message": "Unknown endpoint"}})

    def do_POST(self):
        if self.path not in {"/jobs/build", "/jobs/lifecycle"}:
            return self.respond(404, {"error": {"code": "not_found", "message": "Unknown endpoint"}})
        try:
            length = int(self.headers.get("Content-Length", ""))
            if not 0 < length <= MAX_REQUEST_BYTES:
                raise ValueError("Invalid content length")
            request = json.loads(self.rfile.read(length))
        except (ValueError, UnicodeDecodeError):
            return self.respond(400, {"error": {"code": "invalid_request", "message": "Invalid JSON request"}})
        if self.path == "/jobs/lifecycle" and not isinstance(self.server.jobs, GenerationJobs):
            return self.respond(503, {"error": {"code": "unavailable", "message": "Lifecycle is unavailable"}})
        status, body = (self.server.jobs.lifecycle(request) if self.path == "/jobs/lifecycle"
                        else self.server.jobs.build(request))
        self.respond(status, body)


class Server(socketserver.ThreadingMixIn, socketserver.UnixStreamServer):
    daemon_threads = True

    def __init__(self, socket_path, instance_id, binding=None, database_socket=None, watch_code=False):
        self.jobs = (GenerationJobs(instance_id, binding, database_socket, watch_code)
                     if binding is not None else Jobs(instance_id))
        super().__init__(socket_path, Handler)
        os.chmod(socket_path, 0o600)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--socket", required=True)
    parser.add_argument("--instance-id", required=True)
    parser.add_argument("--binding-file")
    parser.add_argument("--database-socket")
    parser.add_argument("--watch-code", action="store_true")
    args = parser.parse_args()
    if not args.instance_id:
        parser.error("--instance-id must not be empty")
    if bool(args.binding_file) != bool(args.database_socket):
        parser.error("--binding-file and --database-socket must be supplied together")
    binding = None
    if args.binding_file:
        with open(args.binding_file, encoding="utf-8") as stream:
            binding = json.load(stream)
    with Server(args.socket, args.instance_id, binding, args.database_socket, args.watch_code) as server:
        signal.signal(signal.SIGTERM, signal.default_int_handler)
        try:
            if binding is not None:
                server.jobs.start()
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            if binding is not None:
                server.jobs.close()
            os.unlink(args.socket)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
