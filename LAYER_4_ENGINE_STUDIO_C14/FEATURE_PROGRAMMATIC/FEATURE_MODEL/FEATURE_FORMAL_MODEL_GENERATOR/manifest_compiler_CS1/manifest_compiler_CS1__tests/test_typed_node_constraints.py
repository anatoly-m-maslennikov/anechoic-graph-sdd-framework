"""Check constraint lowering for both Model address separators."""
import unittest

from FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.manifest_compiler_CS1.typed_node_constraints import lower_node_constraints
from FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.model_constraint_claims import _merge_constraint_claims
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import parse_native_model_claim


class TypedNodeConstraintsTests(unittest.TestCase):
    def test_model_relation_constraint_is_lowered_validated_and_merged(self):
        path = "Node//Projection"
        subject = "MODEL//ANECHOIC <+ " + path
        text = ("from anechoic.model import Projection, NodeConstraints\n"
                "class Constraints(NodeConstraints):\n"
                "    bearer = Projection\n"
                "    model_relation_constraints = {'IS_PROPERTY_OF': {'targets_per_source': 0}}\n")
        lowered = lower_node_constraints(text, subject + ".Constraints", {"Projection": path})
        constraint = parse_native_model_claim(lowered)
        owner = {"kind": "entity", "arguments": {"entity_name": "Projection", "entity_class": "Projection", "entity_kind": "Primary"}}
        merged = _merge_constraint_claims([("owner", subject, owner), ("constraint", subject + ".Constraints", constraint)])
        self.assertEqual(merged[0][2]["arguments"]["model_relation_constraints"],
                         {"IS_PROPERTY_OF": {"targets_per_source": 0}})
        with self.assertRaises(ValueError):
            parse_native_model_claim(lower_node_constraints(text.replace("targets_per_source", "invalid_key"), subject + ".Constraints", {"Projection": path}))
        with self.assertRaisesRegex(ValueError, "imported known Model classes"):
            lower_node_constraints(text.replace("{'targets_per_source': 0}", "{'target_entity_paths': ('Projection',)}"), subject + ".Constraints", {"Projection": path})

    def test_constraint_name_matches_owner_for_both_hierarchies(self):
        text = "from anechoic.model import Atom, NodeConstraints\nclass Constraints(NodeConstraints):\n    bearer = Atom\n"
        for path in ("Node//Artifact//Atom", "Graph/Node//Artifact/Content/Atom"):
            with self.subTest(path=path):
                subject = "MODEL//ANECHOIC <+ " + path
                lowered = lower_node_constraints(text, subject + ".Constraints", {"Atom": path})
                owner = {"kind": "entity", "arguments": {"entity_name": "Atom", "entity_class": "Atom", "entity_kind": "Primary"}}
                merged = _merge_constraint_claims([("owner", subject, owner), ("constraint", subject + ".Constraints", parse_native_model_claim(lowered))])
                self.assertEqual(len(merged), 1)
                with self.assertRaisesRegex(ValueError, "bearer does not match"):
                    lower_node_constraints(text, subject + "/Wrong.Constraints", {"Atom": path})
