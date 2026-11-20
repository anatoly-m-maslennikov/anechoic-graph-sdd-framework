"""Exercise the opted-in Import Graph through the native Workbench routes."""

import asyncio
from contextlib import redirect_stderr
from dataclasses import replace
from io import StringIO
import json
from pathlib import Path
import subprocess
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import duckdb
import httpx2
from mcp import types
from starlette.applications import Starlette
from watchdog.observers.polling import PollingObserver

import test_native_query_stdio as fixture
from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.import_cache import read_import_sources
from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.import_tables import publish_imports
from native_query import create_native_gateway
from workbench_web import routes


class NativeImportGraphTests(unittest.IsolatedAsyncioTestCase):
    _write = fixture.NativeQueryStdioTests._write

    def setUp(self):
        fixture.NativeQueryStdioTests.setUp(self)
        # The full suite places temporary Projects inside its ignored Git scratch tree.
        subprocess.run(["git", "init", "--quiet", str(self.root)], check=True)

    def _source(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    async def _gateway(self, *, enabled=True, structure_snapshot=None):
        inputs = fixture._native_inputs()

        def validate(fields, component):
            manifest = inputs.validate_manifest(fields, component)
            workbench = {"import_graph": {"python_roots": ["src"]}} if enabled else {}
            return SimpleNamespace(name=manifest.name, prefix=manifest.prefix,
                                   parameters={"runtime": {"workbench": workbench}})

        gateway = create_native_gateway(self.root, fixture.CONTROL, replace(inputs, validate_manifest=validate))
        if structure_snapshot is not None:
            selected = replace(gateway.selection, structure_snapshot=structure_snapshot)
            gateway.selection = gateway._native_query.selection = selected
        with patch("APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.source_watcher.NativeObserver",
                   lambda: PollingObserver(timeout=.05)):
            await gateway.initialize()
        self.addAsyncCleanup(gateway.close)
        return gateway

    async def test_queries_four_relations_and_notices_target_changes(self):
        self._source("src/app/__init__.py", "")
        self._source("src/app/util.py", "")
        self._source("src/dep/__init__.py", "")
        self._source("src/dep/helper.py", "import app.main\n")
        self._source("src/app/main.py", "import dep.helper\nimport dep\nimport missing\nimport dep.helper\n"
                     "if False:\n    from . import util as helper\nimport declared\n")
        self._source("pyproject.toml", '[dependency-groups]\nworkbench = ["declared>=1"]\n')
        self._source("src/unsupported.ts", "import './app';\n")
        self._source("src/generated/ignored.py", "import dep\n")
        self._source("src/invalid.py", "import\n")
        stderr = StringIO()
        with redirect_stderr(stderr):
            gateway = await self._gateway()
        self.assertIn("src/invalid.py", stderr.getvalue())
        app = Starlette(routes=routes(gateway))
        async with httpx2.AsyncClient(transport=httpx2.ASGITransport(app=app),
                                     base_url="http://127.0.0.1:18093") as client:
            base = "/anechoic/Anechoic/api"

            async def rows(sql):
                response = await client.post(f"{base}/run", json={"sql": sql, "result_delivery": "inline"})
                self.assertEqual(response.status_code, 200, response.text)
                return response.json()["rows"]

            schema = await client.post(f"{base}/schema", json={})
            self.assertEqual(schema.status_code, 200, schema.text)
            self.assertTrue({"import_nodes", "module_imports", "import_edges", "package_imports"}
                            <= set(schema.json()["tables"]))
            self.assertEqual(await rows("""
                SELECT DISTINCT s.kind, d.kind, e.derived
                FROM import_edges e JOIN import_nodes s ON s.node_key = e.source_key
                JOIN import_nodes d ON d.node_key = e.target_key
                JOIN module_imports i USING (occurrence_key)
                WHERE i.written_specifier = 'dep.helper' AND i.line = 1
                ORDER BY ALL
            """), [["module", "module", False], ["module", "package", True],
                   ["package", "module", True], ["package", "package", True]])
            self.assertEqual(await rows("""
                SELECT written_specifier, line, resolution_status FROM module_imports
                WHERE written_specifier IN ('dep.helper', 'missing', '.', 'declared') ORDER BY line
            """), [["dep.helper", 1, "internal"], ["missing", 3, "unresolved"],
                   ["dep.helper", 4, "internal"], [".", 6, "internal"], ["declared", 7, "external"]])
            self.assertEqual(await rows("""
                SELECT relative_path, scan_status FROM import_nodes
                WHERE relative_path IN ('src/generated/ignored.py', 'src/unsupported.ts')
            """), [["src/unsupported.ts", "unsupported"]])
            graph = """
                SELECT count(*) FROM GRAPH_TABLE (anechoic
                MATCH (s:ImportNode)-[e:Imports]->(d:ImportNode)
                COLUMNS (e.occurrence_key AS occurrence_key))
            """
            self.assertGreater((await rows(graph))[0][0], 0)
            self.assertTrue(await rows("SELECT * FROM relations LIMIT 1"))
            counts = "SELECT count(*) FROM package_imports"

            async def workbench(operation, arguments):
                response = await client.post(f"{base}/interface", json={
                    "operation": operation, "arguments": arguments,
                })
                self.assertEqual(response.status_code, 200, response.text)
                return response.json()

            workspace = await workbench("workspace_open", {"session_id": "imports"})
            view = {"workspace_id": workspace["workspace_id"], "view_id": workspace["active_view_id"]}
            await workbench("view_update", view | {"sql": counts, "expected_revision": 0})
            await workbench("view_run", view)
            result = await workbench("view_fetch", view | {"result_delivery": "inline"})
            self.assertEqual(result["rows"], await rows(counts))

            owner = gateway._native_query
            with owner._owner()._lock:
                importer = read_import_sources(owner._owner()._connection)["src/app/main.py"]
            target = self._source("src/missing.py", "")
            sql = "SELECT resolution_status FROM module_imports WHERE written_specifier = 'missing'"
            async with asyncio.timeout(6):
                while await rows(sql) != [["internal"]]:
                    await asyncio.sleep(.03)
            target.rename(target.with_name("moved.py"))
            async with asyncio.timeout(6):
                while await rows(sql) != [["unresolved"]]:
                    await asyncio.sleep(.03)
            with owner._owner()._lock:
                self.assertEqual(importer, read_import_sources(owner._owner()._connection)["src/app/main.py"])

            self._source("new_root/added.py", "import os\n")
            async with asyncio.timeout(6):
                while not await rows("SELECT 1 FROM import_nodes WHERE relative_path = 'new_root/added.py'"):
                    await asyncio.sleep(.03)

            owner._inputs = replace(owner._inputs, relation_types=owner._inputs.relation_types | {"TEST_LINK"})
            owner._refresh_after_write(owner._owner())
            self.assertGreater((await rows(graph))[0][0], 0)

    async def test_spec_bindings_are_indexed_and_follow_sidecar_changes(self):
        self._source("src/app/main.py", "pass\n")
        sidecar = self._source("src/app/app__spec_bind.yaml", "implements:\n  - AN-S-001@1\n")
        self._source("src/app/main.py.spec_trace.md", "## Implements\n- CA-R-10@2\n")
        gateway = await self._gateway()
        app = Starlette(routes=routes(gateway))
        async with httpx2.AsyncClient(transport=httpx2.ASGITransport(app=app),
                                     base_url="http://127.0.0.1:18093") as client:
            base = "/anechoic/Anechoic/api"
            schema = await client.post(f"{base}/schema", json={})
            self.assertEqual(schema.status_code, 200, schema.text)
            self.assertIn("implementation_rmedo", schema.json()["tables"])

            async def pins():
                result = await client.post(f"{base}/run", json={
                    "sql": "SELECT owner_path, entry_kind, atom_id, version FROM implementation_rmedo ORDER BY 1",
                    "result_delivery": "inline",
                })
                self.assertEqual(result.status_code, 200, result.text)
                return result.json()["rows"]

            module = ["src/app/main.py", "implements", "CA-R-10", 2]
            self.assertEqual(await pins(), [["src/app", "implements", "AN-S-001", 1], module])
            sidecar.write_text("applies:\n  - AN-S-007@3\n", encoding="utf-8")
            async with asyncio.timeout(6):
                while await pins() != [["src/app", "applies", "AN-S-007", 3], module]:
                    await asyncio.sleep(.03)
            sidecar.unlink()
            async with asyncio.timeout(6):
                while await pins() != [module]:
                    await asyncio.sleep(.03)

    async def test_component_ratios_follow_formal_test_assets(self):
        self._source("src/UNIT_C1/main.py", "pass\npass\n")
        self._source("src/UNIT_C1/tests/test_legacy.py", "pass\n")
        self._source("src/UNIT_C1/UNIT_C1__tests/test_main.py", "pass\n")
        asset = self._source("src/UNIT_C1/UNIT_C1__tests/assets/input.txt", "x\n")
        body = "## Summary\n\nDescribe C1.\n"
        spec = self._source(f"{fixture.CONTROL}/UNIT_C1/AN-S-007-SPEC--description.md", (
            "---\nidentity: {atom_id: AN-S-007}\ncontext: {container: {component: C1}, lens: SPEC}\n"
            "state: {status: active, version: 1}\n---\n" + body
        ))
        structure = self._source(".anechoic_tmp/structure.json", json.dumps({
            "model_sha256": "fixture", "project": {"ref": "AN-S-001@1", "sha256": "fixture"},
            "components": {"C1": {"parent": "C00", "ref": "AN-S-006@1", "sha256": "fixture",
                                  "source_path": "AN-S-006-SPEC-COMPONENT_MANIFEST--unit.md",
                                  "fields": {"name": "Unit"}}},
        }))
        gateway = await self._gateway(structure_snapshot=structure)

        async def ratios():
            response = await gateway.call(None, types.CallToolRequestParams(name="query_run", arguments={
                "sql": "SELECT denominator, realization_kb, realization_lines, spec_full_kb_ratio, "
                       "spec_body_kb_ratio, spec_body_lines_ratio FROM component_metrics "
                       "WHERE component_id = 'C1' ORDER BY denominator", "result_delivery": "inline",
            }))
            self.assertFalse(response.is_error, response.structured_content)
            return response.structured_content["rows"]

        populations = {"implementation": (10, 2), "implementation_and_tests": (17, 4),
                       "test_assets": (2, 1), "test_code": (5, 1), "tests": (7, 2)}
        expected = [[kind, size / 1000, lines, spec.stat().st_size / size, len(body) / size, 3 / lines]
                    for kind, (size, lines) in sorted(populations.items())]
        self.assertEqual(expected, await ratios())
        asset.unlink()
        async with asyncio.timeout(6):
            while (await ratios())[2] != ["test_assets", 0.0, 0, None, None, None]:
                await asyncio.sleep(.03)

    async def test_import_publication_failure_reports_stderr_once(self):
        self._source("src/from_source.py", "import to_source\n")
        self._source("src/to_source.py", "")
        gateway = await self._gateway()
        stderr = StringIO()
        with redirect_stderr(stderr), patch("native_query.replace_imports", side_effect=ValueError("fixture write")) as write:
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
            ).fetchall(), [("src/from_source.py",), ("src/to_source.py",)])

    async def test_disk_reopen_rebuild_and_test_relations(self):
        self._source("src/app/main.py", "import dep.helper\n")
        self._source("src/dep/helper.py", "")
        test_directory = self.root / "src/app/app__tests"
        test_directory.mkdir()
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

        await gateway.close()
        self._source("src/dep/helper.py", "import app.main\n")
        from APP_WORKBENCH.FEATURE_IMPORT_GRAPH_C61 import source
        with patch.object(source, "_parse", wraps=source._parse) as parse:
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
                "APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.query_store.insert_rows",
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
