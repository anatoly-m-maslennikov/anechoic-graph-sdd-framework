"""Exercise ingested Model compilation through the compiler CLI."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory

from ._model_ingestion_fixture import (
    ModelIngestionFixture,
    compile_model,
    project,
)


class ModelIngestionTests(ModelIngestionFixture):
    def test_incompatible_matching_asset_rebuilds(self):
        with TemporaryDirectory() as tmp:
            root, digest, inputs = self.prepare(tmp)
            first = Path(tmp) / "first"
            result = compile_model(root, digest, first, inputs)
            self.assertEqual(0, result.returncode, result.stderr)
            accepted = json.loads((first / "model.json").read_text())
            accepted["class_modules"]["MissingModelType"] = next(
                iter(accepted["class_modules"].values())
            )
            second = Path(tmp) / "second"
            result = compile_model(
                root, digest, second, {**inputs, "accepted_model": accepted}
            )
            self.assertEqual(0, result.returncode, result.stderr)
            rebuilt = json.loads((second / "model.json").read_text())
            self.assertNotIn("MissingModelType", rebuilt["class_modules"])
            self.assertEqual(
                accepted["model_inputs_sha256"], rebuilt["model_inputs_sha256"]
            )

    def test_sticky_fallback_and_tampered_rejection(self):
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
                {**inputs, "has_c9": True, "accepted_model": accepted},
            )
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual(
                accepted["model_sha256"],
                json.loads((second / "model.json").read_text())[
                    "model_sha256"
                ],
            )
            self.assertEqual(
                accepted["model_inputs_sha256"],
                json.loads((second / "model.json").read_text())[
                    "model_inputs_sha256"
                ],
            )
            self.assertIn(
                "No active Model Claims",
                json.loads(result.stdout)["model_diagnostics"][0]["message"],
            )
            accepted["module_sources"]["__init__.py"] = "tampered"
            result = compile_model(
                root,
                digest,
                Path(tmp) / "third",
                {**inputs, "has_c9": True, "accepted_model": accepted},
            )
            self.assertNotEqual(0, result.returncode)
            failure = json.loads(result.stderr)
            self.assertIn("hash mismatch", failure["error"]["message"])
            self.assertEqual(1, len(failure["model_diagnostics"]))

    def test_incompatible_fallback_keeps_the_candidate_diagnostic(self):
        with TemporaryDirectory() as tmp:
            root, digest, inputs = self.prepare(tmp)
            first = Path(tmp) / "first"
            result = compile_model(root, digest, first, inputs)
            self.assertEqual(0, result.returncode, result.stderr)
            accepted = json.loads((first / "model.json").read_text())
            accepted["class_modules"]["MissingModelType"] = next(
                iter(accepted["class_modules"].values())
            )
            failed = compile_model(
                root,
                digest,
                Path(tmp) / "failed",
                {**inputs, "has_c9": True, "accepted_model": accepted},
            )
            self.assertNotEqual(0, failed.returncode)
            failure = json.loads(failed.stderr)
            self.assertIn("MissingModelType", failure["error"]["message"])
            self.assertIn(
                "No active Model Claims",
                failure["model_diagnostics"][0]["message"],
            )

    def test_invalid_envelope_rejected(self):
        with TemporaryDirectory() as tmp:
            root, digest = project(tmp)
            result = compile_model(
                root, digest, Path(tmp) / "stage", {"rows": []}
            )
            self.assertNotEqual(0, result.returncode)
            self.assertEqual(
                [], json.loads(result.stderr)["model_diagnostics"]
            )
