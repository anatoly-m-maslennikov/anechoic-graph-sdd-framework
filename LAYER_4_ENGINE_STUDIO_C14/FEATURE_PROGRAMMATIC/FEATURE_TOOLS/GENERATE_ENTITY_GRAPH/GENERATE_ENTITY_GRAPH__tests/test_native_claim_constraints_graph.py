"""Graph projection assertions for native Model claims."""

from importlib import import_module
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(TOOL := Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(TOOL.parent))
sys.path.insert(0, str(PROGRAMMATIC := TOOL.parents[1]))
_adapter = import_module(
    "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared"
)
_fixtures = import_module(
    "FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS."
    "FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared"
)
_graph = import_module(
    "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH."
    "GENERATE_ENTITY_GRAPH__shared"
)
_cases = import_module(
    "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH."
    "GENERATE_ENTITY_GRAPH__tests._native_claim_graph_cases"
)
parse_native_model_claim = _adapter.parse_native_model_claim
extract_claim_constraints = _graph.extract_claim_constraints
_native_constraints = _graph._native_constraints
compose_contract_graph = _graph.compose_contract_graph
_clause = _graph._clause
build_subject_projection_data = _graph.build_subject_projection_data
ANALYSIS = _fixtures.ANALYSIS
DEPENDENCIES = _fixtures.DEPENDENCIES
EVENT_CLAIM = _fixtures.EVENT_CLAIM
EVENT_CLASS = _fixtures.EVENT_CLASS
FALLBACK_CLAIM = _fixtures.FALLBACK_CLAIM
FALLBACK_PROP = _fixtures.FALLBACK_PROP
FALLBACK_PROJECT = _fixtures.FALLBACK_PROJECT
SEQUENCE_CLAIM = _fixtures.SEQUENCE_CLAIM
SEQUENCE_PLAN = _fixtures.SEQUENCE_PLAN
SEQ = _fixtures.SEQ
STATUS_GROUPS = _fixtures.STATUS_GROUPS
STATUS_PLAN = _fixtures.STATUS_PLAN
THRESHOLD = _fixtures.THRESHOLD
WORKSPACE = _fixtures.WORKSPACE

RELATION_CLAIMS = [
    (
        "IS_DECLARED_BY",
        "GOVERNS",
        (
            "from anechoic.formal_claims import decla"
            "re_relation\ndeclare_relation(relation_na"
            "me='IS_DECLARED_BY', source_endpoint={\"l"
            'evel": "instances"}, target_endpoint={"l'
            'evel": "instances"}, derived_from=\'GOVER'
            "NS')\n"
        ),
    ),
    (
        "RECURSIVELY_CONTAINS",
        "CONTAINS",
        (
            "from anechoic.formal_claims import decla"
            "re_relation\ndeclare_relation(relation_na"
            "me='RECURSIVELY_CONTAINS', source_endpoi"
            'nt={"level": "instances"}, target_endpoi'
            'nt={"level": "instances"}, derived_from='
            "'CONTAINS')\n"
        ),
    ),
]


def body(code):
    return f"## Claim\n\n### Formal Claim\n\n```python\n{code}```\n"


class ModelClaimGraphTests(_cases.NativeClaimGraphCases, unittest.TestCase):
    def test_event_unfiltered_rule_and_catalog(self):
        row = {
            "source": {
                "atom_id": "CA-R-1",
                "version": 1,
                "path": "x",
                "sha256": "a" * 64,
            },
            "body": "## Claim\n### Formal Claim\n```python\n"
            + EVENT_CLAIM
            + "```\n",
            "read_view": {"content_role": "Requirement"},
        }
        records, diags = extract_claim_constraints(row)
        self.assertEqual([], diags)
        uniq = next(
            x for x in records if x["kind"] == "population_unique_constraint"
        )
        self.assertEqual(
            ("Event Record", ("ID",)),
            (uniq["population_selector"], uniq["keys"]),
        )
        self.assertNotIn("status", uniq)
        self.assertNotIn("single_value_paths", uniq)
        self.assertIn("unique ID", _clause(uniq))

    def test_event_class_population_uniqueness(self):
        claim = EVENT_CLASS
        row = {
            "source": {
                "atom_id": "CA-R-1",
                "version": 1,
                "path": "x",
                "sha256": "a" * 64,
            },
            "body": "## Claim\n### Formal Claim\n```python\n"
            + claim
            + "```\n",
            "read_view": {"content_role": "Requirement"},
        }
        records, diagnostics = extract_claim_constraints(row)
        self.assertEqual([], diagnostics)
        (rule,) = (
            item
            for item in records
            if item["kind"] == "population_unique_constraint"
        )
        self.assertEqual(
            ("Atom", ("Header.Identity.ID", "Header.State.Version")),
            (rule["population_selector"], rule["keys"]),
        )

    def test_fallback_chain_and_provenance(self):
        decl = parse_native_model_claim(FALLBACK_CLAIM)
        source = {
            "atom_id": "CA-R-1",
            "version": 1,
            "path": "fixture",
            "sha256": "fixture",
        }
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
        source = {
            "atom_id": "CA-R-1",
            "version": 1,
            "path": "fixture",
            "sha256": "a",
        }
        rows = _native_constraints(d, source, SEQUENCE_CLAIM)
        rules = [
            r for r in rows if r["kind"] == "population_unique_constraint"
        ]
        self.assertEqual(2, len(rules))
        self.assertEqual(
            {
                ("Header.Context.Container.atom", SEQ),
                ("Header.Context.Container.scope_unit", SEQ),
            },
            {r["keys"] for r in rules},
        )
        for rule in rules:
            self.assertEqual("Active", rule["status"])
            self.assertEqual(SEQUENCE_PLAN, rule["population_selector"])
            self.assertEqual(
                set(rule["keys"]), set(rule["single_value_paths"])
            )
            self.assertEqual(source, rule["source"])
            self.assertIn("unique", _clause(rule))
        self.assertTrue(
            any(
                r.get("operator") == ">=" and r.get("value") == 1 for r in rows
            )
        )

    def test_plan_group_order_and_graph(self):
        declaration = parse_native_model_claim(STATUS_PLAN)
        rows = _native_constraints(
            declaration, {"atom_id": "CA-R-1539"}, STATUS_PLAN
        )
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
        rows = _native_constraints(
            declaration, {"atom_id": "CA-R-1875"}, ANALYSIS
        )
        self.assertEqual(
            len([r for r in rows if r.get("kind") == "allowed_literal"]), 2
        )
        self.assertTrue(
            all(
                "Header.Context.Form in (" in r["property_selector"]
                for r in rows
            )
        )

    def test_source_bound_projection_and_registry(self):
        for name, base, code in RELATION_CLAIMS:
            with self.subTest(name=name):
                carrier = {
                    "source": {
                        "atom_id": "CA-R-1",
                        "version": 1,
                        "path": "source.md",
                    },
                    "subjects": {
                        "active": f"ANECHOIC_MODEL <+ Relation//{name}",
                        "passive": [],
                    },
                    "read_view": {
                        "content_role": "Requirement",
                        "type": "Declaration",
                    },
                    "body": body(code),
                }
                clauses, errors = extract_claim_constraints(carrier)
                self.assertEqual([], errors)
                (link,) = [
                    row
                    for row in clauses
                    if row.get("relation") == "IS_DERIVED_RELATION_OF"
                ]
                self.assertEqual(
                    (
                        f"Relation//{name}",
                        f"Relation//{base}",
                        carrier["source"],
                    ),
                    (
                        link["source_selector"],
                        link["target_selector"],
                        link["source"],
                    ),
                )
                (relation,) = compose_contract_graph([carrier])["relations"]
                self.assertEqual(
                    [base],
                    [row["name"] for row in relation["derivation_links"]],
                )
                self.check_registry_projection(carrier, name)

    def check_registry_projection(self, carrier, name):
        (projected,) = build_subject_projection_data([carrier])[
            "relation_declarations"
        ]
        self.assertEqual(
            (name, "Derived"),
            (projected["name"], projected["derivation"]),
        )

    def test_population_dependency_order_and_provenance(self):
        source = {
            "atom_id": "CA-R-1",
            "version": 1,
            "path": "fixture.md",
            "sha256": "fixture",
        }
        records = _native_constraints(
            parse_native_model_claim(DEPENDENCIES), source, DEPENDENCIES
        )
        self.assertEqual(
            2, len([r for r in records if r["kind"] == "property_constraint"])
        )
        rules = [
            r
            for r in records
            if r["kind"] == "population_functional_dependency"
        ]
        self.assertEqual(
            [
                (("Form", "Scope Unit"), ("ID",)),
                (("ID",), ("Form", "Scope Unit")),
            ],
            [(r["keys"], r["dependents"]) for r in rules],
        )
        for row in rules:
            self.assertEqual(source, row["source"])
            self.assertEqual("Projection", row["population_selector"])
            self.assertEqual("instances", row["group"])
            self.assertNotIn("status_group", row)


if __name__ == "__main__":
    unittest.main()
