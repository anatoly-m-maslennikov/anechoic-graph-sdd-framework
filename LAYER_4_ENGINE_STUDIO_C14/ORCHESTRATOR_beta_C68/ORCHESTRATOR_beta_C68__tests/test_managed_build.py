"""Exercise managed builds through the CLI and private Unix socket."""
import http.client
import json
import os
import subprocess
import sys
import socket
import tempfile
import threading
import time
import unittest
from hashlib import sha256
from pathlib import Path

from .ORCHESTRATOR_beta_C68__tests__shared import ENGINE, project, request_json, wait_for, watch_project


class Connection(http.client.HTTPConnection):
    def __init__(self, path):
        super().__init__("localhost", timeout=120)
        self.path = str(path)

    def connect(self):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.settimeout(self.timeout)
        self.sock.connect(self.path)


def request(path, binding):
    connection = Connection(path)
    try:
        connection.request("POST", "/jobs/build", json.dumps(binding))
        response = connection.getresponse()
        return response.status, json.loads(response.read())
    finally:
        connection.close()


class ManagedBuildTests(unittest.TestCase):
    def test_model_targets_rebuild_same_generation_with_real_kernel(self):
        with tempfile.TemporaryDirectory(prefix="ane-model-build-", dir="/tmp") as directory:
            root = Path(directory).resolve()
            control, manifest = project(root)
            (control / "__TKT").mkdir()
            binding = {"root": str(root), "control_root": control.name, "manifest_path": manifest.name,
                       "manifest_sha256": sha256(manifest.read_bytes()).hexdigest(), "project_prefix": "AN"}
            (root / "binding.json").write_text(json.dumps(binding))
            env = {**os.environ, "PYTHONPATH": str(ENGINE)}
            env.setdefault("ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY", str(ENGINE.parent / ".anechoic_tmp/workbench/extensions"))
            db, jobs, worker = (str(root / name) for name in ("db.sock", "jobs.sock", "worker.sock"))
            processes = []
            def start(module, *args):
                process = subprocess.Popen([sys.executable, "-B", "-P", "-m", module, *args], cwd=ENGINE, env=env)
                processes.append(process)
                return process
            try:
                database = start("KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.DATABASE_SERVER_beta_C71__shared",
                                 "--socket", db, "--instance-id", "test", "--manifest-sha256", binding["manifest_sha256"])
                wait_for(Path(db).exists, database, timeout=10)
                runner = start("WORKERS_beta_C69.warm_worker", "--socket", worker)
                wait_for(Path(worker).exists, runner, timeout=10)
                orchestrator = start("ORCHESTRATOR_beta_C68.ORCHESTRATOR_beta_C68__shared", "--socket", jobs,
                    "--instance-id", "test", "--binding-file", str(root / "binding.json"),
                    "--database-socket", db, "--worker-socket", worker, "--worker-load-seconds", "1")
                wait_for(Path(jobs).exists, orchestrator, timeout=10)
                def ready():
                    status, body = request_json(db, "GET", "/health")
                    return status == 200 and body["result"]["ready"] and not body["result"]["archive_pending"]
                wait_for(ready, orchestrator, timeout=90)
                self._assert_full_and_graph_rebuild(control, db, jobs, binding)
                self._assert_model_targets(db, jobs, binding)
            finally:
                for process in reversed(processes):
                    process.terminate()
                    process.wait(timeout=10)

    def _assert_full_and_graph_rebuild(self, control, db, jobs, binding):
        source = control / "__TKT" / "AN-T-1-TASK--check-rebuild.md"
        source.write_text("---\nidentity:\n  atom_id: AN-T-1\ncontext:\n  container:\n    component: C00\n"
                          "state:\n  status: active\n  version: 1\n---\n\n## Summary\n\nFresh source\n")
        status, body = request(jobs, binding | {"instance_id": "test", "refresh_target": "all"})
        self.assertEqual(200, status, body)
        def query(sql):
            status, body = request_json(db, "POST", "/database", {"instance_id": "test",
                "sql": sql, "page_size": 10})
            self.assertEqual(200, status, body)
            return body["result"]["rows"]
        atoms = query('SELECT reference, "content.summary" FROM atoms ORDER BY reference')
        self.assertIn(["AN-T-1", "Fresh source"], atoms)
        model = request_json(db, "GET", "/model?instance_id=test")
        structure = request_json(db, "GET", "/structure?instance_id=test")
        for _ in range(2):
            status, body = request(jobs, binding | {"instance_id": "test", "refresh_target": "realization_graph"})
            self.assertEqual(200, status, body)
            self.assertEqual({}, body["result"]["result_ids"])
            self.assertEqual(atoms, query('SELECT reference, "content.summary" FROM atoms ORDER BY reference'))
            self.assertEqual(model, request_json(db, "GET", "/model?instance_id=test"))
            self.assertEqual(structure, request_json(db, "GET", "/structure?instance_id=test"))

    def _assert_model_targets(self, db, jobs, binding):
        for target in ("model_tree", "model_primary_entities"):
            with self.subTest(target=target):
                queries = []
                for table in ("mrt_model_tree", "model_primary_entities"):
                    status, body = request_json(db, "POST", "/database", {"instance_id": "test",
                        "sql": f"SELECT * FROM {table}", "page_size": 2})
                    self.assertEqual(200, status, body)
                    queries.append(body["result"]["query_id"])
                before = request_json(db, "GET", "/health")[1]["result"]["generation"]
                status, body = request(jobs, binding | {"instance_id": "test", "refresh_target": target})
                self.assertEqual(200, status, body)
                self.assertEqual(before, body["result"]["generation"])
                self.assertTrue(set(queries) <= set(body["result"]["result_ids"]))

    def test_socket_waits_for_fresh_admission_and_reports_failure(self):
        with tempfile.TemporaryDirectory(prefix="ane-managed-", dir="/tmp") as directory:
            root = Path(directory).resolve()
            with watch_project(root) as (control, manifest, path, kernel, _):
                selected = {"instance_id": "test", "root": str(root), "control_root": control.name,
                            "manifest_path": manifest.name, "manifest_sha256": sha256(manifest.read_bytes()).hexdigest(),
                            "project_prefix": "AN"}
                self.assertEqual(409, request(path, {**selected, "instance_id": "wrong"})[0])
                self.assertEqual(409, request(path, {**selected, "project_prefix": "OTHER"})[0])
                kernel.admit_started, kernel.admit_release = threading.Event(), threading.Event()
                results = []
                selected["refresh_target"] = "all"
                client = threading.Thread(target=lambda: results.append(request(path, selected)))
                client2 = None
                client.start()
                try:
                    self.assertTrue(kernel.admit_started.wait(90))
                    self.assertTrue(client.is_alive())
                    self.assertEqual("all", kernel.payloads[-1]["refresh_target"])
                    self.assertEqual(409, request(path, {**selected, "refresh_target": "atoms"})[0])
                    client2 = threading.Thread(target=lambda: results.append(request(path, selected)))
                    client2.start()
                    time.sleep(0.2)
                    self.assertTrue(client2.is_alive())
                finally:
                    kernel.admit_release.set()
                    client.join(90)
                    if client2 is not None:
                        client2.join(90)
                self.assertFalse(client.is_alive())
                expected = (200, {"result": {"generation": "2", "result_ids": {"old": "new"}}})
                self.assertEqual([expected, expected], results)
                self.assertEqual(2, len(kernel.generations))
                self.assertEqual(["/generation", "/generation"], kernel.paths)
                kernel.admit_started = None
                kernel.reject = True
                status, body = request(path, selected)
                self.assertEqual(502, status)
                self.assertEqual("generation_failed", body["error"]["code"])
                self.assertIn("Kernel rejected generation", body["error"]["message"])
