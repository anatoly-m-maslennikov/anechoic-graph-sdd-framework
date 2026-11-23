"""The SQL descriptor binds only source bytes that passed module attestation."""
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

from FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_MODEL_VALIDATION.FEATURE_MODEL_VALIDATION__shared import open_serialized_model


class SerializedModelTests(unittest.TestCase):
    def test_bind_and_reject_changed_source_before_execution(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            engine = Path(__file__).resolve().parents[4]
            compiler = ("FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR."
                        "manifest_compiler_CS1.image_model_compile")
            generated = subprocess.run([sys.executable, "-B", "-P", "-m", compiler, str(root)],
                                       env={**os.environ, "PYTHONPATH": str(engine)},
                                       capture_output=True, text=True, check=True)
            fingerprint = generated.stdout.strip()
            descriptor = json.loads((root / "model.json").read_text())
            descriptor["module_sources"] = {
                name: (root / "anechoic_runtime_model" / name).read_text()
                for name in descriptor["modules"]
            }
            with open_serialized_model(descriptor) as model:
                self.assertEqual(fingerprint, model.fingerprint)
            bad = copy.deepcopy(descriptor)
            name = next(name for name in bad["modules"] if name != "__init__.py")
            bad["module_sources"][name] += "\nraise RuntimeError('executed')\n"
            with self.assertRaisesRegex(ValueError, "hash mismatch"):
                with open_serialized_model(bad):
                    self.fail("unverified source ran")
            del bad["module_sources"][name]
            with self.assertRaisesRegex(ValueError, "module set"):
                with open_serialized_model(bad):
                    self.fail("incomplete source was accepted")
