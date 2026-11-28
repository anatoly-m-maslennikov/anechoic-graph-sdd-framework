"""Simulate private projection peers for the API process tests."""

import json
import os
import socketserver
from http.server import BaseHTTPRequestHandler

DIGEST = "a" * 64
INSTANCE = "b" * 64
QUERY_ID = "c" * 32


class Server(socketserver.ThreadingMixIn, socketserver.UnixStreamServer):
    daemon_threads = True


class Peer(BaseHTTPRequestHandler):
    def log_message(self, *_args):
        pass

    def do_GET(self):
        self.server.requests.append(("GET", self.path, None))
        if getattr(self.server, "unreachable", False):
            self.close_connection = True
            return
        if self.path.startswith("/jobs/worker-runs"):
            runs = {
                "active": {
                    "state": "running",
                    "run_id": "run-1",
                    "worker_alive": True,
                },
                "latest": {"state": "succeeded", "finished_at": 1.0},
                "archive": {"state": "ready"},
            }
            return self.reply({"result": getattr(self.server, "runs", runs)})
        if self.path.startswith("/ingestion/issues"):
            return self.reply({"result": {"rows": [{"code": "warning"}]}})
        result = {"instance_id": INSTANCE, "pid": os.getpid()}
        if self.server.kind == "db":
            ready = getattr(self.server, "ready", False)
            result.update(
                manifest_sha256=DIGEST,
                ready=ready,
                generation="g1" if ready else None,
            )
            pending = getattr(self.server, "archive_pending", None)
            if pending is not None:
                result["archive_pending"] = pending
        else:
            result["startup_replay_pending"] = getattr(
                self.server, "startup_replay_pending", True
            )
            result["watcher_active"] = getattr(
                self.server, "watcher_active", True
            )
        self.reply({"result": result})

    def do_POST(self):
        data = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        self.server.requests.append(("POST", self.path, data))
        if self.path == "/database":
            if hasattr(self.server, "entered"):
                self.server.entered.set()
                if not self.server.release.wait(8):
                    return
            result = {
                "query_id": QUERY_ID,
                "columns": [
                    {"name": "answer", "type": "INTEGER", "has_values": True}
                ],
                "rows": [[42]],
                "offset": 0,
                "has_more": False,
            }
        elif self.path == "/jobs/abort":
            result = {"run_id": data["run_id"], "state": "aborting"}
        else:
            result = {"result_ids": {QUERY_ID: "d" * 32}}
        self.reply({"result": result})

    def reply(self, value):
        data = json.dumps(value).encode()
        self.send_response(200)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


class Owner(socketserver.StreamRequestHandler):
    def handle(self):
        request = json.loads(self.rfile.readline())
        self.server.requests.append(request)
        operation = request["operation"]
        if operation == "status":
            value = {
                "loaded_project_count": 0,
                "max_loaded_projects": 2,
                "loaded_project_processes": [],
            }
        elif operation == "select":
            value = self.server.binding
        else:
            value = (
                self.server.lease
                if request["start"] or not self.server.cold
                else None
            )
        self.send(value)
        if operation == "lease":
            self.server.releases.append(self.rfile.read(1))
            self.send(None)

    def send(self, value):
        self.wfile.write(json.dumps({"result": value}).encode() + b"\n")
        self.wfile.flush()
