"""Exercise Backend, Kernel, and Orchestrator through their private processes."""

from hashlib import sha256
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
from time import monotonic, sleep
import unittest

import httpx2

from .test_project_admission import ENGINE, write_project


def _client(path):
    return httpx2.Client(transport=httpx2.HTTPTransport(uds=str(path)),
                         base_url="http://private", timeout=10, trust_env=False)


def _ready(client, process):
    until = monotonic() + 90
    while process.poll() is None and monotonic() < until:
        try:
            response = client.get("/health")
        except httpx2.TransportError:
            sleep(0.05)
            continue
        response.raise_for_status()
        return response.json()
    raise AssertionError("Backend did not start")


class ApiTests(unittest.TestCase):
    def test_query_and_worker_state_are_served_by_separate_processes(self):
        with TemporaryDirectory(prefix="ane-beta-", dir="/tmp") as folder:
            root = Path(folder).resolve()
            manifest = write_project(root)
            socket = root / "api.sock"
            digest = sha256(manifest.read_bytes()).hexdigest()
            process = subprocess.Popen(
                [sys.executable, "-B", "-P", "-m", "WORKBENCH_BACKEND_beta_C70.runtime__pub",
                 "--socket", str(socket), "--instance-id", "instance", "--project-root", str(root),
                 "--control-root", manifest.parent.name, "--manifest-path", manifest.name,
                 "--manifest-sha256", digest, "--project-prefix", "AN"],
                env={**os.environ, "PYTHONPATH": str(ENGINE)}, stdin=subprocess.PIPE,
            )
            try:
                with _client(socket) as api, _client(root / "jobs.sock") as jobs:
                    backend = _ready(api, process)
                    orchestrator = jobs.get("/health").json()["result"]
                    self.assertEqual(process.pid, backend["pid"])
                    self.assertEqual(3, len({backend["pid"], backend["kernel_pid"], orchestrator["pid"]}))
                    self.assertEqual(digest, backend["manifest_sha256"])
                    self.assert_query_and_jobs(api)
            finally:
                process.stdin.close()
                try:
                    process.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    process.terminate()
                    process.wait(timeout=10)
            self.assertEqual(0, process.returncode)
            for pid in (backend["kernel_pid"], orchestrator["pid"]):
                with self.assertRaises(ProcessLookupError):
                    os.kill(pid, 0)

    def assert_query_and_jobs(self, api):
        params = {"instance_id": "instance"}
        envelope = {"name": "query_run", "arguments": {"sql": "SELECT reference FROM atoms"},
                    "instance_id": "instance", "session_id": None, "public_base_url": None,
                    "asserted_project_root": None}
        tools = api.get("/tools", params=params).json()["result"]["tools"]
        self.assertEqual(["query_run"], [tool["name"] for tool in tools])
        query = api.post("/tools", json=envelope).json()
        self.assertEqual({"columns": ["reference"], "rows": [["AN-S-001"]]}, query["result"]["value"])
        runs = api.get("/jobs/worker-runs", params=params).json()["result"]
        self.assertIsNone(runs["active"])
        self.assertEqual("succeeded", runs["latest"]["state"])
        wrong_binding = api.get("/tools", params={"instance_id": "other"}).json()
        self.assertEqual("value_error", wrong_binding["error"]["code"])
        unsupported = api.post("/tools", json=envelope | {"arguments": {"sql": "SELECT 1", "save": True}}).json()
        self.assertEqual("tool_input_invalid", unsupported["error"]["code"])
