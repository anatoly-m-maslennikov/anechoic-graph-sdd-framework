"""Exercise generation admission and read-only SQL through the real socket."""

from contextlib import contextmanager
from copy import deepcopy
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
from time import monotonic, sleep
import unittest

import httpx2

ENGINE = Path(__file__).resolve().parents[3]
MODULE = "KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.DATABASE_SERVER_beta_C71__pub"
PIN = "a" * 64
BINDING = {"instance_id": "instance"}


@contextmanager
def _server():
    with TemporaryDirectory(prefix="ane-db-test-", dir="/tmp") as directory:
        socket = Path(directory).resolve() / "db.sock"
        command = [sys.executable, "-B", "-P", "-m", MODULE, "--socket", str(socket),
                   "--instance-id", "instance", "--manifest-sha256", PIN]
        process = subprocess.Popen(command, env={**os.environ, "PYTHONPATH": str(ENGINE)})
        try:
            until = monotonic() + 10
            while not socket.exists() and process.poll() is None and monotonic() < until:
                sleep(0.03)
            if not socket.exists() or os.stat(socket).st_mode & 0o077:
                raise AssertionError("Database did not start with a private socket")
            with httpx2.Client(transport=httpx2.HTTPTransport(uds=str(socket)),
                               base_url="http://private", timeout=5, trust_env=False) as client:
                yield client
        finally:
            process.terminate()
            process.wait(timeout=10)


def _generation():
    model = json.dumps({"model_sha256": "b" * 64, "binding_schema": 1, "modules": {"__init__.py": "d" * 64},
                        "module_order": [], "class_modules": {}, "bindings": {}}, indent=2)
    structure = json.dumps({"model_sha256": "b" * 64, "project": {"ref": "AN-S-1", "sha256": PIN},
                            "components": {}}, indent=2)
    return {**BINDING, "snapshot": {"manifest_sha256": PIN, "atoms": [{"reference": "one", "summary": "first"}]},
            "model": model, "structure": structure, "receipt": {
                "manifest_sha256": PIN, "model_sha256": "b" * 64,
                "model_descriptor_sha256": sha256(model.encode()).hexdigest(),
                "structure_sha256": sha256(structure.encode()).hexdigest(),
            }}


def _query(client, sql, **fields):
    return client.post("/database", json={**BINDING, "sql": sql, **fields})


class DatabaseServerTest(unittest.TestCase):
    def test_atomic_generation_and_read_only_query(self):
        with _server() as client:
            self.assertFalse(client.get("/health").json()["result"]["ready"])
            self.assertEqual(_query(client, "SELECT * FROM atoms").status_code, 409)
            self.assertEqual(client.get("/model", params=BINDING).status_code, 409)
            payload = _generation()
            generation = self.admit(client, payload)
            self.assertTrue(client.get("/health").json()["result"]["ready"])
            self.assert_equal_artifacts(client, payload, generation)
            self.assert_rollbacks(client, payload, generation)
            self.assert_read_only_query(client)
            payload["snapshot"]["atoms"][0]["summary"] = "second"
            next_generation = self.admit(client, payload)
            self.assertNotEqual(next_generation, generation)
            self.assert_equal_artifacts(client, payload, next_generation)
            self.assertEqual([["one", "second"]], _query(client, "SELECT * FROM atoms").json()["result"]["rows"])

    def admit(self, client, payload):
        response = client.put("/generation", json=payload)
        self.assertEqual(200, response.status_code, response.text)
        return response.json()["result"]["generation"]

    def assert_equal_artifacts(self, client, payload, generation):
        for name in ("model", "structure"):
            response = client.get("/" + name, params=BINDING)
            self.assertEqual(payload[name].encode(), response.content)
            self.assertEqual(generation, response.headers["x-anechoic-generation"])

    def assert_rollbacks(self, client, payload, generation):
        duplicate = deepcopy(payload)
        duplicate["snapshot"]["atoms"] *= 2
        changed = deepcopy(payload)
        changed["receipt"]["structure_sha256"] = "c" * 64
        for invalid, status in ((duplicate, 400), (changed, 400), ({**payload, "instance_id": "other"}, 403)):
            self.assertEqual(status, client.put("/generation", json=invalid).status_code)
            self.assert_equal_artifacts(client, payload, generation)
            self.assertEqual([["one", "first"]], _query(client, "SELECT * FROM atoms").json()["result"]["rows"])

    def assert_read_only_query(self, client):
        for sql in ("DELETE FROM atoms", "SELECT 1; SELECT 2",
                    "SELECT * FROM read_csv('/etc/passwd')", "SELECT * FROM range(1001)"):
            self.assertEqual(400, _query(client, sql).status_code)
        self.assertEqual(403, _query(client, "SELECT 1", instance_id="other").status_code)
        self.assertEqual(400, _query(client, "SELECT 1", extra=True).status_code)


if __name__ == "__main__":
    unittest.main()
