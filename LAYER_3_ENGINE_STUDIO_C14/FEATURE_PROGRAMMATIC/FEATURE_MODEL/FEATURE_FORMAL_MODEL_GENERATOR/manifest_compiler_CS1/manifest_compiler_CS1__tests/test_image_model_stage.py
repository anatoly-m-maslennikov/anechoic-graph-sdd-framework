"""Check guarded Model staging and the pinned predecessor selection."""

import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.manifest_compiler_CS1 import image_model_stage as stage


IMAGE_ID = "sha256:" + "a" * 64


class ImageModelStageTests(unittest.TestCase):
    def test_previous_selector_mounts_exact_current_codecs_read_only(self):
        names = ("carrier_read__pub.py", "carrier_syntax__pub.py",
                 "carrier_compat__pub.py", "native_carrier_header__pub.py",
                 "content_records__pub.py", "markdown_content__pub.py", "source_row__pub.py")
        inspected = [{"Id": IMAGE_ID, "Os": "linux",
                      "Config": {"Labels": {"org.anechoic.runtime.schema": "1"}}}]
        with tempfile.TemporaryDirectory() as temporary:
            component = Path(temporary) / "model"
            component.mkdir()

            def run(argv, **kwargs):
                if argv[1:3] == ["image", "inspect"]:
                    return subprocess.CompletedProcess(argv, 0, json.dumps(inspected), "")
                for name in names:
                    staged = component.parent / name
                    source = stage.PROGRAMMATIC / "FEATURE_TOOLS/ADAPTERS_C30" / name
                    self.assertEqual(source.read_bytes(), staged.read_bytes())
                    self.assertIn(f"type=bind,src={staged},dst=/workspace/{stage.ENGINE}/"
                                  f"FEATURE_PROGRAMMATIC/FEATURE_TOOLS/ADAPTERS_C30/{name},readonly", argv)
                self.assertIn("--read-only", argv)
                self.assertIn("--network=none", argv)
                return subprocess.CompletedProcess(argv, 0, '[["claim.md", "hash"]]', "")

            with patch.object(stage, "bounded_run", side_effect=run):
                self.assertEqual(stage.previous_claims(component, IMAGE_ID, timeout=5),
                                 [["claim.md", "hash"]])

    def test_previous_ready_image_is_required_when_recorded(self):
        with tempfile.TemporaryDirectory() as temporary:
            failed = subprocess.CompletedProcess([], 1, "", "")
            with patch.object(stage, "bounded_run", return_value=failed) as docker:
                with self.assertRaisesRegex(ValueError, "Previous ready image is unavailable"):
                    stage.previous_claims(Path(temporary), IMAGE_ID, timeout=5)
                docker.assert_called_once()


    def test_staging_rejects_changed_sources_and_selector_mismatch(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            (project / ".anechoic_tmp").mkdir()
            source = project / stage.ONTOLOGY
            source.mkdir()
            claim = source / "claim.md"
            claim.write_bytes(b"claim")
            reader = MagicMock()
            reader.inventory_shallow.return_value = [claim]
            reader.read.return_value = b"claim"
            reader.currentness.return_value = {"state": "changed"}

            def compile_model(command, deadline):
                (Path(command[-1]) / "model.json").write_text(
                    json.dumps({"declarations": [["claim.md@1", None, None]]}))
                return "f" * 64

            with (patch.object(stage, "ReadContext", return_value=reader),
                  patch.object(stage, "_run", side_effect=compile_model),
                  patch.object(stage, "previous_claims", return_value=[])):
                with self.assertRaisesRegex(ValueError, "selection does not match"):
                    stage.stage_model(project, project, 5, IMAGE_ID)
                with self.assertRaisesRegex(ValueError, "sources changed"):
                    stage.stage_model(project, project, 5, None)
