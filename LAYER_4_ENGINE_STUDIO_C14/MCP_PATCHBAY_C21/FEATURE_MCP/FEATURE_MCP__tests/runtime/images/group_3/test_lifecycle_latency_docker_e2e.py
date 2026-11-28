"""Measure successful single-Atom transitions against the candidate image."""

import asyncio
import json
from math import ceil
from pathlib import Path
import re
import shutil
from statistics import median
from time import monotonic
import unittest

from mcp.client.session import ClientSession

from ...project.group_2 import _lifecycle_latency_sequences as sequences
from ....FEATURE_MCP__tests__shared import ROOT
from ....integration.graph.group_2.native_import_graph_docker_cases import (
    archive_project,
)
from ....integration.workbench.group_4.workbench_docker_support import (
    image_mcp_transport,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.transport_support.paths.\
    paths__shared import (
    MCP_PATH,
)


TRIALS = 50
SUMMARY = "## Summary\n\nMeasure lifecycle latency.\n"
CONTRACT = SUMMARY + "\n## Guarantee\n\nReturn a result.\n"
GENERATIONS = """SELECT json_extract_string(detail, '$.kind'), count(*)
    FROM flow_events WHERE component = 'C68' AND name = 'generation_result'
      AND outcome = 'succeeded' GROUP BY 1"""
NON_DELTA_RUNS = """SELECT run_id, json_extract_string(detail, '$.kind')
    FROM flow_events WHERE component = 'C68' AND name = 'generation_result'
      AND outcome = 'succeeded' AND json_extract_string(detail, '$.kind') IS DISTINCT FROM 'native_delta'
    ORDER BY "at" DESC LIMIT 32"""


def target(ref, version=1):
    return {"ref_id": ref, "version": version}


def prepare_project(root):
    shutil.copytree(
        Path(__file__).resolve().parents[3] / "assets" / "lifecycle_latency",
        root,
        dirs_exist_ok=True,
    )
    ontology = Path("_anechoic_anechoic/LAYER_2_META_METHODOLOGY_C58/_DOM/MTD")
    source = ROOT / (
        "_anechoic_anechoic/ONTOLOGY_SCORE_C82/OCCURRENT_METRONOME_C58/_DO"
        "M/MTD"
    )
    for atom in ("AN-S-1928", "AN-S-1834", "AN-S-1831"):
        (original,) = source.rglob(f"{atom}-MTD-*.md")
        path = root / ontology / original.name
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(original, path)


def operation_metrics(label, samples):
    ordered = sorted(samples)
    return {
        "operation": label,
        "trials": len(samples),
        "p50_ms": round(median(ordered), 3),
        **{
            f"p{p}_ms": round(ordered[ceil(p * len(ordered) / 100) - 1], 3)
            for p in (10, 90, 95)
        },
        "max_ms": round(ordered[-1], 3),
        "samples_above_500_ms": sum(sample > 500 for sample in samples),
        "samples_ms": [round(sample, 3) for sample in samples],
    }


def lifecycle_metrics(samples):
    operations = [
        operation_metrics(label, times) for label, times in samples.items()
    ]
    return {
        "operations": operations,
        "overall": {
            "max_ms": max(metrics["max_ms"] for metrics in operations),
            "samples_above_500_ms": sum(
                metrics["samples_above_500_ms"] for metrics in operations
            ),
        },
    }


class LifecycleLatencyImageTest(unittest.TestCase):
    def test_single_atom_lifecycle_latency(self):
        with archive_project(self, prepare_project) as project:
            report = asyncio.run(self._measure(project.url + MCP_PATH))
        print(
            "ANECHOIC_TEST_METRICS "
            + json.dumps({"lifecycle_latency": report}),
            flush=True,
        )

    async def _measure(self, endpoint):
        async with (
            image_mcp_transport(endpoint) as streams,
            ClientSession(*streams) as client,
        ):
            await client.initialize()
            initial_atoms = (
                await self._sql(client, "SELECT count(*) FROM atoms")
            )[0][0]
            before = dict(await self._sql(client, GENERATIONS))
            baseline = await self._sql(client, NON_DELTA_RUNS)
            samples = {}
            for _ in range(TRIALS):
                await self._task(client, samples)
                await self._asset(client, samples)
                await self._contract(client, samples)
            after = dict(await self._sql(client, GENERATIONS))
            expected = before | {
                "native_delta": before.get("native_delta", 0) + 13 * TRIALS
            }
            diagnostics = (
                await self._mismatch_diagnostics(client, baseline)
                if expected != after
                else None
            )
        self.assertEqual(13, len(samples))
        self.assertTrue(
            all(len(values) == TRIALS for values in samples.values())
        )
        self.assertEqual(
            expected,
            after,
            "Lifecycle trials must use only incremental admission; "
            + str(diagnostics),
        )
        return {
            "initial_atoms": initial_atoms,
            "measurement": "MCP request to SQL readback",
            **lifecycle_metrics(samples),
        }

    async def _mismatch_diagnostics(self, client, baseline):
        try:
            after = await self._sql(client, NON_DELTA_RUNS)
            baseline_ids = {row[0] for row in baseline}
            new = [row for row in after if row[0] not in baseline_ids]
            ids = [
                row[0]
                for row in new
                if isinstance(row[0], str)
                and re.fullmatch(r"[0-9a-f]{32}", row[0])
            ]
            events = []
            if ids:
                selected = ", ".join("'" + value + "'" for value in ids)
                events = await self._sql(
                    client,
                    f"""SELECT run_id, sequence, kind, name, outcome,
                    json_extract_string(detail, '$.kind'), json_extract_string(detail, '$.code')
                    FROM flow_events WHERE component = 'C68' AND run_id IN ({selected})
                    ORDER BY run_id, sequence LIMIT 24""",
                )
            return {
                "baseline_non_delta": baseline,
                "new_non_delta": new,
                "events": events,
                "run_limit": 32,
                "event_limit": 24,
            }
        except Exception as error:
            return {
                "baseline_non_delta": baseline,
                "diagnostic_error": str(error),
            }

    async def _sql(self, client, query):
        reply = await client.call_tool(
            "query_run", {"sql": query, "result_delivery": "inline"}
        )
        self.assertFalse(reply.is_error, reply.structured_content)
        return reply.structured_content["rows"]

    async def _run(
        self, client, samples, label, operation, arguments, status, exact=None
    ):
        started = monotonic()
        reply = await client.call_tool(
            f"atom_lifecycle_{operation}", arguments
        )
        receipt = reply.structured_content
        self.assertFalse(reply.is_error, receipt)
        self.assertIn(
            receipt["status"], ("completed", "draft_created"), receipt
        )
        if exact is None:
            exact = (receipt.get("savedDraft") or receipt["artifact"])[
                "ref_id"
            ]
        self.assertRegex(
            exact, r"\AAN-[TS]-[0-9]+(?:@[1-9][0-9]*(?:-draft)?)?\Z"
        )
        rows = await self._sql(
            client,
            f"""SELECT n.exact_ref, a."header.state.status"
            FROM atoms a JOIN native_references n USING (reference)
            WHERE n.exact_ref = '{exact}' OR n.reference = '{exact}'""",
        )
        elapsed_ms = (monotonic() - started) * 1000
        self.assertEqual(1, len(rows), (label, receipt, rows))
        self.assertEqual(
            exact if "@" in exact else f"{exact}@1", rows[0][0], receipt
        )
        self.assertEqual(status, rows[0][1], (label, receipt, rows))
        samples.setdefault(label, []).append(elapsed_ms)
        return rows[0][0]

    async def _task(self, client, samples):
        await sequences.task(self, client, samples, target, SUMMARY)

    async def _asset(self, client, samples):
        asset = await self._run(
            client,
            samples,
            "Create Ticket Asset",
            "create_asset",
            {
                "newAtom": {
                    "template": "work_report",
                    "body": SUMMARY,
                }
            },
            "in_queue",
        )
        await self._run(
            client,
            samples,
            "Update Asset body",
            "direct_update",
            {
                "target": target(asset.split("@")[0]),
                "changes": {"body": SUMMARY + "\nResult.\n"},
            },
            "in_queue",
            asset,
        )

    async def _contract(self, client, samples):
        await sequences.contract(self, client, samples, target, CONTRACT)
