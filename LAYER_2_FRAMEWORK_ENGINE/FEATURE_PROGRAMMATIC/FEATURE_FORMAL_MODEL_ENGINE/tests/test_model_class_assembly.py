"""Class assembly uses native Python inheritance without executing Claims."""

from graphlib import CycleError
from pathlib import Path
import sys
import unittest

PROGRAMMATIC = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROGRAMMATIC))

from FEATURE_FORMAL_MODEL_ENGINE.model_class_assembly import assemble_model_classes


def declaration(name, parent=None):
    base_import = f"from caprmedio.model import {parent}\n" if parent else ""
    base = f"({parent})" if parent else ""
    return ("from caprmedio.formal_claims import declare_entity\n"
            "from dataclasses import dataclass\n" + base_import +
            f"@dataclass\nclass {name}{base}:\n    pass\n"
            f"declare_entity(entity_name='{name}', entity_class={name})\n")


class ModelClassAssemblyTests(unittest.TestCase):
    def test_inheritance_is_ordered_and_importable(self):
        source = assemble_model_classes([declaration("Project", "ScopeUnit"), declaration("ScopeUnit")])
        namespace = {}
        exec(compile(source, "model.py", "exec"), namespace)
        self.assertTrue(issubclass(namespace["Project"], namespace["ScopeUnit"]))
        self.assertNotIn("caprmedio.model", source)

    def test_missing_parent_and_cycle_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "Missing Model parent"):
            assemble_model_classes([declaration("Project", "ScopeUnit")])
        with self.assertRaises(CycleError):
            assemble_model_classes([declaration("A", "B"), declaration("B", "A")])

    def test_legacy_and_duplicate_declarations_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "native Python"):
            assemble_model_classes(["property_rule(address='A')"])
        with self.assertRaisesRegex(ValueError, "Duplicate Model class"):
            assemble_model_classes([declaration("A"), declaration("A")])

    def test_plain_claim_class_becomes_dataclass(self):
        claim = (
            "from caprmedio.formal_claims import declare_entity\n"
            "class Item:\n    name: str\n"
            "declare_entity(entity_name='Item', entity_class=Item)\n"
        )
        namespace = {}
        exec(assemble_model_classes([claim]), namespace)
        self.assertEqual("hello", namespace["Item"]("hello").name)

    def test_formal_claim_dependency_is_not_silently_dropped(self):
        claim = (
            "from dataclasses import dataclass, field\n"
            "from caprmedio.formal_claims import Cardinality, declare_entity\n"
            "@dataclass\nclass Item:\n"
            "    name: str = field(metadata={'values': Cardinality(minimum=1, maximum=1)})\n"
            "declare_entity(entity_name='Item', entity_class=Item)\n"
        )
        with self.assertRaisesRegex(ValueError, "Unsupported class dependency: Cardinality"):
            assemble_model_classes([claim])


if __name__ == "__main__":
    unittest.main()
