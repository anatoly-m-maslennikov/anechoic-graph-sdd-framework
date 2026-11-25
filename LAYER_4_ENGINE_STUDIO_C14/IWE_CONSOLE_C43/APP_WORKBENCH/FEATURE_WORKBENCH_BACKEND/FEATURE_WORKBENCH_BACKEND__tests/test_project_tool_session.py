"""The shared HTTP coordinator keeps its Project lease during a child write."""

import asyncio
import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import httpx2
from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.FEATURE_WORKBENCH_BACKEND__shared import (
    create_shared_app,
    load_host_runtime_config,
)


_NAME = "atom_lifecycle_update"


def _project(parent, name):
    root = parent / name
    control = root / f".anechoic_{name}"
    control.mkdir(parents=True)
    prefix = name.upper()
    (control / f"{prefix}-S-001-PROJECT_MANIFEST--declare.md").write_text(
        "---\n"
        f"identity: {{atom_id: {prefix}-S-001}}\n"
        "context: {container: {component: C00}, tier: -1, template: project_manifest}\n"
        "state: {status: active, version: 1}\n"
        "---\n\n## Claim\n\n### Formal Claim\n\n```python\n"
        "from anechoic.formal_claims import declare_entity\n"
        "from anechoic.model import ProjectManifest\n"
        f"declare_entity(entity_name='Project Manifest', instance=ProjectManifest(name={name!r}, prefix={prefix!r}))\n"
        "```\n",
        encoding="utf-8",
    )
    return root


class ChildHTTP:
    """Return the native health, catalog and Tool envelopes over the HTTP boundary."""

    def __init__(self):
        self.started = asyncio.Event()
        self.finish = asyncio.Event()
        self.posted = []
        self.bindings = {}
        self.popen = subprocess.Popen

    def start(self, command, **options):
        if "--socket" not in command or "--instance-id" not in command:
            return self.popen(command, **options)
        socket = command[command.index("--socket") + 1]
        self.bindings[socket] = {
            key: command[command.index(flag) + 1]
            for key, flag in (("instance_id", "--instance-id"), ("manifest_sha256", "--manifest-sha256"))
        }
        return SimpleNamespace(pid=123, poll=lambda: None, stdin=None, wait=lambda timeout: 0)

    def transport(self, *, uds):
        async def request_message(request):
            match request.method, request.url.path:
                case "GET", "/health":
                    value = {"ready": True, "pid": 123, "kernel_pid": 124, **self.bindings[uds]}
                case "GET", "/tools":
                    value = {"result": {"tools": [{"name": _NAME, "inputSchema": {"type": "object"}}],
                                        "blacklist": []}}
                case "POST", "/tools":
                    self.posted.append(json.loads(request.content))
                    self.started.set()
                    await self.finish.wait()
                    value = {"result": {"value": {}, "text": None}}
                case _:
                    raise AssertionError(f"Unexpected child request {request.method} {request.url.path}")
            return httpx2.Response(200, json=value)

        return httpx2.MockTransport(request_message)


class ProjectToolSessionTests(unittest.IsolatedAsyncioTestCase):
    async def test_cancellation_holds_lease_until_dispatched_tool_finishes_without_replay(self):
        root = Path(self.enterContext(TemporaryDirectory())).resolve()
        projects = root / "projects"
        alpha, beta = (_project(projects, name) for name in ("alpha", "beta"))
        settings = root / "host.toml"
        settings.write_text(f'schema_version=1\n[shared_mcp]\nprojects_root="{projects}"\n'
                            'http_port=8092\nmax_loaded_projects=1\n', encoding="utf-8")
        app = create_shared_app(load_host_runtime_config(settings))
        child = ChildHTTP()
        with patch.object(subprocess, "Popen", child.start), patch.object(httpx2, "AsyncHTTPTransport", child.transport):
            async with app.router.lifespan_context(app):
                async with httpx2.AsyncClient(transport=httpx2.ASGITransport(app=app),
                                              base_url="http://shared") as client:
                    await self._assert_cancelled_write(client, child, alpha, beta)

    def _invoke(self, client, root):
        return client.post("/tools", json={
            "name": _NAME, "arguments": {"project_root": str(root)},
            "session_id": "operator", "public_base_url": None,
        })

    async def _assert_cancelled_write(self, client, child, alpha, beta):
        selected = await client.post("/selection", json={"project_root": str(alpha)})
        instance_id = selected.json()["result"]["instance_id"]
        call = asyncio.create_task(self._invoke(client, alpha))
        try:
            await asyncio.wait_for(child.started.wait(), 5)
            call.cancel()
            await asyncio.sleep(0)
            self.assertFalse(call.done())
            busy = await asyncio.wait_for(self._invoke(client, beta), 5)
            self.assertEqual("project_gateway_busy", busy.json()["error"]["code"])
        finally:
            child.finish.set()
            outcome, = await asyncio.wait_for(asyncio.gather(call, return_exceptions=True), 5)
        self.assertIsInstance(outcome, asyncio.CancelledError)
        self.assertEqual([{
            "name": _NAME, "arguments": {}, "instance_id": instance_id,
            "session_id": "operator", "public_base_url": None, "asserted_project_root": str(alpha),
        }], child.posted)
        ready = await self._invoke(client, beta)
        self.assertEqual({"value": {}, "text": None}, ready.json()["result"])
