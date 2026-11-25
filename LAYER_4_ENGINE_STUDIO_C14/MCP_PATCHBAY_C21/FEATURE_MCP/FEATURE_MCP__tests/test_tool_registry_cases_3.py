
"""Functional registry generation and generic MCP Provider dispatch."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from mcp.client._memory import InMemoryTransport
from mcp.client.session import ClientSession


MCP = Path(__file__).resolve().parents[1]
from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.generate_tool_registry import generate  # noqa: E402
from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.FEATURE_WORKBENCH_BACKEND__shared import shared_project_catalog  # noqa: E402
from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.FEATURE_WORKBENCH_BACKEND__shared import (  # noqa: E402
    ToolRegistryRuntimeError,
)



from .tool_registry_test_support import ToolRegistryFixture, _schema_provider_source, _lifecycle_provider_source, _saved_id_provider_source, _partial_provider_source, _native_gateway


class ToolRegistryTests(ToolRegistryFixture, unittest.IsolatedAsyncioTestCase):
    def test_runtime_refuses_generated_descriptor_drift(self) -> None:
        registry_path = generate(self.package)
        payload = json.loads(registry_path.read_text(encoding="utf-8"))
        payload["providers"][0]["tools"][0]["description"] = "stale"
        registry_path.write_text(json.dumps(payload), encoding="utf-8")
        with self.assertRaises(ToolRegistryRuntimeError):
            self._registry(Path(self.temporary.name).resolve(), object())


    async def test_invalid_metadata_never_creates_provider_and_close_is_exactly_once(self) -> None:
        self._write_provider(_lifecycle_provider_source())
        registry_path = generate(self.package)
        payload = json.loads(registry_path.read_text(encoding="utf-8"))
        payload["public_tools"] = []
        registry_path.write_text(json.dumps(payload), encoding="utf-8")
        with self.assertRaises(ToolRegistryRuntimeError):
            self._registry(Path(self.temporary.name).resolve(), object())
        module = sys.modules[self.module]
        self.assertEqual((0, 0), (module.created, module.closed))

        generate(self.package)
        active = self._registry(Path(self.temporary.name).resolve(), object())
        self.assertEqual((0, 0), (module.created, module.closed))
        self.assertEqual({"ok": True}, await active.call("demo", {}))
        self.assertEqual((1, 0), (module.created, module.closed))
        await active.close()
        await active.close()
        self.assertEqual((1, 1), (module.created, module.closed))


    async def test_invalid_partial_provider_is_closed(self) -> None:
        self._write_provider(_partial_provider_source())
        generate(self.package)
        active = self._registry(Path(self.temporary.name).resolve(), object())
        with self.assertRaises(ToolRegistryRuntimeError):
            await active.call("demo", {})
        module = sys.modules[self.module]
        self.assertEqual((1, 1), (module.created, module.closed))


    async def test_real_mcp_rejects_invalid_input_before_call_and_invalid_output_after_call(self) -> None:
        self._write_provider(_schema_provider_source())
        generate(self.package)
        root = Path(self.temporary.name).resolve()

        def registry_loader(_asset: Path, selected: Path, gateway: object):
            return self._registry(selected, gateway)

        with patch("MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__tests.native_query_test_support.load_active_registry", side_effect=registry_loader):
            gateway = _native_gateway(root)
            await gateway.initialize()
            try:
                async with InMemoryTransport(gateway.build_server(), raise_exceptions=True) as streams:
                    async with ClientSession(*streams) as client:
                        await client.initialize()
                        invalid = await client.call_tool("demo", {"value": 1})
                        self.assertTrue(invalid.is_error)
                        self.assertEqual("rejected", invalid.structured_content["outcome"])
                        self.assertEqual(0, sys.modules[self.module].calls)
                        bad_output = await client.call_tool("demo", {"value": "ok"})
                        self.assertTrue(bad_output.is_error)
                        self.assertTrue(
                            bad_output.structured_content["diagnostics"][0].startswith(
                                "tool_output_invalid:"
                            )
                        )
                        self.assertEqual(1, sys.modules[self.module].calls)
            finally:
                await gateway.close()
        self.assertEqual(1, sys.modules[self.module].closed)


    async def test_generic_provider_result_is_not_rewritten_as_a_workbench_url(self) -> None:
        self._write_provider(_saved_id_provider_source())
        generate(self.package)
        root = Path(self.temporary.name).resolve()

        def registry_loader(_asset: Path, selected: Path, gateway: object):
            return self._registry(selected, gateway)

        with patch("MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__tests.native_query_test_support.load_active_registry", side_effect=registry_loader):
            gateway = _native_gateway(root)
            await gateway.initialize()
            try:
                gateway.selection = SimpleNamespace(project_name="example", parameters={})
                context = SimpleNamespace(
                    request=SimpleNamespace(base_url="http://mcp.test"),
                    params=SimpleNamespace(arguments={}),
                )
                response = await gateway.call(context, SimpleNamespace(name="demo", arguments={}))
                self.assertEqual(
                    {"saved_query_id": "q_0123456789abcdef0123456789abcdef"},
                    response.structured_content,
                )
            finally:
                await gateway.close()


    async def test_registry_failure_is_an_error_and_blocks_shared_discovery(self) -> None:
        root = Path(self.temporary.name).resolve()
        from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import ToolProtocolError
        from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.project_tool_session import ToolProtocolError as SessionProtocolError

        failure = SessionProtocolError("tool_runtime_failure", "tool-registry-unavailable: invalid")
        with patch("MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__tests.native_query_test_support.load_active_registry", side_effect=ToolRegistryRuntimeError("invalid")):
            with self.assertRaises(ToolProtocolError):
                await _native_gateway(root).initialize()

        class BrokenGateway:
            def __init__(self, *_args, **_kwargs):
                self.ready = False

            async def initialize(self):
                raise failure

            async def close(self):
                return None

        config = SimpleNamespace(projects_root=root.parent)
        selection = SimpleNamespace(root=root)
        frontier = shared_project_catalog.SharedToolFrontier()
        with patch.object(shared_project_catalog, "resolve_host_project", return_value=selection):
            with self.assertRaises(SessionProtocolError):
                await shared_project_catalog._discover_project(config, root, BrokenGateway, frontier)
        self.assertNotIn("PROJECT_CANDIDATE_INVALID", [row["code"] for row in frontier.warnings])


