"""Exercise the existing MCP stdio entry point with a native startup snapshot."""

import asyncio
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from types import ModuleType
import unittest
from unittest.mock import patch

import httpx2
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
from mcp.client.streamable_http import streamable_http_client
import yaml


MCP = Path(__file__).resolve().parents[1]
PROGRAMMATIC = MCP.parent
APP_TESTS = PROGRAMMATIC / "FEATURE_APPS" / "APP_WORKBENCH" / "tests"
sys.path[:0] = [str(MCP), str(PROGRAMMATIC), str(PROGRAMMATIC / "FEATURE_TOOLS"), str(APP_TESTS)]

from smalltest_support import extension_directory  # noqa: E402


CONTROL = ".anechoic_anechoic"
MANIFEST = "SPEC/AN-S-001-PROJECT_MANIFEST--declare-anechoic.md"
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
        migration_refs=(
            ("CA-P-9@2", OLD_PATH, "AN-T-009@2"),
            (None, UNNUMBERED_PATH, "AN-T-009@1"),
            (None, STAGING_COPY_PATH, "AN-T-009@1"),
        ),
        extension_directory=extension_directory(MCP.parents[2]),
    )


def _launch_server():
    from server import main
    return main(sys.argv[1:], native_inputs=_native_inputs())


class NativeQueryStdioTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
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
        self._write("__TKT/TASKS/AN-T-009-TASK--verify-runtime.md", "AN-T-009", "active", 2)
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

    def _write(self, relative, atom_id, status, version, *, template="task", body="## Summary\n\nFixture.\n"):
        path = self.root / CONTROL / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        metadata = {
            "identity": {"atom_id": atom_id},
            "context": {"container": {"component": "C0"}, "template": template,
                        "tier": -1 if template == "project_manifest" else 0},
            "state": {"version": version, "status": status, "updated_at": "2026-11-19T00:00:00Z"},
        }
        path.write_text(f"---\n{yaml.safe_dump(metadata)}---\n\n{body}", encoding="utf-8")

    def _carrier_digests(self):
        return {path.relative_to(self.root): hashlib.sha256(path.read_bytes()).hexdigest()
                for path in self.root.rglob("*") if path.is_file()
                and path.relative_to(self.root).parts[0] != ".anechoic_runtime"}

    async def test_queries_the_native_tree_and_keeps_legacy_inputs_unchanged(self):
        before = self._carrier_digests()
        async with (
            asyncio.timeout(25),
            stdio_client(StdioServerParameters(command=sys.executable, args=self.args)) as streams,
            ClientSession(*streams) as client,
        ):
            initialized = await client.initialize()
            self.assertIsNone(initialized.capabilities.resources)
            tools = {tool.name: tool for tool in (await client.list_tools()).tools}
            self.assertTrue({"query_run", "query_page", "query_check", "query_schema", "workspace_open"} <= set(tools))
            schema = await client.call_tool("query_schema", {})
            self.assertFalse(schema.is_error, schema.structured_content)
            tables = schema.structured_content["tables"]
            self.assertEqual({"atoms", "relations", "native_references", "native_legacy_references",
                              "native_migration_paths"}, set(tables))
            self.assertEqual(["original_path", "exact_ref"],
                             [column["name"] for column in tables["native_migration_paths"]])

            async def query(sql, **options):
                response = await client.call_tool("query_run", {
                    "sql": sql, "result_delivery": "inline", "project_root": str(self.root), **options,
                })
                self.assertFalse(response.is_error, response.structured_content)
                return response.structured_content

            sql = ("SELECT stable_ref, exact_ref FROM native_references "
                   "WHERE exact_ref LIKE 'AN-T-%' ORDER BY exact_ref")
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
            legacy = await query("SELECT exact_ref FROM native_legacy_references WHERE original_path = "
                                 f"'{OLD_PATH}' AND legacy_ref = 'CA-P-9@2'")
            self.assertEqual([["AN-T-009@2"]], legacy["rows"])
            paths = await query("SELECT original_path, exact_ref FROM native_migration_paths ORDER BY original_path")
            self.assertEqual([[OLD_PATH, "AN-T-009@2"], [UNNUMBERED_PATH, "AN-T-009@1"],
                              [STAGING_COPY_PATH, "AN-T-009@1"]], paths["rows"])
            legacy_paths = await query("SELECT original_path FROM native_legacy_references")
            self.assertEqual([[OLD_PATH]], legacy_paths["rows"])
            for name, arguments in (
                ("query_run", {"sql": "SELECT 1", "project_root": str(self.root.parent)}),
                ("query_run", {"sql": "SELECT 1", "save": "yes"}),
                ("query_run", {"sql": "DELETE FROM atoms"}),
                ("workspace_get", {"workspace_id": "unavailable"}),
            ):
                with self.subTest(name=name, arguments=arguments):
                    refused = await client.call_tool(name, arguments)
                    self.assertTrue(refused.is_error)
            self.assertEqual(5, (await query("SELECT count(*) AS atoms FROM atoms"))["rows"][0][0])
        self.assertEqual(before, self._carrier_digests())

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
