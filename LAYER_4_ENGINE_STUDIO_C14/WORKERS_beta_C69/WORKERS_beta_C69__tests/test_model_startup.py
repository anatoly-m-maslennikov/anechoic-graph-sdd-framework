import json
import sys
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from .. import WORKERS_beta_C69__shared as worker
from .WORKERS_beta_C69__tests__shared import generation_fixture



class ModelStartupTests(unittest.TestCase):
    def test_managed_build_uses_ingested_model(self):
        with TemporaryDirectory() as tmp:
            binding, output, _ = generation_fixture(tmp)
            result = worker.build_generation(binding, output, managed=True, model_source={"accepted_model": None})
            self.assertEqual([], result["model_diagnostics"])
            self.assertTrue((output / "model.json").exists())
            self.assertEqual(result["receipt"]["model_sha256"], json.loads((output / "model.json").read_text())["model_sha256"])

    def test_failed_fallback_retains_candidate_diagnostic(self):
        diagnostic = {"attempt_id": "attempt", "accepted_generation": None, "severity": "ERROR",
                      "code": "invalid_model_source", "message": "bad candidate", "atom_ref": "AN-C-1@1",
                      "source_path": "__PROJECT_CONFIG/CUSTOM_MODEL/AN-C-1-a.md", "subject": None}
        error = worker._BuildFailure("manifest_build_CS4__shared", "fallback is incompatible")
        error.model_diagnostics = [diagnostic]
        with TemporaryDirectory() as tmp, patch.object(worker, "_run_job", side_effect=error):
            with self.assertRaises(worker._BuildFailure) as failure:
                worker._compile_ingested({}, Path(tmp), {"rows": [], "has_c9": True, "issues": []},
                                         {"accepted_model": {}})
        self.assertEqual([diagnostic], failure.exception.model_diagnostics)

    def test_failed_fallback_worker_envelope_contains_diagnostics(self):
        diagnostic = {"attempt_id": "one", "accepted_generation": None, "severity": "ERROR",
                      "code": "invalid_model_source", "message": "bad source", "atom_ref": None,
                      "source_path": None, "subject": None}
        stdout = StringIO()
        failure = worker._ModelAttemptFailure(ValueError("fallback failed"), [diagnostic])
        with (patch.object(sys, "argv", ["worker", "--generation-dir", "/tmp/stage"]),
              patch.object(sys, "stdin", StringIO('{"binding":{},"reuse":null}')),
              patch.object(worker, "watch_managed_parent"), patch.object(worker, "_run", side_effect=failure),
              redirect_stdout(stdout), redirect_stderr(StringIO())):
            self.assertEqual(1, worker.main())
        envelope = json.loads(stdout.getvalue())
        self.assertEqual([diagnostic], envelope["model_diagnostics"])
        self.assertEqual("build", envelope["ingestion_failure"]["source"])

    def test_failed_fallback_snapshot_is_not_retried(self):
        diagnostic = {"code": "invalid_model_source"}
        with TemporaryDirectory() as tmp:
            binding, output, _ = generation_fixture(tmp)
            with (patch("FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared.prepare_generation_snapshot",
                        return_value=(None, lambda endpoints: (_ for _ in ()).throw(ValueError("invalid snapshot")), {})),
                  patch.object(worker, "_compile_ingested", return_value=({}, {}, {}, [diagnostic])) as compile_stage):
                with self.assertRaises(worker._ModelAttemptFailure) as failure:
                    worker.build_generation(binding, output, model_source={})
            self.assertEqual([diagnostic], failure.exception.model_diagnostics)
            compile_stage.assert_called_once()

    def test_snapshot_fallback_clears_stage_and_passes_failure_to_compiler(self):
        diagnostic = {"code": "model_snapshot_invalid", "message": "undeclared relation"}
        with TemporaryDirectory() as tmp:
            stage = Path(tmp)
            (stage / "stale").write_text("old")
            def run(module, payload, *args):
                self.assertEqual([], list(stage.iterdir()))
                self.assertEqual("undeclared relation", payload["model_inputs"]["issues"][-1]["message"])
                self.assertEqual({"model_sha256": "prior"}, payload["model_inputs"]["accepted_model"])
                return {"model_diagnostics": [diagnostic], "manifest_sha256": "manifest"}
            with (patch.object(worker, "_run_job", side_effect=run),
                  patch.object(worker, "_read_compile_receipt", return_value=({}, {}, {}))):
                result = worker._compile_ingested({}, stage, {"rows": [], "has_c9": True, "issues": []},
                                                  {"accepted_model": {"model_sha256": "prior"}},
                                                  fallback=ValueError("undeclared relation"))
            self.assertEqual([diagnostic], result[3])

    def test_compiler_fatal_returns_candidate_diagnostics(self):
        with TemporaryDirectory() as tmp:
            binding, output, _ = generation_fixture(tmp)
            worker.build_generation(binding, output, model_source={"accepted_model": None})
            accepted = json.loads((output / "model.json").read_text())
            accepted["module_sources"]["__init__.py"] = "tampered"
            (Path(binding["root"]) / binding["control_root"] / "LAYER_1_META_ONTOLOGY_C9").mkdir()
            second = Path(tmp).resolve() / "second"
            second.mkdir()
            with redirect_stderr(StringIO()):
                with self.assertRaises(worker._BuildFailure) as failure:
                    worker.build_generation(binding, second, model_source={"accepted_model": accepted})
            self.assertTrue(failure.exception.model_diagnostics)
            self.assertIn("No active Model Claims", failure.exception.model_diagnostics[0]["message"])
