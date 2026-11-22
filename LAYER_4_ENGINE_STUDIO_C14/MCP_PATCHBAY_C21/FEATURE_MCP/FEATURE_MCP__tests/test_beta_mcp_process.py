"""Run the ordinary MCP entry point with only the Beta runtime Components."""

import asyncio
import os
from pathlib import Path
import shutil
import sys
from tempfile import TemporaryDirectory
import unittest

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

ENGINE = Path(__file__).resolve().parents[3]
COMPONENTS = ("FEATURE_PROGRAMMATIC", "MCP_PATCHBAY_C21", "KERNEL_MIXER_beta_C67",
              "ORCHESTRATOR_beta_C68", "WORKERS_beta_C69", "WORKBENCH_BACKEND_beta_C70",
              "IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_IMPORT_GRAPH_C61")


def _stage(root):
    engine = root / ENGINE.name
    for component in COMPONENTS:
        shutil.copytree(ENGINE / component, engine / component, ignore=shutil.ignore_patterns(
            "__pycache__", "*__tests", ".venv*", "node_modules", "fixtures", ".git",
        ))
    return engine


def _project(root):
    control = root / "_anechoic_example"
    control.mkdir(parents=True)
    (control / "EX-S-1-PROJECT_MANIFEST--declare-example.md").write_text(
        "---\natom_family: SPEC\natom_id: EX-S-1\ncontainer:\n  component: C00\ntier: -1\n"
        "context:\n  template: project_manifest\n  lens: SPEC\nstate:\n  status: active\n  version: 1\n"
        "  updated_at: '2026-11-19T00:00:00Z'\n---\n\n## Summary\n\nDeclare Example\n\n"
        "## Claim\n\n### Formal Claim\n\n```python\n"
        "from anechoic.formal_claims import declare_entity\n"
        "from anechoic.model import ProjectManifest\n"
        "declare_entity(entity_name='Project Manifest', instance=ProjectManifest(name='Example', prefix='EX', "
        "parameters={'runtime': {'workbench': {'import_graph': {'python_roots': ['.']}}}, "
        "'paths': {'journal_root': 'custom/journal'}}))\n```\n",
        encoding="utf-8",
    )
    task = control / "001_TICKETS/TASKS/EX-T-1-TASK--example.md"
    task.parent.mkdir(parents=True)
    task.write_text(
        "---\natom_family: TKT\natom_id: EX-T-1\ncontainer:\n  component: C00\npriority: 2\n"
        "relations:\n  CHILD_OF: [EX-S-1]\n"
        "context:\n  template: task\nstate:\n  status: active\n  version: 1\n"
        "  updated_at: '2026-11-19T00:00:00Z'\n---\n\n## Summary\n\nExample task\n",
        encoding="utf-8",
    )
    (root / "main.py").write_text("import helper\n")
    (root / "helper.py").write_text("value = 1\n")
    journal = root / "custom/journal"
    journal.mkdir(parents=True)
    (journal / "test-2026-11-19-part-1.ndjson").write_text('{"action":"verify"}\n', encoding="utf-8")


class BetaMcpTest(unittest.IsolatedAsyncioTestCase):
    async def test_one_selected_project_query(self):
        with TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            engine = _stage(root / "framework")
            project = root / "project"
            _project(project)
            parameters = StdioServerParameters(
                command=sys.executable,
                args=["-B", "-P", "-m", "MCP_PATCHBAY_C21.FEATURE_MCP.server", "--project-root", str(project)],
                cwd=engine.parent, env={
                    "PYTHONPATH": str(engine), "ANECHOIC_RUNTIME_STACK": "beta",
                    "ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY": os.environ.get(
                        "ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY",
                        str(ENGINE.parent / ".anechoic_tmp/workbench/extensions"),
                    ),
                },
            )
            async with asyncio.timeout(90), stdio_client(parameters) as streams, ClientSession(*streams) as client:
                await client.initialize()
                tools = (await client.list_tools()).tools
                self.assertTrue({"query_run", "query_schema", "query_check", "query_page",
                                 "workspace_open", "view_update", "view_run", "view_check", "view_fetch"}
                                <= {tool.name for tool in tools})
                await self.assert_schema(client)
                query = {"sql": 'SELECT reference, "content.summary" FROM atoms ORDER BY reference',
                         "page_size": 1, "cursor_position": 0, "result_delivery": "inline"}
                reply = await client.call_tool("query_run", query)
                self.assertFalse(reply.is_error, reply.structured_content)
                first = reply.structured_content
                self.assertEqual([["EX-S-1", "Declare Example"]], first["rows"])
                self.assertEqual(2, first["row_count"])
                self.assertTrue(first["has_more"])
                page = await client.call_tool("query_page", {
                    "query_id": first["query_id"], "offset": 1, "page_size": 1, "result_delivery": "inline",
                })
                self.assertFalse(page.is_error, page.structured_content)
                self.assertEqual([["EX-T-1", "Example task"]], page.structured_content["rows"])
                self.assertFalse(page.structured_content["has_more"])
                await self.assert_history(client, query["sql"])
                await self.assert_grid_and_journal(client, first["query_id"])
                await self.assert_workspace(client)
                await self.assert_native_projection(client)
                await self.assert_live_graph(client, project)
                reply = await client.call_tool("query_run", {**query, "project_root": str(root)})
                self.assertTrue(reply.is_error)

    async def assert_history(self, client, sql):
        async with asyncio.timeout(5):
            while True:
                reply = await client.call_tool("query_log_list", {"limit": 1})
                self.assertFalse(reply.is_error, reply.structured_content)
                if records := reply.structured_content["items"]:
                    break
                await asyncio.sleep(0.05)
        record = records[0]
        self.assertEqual((sql, "success", 2, 2),
                         (record["sql"], record["outcome"], record["row_count"], record["column_count"]))
        fetched = await client.call_tool("query_log_get", {"log_id": record["log_id"]})
        self.assertFalse(fetched.is_error, fetched.structured_content)
        self.assertEqual(record, fetched.structured_content)

    async def assert_grid_and_journal(self, client, query_id):
        status = await client.call_tool("workbench_status", {})
        self.assertEqual("live_index", status.structured_content["mode"])
        page = await client.call_tool("query_page", {"query_id": query_id, "result_delivery": "inline", "grid": {
            "filters": [{"column": 1, "operator": "contains", "value": "task"}]}})
        self.assertFalse(page.is_error, page.structured_content)
        self.assertEqual((1, 2), (page.structured_content["row_count"], page.structured_content["source_row_count"]))
        self.assertEqual([["EX-T-1", "Example task"]], page.structured_content["rows"])
        journal = await client.call_tool("query_run", {"sql": "SELECT author FROM work_journal ORDER BY author"})
        self.assertFalse(journal.is_error, journal.structured_content)
        self.assertEqual([["test"]], journal.structured_content["rows"])

    async def assert_schema(self, client):
        schema = await client.call_tool("query_schema", {})
        self.assertFalse(schema.is_error, schema.structured_content)
        tables = schema.structured_content["tables"]
        self.assertEqual(["reference", "content.summary", "relative_path", "filename", "status_group",
                          "header.state.version", "header.state.status"],
                         [column["name"] for column in tables["atoms"]])
        self.assertTrue({"package_external_imports", "native_references", "relations", "query_log"} <= tables.keys())

    async def assert_workspace(self, client):
        opened = await client.call_tool("workspace_open", {"session_id": "mcp-session"})
        self.assertFalse(opened.is_error, opened.structured_content)
        workspace = opened.structured_content
        self.assertEqual("Example", workspace["project_name"])
        key = {"workspace_id": workspace["workspace_id"], "view_id": workspace["active_view_id"]}
        changed = await client.call_tool("view_update", key | {"sql": "SELECT 2", "expected_revision": 0})
        self.assertFalse(changed.is_error, changed.structured_content)
        self.assertEqual(1, changed.structured_content["revision"])
        fetched = await client.call_tool("view_get", key)
        self.assertEqual("SELECT 2", fetched.structured_content["sql"])
        checked = await client.call_tool("view_check", key)
        self.assertTrue(checked.structured_content["valid"])
        self.assertNotIn("sql", checked.structured_content)
        run = await client.call_tool("view_run", key)
        self.assertEqual("success", run.structured_content["status"], run.structured_content)
        self.assertNotIn("rows", run.structured_content)
        page = await client.call_tool("view_fetch", key | {"page_size": 1, "result_delivery": "inline"})
        self.assertEqual([[2]], page.structured_content["rows"])
        self.assertEqual(run.structured_content["query_id"], page.structured_content["query_id"])
        rebuilt = await client.call_tool("query_rebuild", {"target": "all"})
        self.assertFalse(rebuilt.is_error, rebuilt.structured_content)
        new_id = rebuilt.structured_content["result_ids"][run.structured_content["query_id"]]
        self.assertNotEqual(run.structured_content["query_id"], new_id)
        page = await client.call_tool("view_fetch", key | {"page_size": 1, "result_delivery": "inline"})
        self.assertEqual((new_id, [[2]]), (page.structured_content["query_id"], page.structured_content["rows"]))

    async def assert_live_graph(self, client, project):
        query = {"sql": "SELECT resolution_status FROM module_imports WHERE written_specifier = 'helper'"}
        result = await client.call_tool("query_run", query)
        self.assertEqual([["internal"]], result.structured_content["rows"])
        match = await client.call_tool("query_run", {"sql": """
            FROM GRAPH_TABLE (anechoic MATCH (s:ImportNode)-[e:Imports]->(t:ImportNode)
                COLUMNS (s.relative_path AS source, t.relative_path AS target))
            WHERE source = 'main.py' AND target = 'helper.py'
        """})
        self.assertEqual([["main.py", "helper.py"]], match.structured_content["rows"])
        (project / "helper.py").rename(project / "changed.py")
        deadline = asyncio.get_running_loop().time() + 20
        while asyncio.get_running_loop().time() < deadline:
            result = await client.call_tool("query_run", query)
            if result.structured_content.get("rows") == [["unresolved"]]:
                return
            await asyncio.sleep(0.2)
        self.fail(f"Graph did not follow renamed source: {result.structured_content}")

    async def assert_native_projection(self, client):
        query = {"sql": """
            SELECT reference, exact_ref, "header.state.version"
            FROM atoms JOIN native_references USING (reference)
            WHERE reference = 'EX-T-1'
        """}
        reply = await client.call_tool("query_run", query)
        self.assertEqual([["EX-T-1", "EX-T-1@1", 1]], reply.structured_content["rows"])
        graph = await client.call_tool("query_run", {"sql": """
            FROM GRAPH_TABLE (anechoic MATCH (s:Reference)-[e:CONTAINED_BY]->(t:Reference)
                COLUMNS (s.ref AS source, t.ref AS target)) WHERE source = 'EX-T-1'
        """})
        self.assertEqual([["EX-T-1", "C00"]], graph.structured_content["rows"])
        authored = await client.call_tool("query_run", {"sql": """
            SELECT target_ref FROM relations WHERE source_ref = 'EX-T-1'
            AND NOT derived AND relation_type = 'CHILD_OF'
        """})
        self.assertEqual([["EX-S-1"]], authored.structured_content["rows"])


if __name__ == "__main__":
    unittest.main()
