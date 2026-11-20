import importlib
import sys
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

from FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR import native_manifest_model
from FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.model_class_assembly import assemble_model_modules
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

    def test_active_declarations_drive_model_but_callbacks_stay_reviewed(self):
        reviewed, _, reviewed_hash = native_manifest_model.reviewed_model_records()
        active = tuple((f"Meta_C9/AN-S-{i}-SPEC--claim.md@1", subject, claim)
                       for i, (_, subject, claim) in enumerate(reviewed, 1))
        admit = native_manifest_model.admit_active_model_records
        _, _, active_hash = admit(active)
        self.assertNotEqual(active_hash, reviewed_hash)
        self.assertEqual(active_hash, admit(reversed(active))[2])
        with self.assertRaisesRegex(ValueError, "unique Model Declaration"):
            admit((*active, active[0]))
        index = next(i for i, (_, _, claim) in enumerate(active) if "def check_project_manifest(" in claim)
        path, subject, claim = active[index]
        changed = claim.replace("\ndef check_project_manifest(", "    extra_field: int = 10\n\ndef check_project_manifest(", 1)
        self.assertNotEqual(changed, claim)
        active_model = native_manifest_model._NativeModel(records=(*active[:index], (path, subject, changed),
                                                                    *active[index + 1:]))
        self.assertEqual(active_model.validate_manifest(self.fields, "C00").extra_field, 10)
        with self.assertRaisesRegex(ValueError, "check_project_manifest"):
            excessive = self.fields | {"parameters": {f"option{i}": i for i in range(19)}}
            active_model.validate_manifest(excessive, "C00")
        with self.assertRaisesRegex(ValueError, "missing reviewed instance checks"):
            admit((*active[:index], *active[index + 1:]))
        changed = claim.replace("def check_project_manifest(", "def changed_check(", 1)
        changed = changed.replace("instance_check=check_project_manifest", "instance_check=changed_check", 1)
        with self.assertRaisesRegex(ValueError, "instance check differs"):
            admit((*active[:index], (path, subject, changed), *active[index + 1:]))

    def test_compiled_model_uses_generated_class_objects(self):
        records, _, fingerprint = native_manifest_model.reviewed_model_records()
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory) / "anechoic_runtime_model"
            package.mkdir()
            (package / "__init__.py").write_text("")
            for name, source in assemble_model_modules(claim for _, _, claim in records).items():
                (package / name).write_text(source)
            sys.path.insert(0, directory)
            try:
                importlib.invalidate_caches()
                model = native_manifest_model.load_compiled_model()
                cls = importlib.import_module("anechoic_runtime_model.project_manifest").ProjectManifest
                self.assertIs(type(model.validate_manifest(self.fields, "C00")), cls)
                component_cls = importlib.import_module("anechoic_runtime_model.component_manifest").ComponentManifest
                fields = {"atom_id": "AN-S-124", "ref_id": "AN-S-124@1", "version": 1,
                          "tier": 0, "component_id": "C01", "name": "Engine"}
                for parent in ("C00", "C1"):
                    self.assertIs(type(model.validate_component_manifest(fields, parent)), component_cls)
                with self.assertRaisesRegex(ValueError, "check_component_manifest"):
                    model.validate_component_manifest(fields | {"name": " "}, "C00")
                self.assertEqual(model.fingerprint, fingerprint)
                self.assertEqual(model.fingerprint, self.model.fingerprint)
            finally:
                sys.path.remove(directory)
                for name in list(sys.modules):
                    if name == "anechoic_runtime_model" or name.startswith("anechoic_runtime_model."):
                        del sys.modules[name]

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
