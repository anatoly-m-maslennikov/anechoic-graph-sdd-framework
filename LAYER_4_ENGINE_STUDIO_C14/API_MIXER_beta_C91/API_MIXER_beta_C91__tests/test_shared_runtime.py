"""Exercise the shared API over a private peer-owner protocol fixture."""

import json
import os
from pathlib import Path
import socketserver
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from http.server import BaseHTTPRequestHandler

import httpx2


ENGINE = Path(__file__).resolve().parents[2]
DIGEST = "a" * 64
INSTANCE = "b" * 64
MODULE = "API_MIXER_beta_C91.shared_runtime"


class Server(socketserver.ThreadingMixIn, socketserver.UnixStreamServer):
    daemon_threads = True


class OwnerHandler(socketserver.StreamRequestHandler):
    def handle(self):
        request = json.loads(self.rfile.readline())
        self.server.requests.append(request)
        op = request["operation"]
        if op == "status":
            self.send({"result": {"loaded_project_count": 0, "max_loaded_projects": 2, "loaded_project_processes": []}})
        elif op == "select":
            self.select(request)
        elif op == "lease":
            self.send({"result": self.server.lease})
            self.server.releases.append(self.rfile.read(1))
            self.send({"result": None})

    def select(self, request):
        root = request.get("project_root")
        if root is None:
            return self.send({"error": "ValueError", "message": "missing_project_root"})
        if root is not None and root != self.server.binding["root"]:
            return self.send({"error": "ValueError", "message": "outside_project_root"})
        value = self.server.binding.copy()
        if self.server.stale and len([r for r in self.server.requests if r["operation"] == "select"]) > 1:
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
            return self.reply({"result": {"tables": {"atoms": [{"name": "reference", "type": "VARCHAR"}]}}})
        value = {"instance_id": INSTANCE, "pid": os.getpid()}
        if self.server.kind == "db":
            value.update(manifest_sha256=self.server.digest, ready=True, generation="g1")
        else:
            value["startup_replay_pending"] = False
            value["watcher_active"] = True
        self.reply({"result": value})

    def do_POST(self):
        data = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        self.server.requests.append(data)
        value = {"query_id": "q", "columns": [{"name": "answer", "type": "INTEGER", "has_values": True}],
                 "rows": [[42]], "offset": 0, "has_more": False}
        self.reply({"result": value})

    def reply(self, value):
        data = json.dumps(value).encode()
        self.send_response(200)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


class SharedRuntimeTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir="/tmp")
        self.path = Path(self.temp.name).resolve()
        self.servers = []
        for name, handler in (("owner", OwnerHandler), ("db", PeerHandler), ("jobs", PeerHandler)):
            server = Server(str(self.path / (name + ".sock")), handler)
            server.kind, server.requests, server.digest = name, [], DIGEST
            threading.Thread(target=server.serve_forever, daemon=True).start()
            self.servers.append(server)
        owner = self.servers[0]
        owner.stale, owner.releases = False, []
        root = str(self.path)
        owner.binding = {"root": root, "control_root": root + "/control", "control_relative": "control",
                         "instance_id": INSTANCE, "project_name": "Project", "project_prefix": "AN",
                         "manifest_path": root + "/manifest", "manifest_ref": "AN-S-1", "manifest_sha256": DIGEST,
                         "parameters": {}, "host_root": None, "tool_blacklist": [], "release_workflows_enabled": False}
        owner.lease = {"database_socket": root + "/db.sock", "orchestrator_socket": root + "/jobs.sock",
                       "worker_binding": {"root": root, "control_root": "control", "manifest_path": "manifest",
                                          "manifest_sha256": DIGEST, "project_prefix": "AN"}}
        args = [sys.executable, "-B", "-P", "-m", MODULE, "--socket", root + "/api.sock", "--host-settings", "ignored",
                "--peer-owner-socket", root + "/owner.sock"]
        env = {**os.environ, "PYTHONPATH": str(ENGINE), "ANECHOIC_SHARED_RUNTIME_ID": "runtime"}
        self.process = subprocess.Popen(args, cwd=ENGINE, env=env, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        self.client = httpx2.Client(transport=httpx2.HTTPTransport(uds=root + "/api.sock"), base_url="http://private",
                                    trust_env=False, timeout=5)
        self.wait_ready()

    def wait_ready(self):
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            if self.process.poll() is not None:
                self.fail(self.process.stderr.read().decode())
            if (self.path / "api.sock").exists():
                try:
                    if self.client.get("/health").json().get("result", {}).get("initialized"):
                        return
                except httpx2.TransportError:
                    pass
            time.sleep(0.05)
        self.fail("Shared API did not start")

    def tearDown(self):
        self.client.close()
        self.process.stdin.close()
        self.process.wait(timeout=10)
        self.process.stderr.close()
        for server in self.servers:
            server.shutdown()
            server.server_close()
        self.temp.cleanup()

    def call(self, name="query_run", arguments=None, *, headers=None):
        return self.client.post("/tools", json={"name": name, "arguments": arguments or {},
                                                "session_id": None, "public_base_url": None}, headers=headers).json()

    def test_explicit_selection_query_and_release(self):
        catalog = self.client.get("/tools").json()["result"]["tools"]
        self.assertEqual({"query_run", "query_check", "query_page", "query_schema",
                          "iwe_console_status", "iwe_console_abort", "workbench_status", "workbench_abort", "query_rebuild",
                          "query_load", "query_saved_list", "view_save", "workspace_open", "workspace_list",
                          "workspace_get", "query_log_list", "query_log_get", "view_create", "view_duplicate", "view_list",
                          "view_get", "view_update", "view_focus", "view_rename", "view_remove", "view_run", "view_check", "view_fetch",
                          "atom_lifecycle_create_draft", "atom_lifecycle_update", "atom_lifecycle_promote_draft", "atom_lifecycle_change_status", "atom_lifecycle_archive", "atom_lifecycle_create_asset", "atom_lifecycle_direct_update", "iwe_console_atom_document"},
                         {t["name"] for t in catalog})
        self.assertTrue(all("project_root" in t["inputSchema"]["required"] for t in catalog))
        selected = self.client.post("/selection", json={"project_root": str(self.path)}).json()["result"]
        self.assertEqual({"instance_id": INSTANCE, "project_name": "Project", "project_prefix": "AN"}, selected)
        self.assertEqual({"operation": "select", "project_root": str(self.path)}, self.servers[0].requests[-1])
        result = self.call(arguments={"project_root": str(self.path), "sql": "SELECT 42", "result_delivery": "inline"},
                           headers={"X-Anechoic-Project-Instance": selected["instance_id"]})
        self.assertEqual([[42]], result["result"]["value"]["rows"])
        self.assertEqual({"prefix": "AN", "instance_id": INSTANCE}, result["project"])
        self.assertEqual([b"R"], self.servers[0].releases)
        self.assertEqual(INSTANCE, self.servers[1].requests[-1]["instance_id"])

    def test_rebound_project_refuses_lifecycle_before_a_lease_or_write(self):
        owner, database, jobs = self.servers
        root = str(self.path)
        selected = self.client.post("/selection", json={"project_root": root}).json()["result"]
        owner.binding["instance_id"] = "c" * 64
        result = self.call("atom_lifecycle_archive", {"project_root": root, "target": {"ref_id": "AN-S-1@1"}},
                           headers={"X-Anechoic-Project-Instance": selected["instance_id"]})
        self.assertEqual("project_declarations_stale", result["error"]["code"])
        self.assertNotIn("result", result)
        self.assertEqual(["select", "select"], [r["operation"] for r in owner.requests if r["operation"] != "status"])
        self.assertEqual([], database.requests)
        self.assertEqual([], jobs.requests)

    def test_root_required_blacklist_and_binding_checks(self):
        owner = self.servers[0]
        self.assertEqual("missing_project_root", self.call(arguments={"sql": "SELECT 1"})["error"]["code"])
        self.assertEqual("outside_project_root", self.call(arguments={"project_root": "/other", "sql": "SELECT 1"})["error"]["code"])
        root = str(self.path)
        owner.binding["tool_blacklist"] = ["query_run"]
        self.assertEqual("tool_unavailable", self.call(arguments={"project_root": root, "sql": "SELECT 1"})["error"]["code"])
        for denied, called in (("workbench_status", "iwe_console_status"),
                               ("iwe_console_abort", "workbench_abort")):
            owner.binding["tool_blacklist"] = [denied]
            self.assertEqual("tool_unavailable", self.call(called, {"project_root": root})["error"]["code"])
        owner.binding["tool_blacklist"] = []
        self.servers[1].digest = "c" * 64
        self.assertEqual("project_declarations_stale", self.call(arguments={"project_root": root, "sql": "SELECT 1"})["error"]["code"])
        self.assertEqual([b"R"], owner.releases)

    def test_stale_reselection_discards_result(self):
        self.servers[0].stale = True
        response = self.call(arguments={"project_root": str(self.path), "sql": "SELECT 1"})
        self.assertEqual("project_declarations_stale", response["error"]["code"])
        self.assertNotIn("result", response)
        self.assertEqual([b"R"], self.servers[0].releases)

    def test_read_only_family_and_tool_errors(self):
        root = {"project_root": str(self.path)}
        checked = self.call("query_check", {**root, "sql": "SELECT 42"})["result"]["value"]
        self.assertEqual((True, 1), (checked["valid"], checked["row_count"]))
        page = self.call("query_page", {**root, "query_id": "q", "result_delivery": "inline"})
        self.assertEqual([[42]], page["result"]["value"]["rows"])
        self.assertIn("atoms", self.call("query_schema", root)["result"]["value"]["tables"])
        failure = self.call("query_page", {**root, "query_id": "q", "page_size": True})
        self.assertEqual("tool_input_invalid", failure["error"]["code"])
        self.assertEqual("tool", failure["error"]["scope"])
        self.assertEqual([b"R"] * 4, self.servers[0].releases)
        self.assertEqual("missing_project_root", self.call("query_schema")["error"]["code"])

    def test_invalid_selection_envelope_is_domain_refusal(self):
        for value in ([], {}, {"project_root": None}, {"project_root": 42}, {"extra": 1}):
            response = self.client.post("/selection", json=value)
            self.assertEqual("invalid_project_root", response.json()["error"]["code"])

    def test_lifecycle_refuses_foreign_lease_before_write(self):
        self.servers[0].lease["worker_binding"]["project_prefix"] = "OTHER"
        result = self.call("atom_lifecycle_archive", {"project_root": str(self.path), "target": {"ref": "AN-S-1"}})
        self.assertEqual("project_declarations_stale", result["error"]["code"])
        self.assertEqual([], self.servers[2].requests)
        self.assertEqual([b"R"], self.servers[0].releases)


if __name__ == "__main__":
    unittest.main()
