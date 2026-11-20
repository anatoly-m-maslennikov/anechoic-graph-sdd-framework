"""Exercise the opted-in Import Graph through the native Workbench routes."""

import asyncio
from contextlib import redirect_stderr
from dataclasses import replace
from io import StringIO
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import duckdb
import httpx2
from starlette.applications import Starlette
from watchdog.observers.polling import PollingObserver

import test_native_query_stdio as fixture
from native_query import create_native_gateway, publish_imports
from workbench_web import routes


class NativeImportGraphTests(unittest.IsolatedAsyncioTestCase):
    setUp = fixture.NativeQueryStdioTests.setUp
    _write = fixture.NativeQueryStdioTests._write

    def _source(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    async def _gateway(self):
        inputs = fixture._native_inputs()

        def validate(fields, component):
            manifest = inputs.validate_manifest(fields, component)
            return SimpleNamespace(name=manifest.name, prefix=manifest.prefix, parameters={
                "runtime": {"workbench": {"import_graph": {"python_roots": ["src"]}}},
            })

        gateway = create_native_gateway(self.root, fixture.CONTROL, replace(inputs, validate_manifest=validate))
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
            importer = owner._import_sources["src/app/main.py"]
            target = self._source("src/missing.py", "")
            sql = "SELECT resolution_status FROM module_imports WHERE written_specifier = 'missing'"
            async with asyncio.timeout(6):
                while await rows(sql) != [["internal"]]:
                    await asyncio.sleep(.03)
            target.rename(target.with_name("moved.py"))
            async with asyncio.timeout(6):
                while await rows(sql) != [["unresolved"]]:
                    await asyncio.sleep(.03)
            self.assertIs(importer, owner._import_sources["src/app/main.py"])

            owner._inputs = replace(owner._inputs, relation_types=owner._inputs.relation_types | {"TEST_LINK"})
            owner._refresh_after_write(owner._owner())
            self.assertGreater((await rows(graph))[0][0], 0)

    async def test_import_publication_failure_reports_stderr_once(self):
        self._source("src/from_source.py", "import to_source\n")
        self._source("src/to_source.py", "")
        gateway = await self._gateway()
        stderr = StringIO()
        with redirect_stderr(stderr), patch("native_query.publish_imports", side_effect=ValueError("fixture write")) as write:
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
