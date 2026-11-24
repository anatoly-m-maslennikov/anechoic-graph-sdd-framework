"""Check the packaged single-Project roles through their real CLI and sockets."""

import asyncio
from hashlib import sha256
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
from tempfile import TemporaryDirectory
from time import monotonic, sleep
import unittest
from unittest.mock import patch

import httpx2

from .. import WORKBENCH_BACKEND_beta_C70__shared as backend
from .WORKBENCH_BACKEND_beta_C70__tests__shared import process_env, write_project


def _client(path):
    return httpx2.Client(transport=httpx2.HTTPTransport(uds=str(path)), base_url="http://private",
                         timeout=5, trust_env=False)


def _wait(process, predicate, timeout):
    deadline = monotonic() + timeout
    while process.poll() is None and monotonic() < deadline:
        if predicate():
            return
        sleep(0.02)
    raise AssertionError(f"Beta role did not reach readiness (exit {process.poll()})")


def _stop(process):
    process.stdin.close()
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)


class DirectManifestAdmissionTests(unittest.IsolatedAsyncioTestCase):
    async def test_stale_readiness_and_writes_are_blocked_while_accepted_call_finishes(self):
        root = Path(self.enterContext(TemporaryDirectory())).resolve()
        manifest, gate = root / "manifest.md", root / "api.draining"
        manifest.write_text("original")
        info = manifest.lstat()
        version = (info.st_dev, info.st_ino, info.st_mode, info.st_size, info.st_mtime_ns, info.st_ctime_ns)
        binding = json.dumps({"path": str(manifest), "version": version, "gate": str(gate)})
        with patch.dict(os.environ, {"ANECHOIC_BETA_DIRECT_MANIFEST": binding}):
            app = backend.create_app("instance", "digest", str(root), "db", "jobs")
        client = await self.enterAsyncContext(httpx2.AsyncClient(transport=httpx2.ASGITransport(app=app),
                                                                 base_url="http://private"))
        admitted, finish = asyncio.Event(), asyncio.Event()

        async def execute(*args, **kwargs):
            admitted.set()
            await finish.wait()
            return {"result": {"value": {"outcome": "completed"}, "text": None}}

        envelope = {"name": "atom_lifecycle_create_draft", "arguments": {}, "instance_id": "instance",
                    "session_id": None, "public_base_url": None, "asserted_project_root": None}
        with patch.object(backend, "execute_tool", side_effect=execute) as tool:
            accepted = asyncio.create_task(client.post("/tools", json=envelope))
            try:
                await asyncio.wait_for(admitted.wait(), 5)
                manifest.write_text("changed")
                self.assertEqual(503, (await client.get("/health")).status_code)
                blocked = await client.post("/tools", json=envelope)
                self.assertEqual("project_manifest_reloading", blocked.json()["error"]["code"])
                gate.write_text("project_manifest_invalid")
                unready = await client.get("/health")
                self.assertEqual((503, False), (unready.status_code, unready.json()["ready"]))
                blocked = await client.post("/tools", json=envelope)
                self.assertEqual("project_manifest_invalid", blocked.json()["error"]["code"])
            finally:
                finish.set()
                completed = await asyncio.wait_for(accepted, 5)
            self.assertEqual("completed", completed.json()["result"]["value"]["outcome"])
            self.assertEqual(1, tool.await_count)


class RuntimeRoleTests(unittest.TestCase):
    def setUp(self):
        directory = self.enterContext(TemporaryDirectory(prefix="ane-beta-roles-", dir="/tmp"))
        parent = Path(directory).resolve()
        self.root = parent / "project"
        self.root.mkdir()
        manifest = write_project(self.root)
        self.socket = parent / "api.sock"
        self.ready = parent / "peers.ready"
        self.database = parent / "db.sock"
        self.orchestrator = parent / "jobs.sock"
        self.digest = sha256(manifest.read_bytes()).hexdigest()
        self.command = [
            sys.executable, "-B", "-P", "-m", "WORKBENCH_BACKEND_beta_C70.runtime",
            "--socket", str(self.socket), "--instance-id", "instance", "--project-root", str(self.root),
            "--control-root", manifest.parent.name, "--manifest-path", manifest.relative_to(self.root).as_posix(),
            "--manifest-sha256", self.digest, "--project-prefix", "AN", "--project-name", "Anechoic",
            "--host-root", "/host/project", "--blacklist", "query_schema", "--workbench-storage", "memory",
        ]

    def _start(self, role):
        process = subprocess.Popen(self.command + ["--role", role], env=process_env(), stdin=subprocess.PIPE)
        self.addCleanup(_stop, process)
        return process

    def _refusal(self, message, *arguments):
        result = subprocess.run(self.command + ["--role", "api", *arguments], env=process_env(),
                                input="", capture_output=True, text=True, timeout=10)
        self.assertNotEqual(0, result.returncode)
        self.assertIn(message, result.stderr)
        self.assertFalse(self.socket.exists())

    def _api(self):
        process = self._start("api")
        _wait(process, self.socket.is_socket, 10)
        client = self.enterContext(_client(self.socket))
        deadline = monotonic() + 5
        while True:
            try:
                health = client.get("/health").json()
                break
            except httpx2.TransportError:
                if monotonic() >= deadline:
                    raise
                sleep(0.02)
        self.assertEqual((True, process.pid, "instance", self.digest),
                         tuple(health[key] for key in ("ready", "pid", "instance_id", "manifest_sha256")))
        with _client(self.orchestrator) as jobs:
            orchestrator_pid = jobs.get("/health").json()["result"]["pid"]
        return process, client, (health["kernel_pid"], orchestrator_pid)

    def _call(self, client, name, arguments):
        response = client.post("/tools", json={"name": name, "arguments": arguments, "instance_id": "instance",
                                               "session_id": "role-test", "public_base_url": None,
                                               "asserted_project_root": "/host/project"})
        reply = response.json()
        self.assertIn("result", reply, reply)
        return reply["result"]["value"]

    def test_api_restarts_against_ready_peers(self):
        self._refusal("Beta peer owner is not ready")
        owner = self._start("peer-owner")
        _wait(owner, self.ready.is_file, 90)
        self.assertEqual(b"", self.ready.read_bytes())
        self.assertFalse(self.ready.stat().st_mode & 0o077)
        self._refusal("Kernel did not admit the selected Beta Project", "--manifest-sha256", "0" * 64)
        first, api, peers = self._api()
        catalog = api.get("/tools", params={"instance_id": "instance"}).json()["result"]
        self.assertEqual(["query_schema"], catalog["blacklist"])
        query = self._call(api, "query_run", {"sql": "SELECT 42", "result_delivery": "inline"})
        first.kill()
        first.wait(timeout=5)
        self.socket.unlink()
        second, api, same_peers = self._api()
        self.assertNotEqual(first.pid, second.pid)
        self.assertEqual(peers, same_peers)
        page = self._call(api, "query_page", {"query_id": query["query_id"], "result_delivery": "inline"})
        self.assertEqual([[42]], page["rows"])
        second.stdin.close()
        self.assertEqual(0, second.wait(timeout=10))
        self.assertFalse(self.socket.exists())
        self.assertIsNone(owner.poll())
        os.kill(peers[1], signal.SIGKILL)
        self.assertNotEqual(0, owner.wait(timeout=10))
        self.assertFalse(self.ready.exists())
        for peer in peers:
            with self.assertRaises(ProcessLookupError):
                os.kill(peer, 0)

    def test_eof_cancels_initial_admission(self):
        owner = self._start("peer-owner")
        _wait(owner, self.database.is_socket, 25)
        self.assertFalse(self.ready.exists())
        _stop(owner)
        self.assertEqual(0, owner.returncode)
        self.assertFalse(self.ready.exists())
        self.assertFalse(self.database.exists())
