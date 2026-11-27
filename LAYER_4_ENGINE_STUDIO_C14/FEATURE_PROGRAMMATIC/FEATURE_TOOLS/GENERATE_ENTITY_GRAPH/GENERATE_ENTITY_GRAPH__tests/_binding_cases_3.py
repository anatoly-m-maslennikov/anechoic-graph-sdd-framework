"""Source-bound contract graph cases."""

from importlib import import_module

_graph = import_module(
    "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH."
    "GENERATE_ENTITY_GRAPH__shared"
)
_support = import_module(
    "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH."
    "GENERATE_ENTITY_GRAPH__tests.contract_graph_test_support"
)
compose_contract_graph = _graph.compose_contract_graph
render_contract_graph = _graph.render_contract_graph
carrier, body = _support.carrier, _support.body
scope_context_graph = _support.scope_context_graph
_sources = import_module(
    "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH."
    "GENERATE_ENTITY_GRAPH__tests._binding_sources"
)


class BindingCases3:
    def _case_337(
        self,
    ):
        graph = compose_contract_graph(
            _sources.carriers_4_1()
            + _sources.carriers_4_2()
            + _sources.carriers_4_3()
            + _sources.carriers_4_4()
            + _sources.carriers_4_5()
            + _sources.carriers_4_6()
        )

        entities = {row["target"]: row for row in graph["entities"]}
        components = {row["target"]: row for row in graph["components"]}
        relations = {row["target"]: row for row in graph["relations"]}
        self.assertEqual("exact", entities["Node"]["shared"][0]["binding"])
        self.assertEqual(
            "ANECHOIC <+ MODEL <+ Node",
            entities["Node"]["shared"][0]["subject"],
        )
        self.assertEqual("property", entities["Node.Status"]["kind"])
        self.assertEqual("instance", entities["Node//Example"]["kind"])
        self.assertEqual("component", components["Format"]["kind"])
        self.assertEqual("Project", entities["Project"]["shared"][0]["target"])
        self.assertEqual(
            "scope_unit_declaration_context",
            entities["Project"]["shared"][0]["binding"],
        )
        self.assertEqual("depends_on", relations["depends_on"]["target"])
        self.assertEqual(
            "ANECHOIC <+ MODEL <+ CFEL <+ Relation//depends_on",
            relations["depends_on"]["shared"][0]["subject"],
        )
        self.assertEqual(1, len(entities["Node"]["shared"]))
        self.assertEqual(2, len(entities["Projection"]["shared"]))
        self.assertEqual(
            "known_instance_context",
            entities["Projection"]["shared"][0]["binding"],
        )
        self.assertEqual(
            "known_instance_context",
            entities["Named Selection"]["shared"][0]["binding"],
        )
        self.assertEqual(2, graph["coverage"]["coverage_gaps"])

    locals()[
        (
            "test_binds_prefixed_namespaces_to_local_"
            "targets_without_losing_subject_provenance"
        )
    ] = _case_337

    def test_claim_scope_and_details_are_source_bound_context_before_claim(
        self,
    ):
        graph = compose_contract_graph(
            [
                carrier("CA-R-1", "Atom.Status", body("Status declaration.")),
                carrier(
                    "CA-R-2",
                    "Atom.Status:Draft",
                    """## Claim Scope

Only Draft Atom instances.

## Claim

Draft status rule.

## Details

Carrier-specific constraint.
""",
                    form="Rule",
                ),
            ]
        )

        rendered = render_contract_graph(graph)
        rule = rendered[rendered.index("CA-R-2@1") :]
        self.assertLess(
            rule.index("Claim Scope:"), rule.index("Remaining Claim prose:")
        )
        self.assertIn("Only Draft Atom instances.", rendered)
        self.assertIn("Details (source-bound):", rendered)
        self.assertIn("Carrier-specific constraint.", rendered)

    def _case_412(
        self,
    ):
        graph = compose_contract_graph(
            [
                carrier("CA-R-1", "Node", body("Node declaration.")),
                carrier(
                    "CA-R-2",
                    "Unknown",
                    body("First outside line.", "", "Second outside line."),
                    form="Rule",
                ),
            ]
        )

        rendered = render_contract_graph(graph)
        self.assertIn(
            "    First outside line.\n\n    Second outside line.", rendered
        )
        self.assertFalse(
            any(line.endswith(" ") for line in rendered.splitlines())
        )

    locals()[
        (
            "test_renders_blank_outside_scope_pro"
            "se_lines_without_trailing_whitespace"
        )
    ] = _case_412
