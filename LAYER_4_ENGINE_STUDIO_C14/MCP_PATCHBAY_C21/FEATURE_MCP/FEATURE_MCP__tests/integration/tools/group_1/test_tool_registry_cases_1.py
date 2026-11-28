"""Functional registry generation and generic MCP Provider dispatch."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
from uuid import uuid4

from mcp.client._memory import InMemoryTransport
from mcp.client.session import ClientSession


from .... import native_query_test_support
from ..group_2.tool_registry_test_support import ToolRegistryFixture
from ..group_2.tool_registry_test_support import _provider_source
from ..group_2.tool_registry_test_support import (
    _mixed_descriptor_provider_source,
)
from ..group_2.tool_registry_test_support import _schema_provider_source
from ..group_2.tool_registry_test_support import _native_gateway

from IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IWE_CONSOLE_BACKEND.\
    generate_tool_registry import (
    generate,
)  # noqa: E402
from IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IWE_CONSOLE_BACKEND.\
    tool_registry_assets import (
    ToolRegistryAssetError,
)  # noqa: E402


MCP = Path(__file__).resolve().parents[4]


class ToolRegistryTests(ToolRegistryFixture, unittest.IsolatedAsyncioTestCase):
    def test_generator_writes_models_and_filters_global_blacklist(
        self,
    ) -> None:
        registry = json.loads(
            generate(self.package).read_text(encoding="utf-8")
        )
        self.assertEqual(["demo"], registry["public_tools"])
        self.assertEqual(
            ["demo", "blocked"],
            [tool["name"] for tool in registry["providers"][0]["tools"]],
        )
        self.assertEqual(["blocked"], registry["mcp_blacklist"])

    def test_generator_refuses_invalid_inventory_before_writing(self) -> None:
        (self.feature / "tool_providers.json").write_text(
            '{"schema_version": 1}', encoding="utf-8"
        )
        with self.assertRaises(ToolRegistryAssetError):
            generate(self.package)
        self.assertFalse((self.feature / "tool_registry.json").exists())

    def test_generator_refuses_an_invalid_registered_tool_schema(self) -> None:
        self._write_provider(
            _provider_source().replace(
                (
                    'schema = {"type": "object", '
                    '"properties": {}, "additiona'
                    'lProperties": False}'
                ),
                'schema = {"type": "not-a-json-schema-type"}',
            )
        )
        with self.assertRaises(ToolRegistryAssetError):
            generate(self.package)
        self.assertFalse((self.feature / "tool_registry.json").exists())

    async def test_real_transport_quarantines_one_invalid_installed_descriptor(
        self,
    ) -> None:
        self._write_provider(_mixed_descriptor_provider_source())
        with self.assertLogs(
            (
                'IWE_CONSOLE_C43.APP_IWE_CONS'
                'OLE.FEATURE_IWE_CONSOLE_BACK'
                'END.generate_tool_registry'
            ),
            level="WARNING",
        ) as generated:
            generate(self.package)
        self.assertIn("broken", generated.output[0])
        root = Path(self.temporary.name).resolve()

        def registry_loader(_asset: Path, selected: Path, gateway: object):
            return self._registry(selected, gateway)

        with patch.object(
            native_query_test_support,
            "load_active_registry",
            side_effect=registry_loader,
        ):
            gateway = _native_gateway(root)
            with self.assertLogs(
                (
                    'IWE_CONSOLE_C43.APP_IWE_CONS'
                    'OLE.FEATURE_IWE_CONSOLE_BACK'
                    'END.generate_tool_registry'
                ),
                level="WARNING",
            ) as loaded:
                await gateway.initialize()
            self.assertIn("broken", loaded.output[0])
            try:
                async with InMemoryTransport(
                    gateway.build_server(), raise_exceptions=True
                ) as streams:
                    async with ClientSession(*streams) as client:
                        await client.initialize()
                        self.assertEqual(
                            {"demo"},
                            {
                                tool.name
                                for tool in (await client.list_tools()).tools
                            },
                        )
                        accepted = await client.call_tool("demo", {})
                        self.assertFalse(accepted.is_error)
                        rejected = await client.call_tool("broken", {})
                        self.assertTrue(rejected.is_error)
            finally:
                await gateway.close()

    def test_duplicate_identity_refuses_publication_even_if_one_descriptor_is_invalid(
        self,
    ) -> None:
        self._write_provider(
            _mixed_descriptor_provider_source().replace(
                'name="broken"', 'name="demo"'
            )
        )
        with self.assertRaises(ToolRegistryAssetError):
            generate(self.package)
        self.assertFalse((self.feature / "tool_registry.json").exists())

    async def test_invalid_only_provider_does_not_block_an_independent_provider(
        self,
    ) -> None:
        invalid_module = "provider_" + uuid4().hex
        self.addCleanup(sys.modules.pop, invalid_module, None)
        source = (
            _mixed_descriptor_provider_source()
            .replace(
                (
                    'types.Tool(name="demo", desc'
                    'ription="Demo", input_schema'
                    '=valid),\n            '
                ),
                "",
            )
            .replace("input_schema=invalid))", "input_schema=invalid),)")
        )
        (self.feature / f"{invalid_module}.py").write_text(
            source, encoding="utf-8"
        )
        inventory_path = self.feature / "tool_providers.json"
        inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
        inventory["providers"].append({
            "provider_id": "invalid_provider",
            "module": invalid_module,
            "factory": "create_provider",
            "descriptor_factory": "tool_descriptors",
        })
        inventory_path.write_text(json.dumps(inventory), encoding="utf-8")
        with self.assertLogs(
            (
                'IWE_CONSOLE_C43.APP_IWE_CONS'
                'OLE.FEATURE_IWE_CONSOLE_BACK'
                'END.generate_tool_registry'
            ),
            level="WARNING",
        ):
            generate(self.package)
        with self.assertLogs(
            (
                'IWE_CONSOLE_C43.APP_IWE_CONS'
                'OLE.FEATURE_IWE_CONSOLE_BACK'
                'END.generate_tool_registry'
            ),
            level="WARNING",
        ):
            active = self._registry(
                Path(self.temporary.name).resolve(), object()
            )
        self.assertEqual({"demo"}, {tool.name for tool in active.tools})
        self.assertEqual(
            {"name": "demo", "arguments": {}}, await active.call("demo", {})
        )
        await active.close()

    def test_duplicate_identity_across_providers_fails_even_when_one_is_invalid(
        self,
    ) -> None:
        self._write_provider(_mixed_descriptor_provider_source())
        second_module = "provider_" + uuid4().hex
        self.addCleanup(sys.modules.pop, second_module, None)
        source = _provider_source().replace('name="demo"', 'name="broken"')
        (self.feature / f"{second_module}.py").write_text(
            source, encoding="utf-8"
        )
        inventory_path = self.feature / "tool_providers.json"
        inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
        inventory["providers"].append({
            "provider_id": "second_provider",
            "module": second_module,
            "factory": "create_provider",
            "descriptor_factory": "tool_descriptors",
        })
        inventory_path.write_text(json.dumps(inventory), encoding="utf-8")
        with self.assertRaisesRegex(ToolRegistryAssetError, "name-duplicates"):
            generate(self.package)
        self.assertFalse((self.feature / "tool_registry.json").exists())

    async def test_real_transport_dispatches_added_provider_and_denies_global_name(
        self,
    ) -> None:
        generate(self.package)
        root = Path(self.temporary.name).resolve()

        def registry_loader(_asset: Path, selected: Path, gateway: object):
            return self._registry(selected, gateway)

        with patch.object(
            native_query_test_support,
            "load_active_registry",
            side_effect=registry_loader,
        ):
            gateway = _native_gateway(root)
            await gateway.initialize()
            try:
                async with InMemoryTransport(
                    gateway.build_server(), raise_exceptions=True
                ) as streams:
                    async with ClientSession(*streams) as client:
                        await client.initialize()
                        self.assertEqual(
                            {"demo"},
                            {
                                tool.name
                                for tool in (await client.list_tools()).tools
                            },
                        )
                        accepted = await client.call_tool("demo", {})
                        self.assertFalse(accepted.is_error)
                        self.assertEqual(
                            {"name": "demo", "arguments": {}},
                            accepted.structured_content,
                        )
                        rejected = await client.call_tool("blocked", {})
                        self.assertTrue(rejected.is_error)
                        self.assertEqual(
                            ["Unknown Tool"],
                            rejected.structured_content["diagnostics"],
                        )
            finally:
                await gateway.close()

    def _prepare_list_descriptor(self):
        source = (
            _schema_provider_source()
            .replace(
                (
                    'return (types.Tool(name="dem'
                    'o", description="Demo", inpu'
                    't_schema=input_schema, outpu'
                    't_schema=output_schema),)'
                ),
                'return tuple(types.Tool(name=name, description=name + " description", '
                "input_schema=input_schema, output_schema=output_schema) "
                'for name in ("demo", "blocked", "project_blocked"))',
            )
            .replace(
                'return {"ok": "invalid"}',
                (
                    'open(__file__ + ".written", '
                    '"w").write(arguments["value"'
                    '])\n        return {"ok": "in'
                    'valid"}'
                ),
            )
        )
        self._write_provider(source)
        registry_path = generate(self.package)
        installed = json.loads(registry_path.read_text(encoding="utf-8"))
        descriptor = next(
            t
            for t in installed["providers"][0]["tools"]
            if t["name"] == "demo"
        )
        return descriptor

    def _assert_listed_metadata(
        self, listed, descriptor, gateway, root, before
    ):
        self.assertEqual(["demo"], [tool.name for tool in listed])
        self.assertEqual(descriptor["description"], listed[0].description)
        self.assertEqual(
            descriptor["inputSchema"]["required"],
            listed[0].input_schema["required"],
        )
        self.assertEqual(
            descriptor["inputSchema"]["properties"]["value"],
            listed[0].input_schema["properties"]["value"],
        )
        self.assertIsNone(gateway.registry.bindings[0].provider)
        self.assertEqual(0, sys.modules[self.module].calls)
        self.assertFalse((self.feature / f"{self.module}.py.written").exists())
        self.assertEqual(
            before, {p.relative_to(root) for p in root.rglob("*")}
        )

    async def test_tools_list_exposes_admitted_registry_metadata_without_execution(
        self,
    ) -> None:
        descriptor = self._prepare_list_descriptor()
        root = Path(self.temporary.name).resolve()

        def registry_loader(_asset: Path, selected: Path, gateway: object):
            return self._registry(selected, gateway)

        with patch.object(
            native_query_test_support,
            "load_active_registry",
            side_effect=registry_loader,
        ):
            gateway = _native_gateway(
                root, {"project_mcp": {"tool_blacklist": ["project_blocked"]}}
            )
            await gateway.initialize()
            try:
                before = {p.relative_to(root) for p in root.rglob("*")}
                async with InMemoryTransport(
                    gateway.build_server(), raise_exceptions=True
                ) as streams:
                    async with ClientSession(*streams) as client:
                        await client.initialize()
                        listed = (await client.list_tools()).tools
                self._assert_listed_metadata(
                    listed, descriptor, gateway, root, before
                )
            finally:
                await gateway.close()
