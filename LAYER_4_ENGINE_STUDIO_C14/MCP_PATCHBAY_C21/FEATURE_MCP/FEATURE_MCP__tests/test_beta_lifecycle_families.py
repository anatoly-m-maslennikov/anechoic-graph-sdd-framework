"""Exercise native family lifecycle writes through a disposable Beta MCP process."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
from time import monotonic
import unittest

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

from .test_beta_mcp_process import ENGINE, _stage
from .FEATURE_MCP__tests__shared import project as make_project


class BetaLifecycleFamilies(unittest.IsolatedAsyncioTestCase):
    async def test_spec_and_project_config(self):
        with TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            engine = _stage(root / "framework")
            project = root / "project"
            project.mkdir()
            subprocess.run(["git", "init", "--quiet", str(project)], check=True)
            make_project(project)
            control = project / "_anechoic_anechoic"
            source = ENGINE.parent / "_anechoic_anechoic/__PROJECT_CONFIG/AN-P-63-ACTION--author-atom-content-before-summary.md"
            shutil.copy2(source, control / "__PROJECT_CONFIG" / source.name)
            parameters = StdioServerParameters(command=sys.executable, args=[
                "-B", "-P", "-m", "MCP_PATCHBAY_C21.FEATURE_MCP.server", "--project-root", str(project),
            ], cwd=engine.parent, env={"PYTHONPATH": str(engine), "ANECHOIC_RUNTIME_STACK": "beta", "ANECHOIC_RUNTIME_PROFILE": "test",
                "ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY": os.environ.get("ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY",
                    str(ENGINE.parent / ".anechoic_tmp/workbench/extensions"))})
            async with stdio_client(parameters) as streams, ClientSession(*streams) as client:
                await client.initialize()

                await self._spec(client)
                await self._component_contract(client)
                await self._config(client, source)

    async def _call(self, client, name, arguments, status):
        witness = """SELECT count(DISTINCT run_id) FILTER (WHERE t.name = 'lifecycle_refresh' AND e.kind = 'native_delta'),
                    count(DISTINCT run_id) FILTER (WHERE e.kind IN ('full', 'graph_refresh', 'native_refresh'))
                    FROM flow_events t JOIN (
                        SELECT run_id, json_extract_string(detail, '$.kind') AS kind
                        FROM flow_events WHERE kind = 'output' AND name = 'generation_result'
                            AND outcome = 'succeeded'
                    ) e USING (run_id)
            WHERE t.component = 'C68' AND t.kind = 'trigger'"""
        before = await client.call_tool("query_run", {"sql": witness, "result_delivery": "inline"})
        started = monotonic()
        reply = await client.call_tool(name, arguments)
        self.assertFalse(reply.is_error, reply.structured_content)
        self.assertEqual(status, reply.structured_content["status"], reply.structured_content)
        print(f"{name}: {monotonic() - started:.3f}s", flush=True)
        after = await client.call_tool("query_run", {"sql": witness, "result_delivery": "inline"})
        self.assertFalse(after.is_error, after.structured_content)
        delta, refresh = before.structured_content["rows"][0]
        self.assertEqual([[delta + 1, refresh]], after.structured_content["rows"])
        return reply.structured_content

    async def _rows(self, client, atom):
        reply = await client.call_tool("query_run", {"sql":
            'SELECT reference, "header.state.version", "header.state.status" FROM atoms '
            f"WHERE reference = '{atom}' OR reference LIKE '{atom}@%' "
            'ORDER BY "header.state.version", reference', "result_delivery": "inline"})
        self.assertFalse(reply.is_error, reply.structured_content)
        return reply.structured_content["rows"]

    async def _spec(self, client):
        created = await self._call(client, "atom_lifecycle_create_draft", {"newAtom": {
            "template": "axiom", "container": {"component": "C00"}, "lens": "SPEC",
            "body": "## Summary\n\nBeta Spec canary.\n"}}, "completed")
        draft = created["savedDraft"]
        atom = draft["atom_id"]
        self.assertEqual([[draft["ref_id"], 1, "draft"]], await self._rows(client, atom))
        await self._call(client, "atom_lifecycle_promote_draft", {"target": {"ref_id": draft["ref_id"],
            "version": 1}, "targetStatus": "ready"}, "completed")
        self.assertEqual([[atom, 1, "ready"]], await self._rows(client, atom))
        await self._call(client, "atom_lifecycle_change_status", {"target": {"ref_id": atom, "version": 1},
            "targetStatus": "active"}, "completed")
        self.assertEqual([[atom, 1, "active"]], await self._rows(client, atom))

    async def _component_contract(self, client):
        component = await self._call(client, "atom_lifecycle_create_draft", {"newAtom": {
            "template": "component_contract", "container": {"component": "C9"}, "lens": "DES",
            "body": "## Summary\n\nBeta Component contract canary.\n\n## Guarantee\n\nThe canary works.\n"}}, "completed")
        component = component["savedDraft"]
        self.assertEqual([[component["ref_id"], 1, "draft"]], await self._rows(client, component["atom_id"]))
        await self._call(client, "atom_lifecycle_promote_draft", {"target": {"ref_id": component["ref_id"],
            "version": 1}, "targetStatus": "ready"}, "completed")
        self.assertEqual([[component["atom_id"], 1, "ready"]], await self._rows(client, component["atom_id"]))

    async def _config(self, client, source):
        body = source.read_text(encoding="utf-8").split("---", 2)[2] + "\nBeta config canary.\n"
        revised = await self._call(client, "atom_lifecycle_update", {"sourceCurrent": {"ref_id": "AN-P-63", "version": 16},
            "changes": {"body": body}}, "draft_created")
        config = revised["savedDraft"]
        self.assertEqual([["AN-P-63", 16, "active"], [config["ref_id"], 17, "draft"]], await self._rows(client, "AN-P-63"))
        await self._call(client, "atom_lifecycle_promote_draft", {"target": {"ref_id": config["ref_id"],
            "version": 17}, "targetStatus": "active"}, "completed")
        self.assertEqual([["AN-P-63@16", 16, "archived"], ["AN-P-63", 17, "active"]], await self._rows(client, "AN-P-63"))
