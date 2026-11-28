"""Shared gateway transport and routing cases."""

import asyncio
import json
from unittest.mock import patch
from mcp import types
from mcp.client._memory import InMemoryTransport
from mcp.client.session import ClientSession

from ..group_2.gateway_test_fixtures import _Gateway
from ..group_2.gateway_test_fixtures import _Session
from ..group_2.gateway_test_fixtures import _tool

from IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IWE_CONSOLE_BACKEND \
    .project_tool_session import ToolProtocolError  # fmt: skip


class GatewayCases:
    async def test_concurrent_projects_keep_identical_native_payloads_isolated(
        self,
    ):
        gateway = await self._gateway()
        first, second = await asyncio.gather(*[
            gateway.call(
                None,
                types.CallToolRequestParams(
                    name="echo",
                    arguments={
                        "project_root": str(root),
                        "request": "same-id",
                    },
                ),
            )
            for root in self.roots
        ])
        self.assertEqual(
            [str(root) for root in self.roots],
            [
                first.structured_content["root"],
                second.structured_content["root"],
            ],
        )
        self.assertEqual(
            {"request": "same-id"}, first.structured_content["arguments"]
        )
        self.assertEqual(
            {"request": "same-id"}, second.structured_content["arguments"]
        )

    async def test_disabled_outside_and_schema_conflict_refuse(self):
        _Gateway.blacklist_by_root = {str(self.roots[0]): frozenset({"echo"})}
        gateway = await self._gateway()
        disabled = await gateway.call(
            None,
            types.CallToolRequestParams(
                name="echo",
                arguments={"project_root": str(self.roots[0]), "request": "x"},
            ),
        )
        outside = await gateway.call(
            None,
            types.CallToolRequestParams(
                name="echo",
                arguments={"project_root": str(self.base), "request": "x"},
            ),
        )
        self.assertTrue(disabled.is_error)
        self.assertTrue(outside.is_error)
        self.assertEqual(
            ["outside_project_root"], outside.structured_content["diagnostics"]
        )

        _Gateway.blacklist_by_root = {}
        _Gateway.tools_by_root[str(self.roots[1])] = [_tool(field="other")]
        conflict = await self._gateway()
        self.assertNotIn("echo", {tool.name for tool in conflict.tools})
        self.assertIn(
            "PROJECT_TOOL_CONTRACT_CONFLICT",
            [row["code"] for row in (await conflict.status())["warnings"]],
        )

    async def _case_1(
        self,
    ):
        invalid = types.Tool(
            name="invalid",
            inputSchema={
                "$ref": "#/$defs/Args",
                "$defs": {"Args": {"type": "object"}},
            },
        )
        _Gateway.tools_by_root = {
            str(root): [_tool(), invalid]
            for root in (*self.roots, self.nested)
        }
        gateway = await self._gateway()

        self.assertIn(
            "PROJECT_TOOL_CONTRACT_INVALID",
            [row["code"] for row in (await gateway.status())["warnings"]],
        )
        async with InMemoryTransport(
            gateway.build_server(), raise_exceptions=True
        ) as streams:
            async with ClientSession(*streams) as client:
                await client.initialize()
                self.assertEqual(
                    {"echo"},
                    {tool.name for tool in (await client.list_tools()).tools},
                )
                accepted = await client.call_tool(
                    "echo",
                    {"project_root": str(self.roots[0]), "request": "ok"},
                )
                self.assertFalse(accepted.is_error)
                self.assertEqual(
                    {"request": "ok"}, accepted.structured_content["arguments"]
                )
                rejected = await client.call_tool(
                    "invalid", {"project_root": str(self.roots[0])}
                )
                self.assertTrue(rejected.is_error)

    async def _case_2(
        self,
    ):
        gateway = await self._gateway()

        class StaleRegistry:
            def ensure_current(self):
                raise ToolProtocolError(
                    "tool_registry_stale", "tool-registry-stale"
                )

        with (
            patch.object(_Session, "registry", StaleRegistry(), create=True),
            patch.object(
                _Session,
                "call_tool",
                side_effect=AssertionError("must not invoke provider"),
            ) as invoke,
        ):
            async with InMemoryTransport(
                gateway.build_server(), raise_exceptions=True
            ) as streams:
                async with ClientSession(*streams) as client:
                    await client.initialize()
                    refused = await client.call_tool(
                        "echo",
                        {
                            "project_root": str(self.roots[0]),
                            "request": "test",
                        },
                    )
                    self.assertTrue(refused.is_error)
                    self.assertEqual(
                        ["tool_registry_stale"],
                        refused.structured_content["diagnostics"],
                    )
                    invoke.assert_not_awaited()

    async def _case_3(
        self,
    ):
        _Gateway.tools_by_root[str(self.nested)] = [
            _tool(),
            _tool(name="new_tool"),
        ]
        gateway = await self._gateway()
        known = await gateway.call(
            None,
            types.CallToolRequestParams(
                name="echo",
                arguments={"project_root": str(self.nested), "request": "x"},
            ),
        )
        new = await gateway.call(
            None,
            types.CallToolRequestParams(
                name="new_tool",
                arguments={"project_root": str(self.nested), "request": "x"},
            ),
        )
        secret = self.base / "SECRET_PROJECT_ROOT"
        secret.mkdir()
        rejected = await gateway.call(
            None,
            types.CallToolRequestParams(
                name="echo",
                arguments={"project_root": str(secret), "request": "x"},
            ),
        )
        self.assertEqual(str(self.nested), known.structured_content["root"])
        self.assertEqual(
            ["tool_unavailable"], new.structured_content["diagnostics"]
        )
        self.assertNotIn(
            "SECRET_PROJECT_ROOT",
            json.dumps(rejected.model_dump(by_alias=True)),
        )


setattr(
    GatewayCases,
    "test_invalid_descriptor_is_quarantined_without_blocking_valid_tool",
    GatewayCases._case_1,
)

setattr(
    GatewayCases,
    "test_stale_registration_is_rejected_before_shared_transport_dispatch",
    GatewayCases._case_2,
)

setattr(
    GatewayCases,
    "test_nested_project_uses_known_tool_but_new_name_and_secret_refuse",
    GatewayCases._case_3,
)
