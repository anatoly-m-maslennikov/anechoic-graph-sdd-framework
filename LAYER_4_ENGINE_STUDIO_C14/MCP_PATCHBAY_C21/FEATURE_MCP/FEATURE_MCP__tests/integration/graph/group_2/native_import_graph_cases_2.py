"""Exercise the Import Graph through the native Workbench routes."""

import asyncio
from contextlib import redirect_stderr
from dataclasses import replace
from io import StringIO

import httpx2
from starlette.applications import Starlette

from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import read_import_sources
from MCP_PATCHBAY_C21.FEATURE_MCP.gateway.gateway__shared import (
    routes as routes,
)


from ..group_1._native_graph_binding_cases import NativeGraphBindingCases


class ImportGraphCases2(NativeGraphBindingCases):
    async def _check_graph_schema(self, client, base, rows):
        schema = await client.post(f"{base}/schema", json={})
        self.assertEqual(schema.status_code, 200, schema.text)
        self.assertTrue(
            {
                "import_nodes",
                "module_imports",
                "import_edges",
                "package_imports",
            }
            <= set(schema.json()["tables"])
        )
        await self._check_import_edge_rows(rows)

        graph = """
            SELECT count(*) FROM GRAPH_TABLE (anechoic
            MATCH (s:ImportNode)-[e:Imports]->(d:ImportNode)
            COLUMNS (e.occurrence_key AS occurrence_key))
        """
        self.assertGreater((await rows(graph))[0][0], 0)
        self.assertTrue(await rows("SELECT * FROM relations LIMIT 1"))
        counts = "SELECT count(*) FROM package_imports"
        return graph, counts

    async def _check_import_edge_rows(self, rows):
        self.assertEqual(
            await rows("""
            SELECT DISTINCT s.kind, d.kind, e.derived
            FROM import_edges e JOIN import_nodes s ON s.node_key = e.source_key
            JOIN import_nodes d ON d.node_key = e.target_key
            JOIN module_imports i USING (occurrence_key)
            WHERE i.written_specifier = 'dep.helper' AND i.line = 1
            ORDER BY ALL
        """),
            [
                ["module", "module", False],
                ["module", "package", True],
                ["package", "module", True],
                ["package", "package", True],
            ],
        )
        self.assertEqual(
            await rows("""
            SELECT written_specifier, line, resolution_status FROM module_imports
            WHERE written_specifier IN ('dep.helper', 'missing', '.', 'declared') ORDER BY line
        """),
            [
                ["dep.helper", 1, "internal"],
                ["missing", 3, "unresolved"],
                ["dep.helper", 4, "internal"],
                [".", 6, "internal"],
                ["declared", 7, "external"],
            ],
        )
        self.assertEqual(
            await rows("""
            SELECT relative_path, scan_status FROM import_nodes
            WHERE relative_path IN ('src/generated/ignored.py', 'src/unsupported.go')
        """),
            [["src/unsupported.go", "unsupported"]],
        )

    async def _check_graph_updates(self, gateway, rows, graph):
        owner = gateway._native_query
        with owner._owner()._lock:
            importer = read_import_sources(owner._owner()._connection)[
                "src/app/main.py"
            ]
        target = self._source("src/missing.py", "")
        sql = (
            'SELECT resolution_status FRO'
            'M module_imports WHERE writt'
            "en_specifier = 'missing'"
        )
        async with asyncio.timeout(6):
            while await rows(sql) != [["internal"]]:
                await asyncio.sleep(0.03)
        target.rename(target.with_name("moved.py"))
        async with asyncio.timeout(6):
            while await rows(sql) != [["unresolved"]]:
                await asyncio.sleep(0.03)
        with owner._owner()._lock:
            self.assertEqual(
                importer,
                read_import_sources(owner._owner()._connection)[
                    "src/app/main.py"
                ],
            )

        self._source("new_root/added.py", "import os\n")
        async with asyncio.timeout(6):
            while not await rows(
                (
                    'SELECT 1 FROM import_nodes W'
                    "HERE relative_path = 'new_ro"
                    "ot/added.py'"
                )
            ):
                await asyncio.sleep(0.03)

        self._write(
            "001_TICKETS/TASKS/AN-T-010-TASK--external.md",
            "AN-T-010",
            "active",
            1,
        )
        async with asyncio.timeout(6):
            while not await rows(
                "SELECT 1 FROM atoms WHERE reference = 'AN-T-010'"
            ):
                await asyncio.sleep(0.03)
        self.assertGreater((await rows(graph))[0][0], 0)

        await self._check_relation_type_refresh(owner, rows, graph)

    async def _check_relation_type_refresh(self, owner, rows, graph):
        owner._inputs = replace(
            owner._inputs,
            relation_types=owner._inputs.relation_types | {"TEST_LINK"},
        )
        owner._refresh_after_write(owner._owner())
        self.assertGreater((await rows(graph))[0][0], 0)

    async def test_queries_four_relations_and_notices_target_changes(self):
        self._source("src/app/__init__.py", "")
        self._source("src/app/util.py", "")
        self._source("src/dep/__init__.py", "")
        self._source("src/dep/helper.py", "import app.main\n")
        self._source(
            "src/app/main.py",
            "import dep.helper\nimport dep\nimport missing\nimport dep.helper\n"
            "if False:\n    from . import util as helper\nimport declared\n",
        )
        self._source(
            "pyproject.toml",
            '[dependency-groups]\nworkbench = ["declared>=1"]\n',
        )
        self._source("src/unsupported.go", "package example\n")
        self._source("src/generated/ignored.py", "import dep\n")
        self._source("src/invalid.py", "import\n")
        stderr = StringIO()
        with redirect_stderr(stderr):
            gateway = await self._gateway()
        self.assertIn("src/invalid.py", stderr.getvalue())
        app = Starlette(routes=routes(gateway))
        async with httpx2.AsyncClient(
            transport=httpx2.ASGITransport(app=app),
            base_url="http://127.0.0.1:18093",
        ) as client:
            base = "/anechoic/Anechoic/api"

            async def rows(sql):
                response = await client.post(
                    f"{base}/run",
                    json={"sql": sql, "result_delivery": "inline"},
                )
                self.assertEqual(response.status_code, 200, response.text)
                return response.json()["rows"]

            graph, counts = await self._check_graph_schema(client, base, rows)

            await self._check_workbench_counts(client, base, rows, counts)

            await self._check_graph_updates(gateway, rows, graph)

    async def _check_workbench_counts(self, client, base, rows, counts):
        async def workbench(operation, arguments):
            response = await client.post(
                f"{base}/interface",
                json={
                    "operation": operation,
                    "arguments": arguments,
                },
            )
            self.assertEqual(response.status_code, 200, response.text)
            return response.json()

        workspace = await workbench(
            "workspace_open", {"session_id": "imports"}
        )
        view = {
            "workspace_id": workspace["workspace_id"],
            "view_id": workspace["active_view_id"],
        }
        await workbench(
            "view_update", view | {"sql": counts, "expected_revision": 0}
        )
        await workbench("view_run", view)
        result = await workbench(
            "view_fetch", view | {"result_delivery": "inline"}
        )
        self.assertEqual(result["rows"], await rows(counts))
