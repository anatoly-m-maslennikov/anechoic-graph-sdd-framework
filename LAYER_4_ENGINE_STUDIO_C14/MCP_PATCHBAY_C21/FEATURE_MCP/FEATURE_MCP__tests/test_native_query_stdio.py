"""Exercise the existing MCP stdio entry point with native Workbench."""

import asyncio
import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import httpx2
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
from mcp.client.streamable_http import streamable_http_client
import yaml


MCP = Path(__file__).resolve().parents[1]
PROGRAMMATIC = MCP.parents[1] / "FEATURE_PROGRAMMATIC"

from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared import validate_manifest  # noqa: E402
from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared import extension_directory, polling_source_watcher  # noqa: E402

from .native_query_behavior_cases import NativeQueryBehaviorCases
from .native_query_test_support import create_native_gateway


CONTROL = ".anechoic_anechoic"
MANIFEST = "AN-S-001-PROJECT_MANIFEST--declare-anechoic.md"
OLD_PATH = ".anechoic_legacy/03_plan/CA-P-9--old-task.md"
UNNUMBERED_PATH = ".anechoic_legacy/03_plan/archive/old-task.md"
STAGING_COPY_PATH = "migration-evidence/03_plan/old-task-copy.md"


def _native_inputs():
    from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import NativeQueryInputs

    return NativeQueryInputs(
        validate_manifest=validate_manifest,
        relation_types=frozenset({"CONTAINED_BY", "CONTAINS"}),
        inverses={"CONTAINED_BY": "CONTAINS"},
        extension_directory=extension_directory(MCP.parents[2]),
        ticket_labels=("Task", "Subtask", "Sub-epic", "Epic", "Version"),
    )


def _launch_server():
    from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import server_main
    with polling_source_watcher():
        return server_main(sys.argv[1:], gateway_factory=lambda root, control: create_native_gateway(root, control, _native_inputs()))


class NativeJournalOwnershipTests(unittest.TestCase):
    def test_rejects_journal_outside_selected_control(self):
        from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import NativeQueryOwner

        with tempfile.TemporaryDirectory() as root:
            for journal in ("_anechoic_other/_journal", ".anechoic_other/_journal"):
                selection = SimpleNamespace(root=Path(root).resolve(), control_relative=Path("_anechoic_anechoic"),
                                            parameters={"paths": {"journal_root": journal}})
                with self.subTest(journal=journal), self.assertRaisesRegex(ValueError, "another records tree"):
                    NativeQueryOwner(selection, None)
            selection.parameters["paths"]["journal_root"] = "elsewhere/journal"
            with patch("KERNEL_MIXER_C59.native_query_runtime.SavedQueryStore") as saved, \
                    patch("KERNEL_MIXER_C59.native_query_runtime.WorkspaceStore"), \
                    patch("KERNEL_MIXER_C59.native_query_runtime.QueryLog"):
                NativeQueryOwner(selection, None)
                self.assertEqual("elsewhere/journal", saved.call_args.kwargs["journal_root"])

class NativeQueryStdioTests(NativeQueryBehaviorCases, unittest.IsolatedAsyncioTestCase):
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
        self._write("001_TICKETS/TASKS/AN-T-009-TASK--verify-runtime.md", "AN-T-009", "active", 2,
                    body="## Summary\n\nVerify the operator's runtime.\n")
        self._write("001_TICKETS/TASKS/archived/AN-T-009@1-TASK--verify-runtime.md", "AN-T-009", "archived", 1)
        self._write("001_TICKETS/TASKS/draft/AN-T-009@3-draft-TASK--verify-runtime.md", "AN-T-009", "draft", 3)
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
        self.args = ["-B", "-P", "-m", "MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__tests.test_native_query_stdio", "--project-root", str(self.root), "--control-root", CONTROL]

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
            from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import canonical_native_header

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
            stdio_client(StdioServerParameters(command=sys.executable, args=self.args, env={"PYTHONPATH": str(MCP.parents[1])})) as streams,
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













    async def test_ticket_asset_and_spec_draft_archive_tools(self):
        for number in (11, 12):
            self._write(f"01_draft/AN-S-{number:03d}@1-draft-SPEC-COMPONENT_CONTRACT--fixture.md",
                        f"AN-S-{number:03d}", "draft", 1, template="component_contract", lens="SPEC",
                        container={"component": "C0"}, structure_tier=1)
        async with (
            asyncio.timeout(25),
            stdio_client(StdioServerParameters(command=sys.executable, args=self.args, env={"PYTHONPATH": str(MCP.parents[1])})) as streams,
            ClientSession(*streams) as client,
        ):
            await client.initialize()
            asset = await client.call_tool("atom_lifecycle_create_asset", {"newAtom": {
                "template": "spec_proposal", "body": "## Summary\n\nExample proposal\n",
            }})
            self.assertEqual("completed", asset.structured_content["status"], asset.structured_content)
            saved = asset.structured_content["artifact"]
            self.assertEqual("in_queue", saved["status"])
            self.assertIn("/__TICKETS/ASSETS/", saved["path"])
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



    async def test_project_queries_include_only_solutions_at_tier_zero(self):
        self._write("AN-S-1428-axiom.md", "AN-S-1428", "active", 1, template="axiom", tier=-1)
        self._write("AN-S-1429-contract.md", "AN-S-1429", "active", 1, template="solution", tier=0)
        self._write("AN-S-3190-principle.md", "AN-S-3190", "active", 1, template="applicable_principle", tier=2)
        self._write("AN-S-3038-manifest.md", "AN-S-3038", "active", 1, template="component_manifest", tier=0)
        self._write("AN-S-021-tier-one.md", "AN-S-021", "active", 1, template=None, tier=1)
        async with (
            asyncio.timeout(25),
            stdio_client(StdioServerParameters(command=sys.executable, args=self.args, env={"PYTHONPATH": str(MCP.parents[1])})) as streams,
            ClientSession(*streams) as client,
        ):
            await client.initialize()
            for template, expected in (
                ("fetch_contracts", []),
                ("fetch_solutions", ["AN-S-1429@1"]),
            ):
                result = await client.call_tool("query_template", {
                    "template": template, "component": "C0", "result_format": "json_matrix",
                })
                self.assertFalse(result.is_error, result.structured_content)
                self.assertEqual(expected, [row[0] for row in result.structured_content["rows"]])

    async def test_http_queries_native_projection_without_legacy_routes(self):
        from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import HEALTH_PATH, MCP_PATH, WORKBENCH_PATH
        from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import create_http_app as create_app

        before = self._carrier_digests()
        app = create_app(self.root, gateway_factory=lambda root, control: create_native_gateway(root, control, _native_inputs()), control_root=CONTROL)
        async with app.starlette_app.router.lifespan_context(app.starlette_app):
            async with httpx2.AsyncClient(
                transport=httpx2.ASGITransport(app=app), base_url="http://127.0.0.1:18093",
            ) as http:
                health = await http.get(HEALTH_PATH, headers={"Accept": "text/html"})
                self.assertEqual({"state": "ready"}, health.json())
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
        from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import http_main, server_main

        inputs = _native_inputs()
        factory = lambda root, control: create_native_gateway(root, control, inputs)
        args = ["--project-root", str(self.root), "--control-root", CONTROL]
        with patch("MCP_PATCHBAY_C21.FEATURE_MCP.http_server.startup_selection", side_effect=AssertionError("legacy selection")), \
                patch("uvicorn.run") as run:
            self.assertIsNone(server_main(args + ["--transport", "streamable-http"], gateway_factory=factory))
            app = run.call_args.args[0]
            self.assertEqual(self.root, app.gateway.selection.root)
            self.assertIsNotNone(app.gateway._native_query)
        for main, extra in ((server_main, ["--transport", "streamable-http"]), (http_main, [])):
            for selector in (["--instance-id", "legacy"], ["--host-project-root", str(self.root)]):
                with self.subTest(main=main, selector=selector), self.assertRaises(SystemExit):
                    main(args + extra + selector, gateway_factory=factory)
            with self.subTest(main=main, selector="missing control"), self.assertRaises(SystemExit):
                main(["--project-root", str(self.root), *extra], gateway_factory=factory)

    def test_second_native_process_reports_project_lock_to_stderr(self):
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
        self.assertIn("mcp_stdio_startup_failed", result.stderr)
        self.assertIn("anechoic: operation failed", result.stderr)


if __name__ == "__main__":
    raise SystemExit(_launch_server())
