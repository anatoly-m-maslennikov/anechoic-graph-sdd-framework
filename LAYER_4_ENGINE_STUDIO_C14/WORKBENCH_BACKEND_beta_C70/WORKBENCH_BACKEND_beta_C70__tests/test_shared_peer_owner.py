"""Exercise the private peer-owner CLI with real Project peer processes."""

import asyncio
from contextlib import asynccontextmanager, suppress
import json
import os
from pathlib import Path
import signal
import sys
from tempfile import TemporaryDirectory
import unittest

import httpx2

from .WORKBENCH_BACKEND_beta_C70__tests__shared import process_env, write_project

_ADMISSION = "FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_MODEL_VALIDATION.project_admission__pub"
_OWNER = "WORKBENCH_BACKEND_beta_C70.shared_peer_owner"
_BUSY = {"error": "ValueError", "message": "project_gateway_busy"}


def _line(request):
    return json.dumps(request).encode() + b"\n"


async def _response(reader):
    async with asyncio.timeout(35):
        return json.loads(await reader.readline())


async def _admit(roots):
    process = await asyncio.create_subprocess_exec(
        sys.executable, "-B", "-P", "-m", _ADMISSION, env=process_env(),
        stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE,
    )
    requests = [_line({"project_root": str(root), "control_root": None, "instance_id": None, "host_root": None})
                for root in roots]
    try:
        async with asyncio.timeout(30):
            output, _ = await process.communicate(b"".join(requests))
        replies = [json.loads(line) for line in output.splitlines()]
        if process.returncode or len(replies) != len(roots) or any("result" not in reply for reply in replies):
            raise AssertionError(f"Project admission failed: {replies}")
        return [reply["result"] for reply in replies]
    finally:
        if process.returncode is None:
            process.kill()
            await process.wait()


class PeerOwnerTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        directory = self.enterContext(TemporaryDirectory(prefix="ane-peer-owner-", dir="/tmp"))
        root = Path(directory).resolve()
        projects = root / "projects"
        projects.mkdir()
        roots = [projects / name for name in ("alpha", "beta")]
        for project in roots:
            project.mkdir()
            write_project(project)
        self.first, self.second = await _admit(roots)
        self.socket = root / "owner.sock"
        self.projects = projects

    async def _start_owner(self, maximum=1):
        settings = self.socket.with_name("host.toml")
        settings.write_text(f'schema_version=1\n[shared_mcp]\nprojects_root="{self.projects}"\n'
                            f'http_port=8092\nmax_loaded_projects={maximum}\n')
        self.process = await asyncio.create_subprocess_exec(
            sys.executable, "-B", "-P", "-m", _OWNER, "--socket", str(self.socket),
            "--host-settings", str(settings), env=process_env(), stdin=asyncio.subprocess.PIPE,
        )
        self.addAsyncCleanup(self._stop_owner)
        async with asyncio.timeout(20):
            while self.process.returncode is None:
                try:
                    await self._status()
                    break
                except (FileNotFoundError, ConnectionRefusedError):
                    await asyncio.sleep(0.02)
            else:
                self.fail(f"Peer owner exited during startup with {self.process.returncode}")

    async def _stop_owner(self):
        self.process.stdin.close()
        try:
            async with asyncio.timeout(30):
                await self.process.wait()
        except TimeoutError:
            self.process.kill()
            await self.process.wait()
        self.assertEqual(0, self.process.returncode)
        self.assertFalse(self.socket.exists())

    @asynccontextmanager
    async def _connection(self, request):
        reader, writer = await asyncio.open_unix_connection(self.socket)
        try:
            writer.write(_line(request))
            await writer.drain()
            yield reader, writer
        finally:
            writer.close()
            with suppress(OSError):
                await writer.wait_closed()

    def _lease(self, binding, *, start=True):
        return self._connection({"operation": "lease", "binding": binding, "start": start})

    async def _status(self):
        async with self._connection({"operation": "status"}) as (reader, _):
            return (await _response(reader))["result"]

    async def _assert_busy(self, binding):
        async with self._lease(binding) as (reader, _):
            self.assertEqual(_BUSY, await _response(reader))

    async def _acquire(self, binding):
        async with asyncio.timeout(35):
            while True:
                async with self._lease(binding) as (reader, writer):
                    reply = await _response(reader)
                    if reply != _BUSY:
                        self.assertIn("result", reply, reply)
                        writer.write(b"R")
                        await writer.drain()
                        self.assertEqual({"result": None}, await _response(reader))
                        return reply["result"]
                await asyncio.sleep(0.01)

    async def test_disconnect_releases_held_project(self):
        await self._start_owner()
        async with self._lease(self.first) as (reader, _):
            held = await _response(reader)
            self.assertIn("result", held, held)
            self.assertTrue(Path(held["result"]["database_socket"]).is_socket())
            await self._assert_busy(self.second)
        peers = await self._acquire(self.second)
        self.assertTrue(Path(peers["orchestrator_socket"]).is_socket())
        self.assertFalse(Path(held["result"]["database_socket"]).exists())
        report = await self._status()
        self.assertEqual(1, report["loaded_project_count"])
        self.assertEqual(self.second["instance_id"], report["loaded_project_processes"][0]["instance_id"])
        async with self._lease(self.first, start=False) as (reader, _):
            self.assertEqual({"result": None}, await _response(reader))
        self.assertTrue(Path((await self._acquire(self.first))["database_socket"]).is_socket())

    async def test_disconnect_during_start_returns_slot(self):
        await self._start_owner()
        storage = Path(self.first["root"]) / ".anechoic_runtime" / "workbench" / "beta"
        async with self._lease(self.first) as (reader, _):
            reply = asyncio.create_task(_response(reader))
            try:
                async with asyncio.timeout(5):
                    while not storage.is_dir():
                        self.assertFalse(reply.done())
                        await asyncio.sleep(0.01)
                await self._assert_busy(self.second)
                self.assertFalse(reply.done(), "The cold lease already completed")
            finally:
                reply.cancel()
                with suppress(asyncio.CancelledError):
                    await reply
        peers = await self._acquire(self.second)
        self.assertEqual(self.second["root"], peers["worker_binding"]["root"])

    async def test_owner_rejects_binding_with_a_foreign_manifest(self):
        await self._start_owner()
        wrong = self.first | {"manifest_path": self.second["manifest_path"]}
        async with self._lease(wrong) as (reader, _):
            self.assertEqual({"error": "ValueError", "message": "project_declarations_stale"},
                             await _response(reader))
        self.assertEqual(0, (await self._status())["loaded_project_count"])

    async def _peer_pids(self):
        status = await self._status()
        return {entry["instance_id"]: (entry["kernel_pid"], entry["orchestrator_pid"])
                for entry in status["loaded_project_processes"]}

    async def _wait_for_exit(self, pid):
        async with asyncio.timeout(15):
            while True:
                try:
                    os.kill(pid, 0)
                except ProcessLookupError:
                    return
                await asyncio.sleep(0.05)

    async def _wait_for_pair(self, instance, old_pids):
        async with asyncio.timeout(45):
            while True:
                current = await self._peer_pids()
                pair = current.get(instance)
                if pair and not (set(pair) & set(old_pids)):
                    return current
                await asyncio.sleep(0.05)

    async def test_recovers_idle_project_after_either_peer_dies(self):
        await self._start_owner(maximum=2)
        await self._acquire(self.first)
        await self._acquire(self.second)
        first, second = self.first["instance_id"], self.second["instance_id"]
        current = await self._peer_pids()
        other = current[second]
        for index in (0, 1):
            with self.subTest(killed=("kernel", "orchestrator")[index]):
                old = current[first]
                os.kill(old[index], signal.SIGKILL)
                # Observe teardown before sending any more owner requests.
                await self._wait_for_exit(old[1 - index])
                current = await self._wait_for_pair(first, old)
                self.assertEqual({first, second}, set(current))
                self.assertEqual(other, current[second])
        async with self._lease(self.first, start=False) as (reader, _):
            result = (await _response(reader))["result"]
            transport = httpx2.AsyncHTTPTransport(uds=result["database_socket"])
            async with httpx2.AsyncClient(transport=transport, base_url="http://private", trust_env=False) as kernel:
                health = (await kernel.get("/health")).json()["result"]
            self.assertIs(True, health["ready"])
            self.assertEqual(self.first["manifest_sha256"], health["manifest_sha256"])
            self.assertIsNotNone(health["generation"])
