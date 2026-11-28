import asyncio
import sys
from pathlib import Path

from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

MCP = Path(__file__).resolve().parents[4]


class ComponentCases:
    def _write_component_queries(self):
        self._write(
            "AN-S-011-manifest.md",
            "AN-S-011",
            "active",
            1,
            template="component_manifest",
            lens="SPEC",
            tier=1,
            body="""## Summary

Tools.

## Purpose

Provide project tools.

## Component Contract

Guarantee.

## Component Identity

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest
declare_entity(
    entity_name="Component Manifest",
    instance=ComponentManifest(
        component_id="C1", name="Tools", layer=3, lens_whitelist=["SPEC"]
    ),
)
```
""",
        )
        self._write(
            "AN-S-012-child-manifest.md",
            "AN-S-012",
            "active",
            1,
            template="component_manifest",
            lens="SPEC",
            container={"component": "C1"},
            body="## Claim\n\n### Component ID\n\nC2\n\n### Name\n\nChild\n",
        )
        self._write_component_contracts()

    def _write_component_contracts(self):
        self._write(
            "AN-S-013-contract.md",
            "AN-S-013",
            "active",
            1,
            container={"component": "C1"},
        )
        self._write(
            "AN-S-014-solution.md",
            "AN-S-014",
            "active",
            1,
            template="solution",
            container={"component": "C1"},
            tier=0,
        )
        self._write(
            "AN-S-016@1-draft-contract.md",
            "AN-S-016",
            "draft",
            1,
            container={"component": "C1"},
        )
        self._write(
            "AN-S-017-contract.md",
            "AN-S-017",
            "active",
            1,
            template="component_contract",
            container={"component": "C1"},
            structure_tier=1,
            body="## Guarantee\n\nA guarantee.\n",
        )
        self._write_remaining_contracts()

    def _write_remaining_contracts(self):
        self._write(
            "AN-S-018@1-draft-contract.md",
            "AN-S-018",
            "draft",
            1,
            template="component_contract",
            container={"component": "C1"},
            structure_tier=1,
        )
        self._write(
            "AN-S-019-child-contract.md",
            "AN-S-019",
            "active",
            1,
            template="component_contract",
            container={"component": "C2"},
            structure_tier=1,
        )
        self._write(
            "AN-S-020-wrong-tier-contract.md",
            "AN-S-020",
            "active",
            1,
            template="component_contract",
            container={"component": "C1"},
            structure_tier=0,
        )

    async def test_component_queries_use_declared_id_and_owned_spec_tiers(
        self,
    ):
        self._write_component_queries()
        async with (
            asyncio.timeout(25),
            stdio_client(
                StdioServerParameters(
                    command=sys.executable,
                    args=self.args,
                    env={"PYTHONPATH": str(MCP.parents[1])},
                )
            ) as streams,
            ClientSession(*streams) as client,
        ):
            await client.initialize()
            await self._check_component_templates(client)
            await self._check_component_rows(client)

    async def _check_component_templates(self, client):
        for template, selector, expected in (
            ("fetch_contracts", "tools", ["AN-S-011@1"]),
            ("fetch_solutions", "c1", ["AN-S-014@1"]),
            ("get_component_manifest", "C1", ["AN-S-011@1"]),
            ("get_component_purpose", " Tools ", ["AN-S-011@1"]),
            ("get_component_purpose", "Child", []),
        ):
            with self.subTest(template=template, selector=selector):
                result = await client.call_tool(
                    "query_template",
                    {
                        "template": template,
                        "component": selector,
                        "result_format": "json_matrix",
                    },
                )
                self.assertFalse(result.is_error, result.structured_content)
                self.assertEqual(
                    expected,
                    [row[0] for row in result.structured_content["rows"]],
                )

    async def _check_component_rows(self, client):
        result = await client.call_tool(
            "query_run",
            {
                "sql": "SELECT component_id, name, parent_component_id, "
                "layer, lens_whitelist, manifest_ref, purpose_refs "
                "FROM components "
                "WHERE component_id = 'C1'",
                "result_delivery": "inline",
            },
        )
        self.assertFalse(result.is_error, result.structured_content)
        self.assertEqual(
            [
                [
                    "C1",
                    "Tools",
                    "C0",
                    3,
                    ["SPEC"],
                    "AN-S-011@1",
                    ["AN-S-011@1"],
                ]
            ],
            result.structured_content["rows"],
        )
