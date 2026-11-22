"""Validate Model constraint Claim ownership and merging."""

from pathlib import Path
import unittest

PROGRAMMATIC = Path(__file__).resolve().parents[3]


class ConstraintClaimMergeTests(unittest.TestCase):
    def test_property_refinement_requires_the_exact_primary_path(self):
        from FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.model_declaration_sources import (
            _check_manifest_property_bearers,
        )

        records = [
            ("parent", "MODEL//ANECHOIC <+ Node",
             {"arguments": {"entity_kind": "Primary", "entity_name": "Node"}}),
            ("child", "MODEL//ANECHOIC <+ Node//Child",
             {"arguments": {"entity_kind": "Primary", "entity_name": "Child"}}),
        ]
        prop = {"entity_kind": "Property", "entity_name": "Flag", "base_path": "Node",
                "applies_to_entity_classes": ("Node//Child",)}
        records.append(("property", "MODEL//ANECHOIC <+ Node//Child.Flag", {"arguments": prop}))
        _check_manifest_property_bearers(records)
        records[-1] = ("property", "MODEL//ANECHOIC <+ Node.Flag", {"arguments": prop})
        with self.assertRaisesRegex(ValueError, r"expected .*Node//Child.Flag.*actual Node.Flag"):
            _check_manifest_property_bearers(records)
        prop.update(entity_name="Version", base_path="Node.State")
        records[-1] = ("property", "MODEL//ANECHOIC <+ Node//Child.State.Version", {"arguments": prop})
        _check_manifest_property_bearers(records)
        records[-1] = ("property", "MODEL//ANECHOIC <+ Node//Child.Version", {"arguments": prop})
        with self.assertRaisesRegex(ValueError, r"expected .*Node//Child.State.Version.*actual Node//Child.Version"):
            _check_manifest_property_bearers(records)
        prop["applies_to_entity_classes"] = ("Unknown//Child",)
        with self.assertRaisesRegex(ValueError, "unresolved Property refinement owner"):
            _check_manifest_property_bearers(records)

    def test_property_scope_matches_bearer_name_and_refinement(self):
        from FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.model_declaration_sources import (
            _check_manifest_property_bearers,
        )

        owner = ("owner", "MODEL//ANECHOIC <+ Node//Atom",
                 {"arguments": {"entity_kind": "Primary", "entity_name": "Atom"}})
        prop = {"entity_kind": "Property", "entity_name": "Version", "base_path": "Node//Atom.State"}
        def check(subject):
            _check_manifest_property_bearers([owner, ("property", "MODEL//ANECHOIC <+ " + subject,
                                                       {"arguments": prop})])
        check("Node//Atom.State.Version")
        with self.assertRaisesRegex(ValueError, r"expected .*Node//Atom.State.Version.*actual Node//Atom.State.Other"):
            check("Node//Atom.State.Other")
        with self.assertRaisesRegex(ValueError, r"expected .*Node//Atom.State.Version.*actual Node//Atom.Version"):
            check("Node//Atom.Version")
        prop.update(entity_name="Atom ID", base_path="Node//Atom.Identity")
        check("Node//Atom.Identity.Atom ID")

    def test_constraints_are_merged_without_mutating_primary(self):
        from FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.model_declaration_sources import _merge_constraint_claims

        primary = {"kind": "entity", "arguments": {"entity_name": "Atom", "entity_class": "Atom", "entity_kind": "Primary"}}
        constraints = {"kind": "entity", "arguments": {"entity_name": "Atom Constraints", "constraints_for": "Atom", "instance_relation_constraints": {"LINK": {"targets_per_source": 1}}}}
        records = [("owner", "ANECHOIC_MODEL <+ Atom", primary), ("rules", "ANECHOIC_MODEL <+ Rules", constraints)]
        merged = _merge_constraint_claims(records)
        self.assertEqual(merged[0][2]["arguments"]["instance_relation_constraints"], {"LINK": {"targets_per_source": 1}})
        self.assertNotIn("instance_relation_constraints", primary["arguments"])
        for changed, message in [({**constraints, "arguments": constraints["arguments"] | {"constraints_for": "Unknown"}}, "unknown constraint owner"),
                                 ({**constraints, "arguments": constraints["arguments"] | {"entity_name": "Wrong"}}, "invalid constraint Declaration")]:
            with self.assertRaisesRegex(ValueError, message):
                _merge_constraint_claims([records[0], ("rules", records[1][1], changed)])
        with self.assertRaisesRegex(ValueError, "duplicate constraint owner"):
            _merge_constraint_claims([*records, records[1]])



if __name__ == "__main__":
    unittest.main()
