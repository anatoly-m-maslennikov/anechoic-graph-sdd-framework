
"""Functional registry generation and generic MCP Provider dispatch."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

from mcp.client._memory import InMemoryTransport
from mcp.client.session import ClientSession
from mcp import types


MCP = Path(__file__).resolve().parents[1]
from IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IWE_CONSOLE_BACKEND.generate_tool_registry import generate  # noqa: E402
from IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IWE_CONSOLE_BACKEND.tool_registry_assets import ToolRegistryAssetError  # noqa: E402
from IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IWE_CONSOLE_BACKEND.FEATURE_IWE_CONSOLE_BACKEND__shared import (  # noqa: E402
    ToolRegistryRuntimeError, ToolRegistryStaleError,
)



from . import native_query_test_support
from .tool_registry_test_support import ToolRegistryFixture, _drifting_provider_source, _context_provider_source, _native_gateway


class ToolRegistryTests(ToolRegistryFixture, unittest.IsolatedAsyncioTestCase):
    async def test_real_transport_rejects_a_changed_registration_before_invocation(self) -> None:
        registry_path = generate(self.package)
        root = Path(self.temporary.name).resolve()

        def registry_loader(_asset: Path, selected: Path, gateway: object):
            return self._registry(selected, gateway)

        with patch.object(native_query_test_support, "load_active_registry", side_effect=registry_loader):
            gateway = _native_gateway(root)
            await gateway.initialize()
            try:
                async with InMemoryTransport(gateway.build_server(), raise_exceptions=True) as streams:
                    async with ClientSession(*streams) as client:
                        await client.initialize()
                        registry_path.write_text(
                            registry_path.read_text(encoding="utf-8") + "\n", encoding="utf-8"
                        )
                        refused = await client.call_tool("demo", {})
                        self.assertTrue(refused.is_error)
                        self.assertEqual("rejected", refused.structured_content["outcome"])
                        self.assertEqual(
                            ["tool_registry_stale"], refused.structured_content["diagnostics"]
                        )
                        self.assertIsNone(gateway.registry.bindings[0].provider)
            finally:
                await gateway.close()


    async def test_real_transport_refuses_registration_changed_during_prepare(self) -> None:
        self._write_provider(_drifting_provider_source())
        generate(self.package)
        root = Path(self.temporary.name).resolve()

        def registry_loader(_asset: Path, selected: Path, gateway: object):
            return self._registry(selected, gateway)

        with patch.object(native_query_test_support, "load_active_registry", side_effect=registry_loader):
            gateway = _native_gateway(root)
            await gateway.initialize()
            try:
                async with InMemoryTransport(gateway.build_server(), raise_exceptions=True) as streams:
                    async with ClientSession(*streams) as client:
                        await client.initialize()
                        refused = await client.call_tool("demo", {})
                        self.assertTrue(refused.is_error)
                        self.assertEqual(["tool_registry_stale"], refused.structured_content["diagnostics"])
                        self.assertEqual(0, sys.modules[self.module].calls)
            finally:
                await gateway.close()


    async def test_direct_transport_preserves_native_session_and_isolates_caller_context(self) -> None:
        self._write_provider(_context_provider_source())
        generate(self.package)
        root = Path(self.temporary.name).resolve()

        def registry_loader(_asset: Path, selected: Path, gateway: object):
            return self._registry(selected, gateway)

        with patch.object(native_query_test_support, "load_active_registry", side_effect=registry_loader):
            gateway = _native_gateway(root)
            await gateway.initialize()
            try:
                async with InMemoryTransport(gateway.build_server(), raise_exceptions=True) as streams:
                    async with ClientSession(*streams) as client:
                        await client.initialize()
                        tool = (await client.list_tools()).tools[0]
                        self.assertIn("caller_context", tool.input_schema["properties"])
                        response = await client.call_tool("demo", {
                            "session_id": "native", "caller_context": {"session_id": "caller"},
                        })
                        self.assertFalse(response.is_error)
                        self.assertEqual({"native": {"session_id": "native"}, "caller": "caller"},
                                         response.structured_content)
                        stateless = await client.call_tool("demo", {"session_id": "native"})
                        self.assertEqual({"native": {"session_id": "native"}, "caller": None},
                                         stateless.structured_content)
                await self._check_context_isolation(gateway, root)
            finally:
                await gateway.close()


    async def _check_context_isolation(self, gateway, root):
        invalid = await gateway.call(None, types.CallToolRequestParams(
            name="demo", arguments={"caller_context": {"session_id": "  "}}
        ))
        self.assertTrue(invalid.is_error)
        self.assertEqual(["invalid_caller_context"], invalid.structured_content["diagnostics"])
        from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import (
            RuntimeRequestContext, bind_request_context, current_request_context,
        )
        with bind_request_context(RuntimeRequestContext("existing")):
            matching = await gateway.call(None, types.CallToolRequestParams(
                name="demo", arguments={"caller_context": {"session_id": "existing"}}
            ))
            self.assertFalse(matching.is_error)
            self.assertEqual("existing", matching.structured_content["caller"])
            conflict = await gateway.call(None, types.CallToolRequestParams(
                name="demo", arguments={"caller_context": {"session_id": "other"}}
            ))
            self.assertEqual("existing", current_request_context().session_id)
        self.assertTrue(conflict.is_error)
        self.assertEqual(["caller_context_conflict"], conflict.structured_content["diagnostics"])
        self.assertIsNone(current_request_context())
        foreign = await gateway.call(None, types.CallToolRequestParams(
            name="demo", arguments={"project_root": str(root / "foreign"),
                                    "caller_context": {"session_id": "caller"}}
        ))
        self.assertTrue(foreign.is_error)
        self.assertEqual(3, sys.modules[self.module].calls)

    async def test_project_blacklist_cannot_reenable_a_global_deny(self) -> None:
        generate(self.package)
        root = Path(self.temporary.name).resolve()
        def registry_loader(_asset: Path, selected: Path, gateway: object):
            return self._registry(selected, gateway)

        with patch.object(native_query_test_support, "load_active_registry", side_effect=registry_loader):
            gateway = _native_gateway(root, {"project_mcp": {"tool_blacklist": ["demo"]}})
            await gateway.initialize()
            try:
                self.assertEqual(set(), {tool.name for tool in gateway.tools})
                self.assertEqual(frozenset({"blocked", "demo"}), gateway.tool_blacklist)
            finally:
                await gateway.close()


    def test_runtime_refuses_missing_or_stale_generated_asset(self) -> None:
        root = Path(self.temporary.name).resolve()
        with self.assertRaises(ToolRegistryRuntimeError):
            self._registry(root, object())
        generate(self.package)
        self._write_inventory(blacklist=[])
        with self.assertRaises(ToolRegistryRuntimeError):
            self._registry(root, object())


    async def test_registry_refuses_changed_or_missing_inventory_before_provider_creation(self) -> None:
        generate(self.package)
        active = self._registry(Path(self.temporary.name).resolve(), object())
        inventory = self.feature / "tool_providers.json"
        original = inventory.read_text(encoding="utf-8")
        for value in (original + "\n", None):
            with self.subTest(missing=value is None):
                if value is None:
                    inventory.unlink()
                else:
                    inventory.write_text(value, encoding="utf-8")
                with self.assertRaises(ToolRegistryStaleError):
                    await active.call("demo", {})
                self.assertIsNone(active.bindings[0].provider)
                inventory.write_text(original, encoding="utf-8")
        await active.close()


    def test_registry_rejects_duplicate_keys_and_boolean_schema_versions(self) -> None:
        duplicate = '''{"schema_version":1,"mcp_blacklist":["blocked"],"mcp_blacklist":[],"providers":[{"provider_id":"demo_provider","module":"%s","factory":"create_provider","descriptor_factory":"tool_descriptors"}]}''' % self.module
        (self.feature / "tool_providers.json").write_text(duplicate, encoding="utf-8")
        with self.assertRaises(ToolRegistryAssetError):
            generate(self.package)
        self._write_inventory()
        registry = generate(self.package)
        payload = json.loads(registry.read_text(encoding="utf-8"))
        payload["schema_version"] = True
        registry.write_text(json.dumps(payload), encoding="utf-8")
        with self.assertRaises(ToolRegistryRuntimeError):
            self._registry(Path(self.temporary.name).resolve(), object())
        self._write_inventory()
        (self.feature / "tool_providers.json").write_text(
            (self.feature / "tool_providers.json").read_text(encoding="utf-8").replace(
                '"schema_version": 1', '"schema_version": true'
            ), encoding="utf-8",
        )
        with self.assertRaises(ToolRegistryAssetError):
            generate(self.package)


