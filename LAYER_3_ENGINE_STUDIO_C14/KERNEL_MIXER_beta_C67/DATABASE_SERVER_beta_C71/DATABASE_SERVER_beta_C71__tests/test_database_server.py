"""Exercise the public server through its private Unix socket."""

import json
import http.client
import socket as unix_socket
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest



SCRIPT = Path(__file__).resolve().parents[1] / "DATABASE_SERVER_beta_C71__pub.py"


class DatabaseServerTest(unittest.TestCase):
    def test_real_server(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            socket = root / "database.sock"
            snapshot = root / "snapshot.json"
            digest = "a" * 64
            snapshot.write_text(json.dumps({"manifest_sha256": digest, "atoms": [
                {"reference": "AN-S-1", "summary": "actual summary"}]}))
            process = subprocess.Popen([sys.executable, str(SCRIPT), "--socket", str(socket),
                                        "--snapshot", str(snapshot), "--instance-id", "instance",
                                        "--manifest-sha256", digest], stderr=subprocess.PIPE)
            try:
                for _ in range(100):
                    if socket.exists() or process.poll() is not None:
                        break
                    time.sleep(0.05)
                self.assertTrue(socket.exists(), process.stderr.read().decode() if process.poll() is not None else "socket timeout")
                self.assertEqual(os.stat(socket).st_mode & 0o077, 0)
                class Client(http.client.HTTPConnection):
                    def connect(self):
                        self.sock = unix_socket.socket(unix_socket.AF_UNIX)
                        self.sock.connect(str(socket))

                def request(method, path, payload=None):
                    client = Client("localhost")
                    client.request(method, path, None if payload is None else json.dumps(payload),
                                   {"Content-Type": "application/json"})
                    response = client.getresponse()
                    result = response.status, json.loads(response.read())
                    client.close()
                    return result

                self.assertEqual(request("GET", "/health")[1], {"result": {
                    "instance_id": "instance", "pid": process.pid, "manifest_sha256": digest}})
                def run(sql, instance_id="instance", **extra):
                    return request("POST", "/database", {"instance_id": instance_id, "sql": sql, **extra})
                self.assertEqual(run("SELECT * FROM atoms")[1], {"result": {
                    "columns": ["reference", "summary"], "rows": [["AN-S-1", "actual summary"]]}})
                for sql in ("DELETE FROM atoms", "SELECT 1; SELECT 2", "SELECT * FROM read_csv('/etc/passwd')", "SELECT * FROM range(1001)"):
                    self.assertIn("error", run(sql)[1])
                self.assertEqual(run("SELECT 1", "other")[0], 403)
                self.assertEqual(run("SELECT 1", extra=True)[0], 400)
                self.assert_snapshot_admission(request, run, digest)
            finally:
                process.terminate()
                process.wait(timeout=10)
                process.stderr.close()

    def assert_snapshot_admission(self, request, run, digest):
        fresh = {"reference": "AN-S-2", "summary": "new snapshot"}
        for pin, atoms, instance, status in (
            ("b" * 64, [fresh], "instance", 400),
            (digest, [fresh, fresh], "instance", 400),
            (digest, [fresh], "other", 403),
            (digest, [fresh], "instance", 200),
        ):
            response, body = request("PUT", "/snapshot", {"instance_id": instance, "snapshot": {
                "manifest_sha256": pin, "atoms": atoms,
            }})
            self.assertEqual(response, status, body)
            rows = [["AN-S-2", "new snapshot"]] if status == 200 else [["AN-S-1", "actual summary"]]
            self.assertEqual(run("SELECT * FROM atoms")[1]["result"]["rows"], rows)


if __name__ == "__main__":
    unittest.main()
