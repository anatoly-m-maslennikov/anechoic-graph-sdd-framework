"""Exercise the Import Graph through the native Workbench routes."""

import asyncio
from contextlib import redirect_stderr
from io import StringIO
import json
from pathlib import Path
from unittest.mock import patch

import duckdb
import httpx2
from mcp import types
from starlette.applications import Starlette

from KERNEL_MIXER_C59.import_cache import read_import_sources
from KERNEL_MIXER_C59.import_tables import publish_imports
from MCP_PATCHBAY_C21.FEATURE_MCP.workbench_web import routes


_INVERSE_TEST_COMPONENT = """
            FROM GRAPH_TABLE (anechoic
                MATCH (component:Reference)-[edge:COMPONENT_IS_TESTED_BY]->(test:ImportNode)
                COLUMNS (component.ref AS component, test.relative_path AS test_path))
        """

_TESTS_COMPONENT = """
            FROM GRAPH_TABLE (anechoic
                MATCH (test:ImportNode)-[edge:TESTS_COMPONENT]->(component:Reference)
                COLUMNS (component.kind AS kind, component.ref AS ref))
        """

class ImportGraphCases4:
    async def test_component_test_package_and_unmarked_package(self):
        self._source("src/UNIT_C1/UNIT_C1__tests/test_e2e.py", "pass\n")
        implementation = self._source("src/UNIT_C1/service_pkg1/main.py", "pass\n")
        self._source("src/UNIT_C1/service_pkg1/service_pkg1__tests/test_main.py", "pass\n")
        self._source("src/group/group__tests/test_e2e.py", "pass\n")
        structure = self._source(".anechoic_tmp/structure.json", json.dumps({
            "model_sha256": "fixture", "project": {"ref": "AN-S-001@1", "sha256": "fixture"},
            "components": {"C1": {"parent": "C00", "ref": "AN-S-006@1", "sha256": "fixture",
                                  "source_path": "AN-S-006-SPEC-COMPONENT_MANIFEST--unit.md",
                                  "fields": {"name": "Unit"}}},
        }))
        gateway = await self._gateway(structure_snapshot=structure)

        async def rows(sql):
            response = await gateway.call(None, types.CallToolRequestParams(name="query_run", arguments={
                "sql": sql, "result_delivery": "inline",
            }))
            self.assertFalse(response.is_error, response.structured_content)
            return response.structured_content["rows"]

        self.assertEqual([["src/UNIT_C1/UNIT_C1__tests"], ["src/UNIT_C1/service_pkg1"],
                          ["src/UNIT_C1/service_pkg1/service_pkg1__tests"]],
                         await rows("SELECT relative_path FROM import_nodes WHERE kind = 'package' "
                                    "AND relative_path LIKE 'src/UNIT_C1%' ORDER BY relative_path"))
        self.assertEqual([
            ["package:local:src/UNIT_C1/UNIT_C1__tests", "C1"],
            ["package:local:src/UNIT_C1/service_pkg1/service_pkg1__tests",
             "package:local:src/UNIT_C1/service_pkg1"],
        ], await rows("SELECT source_key, target_key FROM test_edges ORDER BY source_key"))
        self.assertEqual([["Component", "C1"]], await rows(_TESTS_COMPONENT))
        inverse = _INVERSE_TEST_COMPONENT
        expected = [["C1", "src/UNIT_C1/UNIT_C1__tests"]]
        self.assertEqual(expected, await rows(inverse))
        issues = "SELECT relative_path, test_issue FROM package_audit WHERE test_issue IS NOT NULL ORDER BY relative_path"
        orphan = ["src/group/group__tests", "missing_test_target"]
        self.assertEqual([["src/UNIT_C1/service_pkg1", "missing_visibility_marker"], orphan], await rows(issues))
        implementation.rename(implementation.with_name("main__shared.py"))
        async with asyncio.timeout(6):
            while await rows(issues) != [orphan]:
                await asyncio.sleep(.03)
        await gateway.close()
        gateway = await self._gateway(structure_snapshot=structure)
        self.assertEqual(expected, await rows(inverse))
        self.assertEqual([orphan], await rows(issues))


    async def test_import_publication_failure_reports_stderr_once(self):
        self._source("src/from_source.py", "import to_source\n")
        self._source("src/to_source.py", "")
        gateway = await self._gateway()
        stderr = StringIO()
        with redirect_stderr(stderr), patch("KERNEL_MIXER_C59.realization_projection.replace_imports", side_effect=ValueError("fixture write")) as write:
            self._source("src/new_source.py", "")
            async with asyncio.timeout(6):
                while "fixture write" not in stderr.getvalue():
                    await asyncio.sleep(.03)
            self.assertEqual(write.call_count, 1)
        store = gateway._native_query._owner()
        duplicate = ("duplicate", "module", "python", "new.py", "ok", None)
        with self.assertRaises(duckdb.ConstraintException):
            publish_imports(store, [duplicate, duplicate], [], [])
        with store._lock:
            self.assertEqual(store._connection.execute(
                "SELECT relative_path FROM import_nodes ORDER BY relative_path",
            ).fetchall(), [("src",), ("src/from_source.py",), ("src/to_source.py",)])


    async def _check_disk_rebuild(self, gateway, store, post, view_call, view, first, independent, expected, test_directory):
        moved = test_directory.parent.parent / test_directory.name
        test_directory.rename(moved)
        rebuilt = await post("rebuild", {"target": "test_edges"})
        second = rebuilt["result_ids"][first]
        self.assertNotEqual(first, second)
        self.assertNotIn(independent, rebuilt["result_ids"])
        fetched = await view_call("view_fetch", view | {"result_delivery": "inline"})
        self.assertEqual((second, []), (fetched["query_id"], fetched["rows"]))
        self.assertTrue(store._results[second].pinned)
        stderr = StringIO()
        with redirect_stderr(stderr), patch.object(store, "prepare_result_rebuild",
                                                   side_effect=ValueError("fixture rebuild failure")):
            await post("rebuild", {"target": "test_edges"}, 400)
        self.assertIn("fixture rebuild failure", stderr.getvalue())
        fetched = await view_call("view_fetch", view | {"result_delivery": "inline"})
        self.assertEqual((second, []), (fetched["query_id"], fetched["rows"]))
        moved.rename(test_directory)
        mcp = await gateway.call(None, types.CallToolRequestParams(
            name="query_rebuild", arguments={"target": "all"},
        ))
        self.assertFalse(mcp.is_error, mcp.structured_content)
        third = mcp.structured_content["result_ids"][second]
        fetched = await view_call("view_fetch", view | {"result_delivery": "inline"})
        self.assertEqual((third, expected), (fetched["query_id"], fetched["rows"]))
        single = await post("rebuild", {"target": f"workbench_results.query_{third}"})
        self.assertIn(third, single["result_ids"])


    async def _check_disk_http(self, gateway, store, database, test_directory, sql):
        app = Starlette(routes=routes(gateway))
        async with httpx2.AsyncClient(transport=httpx2.ASGITransport(app=app),
                                     base_url="http://127.0.0.1:18093") as client:
            base = "/anechoic/Anechoic/api"

            async def post(operation, arguments, status=200):
                response = await client.post(f"{base}/{operation}", json=arguments)
                self.assertEqual(status, response.status_code, response.text)
                return response.json()

            async def view_call(operation, arguments):
                return await post("interface", {"operation": operation, "arguments": arguments})

            workspace = await view_call("workspace_open", {"session_id": "realization"})
            view = {"workspace_id": workspace["workspace_id"], "view_id": workspace["active_view_id"]}
            await view_call("view_update", view | {"sql": sql, "expected_revision": 0})
            first = (await view_call("view_run", view))["query_id"]
            independent = (await post("run", {"sql": "SELECT 7", "result_delivery": "inline"}))["query_id"]
            expected = [["src/app", "src/app/app__tests", "Test Package"]]
            self.assertEqual(expected, (await view_call("view_fetch", view | {"result_delivery": "inline"}))["rows"])
            with store._lock:
                database_file = store._connection.execute(
                    "SELECT path FROM duckdb_databases() WHERE NOT internal"
                ).fetchone()[0]
                self.assertEqual(database.resolve().as_posix(), database_file)
            stderr = StringIO()
            with redirect_stderr(stderr):
                rejected = await post("rebuild", {"target": "unknown"}, 400)
            self.assertIn("Unknown Workbench rebuild target", rejected["error"])
            self.assertIn("Unknown Workbench rebuild target", stderr.getvalue())
            with redirect_stderr(StringIO()) as errors:
                response = await gateway.call(None, types.CallToolRequestParams(
                    name="query_rebuild", arguments={"target": "missing"},
                ))
            self.assertTrue(response.is_error)
            self.assertIn("Unknown Workbench rebuild target", str(response.structured_content))
            self.assertIn("Unknown Workbench rebuild target", errors.getvalue())
            await self._check_disk_rebuild(gateway, store, post, view_call, view, first, independent, expected, test_directory)


    async def test_disk_reopen_rebuild_and_test_relations(self):
        self._source("src/app/main.py", "import dep.helper\n")
        self._source("src/dep/helper.py", "")
        test_directory = self._source("src/app/app__tests/test_app.py", "pass\n").parent
        gateway = await self._gateway()
        owner = gateway._native_query
        store = owner._owner()
        database = self.root / ".anechoic_runtime/workbench/projection.duckdb"
        self.assertTrue(database.is_file())
        sql = """
            SELECT parent.relative_path, test.relative_path, test.package_type
            FROM tested_by_edges e JOIN import_nodes parent ON parent.node_key = e.source_key
            JOIN import_nodes test ON test.node_key = e.target_key
        """
        await self._check_disk_http(gateway, store, database, test_directory, sql)

        await gateway.close()
        self._source("src/dep/helper.py", "import app.main\n")
        from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_IMPORT_GRAPH_C61.source import _parse
        with patch("IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_IMPORT_GRAPH_C61.source._parse", wraps=_parse) as parse:
            reopened = await self._gateway()
            self.assertEqual(["src/dep/helper.py"], [call.args[0] for call in parse.call_args_list])
        reopened_store = reopened._native_query._owner()
        self.assertFalse(reopened_store._results)
        with reopened_store._lock:
            self.assertEqual([(2,)], reopened_store._connection.execute("SELECT count(*) FROM module_imports").fetchall())
            self.assertEqual([], reopened_store._connection.execute(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'workbench_results'"
            ).fetchall())
        await reopened.close()
        disabled = await self._gateway(enabled=False)
        self.assertNotIn("test_edges", disabled._native_query.schema()["tables"])
        disabled_store = disabled._native_query._owner()
        with disabled_store._lock:
            self.assertFalse(read_import_sources(disabled_store._connection))


    async def test_read_issue_is_queryable_and_clears_on_the_next_scan(self):
        source = self._source("src/app/main.py", "import os\n")
        read_bytes = Path.read_bytes

        def read(path):
            if path == source:
                raise PermissionError("fixture read denied")
            return read_bytes(path)

        with patch.object(Path, "read_bytes", read), redirect_stderr(StringIO()) as errors:
            gateway = await self._gateway()
        self.assertIn("fixture read denied", errors.getvalue())
        sql = "SELECT relative_path, error_message FROM import_read_issues"
        owner = gateway._native_query
        self.assertIn("import_read_issues", owner.schema()["tables"])
        self.assertEqual([["src/app/main.py", "fixture read denied"]],
                         owner.run(sql, result_delivery="inline")["rows"])
        owner.rebuild("import_read_issues")
        self.assertEqual([], owner.run(sql, result_delivery="inline")["rows"])


    async def test_graph_rebuild_failure_disables_queries_at_the_public_boundary(self):
        self._source("src/main.py", "")
        gateway = await self._gateway()
        owner = gateway._native_query
        store = owner._owner()
        async with httpx2.AsyncClient(transport=httpx2.ASGITransport(app=Starlette(routes=routes(gateway))),
                                     base_url="http://127.0.0.1:18093") as client:
            stderr = StringIO()
            with redirect_stderr(stderr), patch(
                "KERNEL_MIXER_C59.query_store.insert_rows",
                side_effect=OSError("fixture atom insert blocked"),
            ):
                failure = await client.post("/anechoic/Anechoic/api/rebuild", json={"target": "atoms"})
            self.assertEqual(400, failure.status_code)
            self.assertIn("restart required", failure.json()["error"])
            self.assertIn("fixture atom insert blocked", stderr.getvalue())
            response = await gateway.call(None, types.CallToolRequestParams(
                name="query_run", arguments={"sql": "SELECT count(*) FROM atoms"},
            ))
            self.assertTrue(response.is_error)
            self.assertIn("restart required", str(response.structured_content))
        with store._lock:
            self.assertGreater(store._connection.execute("SELECT count(*) FROM atoms").fetchone()[0], 0)

