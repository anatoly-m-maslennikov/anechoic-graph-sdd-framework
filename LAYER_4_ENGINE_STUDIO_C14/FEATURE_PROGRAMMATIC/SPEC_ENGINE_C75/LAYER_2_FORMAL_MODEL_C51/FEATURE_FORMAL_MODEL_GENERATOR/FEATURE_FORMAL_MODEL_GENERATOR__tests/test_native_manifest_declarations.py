import ast
import unittest
from unittest.mock import patch


from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51.FEATURE_FORMAL_MODEL_GENERATOR.assembly.model_class_assembly import (
    assemble_model_classes,
)
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51.FEATURE_FORMAL_MODEL_GENERATOR.native.native_manifest_model import (
    load_native_model,
)
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51.FEATURE_FORMAL_MODEL_GENERATOR.native import (
    native_manifest_model,
)


class NativeManifestModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = load_native_model()
        cls.fields = {
            "atom_id": "AN-S-123",
            "ref_id": "AN-S-123@1",
            "version": 1,
            "tier": -1,
            "name": "Anechoic",
            "prefix": "AN",
        }

    def test_reviewed_declarations(self):
        reviewed, _, reviewed_hash = (
            native_manifest_model.reviewed_model_records()
        )
        self.assertTrue(
            any(
                subject.endswith("//Project Config Atom")
                and "class ProjectConfigAtom" in claim
                for _, subject, claim in reviewed
            )
        )
        self.assertFalse(
            any(
                "PMETA Atom" in subject or "PMETAAtom" in claim
                for _, subject, claim in reviewed
            )
        )
        self.assertFalse(
            any(
                subject.endswith("//Component Purpose")
                for _, subject, _ in reviewed
            )
        )
        self.assertTrue(
            any(subject.endswith("//Purpose") for _, subject, _ in reviewed)
        )
        self.assertTrue(
            any(
                subject.endswith("//Project Goal")
                for _, subject, _ in reviewed
            )
        )

    def test_active_declarations_drive_model_but_callbacks_stay_reviewed(self):
        reviewed, _, reviewed_hash = (
            native_manifest_model.reviewed_model_records()
        )
        active = tuple(
            (f"Meta_C9/AN-S-{i}-SPEC--claim.md@1", subject, claim)
            for i, (_, subject, claim) in enumerate(reviewed, 1)
        )
        admit = native_manifest_model.admit_active_model_records
        _, _, active_hash = admit(active)
        self.assertNotEqual(active_hash, reviewed_hash)
        self.assertEqual(active_hash, admit(reversed(active))[2])
        with self.assertRaisesRegex(ValueError, "unique Model Declaration"):
            admit((*active, active[0]))
        self._check_active_callbacks(active, admit)

    def _check_active_callbacks(self, active, admit):
        index = next(
            i
            for i, (_, _, claim) in enumerate(active)
            if "def check_project_manifest(" in claim
        )
        path, subject, claim = active[index]
        changed = claim.replace(
            "\ndef check_project_manifest(",
            "    extra_field: int = 10\n\ndef check_project_manifest(",
            1,
        )
        self.assertNotEqual(changed, claim)
        active_model = native_manifest_model._NativeModel(
            records=(
                *active[:index],
                (path, subject, changed),
                *active[index + 1 :],
            )
        )
        self.assertEqual(
            active_model.validate_manifest(self.fields, "C00").extra_field, 10
        )
        with self.assertRaisesRegex(ValueError, "check_project_manifest"):
            excessive = self.fields | {
                "parameters": {f"option{i}": i for i in range(19)}
            }
            active_model.validate_manifest(excessive, "C00")
        with self.assertRaisesRegex(
            ValueError, "missing reviewed instance checks"
        ):
            admit((*active[:index], *active[index + 1 :]))
        self._check_changed_callback(
            active, admit, index, path, subject, claim
        )

    def _check_changed_callback(
        self, active, admit, index, path, subject, claim
    ):
        changed = claim.replace(
            "def check_project_manifest(", "def changed_check(", 1
        )
        changed = changed.replace(
            "instance_check=check_project_manifest",
            "instance_check=changed_check",
            1,
        )
        with self.assertRaisesRegex(ValueError, "instance check differs"):
            admit(
                (
                    *active[:index],
                    (path, subject, changed),
                    *active[index + 1 :],
                )
            )

    def _constraint_primary(self):
        records, _, _ = native_manifest_model.reviewed_model_records()
        index = next(
            i
            for i, (_, _, claim) in enumerate(records)
            if "def check_project_manifest(" in claim
        )
        path, subject, claim = records[index]
        tree = ast.parse(claim)
        function = next(
            node for node in tree.body if isinstance(node, ast.FunctionDef)
        )
        call = tree.body[-1].value
        lines = claim.splitlines(keepends=True)
        check_source = "".join(
            lines[function.lineno - 1 : function.end_lineno]
        )
        cls = next(
            node for node in tree.body if isinstance(node, ast.ClassDef)
        )
        start = min(
            [cls.lineno, *(item.lineno for item in cls.decorator_list)]
        )
        class_source = (
            "".join(lines[: start - 1])
            + f"class {cls.name}({ast.unparse(cls.bases[0])}):\n    pass\n\n"
        )
        kept = [
            ast.unparse(keyword)
            for keyword in call.keywords
            if keyword.arg in {"entity_name", "entity_class"}
        ]
        primary = (
            class_source
            + "declare_entity("
            + ", ".join(kept)
            + ", entity_kind='Primary')\n"
        )
        return records, index, path, subject, primary, call, check_source

    def _constraint_records(self):
        records, index, path, subject, primary, call, check_source = (
            self._constraint_primary()
        )
        moved = [
            ast.unparse(keyword)
            for keyword in call.keywords
            if keyword.arg not in {"entity_name", "entity_class"}
        ]
        target = "Node//Artifact//Atom//Spec Atom//Manifest//Project Manifest"
        constraint = (
            "from anechoic.formal_claims import declare_entity\n"
            "from anechoic.model import ProjectManifest\n"
            + check_source
            + "\n"
            "declare_entity(entity_name='Project Manifest Constraints', "
            "constraints_for=" + repr(target) + ", " + ", ".join(moved) + ")\n"
        )
        active = [
            *records[:index],
            (path, subject, primary),
            *records[index + 1 :],
            (
                "constraint",
                "ANECHOIC_MODEL <+ Project Manifest Constraints",
                constraint,
            ),
        ]
        return records, active, constraint, target

    def test_separate_reviewed_check_and_constraints_follow_their_owner(self):
        records, active, constraint, target = self._constraint_records()
        reviewed_classes = assemble_model_classes(
            claim for _, _, claim in records
        )
        with patch.object(
            native_manifest_model,
            "assemble_model_classes",
            return_value=reviewed_classes,
        ):
            model = native_manifest_model._NativeModel(records=active)
        self.assertEqual(
            model.validate_manifest(self.fields, "C00").name, "Anechoic"
        )
        with self.assertRaisesRegex(ValueError, "instance check differs"):
            native_manifest_model.admit_active_model_records(
                [
                    *active[:-1],
                    (
                        "constraint",
                        active[-1][1],
                        constraint.replace("manifest.name.strip()", "True"),
                    ),
                ]
            )
        with self.assertRaisesRegex(ValueError, "unknown constraint owner"):
            native_manifest_model.admit_active_model_records(
                [
                    *active[:-1],
                    (
                        "constraint",
                        active[-1][1],
                        constraint.replace(target, "Unknown"),
                    ),
                ]
            )


if __name__ == "__main__":
    unittest.main()
