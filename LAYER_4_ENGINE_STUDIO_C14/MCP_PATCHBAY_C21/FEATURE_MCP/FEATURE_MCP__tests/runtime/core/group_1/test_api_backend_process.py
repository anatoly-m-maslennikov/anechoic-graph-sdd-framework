"""Default MCP and web calls share a separate Backend process."""

import asyncio
from dataclasses import replace
import json
import os
from pathlib import Path
import shutil
import signal
import shlex as shlex
import sys
import tempfile
from threading import Event
import time
import unittest
from unittest.mock import patch

import httpx2
from mcp import types as types
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
from starlette.applications import Starlette

from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__tests.runtime.\
    project.group_2.backend_lifecycle_probe import (
    _assert_lifecycle_projection,
)

from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__tests.runtime.\
    core.group_2 import (
    _api_backend_process_cases as cases,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__tests import (
    FEATURE_MCP__tests__shared as shared_fixture,
)

_project = shared_fixture.project

MCP = Path(__file__).resolve().parents[4]
ROOT = MCP.parents[2]

from MCP_PATCHBAY_C21.FEATURE_MCP.gateway.gateway__shared import (  # noqa: E402
    native_runtime_gateway,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared \
    import BackendClient  # noqa: E402
from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared \
    import ToolProtocolError  # noqa: E402
from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import (  # noqa: E402
    select_runtime_project,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.gateway.gateway__shared import (  # noqa: E402
    routes as routes,
)

CONTROL = "_anechoic_anechoic"
QUERY = "SELECT 42 AS answer"


def _test_environment():
    return {
        "ANECHOIC_RUNTIME_NAMESPACE": "docker",
        "ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY": os.environ.get(
            "ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY",
            str(ROOT / ".anechoic_tmp/workbench/extensions"),
        ),
    }


def _release_claim(root):
    directory = root / CONTROL / "__PROJECT_CONFIG"
    directory.mkdir(exist_ok=True)
    name = "AN-P-58-WORKFLOW--release-a-selected-framework-version.md"
    claim = directory / name
    source = ROOT / CONTROL / "__PROJECT_CONFIG" / name
    if not source.is_file():
        source = ROOT / CONTROL / "002_PROJECT_CONFIG" / name
    shutil.copyfile(source, claim)
    script = root / "LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/release.py"
    script.parent.mkdir(parents=True, exist_ok=True)
    script.write_text("# fixture; never executed\n", encoding="utf-8")
    return claim, script


async def _gateway_process(root):
    """Exercise the HTTP route in the very gateway that serves MCP stdio."""
    selection = select_runtime_project(root, CONTROL)
    with native_runtime_gateway(selection) as gateway:
        try:
            await gateway.initialize()
            app = Starlette(routes=routes(gateway))
            async with httpx2.AsyncClient(
                transport=httpx2.ASGITransport(app=app),
                base_url="http://127.0.0.1",
            ) as client:
                invalid = await client.post(
                    "/anechoic/Anechoic/api/run",
                    json={
                        "sql": QUERY,
                        "name": "without-save",
                    },
                )
                response = await client.post(
                    "/anechoic/Anechoic/api/run",
                    json={
                        "sql": QUERY,
                        "result_delivery": "inline",
                    },
                )
            rejected_method = await asyncio.to_thread(
                _raw_method_reply, gateway._native_query
            )
            cases.write_gateway_probe(
                root, gateway, response, invalid, rejected_method, globals()
            )
            await gateway.serve()
        finally:
            await gateway.close()


def _raw_method_reply(owner):
    return owner._http.post(
        "/workbench",
        json={
            "operation": "run",
            "name": "query_run",
            "arguments": {"sql": QUERY},
            "instance_id": owner.selection.instance_id,
            "session_id": None,
        },
    ).json()


def _kernel_pid(owner):
    response = owner._http.get("/health", timeout=2)
    response.raise_for_status()
    health = response.json()
    pid = health["kernel_pid"]
    if (
        health["pid"] != owner.backend_pid
        or health["instance_id"] != owner.selection.instance_id
        or type(pid) is not int
        or pid <= 1
        or pid in {owner.backend_pid, os.getpid()}
    ):
        raise AssertionError(
            "Kernel PID is outside the admitted Backend binding"
        )
    return pid


def _assert_process_stopped(test, pid):
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return
        time.sleep(0.05)
    test.fail("Backend process survived gateway shutdown")


class ApiBackendProcessTests(unittest.IsolatedAsyncioTestCase):
    async def test_backend_exit_preserves_unavailable_error(self):
        await self._assert_process_failure(kernel_exits=False)

    async def test_kernel_exit_preserves_unavailable_error(self):
        await self._assert_process_failure(kernel_exits=True)

    async def _assert_process_failure(self, *, kernel_exits):
        with (
            tempfile.TemporaryDirectory() as temporary,
            patch.dict(os.environ, _test_environment()),
        ):
            root = Path(temporary).resolve()
            _project(root)
            with native_runtime_gateway(
                select_runtime_project(root, CONTROL)
            ) as gateway:
                try:
                    await gateway.initialize()
                    process = gateway._native_query._process
                    kernel = _kernel_pid(gateway._native_query)
                    os.kill(
                        kernel if kernel_exits else process.pid, signal.SIGTERM
                    )
                    await asyncio.to_thread(process.wait, 15)
                    self.assertFalse(gateway.ready)
                    with self.assertRaises(ToolProtocolError) as caught:
                        await gateway.workbench.call_tool("query_schema", {})
                    self.assertEqual(
                        "tool_runtime_failure", caught.exception.code
                    )
                finally:
                    await gateway.close()
                _assert_process_stopped(self, kernel)

    async def test_cancelled_startup_reaps_child_before_returning(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            _project(root)
            await self._cancel_startup(select_runtime_project(root, CONTROL))

    async def _cancel_startup(self, selection):
        entered, release = Event(), Event()
        start = BackendClient.start

        def paused_start(owner):
            entered.set()
            release.wait(timeout=30)
            start(owner)

        with (
            patch.dict(os.environ, _test_environment()),
            patch.object(BackendClient, "start", paused_start),
            native_runtime_gateway(selection) as gateway,
        ):
            pending = asyncio.create_task(gateway.initialize())
            try:
                self.assertTrue(await asyncio.to_thread(entered.wait, 5))
                owner = gateway._native_query
                pending.cancel()
                with self.assertRaises(asyncio.CancelledError):
                    await pending
                self.assertIsNotNone(owner._process.returncode)
                self.assertFalse(gateway.ready)
            finally:
                release.set()

    async def test_backend_refuses_a_changed_manifest_pin(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            _project(root)
            selection = replace(
                select_runtime_project(root, CONTROL), manifest_sha256="0" * 64
            )
            with native_runtime_gateway(selection) as gateway:
                with self.assertRaisesRegex(
                    RuntimeError, "Backend did not start"
                ):
                    await gateway.initialize()
                self.assertFalse(gateway.ready)
                self.assertEqual(1, gateway._native_query._process.returncode)

    async def test_backend_release_command_requires_manifest_enablement(self):
        with (
            tempfile.TemporaryDirectory() as temporary,
            patch.dict(os.environ, _test_environment()),
        ):
            root = Path(temporary).resolve()
            _project(root)
            _release_claim(root)
            manifest = (
                root / "AN-S-3037-SPEC-PROJECT_MANIFEST--declare-anechoic.md"
            )
            original = manifest.read_text(encoding="utf-8")
            self.assertIn("'release_workflows_enabled': True", original)
            manifest.write_text(
                original.replace(
                    "'release_workflows_enabled': True",
                    "'release_workflows_enabled': False",
                ),
                encoding="utf-8",
            )
            selection = select_runtime_project(root, CONTROL)
            self.assertFalse(selection.release_workflows_enabled)
            with native_runtime_gateway(selection) as gateway:
                try:
                    await gateway.initialize()
                    self.assertNotIn(
                        "local_release_command",
                        {tool.name for tool in gateway.tools},
                    )
                    with self.assertRaises(ToolProtocolError) as caught:
                        await gateway.workbench.call_tool(
                            "local_release_command", {"run_id": "smoke-1"}
                        )
                    self.assertEqual("tool_unavailable", caught.exception.code)
                finally:
                    await gateway.close()

    async def test_release_command_uses_backend_claim_and_rejects_stale_or_duplicate_inputs(
        self,
    ):
        await cases.release_case(self, globals())

    async def test_stdio_and_web_share_backend_and_shutdown(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            _project(root)
            parameters = StdioServerParameters(
                command=sys.executable,
                args=["-B", "-P", "-m", __name__, str(root)],
                env={**_test_environment(), "PYTHONPATH": str(MCP.parents[1])},
            )
            async with (
                asyncio.timeout(90),
                stdio_client(parameters) as streams,
            ):
                async with ClientSession(*streams) as client:
                    await client.initialize()
                    probe = json.loads(
                        (root / "gateway-probe.json").read_text(
                            encoding="utf-8"
                        )
                    )
                    self._assert_web_probe(probe)
                    refused = await client.call_tool(
                        "query_rebuild", {"target": "unknown_table"}
                    )
                    self.assertTrue(refused.is_error)
                    self.assertEqual(
                        [
                            "query_error: Unknown Workbench rebuild target: "
                            "'unknown_table'"
                        ],
                        refused.structured_content["diagnostics"],
                    )
                    reply = await client.call_tool(
                        "query_page",
                        {
                            "query_id": probe["http_body"]["query_id"],
                            "result_delivery": "inline",
                        },
                    )
                    self.assertFalse(reply.is_error, reply.structured_content)
                    self.assertEqual([[42]], reply.structured_content["rows"])
                    await _assert_lifecycle_projection(self, client, root)
            _assert_process_stopped(self, probe["backend_pid"])
            _assert_process_stopped(self, probe["kernel_pid"])

    def _assert_web_probe(self, probe):
        cases.assert_web_probe(self, probe, os)


if __name__ == "__main__":
    asyncio.run(_gateway_process(Path(sys.argv[1]).resolve()))
