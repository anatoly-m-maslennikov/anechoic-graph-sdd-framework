"""Source filtering and native projection contracts for Import Graph."""

import asyncio

from mcp import types


class _MiscImportGraphCases:
    async def _package_rows(self, owner, sql):
        response = await owner.call(
            None,
            types.CallToolRequestParams(
                name="query_run",
                arguments={"sql": sql, "result_delivery": "inline"},
            ),
        )
        self.assertFalse(response.is_error, response.structured_content)
        return response.structured_content["rows"]

    async def _native_rows(self, gateway, sql):
        response = await gateway.call(
            None,
            types.CallToolRequestParams(
                name="query_run",
                arguments={"sql": sql, "result_delivery": "inline"},
            ),
        )
        self.assertFalse(response.is_error, response.structured_content)
        return response.structured_content["rows"]

    async def test_direct_packages_follow_unsupported_source_removal(self):
        source = self._source("src/tree/nested/leaf/main.go", "package leaf\n")
        self._source("src/tree/assets/image.txt", "asset\n")
        self._source("src/tree/tree__tests/assets/input.txt", "asset\n")
        self._source("src/tree/.hidden/hidden.go", "package hidden\n")
        self._source("src/tree/generated/generated.go", "package generated\n")
        self._source("src/tree/ignored/ignored.go", "package ignored\n")
        self._source(".gitignore", "src/tree/ignored/\n")
        (self.root / "src/tree/empty").mkdir()
        gateway = await self._gateway()

        packages = """
            SELECT n.node_key, count(a.relative_path)
            FROM import_nodes n LEFT JOIN package_audit a ON a.relative_path = n.relative_path
            WHERE n.kind = 'package' AND n.relative_path LIKE 'src/tree%'
            GROUP BY n.node_key ORDER BY n.node_key
        """
        expected = [["package:local:src/tree/nested/leaf", 1]]
        self.assertEqual(expected, await self._package_rows(gateway, packages))
        self.assertEqual(
            [["src/tree/nested/leaf/main.go", "unsupported"]],
            await self._package_rows(
                gateway,
                """
            SELECT relative_path, scan_status FROM import_nodes
            WHERE kind = 'module' AND relative_path LIKE 'src/tree%' ORDER BY relative_path
        """,
            ),
        )
        source.unlink()
        async with asyncio.timeout(6):
            while await self._package_rows(gateway, packages):
                await asyncio.sleep(0.03)
        await gateway.close()
        reopened = await self._gateway()
        self.assertEqual([], await self._package_rows(reopened, packages))
        source.write_text("package leaf\n", encoding="utf-8")
        async with asyncio.timeout(6):
            while await self._package_rows(reopened, packages) != expected:
                await asyncio.sleep(0.03)

    async def _assert_native_projection(self, gateway):
        refs = await self._native_rows(
            gateway,
            "SELECT stable_ref, exact_ref FROM native_references "
            "WHERE exact_ref LIKE 'AN-T-009@%' ORDER BY exact_ref",
        )
        self.assertEqual(
            [
                [None, "AN-T-009@1"],
                ["AN-T-009", "AN-T-009@2"],
                [None, "AN-T-009@3-draft"],
            ],
            refs,
        )
        facts = await self._native_rows(
            gateway,
            "SELECT source_kind, source_ref, target_kind, target_ref, relation_type, derived "
            "FROM relations WHERE (source_ref = 'AN-T-010' AND target_ref = 'AN-T-009') "
            "OR (source_ref = 'AN-T-009' AND target_ref = 'AN-T-010') "
            "OR (source_kind = 'Component' AND source_ref = 'C0' "
            "AND target_ref = 'AN-T-009')",
        )
        self.assertIn(
            ["Atom", "AN-T-010", "Atom", "AN-T-009", "CONTAINED_BY", False],
            facts,
        )
        self.assertIn(
            ["Atom", "AN-T-009", "Atom", "AN-T-010", "CONTAINS", True], facts
        )
        self.assertIn(
            ["Component", "C0", "Atom", "AN-T-009", "CONTAINS", True], facts
        )
        self.assertEqual(
            [], await self._native_rows(gateway, "SELECT * FROM scope_units")
        )

    async def test_native_projection_revision_and_containment_facts_through_mcp(
        self,
    ):
        self._write(
            "001_TICKETS/ASSETS/AN-T-010-ASSET--child.md",
            "AN-T-010",
            "active",
            1,
            container={"atom": "AN-T-009"},
        )
        gateway = await self._gateway(enabled=False)
        await self._assert_native_projection(gateway)
