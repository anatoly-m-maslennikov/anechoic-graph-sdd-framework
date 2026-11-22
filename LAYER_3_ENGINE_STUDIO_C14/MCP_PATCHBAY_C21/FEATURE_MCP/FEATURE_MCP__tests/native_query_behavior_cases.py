"""Native query template and result behavior cases."""

import asyncio
import json
import tempfile
from pathlib import Path
import sys

from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.FEATURE_PROJECT_TOOLS__tests.smalltest_support__pub import extension_directory

MCP = Path(__file__).resolve().parents[1]
CONTROL = ".anechoic_anechoic"


class NativeQueryBehaviorCases:
    async def _create_ticket(self, client, label, container, summary):
        response = await client.call_tool("atom_lifecycle_create_draft", {"newAtom": {
            "template": "task", "label": label, "container": container,
            "body": f"## Summary\n\n{summary}\n",
        }})
        result = response.structured_content
        self.assertEqual("completed", result["status"], result)
        return result["savedDraft"]


    async def test_ticket_label_queries_and_legacy_epic_kind(self):
        self._write("001_TICKETS/TASKS/AN-T-011-EPIC--canonical.md", "AN-T-011", "active", 1, label="Epic")
        self._write("001_TICKETS/TASKS/AN-T-012-SUB_EPIC--canonical.md", "AN-T-012", "active", 1, label="Sub-epic")
        self._write("001_TICKETS/TASKS/AN-T-013-EPIC--legacy.md", "AN-T-013", "active", 1, template="epic")
        self._write("001_TICKETS/TASKS/AN-T-014-TASK--custom.md", "AN-T-014", "active", 1, label="Custom Group")
        async with (
            asyncio.timeout(25),
            stdio_client(StdioServerParameters(
                command=sys.executable, args=self.args,
                env={"PYTHONPATH": str(MCP.parents[1]), "ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY": str(extension_directory(MCP.parents[2]))},
            )) as streams,
            ClientSession(*streams) as client,
        ):
            await client.initialize()

            async def query(**arguments):
                response = await client.call_tool("query_template", {
                    "template": "list_tickets", "result_format": "json_matrix", **arguments,
                })
                self.assertFalse(response.is_error, response.structured_content)
                return response.structured_content

            epics = await query(kind="epic")
            self.assertEqual(["ref", "summary", "kind", "status", "path", "label"],
                             [column["name"] for column in epics["columns"]])
            self.assertEqual({("AN-T-011", "task", "Epic"), ("AN-T-012", "task", "Sub-epic"),
                              ("AN-T-013", "epic", None)},
                             {(row[0], row[2], row[5]) for row in epics["rows"]})
            self.assertEqual(["AN-T-012"], [row[0] for row in (await query(label="sub epic"))["rows"]])
            self.assertEqual(["AN-T-014"], [row[0] for row in (await query(label="CUSTOM-GROUP"))["rows"]])

            parent = await self._create_ticket(client, "Version", {"component": "C00"}, "Parent version")
            child = await self._create_ticket(client, "Epic", {"atom": parent["atom_id"]}, "Child epic")
            promoted = await client.call_tool("atom_lifecycle_promote_draft", {
                "target": {"ref_id": parent["ref_id"], "version": parent["version"]},
                "targetStatus": "backlog",
            })
            self.assertEqual("completed", promoted.structured_content["status"], promoted.structured_content)
            children = (await query(parent=parent["atom_id"], statuses=["backlog"]))["rows"]
            self.assertEqual([(child["atom_id"], "task", "Epic")],
                             [(row[0], row[2], row[5]) for row in children])


    async def _tree_query(self, client, sql, **options):
        response = await client.call_tool("query_run", {
            "sql": sql, "result_delivery": "inline", "project_root": str(self.root), **options,
        })
        self.assertFalse(response.is_error, response.structured_content)
        return response.structured_content


    async def _tree_template(self, client, name, **arguments):
        response = await client.call_tool("query_template", {
            "template": name, "result_format": "json_matrix", **arguments,
        })
        self.assertFalse(response.is_error, response.structured_content)
        return response.structured_content


    async def _check_query_schema(self, client):
        initialized = await client.initialize()
        self.assertIsNone(initialized.capabilities.resources)
        tools = {tool.name: tool for tool in (await client.list_tools()).tools}
        self.assertTrue({"query_run", "query_page", "query_check", "query_schema", "query_template", "workspace_open"} <= set(tools))
        schema = await client.call_tool("query_schema", {})
        self.assertFalse(schema.is_error, schema.structured_content)
        tables = schema.structured_content["tables"]
        self.assertEqual({
            "atoms", "relations", "native_references", "components",
            "import_nodes", "module_imports", "import_edges", "package_imports", "package_external_imports", "test_edges",
            "tested_by_edges", "import_read_issues", "implementation_rmedo", "component_metrics", "package_audit",
            "change_log", "query_log", "live_runs", "runtime_diagnostics", "atom_parse_issues",
            "atom_schema_issues", "atom_declared_carrier_issues", "atom_physical_carrier_issues",
            "atom_duplicate_revision_issues", "boundary_declarations", "code_access_findings",
        }, set(tables))
        small = await client.call_tool("query_run", {"sql": "SELECT 0 AS n FROM range(120)"})
        self.assertFalse(small.is_error, small.structured_content)
        self.assertEqual([[0]] * 120, small.structured_content["rows"])
        self.assertEqual(120, small.structured_content["row_count"])
        self.assertLessEqual(len(small.content[0].text.encode("utf-8")), 4096)
        large = await client.call_tool("query_run", {"sql": "SELECT repeat('a', 4096) AS payload"})
        self.assertFalse(large.is_error, large.structured_content)
        file = large.structured_content["result_file"]
        self.assertEqual("json_matrix", file["format"])
        self.assertEqual([["a" * 4096]], json.loads((self.root / file["path"]).read_text())["rows"])
        csv = await client.call_tool("query_run", {"sql": "SELECT 1 AS n", "result_format": "csv"})
        self.assertFalse(csv.is_error, csv.structured_content)
        self.assertEqual('"n"\r\n"1"\r\n', csv.content[0].text)


    async def _check_atom_templates(self, client):
        current = await self._tree_template(client, "get_atom", reference="AN-T-009")
        self.assertEqual(["exact_ref", "summary", "status", "path"], [column["name"] for column in current["columns"]])
        self.assertEqual([[
            "AN-T-009@2", "Verify the operator's runtime.", "active",
            f"{CONTROL}/001_TICKETS/TASKS/AN-T-009-TASK--verify-runtime.md",
        ]], current["rows"])
        exact = await self._tree_template(client, "get_atom", reference="AN-T-009@1")
        self.assertEqual("AN-T-009@1", exact["rows"][0][0])
        state = await self._tree_template(client, "get_atom_state", reference="AN-T-009")
        self.assertEqual(["status", "version"], [column["name"] for column in state["columns"]])
        self.assertEqual([["active", 2]], state["rows"])
        state_csv = await client.call_tool("query_template", {
            "template": "get_atom_state", "reference": "AN-T-009",
        })
        self.assertFalse(state_csv.is_error, state_csv.structured_content)
        self.assertEqual('"status","version"\r\n"active","2"\r\n', state_csv.content[0].text)
        self.assertEqual(state_csv.content[0].text, state_csv.structured_content["csv"])
        self.assertNotIn("rows", state_csv.structured_content)
        self.assertNotIn("result_file", state_csv.structured_content)
        csv_file = await self._tree_template(client, "list_versions", reference="AN-T-009", result_format="csv", page_size=1)
        self.assertEqual("csv", csv_file["result_file"]["format"])
        self.assertEqual(3, csv_file["result_file"]["row_count"])
        versions = await self._tree_template(client, "list_versions", reference="AN-T-009")
        self.assertEqual(["AN-T-009@3-draft", "AN-T-009@2", "AN-T-009@1"],
                         [item[0] for item in versions["rows"]])
        found = await self._tree_template(client, "find_atoms", text="OPERATOR'S")
        self.assertEqual([["AN-T-009", "Verify the operator's runtime.",
                           f"{CONTROL}/001_TICKETS/TASKS/AN-T-009-TASK--verify-runtime.md"]], found["rows"])
        self.assertEqual(found["rows"], (await self._tree_template(client, "find_atoms", text="TASK--verify-runtime"))["rows"])


    async def _check_inventory_templates(self, client):
        tickets = await self._tree_template(client, "list_tickets", kind="task")
        self.assertEqual({"AN-T-009", "AN-T-009@3-draft", "AN-T-010"}, {item[0] for item in tickets["rows"]})
        children = await self._tree_template(client, "list_tickets", parent="AN-T-009", statuses=["done"])
        self.assertEqual([["AN-T-010", "Fixture.", "task", "done",
                           f"{CONTROL}/001_TICKETS/TASKS/AN-T-010-TASK--child.md", None]], children["rows"])
        listed = await self._tree_template(client, "list_atoms", family="project_config", statuses=["active"])
        self.assertEqual({"AN-P-001", "AN-C-001"}, {row[0] for row in listed["rows"]})
        self.assertEqual({"AN-P-001"}, {row[0] for row in (await self._tree_template(client, "list_atoms", family="pmeta", statuses=["active"]))["rows"]})
        self.assertEqual([["active", 1]], (await self._tree_template(client, "get_atom_state", reference="AN-C-001@1"))["rows"])
        self.assertEqual([["CONTAINED_BY", "AN-P-001", False]],
                         (await self._tree_template(client, "list_relations", reference="AN-C-001@1"))["rows"])
        counted = await self._tree_template(client, "count_atoms", family="tkt", kind="task", statuses=["archived"])
        self.assertEqual(["count"], [column["name"] for column in counted["columns"]])
        self.assertEqual([[1]], counted["rows"])
        grouped = await self._tree_template(client, "count_atoms", family="tkt", group_by="status")
        self.assertEqual([["active", 1], ["archived", 1], ["done", 1], ["draft", 1]], grouped["rows"])
        edges = await self._tree_template(client, "list_relations", reference="AN-T-010@1")
        self.assertEqual([["CONTAINED_BY", "AN-T-009", False]], edges["rows"])
        incoming = await self._tree_template(client, "list_relations", reference="AN-T-010", direction="incoming")
        self.assertEqual([["CONTAINS", "AN-T-009", True]], incoming["rows"])
        edge_counts = await self._tree_template(client, "count_relations_by_type")
        self.assertEqual([["CONTAINED_BY", False, 7], ["CONTAINS", True, 7]], edge_counts["rows"])


    async def _check_query_pages(self, client):
        sql = ("SELECT stable_ref, exact_ref FROM native_references "
               "WHERE exact_ref LIKE 'AN-T-009@%' ORDER BY exact_ref")
        checked = await client.call_tool("query_check", {"sql": sql})
        self.assertTrue(checked.structured_content["valid"])
        first = await self._tree_query(client, sql, page_size=1)
        self.assertEqual([[None, "AN-T-009@1"]], first["rows"])
        page = await client.call_tool("query_page", {
            "query_id": first["query_id"], "offset": 1, "result_delivery": "inline",
        })
        self.assertEqual([["AN-T-009", "AN-T-009@2"], [None, "AN-T-009@3-draft"]],
                         page.structured_content["rows"])
        inverse = await self._tree_query(client, 
            "SELECT relation_type, derived FROM relations "
            "WHERE (source_ref = 'C0' AND target_ref = 'AN-T-009') "
            "OR (source_ref = 'AN-T-009' AND target_ref = 'C0') ORDER BY derived"
        )
        self.assertEqual([["CONTAINED_BY", False], ["CONTAINS", True]], inverse["rows"])
        for name, arguments in (
            ("query_run", {"sql": "SELECT 1", "project_root": str(self.root.parent)}),
            ("query_run", {"sql": "SELECT 1", "save": "yes"}),
            ("query_run", {"sql": "DELETE FROM atoms"}),
            ("query_template", {"template": "list_versions", "reference": "AN-T-009@2"}),
            ("query_template", {"template": "get_atom", "reference": "AN-T-009", "text": "wrong input"}),
            ("workspace_get", {"workspace_id": "unavailable"}),
        ):
            with self.subTest(name=name, arguments=arguments):
                refused = await client.call_tool(name, arguments)
                self.assertTrue(refused.is_error)
        self.assertEqual(7, (await self._tree_query(client, "SELECT count(*) AS atoms FROM atoms"))["rows"][0][0])


    async def _check_query_diagnostics(self, client):
        cases = (
            ("SELECT missing FROM atoms WHERE 'private_binder_value' = 'x'", "binding"),
            ("SELECT 'private_parser_value' FROM", "syntax"),
            ("SELECT CAST('private_conversion_value' AS INTEGER)", "convert"),
        )
        for sql, reason in cases:
            for operation in ("query_run", "query_check"):
                with self.subTest(operation=operation, reason=reason):
                    response = await client.call_tool(operation, {"sql": sql})
                    self.assertTrue(response.is_error)
                    self.assertEqual("failed", response.structured_content["outcome"])
                    detail = json.dumps(response.structured_content).lower()
                    self.assertNotIn("private_", detail)
                    self.assertNotIn(sql.lower(), detail)
                    self.assertIn("query_error", detail)
                    self.assertIn(reason, detail)
                    recovered = await self._tree_query(client, "SELECT 1")
                    self.assertEqual([[1]], recovered["rows"])


    async def test_queries_the_native_tree_and_keeps_legacy_inputs_unchanged(self):
        self._write("001_TICKETS/TASKS/AN-T-010-TASK--child.md", "AN-T-010", "done", 1,
                    container={"atom": "AN-T-009"})
        self._write("002_PROJECT_CONFIG/CUSTOM_MODEL/AN-C-001--definition.md", "AN-C-001", "active", 1,
                    container={"atom": "AN-P-001"})
        before = self._carrier_digests()
        diagnostics = self.enterContext(tempfile.TemporaryFile(mode="w+t"))
        async with (
            asyncio.timeout(25),
            stdio_client(StdioServerParameters(
                command=sys.executable, args=self.args,
                env={"PYTHONPATH": str(MCP.parents[1]), "ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY": str(extension_directory(MCP.parents[2]))},
            ), errlog=diagnostics) as streams,
            ClientSession(*streams) as client,
        ):
            await self._check_query_schema(client)
            await self._check_atom_templates(client)
            await self._check_inventory_templates(client)
            await self._check_query_pages(client)
            await self._check_query_diagnostics(client)
        self.assertEqual(before, self._carrier_digests())
        diagnostics.seek(0)
        output = diagnostics.read()
        self.assertNotIn("private_", output)
        records = [json.loads(line) for line in output.splitlines() if '"code":"query_error"' in line]
        self.assertGreaterEqual(len(records), 6)
        self.assertTrue(all(row["severity"] == "WARNING" and row["outcome"] == "failed" for row in records))


    def _write_component_queries(self):
        self._write("AN-S-011-manifest.md", "AN-S-011", "active", 1, template="component_manifest", lens="SPEC",
                    body="""## Summary

Tools.

## Purpose

Provide project tools.

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest
declare_entity(
    entity_name="Component Manifest",
    instance=ComponentManifest(component_id="C1", name="Tools", layer=3, lens_whitelist=["SPEC"]),
)
```
""")
        self._write("AN-S-012-child-manifest.md", "AN-S-012", "active", 1, template="component_manifest",
                    lens="SPEC", container={"component": "C1"},
                    body="## Claim\n\n### Component ID\n\nC2\n\n### Name\n\nChild\n")
        self._write("AN-S-013-contract.md", "AN-S-013", "active", 1, container={"component": "C1"})
        self._write("AN-S-014-solution.md", "AN-S-014", "active", 1, container={"component": "C1"}, tier=1)
        self._write("AN-S-016@1-draft-contract.md", "AN-S-016", "draft", 1, container={"component": "C1"})
        self._write("AN-S-017-contract.md", "AN-S-017", "active", 1, template="component_contract",
                    container={"component": "C1"}, structure_tier=1, body="## Guarantee\n\nA guarantee.\n")
        self._write("AN-S-018@1-draft-contract.md", "AN-S-018", "draft", 1, template="component_contract",
                    container={"component": "C1"}, structure_tier=1)
        self._write("AN-S-019-child-contract.md", "AN-S-019", "active", 1, template="component_contract",
                    container={"component": "C2"}, structure_tier=1)
        self._write("AN-S-020-wrong-tier-contract.md", "AN-S-020", "active", 1, template="component_contract",
                    container={"component": "C1"}, structure_tier=0)


    async def test_component_queries_use_declared_id_and_owned_spec_tiers(self):
        self._write_component_queries()
        async with (
            asyncio.timeout(25),
            stdio_client(StdioServerParameters(command=sys.executable, args=self.args, env={"PYTHONPATH": str(MCP.parents[1])})) as streams,
            ClientSession(*streams) as client,
        ):
            await client.initialize()
            for template, selector, expected in (
                ("fetch_contracts", "tools", ["AN-S-012@1", "AN-S-013@1", "AN-S-020@1"]),
                ("fetch_solutions", "c1", ["AN-S-014@1", "AN-S-017@1"]),
                ("get_component_manifest", "C1", ["AN-S-011@1"]),
                ("get_component_purpose", " Tools ", ["AN-S-011@1"]),
                ("get_component_purpose", "Child", []),
            ):
                with self.subTest(template=template, selector=selector):
                    result = await client.call_tool("query_template", {
                        "template": template, "component": selector, "result_format": "json_matrix",
                    })
                    self.assertFalse(result.is_error, result.structured_content)
                    self.assertEqual(expected, [row[0] for row in result.structured_content["rows"]])
            result = await client.call_tool("query_run", {
                "sql": "SELECT component_id, name, parent_component_id, layer, lens_whitelist, "
                       "manifest_ref, purpose_refs FROM components WHERE component_id = 'C1'",
                "result_delivery": "inline",
            })
            self.assertFalse(result.is_error, result.structured_content)
            self.assertEqual([["C1", "Tools", "C0", 3, ["SPEC"], "AN-S-011@1", ["AN-S-011@1"]]],
                             result.structured_content["rows"])

