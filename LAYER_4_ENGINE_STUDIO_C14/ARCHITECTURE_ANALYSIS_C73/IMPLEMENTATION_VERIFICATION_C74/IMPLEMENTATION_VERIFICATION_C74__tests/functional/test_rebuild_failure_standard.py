"""Check observed rebuild failures against the AN-S-3116 Lean claim."""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = next(
    path
    for path in Path(__file__).resolve().parents
    if (path / "_anechoic_anechoic").is_dir()
)
STUDIO = ROOT / "LAYER_4_ENGINE_STUDIO_C14"
SOURCE = STUDIO / "KERNEL_MIXER_C59/native_query_rebuild.py"
CLAIM = ROOT / (
    "_anechoic_anechoic/LAYER_4_ENGIN"
    "E_STUDIO_C14/IWE_CONSOLE_C43/FEA"
    "TURE_IWE_CONSOLE_BACKEND_C45/01_"
    "TIER_1_ARCHITECTURE/AN-S-3116-DE"
    "S-DECISION--store-native-workben"
    "ch-duckdb-data-on-disk.md"
)
OBSERVER = (
    "MCP_PATCHBAY_C21.FEATURE_MCP.FEA"
    "TURE_MCP__tests.native_rebuild_f"
    "ailure_trace"
)
EVENTS = {"failed", "diagnostic", "published", "clientError", "clientSuccess"}


class RebuildFailureStandardTests(unittest.TestCase):
    def evaluate_trace(self, lean, claim, lean_file, events):
        self.assertIsInstance(events, list)
        self.assertTrue(
            events
            and all(
                isinstance(event, str) and event in EVENTS for event in events
            ),
            events,
        )
        terms = ", ".join(f".{event}" for event in events)
        lean_file.write_text(
            claim
            + "\n\ndef observed : List WorkbenchRebuildFailure.Event := ["
            + terms
            + "]\n"
            "#eval WorkbenchRebuildFailure.conforms observed\n"
        )
        check = subprocess.run(
            [lean, str(lean_file)],
            capture_output=True,
            text=True,
            timeout=45,
            check=False,
        )
        self.assertEqual(check.returncode, 0, check.stdout + check.stderr)
        return check.stdout.strip()

    def test_observed_failure_and_mutation(self):
        lean, block, source, old, ready, silent = self._mutation_inputs()
        with tempfile.TemporaryDirectory() as temp:
            scratch = Path(temp)
            overlays = self._make_overlays(scratch, source, old, ready, silent)
            records = {}
            for name, prefix, expected_source, status, expected_events in (
                (
                    "baseline",
                    [],
                    SOURCE,
                    400,
                    ["failed", "diagnostic", "clientError"],
                ),
                (
                    "mutated",
                    [overlays["mutated"][0]],
                    overlays["mutated"][1],
                    200,
                    ["failed", "diagnostic", "clientSuccess"],
                ),
                (
                    "missing_diagnostic",
                    [overlays["missing_diagnostic"][0]],
                    overlays["missing_diagnostic"][1],
                    400,
                    ["failed", "clientError"],
                ),
            ):
                self._check_observed_case(
                    name,
                    prefix,
                    expected_source,
                    status,
                    expected_events,
                    lean,
                    block,
                    scratch,
                    records,
                )
            print(json.dumps(records, sort_keys=True))

    def _mutation_inputs(self):
        lean = os.environ.get("LEAN_BIN") or shutil.which("lean")
        self.assertTrue(lean, "Set LEAN_BIN or install Lean on PATH")
        blocks = re.findall(
            r"```lean\s*\n(.*?)\n```", CLAIM.read_text(), re.DOTALL
        )
        blocks = [
            block
            for block in blocks
            if "namespace WorkbenchRebuildFailure\n" in block
        ]
        self.assertEqual(
            len(blocks),
            1,
            "Expected exactly one WorkbenchRebuildFailure Lean block",
        )
        old = (
            "            except Exception as "
            'error:\n                print(f"W'
            "orkbench rebuild failed for {tar"
            'get!r}: {error}", file=sys.stder'
            "r)\n                raise\n"
        )
        ready = old.replace(
            "                raise\n",
            (
                '                return {"status"'
                ': "ready", "target": target, "re'
                'sult_ids": {}}\n'
            ),
        )
        silent = old.replace(
            (
                '                print(f"Workbenc'
                "h rebuild failed for {target!r}:"
                ' {error}", file=sys.stderr)\n'
            ),
            "",
        )
        source = SOURCE.read_text()
        self.assertEqual(source.count(old), 1, "Mutation anchor changed")
        return lean, blocks[0], source, old, ready, silent

    def _make_overlays(self, scratch, source, old, ready, silent):
        overlays = {}
        for name, replacement in (
            ("mutated", ready),
            ("missing_diagnostic", silent),
        ):
            overlay = scratch / name
            mutated = overlay / "KERNEL_MIXER_C59/native_query_rebuild.py"
            mutated.parent.mkdir(parents=True)
            mutated.write_text(source.replace(old, replacement))
            overlays[name] = (overlay, mutated)
        return overlays

    def _check_observed_case(
        self,
        name,
        prefix,
        expected_source,
        status,
        expected_events,
        lean,
        block,
        scratch,
        records,
    ):
        env = os.environ.copy()
        env["PYTHONPATH"] = os.pathsep.join(map(str, [*prefix, STUDIO]))
        run = subprocess.run(
            [sys.executable, "-B", "-m", OBSERVER],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            timeout=300,
            check=False,
        )
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        record = json.loads(run.stdout.splitlines()[-1])
        self.assertEqual(
            Path(record["source"]).resolve(), expected_source.resolve()
        )
        events = record["events"]
        verdict = self.evaluate_trace(
            lean, block, scratch / f"{name}.lean", events
        )
        self.assertEqual(
            verdict, "true" if name == "baseline" else "false", record
        )
        self.assertEqual(record["http_status"], status, record)
        self.assertEqual(events, expected_events, record)
        if name == "missing_diagnostic":
            self.assertIn("query failed:", record["stderr"])
            self.assertNotIn("Workbench rebuild failed", record["stderr"])
        records[name] = {**record, "lean_conforms": verdict == "true"}


if __name__ == "__main__":
    unittest.main()
