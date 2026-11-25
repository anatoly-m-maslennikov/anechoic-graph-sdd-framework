import json
import os
from pathlib import Path
from subprocess import run
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from .WORKERS_beta_C69__tests__shared import generation_fixture


def _build(binding, output, accepted_model=None):
    request = {"binding": binding, "reuse": None, "model_source": {"accepted_model": accepted_model}}
    return run([sys.executable, "-B", "-P", "-m", "WORKERS_beta_C69.WORKERS_beta_C69__shared",
                "--generation-dir", str(output)], input=json.dumps(request), text=True, capture_output=True)


class ModelStartupTests(unittest.TestCase):
    def test_managed_build_uses_ingested_model(self):
        with TemporaryDirectory() as directory, patch.dict(os.environ, {"ANECHOIC_STARTUP_TIMING": "1"}):
            binding, output, _ = generation_fixture(directory)
            run_result = _build(binding, output)
            self.assertEqual(0, run_result.returncode, run_result.stderr)
            reply = json.loads(run_result.stdout)
            model = json.loads((output / "model.json").read_bytes())
        self.assertEqual([], reply["model_diagnostics"])
        self.assertEqual(model["model_sha256"], reply["receipt"]["model_sha256"])
        prefix = "ANECHOIC_STARTUP_TIMING "
        timings = [json.loads(line.removeprefix(prefix)) for line in run_result.stderr.splitlines()
                   if line.startswith(prefix)]
        modes = {event["phase"]: event.get("mode") for event in timings}
        self.assertEqual("built", modes.get("model_ready"))
        self.assertEqual("built", modes.get("structure_ready"))

    def test_invalid_candidate_and_tampered_fallback_report_model_diagnostic(self):
        with TemporaryDirectory() as directory:
            binding, output, _ = generation_fixture(directory)
            baseline = _build(binding, output)
            self.assertEqual(0, baseline.returncode, baseline.stderr)
            accepted = json.loads((output / "model.json").read_bytes())
            accepted["module_sources"]["__init__.py"] = "tampered"
            (Path(binding["root"]) / binding["control_root"] / "LAYER_1_META_ONTOLOGY_C9").mkdir()
            second = Path(directory).resolve() / "second"
            second.mkdir()
            failed = _build(binding, second, accepted)
            self.assertEqual(1, failed.returncode)
            reply = json.loads(failed.stdout)
            self.assertEqual([], list(second.iterdir()))
        self.assertEqual("build", reply["ingestion_failure"]["source"])
        self.assertEqual("invalid_model_source", reply["model_diagnostics"][0]["code"])
        self.assertIn("No active Model Claims", reply["model_diagnostics"][0]["message"])
