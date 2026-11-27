"""Separate Primary and Property declarations compile into public classes."""

import importlib
from dataclasses import asdict
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from pydantic import ValidationError

_shared = __import__(
    "FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51."
    "FEATURE_FORMAL_MODEL_GENERATOR.FEATURE_FORMAL_MODEL_GENERATOR__shared",
    fromlist=["assemble_model_classes", "assemble_model_modules"],
)
assemble_model_classes = _shared.assemble_model_classes
assemble_model_modules = _shared.assemble_model_modules


_cases = importlib.import_module(
    "FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51."
    "FEATURE_FORMAL_MODEL_GENERATOR.FEATURE_FORMAL_MODEL_GENERATOR__tests."
    "_manifest_property_fields_cases"
)
_rejections = importlib.import_module(
    "FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51."
    "FEATURE_FORMAL_MODEL_GENERATOR.FEATURE_FORMAL_MODEL_GENERATOR__tests."
    "_manifest_property_rejection_cases"
)
PropertyRejectionCases = _rejections.PropertyRejectionCases
PropertyInheritanceCases = _cases.PropertyInheritanceCases
primary = _cases.primary
prop = _cases.prop


class ManifestPropertyFieldsTests(
    PropertyRejectionCases, PropertyInheritanceCases, unittest.TestCase
):
    def claims(self):
        atom = "Node//Artifact//Atom"
        return [
            primary("Node"),
            primary("Artifact", "Node"),
            primary(
                "Atom",
                "Artifact",
                extra=", identity_properties=('Identity.Atom ID',)",
            ),
            primary(
                "Plan",
                "Atom",
                extra=", identity_properties=('State.Version',)",
            ),
            prop(
                "Identity",
                atom,
                ", value_cardinality=0, "
                "allowed_dependent_property_names=('Atom ID',)",
            ),
            prop("Atom ID", atom + ".Identity", ", value_format=str"),
            prop(
                "State",
                atom,
                ", value_cardinality=0, "
                "allowed_dependent_property_names=('Version', 'Status', "
                "'Updated At')",
            ),
            prop(
                "Version",
                atom + ".State",
                ", value_format=int, minimum_value=1",
            ),
        ] + self._remaining_claims(atom)

    def _remaining_claims(self, atom):
        return [
            prop(
                "Status",
                atom + ".State",
                ", value_format=str, "
                "field_options={'kw_only': True}, allowed_values=('draft', "
                "'active')",
            ),
            prop("Updated At", atom + ".State", ", value_format=datetime"),
            prop(
                "Tags",
                atom,
                ", value_format=list[str] | None, field_options={'default': "
                "None, 'kw_only': True}",
            ),
            prop(
                "Attributes",
                atom,
                ", value_format=dict[str, str], "
                "field_options={'default_factory': dict, 'kw_only': True}",
            ),
            prop(
                "Ref ID",
                atom,
                ", value_format=str, "
                "derived_from_properties=('Identity.Atom ID', "
                "'State.Version', 'State.Status')",
            ),
            prop(
                "Status",
                atom + ".State",
                ", applies_to_entity_classes=('Node//Artifact//Atom//Plan',), "
                "allowed_values=('draft', 'active', 'done')",
            ),
        ]

    def test_aggregate_and_modules_emit_fields_on_correct_classes(self):
        claims = self.claims()
        modules = assemble_model_modules(claims)
        self.assertIn("class Atom(Artifact)", modules["atom.py"])
        self.assertIn("class Plan(Atom)", modules["plan.py"])
        self.assertNotIn("version:", modules["plan.py"])
        with TemporaryDirectory() as folder:
            package = Path(folder) / "model_fixture"
            package.mkdir()
            (package / "__init__.py").write_text("")
            for filename, source in modules.items():
                (package / filename).write_text(source)
            with patch.object(sys, "path", [folder, *sys.path]):
                try:
                    atom = importlib.import_module("model_fixture.atom").Atom
                    plan = importlib.import_module("model_fixture.plan").Plan
                    self._check_fields(atom, plan)
                    self._check_instance(atom, plan)
                finally:
                    for name in list(sys.modules):
                        if name == "model_fixture" or name.startswith(
                            "model_fixture."
                        ):
                            del sys.modules[name]

    def _check_fields(self, atom, plan):
        self.assertTrue(issubclass(plan, atom))
        self.assertEqual(
            set(atom.__dataclass_fields__),
            {
                "atom_id",
                "version",
                "status",
                "updated_at",
                "tags",
                "attributes",
            },
        )
        self.assertEqual(
            atom.__dataclass_fields__["version"].metadata["minimum_value"],
            1,
        )
        self.assertEqual(
            plan.__dataclass_fields__["status"].metadata["allowed_values"],
            ("draft", "active", "done"),
        )
        self.assertIs(
            atom.__dataclass_fields__["attributes"].default_factory,
            dict,
        )
        self.assertTrue(atom.__dataclass_fields__["tags"].kw_only)

    def _check_instance(self, atom, plan):
        from datetime import datetime

        values = {
            "atom_id": "AN-S-1",
            "version": 2,
            "updated_at": datetime.now(),
        }
        instance = plan(**values, status="draft")
        self.assertEqual(instance.ref_id, "AN-S-1@2-draft")
        instance.status = "active"
        self.assertEqual(instance.ref_id, "AN-S-1@2")
        instance.version = 3
        instance.status = "archived"
        self.assertEqual(instance.ref_id, "AN-S-1@3")
        self.assertNotIn("ref_id", asdict(instance))
        self.assertNotIn("ref_id", vars(instance))
        with self.assertRaises(AttributeError):
            instance.ref_id = "incorrect"
        with self.assertRaisesRegex(ValidationError, "ref_id"):
            atom(**values, status="active", ref_id="incorrect")

    def test_primary_classification_does_not_add_dataclass_field(self):
        claims = self.claims()
        classified = [
            claim.replace(
                "entity_kind='Primary'",
                "entity_kind='Primary', axes={'Temporal Kind': 'Continuant'}",
                1,
            )
            if "class Atom(" in claim
            else claim
            for claim in claims
        ]
        self.assertEqual(
            assemble_model_classes(claims), assemble_model_classes(classified)
        )

    def test_valueless_dynamic_group_does_not_add_dataclass_field(self):
        claims = self.claims()
        before = assemble_model_classes(claims)
        content = prop(
            "Content",
            "Node//Artifact//Atom",
            ", value_cardinality=0, dependent_property_cardinality=0",
        )
        self.assertEqual(before, assemble_model_classes(claims + [content]))

    def test_identity_resolves_every_segment_from_the_primary_entity(self):
        claims = self.claims()
        self._check_identity_paths(claims)
        nested = [
            primary(
                "Entity",
                extra=", identity_properties=('Identity.Revision.Version',)",
            ),
            prop(
                "Identity",
                "Entity",
                ", value_cardinality=0, "
                "allowed_dependent_property_names=('Revision',)",
            ),
            prop(
                "Revision",
                "Entity.Identity",
                ", value_cardinality=0, "
                "allowed_dependent_property_names=('Version',)",
            ),
            prop("Version", "Entity.Identity.Revision", ", value_format=int"),
        ]
        self.assertIn("version: int", assemble_model_classes(nested))
        with self.assertRaisesRegex(
            ValueError, "Unresolved Property group bearer"
        ):
            assemble_model_classes([nested[0], nested[1], nested[3]])

    def _check_identity_paths(self, claims):
        for path in (
            "Atom ID",
            "Imaginary.Atom ID",
            "State.Atom ID",
            "Atom.Identity.Atom ID",
        ):
            with (
                self.subTest(path=path),
                self.assertRaisesRegex(
                    ValueError, "identity Property does not exist"
                ),
            ):
                assemble_model_classes(
                    [
                        claim.replace(
                            "identity_properties=('Identity.Atom ID',)",
                            f"identity_properties=({path!r},)",
                        )
                        for claim in claims
                    ]
                )

    def test_declared_field_under_an_open_property_group(self):
        claims = [
            primary("Entity"),
            prop(
                "Content",
                "Entity",
                ", value_cardinality=0, "
                "dependent_property_cardinality={'minimum': 0, "
                "'maximum': None}",
            ),
            prop("Summary", "Entity.Content", ", value_format=str"),
        ]
        self.assertIn("summary: str", assemble_model_classes(claims))
        with self.assertRaisesRegex(
            ValueError, "Unresolved Property group bearer"
        ):
            assemble_model_classes([claims[0], claims[2]])


if __name__ == "__main__":
    unittest.main()
