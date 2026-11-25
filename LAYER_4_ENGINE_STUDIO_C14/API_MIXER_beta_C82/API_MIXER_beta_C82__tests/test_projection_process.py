"""Exercise projection control through both API CLI entry points."""

import json
import os
import socketserver
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler
from pathlib import Path

import httpx2

ENGINE = Path(__file__).resolve().parents[2]
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
            runs = {"active": {"state": "running", "run_id": "run-1", "worker_alive": True},
                    "latest": {"state": "succeeded", "finished_at": 1.0}, "archive": {"state": "ready"}}
            return self.reply({"result": getattr(self.server, "runs", runs)})
        if self.path.startswith("/ingestion/issues"):
            return self.reply({"result": {"rows": [{"code": "warning"}]}})
        result = {"instance_id": INSTANCE, "pid": os.getpid()}
        if self.server.kind == "db":
            ready = getattr(self.server, "ready", False)
            result.update(manifest_sha256=DIGEST, ready=ready, generation="g1" if ready else None)
            pending = getattr(self.server, "archive_pending", None)
            if pending is not None:
                result["archive_pending"] = pending
        else:
            result["startup_replay_pending"] = getattr(self.server, "startup_replay_pending", True)
        self.reply({"result": result})

    def do_POST(self):
        data = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        self.server.requests.append(("POST", self.path, data))
        if self.path == "/database":
            if hasattr(self.server, "entered"):
                self.server.entered.set()
                if not self.server.release.wait(8):
                    return
            result = {"query_id": QUERY_ID, "columns": [{"name": "answer", "type": "INTEGER", "has_values": True}],
                      "rows": [[42]], "offset": 0, "has_more": False}
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
            value = {"loaded_project_count": 0, "max_loaded_projects": 2, "loaded_project_processes": []}
        elif operation == "select":
            value = self.server.binding
        else:
            value = self.server.lease if request["start"] or not self.server.cold else None
        self.send(value)
        if operation == "lease":
            self.server.releases.append(self.rfile.read(1))
            self.send(None)

    def send(self, value):
        self.wfile.write(json.dumps({"result": value}).encode() + b"\n")
        self.wfile.flush()


class ProjectionTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir="/tmp")
        self.path = Path(self.temp.name).resolve()
        self.servers = []
        for kind, handler in (("db", Peer), ("jobs", Peer), ("owner", Owner)):
            server = Server(str(self.path / (kind + ".sock")), handler)
            os.chmod(self.path / (kind + ".sock"), 0o600)
            server.kind, server.requests = kind, []
            threading.Thread(target=server.serve_forever, daemon=True).start()
            self.servers.append(server)
        self.prepare_owner()
        self.manifest = self.path / "manifest"
        self.manifest.write_text("manifest")
        info = self.manifest.stat()
        self.version = [info.st_dev, info.st_ino, info.st_mode, info.st_size, info.st_mtime_ns, info.st_ctime_ns]
        self.gate = self.path / "gate"
        (self.path / "peers.ready").touch(mode=0o600)
        self.processes, self.clients = [], []
        self.start_apis()

    def prepare_owner(self):
        root = str(self.path)
        owner = self.servers[2]
        owner.releases, owner.cold = [], True
        owner.binding = {"root": root, "control_root": root + "/control", "control_relative": "control",
                         "instance_id": INSTANCE, "project_name": "Project", "project_prefix": "AN",
                         "manifest_path": root + "/manifest", "manifest_ref": "AN-S-1", "manifest_sha256": DIGEST,
                         "parameters": {}, "host_root": None, "tool_blacklist": [], "release_workflows_enabled": False}
        self.worker_binding = {"root": root, "control_root": "control", "manifest_path": "manifest",
                               "manifest_sha256": DIGEST, "project_prefix": "AN"}
        owner.lease = {"database_socket": root + "/db.sock", "orchestrator_socket": root + "/jobs.sock",
                       "worker_binding": self.worker_binding}

    def start_apis(self):
        root = str(self.path)
        direct = ["API_MIXER_beta_C82.API_MIXER_beta_C82__shared", "--role", "api", "--socket", root + "/direct.sock",
                  "--instance-id", INSTANCE, "--project-root", root, "--control-root", "control",
                  "--manifest-path", "manifest", "--manifest-sha256", DIGEST, "--project-prefix", "AN"]
        shared = ["API_MIXER_beta_C82.shared_runtime", "--socket", root + "/shared.sock",
                  "--peer-owner-socket", root + "/owner.sock"]
        for args, name in ((direct, "direct"), (shared, "shared")):
            env = {**os.environ, "PYTHONPATH": str(ENGINE), "ANECHOIC_LOG_LEVEL": "ERROR"}
            if name == "direct":
                env["ANECHOIC_BETA_DIRECT_MANIFEST"] = json.dumps(
                    {"path": str(self.manifest), "gate": str(self.gate), "version": self.version})
            process = subprocess.Popen([sys.executable, "-B", "-P", "-m", *args], cwd=ENGINE, env=env,
                                       stdin=subprocess.PIPE, stderr=subprocess.PIPE)
            client = httpx2.Client(transport=httpx2.HTTPTransport(uds=root + "/" + name + ".sock"),
                                   base_url="http://private", timeout=5, trust_env=False)
            self.processes.append(process)
            self.clients.append(client)
            deadline = time.monotonic() + 10
            while not (self.path / (name + ".sock")).exists() and process.poll() is None and time.monotonic() < deadline:
                time.sleep(0.05)
            if not (self.path / (name + ".sock")).exists():
                self.fail("API process did not start")

    def tearDown(self):
        for client in self.clients:
            client.close()
        for process in self.processes:
            process.stdin.close()
            process.wait(timeout=10)
            process.stderr.close()
        for server in self.servers:
            server.shutdown()
            server.server_close()
        self.temp.cleanup()

    def call(self, index, name, arguments):
        data = {"name": name, "arguments": arguments, "session_id": None, "public_base_url": None}
        if index == 0:
            data.update(instance_id=INSTANCE, asserted_project_root=None)
        else:
            data["arguments"] = {"project_root": str(self.path), **arguments}
        return self.clients[index].post("/tools", json=data).json()

    def test_ready_kernel_waits_for_startup_replay(self):
        database, jobs = self.servers[:2]
        database.ready = True
        jobs.runs = {"active": None, "latest": None}
        sql = {"sql": "SELECT 42", "result_delivery": "inline"}
        health = self.clients[0].get("/health")
        self.assertEqual((200, "pending"), (health.status_code, health.json()["state"]))
        self.assertEqual("project_build_pending", self.call(0, "query_run", sql)["error"]["code"])
        database.unreachable = True
        health = self.clients[0].get("/health")
        self.assertEqual((503, "unavailable"), (health.status_code, health.json()["state"]))
        request = {"name": "query_run", "arguments": sql, "instance_id": INSTANCE,
                   "session_id": None, "public_base_url": None, "asserted_project_root": None}
        refused = self.clients[0].post("/tools", json=request)
        self.assertEqual((503, "project_build_unavailable"), (refused.status_code, refused.json()["error"]["code"]))
        database.unreachable = False
        jobs.runs["latest"] = {"state": "failed"}
        health = self.clients[0].get("/health")
        self.assertEqual((200, "degraded"), (health.status_code, health.json()["state"]))
        self.assertEqual("project_build_unavailable", self.call(0, "query_run", sql)["error"]["code"])
        self.assertFalse(any(method == "POST" for method, _, _ in database.requests))
        jobs.startup_replay_pending = False
        self.assertEqual("ready", self.clients[0].get("/health").json()["state"])
        self.assertEqual([[42]], self.call(0, "query_run", sql)["result"]["value"]["rows"])
        self.assertEqual(1, sum(method == "POST" for method, _, _ in database.requests))

    def test_manifest_gate_blocks_new_calls_but_drains_accepted_call(self):
        database, jobs = self.servers[:2]
        database.ready, jobs.startup_replay_pending = True, False
        database.entered, database.release = threading.Event(), threading.Event()
        sql = {"sql": "SELECT 42", "result_delivery": "inline"}
        with ThreadPoolExecutor(max_workers=1) as pool:
            accepted = pool.submit(self.call, 0, "query_run", sql)
            try:
                self.assertTrue(database.entered.wait(5), "accepted query did not reach Kernel")
                for content, state, status, code in (
                    (b"project_manifest_reloading", "pending", 200, "project_manifest_reloading"),
                    (b"project_manifest_invalid", "degraded", 200, "project_manifest_invalid"),
                    (b"\xff", "unavailable", 503, "admission_gate_unavailable"),
                ):
                    with self.subTest(code=code):
                        self.gate.write_bytes(content)
                        health = self.clients[0].get("/health")
                        self.assertEqual((status, state), (health.status_code, health.json()["state"]))
                        self.assertEqual(code, health.json()["error"]["code"])
                        request = {"name": "query_run", "arguments": sql, "instance_id": INSTANCE,
                                   "session_id": None, "public_base_url": None, "asserted_project_root": None}
                        refused = self.clients[0].post("/tools", json=request)
                        self.assertEqual((status, code), (refused.status_code, refused.json()["error"]["code"]))
                self.assertEqual(1, sum(method == "POST" for method, _, _ in database.requests))
            finally:
                database.release.set()
            self.assertEqual([[42]], accepted.result(timeout=5)["result"]["value"]["rows"])

    def test_direct_unready_status_abort_and_rebuild(self):
        refused = self.call(0, "query_run", {"sql": "SELECT 1"})
        self.assertEqual("project_build_pending", refused["error"]["code"])
        refused = self.call(0, "atom_lifecycle_archive", {"target": {"ref": "AN-S-1"}})
        self.assertEqual("project_build_pending", refused["error"]["code"])
        value = self.call(0, "workbench_status", {})["result"]["value"]
        self.assertEqual((True, "run-1", True), (value["syncing"], value["run_id"], value["worker_alive"]))
        self.assertEqual([{"code": "warning"}], value["ingestion_issues"])
        self.assertEqual("aborting", self.call(0, "workbench_abort", {"run_id": "run-1"})["result"]["value"]["state"])
        result = self.call(0, "query_rebuild", {"target": "main.mrt_atoms"})["result"]["value"]
        self.assertEqual({"status": "ready", "target": "main.mrt_atoms", "result_ids": {QUERY_ID: "d" * 32}}, result)
        self.assertEqual(("POST", "/jobs/build", {**self.worker_binding, "instance_id": INSTANCE, "refresh_target": "atoms"}),
                         self.servers[1].requests[-1])
        self.call(0, "query_rebuild", {"target": "query_" + QUERY_ID})
        self.assertEqual(("POST", "/results/rebuild", {"instance_id": INSTANCE, "target": QUERY_ID}),
                         self.servers[0].requests[-1])
        count = len(self.servers[1].requests) + len(self.servers[0].requests)
        self.assertEqual("tool_input_invalid", self.call(0, "query_rebuild", {"target": "unknown"})["error"]["code"])
        self.assertEqual(count, len(self.servers[1].requests) + len(self.servers[0].requests))

    def test_shared_cold_status_abort_do_not_start_project(self):
        status = self.call(1, "workbench_status", {})["result"]["value"]
        self.assertEqual({"mode": "unavailable", "syncing": False, "last_synced_at": None}, status)
        abort = self.call(1, "workbench_abort", {"run_id": "run-1"})
        self.assertEqual("run_not_abortable", abort["error"]["code"])
        leases = [item for item in self.servers[2].requests if item["operation"] == "lease"]
        self.assertEqual([False, False], [item["start"] for item in leases])
        self.assertEqual([b"R", b"R"], self.servers[2].releases)
        rebuilt = self.call(1, "query_rebuild", {"target": "all"})["result"]["value"]
        self.assertEqual("ready", rebuilt["status"])
        leases = [item for item in self.servers[2].requests if item["operation"] == "lease"]
        self.assertTrue(leases[-1]["start"])
        self.assertEqual("all", self.servers[1].requests[-1][2]["refresh_target"])

    def test_direct_worker_runs_binding(self):
        response = self.clients[0].get("/jobs/worker-runs", params={"instance_id": INSTANCE})
        self.assertEqual("run-1", response.json()["result"]["active"]["run_id"])
        count = len(self.servers[1].requests)
        for params in ({}, {"instance_id": "other"}, {"instance_id": INSTANCE, "extra": "x"}):
            result = self.clients[0].get("/jobs/worker-runs", params=params).json()
            self.assertEqual("value_error", result["error"]["code"])
        self.assertEqual(count, len(self.servers[1].requests))

    def test_shared_warm_status_and_abort_use_no_start_lease(self):
        self.servers[2].cold = False
        status = self.call(1, "workbench_status", {})["result"]["value"]
        self.assertEqual(("run-1", True), (status["run_id"], status["worker_alive"]))
        result = self.call(1, "workbench_abort", {"run_id": "run-1"})["result"]["value"]
        self.assertEqual({"run_id": "run-1", "state": "aborting"}, result)
        leases = [item for item in self.servers[2].requests if item["operation"] == "lease"]
        self.assertEqual([False, False], [item["start"] for item in leases])
        self.assertNotIn("/jobs/build", [item[1] for item in self.servers[1].requests])

    def test_archive_pending_keeps_live_health_and_queries_ready(self):
        database, jobs = self.servers[:2]
        database.ready, jobs.startup_replay_pending = True, False
        for pending in (True, False, None):
            with self.subTest(pending=pending):
                database.archive_pending = pending
                response = self.clients[0].get("/health")
                self.assertEqual(200, response.status_code)
                self.assertEqual("ready", response.json()["state"])
                self.assertIs(pending is True, response.json()["archive_pending"])
                query = self.call(0, "query_run", {"sql": "SELECT 42", "result_delivery": "inline"})
                self.assertEqual([[42]], query["result"]["value"]["rows"])
        self.assertNotIn("/jobs/build", [item[1] for item in jobs.requests])

    def test_archive_status_is_not_live_sync_for_direct_and_shared(self):
        archive = {"state": "running", "started_at": 100, "worker_alive": True}
        self.servers[1].runs = {"active": None, "latest": {"state": "succeeded", "finished_at": 50.0},
                                "archive": archive}
        self.servers[2].cold = False
        for index in (0, 1):
            with self.subTest(index=index):
                status = self.call(index, "workbench_status", {})["result"]["value"]
                self.assertFalse(status["syncing"])
                self.assertEqual(archive, status["archive"])
                self.assertEqual([{"code": "warning"}], status["ingestion_issues"])
        self.assertNotIn("/jobs/build", [item[1] for item in self.servers[1].requests])


if __name__ == "__main__":
    unittest.main()
