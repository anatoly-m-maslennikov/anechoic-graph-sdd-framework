"""Exercise graph refresh with a witnessed Lean installation and a checker failure."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from .WORKERS_beta_C69__tests__shared import command_with_fixture, generation_fixture


WORKER = "WORKERS_beta_C69.WORKERS_beta_C69__shared"
LEAN = shutil.which("lean")


class LeanGraphRefreshTests(unittest.TestCase):
    def worker(self, output, request):
        result = subprocess.run([sys.executable, "-B", "-P", "-m", WORKER, "--generation-dir", str(output)],
                                input=json.dumps(request), text=True, capture_output=True, timeout=120)
        self.assertEqual(0, result.returncode, result.stderr)
        return json.loads(result.stdout)

    @unittest.skipUnless(LEAN and (Path(LEAN).resolve().parents[1] / "lib/lean").is_dir(),
                         "Direct Lean installation is unavailable")
    def test_existing_code_reuses_model_and_runs_lean_after_edit(self):
        binding, output, _ = generation_fixture(self.enterContext(TemporaryDirectory()))
        source = Path(binding["root"]) / "report.py"
        source.write_text("def report():\n    print('event')\n")
        original = self.worker(output, {"binding": binding, "reuse": None})
        self.assertIsInstance(original["reuse"], dict, original["graph"]["state_effect_findings"])
        reuse = original["reuse"] | {"base_generation": "admitted"}
        structure = json.loads((output / "structure.json").read_text())
        source.write_text("def report():\n    print('event')\n    print('second event')\n")
        refreshed = output.with_name("refreshed")
        refreshed.mkdir()
        result = self.worker(refreshed, {"binding": binding, "reuse": reuse, "structure": structure})
        self.assertEqual("admitted", result["base_generation"])
        self.assertFalse(any(refreshed.iterdir()))
        self.assertEqual(reuse["inputs"]["manifest"], result["reuse"]["inputs"]["manifest"])
        self.assertNotEqual(reuse["inputs"]["graph"], result["reuse"]["inputs"]["graph"])
        report, = (row for row in result["graph"]["state_effect_findings"] if row[1:4] == ["report.py", "python", "report"])
        self.assertEqual("hasEffects", report[6])
        self.assertEqual(["output", "output"], [event["kind"] for event in json.loads(report[8])])
        stale = reuse | {"inputs": reuse["inputs"] | {"carrier_schema": "0" * 64}}
        rebuilt = self.worker(refreshed, {"binding": binding, "reuse": stale, "structure": structure})
        self.assertIn("receipt", rebuilt)
        self.assertTrue((refreshed / "structure.json").is_file())

    def test_failed_lean_check_publishes_fresh_output_without_reuse(self):
        binding, output, _ = generation_fixture(self.enterContext(TemporaryDirectory()))
        failure = ["module:report.py", "report.py", "python", "<module>", 1, None,
                   "unresolved", False, "[]", "[]", "Lean check failed"]
        graph = {"state_effect_findings": [failure]}
        original_run = subprocess.run

        def launch(command, *args, **options):
            if command[-1] == "WORKERS_beta_C69.realization_graph":
                return subprocess.CompletedProcess(command, 0, json.dumps(graph), "")
            return original_run(command, *args, **options)

        with patch.object(subprocess, "run", side_effect=launch):
            response = command_with_fixture(WORKER, {"binding": binding, "reuse": None}, "--generation-dir", str(output))
        self.assertEqual(0, response.returncode, response.stderr)
        result = json.loads(response.stdout)
        self.assertIn("receipt", result)
        self.assertEqual(graph, result["graph"])
        self.assertIsNone(result["reuse"])
