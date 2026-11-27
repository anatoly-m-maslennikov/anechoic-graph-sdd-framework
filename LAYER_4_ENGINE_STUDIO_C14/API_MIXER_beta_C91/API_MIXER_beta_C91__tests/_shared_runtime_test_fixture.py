"""Protocol peers and Tool names for shared-runtime tests."""

import json
import os
import socketserver
from http.server import BaseHTTPRequestHandler

INSTANCE = "b" * 64


class Server(socketserver.ThreadingMixIn, socketserver.UnixStreamServer):
    daemon_threads = True


class OwnerHandler(socketserver.StreamRequestHandler):
    def handle(self):
        request = json.loads(self.rfile.readline())
        self.server.requests.append(request)
        op = request["operation"]
        if op == "status":
            self.send(
                {
                    "result": {
                        "loaded_project_count": 0,
                        "max_loaded_projects": 2,
                        "loaded_project_processes": [],
                    }
                }
            )
        elif op == "select":
            self.select(request)
        elif op == "lease":
            self.send({"result": self.server.lease})
            self.server.releases.append(self.rfile.read(1))
            self.send({"result": None})

    def select(self, request):
        root = request.get("project_root")
        if root is None:
            return self.send(
                {"error": "ValueError", "message": "missing_project_root"}
            )
        if root is not None and root != self.server.binding["root"]:
            return self.send(
                {"error": "ValueError", "message": "outside_project_root"}
            )
        value = self.server.binding.copy()
        if (
            self.server.stale
            and len(
                [r for r in self.server.requests if r["operation"] == "select"]
            )
            > 1
        ):
            value["manifest_sha256"] = "c" * 64
        self.send({"result": value})

    def send(self, value):
        self.wfile.write(json.dumps(value).encode() + b"\n")
        self.wfile.flush()


class PeerHandler(BaseHTTPRequestHandler):
    def log_message(self, *_args):
        pass

    def do_GET(self):
        if self.path.startswith("/schema?"):
            return self.reply(
                {
                    "result": {
                        "tables": {
                            "atoms": [{"name": "reference", "type": "VARCHAR"}]
                        }
                    }
                }
            )
        value = {"instance_id": INSTANCE, "pid": os.getpid()}
        if self.server.kind == "db":
            value.update(
                manifest_sha256=self.server.digest, ready=True, generation="g1"
            )
        else:
            value["startup_replay_pending"] = False
            value["watcher_active"] = True
        self.reply({"result": value})

    def do_POST(self):
        data = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        self.server.requests.append(data)
        value = {
            "query_id": "q",
            "columns": [
                {"name": "answer", "type": "INTEGER", "has_values": True}
            ],
            "rows": [[42]],
            "offset": 0,
            "has_more": False,
        }
        self.reply({"result": value})

    def reply(self, value):
        data = json.dumps(value).encode()
        self.send_response(200)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


EXPECTED_TOOL_NAMES = {
    "query_run",
    "query_check",
    "query_page",
    "query_schema",
    "iwe_console_status",
    "iwe_console_abort",
    "workbench_status",
    "workbench_abort",
    "query_rebuild",
    "query_load",
    "query_saved_list",
    "view_save",
    "workspace_open",
    "workspace_list",
    "workspace_get",
    "query_log_list",
    "query_log_get",
    "view_create",
    "view_duplicate",
    "view_list",
    "view_get",
    "view_update",
    "view_focus",
    "view_rename",
    "view_remove",
    "view_run",
    "view_check",
    "view_fetch",
    "atom_lifecycle_create_draft",
    "atom_lifecycle_update",
    "atom_lifecycle_promote_draft",
    "atom_lifecycle_change_status",
    "atom_lifecycle_archive",
    "atom_lifecycle_create_asset",
    "atom_lifecycle_direct_update",
    "iwe_console_atom_document",
}
