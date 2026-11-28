import json
import os
from pathlib import Path
from subprocess import run
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from ..WORKERS_beta_C69__tests__shared import generation_fixture


from .model_startup_fixture import COMPONENT_MANIFEST


def _build(binding, output, accepted_model=None):
    request = {
        "binding": binding,
        "reuse": None,
        "model_source": {"accepted_model": accepted_model},
    }
    return run(
        [
            sys.executable,
            "-B",
            "-P",
            "-m",
            "WORKERS_beta_C69.WORKERS_beta_C69__shared",
            "--generation-dir",
            str(output),
        ],
        input=json.dumps(request),
        text=True,
        capture_output=True,
    )


class ModelStartupTests(unittest.TestCase):
    def test_managed_build_uses_ingested_model(self):
        with (
            TemporaryDirectory() as directory,
            patch.dict(os.environ, {"ANECHOIC_STARTUP_TIMING": "1"}),
        ):
            binding, output, _ = generation_fixture(directory)
            run_result = _build(binding, output)
            self.assertEqual(0, run_result.returncode, run_result.stderr)
            reply = json.loads(run_result.stdout)
            model = json.loads((output / "model.json").read_bytes())
        self.assertEqual([], reply["model_diagnostics"])
        self.assertEqual(
            model["model_sha256"], reply["receipt"]["model_sha256"]
        )
        prefix = "ANECHOIC_STARTUP_TIMING "
        timings = [
            json.loads(line.removeprefix(prefix))
            for line in run_result.stderr.splitlines()
            if line.startswith(prefix)
        ]
        modes = {event["phase"]: event.get("mode") for event in timings}
        self.assertEqual("built", modes.get("model_ready"))
        self.assertEqual("built", modes.get("structure_ready"))

    def test_invalid_candidate_and_tampered_fallback_report_model_diagnostic(
        self,
    ):
        with TemporaryDirectory() as directory:
            binding, output, _ = generation_fixture(directory)
            baseline = _build(binding, output)
            self.assertEqual(0, baseline.returncode, baseline.stderr)
            accepted = json.loads((output / "model.json").read_bytes())
            accepted["module_sources"]["__init__.py"] = "tampered"
            (
                Path(binding["root"])
                / binding["control_root"]
                / "LAYER_1_META_ONTOLOGY_C9"
            ).mkdir()
            second = Path(directory).resolve() / "second"
            second.mkdir()
            failed = _build(binding, second, accepted)
            self.assertEqual(1, failed.returncode)
            reply = json.loads(failed.stdout)
            self.assertEqual([], list(second.iterdir()))
        self.assertEqual("build", reply["ingestion_failure"]["source"])
        self.assertEqual(
            "invalid_model_source", reply["model_diagnostics"][0]["code"]
        )
        self.assertIn(
            "No active Model Claims", reply["model_diagnostics"][0]["message"]
        )

    def test_malformed_component_blocks_managed_spec_staging(self):
        # fmt: off
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
            ADAPTERS_C30__shared import prepare_generation_snapshot
        # fmt: on
        from WORKERS_beta_C69.generation.spec_staging import _stage_spec_rows
        from WORKERS_beta_C69.generation.generation__shared import (
            _compile_ingested,
        )

        with TemporaryDirectory() as directory:
            binding, output, _ = generation_fixture(directory)
            control = Path(binding["root"]) / binding["control_root"]
            component = control / (
                "01_TIER_1_ARCHITECTURE/AN-S-3039-SPEC-COMPONENT_MANIFEST--dec"
                "lare-engine-studio.md"
            )
            component.parent.mkdir()
            component.write_text(COMPONENT_MANIFEST)
            baseline = _build(binding, output)
            self.assertEqual(0, baseline.returncode, baseline.stderr)
            structure = json.loads((output / "structure.json").read_bytes())
            self.assertIn("C14", structure["components"])
            _, _, inputs = prepare_generation_snapshot(
                binding, include_model_inputs=True, include_spec_rows=True
            )
            stage = Path(directory).resolve() / "staged"
            stage.mkdir()
            staged = {**inputs, "snapshot_id": "fixture-snapshot"}
            receipt, compiled, _, _ = _compile_ingested(
                binding, stage, staged, {"accepted_model": None}
            )
            self.assertIn("C14", compiled["components"])
            self.assertEqual(
                binding["manifest_sha256"], receipt["manifest_sha256"]
            )
            self._assert_malformed_component(
                component,
                binding,
                prepare_generation_snapshot,
                _stage_spec_rows,
            )

    def _assert_malformed_component(
        self, component, binding, prepare_generation_snapshot, _stage_spec_rows
    ):
        component.write_text(
            COMPONENT_MANIFEST.replace(
                "context:\n  template: component_manifest\n  lens: SPEC",
                "context: malformed",
            )
        )
        _, _, inputs = prepare_generation_snapshot(
            binding, include_model_inputs=True, include_spec_rows=True
        )
        self.assertTrue(inputs["structure_issues"])
        with self.assertRaisesRegex(
            ValueError, "Structure source ingestion failed"
        ):
            _stage_spec_rows(
                binding,
                inputs,
                {"socket": "/tmp/unused", "instance_id": "i"},
            )
