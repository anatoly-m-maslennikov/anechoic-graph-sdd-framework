"""HTTP server entry point for the beta Orchestrator."""
import argparse
import json
import math
import os
import signal
import socketserver
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlsplit

from .jobs import Jobs

MAX_REQUEST_BYTES = 65536

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
        from .ORCHESTRATOR_beta_C68__shared import GenerationJobs
        if self.path not in {"/jobs/build", "/jobs/lifecycle", "/jobs/abort"}:
            return self.respond(404, {"error": {"code": "not_found", "message": "Unknown endpoint"}})
        try:
            length = int(self.headers.get("Content-Length", ""))
            if not 0 < length <= MAX_REQUEST_BYTES:
                raise ValueError("Invalid content length")
            request = json.loads(self.rfile.read(length))
        except (ValueError, UnicodeDecodeError):
            return self.respond(400, {"error": {"code": "invalid_request", "message": "Invalid JSON request"}})
        if self.path in {"/jobs/lifecycle", "/jobs/abort"} and not isinstance(self.server.jobs, GenerationJobs):
            return self.respond(503, {"error": {"code": "unavailable", "message": "Lifecycle is unavailable"}})
        status, body = (self.server.jobs.lifecycle(request) if self.path == "/jobs/lifecycle"
                        else self.server.jobs.abort(request) if self.path == "/jobs/abort"
                        else self.server.jobs.build(request))
        self.respond(status, body)


class Server(socketserver.ThreadingMixIn, socketserver.UnixStreamServer):
    daemon_threads = True

    def __init__(self, socket_path, instance_id, binding=None, database_socket=None, watch_code=False,
                 worker_socket=None, worker_load_seconds=None):
        from .ORCHESTRATOR_beta_C68__shared import GenerationJobs
        self.jobs = (GenerationJobs(instance_id, binding, database_socket, watch_code, worker_socket, worker_load_seconds)
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
    parser.add_argument("--worker-socket")
    parser.add_argument("--worker-load-seconds", type=float)
    args = parser.parse_args()
    if not args.instance_id:
        parser.error("--instance-id must not be empty")
    if bool(args.binding_file) != bool(args.database_socket):
        parser.error("--binding-file and --database-socket must be supplied together")
    if bool(args.worker_socket) != (args.worker_load_seconds is not None):
        parser.error("--worker-socket and --worker-load-seconds must be supplied together")
    if args.worker_load_seconds is not None and (not math.isfinite(args.worker_load_seconds) or args.worker_load_seconds <= 0):
        parser.error("--worker-load-seconds must be finite and positive")
    binding = None
    if args.binding_file:
        with open(args.binding_file, encoding="utf-8") as stream:
            binding = json.load(stream)
    with Server(args.socket, args.instance_id, binding, args.database_socket, args.watch_code,
                args.worker_socket, args.worker_load_seconds) as server:
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


