"""Source-bound graph constraints cases."""

from pathlib import Path
import sys
import tempfile
import unittest

TOOL = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(TOOL.parent), str(TOOL)]

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.GENERATE_ENTITY_GRAPH__shared import extract_claim_constraints
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import read_current_model_carriers
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.GENERATE_ENTITY_GRAPH__shared import compose_enhanced_current_graph
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.GENERATE_ENTITY_GRAPH__shared import render_model
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.GENERATE_ENTITY_GRAPH__tests.enhanced_graph_test_support import carrier


class EnhancedCurrentGraphTests(unittest.TestCase):
    def test_grouped_constraints_keep_declaration_model_and_instance_evidence_separate(self):
        block = """# model
property_rule(address='Node.Name', value_format='string', values='1')
relation(source='Node', name='CONTAINS', target='Node')
# instances
property_rule(address='Node//$n.Name', value_format='integer', values='1')
relation(source='Node//$n', name='CONTAINS', target='Node//$child')
"""
        graph, _ = compose_enhanced_current_graph([
            carrier("CA-R-1", {"active": "Node", "passive": []}, declaration=True),
            carrier("CA-R-2", {"active": "Node.Name", "passive": []}, "## Claim\n```python\n" + block + "```\n", declaration=True),
            carrier("CA-R-3", {"active": "Node.Name", "passive": []}, """## Claim
```python
property_rule(address='Node.Name', value_format='integer', values='1')
```
""", declaration=True, form="Rule"),
        ])
        self.assertEqual(["string"], [row["value_format"] for row in graph["model_contracts"]])
        self.assertEqual(["integer"], [row["value_format"] for row in graph["source_constraints"]])
        self.assertEqual({"property_constraint", "relation_cardinality"},
                         {row["kind"] for row in graph["instance_constraints"]})
        self.assertTrue(any(row.get("relation") == "CONTAINS" for row in graph["constraints"]))
        self.assertIn(block, [row["block"] for row in graph["formal_claim_blocks"]])
        self.assertFalse(any("$n" in row["identity"] for row in graph["model"]["primary_nodes"]))

    def test_enhanced_view_separates_nodes_instances_relations_classifications_and_constraints(self) -> None:
        graph, _ = compose_enhanced_current_graph([
            carrier("CA-R-1001", {"active": "Node >| Independence", "passive": []}, declaration=True),
            carrier("CA-R-1002", {"active": "Node.Property: literal", "passive": []}, """## Claim
```python
property_rule(address='Node.Property', value_format='string', values='1')
relation(source='Journal//', name='CONTAINS', target='Event Record//', source_count='0+')
```
""", declaration=True),
            carrier("CA-R-1003", {"active": "Workflow//Daily", "passive": []}, declaration=True),
            carrier("CA-R-1004", {"active": "Node", "passive": []}, declaration=True),
            carrier("CA-R-1005", {"active": "Node.Property", "passive": []}, declaration=True),
        ])
        self.assertEqual("current_atom_model_graph", graph["kind"])
        self.assertEqual(
            {"Node"},
            {row["identity"] for row in graph["model"]["primary_nodes"]},
        )
        self.assertEqual(["Node.Property"], [row["identity"] for row in graph["model"]["properties"]])
        self.assertEqual(["Workflow//Daily"], [row["identity"] for row in graph["model"]["instances"]])
        self.assertEqual([], graph["model"]["relations"])
        self.assertEqual([], graph["model"]["axes"])
        self.assertEqual([], graph["model"]["allowed_literals"])
        self.assertIn("Node >| Independence", [
            row["expression"] for row in graph["model"]["selected_subject_expressions"]
        ])
        self.assertEqual(
            {"property_constraint", "relation_cardinality"},
            {row["kind"] for row in graph["constraints"]},
        )
        self.assertEqual([], graph["claim_diagnostics"])

    def test_model_renderer_keeps_constraint_and_unsupported_helper_visible(self):
        graph, provenance = compose_enhanced_current_graph([
            carrier("CA-R-1001", {"active": "Node.Property: literal", "passive": []}, """## Claim
```python
property_rule(address='Node.Property', value_format='string', values='1')
deliver(source='Atom//$atom', carrier='Carrier//$carrier')
```
""", declaration=True),
        ])
        document = render_model(
            graph, provenance, updated_at="2026-11-01 00:00:00 +0000",
            source_selection="Current Atoms in sources",
            projection_identity={"projection_id": "CA-PROJ-901", "named_selection": "Current Atoms"},
        )
        for heading in ("## Model graph", "## Primary Nodes", "## Properties", "## Allowed literals",
                        "## Constraints", "## Python Formal Claim diagnostics"):
            self.assertIn(heading, document)
        self.assertIn("Node.Property:: [string]{::1}", document)
        self.assertIn("Atom//$atom >> Carrier//$carrier", document)

    def test_reverse_named_relation_clause_normalizes_endpoints_and_written_counts(self) -> None:
        records, diagnostics = extract_claim_constraints(carrier("CA-R-1001", {}, """## Claim
```python
relation(source='Step', name='IS_CONTAINED_BY', target='Workflow', source_count='1', target_count='2')
relation(source='Workflow', name='IS_CONTAINED_BY', target='Step', source_count='2', target_count='1', reverse=True)
```
""", declaration=True))
        self.assertEqual([], diagnostics)
        forward, reverse = records
        self.assertEqual(
            (forward["relation"], forward["source_selector"], forward["target_selector"],
             forward["source_cardinality"], forward["target_cardinality"]),
            (reverse["relation"], reverse["source_selector"], reverse["target_selector"],
             reverse["source_cardinality"], reverse["target_cardinality"]),
        )
        self.assertEqual("forward", forward["written_direction"])
        self.assertEqual("reverse", reverse["written_direction"])
        self.assertEqual(("Workflow", "Step"),
                         (reverse["written_source_selector"], reverse["written_target_selector"]))

    def test_post_cutover_role_form_frontier_keeps_catalogue_and_constraints_separate(self) -> None:
        temporary_root = Path.cwd() / ".anechoic_tmp/tests/test_enhanced_current_graph"
        temporary_root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=temporary_root) as temporary:
            root = Path(temporary)
            source_root = root / "current-model"
            source_root.mkdir()

            def write(atom_id: str, role: str, form: str, active: str, claim: str = "") -> None:
                (source_root / f"{atom_id}.md").write_text(
                    "---\n"
                    f"atom_id: {atom_id}\nversion: 1\nstatus: Active\nrole: {role}\nform: {form}\n"
                    f"subjects:\n  active: {active}\n  passive: []\n---\n" + claim,
                    encoding="utf-8",
                )

            write("CA-R-9001", "Requirement", "Declaration", "Node")
            write(
                "CA-R-9002", "Requirement", "Declaration", "Projection.Form",
                "## Claim\n```python\nfrom anechoic.formal_claims import declare_entity\ndeclare_entity(entity_name='Form', relation_name='IS_PROPERTY_OF', base_path='Projection', allowed_values=('Catalog', 'Map'), property_occurrence_cardinality=1, value_cardinality=1, value_format=str)\n```\n",
            )
            write("CA-R-9003", "Requirement", "Relation Definition", "Entity/CFEL <+ Relation//RUN")
            write("CA-R-9004", "Requirement", "Declaration", "Node/Continuant")
            write("CA-R-9005", "Requirement", "Declaration", "Node/Occurrent")
            write("CA-R-9006", "Requirement", "Rule", "(Node, Node/**, .**)")

            graph, _ = compose_enhanced_current_graph(read_current_model_carriers(source_root, root))

        self.assertEqual(
            ["Node", "Node/Continuant", "Node/Occurrent"],
            [row["identity"] for row in graph["model"]["primary_nodes"]],
        )
        self.assertEqual(["Projection.Form"], [row["identity"] for row in graph["model"]["properties"]])
        self.assertEqual(["Relation//RUN"], [row["identity"] for row in graph["model"]["relations"]])
        self.assertEqual(
            {"Projection.Form :: Catalog", "Projection.Form :: Map"},
            {row["expression"] for row in graph["constraints"] if row["kind"] == "allowed_literal"},
        )
        self.assertNotIn("CA-R-9006", [row["source"]["atom_id"] for row in graph["model"]["selected_subject_expressions"]])
