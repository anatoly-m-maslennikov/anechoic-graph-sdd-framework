"""Focused health and failure-boundary checks for the shared gateway."""

from __future__ import annotations

import asyncio
from concurrent.futures import CancelledError as FutureCancelledError
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

MCP = Path(__file__).resolve().parents[1]
TOOLS = MCP.parents[1] / "FEATURE_PROGRAMMATIC" / "FEATURE_TOOLS"

from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import render_health_page  # noqa: E402
from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.FEATURE_WORKBENCH_BACKEND__shared import load_host_runtime_config  # noqa: E402
from mcp import types  # noqa: E402
from .test_native_startup import RuntimeSelectionTests  # noqa: E402
from .shared_backend_fixture import backend_gateway  # noqa: E402


def _tool():
    return types.Tool(name="echo", inputSchema={"type": "object"}, outputSchema={"type": "object"})


class _Gateway:
    hold = None
    started = None

    def __init__(self, _root, *, selection):
        self.selection = selection
        self.ready = True
        self.tools = [_tool().model_dump(mode="json", by_alias=True)]
        self.tool_blacklist = frozenset()

    async def initialize(self):
        return None

    async def close(self):
        return None

    async def ensure_current(self):
        return None

    async def call_tool(self, _name, _arguments, *, session_id, public_base_url, asserted_project_root):
        if self.started is not None:
            self.started.set()
        if self.hold is not None:
            await self.hold.wait()
        return {"value": {"outcome": "completed"}, "text": None}


class SharedGatewayHealthTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name).resolve()
        self.projects = self.base / "My_Repos"
        self.root = self._project("alpha")
        self.other = self._project("beta")

    def _project(self, name):
        root = self.projects / name
        control = root / f".anechoic_{name}"
        RuntimeSelectionTests.manifest(
            self, control, name=root.name, prefix="".join(c for c in root.name.upper() if c.isalpha()), component="C00",
        )
        return root

    def _config(self, max_loaded=2):
        self.config_path = self.base / "MCP_PATCHBAY_C21.FEATURE_MCP.docker.runtime.toml"
        self.config_path.write_text(
            "schema_version=1\n[shared_mcp]\n"
            f'projects_root="{self.projects}"\nhttp_port=8092\nmax_loaded_projects={max_loaded}\n'
        )
        _Gateway.hold = None
        _Gateway.started = None

    async def _gateway(self):
        return await self.enterAsyncContext(
            backend_gateway(load_host_runtime_config(self.config_path), _Gateway)
        )

    def _params(self, root=None):
        return types.CallToolRequestParams(
            name="echo", arguments={"project_root": str(self.root if root is None else root)}
        )

    async def test_status_and_html_contain_attributable_observations(self):
        self._config()
        gateway = await self._gateway()
        await gateway.call(None, self._params())
        status = await gateway.status()
        self.assertEqual(1, len(status["calls"]))
        self.assertNotIn("workflows", status)
        self.assertEqual("ALPHA", status["calls"][0]["project_prefix"])
        self.assertEqual(1, len(status["known_project_contexts"]))
        html = render_health_page(status, state="ready", gateway=gateway)
        self.assertIn("Known Project contexts", html)
        self.assertIn(status["calls"][0]["project_instance_id"], html)
        projects = html.split('<section aria-labelledby="projects">')[1].split("</section>")[0]
        self.assertIn("ALPHA / " + status["calls"][0]["project_instance_id"], projects)

    async def test_observer_failure_warns_without_replacing_native_success(self):
        class BrokenObserver:
            def record(self, *_args, **_kwargs):
                raise RuntimeError("SECRET_OBSERVER_FAILURE")

        self._config()
        gateway = await self._gateway()
        gateway.health_observations = BrokenObserver()
        with patch("MCP_PATCHBAY_C21.FEATURE_MCP.shared_gateway_support.warning") as reported:
            response = await gateway.call(None, self._params())
        self.assertFalse(response.is_error)
        reported.assert_called_once_with("health_observation_failed")

    async def test_async_and_future_cancellation_are_not_adapted_to_success(self):
        self._config()
        gateway = await self._gateway()
        wait = asyncio.Event()
        _Gateway.hold = wait
        _Gateway.started = asyncio.Event()
        pending = asyncio.create_task(gateway.call(None, self._params()))
        await asyncio.wait_for(_Gateway.started.wait(), 10)
        pending.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await pending
        missing_root = types.CallToolRequestParams(name="echo", arguments={})
        with patch("MCP_PATCHBAY_C21.FEATURE_MCP.shared_gateway_support.warning", return_value="technical diagnostic emission failed"):
            refusal_result = await gateway.call(None, missing_root)
        self.assertTrue(refusal_result.is_error)
        self.assertEqual(
            ["missing_project_root", "technical_diagnostics_unavailable"],
            refusal_result.structured_content["diagnostics"],
        )
        with patch("MCP_PATCHBAY_C21.FEATURE_MCP.shared_gateway_support.warning", side_effect=FutureCancelledError()):
            with self.assertRaises(FutureCancelledError):
                await gateway.call(None, missing_root)

    async def test_observer_future_cancellation_propagates(self):
        class CancelledObserver:
            def record(self, *_args, **_kwargs):
                raise FutureCancelledError()

        self._config()
        gateway = await self._gateway()
        gateway.health_observations = CancelledObserver()
        with self.assertRaises(FutureCancelledError):
            await gateway.call(None, self._params())

    async def test_busy_capacity_refuses_another_project(self):
        self._config(max_loaded=1)
        gateway = await self._gateway()
        _Gateway.hold = asyncio.Event()
        _Gateway.started = asyncio.Event()
        first = asyncio.create_task(gateway.call(None, self._params()))
        await asyncio.wait_for(_Gateway.started.wait(), 10)
        refused = await gateway.call(
            None,
            types.CallToolRequestParams(name="echo", arguments={"project_root": str(self.other)}),
        )
        self.assertTrue(refused.is_error)
        _Gateway.hold.set()
        self.assertFalse((await first).is_error)

    async def test_known_project_contexts_are_bounded(self):
        roots = [
            self.root,
            *[self._project(f"project{index}") for index in range(32)],
        ]
        self._config()
        gateway = await self._gateway()
        for root in roots:
            await gateway.call(None, self._params(root))
        contexts = (await gateway.status())["known_project_contexts"]
        self.assertEqual(32, len(contexts))
        self.assertNotIn("ALPHA", [context["prefix"] for context in contexts])


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
