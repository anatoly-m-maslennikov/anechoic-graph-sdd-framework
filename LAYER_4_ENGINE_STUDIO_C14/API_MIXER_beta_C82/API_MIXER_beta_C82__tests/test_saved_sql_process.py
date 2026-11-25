"""Exercise saved SQL through the C82 CLIs and a real Kernel."""

from hashlib import sha256
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
from urllib.parse import parse_qs, urlsplit
from uuid import UUID

import httpx2


ENGINE = Path(__file__).resolve().parents[2]
DIGEST = "a" * 64
INSTANCE = "b" * 64
KERNEL = "KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.DATABASE_SERVER_beta_C71__shared"


def generation():
    model = json.dumps({"model_sha256": "b" * 64, "binding_schema": 1, "modules": {"__init__.py": "d" * 64},
                        "module_order": [], "class_modules": {}, "bindings": {}}, indent=2)
    structure = json.dumps({"model_sha256": "b" * 64, "project": {"ref": "AN-S-1", "sha256": DIGEST},
                            "components": {}}, indent=2)
    return {"instance_id": INSTANCE, "snapshot": {"manifest_sha256": DIGEST, "atoms": []}, "model": model,
            "structure": structure, "graph": None, "receipt": {"manifest_sha256": DIGEST, "model_sha256": "b" * 64,
            "graph_sha256": sha256(b"null").hexdigest(), "model_descriptor_sha256": sha256(model.encode()).hexdigest(),
            "structure_sha256": sha256(structure.encode()).hexdigest()}}


class Server(socketserver.ThreadingMixIn, socketserver.UnixStreamServer):
    daemon_threads = True


class Jobs(BaseHTTPRequestHandler):
    def log_message(self, *_args):
        pass

    def do_GET(self):
        payload = {"result": {"instance_id": INSTANCE, "pid": os.getpid(), "startup_replay_pending": False, "watcher_active": True}}
        value = json.dumps(payload).encode()
        self.send_response(200)
        self.send_header("Content-Length", str(len(value)))
        self.end_headers()
        self.wfile.write(value)

    def do_POST(self):
        self.server.requests.append((self.path, json.loads(self.rfile.read(int(self.headers["Content-Length"])))))
        payload = {"result": {"write_state": "known", "projection": {"state": "ready"}, "lifecycle": {"outcome": "completed"}}}
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
            value = {"loaded_project_count": 1, "max_loaded_projects": 2, "loaded_project_processes": []}
        self.send(value)
        if operation == "lease":
            self.rfile.read(1)
            self.send(None)

    def send(self, value):
        self.wfile.write(json.dumps({"result": value}).encode() + b"\n")
        self.wfile.flush()


class SavedSqlProcessTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir="/tmp")
        self.root = Path(self.temp.name).resolve()
        self.processes, self.clients, self.servers = [], [], []
        self.env = {**os.environ, "PYTHONPATH": str(ENGINE), "ANECHOIC_LOG_LEVEL": "ERROR",
                    "ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY": str(ENGINE.parent / ".anechoic_tmp/workbench/extensions")}
        for name, handler in (("jobs", Jobs), ("owner", Owner)):
            server = Server(str(self.root / (name + ".sock")), handler)
            server.requests = []
            os.chmod(self.root / (name + ".sock"), 0o600)
            threading.Thread(target=server.serve_forever, daemon=True).start()
            self.servers.append(server)
        self.configure_owner()
        self.start_kernel()
        self.start_apis()

    def configure_owner(self):
        root = str(self.root)
        owner = self.servers[1]
        owner.binding = {"root": root, "control_root": root + "/control", "control_relative": "control",
                         "instance_id": INSTANCE, "project_name": "Project A", "project_prefix": "AN",
                         "manifest_path": root + "/manifest", "manifest_ref": "AN-S-1", "manifest_sha256": DIGEST,
                         "parameters": {"runtime": {"workbench": {"public_url": "https://configured.test/workbench"}}},
                         "host_root": None, "tool_blacklist": [], "release_workflows_enabled": False}
        owner.lease = {"database_socket": root + "/db.sock", "orchestrator_socket": root + "/jobs.sock",
                       "worker_binding": {"root": root, "control_root": "control", "manifest_path": "manifest",
                                          "manifest_sha256": DIGEST, "project_prefix": "AN"}}

    def start(self, module, args, socket_name):
        command = [sys.executable, "-B", "-P", "-m", module, *args]
        process = subprocess.Popen(command, cwd=ENGINE, env=self.env, stdin=subprocess.PIPE,
                                   stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        self.processes.append(process)
        path = self.root / socket_name
        deadline = time.monotonic() + 20
        while not path.exists() and process.poll() is None and time.monotonic() < deadline:
            time.sleep(0.05)
        if not path.exists():
            if process.poll() is None:
                process.terminate()
            self.fail(process.stderr.read().decode())
        client = httpx2.Client(transport=httpx2.HTTPTransport(uds=str(path)), base_url="http://private",
                               trust_env=False, timeout=20)
        self.clients.append(client)
        return client

    def start_kernel(self):
        args = ["--socket", str(self.root / "db.sock"), "--instance-id", INSTANCE, "--manifest-sha256", DIGEST,
                "--project-root", str(self.root), "--journal-relative", "control/journal"]
        self.kernel = self.start(KERNEL, args, "db.sock")
        response = self.kernel.put("/generation", json=generation())
        self.assertEqual(200, response.status_code, response.text)
        (self.root / "peers.ready").touch(mode=0o600)

    def start_direct(self, socket_name, public_url):
        root = str(self.root)
        direct = ["--role", "api", "--socket", str(self.root / socket_name), "--instance-id", INSTANCE,
                  "--project-root", root, "--control-root", "control", "--manifest-path", "manifest",
                  "--manifest-sha256", DIGEST, "--project-prefix", "AN", "--project-name", "Project A"]
        if public_url is not None:
            direct.extend(("--workbench-public-url", public_url))
        return self.start("API_MIXER_beta_C82.API_MIXER_beta_C82__shared", direct, socket_name)

    def start_apis(self):
        self.direct = self.start_direct("direct.sock", "https://configured.test/workbench")
        shared = ["--socket", str(self.root / "shared.sock"), "--peer-owner-socket", str(self.root / "owner.sock")]
        self.shared = self.start("API_MIXER_beta_C82.shared_runtime", shared, "shared.sock")

    def tearDown(self):
        for client in self.clients:
            client.close()
        for process in reversed(self.processes):
            if process is self.processes[0]:
                process.terminate()
            else:
                process.stdin.close()
            process.wait(timeout=10)
            if not process.stdin.closed:
                process.stdin.close()
            process.stderr.close()
        for server in self.servers:
            server.shutdown()
            server.server_close()
        self.temp.cleanup()

    def call(self, shared, name, args, *, base="http://example.test", asserted=True, session=None):
        body = {"name": name, "arguments": args.copy(), "session_id": session, "public_base_url": base}
        if shared:
            body["arguments"]["project_root"] = str(self.root)
        else:
            body.update(instance_id=INSTANCE, asserted_project_root=str(self.root) if asserted else None)
        return (self.shared if shared else self.direct).post("/tools", json=body).json()

    def value(self, shared, name, args, **options):
        result = self.call(shared, name, args, **options)
        self.assertIn("result", result, result)
        return result["result"]["value"]

    def test_direct_save_load_list_and_view(self):
        sql = " SELECT 43 AS answer\n"
        saved = self.value(False, "query_run", {"sql": sql, "save": True, "name": "Bookmark", "result_delivery": "inline"})
        self.assertEqual([[43]], saved["rows"])
        self.assertEqual(7, UUID(saved["saved_query_id"]).version)
        url = urlsplit(saved["saved_query_url"])
        self.assertEqual(("example.test", "/anechoic/workbench/Project%20A"), (url.netloc, url.path))
        self.assertEqual([str(self.root)], parse_qs(url.query)["project_root"])
        loaded = self.value(False, "query_load", {"reference": saved["saved_query_url"]})
        self.assertEqual((sql, "Bookmark"), (loaded["sql"], loaded["name"]))
        view = self.value(False, "view_save", {"sql": "SELECT missing_column", "name": "Snapshot"})
        self.assertEqual("view", view["kind"])
        self.assertEqual("SELECT missing_column", self.value(False, "query_load", {"reference": view["saved_query_id"]})["sql"])
        items = self.value(False, "query_saved_list", {"limit": 10})["items"]
        self.assertEqual({saved["saved_query_id"], view["saved_query_id"]}, {item["saved_query_id"] for item in items})

    def test_shared_links_and_input_refusals(self):
        saved = self.value(True, "query_run", {"sql": "SELECT 7", "save": True, "result_delivery": "inline"})
        loaded = self.value(True, "query_load", {"reference": saved["saved_query_url"]})
        self.assertEqual("SELECT 7", loaded["sql"])
        bad_link = saved["saved_query_url"].replace("example.test", "foreign.test")
        self.assertEqual("tool_input_invalid", self.call(True, "query_load", {"reference": bad_link})["error"]["code"])
        for name, args in (("query_run", {"sql": "SELECT 1", "name": "bad"}),
                           ("query_run", {"sql": "SELECT 1", "save": 1}),
                           ("view_save", {"sql": "SELECT 1", "workspace_id": "x"}),
                           ("query_saved_list", {"limit": True})):
            self.assertEqual("tool_input_invalid", self.call(True, name, args)["error"]["code"])
        configured = self.value(False, "query_load", {"reference": saved["saved_query_id"]}, base=None, asserted=False)
        self.assertTrue(configured["saved_query_url"].startswith("https://configured.test/workbench?"))

    def test_missing_or_invalid_public_url_preserves_saved_sql(self):
        sql = "SELECT 31"
        for index, public_url in enumerate((None, "https://user@configured.test/custom")):
            self.direct = self.start_direct(f"fallback-{index}.sock", public_url)
            workbench = {} if public_url is None else {"public_url": public_url}
            self.servers[1].binding["parameters"] = {"runtime": {"workbench": workbench}}
            for shared in (False, True):
                for operation, args in (("query_run", {"save": True, "result_delivery": "inline"}), ("view_save", {})):
                    with self.subTest(public_url=public_url, shared=shared, operation=operation):
                        saved = self.value(shared, operation, {"sql": sql, **args}, base=None, asserted=False)
                        saved_id = saved["saved_query_id"]
                        self.assertEqual(7, UUID(saved_id).version)
                        self.assertIsNone(saved["saved_query_url"])
                        self.assertEqual("workbench_url_unknown", saved["saved_query_url_reason"])
                        loaded = self.value(shared, "query_load", {"reference": saved_id}, base=None, asserted=False)
                        self.assertEqual((saved_id, sql), (loaded["saved_query_id"], loaded["sql"]))

    def test_save_existing_view_uses_its_workspace_identity(self):
        def kernel(operation, arguments):
            response = self.kernel.post("/workspace", json={"instance_id": INSTANCE, "operation": operation, "arguments": arguments})
            self.assertEqual(200, response.status_code, response.text)
            return response.json()["result"]
        workspace = kernel("workspace_open", {"session_id": "session-a"})
        view = {"workspace_id": workspace["workspace_id"], "view_id": workspace["active_view_id"]}
        kernel("view_update", {**view, "sql": "SELECT 12", "expected_revision": 0})
        saved = self.value(True, "view_save", view)
        self.assertEqual(view, {key: saved[key] for key in view})
        self.assertEqual("SELECT 12", self.value(True, "query_load", {"reference": saved["saved_query_id"]})["sql"])

    def test_workspace_session_binding_links_and_refusals(self):
        for shared, session in ((False, "direct-session"), (True, "shared-session")):
            opened = self.value(shared, "workspace_open", {}, session=session)
            self.assertEqual(session, opened["workspace_id"])
            self.assertEqual("Project A", opened["project_name"])
            self.assertEqual({"workspace": [session], "project_root": [str(self.root)]},
                             parse_qs(urlsplit(opened["workspace_url"]).query))
            loaded = self.value(shared, "workspace_get", {"workspace_id": session})
            self.assertEqual(opened, loaded)
            explicit = self.value(shared, "workspace_open", {"session_id": session + "-explicit"}, session=session)
            self.assertEqual(session + "-explicit", explicit["workspace_id"])
            items = self.value(shared, "workspace_list", {})["items"]
            self.assertIn({"workspace_id": session}, items)
            for name, args in (("workspace_open", {}), ("workspace_open", {"session_id": " "}),
                               ("workspace_get", {"workspace_id": ""}), ("workspace_list", {"extra": True})):
                self.assertEqual("tool_input_invalid", self.call(shared, name, args)["error"]["code"])

    def test_query_log_list_and_get(self):
        self.value(False, "query_run", {"sql": "SELECT 27", "result_delivery": "inline"})
        for shared in (False, True):
            items = self.value(shared, "query_log_list", {"limit": 1})["items"]
            self.assertEqual(1, len(items))
            record = self.value(shared, "query_log_get", {"log_id": items[0]["log_id"]})
            self.assertEqual(items[0], record)
            self.assertEqual(("SELECT 27", "success"), (record["sql"], record["outcome"]))
            for name, args in (("query_log_list", {"limit": True}), ("query_log_list", {"limit": 1001}),
                               ("query_log_get", {"log_id": " "})):
                self.assertEqual("tool_input_invalid", self.call(shared, name, args)["error"]["code"])

    def test_rebuild_qualified_query_and_flow_targets(self):
        for shared in (False, True):
            with self.subTest(shared=shared):
                run = self.value(shared, "query_run", {"sql": "SELECT 27", "result_delivery": "inline"})
                target = "workbench_results.query_" + run["query_id"]
                rebuilt = self.value(shared, "query_rebuild", {"target": target})
                self.assertEqual(target, rebuilt["target"])
                args = {"query_id": rebuilt["result_ids"][run["query_id"]], "result_delivery": "inline"}
                self.assertEqual([[27]], self.value(shared, "query_page", args)["rows"])
                for rejected in ("ops_ingestion_issues", "mrt_flow_events", "mrt_package_coupling", "biz_atoms"):
                    reply = self.call(shared, "query_rebuild", {"target": rejected})
                    self.assertEqual("tool_input_invalid", reply["error"]["code"], rejected)
        flow = self.value(False, "query_run", {"sql": "SELECT count(*) FROM main.src_flow_events", "result_delivery": "inline"})
        target = "main.src_flow_events"
        rebuilt = self.value(False, "query_rebuild", {"target": target})
        self.assertEqual(target, rebuilt["target"])
        self.assertIn(flow["query_id"], rebuilt["result_ids"])

    def test_view_family_direct_and_shared(self):
        for shared in (False, True):
            self.exercise_views(shared)

    def test_lifecycle_direct_and_shared_binding(self):
        for shared in (False, True):
            args = {"target": {"ref": "AN-S-1"}}
            result = self.value(shared, "atom_lifecycle_archive", args)
            self.assertEqual("completed", result["status"])
            request = {**self.servers[1].lease["worker_binding"], "instance_id": INSTANCE,
                       "name": "atom_lifecycle_archive", "arguments": args}
            self.assertEqual(("/jobs/lifecycle", request), self.servers[0].requests[-1])

    def exercise_views(self, shared):
        session = "views-shared" if shared else "views-direct"
        workspace = self.value(shared, "workspace_open", {"session_id": session})
        view = {"workspace_id": session, "view_id": workspace["active_view_id"]}
        update = {**view, "sql": "SELECT 42 AS answer", "expected_revision": 0}
        self.assertEqual(1, self.value(shared, "view_update", update)["revision"])
        self.assertTrue(self.value(shared, "view_check", view)["valid"])
        run = self.value(shared, "view_run", {**view, "save": True, "name": "Saved View Run"})
        self.assertEqual("success", run["status"])
        self.assertIn("saved_query_url", run)
        self.assertEqual("SELECT 42 AS answer", self.value(shared, "query_load", {"reference": run["saved_query_id"]})["sql"])
        grid = {"sort": [{"column": 0, "direction": "desc"}]}
        page = self.value(shared, "view_fetch", {**view, "result_delivery": "inline", "grid": grid})
        self.assertEqual([[42]], page["rows"])
        exported = self.value(shared, "view_fetch", view)["result_file"]
        self.assertTrue((self.root / exported["path"]).is_file())
        self.assertEqual(run["query_id"], self.value(shared, "view_get", view)["result"]["query_id"])
        created = self.value(shared, "view_create", {"workspace_id": session, "name": "Second", "position": "first"})
        second = {"workspace_id": session, "view_id": created["view_id"]}
        duplicate = self.value(shared, "view_duplicate", second)
        third = {"workspace_id": session, "view_id": duplicate["view_id"]}
        self.assertEqual("Renamed", self.value(shared, "view_rename", {**third, "name": "Renamed"})["name"])
        self.assertEqual(third["view_id"], self.value(shared, "view_focus", third)["active_view_id"])
        self.assertEqual(3, len(self.value(shared, "view_list", {"workspace_id": session})["views"]))
        self.value(shared, "view_remove", third)
        self.value(shared, "view_remove", second)
        self.assertEqual("workspace_error", self.call(shared, "view_remove", view)["error"]["code"])
        self.assertEqual("workspace_error", self.call(shared, "view_update", update)["error"]["code"])
        for name, args in (("view_run", {**view, "name": "without save"}),
                           ("view_update", {**update, "expected_revision": True}),
                           ("view_fetch", {**view, "page_size": 0}), ("view_get", {**view, "extra": 1})):
            self.assertEqual("tool_input_invalid", self.call(shared, name, args)["error"]["code"])


if __name__ == "__main__":
    unittest.main()
