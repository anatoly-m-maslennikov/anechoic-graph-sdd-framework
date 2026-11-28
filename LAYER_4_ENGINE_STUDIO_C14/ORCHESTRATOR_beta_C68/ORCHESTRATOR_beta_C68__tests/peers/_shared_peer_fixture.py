"""Fixtures for the shared peer-owner process tests."""

import asyncio
from contextlib import asynccontextmanager, suppress
import json
import os
from pathlib import Path
import sys
from tempfile import TemporaryDirectory


ENGINE = Path(__file__).resolve().parents[3]
ROOT = ENGINE.parent


def process_env():
    return {
        **os.environ,
        "PYTHONPATH": str(ENGINE),
        "ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY": os.environ.get(
            "ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY",
            str(ROOT / ".anechoic_tmp/workbench/extensions"),
        ),
    }


def write_project(root):
    control = root / "_anechoic_anechoic"
    control.mkdir()
    (control / "AN-S-001-PROJECT_MANIFEST--declare-anechoic.md").write_text(
        "---\natom_family: SPEC\natom_id: AN-S-001\n"
        "container:\n  component: C00\ntier: -1\n"
        "context:\n  template: project_manifest\n  lens: SPEC\n"
        "state:\n  status: active\n  version: 3\n"
        "  updated_at: '2026-11-19T00:00:00Z'\n---\n\n"
        "## Summary\n\nDeclare Anechoic\n\n"
        "## Claim\n\n### Formal Claim\n\n```python\n"
        "from anechoic.formal_claims import declare_entity\n"
        "from anechoic.model import ProjectManifest\n"
        "declare_entity(entity_name='Project Manifest', "
        "instance=ProjectManifest(name='Anechoic', prefix='AN'))\n```\n",
        encoding="utf-8",
    )


_ADMISSION = (
    "FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51."
    "FEATURE_MODEL_VALIDATION.project_admission__pub"
)
_OWNER = "ORCHESTRATOR_beta_C68.shared_peer_owner"
_BUSY = {"error": "ValueError", "message": "project_gateway_busy"}


def _line(request):
    return json.dumps(request).encode() + b"\n"


async def _response(reader):
    async with asyncio.timeout(35):
        return json.loads(await reader.readline())


async def _admit(roots):
    process = await asyncio.create_subprocess_exec(
        sys.executable,
        "-B",
        "-P",
        "-m",
        _ADMISSION,
        env=process_env(),
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
    )
    requests = [
        _line(
            {
                "project_root": str(root),
                "control_root": None,
                "instance_id": None,
                "host_root": None,
            }
        )
        for root in roots
    ]
    try:
        async with asyncio.timeout(30):
            output, _ = await process.communicate(b"".join(requests))
        replies = [json.loads(line) for line in output.splitlines()]
        if (
            process.returncode
            or len(replies) != len(roots)
            or any("result" not in reply for reply in replies)
        ):
            raise AssertionError(f"Project admission failed: {replies}")
        return [reply["result"] for reply in replies]
    finally:
        if process.returncode is None:
            process.kill()
            await process.wait()


class PeerOwnerFixture:
    async def asyncSetUp(self):
        directory = self.enterContext(
            TemporaryDirectory(prefix="ane-peer-owner-", dir="/tmp")
        )
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

    async def _start_owner(
        self, maximum=1, *, project_root=None, settings=None
    ):
        if settings is None:
            settings = self.socket.with_name("host.toml")
            root_field = (
                f'project_root="{project_root}"'
                if project_root
                else f'projects_root="{self.projects}"'
            )
            settings.write_text(
                f"schema_version=1\n[shared_mcp]\n{root_field}\n"
                f"http_port=8092\nmax_loaded_projects={maximum}\n"
            )
        self.process = await asyncio.create_subprocess_exec(
            sys.executable,
            "-B",
            "-P",
            "-m",
            _OWNER,
            "--socket",
            str(self.socket),
            "--host-settings",
            str(settings),
            env=process_env(),
            stdin=asyncio.subprocess.PIPE,
        )
        self.addAsyncCleanup(self._stop_owner)
        async with asyncio.timeout(20):
            while self.process.returncode is None:
                try:
                    await self._status()
                    break
                except FileNotFoundError, ConnectionRefusedError:
                    await asyncio.sleep(0.02)
            else:
                self.fail(
                    "Peer owner exited during startup with "
                    f"{self.process.returncode}"
                )

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
        return self._connection(
            {"operation": "lease", "binding": binding, "start": start}
        )

    async def _status(self):
        async with self._connection({"operation": "status"}) as (reader, _):
            return (await _response(reader))["result"]

    async def _select(self, **arguments):
        async with self._connection({"operation": "select", **arguments}) as (
            reader,
            _,
        ):
            return await _response(reader)

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
                        self.assertEqual(
                            {"result": None}, await _response(reader)
                        )
                        return reply["result"]
                await asyncio.sleep(0.01)

    async def _peer_pids(self):
        status = await self._status()
        return {
            entry["instance_id"]: (
                entry["kernel_pid"],
                entry["orchestrator_pid"],
            )
            for entry in status["loaded_project_processes"]
        }

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
