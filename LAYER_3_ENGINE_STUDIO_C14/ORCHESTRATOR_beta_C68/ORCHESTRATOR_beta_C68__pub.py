"""Private, single-build Orchestrator for the pinned beta Worker."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import socketserver
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlsplit

ENGINE = Path(__file__).resolve().parents[1]
FIELDS = {"instance_id", "root", "control_root", "manifest_path", "manifest_sha256", "project_prefix"}
DEADLINE_SECONDS = 120
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

    def __init__(self, socket_path, instance_id):
        self.jobs = Jobs(instance_id)
        super().__init__(socket_path, Handler)
        os.chmod(socket_path, 0o600)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--socket", required=True)
    parser.add_argument("--instance-id", required=True)
    args = parser.parse_args()
    if not args.instance_id:
        parser.error("--instance-id must not be empty")
    with Server(args.socket, args.instance_id) as server:
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            os.unlink(args.socket)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
