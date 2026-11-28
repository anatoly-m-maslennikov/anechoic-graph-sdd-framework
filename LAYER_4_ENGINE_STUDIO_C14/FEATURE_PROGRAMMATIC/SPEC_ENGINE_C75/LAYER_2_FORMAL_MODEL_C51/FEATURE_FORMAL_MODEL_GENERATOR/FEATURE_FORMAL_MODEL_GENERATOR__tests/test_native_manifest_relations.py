import importlib
import sys
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch


from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51.FEATURE_FORMAL_MODEL_GENERATOR.assembly.model_class_assembly import (
    assemble_model_modules,
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

    def test_node_axis_is_inherited_and_can_be_overridden(self):
        scope = "MODEL//ANECHOIC <+ Graph/Node >| Persistence"
        domain = (
            "from anechoic.formal_claims import declare_entity\n"
            "declare_entity(entity_name='Node', allowed_axis_values="
            "{'Persistence': ('Artifact', 'Ephemeral')})\n"
        )
        rows = [("axis", scope, domain)]
        for name, parent, fields in (
            ("Node", "", ""),
            ("Artifact", "Node", ", axes={'Persistence': 'Artifact'}"),
            ("Child", "Artifact", ", axes={'Persistence': 'Ephemeral'}"),
            ("Descendant", "Child", ""),
            ("Sibling", "Artifact", ""),
        ):
            imports = (
                f"from anechoic.model import {parent}\n" if parent else ""
            )
            bases = f"({parent})" if parent else ""
            claim = (
                "from anechoic.formal_claims import declare_entity\n"
                f"{imports}class {name}{bases}:\n    pass\n"
                f"declare_entity(entity_name={name!r}, entity_class={name}, "
                f"entity_kind='Primary'{fields})\n"
            )
            rows.append((name, f"MODEL//ANECHOIC <+ Graph/{name}", claim))
        bindings = native_manifest_model.compile_native_bindings(rows, {})
        axes = {
            args["entity_class"]: args.get("axes", {})
            for _, item in bindings["declarations"]
            if "entity_class" in (args := item["arguments"])
        }
        self.assertEqual({}, axes["Node"])
        self.assertEqual({"Persistence": "Ephemeral"}, axes["Descendant"])
        self.assertEqual({"Persistence": "Artifact"}, axes["Sibling"])

    def _check_compiled_component(self, model):
        component_cls = importlib.import_module(
            "anechoic_runtime_model.component_manifest"
        ).ComponentManifest
        fields = {
            "atom_id": "AN-S-124",
            "ref_id": "AN-S-124@1",
            "version": 1,
            "tier": 4,
            "component_id": "C01",
            "name": "Engine",
        }
        for parent in ("C00", "C1"):
            self.assertIs(
                type(model.validate_component_manifest(fields, parent)),
                component_cls,
            )
        with self.assertRaisesRegex(ValueError, "check_component_manifest"):
            model.validate_component_manifest(fields | {"name": " "}, "C00")

    def test_compiled_model_uses_generated_class_objects(self):
        records, _, fingerprint = (
            native_manifest_model.reviewed_model_records()
        )
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory) / "anechoic_runtime_model"
            package.mkdir()
            (package / "__init__.py").write_text("")
            for name, source in assemble_model_modules(
                claim for _, _, claim in records
            ).items():
                (package / name).write_text(source)
            sys.path.insert(0, directory)
            try:
                importlib.invalidate_caches()
                model = native_manifest_model.load_compiled_model()
                cls = importlib.import_module(
                    "anechoic_runtime_model.project_manifest"
                ).ProjectManifest
                self.assertIs(
                    type(model.validate_manifest(self.fields, "C00")), cls
                )
                self._check_compiled_component(model)
                self.assertEqual(model.fingerprint, fingerprint)
                self.assertEqual(model.fingerprint, self.model.fingerprint)
            finally:
                sys.path.remove(directory)
                for name in list(sys.modules):
                    if name == "anechoic_runtime_model" or name.startswith(
                        "anechoic_runtime_model."
                    ):
                        del sys.modules[name]

    def test_reviewed_relations_only(self):
        self.assertEqual(
            self.model.relation_types,
            {
                "CHILD_OF",
                "CHILDREN",
                "CONTAINED_BY",
                "CONTAINS",
                "IS_CLASSIFIED_BY",
                "CLASSIFIES",
                "IS_PROPERTY_OF",
            },
        )
        self.assertEqual(
            self.model.inverses,
            {
                "CHILD_OF": "CHILDREN",
                "CONTAINED_BY": "CONTAINS",
                "IS_CLASSIFIED_BY": "CLASSIFIES",
            },
        )

    def test_upgraded_parent_relation_is_used_for_manifest_validation(self):
        records, _, _ = native_manifest_model.reviewed_model_records()
        upgraded = [
            (
                path,
                subject.replace("CHILD_OF", "IS_CHILD_OF")
                .replace("CHILDREN", "IS_PARENT_FOR")
                .replace("CONTAINED_BY", "IS_CONTAINED_BY"),
                claim.replace("CHILD_OF", "IS_CHILD_OF")
                .replace("CHILDREN", "IS_PARENT_FOR")
                .replace("CONTAINED_BY", "IS_CONTAINED_BY"),
            )
            for path, subject, claim in records
        ]
        model = native_manifest_model._NativeModel(records=upgraded)
        fields = {
            "atom_id": "AN-S-124",
            "ref_id": "AN-S-124@1",
            "version": 1,
            "tier": 4,
            "component_id": "C01",
            "name": "Engine",
        }
        for parent in ("C00", "C01"):
            self.assertEqual(
                model.validate_component_manifest(fields, parent).name,
                "Engine",
            )
        with patch.object(
            model, "_validate", wraps=model._validate
        ) as validate:
            with self.assertRaises(ValueError):
                model.validate_component_seed_manifest({}, "C01")
            self.assertEqual(
                next(iter(validate.call_args_list[1].args[2])), "IS_CHILD_OF"
            )

    def _classified_relation_records(self):
        records, _, _ = native_manifest_model.reviewed_model_records()
        axis = (
            "functional",
            "MODEL//ANECHOIC <+ Graph/Relation >| Functional",
            "from anechoic.formal_claims import declare_entity\n"
            'declare_entity(entity_name="Relation", '
            'allowed_axis_values={"Functional": ("yes", "no")})',
        )
        relation_index = next(
            i
            for i, (_, subject, _) in enumerate(records)
            if subject.endswith("//CHILD_OF")
        )
        path, subject, claim = records[relation_index]
        classified = claim.replace(
            '    inverse_alias="CHILDREN",',
            '    inverse_alias="CHILDREN",\n'
            '    axes={"Functional": "yes"},\n'
            '    inverse_axes={"Functional": "no"},',
        )
        records[relation_index] = (path, subject, classified)
        return records, axis

    def test_relation_axes_use_admitted_values_per_direction(self):
        records, axis = self._classified_relation_records()
        model = native_manifest_model._NativeModel(records=[*records, axis])
        self.assertEqual(
            {"Functional": "yes"}, model.relation_axes["CHILD_OF"]
        )
        self.assertEqual({"Functional": "no"}, model.relation_axes["CHILDREN"])
        self.assertEqual({}, model.relation_axes["CONTAINS"])
        duplicate = (
            "custom.md",
            "MODEL//ANECHOIC <+ Graph/Relation >| ShadowAxis",
            axis[2].replace('("yes", "no")', '("no",)'),
        )
        with self.assertRaisesRegex(
            ValueError, "custom.md: duplicate Relation axis: Functional"
        ):
            native_manifest_model.admit_active_model_records(
                [*records, axis, duplicate]
            )
        with self.assertRaisesRegex(
            ValueError, "custom.md: invalid Relation axis scope: Functional"
        ):
            native_manifest_model.admit_active_model_records(
                [*records, duplicate]
            )
        with self.assertRaisesRegex(
            ValueError, "CHILD_OF: unadmitted Relation axis Functional=yes"
        ):
            native_manifest_model.admit_active_model_records(records)


if __name__ == "__main__":
    unittest.main()
