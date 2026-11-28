"""Structure and boundary contracts for the native Import Graph."""

import asyncio
import json

from mcp import types


def _boundary_carrier(ref, fields, **relations):
    return {
        "ref": ref,
        "sha256": "fixture",
        "source_path": "manifest.md",
        "fields": fields,
        **relations,
    }


def _boundary_packages():
    return {
        "CS1": _boundary_carrier(
            "AN-S-012@1",
            {"boundaries": {"state": "pure"}},
            component="C2",
        ),
        "CS2": _boundary_carrier(
            "AN-S-013@1",
            {"boundaries": {"state": "local"}},
            component="C2",
        ),
    }


def _boundary_snapshot():
    left = {
        "name": "Left",
        "layer": 2,
        "boundaries": {
            "code": {"imports": ["RIGHT_C2.api.exposed"]},
            "state": "local",
            "io": {"client": [{"component": "C2", "interface": "run"}]},
        },
    }
    right = {
        "name": "Right",
        "layer": 1,
        "boundaries": {
            "code": {"exports": {"api.exposed": None}},
            "io": {
                "server": {
                    "run": {
                        "transport": "cli",
                        "path": "src/RIGHT_C2/api.py",
                    }
                }
            },
        },
    }
    snapshot = {
        "model_sha256": "fixture",
        "project": {"ref": "AN-S-001@1", "sha256": "fixture"},
        "components": {
            "C1": _boundary_carrier("AN-S-010@1", left, parent="C00"),
            "C2": _boundary_carrier("AN-S-011@1", right, parent="C00"),
        },
        "packages": _boundary_packages(),
    }
    return right, snapshot


class _BoundaryCases:
    async def _prepare_boundaries(self):
        self._source("src/_bypass__shared.py", "")
        self._source("src/LEFT_C1/_package__shared.py", "")
        self._source("src/RIGHT_C2/_package__shared.py", "")
        self._source(
            "src/LEFT_C1/client.py",
            "from RIGHT_C2.api import exposed, hidden\n",
        )
        self._source("src/RIGHT_C2/api.py", "exposed = 1\nhidden = 2\n")
        self._source("src/RIGHT_C2/service_CS1/main__shared.py", "pass\n")

        right, snapshot = _boundary_snapshot()
        structure = self._source(
            ".anechoic_tmp/generation/structure.json", json.dumps(snapshot)
        )
        gateway = await self._gateway(structure_snapshot=structure)

        return right, snapshot, structure, gateway

    async def _query_boundary_rows(self, gateway, sql):
        result = await gateway.call(
            None,
            types.CallToolRequestParams(
                name="query_run",
                arguments={"sql": sql, "result_delivery": "inline"},
            ),
        )
        self.assertFalse(result.is_error, result.structured_content)
        return result.structured_content["rows"]

    async def _assert_boundary_tables(self, gateway):
        schema = await gateway.call(
            None,
            types.CallToolRequestParams(name="query_schema", arguments={}),
        )
        self.assertTrue(
            {"boundary_declarations", "code_access_findings"}
            <= schema.structured_content["tables"].keys()
        )

    async def _assert_declared_boundaries(self, gateway):
        await self._assert_boundary_tables(gateway)
        declarations = await self._query_boundary_rows(
            gateway,
            """
            SELECT owner_id, node_key, layer, json_extract_string(state, '$'),
                   json_extract_string(io, '$.client[0].interface'),
                   json_extract_string(io, '$.server.run.transport')
            FROM boundary_declarations ORDER BY owner_id
        """,
        )
        self.assertEqual(
            [
                ["C1", "C1", 2, "local", "run", None],
                ["C2", "C2", 1, None, None, "cli"],
                [
                    "CS1",
                    "package:local:src/RIGHT_C2/service_CS1",
                    None,
                    "pure",
                    None,
                    None,
                ],
                ["CS2", None, None, "local", None, None],
            ],
            declarations,
        )
        findings_sql = (
            'SELECT written_specifier, st'
            'atus, reason FROM code_acces'
            's_findings ORDER BY written_'
            'specifier'
        )
        self.assertEqual(
            [
                [
                    "from RIGHT_C2.api import exposed",
                    "declared_bypass",
                    "exact import and export declarations",
                ],
                [
                    "from RIGHT_C2.api import hidden",
                    "denied",
                    "code access rule",
                ],
            ],
            await self._query_boundary_rows(gateway, findings_sql),
        )
        return findings_sql

    async def _assert_layer_reordering(
        self, right, snapshot, structure, gateway, findings_sql
    ):
        right["layer"] = 3
        pending = self._source(
            ".anechoic_tmp/generation/structure.pending", json.dumps(snapshot)
        )
        pending.replace(structure)
        expected = [
            [
                f"from RIGHT_C2.api import {name}",
                "denied",
                "sibling layer order",
            ]
            for name in ("exposed", "hidden")
        ]
        async with asyncio.timeout(6):
            while (
                await self._query_boundary_rows(gateway, findings_sql)
                != expected
            ):
                await asyncio.sleep(0.03)
        rebuild = await gateway.call(
            None,
            types.CallToolRequestParams(
                name="query_rebuild",
                arguments={"target": "boundary_declarations"},
            ),
        )
        self.assertFalse(rebuild.is_error, rebuild.structured_content)
        self.assertEqual(
            expected, await self._query_boundary_rows(gateway, findings_sql)
        )
        await gateway.close()

    async def _assert_disabled_boundary_schema(self, structure):
        disabled = await self._gateway(
            enabled=False, structure_snapshot=structure
        )
        schema = await disabled.call(
            None,
            types.CallToolRequestParams(name="query_schema", arguments={}),
        )
        self.assertTrue(
            {"boundary_declarations", "code_access_findings"}.isdisjoint(
                schema.structured_content["tables"]
            )
        )

    async def test_boundaries_follow_structure_and_named_imports(self):
        right, snapshot, structure, gateway = await self._prepare_boundaries()
        findings_sql = await self._assert_declared_boundaries(gateway)
        await self._assert_layer_reordering(
            right, snapshot, structure, gateway, findings_sql
        )
        await self._assert_disabled_boundary_schema(structure)
