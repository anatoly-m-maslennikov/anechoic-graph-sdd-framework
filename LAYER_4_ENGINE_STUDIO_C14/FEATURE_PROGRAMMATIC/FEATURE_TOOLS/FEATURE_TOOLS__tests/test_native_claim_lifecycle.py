"""Lifecycle constraints from native model declarations."""

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(TOOLS := Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(PROGRAMMATIC := TOOLS.parent))

from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared import (
    CONTENT_PROPERTY,
    RECURSIVE_CONTENT,
    NESTED_CONTENT,
    NESTED_HEADER,
    ROLE_HEADER,
    ROLE,
    HEADER_RELATIONS,
    FORM_EXAMPLES,
    ANALYSIS,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.ATOM_LIFECYCLE__shared import compile_content_constraints
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.ATOM_LIFECYCLE__shared import compile_header_constraints, load_header_constraints
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.ATOM_LIFECYCLE__shared import compile_role_form
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.ATOM_LIFECYCLE__shared import status_memberships


def _native_row(source, identifier="CA-R-1"):
    body = f"## Claim\n### Formal Claim\n```python\n{source}\n```\n"
    return {
        "id": identifier,
        "ref": identifier,
        "version": 1,
        "source_path": "source.md",
        "status_group": "Current",
        "role": "Requirement",
        "form": "Declaration",
        "_content_bytes": body.encode(),
        "content_markdown": body,
    }


class NativeClaimLifecycleTests(unittest.TestCase):
    def test_content_property_contributes_same_roles_and_cardinalities(self):
        native = CONTENT_PROPERTY
        actual = compile_content_constraints([_native_row(native)])
        self.assertEqual(
            {("children", 0, 0), ("value", 0, 1)},
            {(item["kind"], item["min"], item["max"]) for item in actual},
        )
        self.assertTrue(
            all(
                item["path"] == ["semantics"]
                and item["roles"]
                == ["Delivery", "Evaluation", "Method", "Requirement"]
                for item in actual
            )
        )

    def test_recursive_content_and_role_scoped_ordering(self):
        native = RECURSIVE_CONTENT
        orders = compile_content_constraints([_native_row(native)])
        self.assertEqual(
            {
                ("summary", "claim"),
                ("claim", "semantics"),
                ("semantics", "details"),
            },
            {
                tuple(item["children"])
                for item in orders
                if item["kind"] == "order"
            },
        )

    def test_nested_content_property_preserves_role_selection(self):
        native = NESTED_CONTENT
        actual = compile_content_constraints([_native_row(native)])
        self.assertEqual(
            {("children", 0, 0), ("value", 0, 1)},
            {(item["kind"], item["min"], item["max"]) for item in actual},
        )
        self.assertTrue(
            all(item["path"] == ["claim", "prose_claim"] for item in actual)
        )

    def test_nested_header_constraints_and_wildcard_formats(self):
        native = NESTED_HEADER
        records = compile_header_constraints([_native_row(native)])
        self.assertIn(
            {
                "kind": "children",
                "path": "destination.file",
                "selector": "",
                "selected": "",
                "value": (2, 2, "name", "path"),
                "source": "CA-R-1",
            },
            records,
        )

    def test_nested_header_property_preserves_single_role(self):
        native = ROLE_HEADER
        records = compile_header_constraints([_native_row(native)])
        self.assertIn(
            {
                "kind": "children",
                "path": "context.plan",
                "selector": "role",
                "selected": "Plan",
                "value": (
                    1,
                    2,
                    "ai_agent_confidence_threshold",
                    "work_sequence_number",
                ),
                "source": "CA-R-1",
            },
            records,
        )

    def test_role_order_and_form_are_qualified_by_role(self):
        role = ROLE
        form = """
from anechoic.formal_claims import declare_entity
from anechoic.model import Method
class Decision(Method):
    pass
declare_entity(entity_class=Decision, entity_name="Decision", qualification_property_path="Atom.Header.Context.Form")
"""
        self.assertIn(
            {
                "kind": "role",
                "value": "Method",
                "role": "",
                "source": "CA-R-1",
            },
            compile_role_form([_native_row(role)]),
        )
        self.assertIn(
            {
                "kind": "qualified",
                "value": "Decision",
                "role": "Method",
                "source": "CA-R-2",
            },
            compile_role_form(
                [_native_row(role), _native_row(form, "CA-R-2")]
            ),
        )


    def test_header_relations_child_value_cardinality(self):
        native = HEADER_RELATIONS
        constraints = compile_header_constraints([_native_row(native)])
        self.assertIn(
            {
                "kind": "value",
                "path": "relations.*",
                "selector": "",
                "selected": "",
                "value": (1, None),
                "source": "CA-R-1",
            },
            constraints,
        )
        validator = load_header_constraints(constraints, {"CA-R-1"})
        valid = {"role": "Requirement", "relations": {"related": ["CA-R-2"]}}
        empty = {"role": "Requirement", "relations": {"related": []}}
        self.assertEqual([], validator.validate(valid, metadata=valid))
        self.assertTrue(
            any(
                field == "relations.related"
                for field, _, _ in validator.validate(empty, metadata=empty)
            )
        )


    def test_workflow_content_projection_keeps_form_ancestry(self):
        new = _native_row(
            """from anechoic.formal_claims import declare_entity
from anechoic.model import Operations
class Workflow(Operations):
    pass
declare_entity(entity_name='Workflow', entity_class=Workflow, qualification_property_path='Atom.Header.Context.Form', project_form_content=True)""",
            "workflow",
        )
        content = _native_row(
            """from anechoic.formal_claims import declare_entity
declare_entity(entity_name='Claim', relation_name='IS_PROPERTY_OF', base_path='Workflow.Content',
    property_occurrence_cardinality=1, value_cardinality=1)""",
            "content",
        )
        result = compile_content_constraints([new, content])
        self.assertEqual(
            {"heading", "heading_value"}, {item["kind"] for item in result}
        )
        for item in result:
            self.assertEqual(
                (["claim"], ["Operations"], ["Workflow"], 1, 1),
                (
                    item["path"],
                    item["roles"],
                    item["forms"],
                    item["min"],
                    item["max"],
                ),
            )


    def test_role_and_content_consumers_match(self):
        self.assertEqual(
            [],
            compile_content_constraints(
                [_native_row(FORM_EXAMPLES[0][1], "R")]
            ),
        )
        self.assertEqual(
            {
                ("value", ("details",), 1, 1, ()),
                ("children", ("details",), 0, 0, ()),
                ("order", (), 0, 0, ("summary", "details")),
            },
            {
                (
                    item["kind"],
                    tuple(item["path"]),
                    item["min"],
                    item["max"],
                    tuple(item["children"]),
                )
                for item in compile_content_constraints(
                    [_native_row(FORM_EXAMPLES[1][1], "R")]
                )
            },
        )
        self.assertEqual(
            {('form', 'Scope Delegation', ''),
             *(('constraint', 'Scope Delegation', role) for role in
               ('Requirement', 'Method', 'Evaluation', 'Delivery', 'Operations'))},
            {(item['kind'], item['value'], item['role'])
             for item in compile_role_form([_native_row(FORM_EXAMPLES[0][1], 'R')])},
        )
        self.assertEqual(
            {
                ("form", "Work Report", ""),
                ("constraint", "Work Report", "Plan"),
            },
            {
                (item["kind"], item["value"], item["role"])
                for item in compile_role_form(
                    [_native_row(FORM_EXAMPLES[1][1], "R")]
                )
            },
        )

    def test_analysis_only_two_forms(self):
        decoded = set(
            status_memberships(
                "## Claim\n\n### Formal Claim\n\n```python\n"
                + ANALYSIS
                + "\n```\n"
            )
        )
        self.assertEqual(
            decoded,
            {
                ("Analysis and Advisory", "Analysis Report", "Done"),
                ("Analysis and Advisory", "Rationale", "Done"),
            },
        )


if __name__ == "__main__":
    unittest.main()
