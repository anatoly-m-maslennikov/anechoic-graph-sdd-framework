"""Bind actual parsed Declarations to generated Model classes."""

from pathlib import Path
import sys
import unittest

PROGRAMMATIC = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(PROGRAMMATIC), str(PROGRAMMATIC / "FEATURE_TOOLS")]

from FEATURE_FORMAL_MODEL_ENGINE.native_model_claim import parse_native_model_claim
from FEATURE_MODEL.FEATURE_MODEL_VALIDATION.model_declaration_bindings import bind_model_declarations
from FEATURE_MODEL.FEATURE_MODEL_VALIDATION.model_relation_validation import validate_model_relations


class Node:
    pass


class Container(Node):
    pass


def claim(name, parent="", rules="", uniqueness=""):
    model_import = f"from anechoic.model import {parent}\n" if parent else ""
    base = f"({parent})" if parent else ""
    return parse_native_model_claim(
        "from anechoic.formal_claims import declare_entity\n" + model_import
        + f"class {name}{base}:\n    pass\n"
        + f"declare_entity(entity_name='{name}', entity_class={name}{rules}{uniqueness})\n"
    )


class ModelDeclarationBindingsTests(unittest.TestCase):
    def test_binds_endpoint_types_relations_and_population_constraints(self):
        node = claim("Node", rules=", instance_relation_constraints={"
                     "'LINKS': {'target_entity_paths': ('Node',), 'targets_per_source': 1}}",
                     uniqueness=", population_unique_constraints=({'keys': ('ID',)},)")
        child = claim("Container", "Node", rules=", instance_relation_constraints={"
                      "'LINKS': {'target_entity_paths': ('Node',), 'targets_per_source': 0}}")
        bindings = bind_model_declarations([
            ("ANECHOIC_MODEL <+ Node", node),
            ("ANECHOIC_MODEL <+ Node/Container", child),
        ], {"Node": Node, "Container": Container})
        relations, types, populations = bindings
        self.assertIs(types["Node"], Node)
        self.assertIs(types["Node/Container"], Container)
        self.assertEqual(populations[Node], ({"keys": ("ID",)},))
        validate_model_relations(Container, {}, relations, types)
        with self.assertRaisesRegex(ValueError, "target count"):
            validate_model_relations(Container, {"LINKS": [Node()]}, relations, types)

    def test_rejects_mismatch_duplicates_and_unknown_targets(self):
        node = claim("Node")
        child = claim("Container", "Node", rules=", instance_relation_constraints={"
                      "'LINKS': {'target_entity_paths': ('Missing',)}}")
        with self.assertRaisesRegex(ValueError, "Invalid Model class binding"):
            bind_model_declarations([("ANECHOIC_MODEL <+ Other", node)], {"Node": Node})
        with self.assertRaisesRegex(ValueError, "Duplicate Model class binding"):
            bind_model_declarations([("ANECHOIC_MODEL <+ Node", node)] * 2, {"Node": Node})
        with self.assertRaisesRegex(ValueError, "unresolved or ambiguous target kind"):
            bind_model_declarations([
                ("ANECHOIC_MODEL <+ Node", node),
                ("ANECHOIC_MODEL <+ Node/Container", child),
            ], {"Node": Node, "Container": Container})

    def test_rejects_different_python_inheritance(self):
        wrong = type("Container", (), {})
        with self.assertRaisesRegex(ValueError, "inheritance differs"):
            bind_model_declarations([("ANECHOIC_MODEL <+ Node/Container", claim("Container", "Node"))],
                                    {"Container": wrong})
        fake_node = type("Node", (), {})
        with self.assertRaisesRegex(ValueError, "inheritance differs"):
            bind_model_declarations([("ANECHOIC_MODEL <+ Node/Container", claim("Container", "Node"))],
                                    {"Container": Container, "Node": fake_node})

    def test_binds_uniqueness_declared_on_a_property(self):
        prop = parse_native_model_claim(
            "from anechoic.formal_claims import declare_entity\n"
            "declare_entity(entity_name='ID', relation_name='IS_PROPERTY_OF', base_path='Node', "
            "population_unique_constraints=({'keys': ('ID',)},))\n"
        )
        subject = ("ANECHOIC_MODEL <+ Node.ID", prop)
        rows = [("ANECHOIC_MODEL <+ Node", claim("Node")), subject]
        _, _, populations = bind_model_declarations(rows, {"Node": Node})
        self.assertEqual(populations[Node], ({"keys": ("ID",)},))
        with self.assertRaisesRegex(ValueError, "Unresolved or ambiguous population kind"):
            bind_model_declarations([subject], {})


if __name__ == "__main__":
    unittest.main()
