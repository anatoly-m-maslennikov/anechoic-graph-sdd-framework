"""Exercise the Import Graph through the native Workbench routes."""

import asyncio as asyncio
from contextlib import redirect_stderr
from io import StringIO
import json as json
from pathlib import Path
from unittest.mock import patch

import duckdb
import httpx2
from mcp import types
from starlette.applications import Starlette

from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import read_import_sources
from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import publish_imports
from MCP_PATCHBAY_C21.FEATURE_MCP.gateway.gateway__shared import (
    routes as routes,
)


from ..group_2.native_import_graph_cases_4_extra import ImportGraphCases4Extra


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


class ImportGraphCases4(ImportGraphCases4Extra):
    async def test_import_publication_failure_reports_stderr_once(self):
        self._source("src/from_source.py", "import to_source\n")
        self._source("src/to_source.py", "")
        gateway = await self._gateway()
        stderr = StringIO()
        with (
            redirect_stderr(stderr),
            patch(
                "KERNEL_MIXER_C59.realization_projection.replace_imports",
                side_effect=ValueError("fixture write"),
            ) as write,
        ):
            self._source("src/new_source.py", "")
            async with asyncio.timeout(6):
                while "fixture write" not in stderr.getvalue():
                    await asyncio.sleep(0.03)
            self.assertEqual(write.call_count, 1)
        store = gateway._native_query._owner()
        duplicate = ("duplicate", "module", "python", "new.py", "ok", None)
        with self.assertRaises(duckdb.ConstraintException):
            publish_imports(store, [duplicate, duplicate], [], [])
        with store._lock:
            self.assertEqual(
                store._connection.execute(
                    (
                        "SELECT relative_path FROM import_nodes ORDER BY "
                        "relative_path"
                    ),
                ).fetchall(),
                [("src",), ("src/from_source.py",), ("src/to_source.py",)],
            )

    async def _check_disk_rebuild(
        self,
        gateway,
        store,
        post,
        view_call,
        view,
        first,
        independent,
        expected,
        test_directory,
    ):
        moved = test_directory.parent.parent / test_directory.name
        test_directory.rename(moved)
        rebuilt = await post("rebuild", {"target": "test_edges"})
        second = rebuilt["result_ids"][first]
        self.assertNotEqual(first, second)
        self.assertNotIn(independent, rebuilt["result_ids"])
        fetched = await view_call(
            "view_fetch", view | {"result_delivery": "inline"}
        )
        self.assertEqual((second, []), (fetched["query_id"], fetched["rows"]))
        self.assertTrue(store._results[second].pinned)
        stderr = StringIO()
        with (
            redirect_stderr(stderr),
            patch.object(
                store,
                "prepare_result_rebuild",
                side_effect=ValueError("fixture rebuild failure"),
            ),
        ):
            await post("rebuild", {"target": "test_edges"}, 400)
        self.assertIn("fixture rebuild failure", stderr.getvalue())
        fetched = await view_call(
            "view_fetch", view | {"result_delivery": "inline"}
        )
        self.assertEqual((second, []), (fetched["query_id"], fetched["rows"]))
        moved.rename(test_directory)
        await self._assert_mcp_rebuild(
            gateway, post, view_call, view, second, expected
        )

    async def _assert_mcp_rebuild(
        self, gateway, post, view_call, view, second, expected
    ):
        mcp = await gateway.call(
            None,
            types.CallToolRequestParams(
                name="query_rebuild",
                arguments={"target": "all"},
            ),
        )
        self.assertFalse(mcp.is_error, mcp.structured_content)
        third = mcp.structured_content["result_ids"][second]
        fetched = await view_call(
            "view_fetch", view | {"result_delivery": "inline"}
        )
        self.assertEqual(
            (third, expected), (fetched["query_id"], fetched["rows"])
        )
        single = await post(
            "rebuild", {"target": f"workbench_results.query_{third}"}
        )
        self.assertIn(third, single["result_ids"])

    async def _check_disk_http(
        self, gateway, store, database, test_directory, sql
    ):
        app = Starlette(routes=routes(gateway))
        async with httpx2.AsyncClient(
            transport=httpx2.ASGITransport(app=app),
            base_url="http://127.0.0.1:18093",
        ) as client:
            base = "/anechoic/Anechoic/api"

            async def post(operation, arguments, status=200):
                response = await client.post(
                    f"{base}/{operation}", json=arguments
                )
                self.assertEqual(status, response.status_code, response.text)
                return response.json()

            async def view_call(operation, arguments):
                return await post(
                    "interface",
                    {"operation": operation, "arguments": arguments},
                )

            view, first, independent, expected = await self._prepare_disk_view(
                view_call, post, sql
            )
            with store._lock:
                database_file = store._connection.execute(
                    "SELECT path FROM duckdb_databases() WHERE NOT internal"
                ).fetchone()[0]
                self.assertEqual(database.resolve().as_posix(), database_file)
            await self._assert_unknown_rebuild(gateway, post)
            await self._check_disk_rebuild(
                gateway,
                store,
                post,
                view_call,
                view,
                first,
                independent,
                expected,
                test_directory,
            )

    async def _prepare_disk_view(self, view_call, post, sql):
        workspace = await view_call(
            "workspace_open", {"session_id": "realization"}
        )
        view = {
            "workspace_id": workspace["workspace_id"],
            "view_id": workspace["active_view_id"],
        }
        await view_call(
            "view_update", view | {"sql": sql, "expected_revision": 0}
        )
        first = (await view_call("view_run", view))["query_id"]
        independent = (
            await post("run", {"sql": "SELECT 7", "result_delivery": "inline"})
        )["query_id"]
        expected = [["src/app", "src/app/app__tests", "Test Package"]]
        self.assertEqual(
            expected,
            (
                await view_call(
                    "view_fetch", view | {"result_delivery": "inline"}
                )
            )["rows"],
        )
        return view, first, independent, expected

    async def _assert_unknown_rebuild(self, gateway, post):
        stderr = StringIO()
        with redirect_stderr(stderr):
            rejected = await post("rebuild", {"target": "unknown"}, 400)
        self.assertIn("Unknown Workbench rebuild target", rejected["error"])
        self.assertIn("Unknown Workbench rebuild target", stderr.getvalue())
        with redirect_stderr(StringIO()) as errors:
            response = await gateway.call(
                None,
                types.CallToolRequestParams(
                    name="query_rebuild",
                    arguments={"target": "missing"},
                ),
            )
        self.assertTrue(response.is_error)
        self.assertIn(
            "Unknown Workbench rebuild target",
            str(response.structured_content),
        )
        self.assertIn("Unknown Workbench rebuild target", errors.getvalue())

    async def test_disk_reopen_rebuild_and_test_relations(self):
        self._source("src/app/main.py", "import dep.helper\n")
        self._source("src/dep/helper.py", "")
        test_directory = self._source(
            "src/app/app__tests/test_app.py", "pass\n"
        ).parent
        gateway = await self._gateway()
        owner = gateway._native_query
        store = owner._owner()
        database = self.root / ".anechoic_runtime/db/project.duckdb"
        self.assertTrue(database.is_file())
        sql = """
            SELECT parent.relative_path, test.relative_path, test.package_type
            FROM tested_by_edges e JOIN import_nodes parent ON parent.node_key = e.source_key
            JOIN import_nodes test ON test.node_key = e.target_key
        """
        await self._check_disk_http(
            gateway, store, database, test_directory, sql
        )

        await gateway.close()
        await self._assert_disk_reopen()

    async def _assert_disk_reopen(self):
        self._source("src/dep/helper.py", "import app.main\n")
        read_paths = []
        read_bytes = Path.read_bytes

        def record_source_read(path):
            if path.suffix == ".py" and path.is_relative_to(self.root):
                read_paths.append(path.relative_to(self.root).as_posix())
            return read_bytes(path)

        with patch.object(Path, "read_bytes", record_source_read):
            reopened = await self._gateway()
        self.assertEqual(["src/dep/helper.py"], read_paths)
        reopened_store = reopened._native_query._owner()
        self.assertFalse(reopened_store._results)
        with reopened_store._lock:
            self.assertEqual(
                [(2,)],
                reopened_store._connection.execute(
                    "SELECT count(*) FROM module_imports"
                ).fetchall(),
            )
            self.assertEqual(
                [],
                reopened_store._connection.execute(
                    (
                        "SELECT table_name FROM information_schema.tables "
                        "WHERE table_schema = 'workbench_results'"
                    )
                ).fetchall(),
            )
        await reopened.close()
        disabled = await self._gateway(enabled=False)
        self.assertNotIn(
            "test_edges", disabled._native_query.schema()["tables"]
        )
        disabled_store = disabled._native_query._owner()
        with disabled_store._lock:
            self.assertFalse(read_import_sources(disabled_store._connection))
