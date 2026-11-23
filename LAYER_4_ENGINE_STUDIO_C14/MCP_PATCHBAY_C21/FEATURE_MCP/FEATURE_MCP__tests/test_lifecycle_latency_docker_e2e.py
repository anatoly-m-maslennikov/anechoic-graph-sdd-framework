"""Measure successful single-Atom transitions against the candidate image."""

import asyncio
import json
from math import ceil
from pathlib import Path
import shutil
from statistics import median
from time import monotonic
import unittest

from mcp.client.session import ClientSession

from .FEATURE_MCP__tests__shared import ROOT
from .native_import_graph_docker_cases import archive_project
from .workbench_docker_support import image_mcp_transport
from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import MCP_PATH


TRIALS = 50
SUMMARY = "## Summary\n\nMeasure lifecycle latency.\n"
CONTRACT = SUMMARY + "\n## Guarantee\n\nReturn a result.\n"
GENERATIONS = """SELECT json_extract_string(detail, '$.kind'), count(*)
    FROM flow_events WHERE component = 'C68' AND name = 'generation_result'
      AND outcome = 'succeeded' GROUP BY 1"""


def target(ref, version=1):
    return {"ref_id": ref, "version": version}


def prepare_project(root):
    shutil.copytree(Path(__file__).with_name("assets") / "lifecycle_latency", root, dirs_exist_ok=True)
    ontology = Path("_anechoic_anechoic/LAYER_1_META_ONTOLOGY_C9")
    source = ROOT / ontology
    for atom in ("AN-S-1928", "AN-S-1834", "AN-S-1831"):
        original, = source.rglob(f"{atom}-DOM-*.md")
        path = root / ontology / original.relative_to(source)
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(original, path)


def operation_metrics(label, samples):
    ordered = sorted(samples)
    return {
        "operation": label,
        "trials": len(samples),
        "p50_ms": round(median(ordered), 3),
        **{f"p{p}_ms": round(ordered[ceil(p * len(ordered) / 100) - 1], 3)
           for p in (10, 90, 95)},
        "max_ms": round(ordered[-1], 3),
        "samples_ms": [round(sample, 3) for sample in samples],
    }


class LifecycleLatencyImageTest(unittest.TestCase):
    def test_single_atom_lifecycle_latency(self):
        with archive_project(self, prepare_project) as project:
            report = asyncio.run(self._measure(project.url + MCP_PATH))
        print("ANECHOIC_TEST_METRICS " + json.dumps({"lifecycle_latency": report}), flush=True)

    async def _measure(self, endpoint):
        async with image_mcp_transport(endpoint) as streams, ClientSession(*streams) as client:
            await client.initialize()
            initial_atoms = (await self._sql(client, "SELECT count(*) FROM atoms"))[0][0]
            before = dict(await self._sql(client, GENERATIONS))
            samples = {}
            for _ in range(TRIALS):
                await self._task(client, samples)
                await self._asset(client, samples)
                await self._contract(client, samples)
            after = dict(await self._sql(client, GENERATIONS))
        self.assertEqual(13, len(samples))
        self.assertTrue(all(len(values) == TRIALS for values in samples.values()))
        expected = before | {"native_delta": before.get("native_delta", 0) + 13 * TRIALS}
        self.assertEqual(expected, after, "Lifecycle trials must use only incremental admission")
        return {
            "initial_atoms": initial_atoms,
            "measurement": "MCP request to SQL readback",
            "operations": [operation_metrics(label, times) for label, times in samples.items()],
        }

    async def _sql(self, client, query):
        reply = await client.call_tool("query_run", {"sql": query, "result_delivery": "inline"})
        self.assertFalse(reply.is_error, reply.structured_content)
        return reply.structured_content["rows"]

    async def _run(self, client, samples, label, operation, arguments, status, exact=None):
        started = monotonic()
        reply = await client.call_tool(f"atom_lifecycle_{operation}", arguments)
        receipt = reply.structured_content
        self.assertFalse(reply.is_error, receipt)
        self.assertIn(receipt["status"], ("completed", "draft_created"), receipt)
        if exact is None:
            exact = (receipt.get("savedDraft") or receipt["artifact"])["ref_id"]
        self.assertRegex(exact, r"\AAN-[TS]-[0-9]+(?:@[1-9][0-9]*(?:-draft)?)?\Z")
        rows = await self._sql(client, f"""SELECT n.exact_ref, a."header.state.status"
            FROM atoms a JOIN native_references n USING (reference)
            WHERE n.exact_ref = '{exact}' OR n.reference = '{exact}'""")
        elapsed_ms = (monotonic() - started) * 1000
        self.assertEqual(1, len(rows), (label, receipt, rows))
        self.assertEqual(exact if "@" in exact else f"{exact}@1", rows[0][0], receipt)
        self.assertEqual(status, rows[0][1], (label, receipt, rows))
        samples.setdefault(label, []).append(elapsed_ms)
        return rows[0][0]

    async def _task(self, client, samples):
        draft = await self._run(client, samples, "Create Task Draft", "create_draft", {"newAtom": {
            "template": "task", "container": {"component": "C00"}, "body": SUMMARY,
        }}, "draft")
        atom = draft.split("@")[0]
        await self._run(client, samples, "Publish Task Draft", "promote_draft", {
            "target": target(draft), "targetStatus": "backlog",
        }, "backlog", f"{atom}@1")
        await self._run(client, samples, "Queue Task", "change_status", {
            "target": target(atom), "targetStatus": "in_queue",
        }, "in_queue", f"{atom}@1")
        revised = await self._run(client, samples, "Revise Task", "update", {
            "sourceCurrent": target(atom), "changes": {"body": SUMMARY + "\nRevised.\n"},
        }, "draft", f"{atom}@2-draft")
        await self._run(client, samples, "Publish Task revision", "promote_draft", {
            "target": target(revised, 2), "targetStatus": "backlog",
        }, "backlog", f"{atom}@2")

    async def _asset(self, client, samples):
        asset = await self._run(client, samples, "Create Ticket Asset", "create_asset", {"newAtom": {
            "template": "work_report", "body": SUMMARY,
        }}, "in_queue")
        await self._run(client, samples, "Update Asset body", "direct_update", {
            "target": target(asset.split("@")[0]), "changes": {"body": SUMMARY + "\nResult.\n"},
        }, "in_queue", asset)

    async def _contract(self, client, samples):
        draft = await self._run(client, samples, "Create Contract Draft", "create_draft", {"newAtom": {
            "template": "component_contract", "container": {"component": "C00"}, "lens": "SPEC", "body": CONTRACT,
        }}, "draft")
        atom = draft.split("@")[0]
        await self._run(client, samples, "Publish Contract Draft", "promote_draft", {
            "target": target(draft), "targetStatus": "ready",
        }, "ready", f"{atom}@1")
        await self._run(client, samples, "Activate Contract", "change_status", {
            "target": target(atom), "targetStatus": "active",
        }, "active", f"{atom}@1")
        revised = await self._run(client, samples, "Revise Contract", "update", {
            "sourceCurrent": target(atom), "changes": {"body": CONTRACT + "\nRevised.\n"},
        }, "draft", f"{atom}@2-draft")
        await self._run(client, samples, "Archive Contract Draft", "archive", {
            "target": target(revised, 2),
        }, "archived", f"{atom}@2")
        await self._run(client, samples, "Archive Active Contract", "archive", {
            "target": target(atom),
        }, "archived", f"{atom}@1")
