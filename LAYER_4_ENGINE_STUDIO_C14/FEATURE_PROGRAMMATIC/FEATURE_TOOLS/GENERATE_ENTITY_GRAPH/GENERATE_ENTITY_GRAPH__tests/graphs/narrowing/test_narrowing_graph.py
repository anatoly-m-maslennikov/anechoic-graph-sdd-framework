"""Declared-only Current NARROWER_THAN tree projection."""

from importlib import import_module
from pathlib import Path
import sys
import unittest


TOOL = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(TOOL.parent), str(TOOL)]

_graph = import_module(
    "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH."
    "GENERATE_ENTITY_GRAPH__shared"
)
_fixture = import_module(
    "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH."
    "GENERATE_ENTITY_GRAPH__tests.graphs.narrowing._narrowing_graph_fixture"
)
_cases = import_module(
    "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH."
    "GENERATE_ENTITY_GRAPH__tests.graphs.narrowing._narrowing_graph_cases"
)
compose_narrowing_graph = _graph.compose_narrowing_graph
render_inherency = _graph.render_inherency
carrier = _fixture.carrier
claim = _fixture.claim
event_record_claim = _fixture.event_record_claim


def missing_carriers():
    return [
        carrier("CA-R-0", "Node"),
        carrier("CA-R-1", "Node/Continuant"),
        carrier("CA-R-2", "Node/Continuant"),
        carrier(
            "CA-R-3",
            "Node/Actor",
            body=claim(
                (
                    "relation(source='Actor', name='NARROWER_"
                    "THAN', target='@Continuant')"
                )
            ),
        ),
        carrier(
            "CA-R-4",
            "Node/Aspect",
            body=claim(
                (
                    "relation(source='Aspect', name='NARROWER"
                    "_THAN', target='@Missing')"
                )
            ),
        ),
    ]


class NarrowingGraphTests(_cases.NarrowingCases, unittest.TestCase):
    def test_bare_narrowing_target_uses_declared_unique_parent(self):
        graph, _ = compose_narrowing_graph(
            [
                carrier("CA-R-0", "Node"),
                carrier("CA-R-1", "Node/Continuant"),
                carrier("CA-R-2", "Event Record", body=event_record_claim()),
                carrier(
                    "CA-R-3",
                    "Node/Other",
                    body=claim(
                        (
                            "relation(source='Other', name='NARROWER_"
                            "THAN', target='Missing')"
                        )
                    ),
                ),
            ]
        )
        names = {row["id"]: row["identity"] for row in graph["nodes"]}
        edges = {
            (names[row["relation_source"]], names[row["relation_target"]])
            for row in graph["edges"]
        }
        self.assertIn(("Event Record", "Node/Continuant"), edges)
        self.assertTrue(
            any("undeclared endpoint" in row for row in graph["diagnostics"])
        )
        self.assertFalse(
            any(
                "Event Record: no explicit" in row
                for row in graph["diagnostics"]
            )
        )

    def test_bare_narrowing_target_with_duplicate_declarations_is_not_bound(
        self,
    ):
        graph, _ = compose_narrowing_graph(
            [
                carrier("CA-R-0", "Node"),
                carrier("CA-R-1", "Node/Continuant"),
                carrier("CA-R-2", "Node/Continuant"),
                carrier(
                    "CA-R-3",
                    "Event Record",
                    body=claim(
                        (
                            "relation(source='Event Record', name='NA"
                            "RROWER_THAN', target='Continuant')"
                        )
                    ),
                ),
            ]
        )
        self.assertTrue(
            any(
                "reference `Continuant` is ambiguous" in row
                for row in graph["diagnostics"]
            )
        )

    def test_instance_group_cannot_create_a_narrowing_edge(self):
        graph, _ = compose_narrowing_graph(
            [
                carrier("CA-R-1", "Node"),
                carrier("CA-R-2", "Node/Continuant"),
                carrier(
                    "CA-R-3",
                    "Node/Actor",
                    body=claim(
                        (
                            "# instances\nrelation(source='Actor', nam"
                            "e='NARROWER_THAN', target='@Continuant')"
                        )
                    ),
                ),
            ]
        )
        names = {row["id"]: row["identity"] for row in graph["nodes"]}
        edges = {
            (names[row["relation_source"]], names[row["relation_target"]])
            for row in graph["edges"]
        }
        self.assertNotIn(("Node/Actor", "Node/Continuant"), edges)

    def test_missing_and_ambiguous_reference_parents_are_diagnostics(self):
        graph, _ = compose_narrowing_graph(missing_carriers())
        names = {row["id"]: row["identity"] for row in graph["nodes"]}
        edges = {
            (names[row["relation_source"]], names[row["relation_target"]])
            for row in graph["edges"]
        }
        self.assertNotIn(("Node/Actor", "Node/Continuant"), edges)
        self.assertTrue(
            any(
                "reference `Continuant` is ambiguous" in row
                for row in graph["diagnostics"]
            )
        )
        self.assertTrue(
            any(
                "Aspect` -> `Missing` has an undeclared endpoint" in row
                for row in graph["diagnostics"]
            )
        )

    def _cfel_components(
        self,
    ):
        graph, _ = compose_narrowing_graph(
            [
                carrier("CA-R-1", "CFEL", form="Entity Definition"),
                carrier("CA-R-2", "CFEL <+ Format"),
                carrier("CA-R-3", "CFEL <+ Format/bool"),
                carrier("CA-R-4", "CFEL <+ Operator//not-a-primary-component"),
                carrier("CA-R-5", "CFEL <+ Relation//RUN"),
            ]
        )

        nodes = {row["identity"]: row for row in graph["nodes"]}
        self.assertEqual({"CFEL", "Format", "Format/bool"}, set(nodes))
        names = {row["id"]: row["identity"] for row in graph["nodes"]}
        edges = {
            (names[row["relation_source"]], names[row["relation_target"]])
            for row in graph["edges"]
        }
        self.assertEqual({("Format/bool", "Format")}, edges)
        self.assertFalse(
            any(
                "Format" in row and "undeclared endpoint" in row
                for row in graph["diagnostics"]
            )
        )
        self.assertFalse(
            any(
                "Operator//not-a-primary-component" in row
                for row in graph["diagnostics"]
            )
        )
        self.assertFalse(
            any("Relation//RUN" in row for row in graph["diagnostics"])
        )

    locals()[
        (
            "test_declared_cfel_components_form_their_o"
            "wn_narrowing_branch_not_a_composition_edge"
        )
    ] = _cfel_components

    def test_namespace_prefix_admits_only_the_local_narrowing_tree(self):
        graph, _ = compose_narrowing_graph(
            [
                carrier("CA-R-1", "ANECHOIC <+ MODEL <+ Node"),
                carrier("CA-R-2", "ANECHOIC <+ MODEL <+ Node/Atom"),
                carrier("CA-R-3", "ANECHOIC <+ MODEL <+ CFEL <+ Format"),
                carrier("CA-R-4", "ANECHOIC <+ MODEL <+ CFEL <+ Format/bool"),
            ]
        )

        names = {row["id"]: row["identity"] for row in graph["nodes"]}
        edges = {
            (names[row["relation_source"]], names[row["relation_target"]])
            for row in graph["edges"]
        }
        self.assertTrue(
            {"Node", "Node/Atom", "Format", "Format/bool"}
            <= set(names.values())
        )
        self.assertIn(("Node/Atom", "Node"), edges)
        self.assertIn(("Format/bool", "Format"), edges)
        self.assertFalse(any("ANECHOIC" in edge for edge in edges))

    def test_explicit_namespace_roots_do_not_create_primary_nodes(self):
        graph, _ = compose_narrowing_graph(
            [
                carrier("CA-R-1", "ANECHOIC_MODEL"),
                carrier("CA-R-2", "ANECHOIC_STRUCTURE"),
                carrier("CA-R-3", "ANECHOIC_MODEL <+ Node"),
            ]
        )
        self.assertEqual({"Node"}, {row["identity"] for row in graph["nodes"]})
