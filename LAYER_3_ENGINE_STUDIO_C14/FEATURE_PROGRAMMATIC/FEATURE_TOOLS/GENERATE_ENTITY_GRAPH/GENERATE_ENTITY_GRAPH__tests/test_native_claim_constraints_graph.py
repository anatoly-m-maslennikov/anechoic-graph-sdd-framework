"""Graph projection assertions for native Model claims."""

from pathlib import Path
import sys
import unittest

TOOL = Path(__file__).resolve().parents[1]
PROGRAMMATIC = TOOL.parents[1]
sys.path[:0] = [str(PROGRAMMATIC), str(TOOL.parent), str(TOOL)]
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.native_model_claim__pub import parse_native_model_claim
from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.FEATURE_PROJECT_TOOLS__tests.compiler_claim_fixtures__pub import (
    ANALYSIS,
    DEPENDENCIES,
    EVENT_CLAIM,
    EVENT_CLASS,
    FALLBACK_CLAIM,
    FALLBACK_PROP,
    FALLBACK_PROJECT,
    SEQUENCE_CLAIM,
    SEQUENCE_PLAN,
    SEQ,
    STATUS_GROUPS,
    STATUS_PLAN,
    THRESHOLD,
    WORKSPACE,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.cfel_claim_constraints import extract_claim_constraints, _native_constraints
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.contract_graph import compose_contract_graph
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.contract_graph_render import _clause
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.subject_projection_relations import _relation_declarations

RELATION_CLAIMS = [
    (
        "IS_DECLARED_BY",
        "GOVERNS",
        'from anechoic.formal_claims import declare_relation\ndeclare_relation(relation_name=\'IS_DECLARED_BY\', source_endpoint={"level": "instances"}, target_endpoint={"level": "instances"}, derived_from=\'GOVERNS\')\n',
    ),
    (
        "RECURSIVELY_CONTAINS",
        "CONTAINS",
        'from anechoic.formal_claims import declare_relation\ndeclare_relation(relation_name=\'RECURSIVELY_CONTAINS\', source_endpoint={"level": "instances"}, target_endpoint={"level": "instances"}, derived_from=\'CONTAINS\')\n',
    ),
]


def body(code):
    return f"## Claim\n\n### Formal Claim\n\n```python\n{code}```\n"


class ModelClaimGraphTests(unittest.TestCase):
    def test_event_unfiltered_rule_and_catalog(self):
        row = {
            "source": {"atom_id": "CA-R-1", "version": 1, "path": "x", "sha256": "a" * 64},
            "body": "## Claim\n### Formal Claim\n```python\n" + EVENT_CLAIM + "```\n",
            "read_view": {"content_role": "Requirement"},
        }
        records, diags = extract_claim_constraints(row)
        self.assertEqual([], diags)
        uniq = next(x for x in records if x["kind"] == "population_unique_constraint")
        self.assertEqual(("Event Record", ("ID",)), (uniq["population_selector"], uniq["keys"]))
        self.assertNotIn("status", uniq)
        self.assertNotIn("single_value_paths", uniq)
        self.assertIn("unique ID", _clause(uniq))

    def test_event_class_population_uniqueness(self):
        claim = EVENT_CLASS
        row = {
            "source": {"atom_id": "CA-R-1", "version": 1, "path": "x", "sha256": "a" * 64},
            "body": "## Claim\n### Formal Claim\n```python\n" + claim + "```\n",
            "read_view": {"content_role": "Requirement"},
        }
        records, diagnostics = extract_claim_constraints(row)
        self.assertEqual([], diagnostics)
        (rule,) = (item for item in records if item["kind"] == "population_unique_constraint")
        self.assertEqual(
            ("Atom", ("Header.Identity.ID", "Header.State.Version")),
            (rule["population_selector"], rule["keys"]),
        )

    def test_fallback_chain_and_provenance(self):
        decl = parse_native_model_claim(FALLBACK_CLAIM)
        source = {"atom_id": "CA-R-1", "version": 1, "path": "fixture", "sha256": "fixture"}
        (row,) = [
            r
            for r in _native_constraints(decl, source, FALLBACK_CLAIM)
            if r["kind"] == "effective_value_fallback_chain"
        ]
        self.assertEqual(source, row["source"])
        self.assertEqual(("undefined", "null", ""), row["empty_values"])
        self.assertEqual(1, row["project_cardinality"])
        self.assertEqual(
            ("IS_CONTAINED_BY", FALLBACK_PROP, "Project", FALLBACK_PROJECT),
            (
                row["branches"][0]["lookup_relation"],
                row["branches"][0]["lookup_property"],
                row["branches"][1]["project_entity"],
                row["branches"][1]["project_property"],
            ),
        )
        self.assertIn("via `IS_CONTAINED_BY`", _clause(row))

    def test_plan_sequence_containers(self):
        d = parse_native_model_claim(SEQUENCE_CLAIM)
        source = {"atom_id": "CA-R-1", "version": 1, "path": "fixture", "sha256": "a"}
        rows = _native_constraints(d, source, SEQUENCE_CLAIM)
        rules = [r for r in rows if r["kind"] == "population_unique_constraint"]
        self.assertEqual(2, len(rules))
        self.assertEqual(
            {("Header.Context.Container.atom", SEQ), ("Header.Context.Container.scope_unit", SEQ)},
            {r["keys"] for r in rules},
        )
        for rule in rules:
            self.assertEqual("Active", rule["status"])
            self.assertEqual(SEQUENCE_PLAN, rule["population_selector"])
            self.assertEqual(set(rule["keys"]), set(rule["single_value_paths"]))
            self.assertEqual(source, rule["source"])
            self.assertIn("unique", _clause(rule))
        self.assertTrue(any(r.get("operator") == ">=" and r.get("value") == 1 for r in rows))

    def test_plan_group_order_and_graph(self):
        declaration = parse_native_model_claim(STATUS_PLAN)
        rows = _native_constraints(declaration, {"atom_id": "CA-R-1539"}, STATUS_PLAN)
        self.assertTrue(
            any(
                r.get("axis") == "Status Group"
                and r.get("value") == "Backlog"
                and "Role := Plan" in r.get("subject_selector", "")
                for r in rows
            )
        )

    def test_analysis_only_two_forms(self):
        declaration = parse_native_model_claim(ANALYSIS)
        rows = _native_constraints(declaration, {"atom_id": "CA-R-1875"}, ANALYSIS)
        self.assertEqual(len([r for r in rows if r.get("kind") == "allowed_literal"]), 2)
        self.assertTrue(all("Header.Context.Form in (" in r["property_selector"] for r in rows))

    def test_source_bound_projection_and_registry(self):
        for name, base, code in RELATION_CLAIMS:
            with self.subTest(name=name):
                carrier = {
                    "source": {"atom_id": "CA-R-1", "version": 1, "path": "source.md"},
                    "subjects": {"active": f"ANECHOIC_MODEL <+ Relation//{name}", "passive": []},
                    "read_view": {"content_role": "Requirement", "type": "Declaration"},
                    "body": body(code),
                }
                clauses, errors = extract_claim_constraints(carrier)
                self.assertEqual([], errors)
                (link,) = [
                    row for row in clauses if row.get("relation") == "IS_DERIVED_RELATION_OF"
                ]
                self.assertEqual(
                    (f"Relation//{name}", f"Relation//{base}", carrier["source"]),
                    (link["source_selector"], link["target_selector"], link["source"]),
                )
                (relation,) = compose_contract_graph([carrier])["relations"]
                self.assertEqual([base], [row["name"] for row in relation["derivation_links"]])
                (projected,) = _relation_declarations([relation])
                self.assertEqual((name, "Derived"), (projected["name"], projected["derivation"]))

    def test_population_dependency_order_and_provenance(self):
        source = {"atom_id": "CA-R-1", "version": 1, "path": "fixture.md", "sha256": "fixture"}
        records = _native_constraints(parse_native_model_claim(DEPENDENCIES), source, DEPENDENCIES)
        self.assertEqual(2, len([r for r in records if r["kind"] == "property_constraint"]))
        rules = [r for r in records if r["kind"] == "population_functional_dependency"]
        self.assertEqual(
            [(("Form", "Scope Unit"), ("ID",)), (("ID",), ("Form", "Scope Unit"))],
            [(r["keys"], r["dependents"]) for r in rules],
        )
        for row in rules:
            self.assertEqual(source, row["source"])
            self.assertEqual("Projection", row["population_selector"])
            self.assertEqual("instances", row["group"])
            self.assertNotIn("status_group", row)

    def test_status_groups_and_rendering(self):
        source = {"atom_id": "CA-R-1", "version": 1, "path": "fixture", "sha256": "a"}
        (row,) = [
            r
            for r in _native_constraints(
                parse_native_model_claim(STATUS_GROUPS), source, STATUS_GROUPS
            )
            if r["kind"] == "population_functional_dependency"
        ]
        self.assertEqual(
            (
                "Atom",
                ("Header.Identity.ID",),
                ("Content.Summary",),
                ("Current", "Backlog", "Archived"),
            ),
            (row["population_selector"], row["keys"], row["dependents"], row["status_groups"]),
        )
        self.assertEqual(source, row["source"])
        self.assertNotIn("Draft", row["status_groups"])
        self.assertIn("Status Group in (Current, Backlog, Archived)", _clause(row))

    def test_threshold_bounds_and_fallback(self):
        records = _native_constraints(
            parse_native_model_claim(THRESHOLD), {"atom_id": "fixture"}, THRESHOLD
        )
        self.assertEqual(
            {(">=", 0), ("<=", 100)},
            {(r["operator"], r["value"]) for r in records if r["kind"] == "property_value_bound"},
        )
        self.assertEqual(
            90,
            next(r["fallback_literal"] for r in records if r["kind"] == "effective_value_fallback"),
        )

    def test_workspace_relation_direction_and_cardinality(self):
        body = "## Claim\n### Formal Claim\n```python\n" + WORKSPACE + "```\n"
        row = {
            "source": {"atom_id": "R", "version": 1, "path": "x", "sha256": "x"},
            "body": body,
            "read_view": {"content_role": "Requirement"},
        }
        records, errors = extract_claim_constraints(row)
        self.assertEqual([], errors)
        relation = records[-1]
        self.assertEqual(
            (
                "View",
                "Workspace",
                "IS_CONTAINED_BY",
                {"minimum": 1, "maximum": 1},
                {"minimum": 1, "maximum": None},
            ),
            tuple(
                relation[k]
                for k in (
                    "source_selector",
                    "target_selector",
                    "relation",
                    "source_cardinality",
                    "target_cardinality",
                )
            ),
        )


if __name__ == "__main__":
    unittest.main()
