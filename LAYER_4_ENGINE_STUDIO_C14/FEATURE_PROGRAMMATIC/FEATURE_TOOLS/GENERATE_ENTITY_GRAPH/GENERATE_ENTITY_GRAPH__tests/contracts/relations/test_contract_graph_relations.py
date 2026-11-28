"""Source-bound graph relations cases."""

from importlib import import_module
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(TOOL := Path(__file__).resolve().parents[3]))
sys.path.insert(0, str(TOOL.parent))

_graph = import_module(
    "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH."
    "GENERATE_ENTITY_GRAPH__shared"
)
_support = import_module(
    "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH."
    "GENERATE_ENTITY_GRAPH__tests.contracts.contracts__shared"
)
_cases = import_module(
    "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH."
    "GENERATE_ENTITY_GRAPH__tests.contracts.relations._contract_relation_cases"
)
_cases2 = import_module(
    "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH."
    "GENERATE_ENTITY_GRAPH__tests.contracts.relations._contract_relation_cases_2"
)
compose_contract_graph = _graph.compose_contract_graph
render_contract_graph = _graph.render_contract_graph
extract_claim_constraints = _graph.extract_claim_constraints
carrier, body = _support.carrier, _support.body
build_subject_projection_data = _graph.build_subject_projection_data


def metadata_carriers():
    return [
        carrier(
            "CA-R-1",
            "CFEL <+ Relation//depends_on",
            body(
                "```python",
                (
                    "relation(source='Step//', name='depends_"
                    "on', target='Action//', source_count='1'"
                    ", target_count='1')"
                ),
                (
                    "relation(source='Relation//depends_on', "
                    "name='HAS_INVERSE', target='Relation//is"
                    "_depended_on')"
                ),
                (
                    "relation(source='Relation//depends_on', "
                    "name='IS_DERIVED_RELATION_OF', target='R"
                    "elation//is_depended_on')"
                ),
                (
                    "classify(address='Relation//depends_on',"
                    " axis='Derivation', value='Direct', nota"
                    "tion='relation')"
                ),
                "```",
                semantics="Dependency direction.",
            ),
        ),
    ]


class ContractGraphTests(
    _cases.ContractRelationCases1,
    _cases2.ContractRelationCases2,
    unittest.TestCase,
):
    def test_qualified_declared_by_derivation_is_not_an_unconditional_inverse(
        self,
    ):
        graph = compose_contract_graph(
            [
                carrier(
                    "CA-R-1",
                    "CFEL <+ Relation//IS_DECLARED_BY",
                    body(
                        "### Formal Claim",
                        "```python",
                        "# model",
                        (
                            "relation(source='Relation//IS_DECLARED_B"
                            "Y', name='IS_DERIVED_RELATION_OF', targe"
                            "t='Relation//GOVERNS')"
                        ),
                        "```",
                        "### Prose Claim",
                        (
                            "Only governing links satisfying the Decl"
                            "aration ownership rule."
                        ),
                    ),
                )
            ]
        )
        relation = graph["relations"][0]
        self.assertEqual(
            ["GOVERNS"], [row["name"] for row in relation["derivation_links"]]
        )
        self.assertEqual([], relation["inverses"])
        self.assertNotIn("derived_view", relation)
        self.assertIn(
            "not structurally interpreted", relation["derivation_scope"]
        )

    def _relation_metadata(
        self,
    ):
        graph = compose_contract_graph(metadata_carriers())

        relation = graph["relations"][0]
        self.assertEqual("depends_on", relation["target"])
        self.assertEqual(
            ["is_depended_on"], [row["name"] for row in relation["inverses"]]
        )
        self.assertEqual(
            ["is_depended_on"],
            [row["name"] for row in relation["derivation_links"]],
        )
        self.assertEqual(
            {"derivation"}, {row["kind"] for row in relation["metadata"]}
        )
        self.assertEqual(0, graph["coverage"]["missing_relation_semantics"])
        rendered = render_contract_graph(graph)
        self.assertIn(
            "does not certify an undeclared inverse Relation", rendered
        )
        self.assertIn("Derivation interpretation gap", rendered)
        self.assertNotIn("((is_depended_on)) — declared Relation", rendered)

    locals()[
        (
            "test_relation_metadata_is_case_preservin"
            "g_and_inverse_is_not_another_declaration"
        )
    ] = _relation_metadata

    def test_typed_relation_inverse_is_source_bound_in_either_direction(self):
        def read(binding):
            return compose_contract_graph(
                [
                    carrier(
                        "CA-R-1",
                        "Relation//NARROWER_THAN",
                        body(
                            "### Formal Claim",
                            "```python",
                            binding,
                            (
                                "relation(source='Node', name='NARROWER_T"
                                "HAN', target='Node')"
                            ),
                            "```",
                        ),
                    ),
                ]
            )["relations"][0]

        forward = read(
            (
                "relation(source='Relation//NARROWER_THAN"
                "', name='HAS_INVERSE', target='Relation/"
                "/BROADER_THAN')"
            )
        )
        reverse = read(
            (
                "relation(source='Relation//BROADER_THAN'"
                ", name='HAS_INVERSE', target='Relation//"
                "NARROWER_THAN', reverse=True)"
            )
        )
        self.assertEqual(
            ["BROADER_THAN"], [row["name"] for row in forward["inverses"]]
        )
        self.assertEqual(forward["inverses"], reverse["inverses"])
        self.assertEqual(
            ["Node"],
            [row["source_selector"] for row in forward["host_target"]],
        )

    def test_declared_derived_relation_keeps_its_own_metadata(self):
        graph = compose_contract_graph(
            [
                carrier(
                    "CA-R-1",
                    "CFEL <+ Relation//is_depended_on",
                    body(
                        "### Formal Claim",
                        "```python",
                        "from anechoic.formal_claims import declare_relation",
                        (
                            "declare_relation(relation_name='is_depen"
                            "ded_on', derived_from='depends_on',"
                        ),
                        (
                            "  source_endpoint={'level': 'instances'}"
                            ", target_endpoint={'level': 'instances'}"
                            ")"
                        ),
                        "```",
                        semantics="Reverse dependency.",
                    ),
                ),
            ]
        )

        relation = graph["relations"][0]
        self.assertEqual("is_depended_on", relation["target"])
        self.assertEqual(
            ["Derived"], [row["value"] for row in relation["metadata"]]
        )
        self.assertIn(
            "`((is_depended_on))` — declared Relation",
            render_contract_graph(graph),
        )

    def _duplicate_declaration(
        self,
    ):
        graph = compose_contract_graph(
            [
                carrier("CA-R-1", "Node", body("One.")),
                carrier("CA-R-2", "Node", body("Two.")),
                carrier(
                    "CA-R-3",
                    "CFEL <+ Relation//RUN",
                    body(
                        "### Formal Claim",
                        "```python",
                        "from anechoic.formal_claims import declare_relation",
                        (
                            "declare_relation(relation_name='RUN', wr"
                            "itten_alias='>>')"
                        ),
                        "```",
                    ),
                ),
            ]
        )

        self.assertEqual(1, graph["coverage"]["duplicate_declarations"])
        self.assertEqual(1, graph["coverage"]["missing_relation_semantics"])
        self.assertEqual("incomplete", graph["outcome"])

    locals()[
        (
            "test_duplicate_declaration_and_missing_"
            "relation_semantics_are_coverage_failures"
        )
    ] = _duplicate_declaration

    def test_relation_metadata_reads_structured_python_helper(self):
        declaration = carrier(
            "CA-R-1",
            "CFEL <+ Relation//RUNS",
            body(
                "### Formal Claim",
                "```python",
                "# model",
                (
                    "classify(address='Relation//RUNS', axis="
                    "'Derivation', value='Direct', notation='"
                    "relation')"
                ),
                "# instances",
                (
                    "classify(address='Relation//RUNS', axis="
                    "'Derivation', value='Derived', notation="
                    "'relation')"
                ),
                "```",
            ),
        )
        (relation,) = compose_contract_graph([declaration])["relations"]
        self.assertEqual(
            [
                {
                    "kind": "derivation",
                    "value": "Direct",
                    "source": declaration["source"],
                }
            ],
            relation["metadata"],
        )
