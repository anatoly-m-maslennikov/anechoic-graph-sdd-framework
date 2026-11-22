import http.client
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import socket
import subprocess
import tempfile
import threading
import unittest
from unittest.mock import patch

MODULE = Path(__file__).resolve().parents[1] / "ORCHESTRATOR_beta_C68__pub.py"
spec = importlib.util.spec_from_file_location("orchestrator", MODULE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class UnixConnection(http.client.HTTPConnection):
    def __init__(self, path):
        super().__init__("localhost")
        self.path = path

    def connect(self):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.connect(self.path)


class OrchestratorTests(unittest.TestCase):
    def test_http_and_real_worker_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "server.sock")
            server = module.Server(path, "test")
            thread = threading.Thread(target=server.serve_forever)
            thread.start()
            self.addCleanup(thread.join)
            self.addCleanup(server.server_close)
            self.addCleanup(server.shutdown)
            def call(method, target, body=None):
                connection = UnixConnection(path)
                connection.request(method, target, body=body)
                response = connection.getresponse()
                result = response.status, json.loads(response.read())
                connection.close()
                return result
            status, health = call("GET", "/health")
            self.assertEqual(200, status)
            self.assertEqual("test", health["result"]["instance_id"])
            self.assertEqual(409, call("GET", "/jobs/worker-runs?instance_id=other")[0])
            self.assertEqual(400, call("POST", "/jobs/build", "{}")[0])
            binding = {key: "bad" for key in module.FIELDS}
            binding["instance_id"] = "test"
            status, result = call("POST", "/jobs/build", json.dumps(binding))
            self.assertEqual(502, status)
            self.assertEqual("worker_failed", result["error"]["code"])
            status, result = call("GET", "/jobs/worker-runs?instance_id=test")
            self.assertEqual(200, status)
            self.assertIsNone(result["result"]["active"])
            self.assertEqual("failed", result["result"]["latest"]["state"])

    def test_real_worker_success(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            control = root / ".anechoic_test"
            control.mkdir()
            manifest = control / "AN-S-001-manifest.md"
            manifest.write_text("---\nidentity:\n  atom_id: AN-S-001\ncontext:\n  container:\n    component: C0\nstate:\n  status: active\n  version: 1\n---\n\n## Summary\n\nManifest\n")
            binding = {"instance_id": "test", "root": str(root), "control_root": control.name,
                       "manifest_path": manifest.name, "manifest_sha256": sha256(manifest.read_bytes()).hexdigest(),
                       "project_prefix": "AN"}
            jobs = module.Jobs("test")
            status, result = jobs.build(binding)
            self.assertEqual(200, status, result)
            self.assertEqual([{"reference": "AN-S-001", "summary": "Manifest"}], result["result"]["atoms"])
            self.assertEqual("succeeded", jobs.status()["latest"]["state"])

    def test_single_active_build_and_timeout(self):
        jobs = module.Jobs("test")
        request = {key: "x" for key in module.FIELDS}
        request["instance_id"] = "test"
        started, release = threading.Event(), threading.Event()
        def worker(*args, **kwargs):
            started.set()
            release.wait(5)
            return subprocess.CompletedProcess([], 0, '{"atoms": []}', '')
        result = []
        with patch.object(module.subprocess, "run", side_effect=worker):
            thread = threading.Thread(target=lambda: result.append(jobs.build(request)))
            thread.start()
            self.assertTrue(started.wait(5))
            self.assertEqual("running", jobs.status()["active"]["state"])
            self.assertEqual(409, jobs.build(request)[0])
            release.set()
            thread.join(5)
        self.assertEqual((200, {"result": {"atoms": []}}), result[0])
        with patch.object(module.subprocess, "run", side_effect=subprocess.TimeoutExpired("worker", 1)):
            self.assertEqual(504, jobs.build(request)[0])
        self.assertEqual("worker_timeout", jobs.status()["latest"]["code"])


if __name__ == "__main__":
    unittest.main()
