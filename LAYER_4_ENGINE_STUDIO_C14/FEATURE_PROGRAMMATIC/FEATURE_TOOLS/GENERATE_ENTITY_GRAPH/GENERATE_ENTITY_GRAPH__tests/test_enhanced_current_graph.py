"""Source-bound graph projection cases."""

from pathlib import Path
import sys
import tempfile
import unittest

TOOL = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(TOOL.parent), str(TOOL)]

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.cfel_claim_constraints import preview_constraints_from_paths
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.current_subject_common import subject_facts
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.current_subject_graph import compose_current_graph, compose_enhanced_current_graph
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.readable_entity_tree import render_model
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
                subject_facts(value)

    def test_model_binder_is_opaque_and_population_count_applies_to_selection(self) -> None:
        block = '''# model
IF $model_node in (Node, Node.**) THEN (
  $model_node.Name: [string]{:1};
  IF $model_node >| Category == "A; B" THEN ($model_node.X: [string]{:1})
);
Relation//$relation ((HAS_INVERSE)) Relation//$relation_2;
# instances
Node//$n{:1..3};
$n.Name: [string]{:1}
'''
        graph, _ = compose_enhanced_current_graph([
            carrier("CA-R-1", {"active": "Node", "passive": []}, declaration=True),
            carrier("CA-R-2", {"active": "Node.Name", "passive": []}, "## Claim\n### Formal Claim\n```CFEL\n" + block + "```\n", declaration=True),
        ])
        binder = next(row for row in graph["constraints"] if row["kind"] == "model_binding")
        self.assertEqual("model_node", binder["variable"])
        self.assertEqual("Node, Node.**", binder["selection"])
        self.assertIn('"A; B"', binder["expression"])
        self.assertEqual("opaque", binder["interpretation"])
        self.assertEqual([], graph["model_contracts"])
        population = next(row for row in graph["instance_constraints"] if row["kind"] == "instance_population_constraint")
        self.assertEqual({"minimum": 1, "maximum": 3}, population["population_cardinality"])
        self.assertEqual("Node", population["kind_selector"])
        self.assertTrue(any(row.get("relation") == "HAS_INVERSE" for row in graph["constraints"]))
        self.assertFalse(any("$" in row["identity"] for row in graph["model"]["primary_nodes"]))
        self.assertIn(block, [row["block"] for row in graph["formal_claim_blocks"]])

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

    def test_model_renderer_keeps_nonexpression_cfel_diagnostic_visible(self) -> None:
        graph, provenance = compose_enhanced_current_graph([
            carrier("CA-R-1001", {"active": "Node", "passive": []}, """## Claim
```CFEL
Node: [string]{:1}
""", declaration=True),
        ])
        document = render_model(
            graph, provenance, updated_at="2026-11-01 00:00:00 +0000",
            source_selection="Current Atoms in sources",
            projection_identity={"projection_id": "CA-PROJ-901", "named_selection": "Current Atoms"},
        )
        self.assertIn("CFEL fence has no closing fence", document)

    def test_explicit_draft_paths_are_read_only_preview_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = root / "draft" / "CA-R-1001@1-draft.md"
            path.parent.mkdir()
            path.write_text(
                "---\natom_id: CA-R-1001\nversion: 1\nstatus: Draft\nsubjects:\n  active: Node\n"
                "---\n## Claim\n```CFEL\nNode.Property: [string]{:1};\nIF Node THEN Property\n```\n",
                encoding="utf-8",
            )
            before = path.read_bytes()
            records, diagnostics = preview_constraints_from_paths([path], repository=root)
            self.assertEqual("property_constraint", records[0]["kind"])
            self.assertEqual("draft/CA-R-1001@1-draft.md", records[0]["source"]["path"])
            self.assertEqual("cfel-expression-unsupported", diagnostics[0]["code"])
            self.assertEqual(before, path.read_bytes())

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
        nodes, facts, _ = subject_facts("Relation//NARROWER_THAN <--> Relation//BROADER_THAN")
        self.assertTrue({"Relation//NARROWER_THAN", "Relation//BROADER_THAN"} <=
                        {row["identity"] for row in nodes})
        inverse = [row for row in facts if row["kind"] == "HAS_INVERSE"]
        self.assertEqual(1, len(inverse))
        self.assertEqual(("Relation//NARROWER_THAN", "Relation//BROADER_THAN"),
                         (inverse[0]["source"], inverse[0]["target"]))

    def test_bare_legacy_namespace_subjects_remain_literal_without_containment(self) -> None:
        for subject in ("MODEL", "PROJECT STRUCTURE"):
            nodes, facts, target = subject_facts(subject)
            self.assertEqual([subject], [row["identity"] for row in nodes])
            self.assertEqual([], facts)
            self.assertEqual(subject, target)

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
