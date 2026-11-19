import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

from FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR import native_manifest_model
from FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.native_manifest_model import load_native_model


class NativeManifestModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = load_native_model()
        cls.fields = {"atom_id": "AN-S-123", "ref_id": "AN-S-123@1", "version": 1,
                      "tier": -1, "name": "Anechoic", "prefix": "AN"}

    def test_reviewed_manifest_validation(self):
        fields = self.fields | {"parameters": {f"option{i}": i for i in range(18)}}
        self.assertEqual(self.model.validate_manifest(fields, "C00").name, "Anechoic")
        with self.assertRaisesRegex(ValueError, "check_project_manifest"):
            self.model.validate_manifest(fields | {"parameters": fields["parameters"] | {"extra": 1}}, "C00")
        with self.assertRaisesRegex(ValueError, "check_atom_identity"):
            self.model.validate_manifest(fields | {"ref_id": "AN-S-123@2"}, "C00")
        with self.assertRaisesRegex(ValueError, "Project C00"):
            self.model.validate_manifest(fields, "C01")

    def test_containment_is_checked_by_the_reviewed_model(self):
        project = self.model._validate("Project", {}, {})
        component = self.model._validate("Component", {}, {"CHILD_OF": [project]})
        with self.assertRaisesRegex(ValueError, "CONTAINED_BY: invalid target kind"):
            self.model._validate("Project Manifest", self.fields, {"CONTAINED_BY": [component]})

    def test_claim_file_tampering_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "native-graph-claims.json"
            path.write_bytes(b"[]")
            with patch.object(native_manifest_model, "_ASSETS", Path(directory)):
                with self.assertRaisesRegex(ValueError, "reviewed Claim file differs"):
                    native_manifest_model._NativeModel()

    def test_reviewed_relations_only(self):
        self.assertEqual(self.model.relation_types, {
            "CHILD_OF", "CHILDREN", "CONTAINED_BY", "CONTAINS", "IS_CLASSIFIED_BY", "CLASSIFIES",
            "IS_PROPERTY_OF",
        })
        self.assertEqual(self.model.inverses, {
            "CHILD_OF": "CHILDREN", "CONTAINED_BY": "CONTAINS", "IS_CLASSIFIED_BY": "CLASSIFIES",
        })


if __name__ == "__main__":
    unittest.main()
