"""Exercise managed builds through the CLI and private Unix socket."""
import http.client
import json
import socket
import tempfile
import threading
import time
import unittest
from hashlib import sha256
from pathlib import Path

from .ORCHESTRATOR_beta_C68__tests__shared import watch_project


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
