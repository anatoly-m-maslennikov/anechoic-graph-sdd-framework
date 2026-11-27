"""Exercise native family lifecycle writes through a disposable Beta MCP process."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
from time import monotonic
import unittest

import yaml

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

from .test_beta_mcp_process import ENGINE, _stage
from .FEATURE_MCP__tests__shared import ONTOLOGY, project as make_project


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
            lens = "_DES/AN-S-2272-DES--declare-evaluation-decision-form.md"
            source = (ENGINE.parent / "_anechoic_anechoic/000_ANECHOIC_framework/SUPERLAYER_1_METHODOLOGY_SOURCES"
                      / "LAYER_1_META_ONTOLOGY_C9/__DES" / Path(lens).name)
            shutil.copy2(source, control / ONTOLOGY / lens)
            source = ENGINE.parent / "_anechoic_anechoic/__PROJECT_CONFIG/AN-P-63-ACTION--author-atom-content-before-summary.md"
            shutil.copy2(source, control / "__PROJECT_CONFIG" / source.name)
            parameters = StdioServerParameters(command=sys.executable, args=[
                "-B", "-P", "-m", "MCP_PATCHBAY_C21.FEATURE_MCP.server", "--project-root", str(project),
            ], cwd=engine.parent, env={"PYTHONPATH": str(engine), "ANECHOIC_RUNTIME_STACK": "beta_next",
                "ANECHOIC_RUNTIME_PROFILE": "test",
                "ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY": os.environ.get("ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY",
                    str(ENGINE.parent / ".anechoic_tmp/workbench/extensions"))})
            async with stdio_client(parameters) as streams, ClientSession(*streams) as client:
                await client.initialize()

                await self._spec(client)
                await self._component_contract(client)
                await self._config(client, source)

    async def test_task_revision_promotion(self):
        with TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            engine = _stage(root / "framework")
            project = root / "project"
            project.mkdir()
            subprocess.run(["git", "init", "--quiet", str(project)], check=True)
            make_project(project)
            control = project / "_anechoic_anechoic"
            task = (
                control / "__TICKETS/TASKS/AN-T-9999-TASK--promotion-canary.md"
            )
            contract = (
                control
                / "AN-S-9998-SPEC-PROJECT_CONTRACT--promotion-canary.md"
            )
            contract.write_text(
                "---\natom_family: SPEC\natom_id: AN-S-9998\ncontainer: {component: C00}\n"
                "tier: 0\ncontext: {template: project_contract, lens: SPEC}\n"
                "state: {status: active, version: 1, updated_at: '2026-11-19T00:00:00Z'}\n---\n"
                "\n## Summary\n\nPromotion canary\n\n## Guarantee\n\nThe Task can be promoted.\n")
            task.parent.mkdir(parents=True)
            task.write_text("---\natom_family: TKT\natom_id: AN-T-9999\ncontainer: {component: C00}\n"
                "priority: 2\nrelations: {IS_SOLUTION_FOR: [AN-S-9998]}\ncontext: {template: task}\n"
                "state: {status: in_queue, version: 1, updated_at: '2026-11-19T00:00:00Z'}\n---\n"
                "\n## Summary\n\nPromotion canary\n\n## Work\n\nOld work.\n")
            parameters = StdioServerParameters(command=sys.executable, args=[
                "-B", "-P", "-m", "MCP_PATCHBAY_C21.FEATURE_MCP.server", "--project-root", str(project),
            ], cwd=engine.parent, env={"PYTHONPATH": str(engine), "ANECHOIC_RUNTIME_STACK": "beta_next",
                "ANECHOIC_RUNTIME_PROFILE": "test",
                "ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY": os.environ.get("ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY",
                    str(ENGINE.parent / ".anechoic_tmp/workbench/extensions"))})
            async with stdio_client(parameters) as streams, ClientSession(*streams) as client:
                await client.initialize()
                await self._promotion(client, project, task)

    async def _call(self, client, name, arguments, status):
        witness = """SELECT count(DISTINCT run_id) FILTER (WHERE t.name = 'lifecycle_refresh' AND e.kind = 'native_delta'),
                    count(DISTINCT run_id) FILTER (WHERE e.kind IN ('full', 'graph_refresh', 'native_refresh'))
                    FROM flow_events t JOIN (
                        SELECT run_id, json_extract_string(detail, '$.kind') AS kind
                        FROM flow_events WHERE kind = 'output' AND name = 'generation_result'
                            AND outcome = 'succeeded'
                    ) e USING (run_id)
            WHERE t.component = 'C68' AND t.kind = 'trigger'"""
        before = await client.call_tool(
            "query_run", {"sql": witness, "result_delivery": "inline"}
        )
        started = monotonic()
        reply = await client.call_tool(name, arguments)
        self.assertFalse(reply.is_error, reply.structured_content)
        self.assertEqual(
            status,
            reply.structured_content["status"],
            reply.structured_content,
        )
        print(f"{name}: {monotonic() - started:.3f}s", flush=True)
        after = await client.call_tool(
            "query_run", {"sql": witness, "result_delivery": "inline"}
        )
        self.assertFalse(after.is_error, after.structured_content)
        delta, refresh = before.structured_content["rows"][0]
        self.assertEqual(
            [[delta + 1, refresh]], after.structured_content["rows"]
        )
        return reply.structured_content

    async def _rows(self, client, atom):
        reply = await client.call_tool(
            "query_run",
            {
                "sql": 'SELECT reference, "header.state.version", "header.state.status" FROM atoms '
                f"WHERE reference = '{atom}' OR reference LIKE '{atom}@%' "
                'ORDER BY "header.state.version", reference',
                "result_delivery": "inline",
            },
        )
        self.assertFalse(reply.is_error, reply.structured_content)
        return reply.structured_content["rows"]

    async def _promotion(self, client, project, source):
        before = source.read_text()
        body = before.split("---", 2)[2][1:].replace("Old work.", "New work.")
        revised = await self._call(client, "atom_lifecycle_update", {
            "sourceCurrent": {"ref_id": "AN-T-9999", "version": 1},
            "changes": {"body": body}}, "draft_created")
        draft = revised["savedDraft"]
        draft_path = project / draft["path"]
        draft_text = draft_path.read_text()
        old_header = self._header(before)
        draft_header = self._header(draft_text)
        self.assertEqual({k: v for k, v in old_header.items() if k != "state"},
                         {k: v for k, v in draft_header.items() if k != "state"})
        self.assertEqual(body, draft_text.split("---", 2)[2][1:])
        self.assertNotEqual(old_header["state"]["updated_at"], draft_header["state"]["updated_at"])
        self.assertEqual([["AN-T-9999", 1, "in_queue"], [draft["ref_id"], 2, "draft"]],
                         await self._rows(client, "AN-T-9999"))
        snapshot = await self._snapshot(client)
        invalid = await client.call_tool("atom_lifecycle_promote_draft", {
            "target": {"ref_id": draft["ref_id"], "version": 2}, "targetStatus": "in_queue"})
        self.assertFalse(invalid.is_error, invalid.structured_content)
        self.assertEqual("failed", invalid.structured_content["status"], invalid.structured_content)
        self.assertEqual("invalid_input", invalid.structured_content["errors"][0]["code"])
        self.assertEqual([], invalid.structured_content["effects"])
        self.assertEqual([["AN-T-9999", 1, "in_queue"], [draft["ref_id"], 2, "draft"]],
                         await self._rows(client, "AN-T-9999"))
        self.assertEqual(snapshot, await self._snapshot(client))
        self.assertEqual(before, source.read_text())
        self.assertEqual(draft_text, draft_path.read_text())
        promoted = await self._call(client, "atom_lifecycle_promote_draft", {
            "target": {"ref_id": draft["ref_id"], "version": 2}, "targetStatus": "backlog"}, "completed")
        current = project / promoted["artifact"]["path"]
        archive = source.parent / "09_archived/AN-T-9999@1-TASK--promotion-canary.md"
        self.assertFalse(source.exists())
        self.assertFalse(draft_path.exists())
        self._compare_carrier(before, archive.read_text(), "archived")
        self._compare_carrier(draft_text, current.read_text(), "backlog")
        self.assertEqual([["AN-T-9999@1", 1, "archived"], ["AN-T-9999", 2, "backlog"]],
                         await self._rows(client, "AN-T-9999"))
        relation = await client.call_tool("query_run", {"sql": "SELECT target_ref FROM relations "
            "WHERE source_ref = 'AN-T-9999' AND relation_type = 'IS_SOLUTION_FOR' AND NOT derived",
            "result_delivery": "inline"})
        self.assertEqual([["AN-S-9998"]], relation.structured_content["rows"])
        self._lean_headers(project / "_anechoic_anechoic", [before, draft_text,
                                                           archive.read_text(), current.read_text()])

    async def _snapshot(self, client):
        results = []
        for sql in (
            "SELECT * FROM atoms WHERE reference LIKE 'AN-T-9999%' ORDER BY reference",
            "SELECT * FROM relations WHERE source_ref LIKE 'AN-T-9999%' ORDER BY source_ref, target_ref",
        ):
            result = await client.call_tool(
                "query_run", {"sql": sql, "result_delivery": "inline"}
            )
            self.assertFalse(result.is_error, result.structured_content)
            results.append(result.structured_content["rows"])
        return results

    def _lean_headers(self, control, carriers):
        observations = []
        for carrier in carriers:
            header = self._header(carrier)
            observations.append({"family": header["atom_family"],
                "model_class": "Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Ticket",
                "status": header["state"]["status"],
                "tier": header.get("tier"), "priority": header.get("priority")})
        module = ("FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51.FEATURE_FORMAL_MODEL_GENERATOR."
                  "manifest_compiler_CS1.manifest_compiler_CS1__tests.functional.model_lean_pilot")
        env = {**os.environ, "PYTHONPATH": str(ENGINE)}
        result = subprocess.run([sys.executable, "-B", "-P", "-m", module, str(control), str(control / ONTOLOGY)],
            input=json.dumps(observations), text=True, capture_output=True, env=env, timeout=120)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def _header(self, text):
        header = text.split("---", 2)[1]
        node = yaml.compose(header)
        states = [value for key, value in node.value if key.value == "state"]
        self.assertEqual(1, len(states))
        self.assertIsInstance(states[0], yaml.MappingNode)
        statuses = [
            value for key, value in states[0].value if key.value == "status"
        ]
        self.assertEqual(1, len(statuses))
        self.assertIsInstance(statuses[0], yaml.ScalarNode)
        return yaml.safe_load(header)

    def _compare_carrier(self, before, after, status):
        _, _, old_body = before.split("---", 2)
        _, _, new_body = after.split("---", 2)
        old, new = self._header(before), self._header(after)
        old["state"]["status"] = status
        self.assertEqual(old, new)
        self.assertEqual(old_body, new_body)

    async def _spec(self, client):
        created = await self._call(
            client,
            "atom_lifecycle_create_draft",
            {
                "newAtom": {
                    "template": "axiom",
                    "container": {"component": "C00"},
                    "lens": "SPEC",
                    "body": "## Summary\n\nBeta Spec canary.\n",
                }
            },
            "completed",
        )
        draft = created["savedDraft"]
        atom = draft["atom_id"]
        self.assertEqual(
            [[draft["ref_id"], 1, "draft"]], await self._rows(client, atom)
        )
        await self._call(
            client,
            "atom_lifecycle_promote_draft",
            {
                "target": {"ref_id": draft["ref_id"], "version": 1},
                "targetStatus": "ready",
            },
            "completed",
        )
        self.assertEqual([[atom, 1, "ready"]], await self._rows(client, atom))
        await self._call(
            client,
            "atom_lifecycle_change_status",
            {
                "target": {"ref_id": atom, "version": 1},
                "targetStatus": "active",
            },
            "completed",
        )
        self.assertEqual([[atom, 1, "active"]], await self._rows(client, atom))

    async def _component_contract(self, client):
        reply = await client.call_tool(
            "atom_lifecycle_create_draft",
            {
                "newAtom": {
                    "template": "component_contract",
                    "container": {"component": "C9"},
                    "lens": "DES",
                    "body": "## Summary\n\nBeta Component contract canary.\n\n## Guarantee\n\nThe canary works.\n",
                }
            },
        )
        result = reply.structured_content
        self.assertEqual("failed", result["status"], result)
        self.assertEqual([], result["effects"], result)
        self.assertEqual("invalid_input", result["errors"][0]["code"])
        self.assertEqual(
            "Add the Component Contract to the Component Manifest.",
            result["errors"][0]["message"],
        )

    async def _config(self, client, source):
        body = (
            source.read_text(encoding="utf-8").split("---", 2)[2]
            + "\nBeta config canary.\n"
        )
        revised = await self._call(
            client,
            "atom_lifecycle_update",
            {
                "sourceCurrent": {"ref_id": "AN-P-63", "version": 16},
                "changes": {"body": body},
            },
            "draft_created",
        )
        config = revised["savedDraft"]
        self.assertEqual(
            [["AN-P-63", 16, "active"], [config["ref_id"], 17, "draft"]],
            await self._rows(client, "AN-P-63"),
        )
        await self._call(
            client,
            "atom_lifecycle_promote_draft",
            {
                "target": {"ref_id": config["ref_id"], "version": 17},
                "targetStatus": "active",
            },
            "completed",
        )
        self.assertEqual(
            [["AN-P-63@16", 16, "archived"], ["AN-P-63", 17, "active"]],
            await self._rows(client, "AN-P-63"),
        )
