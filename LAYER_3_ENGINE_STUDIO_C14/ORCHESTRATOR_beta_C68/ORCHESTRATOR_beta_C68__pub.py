"""Private, single-build Orchestrator for the pinned beta Worker."""
from __future__ import annotations

import argparse
import json
import http.client
import os
from pathlib import Path
import socketserver
import socket
import signal
import subprocess
import sys
import threading
import tempfile
import time
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlsplit

ENGINE = Path(__file__).resolve().parents[1]
FIELDS = {"instance_id", "root", "control_root", "manifest_path", "manifest_sha256", "project_prefix"}
DEADLINE_SECONDS = 120
GENERATION_DEADLINE_SECONDS = 150
MAX_REQUEST_BYTES = 65536


class Jobs:
    def __init__(self, instance_id):
        self.instance_id = instance_id
        self.lock = threading.Lock()
        self.active = None
        self.latest = None

    def status(self):
        with self.lock:
            return {"active": self.active, "latest": self.latest}

    def build(self, request):
        if not isinstance(request, dict) or set(request) != FIELDS:
            return 400, {"error": {"code": "invalid_request", "message": "Invalid build fields"}}
        if request["instance_id"] != self.instance_id:
            return 409, {"error": {"code": "instance_mismatch", "message": "Instance does not match"}}
        with self.lock:
            if self.active is not None:
                return 409, {"error": {"code": "build_active", "message": "A build is already active"}}
            self.active = {"state": "running", "started_at": time.time()}
        outcome = {"state": "failed", "code": "internal_error"}
        try:
            binding = {key: value for key, value in request.items() if key != "instance_id"}
            env = {key: value for key, value in os.environ.items() if key != "PYTHONHOME"}
            env["PYTHONPATH"] = str(ENGINE)
            process = subprocess.run(
                [sys.executable, "-B", "-P", "-m", "WORKERS_beta_C69.WORKERS_beta_C69__pub"],
                input=json.dumps(binding), text=True, capture_output=True,
                timeout=DEADLINE_SECONDS, cwd=ENGINE, env=env, check=False)
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
                self.latest = {**self.active, **outcome, "finished_at": time.time()}
                self.active = None


class UnixConnection(http.client.HTTPConnection):
    def __init__(self, path):
        super().__init__("localhost", timeout=30)
        self.path = path

    def connect(self):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.settimeout(self.timeout)
        self.sock.connect(self.path)


class GenerationJobs(Jobs):
    def __init__(self, instance_id, binding, database_socket):
        super().__init__(instance_id)
        if not isinstance(binding, dict) or set(binding) != FIELDS - {"instance_id"}:
            raise ValueError("Invalid binding fields")
        if not all(isinstance(value, str) and value for value in binding.values()):
            raise ValueError("Invalid binding values")
        self.binding = binding
        self.database_socket = database_socket
        self.stopping = threading.Event()
        self.process = None
        sys.path.insert(0, str(ENGINE))
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.source_watcher__pub import SourceWatcher
        root = Path(binding["root"])
        self.watcher = SourceWatcher(root, root / binding["control_root"], poll_bind_mount=True, watch_root_files=True)
        self.thread = None

    def start(self):
        self.watcher.start()
        self.thread = threading.Thread(target=self._watch, daemon=True)
        self.thread.start()

    def close(self):
        self.stopping.set()
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
        return 409, {"error": {"code": "managed_build", "message": "Builds are managed by the source watcher"}}

    def _watch(self):
        self._generate()
        while not self.stopping.is_set():
            changes = self.watcher.changes(0.5)
            if any(str(change.get(key) or "").lower().endswith(".md")
                   for change in changes for key in ("old_path", "new_path")):
                self._generate()

    def _run_worker(self, directory):
        env = {key: value for key, value in os.environ.items() if key != "PYTHONHOME"}
        env["PYTHONPATH"] = str(ENGINE)
        with self.lock:
            if self.stopping.is_set():
                raise RuntimeError("Orchestrator is stopping")
            process = subprocess.Popen(
                [sys.executable, "-B", "-P", "-m", "WORKERS_beta_C69.WORKERS_beta_C69__pub",
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
        result = json.loads(stdout)
        if not isinstance(result, dict) or set(result) != {"snapshot", "receipt"}:
            raise ValueError("Worker returned invalid generation")
        return result

    def _admit(self, directory, result):
        payload = {"instance_id": self.instance_id, **result,
                   "model": (Path(directory) / "model.json").read_bytes().decode("utf-8"),
                   "structure": (Path(directory) / "structure.json").read_bytes().decode("utf-8")}
        connection = UnixConnection(self.database_socket)
        try:
            connection.request("PUT", "/generation", json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                               {"Content-Type": "application/json"})
            response = connection.getresponse()
            body = response.read()
            if response.status != 200:
                raise RuntimeError("Kernel rejected generation: " + body.decode("utf-8", "replace")[:2048])
            return json.loads(body)["result"]["generation"]
        finally:
            connection.close()

    def _generate(self):
        with self.lock:
            self.active = {"state": "running", "started_at": time.time()}
        outcome = {"state": "failed", "code": "generation_failed"}
        try:
            with tempfile.TemporaryDirectory(prefix="anechoic-generation-") as temporary:
                directory = str(Path(temporary).resolve(strict=True))
                generation = self._admit(directory, self._run_worker(directory))
                outcome = {"state": "succeeded", "generation": generation}
        except (OSError, ValueError, TypeError, KeyError, RuntimeError, http.client.HTTPException) as error:
            outcome["message"] = str(error)[-2048:]
        finally:
            with self.lock:
                self.latest = {**self.active, **outcome, "finished_at": time.time()}
                self.active = None


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
        if self.path != "/jobs/build":
            return self.respond(404, {"error": {"code": "not_found", "message": "Unknown endpoint"}})
        try:
            length = int(self.headers.get("Content-Length", ""))
            if not 0 < length <= MAX_REQUEST_BYTES:
                raise ValueError("Invalid content length")
            request = json.loads(self.rfile.read(length))
        except (ValueError, UnicodeDecodeError):
            return self.respond(400, {"error": {"code": "invalid_request", "message": "Invalid JSON request"}})
        status, body = self.server.jobs.build(request)
        self.respond(status, body)


class Server(socketserver.ThreadingMixIn, socketserver.UnixStreamServer):
    daemon_threads = True

    def __init__(self, socket_path, instance_id, binding=None, database_socket=None):
        self.jobs = (GenerationJobs(instance_id, binding, database_socket)
                     if binding is not None else Jobs(instance_id))
        super().__init__(socket_path, Handler)
        os.chmod(socket_path, 0o600)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--socket", required=True)
    parser.add_argument("--instance-id", required=True)
    parser.add_argument("--binding-file")
    parser.add_argument("--database-socket")
    args = parser.parse_args()
    if not args.instance_id:
        parser.error("--instance-id must not be empty")
    if bool(args.binding_file) != bool(args.database_socket):
        parser.error("--binding-file and --database-socket must be supplied together")
    binding = None
    if args.binding_file:
        with open(args.binding_file, encoding="utf-8") as stream:
            binding = json.load(stream)
    with Server(args.socket, args.instance_id, binding, args.database_socket) as server:
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
