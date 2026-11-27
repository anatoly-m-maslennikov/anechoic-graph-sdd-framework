import ast
import importlib
import sys
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

from pydantic import ConfigDict
from pydantic.dataclasses import dataclass, is_pydantic_dataclass

from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51.FEATURE_FORMAL_MODEL_GENERATOR.FEATURE_FORMAL_MODEL_GENERATOR__shared import (
    assemble_model_classes, assemble_model_modules, load_native_model, native_manifest_model,
)


class NativeManifestModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = load_native_model()
        cls.fields = {"atom_id": "AN-S-123", "ref_id": "AN-S-123@1", "version": 1,
                      "tier": -1, "name": "Anechoic", "prefix": "AN"}

    def test_reviewed_classes_are_pydantic_dataclasses(self):
        self.assertTrue(all(is_pydantic_dataclass(cls) for cls in self.model._types.values()))

    def test_reviewed_manifest_validation(self):
        fields = self.fields | {"parameters": {f"option{i}": i for i in range(18)}}
        self.assertEqual(self.model.validate_manifest(fields, "C00").name, "Anechoic")
        with self.assertRaisesRegex(ValueError, "check_project_manifest"):
            self.model.validate_manifest(fields | {"parameters": fields["parameters"] | {"extra": 1}}, "C00")
        with self.assertRaisesRegex(ValueError, "check_atom_identity"):
            self.model.validate_manifest(fields | {"ref_id": "AN-S-123@2"}, "C00")
        with self.assertRaisesRegex(ValueError, "Project C00"):
            self.model.validate_manifest(fields, "C01")

    def test_project_config_identity_accepts_current_and_legacy_markers(self):
        check = self.model._checks["Atom"][1]
        for marker in ("C", "P"):
            atom_id = f"AN-{marker}-1"
            atom = self.model._types["Project Config Atom"](atom_id=atom_id, version=1, ref_id=f"{atom_id}@1")
            self.assertTrue(check(atom))
        atom.atom_id = "AN-S-1"
        atom.ref_id = "AN-S-1@1"
        self.assertFalse(check(atom))

    def test_reviewed_component_manifest_accepts_optional_boundaries(self):
        fields = {"atom_id": "AN-S-124", "ref_id": "AN-S-124@1", "version": 1,
                  "tier": 4, "component_id": "C01", "name": "Engine"}
        boundaries = {"code": {"imports": ["C02"]}}
        self.assertIsNone(self.model.validate_component_manifest(fields, "C00").boundaries)
        manifest = self.model.validate_component_manifest(fields | {"boundaries": boundaries}, "C00")
        self.assertEqual(manifest.boundaries, boundaries)
        self.assertEqual(self.model.validate_component_manifest(fields | {"tier": 1}, "C00").tier, 1)
        with self.assertRaises(ValueError):
            self.model.validate_component_manifest(fields | {"tier": 0}, "C00")
        with self.assertRaisesRegex(ValueError, "boundaries:"):
            self.model.validate_component_manifest(fields | {"boundaries": ["C02"]}, "C00")

    def test_active_component_manifest_tier_is_used(self):
        records, _, _ = native_manifest_model.reviewed_model_records()
        active = []
        for path, subject, claim in records:
            if subject.endswith('//Component Manifest'):
                claim = claim.replace('allowed_values\": (1, 4)', 'allowed_values\": (0,)')
            active.append((path, subject, claim))
        model = native_manifest_model._NativeModel(records=active)
        fields = {"atom_id": "AN-S-124", "ref_id": "AN-S-124@1", "version": 1,
                  "tier": 0, "component_id": "C01", "name": "Engine"}
        self.assertEqual(model.validate_component_manifest(fields, "C00").tier, 0)
        with self.assertRaises(ValueError):
            model.validate_component_manifest(fields | {"tier": 4}, "C00")

    def test_component_seed_manifest_checks_identity_and_accepts_optional_prose(self):
        fields = {"atom_id": "AN-S-125", "ref_id": "AN-S-125@1", "version": 1,
                  "tier": 2, "component_seed_id": "CS123"}
        seed = self.model.validate_component_seed_manifest(fields, "C01")
        self.assertEqual((seed.purpose, seed.contract, seed.solution), (None, None, None))
        prose = {"purpose": "Purpose", "contract": "Contract", "solution": "Solution"}
        seed = self.model.validate_component_seed_manifest(fields | prose, "C01")
        self.assertEqual((seed.purpose, seed.contract, seed.solution), tuple(prose.values()))
        for seed_id in ("CS", "CS１２", "pkg1", "CS1x"):
            with self.subTest(seed_id=seed_id), self.assertRaisesRegex(ValueError, "check_component_seed_manifest"):
                self.model.validate_component_seed_manifest(fields | {"component_seed_id": seed_id}, "C01")

    def test_release_workflow_setting_is_an_optional_exact_boolean(self):
        self.model.validate_manifest(self.fields | {"parameters": {"project_mcp": {}}}, "C00")
        for enabled in (True, False):
            with self.subTest(enabled=enabled):
                parameters = {"project_mcp": {"release_workflows_enabled": enabled}}
                manifest = self.model.validate_manifest(self.fields | {"parameters": parameters}, "C00")
                self.assertIs(manifest.parameters["project_mcp"]["release_workflows_enabled"], enabled)
        for invalid in (1, "true", None):
            with self.subTest(invalid=invalid):
                parameters = {"project_mcp": {"release_workflows_enabled": invalid}}
                with self.assertRaisesRegex(ValueError, "check_project_manifest"):
                    self.model.validate_manifest(self.fields | {"parameters": parameters}, "C00")

    def test_derived_ref_id_input_is_checked_and_not_passed_to_constructor(self):
        @dataclass(config=ConfigDict(strict=True, extra="forbid"))
        class StrictAtom:
            atom_id: str
            version: int

            @property
            def ref_id(self):
                return f"{self.atom_id}@{self.version}"

        def validate(cls, *, properties, **kwargs):
            return cls(**properties)

        with patch.dict(self.model._types, {"Strict": StrictAtom}), patch.object(
            native_manifest_model, "validate_model_instance", side_effect=validate
        ):
            fields = {"atom_id": "AN-S-123", "version": 1, "ref_id": "AN-S-123@1"}
            self.assertEqual(self.model._validate("Strict", fields, {}).ref_id, fields["ref_id"])
            self.assertIn("ref_id", fields)
            with self.assertRaisesRegex(ValueError, "differs from derived"):
                self.model._validate("Strict", fields | {"ref_id": "AN-S-123@2"}, {})

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
        self.assertTrue(any(subject.endswith("//Project Config Atom") and "class ProjectConfigAtom" in claim
                            for _, subject, claim in reviewed))
        self.assertFalse(any("PMETA Atom" in subject or "PMETAAtom" in claim
                             for _, subject, claim in reviewed))
        self.assertFalse(any(subject.endswith("//Component Purpose") for _, subject, _ in reviewed))
        self.assertTrue(any(subject.endswith("//Purpose") for _, subject, _ in reviewed))
        self.assertTrue(any(subject.endswith("//Project Goal") for _, subject, _ in reviewed))
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

    def test_separate_reviewed_check_and_constraints_follow_their_owner(self):
        records, _, _ = native_manifest_model.reviewed_model_records()
        index = next(i for i, (_, _, claim) in enumerate(records) if "def check_project_manifest(" in claim)
        path, subject, claim = records[index]
        tree = ast.parse(claim)
        function = next(node for node in tree.body if isinstance(node, ast.FunctionDef))
        call = tree.body[-1].value
        lines = claim.splitlines(keepends=True)
        check_source = "".join(lines[function.lineno - 1:function.end_lineno])
        cls = next(node for node in tree.body if isinstance(node, ast.ClassDef))
        start = min([cls.lineno, *(item.lineno for item in cls.decorator_list)])
        class_source = "".join(lines[:start - 1]) + f"class {cls.name}({ast.unparse(cls.bases[0])}):\n    pass\n\n"
        kept = [ast.unparse(keyword) for keyword in call.keywords if keyword.arg in {"entity_name", "entity_class"}]
        primary = class_source + "declare_entity(" + ", ".join(kept) + ", entity_kind='Primary')\n"
        moved = [ast.unparse(keyword) for keyword in call.keywords if keyword.arg not in {"entity_name", "entity_class"}]
        target = "Node//Artifact//Atom//Spec Atom//Manifest//Project Manifest"
        constraint = ("from anechoic.formal_claims import declare_entity\n"
                      "from anechoic.model import ProjectManifest\n" + check_source + "\n"
                      "declare_entity(entity_name='Project Manifest Constraints', constraints_for=" + repr(target)
                      + ", " + ", ".join(moved) + ")\n")
        active = [*records[:index], (path, subject, primary), *records[index + 1:],
                  ("constraint", "ANECHOIC_MODEL <+ Project Manifest Constraints", constraint)]
        reviewed_classes = assemble_model_classes(claim for _, _, claim in records)
        with patch.object(native_manifest_model, "assemble_model_classes", return_value=reviewed_classes):
            model = native_manifest_model._NativeModel(records=active)
        self.assertEqual(model.validate_manifest(self.fields, "C00").name, "Anechoic")
        with self.assertRaisesRegex(ValueError, "instance check differs"):
            native_manifest_model.admit_active_model_records(
                [*active[:-1], ("constraint", active[-1][1], constraint.replace("manifest.name.strip()", "True"))])
        with self.assertRaisesRegex(ValueError, "unknown constraint owner"):
            native_manifest_model.admit_active_model_records(
                [*active[:-1], ("constraint", active[-1][1], constraint.replace(target, "Unknown"))])

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
                          "tier": 4, "component_id": "C01", "name": "Engine"}
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

    def test_upgraded_parent_relation_is_used_for_manifest_validation(self):
        records, _, _ = native_manifest_model.reviewed_model_records()
        upgraded = [(path, subject.replace("CHILD_OF", "IS_CHILD_OF").replace("CHILDREN", "IS_PARENT_FOR").replace("CONTAINED_BY", "IS_CONTAINED_BY"),
                     claim.replace("CHILD_OF", "IS_CHILD_OF").replace("CHILDREN", "IS_PARENT_FOR").replace("CONTAINED_BY", "IS_CONTAINED_BY"))
                    for path, subject, claim in records]
        model = native_manifest_model._NativeModel(records=upgraded)
        fields = {"atom_id": "AN-S-124", "ref_id": "AN-S-124@1", "version": 1,
                  "tier": 4, "component_id": "C01", "name": "Engine"}
        for parent in ("C00", "C01"):
            self.assertEqual(model.validate_component_manifest(fields, parent).name, "Engine")
        with patch.object(model, "_validate", wraps=model._validate) as validate:
            with self.assertRaises(ValueError):
                model.validate_component_seed_manifest({}, "C01")
            self.assertEqual(next(iter(validate.call_args_list[1].args[2])), "IS_CHILD_OF")

    def test_relation_axes_use_admitted_values_per_direction(self):
        records, _, _ = native_manifest_model.reviewed_model_records()
        axis = (
            "functional",
            "MODEL//ANECHOIC <+ Graph/Relation >| Functional",
            'from anechoic.formal_claims import declare_entity\n'
            'declare_entity(entity_name="Relation", allowed_axis_values={"Functional": ("yes", "no")})',
        )
        relation_index = next(i for i, (_, subject, _) in enumerate(records) if subject.endswith("//CHILD_OF"))
        path, subject, claim = records[relation_index]
        classified = claim.replace(
            '    inverse_alias="CHILDREN",',
            '    inverse_alias="CHILDREN",\n'
            '    axes={"Functional": "yes"},\n'
            '    inverse_axes={"Functional": "no"},',
        )
        records[relation_index] = (path, subject, classified)
        model = native_manifest_model._NativeModel(records=[*records, axis])
        self.assertEqual({"Functional": "yes"}, model.relation_axes["CHILD_OF"])
        self.assertEqual({"Functional": "no"}, model.relation_axes["CHILDREN"])
        self.assertEqual({}, model.relation_axes["CONTAINS"])
        duplicate = ("custom.md", "MODEL//ANECHOIC <+ Graph/Relation >| ShadowAxis",
                     axis[2].replace('("yes", "no")', '("no",)'))
        with self.assertRaisesRegex(ValueError, "custom.md: duplicate Relation axis: Functional"):
            native_manifest_model.admit_active_model_records([*records, axis, duplicate])
        with self.assertRaisesRegex(ValueError, "custom.md: invalid Relation axis scope: Functional"):
            native_manifest_model.admit_active_model_records([*records, duplicate])
        with self.assertRaisesRegex(ValueError, "CHILD_OF: unadmitted Relation axis Functional=yes"):
            native_manifest_model.admit_active_model_records(records)


if __name__ == "__main__":
    unittest.main()
