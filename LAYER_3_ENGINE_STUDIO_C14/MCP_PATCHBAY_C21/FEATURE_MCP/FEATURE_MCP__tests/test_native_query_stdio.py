"""Exercise the existing MCP stdio entry point with native Workbench."""

import asyncio
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import patch

import httpx2
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
from mcp.client.streamable_http import streamable_http_client
import yaml


MCP = Path(__file__).resolve().parents[1]
PROGRAMMATIC = MCP.parents[1] / "FEATURE_PROGRAMMATIC"
APP_TESTS = MCP.parents[1] / "IWE_CONSOLE_C43" / "APP_WORKBENCH" / "APP_WORKBENCH__tests"
sys.path[:0] = [str(MCP), str(PROGRAMMATIC), str(PROGRAMMATIC / "FEATURE_TOOLS"), str(APP_TESTS)]

from smalltest_support import extension_directory, polling_source_watcher  # noqa: E402


CONTROL = ".anechoic_anechoic"
MANIFEST = "AN-S-001-PROJECT_MANIFEST--declare-anechoic.md"
OLD_PATH = ".anechoic_legacy/03_plan/CA-P-9--old-task.md"
UNNUMBERED_PATH = ".anechoic_legacy/03_plan/archive/old-task.md"
STAGING_COPY_PATH = "migration-evidence/03_plan/old-task-copy.md"


def _native_inputs():
    from native_query import NativeQueryInputs
    from FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.model_class_assembly import assemble_model_classes
    from FEATURE_MODEL.FEATURE_MODEL_VALIDATION.model_field_validation import validate_model_fields

    model = ModuleType("compiled_mcp_fixture")
    sys.modules[model.__name__] = model
    source = assemble_model_classes(["""
from anechoic.formal_claims import declare_entity
from dataclasses import field

class ProjectManifest:
    atom_id: str
    ref_id: str
    version: int
    tier: int = field(metadata={"allowed_values": (-1,)})
    name: str
    prefix: str

declare_entity(entity_name="Project Manifest", entity_class=ProjectManifest)
"""])
    exec(source, vars(model))

    def validate_manifest(fields, owner):
        if owner != "C0":
            raise ValueError("Manifest must be contained by the Project")
        validate_model_fields(model.ProjectManifest, fields)
        return model.ProjectManifest(**fields)

    return NativeQueryInputs(
        validate_manifest=validate_manifest,
        relation_types=frozenset({"CONTAINED_BY", "CONTAINS"}),
        inverses={"CONTAINED_BY": "CONTAINS"},
        extension_directory=extension_directory(MCP.parents[2]),
        ticket_labels=("Task", "Subtask", "Sub-epic", "Epic", "Version"),
    )


def _launch_server():
    from server import main
    with polling_source_watcher():
        return main(sys.argv[1:], native_inputs=_native_inputs())


class NativeJournalOwnershipTests(unittest.TestCase):
    def test_rejects_journal_outside_selected_control(self):
        from native_query import NativeQueryOwner

        with tempfile.TemporaryDirectory() as root:
            for journal in ("_anechoic_other/_journal", ".anechoic_other/_journal"):
                selection = SimpleNamespace(root=Path(root).resolve(), control_relative=Path("_anechoic_anechoic"),
                                            parameters={"paths": {"journal_root": journal}})
                with self.subTest(journal=journal), self.assertRaisesRegex(ValueError, "another records tree"):
                    NativeQueryOwner(selection, None)
            selection.parameters["paths"]["journal_root"] = "elsewhere/journal"
            with patch("native_query.SavedQueryStore") as saved, patch("native_query.WorkspaceStore"), \
                    patch("native_query.QueryLog"):
                NativeQueryOwner(selection, None)
                self.assertEqual("elsewhere/journal", saved.call_args.kwargs["journal_root"])

class NativeQueryStdioTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.enterContext(polling_source_watcher())
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        self._write(MANIFEST, "AN-S-001", "active", 1, template="project_manifest", body="""
## Summary

Declare the native Project.

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ProjectManifest
declare_entity(entity_name="Project Manifest", instance=ProjectManifest(name="Anechoic", prefix="AN"))
```
""")
        self._write("__TKT/TASKS/AN-T-009-TASK--verify-runtime.md", "AN-T-009", "active", 2,
                    body="## Summary\n\nVerify the operator's runtime.\n")
        self._write("__TKT/TASKS/archived/AN-T-009@1-TASK--verify-runtime.md", "AN-T-009", "archived", 1)
        self._write("__TKT/TASKS/draft/AN-T-009@3-draft-TASK--verify-runtime.md", "AN-T-009", "draft", 3)
        self._write("_PMETA/AN-P-001-WORKFLOW--fixture.md", "AN-P-001", "active", 1)
        legacy = self.root / OLD_PATH
        legacy.parent.mkdir(parents=True)
        legacy.write_text("Legacy carrier held beside the selected native tree.\n", encoding="utf-8")
        unnumbered = self.root / UNNUMBERED_PATH
        unnumbered.parent.mkdir()
        unnumbered.write_text("## Summary\n\nArchived task with no legacy ID.\n", encoding="utf-8")
        (self.root / ".anechoic_legacy" / "anechoic_project_settings.toml").write_text(
            '[project_mcp]\nhttp_port = 18000\ntool_blacklist = ["query_run"]\n', encoding="utf-8",
        )
        self.args = [str(Path(__file__).resolve()), "--project-root", str(self.root), "--control-root", CONTROL]

    def _write(self, relative, atom_id, status, version, *, template="task", body="## Summary\n\nFixture.\n",
               container=None, tier=None, lens=None, structure_tier=None, label=None):
        path = self.root / CONTROL / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        metadata = {
            "identity": {"atom_id": atom_id},
            "context": {"container": container or {"component": "C0"}, "template": template,
                        "tier": tier if tier is not None else -1 if template == "project_manifest" else 0},
            "state": {"version": version, "status": status, "updated_at": "2026-11-19T00:00:00Z"},
        }
        if label is not None:
            metadata["context"]["label"] = label
        if lens:
            metadata["context"]["lens"] = lens
        if structure_tier is not None:
            from native_carrier_header import canonical_native_header

            metadata["context"]["tier"] = structure_tier
            metadata["context"].setdefault("lens", "DES")
            metadata = canonical_native_header(metadata)
        path.write_text(f"---\n{yaml.safe_dump(metadata)}---\n\n{body}", encoding="utf-8")

    def _carrier_digests(self):
        return {path.relative_to(self.root): hashlib.sha256(path.read_bytes()).hexdigest()
                for path in self.root.rglob("*") if path.is_file()
                and path.relative_to(self.root).parts[0] not in {".anechoic_runtime", ".anechoic_tmp"}}

    async def test_discovered_query_templates_and_statuses_are_callable(self):
        samples = {
            "get_atom": {"reference": "AN-T-009"},
            "get_atom_state": {"reference": "AN-T-009"},
            "find_atoms": {"text": "fixture"},
            "list_versions": {"reference": "AN-T-009"},
            "list_tickets": {"label": "Task"},
            "list_atoms": {"family": "spec"},
            "count_atoms": {"group_by": "status"},
            "list_relations": {"reference": "AN-T-009"},
            "count_relations_by_type": {},
            "fetch_contracts": {"component": "C00"},
            "fetch_solutions": {"component": "C00"},
            "get_component_manifest": {"component": "C00"},
            "get_component_purpose": {"component": "C00"},
        }
        async with (
            asyncio.timeout(25),
            stdio_client(StdioServerParameters(command=sys.executable, args=self.args)) as streams,
            ClientSession(*streams) as client,
        ):
            await client.initialize()
            tools = (await client.list_tools()).tools
            descriptor = next(tool for tool in tools if tool.name == "query_template")
            properties = descriptor.input_schema["properties"]
            self.assertEqual(set(samples), set(properties["template"]["enum"]))
            statuses = properties["statuses"]["items"]["enum"]
            self.assertTrue({"ready", "in_queue", "complete"}.issubset(statuses))
            for template, arguments in samples.items():
                with self.subTest(template=template):
                    response = await client.call_tool("query_template", {
                        "template": template, "result_format": "json_matrix", **arguments,
                    })
                    self.assertFalse(response.is_error, response.structured_content)
            for status in statuses:
                with self.subTest(status=status):
                    response = await client.call_tool("query_template", {
                        "template": "list_tickets", "statuses": [status], "result_format": "json_matrix",
                    })
                    self.assertFalse(response.is_error, response.structured_content)

    async def test_ticket_label_queries_and_legacy_epic_kind(self):
        self._write("__TKT/TASKS/AN-T-011-EPIC--canonical.md", "AN-T-011", "active", 1, label="Epic")
        self._write("__TKT/TASKS/AN-T-012-SUB_EPIC--canonical.md", "AN-T-012", "active", 1, label="Sub-epic")
        self._write("__TKT/TASKS/AN-T-013-EPIC--legacy.md", "AN-T-013", "active", 1, template="epic")
        self._write("__TKT/TASKS/AN-T-014-TASK--custom.md", "AN-T-014", "active", 1, label="Custom Group")
        async with (
            asyncio.timeout(25),
            stdio_client(StdioServerParameters(
                command=sys.executable, args=self.args,
                env={"ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY": str(extension_directory(MCP.parents[2]))},
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

            async def create(label, container, summary):
                response = await client.call_tool("atom_lifecycle_create_draft", {"newAtom": {
                    "template": "task", "label": label, "container": container,
                    "body": f"## Summary\n\n{summary}\n",
                }})
                result = response.structured_content
                self.assertEqual("completed", result["status"], result)
                return result["savedDraft"]

            parent = await create("Version", {"component": "C00"}, "Parent version")
            child = await create("Epic", {"atom": parent["atom_id"]}, "Child epic")
            promoted = await client.call_tool("atom_lifecycle_promote_draft", {
                "target": {"ref_id": parent["ref_id"], "version": parent["version"]},
                "targetStatus": "backlog",
            })
            self.assertEqual("completed", promoted.structured_content["status"], promoted.structured_content)
            children = (await query(parent=parent["atom_id"], statuses=["backlog"]))["rows"]
            self.assertEqual([(child["atom_id"], "task", "Epic")],
                             [(row[0], row[2], row[5]) for row in children])

    async def test_queries_the_native_tree_and_keeps_legacy_inputs_unchanged(self):
        self._write("__TKT/TASKS/AN-T-010-TASK--child.md", "AN-T-010", "done", 1,
                    container={"atom": "AN-T-009"})
        before = self._carrier_digests()
        async with (
            asyncio.timeout(25),
            stdio_client(StdioServerParameters(
                command=sys.executable, args=self.args,
                env={"ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY": str(extension_directory(MCP.parents[2]))},
            )) as streams,
            ClientSession(*streams) as client,
        ):
            initialized = await client.initialize()
            self.assertIsNone(initialized.capabilities.resources)
            tools = {tool.name: tool for tool in (await client.list_tools()).tools}
            self.assertTrue({"query_run", "query_page", "query_check", "query_schema", "query_template", "workspace_open"} <= set(tools))
            schema = await client.call_tool("query_schema", {})
            self.assertFalse(schema.is_error, schema.structured_content)
            tables = schema.structured_content["tables"]
            self.assertEqual({
                "atoms", "relations", "native_references", "components",
                "import_nodes", "module_imports", "import_edges", "package_imports", "test_edges",
                "tested_by_edges", "import_read_issues", "implementation_rmedo", "component_metrics", "package_audit",
                "change_log", "query_log", "live_runs", "runtime_diagnostics", "atom_parse_issues",
                "atom_schema_issues", "atom_declared_carrier_issues", "atom_physical_carrier_issues",
                "atom_duplicate_revision_issues",
            }, set(tables))
            small = await client.call_tool("query_run", {"sql": "SELECT 0 AS n FROM range(120)"})
            self.assertFalse(small.is_error, small.structured_content)
            self.assertEqual([[0]] * 120, small.structured_content["rows"])
            self.assertLessEqual(len(small.content[0].text.encode("utf-8")), 4096)
            large = await client.call_tool("query_run", {"sql": "SELECT repeat('a', 4096) AS payload"})
            self.assertFalse(large.is_error, large.structured_content)
            file = large.structured_content["result_file"]
            self.assertEqual("json_matrix", file["format"])
            self.assertEqual([["a" * 4096]], json.loads((self.root / file["path"]).read_text())["rows"])
            csv = await client.call_tool("query_run", {"sql": "SELECT 1 AS n", "result_format": "csv"})
            self.assertFalse(csv.is_error, csv.structured_content)
            self.assertEqual('"n"\r\n"1"\r\n', csv.content[0].text)

            async def query(sql, **options):
                response = await client.call_tool("query_run", {
                    "sql": sql, "result_delivery": "inline", "project_root": str(self.root), **options,
                })
                self.assertFalse(response.is_error, response.structured_content)
                return response.structured_content

            async def template(name, **arguments):
                response = await client.call_tool("query_template", {
                    "template": name, "result_format": "json_matrix", **arguments,
                })
                self.assertFalse(response.is_error, response.structured_content)
                return response.structured_content

            current = await template("get_atom", reference="AN-T-009")
            self.assertEqual(["exact_ref", "summary", "status", "path"], [column["name"] for column in current["columns"]])
            self.assertEqual([[
                "AN-T-009@2", "Verify the operator's runtime.", "active",
                f"{CONTROL}/__TKT/TASKS/AN-T-009-TASK--verify-runtime.md",
            ]], current["rows"])
            exact = await template("get_atom", reference="AN-T-009@1")
            self.assertEqual("AN-T-009@1", exact["rows"][0][0])
            state = await template("get_atom_state", reference="AN-T-009")
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
            csv_file = await template("list_versions", reference="AN-T-009", result_format="csv", page_size=1)
            self.assertEqual("csv", csv_file["result_file"]["format"])
            self.assertEqual(3, csv_file["result_file"]["row_count"])
            versions = await template("list_versions", reference="AN-T-009")
            self.assertEqual(["AN-T-009@3-draft", "AN-T-009@2", "AN-T-009@1"],
                             [item[0] for item in versions["rows"]])
            found = await template("find_atoms", text="OPERATOR'S")
            self.assertEqual([["AN-T-009", "Verify the operator's runtime.",
                               f"{CONTROL}/__TKT/TASKS/AN-T-009-TASK--verify-runtime.md"]], found["rows"])
            self.assertEqual(found["rows"], (await template("find_atoms", text="TASK--verify-runtime"))["rows"])
            tickets = await template("list_tickets", kind="task")
            self.assertEqual({"AN-T-009", "AN-T-009@3-draft", "AN-T-010"}, {item[0] for item in tickets["rows"]})
            children = await template("list_tickets", parent="AN-T-009", statuses=["done"])
            self.assertEqual([["AN-T-010", "Fixture.", "task", "done",
                               f"{CONTROL}/__TKT/TASKS/AN-T-010-TASK--child.md", None]], children["rows"])
            listed = await template("list_atoms", family="pmeta", statuses=["active"])
            self.assertEqual([["AN-P-001", "Fixture.", "task", "active",
                               f"{CONTROL}/_PMETA/AN-P-001-WORKFLOW--fixture.md"]], listed["rows"])
            counted = await template("count_atoms", family="tkt", kind="task", statuses=["archived"])
            self.assertEqual(["count"], [column["name"] for column in counted["columns"]])
            self.assertEqual([[1]], counted["rows"])
            grouped = await template("count_atoms", family="tkt", group_by="status")
            self.assertEqual([["active", 1], ["archived", 1], ["done", 1], ["draft", 1]], grouped["rows"])
            edges = await template("list_relations", reference="AN-T-010@1")
            self.assertEqual([["CONTAINED_BY", "AN-T-009", False]], edges["rows"])
            incoming = await template("list_relations", reference="AN-T-010", direction="incoming")
            self.assertEqual([["CONTAINS", "AN-T-009", True]], incoming["rows"])
            edge_counts = await template("count_relations_by_type")
            self.assertEqual([["CONTAINED_BY", False, 6], ["CONTAINS", True, 6]], edge_counts["rows"])
            sql = ("SELECT stable_ref, exact_ref FROM native_references "
                   "WHERE exact_ref LIKE 'AN-T-009@%' ORDER BY exact_ref")
            checked = await client.call_tool("query_check", {"sql": sql})
            self.assertTrue(checked.structured_content["valid"])
            first = await query(sql, page_size=1)
            self.assertEqual([[None, "AN-T-009@1"]], first["rows"])
            page = await client.call_tool("query_page", {
                "query_id": first["query_id"], "offset": 1, "result_delivery": "inline",
            })
            self.assertEqual([["AN-T-009", "AN-T-009@2"], [None, "AN-T-009@3-draft"]],
                             page.structured_content["rows"])
            inverse = await query(
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
            self.assertEqual(6, (await query("SELECT count(*) AS atoms FROM atoms"))["rows"][0][0])
        self.assertEqual(before, self._carrier_digests())

    async def test_ticket_asset_and_spec_draft_archive_tools(self):
        for number in (11, 12):
            self._write(f"01_draft/AN-S-{number:03d}@1-draft-SPEC-COMPONENT_CONTRACT--fixture.md",
                        f"AN-S-{number:03d}", "draft", 1, template="component_contract", lens="SPEC",
                        container={"component": "C0"}, structure_tier=1)
        async with (
            asyncio.timeout(25),
            stdio_client(StdioServerParameters(command=sys.executable, args=self.args)) as streams,
            ClientSession(*streams) as client,
        ):
            await client.initialize()
            asset = await client.call_tool("atom_lifecycle_create_asset", {"newAtom": {
                "template": "spec_proposal", "body": "## Summary\n\nExample proposal\n",
            }})
            self.assertEqual("completed", asset.structured_content["status"], asset.structured_content)
            saved = asset.structured_content["artifact"]
            self.assertEqual("in_queue", saved["status"])
            self.assertIn("/001_TICKETS/ASSETS/", saved["path"])
            selection = await client.call_tool("query_run", {
                "sql": 'SELECT reference, "header.state.version" FROM atoms '
                       "WHERE reference IN ('AN-S-011@1-draft', 'AN-S-012@1-draft') ORDER BY 1",
                "result_delivery": "inline",
            })
            targets = selection.structured_content["rows"]
            self.assertEqual([["AN-S-011@1-draft", 1], ["AN-S-012@1-draft", 1]], targets)
            archived = await client.call_tool("atom_lifecycle_archive", {"targets": targets})
            self.assertEqual("completed", archived.structured_content["status"], archived.structured_content)
            self.assertEqual(["AN-S-011@1", "AN-S-012@1"],
                             [row["artifact"]["ref_id"] for row in archived.structured_content["results"]])

    async def test_component_queries_use_declared_id_and_owned_spec_tiers(self):
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
        async with (
            asyncio.timeout(25),
            stdio_client(StdioServerParameters(command=sys.executable, args=self.args)) as streams,
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

    async def test_project_queries_include_all_current_atoms_at_selected_tier(self):
        self._write("AN-S-1428-axiom.md", "AN-S-1428", "active", 1, template="axiom", tier=-1)
        self._write("AN-S-1429-contract.md", "AN-S-1429", "active", 1, template=None, tier=0)
        self._write("AN-S-3190-principle.md", "AN-S-3190", "active", 1, template="applicable_principle", tier=2)
        self._write("AN-S-3038-manifest.md", "AN-S-3038", "active", 1, template="component_manifest", tier=0)
        self._write("AN-S-021-tier-one.md", "AN-S-021", "active", 1, template=None, tier=1)
        async with (
            asyncio.timeout(25),
            stdio_client(StdioServerParameters(command=sys.executable, args=self.args)) as streams,
            ClientSession(*streams) as client,
        ):
            await client.initialize()
            for template, expected in (
                ("fetch_contracts", ["AN-S-1429@1", "AN-S-3038@1"]),
                ("fetch_solutions", ["AN-S-021@1"]),
            ):
                result = await client.call_tool("query_template", {
                    "template": template, "component": "C0", "result_format": "json_matrix",
                })
                self.assertFalse(result.is_error, result.structured_content)
                self.assertEqual(expected, [row[0] for row in result.structured_content["rows"]])

    async def test_http_queries_native_projection_without_legacy_routes(self):
        from http_paths import HEALTH_PATH, MCP_PATH, WORKBENCH_PATH
        from http_server import create_app

        before = self._carrier_digests()
        app = create_app(self.root, native_inputs=_native_inputs(), control_root=CONTROL)
        async with app.starlette_app.router.lifespan_context(app.starlette_app):
            async with httpx2.AsyncClient(
                transport=httpx2.ASGITransport(app=app), base_url="http://127.0.0.1:18093",
            ) as http:
                health = await http.get(HEALTH_PATH, headers={"Accept": "text/html"})
                self.assertEqual({"ready": True}, health.json())
                for path in (f"{HEALTH_PATH}/workbench-restart", f"{HEALTH_PATH}/workbench-reread"):
                    self.assertEqual(404, (await http.post(path)).status_code)
                self.assertEqual(404, (await http.get(f"{WORKBENCH_PATH}/fixture")).status_code)
                self.assertEqual(421, (await http.get(HEALTH_PATH, headers={"Host": "example.com"})).status_code)
                async with streamable_http_client(
                    "http://127.0.0.1:18093" + MCP_PATH, http_client=http,
                ) as streams, ClientSession(*streams) as client:
                    await client.initialize()
                    self.assertTrue({"query_run", "query_page", "query_check", "query_schema", "workspace_open"} <=
                                    {tool.name for tool in (await client.list_tools()).tools})
                    schema = await client.call_tool("query_schema", {})
                    self.assertIn("native_references", schema.structured_content["tables"])
                    sql = "SELECT exact_ref FROM native_references WHERE exact_ref LIKE 'AN-T-%' ORDER BY exact_ref"
                    checked = await client.call_tool("query_check", {"sql": sql})
                    self.assertTrue(checked.structured_content["valid"])
                    first = await client.call_tool("query_run", {
                        "sql": sql, "page_size": 1, "result_delivery": "inline",
                    })
                    self.assertFalse(first.is_error, first.structured_content)
                    self.assertEqual([["AN-T-009@1"]], first.structured_content["rows"])
                    page = await client.call_tool("query_page", {
                        "query_id": first.structured_content["query_id"], "offset": 1,
                        "result_delivery": "inline",
                    })
                    self.assertFalse(page.is_error, page.structured_content)
                    self.assertEqual([["AN-T-009@2"], ["AN-T-009@3-draft"]],
                                     page.structured_content["rows"])
                    refused = await client.call_tool("workspace_get", {"workspace_id": "unavailable"})
                    self.assertTrue(refused.is_error)
        self.assertEqual(before, self._carrier_digests())

    def test_http_entrypoint_uses_native_selection(self):
        import server
        from http_server import main as http_main

        inputs = _native_inputs()
        args = ["--project-root", str(self.root), "--control-root", CONTROL]
        with patch("http_server.startup_selection", side_effect=AssertionError("legacy selection")), \
                patch("uvicorn.run") as run:
            self.assertIsNone(server.main(args + ["--transport", "streamable-http"], native_inputs=inputs))
            app = run.call_args.args[0]
            self.assertEqual(self.root, app.gateway.selection.root)
            self.assertIsNotNone(app.gateway._native_query)
        for main, extra in ((server.main, ["--transport", "streamable-http"]), (http_main, [])):
            with self.subTest(main=main), self.assertRaises(SystemExit):
                main(args + extra + ["--instance-id", "legacy"], native_inputs=inputs)

    def test_second_native_process_reports_project_lock_to_stderr(self):
        from native_query import create_native_gateway

        owner = create_native_gateway(self.root, CONTROL, _native_inputs())._native_query
        self.addCleanup(owner.close)
        owner.start()
        completed = subprocess.run([sys.executable, *self.args], input="", text=True,
                                   capture_output=True, timeout=15, check=False)
        self.assertEqual(2, completed.returncode, completed.stderr)
        self.assertEqual("", completed.stdout)
        self.assertIn("This Project is already open", completed.stderr)

    def test_startup_refuses_an_unapproved_manifest_owner(self):
        manifest_path = self.root / CONTROL / MANIFEST
        source = manifest_path.read_text(encoding="utf-8")
        manifest_path.write_text(source.replace("component: C0", "component: C1"), encoding="utf-8")
        result = subprocess.run([sys.executable, *self.args], input="", text=True,
                                capture_output=True, timeout=15, check=False)
        self.assertEqual(2, result.returncode, result.stderr)
        self.assertEqual("", result.stdout)
        diagnostic = json.loads(result.stderr.splitlines()[0])
        self.assertEqual("mcp.stdio_startup", diagnostic["operation"])
        self.assertEqual("ProjectSelectionError", diagnostic["exception_class"])


if __name__ == "__main__":
    raise SystemExit(_launch_server())
