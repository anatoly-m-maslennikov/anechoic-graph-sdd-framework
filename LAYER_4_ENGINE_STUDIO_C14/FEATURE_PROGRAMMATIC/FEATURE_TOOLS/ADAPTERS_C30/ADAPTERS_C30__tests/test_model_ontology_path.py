from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest

from ..model_ontology_path__pub import find_ontology_component, is_ontology_model_source
from ..model_capture import model_inputs


class OntologyPathTests(unittest.TestCase):
    def test_relocated_source_and_component(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            c9 = root / "ONTOLOGY_SCORE_C91/CONTINUANT_PITCHFORK_C9"
            c9.mkdir(parents=True)
            self.assertEqual(c9, find_ontology_component(root))
            self.assertTrue(is_ontology_model_source("ONTOLOGY_SCORE_C91/CONTINUANT_PITCHFORK_C9/_SPEC/a.md"))
            self.assertFalse(is_ontology_model_source("ONTOLOGY_SCORE_C91/CONTINUANT_PITCHFORK_C9/_SPEC/deep/a.md"))
            (root / "OTHER_C9").mkdir()
            with self.assertRaisesRegex(ValueError, "Duplicate"):
                find_ontology_component(root)

    def test_symlink_component_rejected(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "UNSAFE_C9").symlink_to(root, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "Unsafe"):
                find_ontology_component(root)

    def test_capture_selects_relocated_current_model_and_issues(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            control = root / "control"
            c9 = control / "ONTOLOGY_SCORE_C91/CONTINUANT_PITCHFORK_C9"
            c9.mkdir(parents=True)
            relative = "control/ONTOLOGY_SCORE_C91/CONTINUANT_PITCHFORK_C9/_DES/a.md"
            row = {"source_path": relative, "_exact_ref": "AN-S-1@1", "header_json": {},
                   "_content_bytes": b"body", "status_group": "Current"}
            issue = {"relative_path": relative, "message": "bad"}
            capture = SimpleNamespace(atoms=[row], ingestion_issues=[issue], errors={})
            inputs = model_inputs(SimpleNamespace(root=root, control_root=control), capture)
            self.assertTrue(inputs["has_c9"])
            self.assertEqual("ONTOLOGY_SCORE_C91/CONTINUANT_PITCHFORK_C9/_DES/a.md", inputs["rows"][0]["source_path"])
            self.assertEqual((issue,), inputs["issues"])
