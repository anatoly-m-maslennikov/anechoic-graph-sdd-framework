"""Private HTTP peers for C91 process tests."""

import json
import os
import socketserver
from hashlib import sha256
from http.server import BaseHTTPRequestHandler

DIGEST = "a" * 64
INSTANCE = "b" * 64


class Server(socketserver.ThreadingMixIn, socketserver.UnixStreamServer):
    daemon_threads = True


class ApiPeer(BaseHTTPRequestHandler):
    def log_message(self, *_args):
        pass

    def do_GET(self):
        if self.path.startswith("/schema?"):
            self.server.schema_paths.append(self.path)
            schema = getattr(
                self.server,
                "schema",
                {
                    "tables": {
                        "atoms": [{"name": "reference", "type": "VARCHAR"}]
                    }
                },
            )
            self.reply({"result": schema})
            return
        result = {"instance_id": "instance", "pid": os.getpid()}
        if self.server.kind == "db":
            result.update(
                manifest_sha256=DIGEST,
                ready=True,
                generation="g1",
                archive_pending=False,
            )
        else:
            result.update(startup_replay_pending=False, watcher_active=True)
        self.reply({"result": result})

    def do_POST(self):
        data = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        self.server.received.append(data)
        if data.get("sql") == "DELETE FROM atoms" or data.get("grid") == {
            "bad": True
        }:
            self.reply(
                {
                    "error": {
                        "code": "invalid_query",
                        "message": "invalid query",
                    }
                }
            )
            return
        page = {
            "query_id": "query",
            "columns": [
                {"name": "answer", "type": "INTEGER", "has_values": True}
            ],
            "rows": [[42]],
            "offset": 0,
            "has_more": False,
        }
        if getattr(self.server, "invalid", False):
            page["columns"] = "invalid"
        self.reply({"result": page})

    def reply(self, payload):
        value = json.dumps(payload).encode()
        self.send_response(200)
        self.send_header("Content-Length", str(len(value)))
        self.end_headers()
        self.wfile.write(value)


class Jobs(BaseHTTPRequestHandler):
    def log_message(self, *_args):
        pass

    def do_GET(self):
        payload = {
            "result": {
                "instance_id": INSTANCE,
                "pid": os.getpid(),
                "startup_replay_pending": False,
                "watcher_active": True,
            }
        }
        value = json.dumps(payload).encode()
        self.send_response(200)
        self.send_header("Content-Length", str(len(value)))
        self.end_headers()
        self.wfile.write(value)

    def do_POST(self):
        self.server.requests.append(
            (
                self.path,
                json.loads(
                    self.rfile.read(int(self.headers["Content-Length"]))
                ),
            )
        )
        payload = (
            {"result": {"ref_id": "AN-S-1", "body": "text"}}
            if self.path == "/jobs/atom-document"
            else {
                "result": {
                    "write_state": "known",
                    "projection": {"state": "ready"},
                    "lifecycle": {"outcome": "completed"},
                }
            }
        )
        value = json.dumps(payload).encode()
        self.send_response(200)
        self.send_header("Content-Length", str(len(value)))
        self.end_headers()
        self.wfile.write(value)


class Owner(socketserver.StreamRequestHandler):
    def handle(self):
        request = json.loads(self.rfile.readline())
        operation = request["operation"]
        if operation == "select":
            value = self.server.binding
        elif operation == "lease":
            value = self.server.lease
        else:
            value = {
                "loaded_project_count": 1,
                "max_loaded_projects": 2,
                "loaded_project_processes": [],
            }
        self.send(value)
        if operation == "lease":
            self.rfile.read(1)
            self.send(None)

    def send(self, value):
        self.wfile.write(json.dumps({"result": value}).encode() + b"\n")
        self.wfile.flush()


def saved_sql_generation():
    model = json.dumps(
        {
            "model_sha256": "b" * 64,
            "binding_schema": 1,
            "modules": {"__init__.py": "d" * 64},
            "module_order": [],
            "class_modules": {},
            "bindings": {},
        },
        indent=2,
    )
    structure = json.dumps(
        {
            "model_sha256": "b" * 64,
            "project": {"ref": "AN-S-1", "sha256": DIGEST},
            "components": {},
        },
        indent=2,
    )
    return {
        "instance_id": INSTANCE,
        "snapshot": {"manifest_sha256": DIGEST, "atoms": []},
        "model": model,
        "structure": structure,
        "graph": None,
        "receipt": {
            "manifest_sha256": DIGEST,
            "model_sha256": "b" * 64,
            "graph_sha256": sha256(b"null").hexdigest(),
            "model_descriptor_sha256": sha256(model.encode()).hexdigest(),
            "structure_sha256": sha256(structure.encode()).hexdigest(),
        },
    }
