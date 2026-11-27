"""Exercise ingested Model compilation through the compiler CLI."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from ._model_ingestion_fixture import (
    ModelIngestionFixture,
    compile_model,
    compile_structure,
    model_args,
    model_ingestion,
)


class ModelIngestionTests(ModelIngestionFixture):
    def test_candidate_admission_failure_restores_accepted_model(self):
        with TemporaryDirectory() as tmp:
            root, digest, inputs = self.prepare(tmp)
            first = Path(tmp) / "first"
            result = compile_model(root, digest, first, inputs)
            self.assertEqual(0, result.returncode, result.stderr)
            accepted = json.loads((first / "model.json").read_text())
            stage = (Path(tmp) / "second").resolve()
            stage.mkdir()
            args = model_args(stage, root, digest)
            open_model = model_ingestion.open_admitted_model
            calls = 0

            def reject_candidate(*args, **kwargs):
                nonlocal calls
                calls += 1
                if calls == 1:
                    raise OSError("candidate admission failed")
                return open_model(*args, **kwargs)

            with patch.object(
                model_ingestion,
                "open_admitted_model",
                side_effect=reject_candidate,
            ):
                outcome = model_ingestion.compile_ingested(
                    args,
                    {
                        **inputs,
                        "accepted_model": accepted,
                        "force_rebuild": True,
                    },
                    compile_structure,
                )
            self.assertNotIn("error", outcome)
            self.assertEqual(
                accepted["model_sha256"],
                json.loads((stage / "model.json").read_text())["model_sha256"],
            )
            self.assertIn(
                "candidate admission failed",
                outcome["model_diagnostics"][0]["message"],
            )

            self.check_failed_fallback(tmp, args, inputs, accepted)

    def check_failed_fallback(self, tmp, args, inputs, accepted):
        failed_stage = (Path(tmp) / "third").resolve()
        failed_stage.mkdir()
        args.generation = failed_stage
        with patch.object(
            model_ingestion,
            "open_admitted_model",
            side_effect=[
                OSError("candidate admission failed"),
                KeyError("fallback admission failed"),
            ],
        ):
            failure = model_ingestion.compile_ingested(
                args,
                {
                    **inputs,
                    "accepted_model": accepted,
                    "force_rebuild": True,
                },
                compile_structure,
            )
        self.assertIn("fallback admission failed", failure["error"]["message"])
        self.assertIn(
            "candidate admission failed",
            failure["model_diagnostics"][0]["message"],
        )

    def test_identical_inputs_reuse_and_force_rebuild(self):
        with TemporaryDirectory() as tmp:
            root, digest, inputs = self.prepare(tmp)
            first = Path(tmp) / "first"
            result = compile_model(root, digest, first, inputs)
            self.assertEqual(0, result.returncode, result.stderr)
            accepted = json.loads((first / "model.json").read_text())
            self.assertIn("model_inputs_sha256", accepted)
            stage = (Path(tmp) / "second").resolve()
            stage.mkdir()
            args = model_args(stage, root, digest)
            with patch.object(
                model_ingestion,
                "write_model_records",
                wraps=model_ingestion.write_model_records,
            ) as compile_records:
                outcome = model_ingestion.compile_ingested(
                    args,
                    {**inputs, "accepted_model": accepted},
                    compile_structure,
                )
                self.assertNotIn("error", outcome)
                compile_records.assert_not_called()
                self.assertIn("structure", outcome)
                args.generation = (Path(tmp) / "third").resolve()
                args.generation.mkdir()
                outcome = model_ingestion.compile_ingested(
                    args,
                    {
                        **inputs,
                        "accepted_model": accepted,
                        "force_rebuild": True,
                    },
                    compile_structure,
                )
                self.assertNotIn("error", outcome)
                compile_records.assert_called_once()

    def test_changed_compiler_fingerprint_rebuilds_identical_rows(self):
        with TemporaryDirectory() as tmp:
            root, digest, inputs = self.prepare(tmp)
            first = Path(tmp) / "first"
            result = compile_model(root, digest, first, inputs)
            self.assertEqual(0, result.returncode, result.stderr)
            accepted = json.loads((first / "model.json").read_text())
            second = Path(tmp) / "second"
            result = compile_model(
                root,
                digest,
                second,
                {
                    **inputs,
                    "accepted_model": accepted,
                    "compiler_sha256": "b" * 64,
                },
            )
            self.assertEqual(0, result.returncode, result.stderr)
            rebuilt = json.loads((second / "model.json").read_text())
            self.assertNotEqual(
                accepted["model_inputs_sha256"], rebuilt["model_inputs_sha256"]
            )
