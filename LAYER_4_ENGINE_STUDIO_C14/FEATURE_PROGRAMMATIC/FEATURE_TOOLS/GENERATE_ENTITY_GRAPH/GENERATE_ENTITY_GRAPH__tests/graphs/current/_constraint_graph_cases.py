"""Named relation constraint graph case."""

from importlib import import_module

_graph = import_module(
    "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH."
    "GENERATE_ENTITY_GRAPH__shared"
)
_support = import_module(
    "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH."
    "GENERATE_ENTITY_GRAPH__tests.graphs.current.enhanced_graph_test_support"
)
extract_claim_constraints = _graph.extract_claim_constraints
carrier = _support.carrier


class ConstraintGraphCases:
    def _reverse_named_relation(
        self,
    ) -> None:
        records, diagnostics = extract_claim_constraints(
            carrier(
                "CA-R-1001",
                {},
                (
                    "## Claim\n```python\nrelation(source='Step"
                    "', name='IS_CONTAINED_BY', target='Workf"
                    "low', source_count='1', target_count='2'"
                    ")\nrelation(source='Workflow', name='IS_C"
                    "ONTAINED_BY', target='Step', source_coun"
                    "t='2', target_count='1', reverse=True)\n`"
                    "``\n"
                ),
                declaration=True,
            )
        )
        self.assertEqual([], diagnostics)
        forward, reverse = records
        self.assertEqual(
            (
                forward["relation"],
                forward["source_selector"],
                forward["target_selector"],
                forward["source_cardinality"],
                forward["target_cardinality"],
            ),
            (
                reverse["relation"],
                reverse["source_selector"],
                reverse["target_selector"],
                reverse["source_cardinality"],
                reverse["target_cardinality"],
            ),
        )
        self.assertEqual("forward", forward["written_direction"])
        self.assertEqual("reverse", reverse["written_direction"])
        self.assert_reverse_selectors(reverse)

    def assert_reverse_selectors(self, reverse):
        self.assertEqual(
            ("Workflow", "Step"),
            (
                reverse["written_source_selector"],
                reverse["written_target_selector"],
            ),
        )

    locals()[
        (
            "test_reverse_named_relation_clause_normalizes_endpoints_"
            "and_written_counts"
        )
    ] = _reverse_named_relation
