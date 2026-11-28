"""Additional native Model claim graph cases."""

from importlib import import_module

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
parse_native_model_claim = _adapter.parse_native_model_claim
_native_constraints = _graph._native_constraints
extract_claim_constraints = _graph.extract_claim_constraints
_clause = _graph._clause
STATUS_GROUPS = _fixtures.STATUS_GROUPS
THRESHOLD = _fixtures.THRESHOLD
WORKSPACE = _fixtures.WORKSPACE


class NativeClaimGraphCases:
    def test_status_groups_and_rendering(self):
        source = {
            "atom_id": "CA-R-1",
            "version": 1,
            "path": "fixture",
            "sha256": "a",
        }
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
            (
                row["population_selector"],
                row["keys"],
                row["dependents"],
                row["status_groups"],
            ),
        )
        self.assertEqual(source, row["source"])
        self.assertNotIn("Draft", row["status_groups"])
        self.assertIn(
            "Status Group in (Current, Backlog, Archived)", _clause(row)
        )

    def test_threshold_bounds_and_fallback(self):
        records = _native_constraints(
            parse_native_model_claim(THRESHOLD),
            {"atom_id": "fixture"},
            THRESHOLD,
        )
        self.assertEqual(
            {(">=", 0), ("<=", 100)},
            {
                (r["operator"], r["value"])
                for r in records
                if r["kind"] == "property_value_bound"
            },
        )
        self.assertEqual(
            90,
            next(
                r["fallback_literal"]
                for r in records
                if r["kind"] == "effective_value_fallback"
            ),
        )

    def test_workspace_relation_direction_and_cardinality(self):
        body = "## Claim\n### Formal Claim\n```python\n" + WORKSPACE + "```\n"
        row = {
            "source": {
                "atom_id": "R",
                "version": 1,
                "path": "x",
                "sha256": "x",
            },
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
