"""Property declaration rejection scenarios."""

from importlib import import_module

_cases = import_module(
    "FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51."
    "FEATURE_FORMAL_MODEL_GENERATOR.FEATURE_FORMAL_MODEL_GENERATOR__tests.properties."
    "_manifest_property_fields_cases"
)
assemble_model_classes = _cases.assemble_model_classes
primary = _cases.primary
prop = _cases.prop


class PropertyRejectionCases:
    def test_rejects_non_primary_class_and_invalid_overrides(self):
        claims = self.claims()
        self._check_class_rejections(claims)
        self._check_group_rejections(claims)
        self._check_identity_rejections(claims)

    def _check_class_rejections(self, claims):
        with self.assertRaisesRegex(ValueError, "whitelisted"):
            assemble_model_classes(
                claims
                + [primary("Bad", extra=", instance_population_cardinality=1")]
            )
        with self.assertRaisesRegex(ValueError, "subclass"):
            assemble_model_classes(
                claims
                + [
                    prop(
                        "Atom ID",
                        "Node//Artifact//Atom.Identity",
                        ", applies_to_entity_classes=('Node',)",
                    )
                ]
            )
        with self.assertRaisesRegex(ValueError, "ambiguous"):
            assemble_model_classes(
                claims + [primary("Other", entity_name="Atom")]
            )

    def _check_group_rejections(self, claims):
        with self.assertRaisesRegex(
            ValueError, "State: expected declared children"
        ):
            assemble_model_classes(
                [
                    claim
                    for claim in claims
                    if "entity_name='Updated At'" not in claim
                ]
            )
        with self.assertRaisesRegex(
            ValueError, "State: expected declared children"
        ):
            assemble_model_classes(
                [
                    claim.replace(
                        "('Version', 'Status', 'Updated At')",
                        "('Version', 'Status')",
                    )
                    for claim in claims
                ]
            )
        with self.assertRaisesRegex(ValueError, "must be declared at State"):
            assemble_model_classes(
                claims
                + [
                    prop(
                        "UpdatedAt",
                        "Node//Artifact//Atom",
                        ", value_format=datetime",
                    )
                ]
            )

    def _check_identity_rejections(self, claims):
        with self.assertRaisesRegex(
            ValueError, "identity Property does not exist"
        ):
            assemble_model_classes(
                [primary("Base", extra=", identity_properties=('Missing',)")]
            )
        with self.assertRaisesRegex(ValueError, "requires its derived"):
            assemble_model_classes(
                [
                    claim.replace(
                        ", derived_from_properties=('Identity.Atom ID', "
                        "'State.Version', 'State.Status')",
                        "",
                    )
                    for claim in claims
                ]
            )
        with self.assertRaisesRegex(ValueError, "cannot be redeclared"):
            assemble_model_classes(
                claims
                + [
                    prop(
                        "Ref ID",
                        "Node//Artifact//Atom//Plan",
                        ", value_format=str",
                    )
                ]
            )
