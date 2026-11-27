"""Source-bound graph projection cases."""

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(TOOL := Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(TOOL.parent))

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.GENERATE_ENTITY_GRAPH__shared import compose_current_graph, compose_enhanced_current_graph
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.GENERATE_ENTITY_GRAPH__tests.enhanced_graph_test_support import carrier


class EnhancedCurrentGraphTests(unittest.TestCase):
    def test_selection_scopes_do_not_emit_entities_or_declarations(self) -> None:
        values = ("Node.**", "Node//", "@(Node.**)", "ANECHOIC <+ MODEL <+ (Node,Node.**)")
        carriers = [carrier(f"CA-R-{i}", {"active": value, "passive": []}, declaration=True)
                    for i, value in enumerate(values, 1)]
        graph, provenance = compose_enhanced_current_graph(carriers)
        self.assertEqual([], graph["nodes"])
        self.assertEqual([], graph["edges"])
        self.assertEqual(4, len(graph["diagnostics"]))
        self.assertEqual(4, len(provenance["occurrences"]))
        for category in ("primary_nodes", "properties", "instances"):
            self.assertEqual([], graph["model"][category])
        for value in values:
            with self.assertRaisesRegex(ValueError, "Complex Subject selection"):
                compose_current_graph([carrier("CA-R-1", {"active": value})])

    def test_migrated_subject_keys_keep_the_legacy_graph_shape(self) -> None:
        legacy, _ = compose_current_graph([
            carrier("CA-R-1001", {"governs": "Node.Property", "depends_on": []}),
        ])
        migrated, _ = compose_current_graph([
            carrier("CA-R-1001", {"active": "Node.Property", "passive": []}),
        ])
        self.assertEqual(legacy, migrated)

    def test_conflicting_subject_aliases_fail_before_graph_projection(self) -> None:
        with self.assertRaisesRegex(ValueError, "Conflicting carrier aliases"):
            compose_current_graph([
                carrier("CA-R-1001", {"active": "Node", "governs": "Other", "passive": []}),
            ])

    def test_enhanced_view_keeps_unparseable_current_subjects_as_diagnostics(self) -> None:
        graph, _ = compose_enhanced_current_graph([
            carrier(
                "CA-R-1016",
                {"active": "CFEL > Relation//rationale_for", "passive": []},
                declaration=True,
                form="Relation Definition",
            ),
        ])
        self.assertEqual([], graph["model"]["relations"])
        self.assertEqual(
            ["CFEL > Relation//rationale_for"],
            [row["expression"] for row in graph["model"]["selected_subject_expressions"]],
        )
        self.assertTrue(any("CA-R-1016" in row and "Subject projection failed" in row for row in graph["diagnostics"]))
        self.assertTrue(any("CA-R-1016" in row and "Model target unavailable" in row for row in graph["diagnostics"]))

    def test_qualified_declaration_admits_its_node_but_other_roles_do_not(self) -> None:
        graph, _ = compose_enhanced_current_graph([
            carrier(
                "CA-R-1001", {"active": "Atom/(.Role := Requirement)/(.Form := Rule)", "passive": []},
                declaration=True,
            ),
            carrier(
                "CA-C-1002", {"active": "Atom/(.Role := Concern)", "passive": []},
            ),
        ])
        self.assertTrue(graph["nodes"], "legacy syntax graph remains available")
        self.assertEqual(
            ["Atom/(.Role:=Requirement)/(.Form:=Rule)"],
            [row["identity"] for row in graph["model"]["primary_nodes"]],
        )
        self.assertEqual([], graph["model"]["properties"])
        self.assertEqual(
            ["Atom/(.Role := Concern)", "Atom/(.Role := Requirement)/(.Form := Rule)"],
            [row["expression"] for row in graph["model"]["selected_subject_expressions"]],
        )

    def test_namespace_prefixes_add_containment_without_changing_local_targets(self) -> None:
        graph, _ = compose_enhanced_current_graph([
            carrier("CA-R-1001", {"active": "ANECHOIC <+ MODEL <+ Node", "passive": []}, declaration=True),
            carrier("CA-R-1002", {"active": "ANECHOIC <+ MODEL <+ Node.Property", "passive": []}, declaration=True),
            carrier("CA-R-1003", {"active": "ANECHOIC <+ MODEL <+ Workflow//Daily", "passive": []}, declaration=True),
            carrier("CA-R-1004", {"active": "ANECHOIC <+ MODEL <+ CFEL <+ Relation//RUN", "passive": []}, declaration=True, form="Relation Definition"),
        ])

        self.assertEqual({"Node"}, {
            row["identity"] for row in graph["model"]["primary_nodes"]
        })
        self.assertEqual(["Node.Property"], [row["identity"] for row in graph["model"]["properties"]])
        self.assertEqual(["Workflow//Daily"], [row["identity"] for row in graph["model"]["instances"]])
        self.assertEqual(["Relation//RUN"], [row["identity"] for row in graph["model"]["relations"]])
        nodes = {row["id"]: row["identity"] for row in graph["nodes"]}
        containment = {
            (nodes[row["relation_source"]], nodes[row["relation_target"]])
            for row in graph["edges"] if row["kind"] == "IS_CONTAINED_BY"
        }
        self.assertIn(("MODEL", "ANECHOIC"), containment)

    def test_inverse_glyph_projects_distinct_relation_endpoints(self) -> None:
        graph, _ = compose_current_graph([
            carrier("CA-R-1", {"active": "Relation//NARROWER_THAN <--> Relation//BROADER_THAN"}),
        ])
        names = {row["id"]: row["identity"] for row in graph["nodes"]}
        self.assertTrue({"Relation//NARROWER_THAN", "Relation//BROADER_THAN"} <=
                        set(names.values()))
        inverse = [row for row in graph["edges"] if row["kind"] == "HAS_INVERSE"]
        self.assertEqual(1, len(inverse))
        self.assertEqual(("Relation//NARROWER_THAN", "Relation//BROADER_THAN"),
                         (names[inverse[0]["relation_source"]], names[inverse[0]["relation_target"]]))

    def test_bare_legacy_namespace_subjects_remain_literal_without_containment(self) -> None:
        for subject in ("MODEL", "PROJECT STRUCTURE"):
            graph, _ = compose_current_graph([carrier("CA-R-1", {"active": subject})])
            target, = graph["nodes"]
            self.assertEqual(subject, target["identity"])
            self.assertTrue(target["is_full_target"])
            self.assertEqual([], graph["edges"])

    def test_explicit_roots_are_not_model_nodes_and_grouped_selectors_project(self) -> None:
        graph, _ = compose_enhanced_current_graph([
            carrier("CA-R-1001", {"active": "ANECHOIC_MODEL", "passive": []}, declaration=True),
            carrier("CA-R-1002", {"active": "ANECHOIC_STRUCTURE", "passive": []}, declaration=True),
            carrier("CA-R-1003", {"active": "ANECHOIC_MODEL <+ (Atom/(.Header.Role := Method))", "passive": []}, declaration=True),
            carrier("CA-R-1004", {"active": "(ANECHOIC_MODEL <+ Atom)/(.Header.Form := Rule)", "passive": []}, declaration=True),
        ])
        self.assertEqual({"Atom/(.Header.Role:=Method)", "Atom/(.Header.Form:=Rule)"},
                         {row["identity"] for row in graph["model"]["primary_nodes"]})
        self.assertEqual([], graph["diagnostics"])
