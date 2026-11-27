"""Project the reviewed Topics check without executing it."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.GENERATE_ENTITY_GRAPH__shared import extract_claim_constraints
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.GENERATE_ENTITY_GRAPH__shared import compose_contract_graph

CLAIM = '''from anechoic.formal_claims import Cardinality, declare_entity
from anechoic.model import Atom

def dependencies_are_distinct(atom: Atom) -> bool:
    return len(atom.dependencies) == len(set(atom.dependencies))

declare_entity(
    entity_name="Dependencies",
    relation_name="IS_PROPERTY_OF",
    base_path="Atom.Header.Context.Topics",
    property_occurrence_cardinality=Cardinality(minimum=0, maximum=1),
    value_format=str,
    value_cardinality=Cardinality(minimum=0, maximum=None),
    dependent_property_cardinality=0,
    instance_check=dependencies_are_distinct,
)
'''


def carrier(code, subject="Atom.Header.Context.Topics.Dependencies"):
    return {
        "source": {"atom_id": "CA-R-2708", "version": 2, "path": "source.md", "sha256": "reviewed"},
        "subjects": {"active": subject, "passive": []},
        "read_view": {"content_role": "Requirement", "type": "Declaration"},
        "body": f"## Claim\n\n### Formal Claim\n\n```python\n{code}\n```\n",
    }


class TopicsUniquenessGraphTests(unittest.TestCase):
    def test_class_dependent_property_constraint_keeps_cardinality_and_names(self):
        code = '''from anechoic.formal_claims import declare_entity
class Atom:
    pass
declare_entity(entity_name="Atom", entity_class=Atom,
               dependent_property_cardinality=2,
               allowed_dependent_property_names=("Header", "Content"))
'''
        rows, diagnostics = extract_claim_constraints(carrier(code, subject="Atom"))
        self.assertEqual([], diagnostics)
        actual, = [row for row in rows if row.get("selection") == "immediate_dependents"]
        count = {"minimum": 2, "maximum": 2}
        self.assertEqual("Atom", actual["property_selector"])
        self.assertEqual(count, actual["occurrence_cardinality"])
        self.assertEqual(count, actual["effective_occurrence_cardinality"])
        self.assertFalse(actual["occurrence_conflict"])
        self.assertEqual(("Header", "Content"), actual["allowed_names"])
        graph = compose_contract_graph([carrier(code, subject="Atom")])
        entry, = [e for n in graph["entities"] for e in n["own"] if e["source"]["atom_id"] == "CA-R-2708"]
        self.assertIn(actual, entry["clauses"])

    def test_reviewed_check_keeps_property_bounds_and_provenance(self):
        row = carrier(CLAIM)
        clauses, diagnostics = extract_claim_constraints(row)
        self.assertEqual([], diagnostics)
        check, = [c for c in clauses if c["kind"] == "instance_check"]
        self.assertEqual("instances", check["group"])
        self.assertEqual("dependencies_are_distinct", check["callback"])
        self.assertEqual(row["source"], check["source"])
        prop, = [c for c in clauses if c.get("selection") == "property"]
        self.assertEqual({"minimum": 0, "maximum": 1}, prop["effective_occurrence_cardinality"])
        self.assertEqual({"minimum": 0, "maximum": None}, prop["value_cardinality"])
        self.assertEqual("str", prop["value_format"])
        dependent, = [c for c in clauses if c.get("selection") == "immediate_dependents"]
        self.assertEqual({"minimum": 0, "maximum": 0}, dependent["effective_occurrence_cardinality"])
        graph = compose_contract_graph([row])
        entry, = [e for n in graph["entities"] for e in n["own"] if e["source"]["atom_id"] == "CA-R-2708"]
        self.assertEqual([check], entry["instance_clauses"])

    def test_unknown_callback_shapes_fail_closed(self):
        for code in (
            CLAIM.replace("len(atom.dependencies) == len(set(atom.dependencies))", "True"),
            CLAIM.replace("dependencies_are_distinct", "other_check"),
            CLAIM.replace("base_path=\"Atom.Header.Context.Topics\"", "base_path=\"Atom.Header.Context\""),
            CLAIM.replace("dependent_property_cardinality=0", "dependent_property_cardinality=1"),
            CLAIM.replace("instance_check=dependencies_are_distinct,", "minimum_value=0, instance_check=dependencies_are_distinct,"),
        ):
            with self.subTest(code=code):
                clauses, diagnostics = extract_claim_constraints(carrier(code))
                self.assertEqual([], clauses)
                self.assertTrue(any(d["code"] == "python-formal-claim-invalid" for d in diagnostics))

    def test_existing_scope_check_still_projects(self):
        code = '''from anechoic.formal_claims import declare_entity
from anechoic.model import ScopeUnit

def check_structural_level(unit: ScopeUnit) -> bool:
    return True

declare_entity(entity_name="structural_level", relation_name="IS_PROPERTY_OF", base_path="Scope Unit", instance_check=check_structural_level)
'''
        clauses, diagnostics = extract_claim_constraints(carrier(code, subject="Scope Unit.structural_level"))
        self.assertEqual([], diagnostics)
        self.assertEqual(["check_structural_level"], [c["callback"] for c in clauses if c["kind"] == "instance_check"])


if __name__ == "__main__":
    unittest.main()
