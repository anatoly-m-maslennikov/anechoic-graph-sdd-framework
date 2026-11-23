"""Source-bound graph constraints cases."""

from pathlib import Path
import sys
import tempfile
import unittest

TOOL = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(TOOL.parent), str(TOOL)]

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.GENERATE_ENTITY_GRAPH__shared import extract_claim_constraints
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.current_entity_sources import build_current_model_graph
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.GENERATE_ENTITY_GRAPH__shared import compose_enhanced_current_graph
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.GENERATE_ENTITY_GRAPH__shared import render_model
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.GENERATE_ENTITY_GRAPH__tests.enhanced_graph_test_support import carrier, property_population_records, fenced_scope_records


class EnhancedCurrentGraphTests(unittest.TestCase):
    def test_scoped_claims_are_preserved_without_unqualified_bindings(self):
        records, diagnostics = extract_claim_constraints(carrier("CA-R-1001", {}, """## Claim
```CFEL
# model
Atom/(.Header.Role: Plan);
Atom/(.Header.Role: Plan).Header.Priority: [string]{:0..1};
Atom/(.Header.Role: Plan).Header.Priority.*[]{:0};
Atom/(.Header.Role: Plan).Header.Priority: High;
# instances
Atom/(.Header.Role: Plan)//$atom;
Atom/(.Header.Role: )//$bad;
IF (A) THEN (B)
```
"""))
        self.assertEqual(["subject_expression", "property_constraint", "property_constraint", "allowed_literal", "instance_binding"],
                         [row["kind"] for row in records])
        self.assertTrue(all(".Header.Role: Plan" in row.get("property_selector", row.get("kind_selector", row.get("expression", ""))) for row in records))
        self.assertEqual("atom", records[-1]["variable"])
        self.assertEqual(["Atom/(.Header.Role: )//$bad", "IF (A) THEN (B)"], [row["expression"] for row in diagnostics])

    def test_grouped_constraints_keep_declaration_model_and_instance_evidence_separate(self) -> None:
        block = """# model
Node.Name: [string]{:1};
Node ((CONTAINS)) Node;
# instances
Node//$n;
$n.Name: [integer]{:1};
$n ((CONTAINS)) Node//$child
"""
        graph, _ = compose_enhanced_current_graph([
            carrier("CA-R-1", {"active": "Node", "passive": []}, declaration=True),
            carrier("CA-R-2", {"active": "Node.Name", "passive": []}, "## Claim\n### Formal Claim\n```CFEL\n" + block + "```\n", declaration=True),
            carrier("CA-R-3", {"active": "Node.Name", "passive": []}, "## Claim\n```CFEL\n# model\nNode.Name: [integer]{:1};\n```\n", declaration=True, form="Rule"),
        ])
        self.assertEqual(["string"], [row["value_format"] for row in graph["model_contracts"]])
        self.assertEqual(["integer"], [row["value_format"] for row in graph["source_constraints"]])
        self.assertEqual({"instance_binding", "property_constraint", "relation_cardinality"},
                         {row["kind"] for row in graph["instance_constraints"]})
        self.assertTrue(any(row.get("relation") == "CONTAINS" for row in graph["constraints"]))
        self.assertIn(block, [row["block"] for row in graph["formal_claim_blocks"]])
        self.assertFalse(any("$n" in row["identity"] for row in graph["model"]["primary_nodes"]))

    def test_enhanced_view_separates_nodes_instances_relations_classifications_and_constraints(self) -> None:
        graph, _ = compose_enhanced_current_graph([
            carrier("CA-R-1001", {"active": "Node >| Independence", "passive": []}, declaration=True),
            carrier("CA-R-1002", {"active": "Node.Property: literal", "passive": []}, """## Claim
```CFEL
Node.Property{:0..1}: [string]{:1};
Node.Content.**[string]{:0+}: [markdown]{:1};
Journal// {:0+}((CONTAINS)) Event Record//;
Node >| Independence == Primary Node;
IF Node THEN Property
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
        self.assertEqual([], graph["model"]["classifications"])
        self.assertEqual([], graph["model"]["allowed_literals"])
        self.assertIn("Node >| Independence", [
            row["expression"] for row in graph["model"]["selected_subject_expressions"]
        ])
        self.assertEqual(
            {"property_constraint", "relation_cardinality", "classification_condition"},
            {row["kind"] for row in graph["constraints"]},
        )
        self.assertEqual(["cfel-expression-unsupported"], [row["code"] for row in graph["cfel_diagnostics"]])

    def test_property_value_count_is_per_property_and_recursive_name_count_stays_separate(self) -> None:
        records, diagnostics = extract_claim_constraints(carrier("CA-R-1001", {}, """## Claim
```CFEL
Property: [string]{:1};
Property.**[string]{:0+}: [markdown]{:1}
```
"""))
        self.assertEqual([], diagnostics)
        values = next(row for row in records if row["selection"] == "values")
        recursive = next(row for row in records if row["selection"] == "recursive_dependents")
        self.assertEqual("Property", values["property_selector"])
        self.assertIsNone(values["occurrence_cardinality"])
        self.assertEqual({"minimum": 1, "maximum": 1}, values["value_cardinality"])
        self.assertEqual({"minimum": 0, "maximum": None}, recursive["occurrence_cardinality"])
        self.assertEqual({"minimum": 1, "maximum": 1}, recursive["value_cardinality"])

    def test_named_property_occurrences_and_property_population_scopes(self) -> None:
        records, diagnostics = property_population_records()
        self.assertEqual([], diagnostics)
        (bare, bare_explicit, implicit, explicit, bounded, impossible, required, inherited, inherited_explicit,
         forbidden, scheme, scheme_children, inherited_scope, wildcard, prop_population, kind_population) = records
        one = {"minimum": 1, "maximum": 1}
        optional = {"minimum": 0, "maximum": 1}
        self.assertEqual(optional, bare["effective_occurrence_cardinality"])
        self.assertEqual(one, bare_explicit["effective_occurrence_cardinality"])
        self.assertEqual(optional, implicit["effective_occurrence_cardinality"])
        self.assertEqual(one, explicit["effective_occurrence_cardinality"])
        self.assertEqual(optional, bounded["occurrence_cardinality"])
        self.assertEqual(optional, bounded["effective_occurrence_cardinality"])
        self.assertIsNone(impossible["effective_occurrence_cardinality"])
        self.assertTrue(impossible["occurrence_conflict"])
        self.assertEqual(one, required["effective_occurrence_cardinality"])
        self.assertEqual(optional, inherited["value_cardinality"])
        self.assertIsNone(inherited["value_format"])
        self.assertEqual(optional, inherited_explicit["effective_occurrence_cardinality"])
        self.assertIsNone(inherited_explicit["value_format"])
        zero = {"minimum": 0, "maximum": 0}
        self.assertEqual(zero, forbidden["effective_occurrence_cardinality"])
        self.assertFalse(forbidden["occurrence_conflict"])
        self.assertEqual(optional, scheme["effective_occurrence_cardinality"])
        self.assertEqual(one, scheme["value_cardinality"])
        self.assertEqual("markdown", scheme["value_format"])
        self.assertEqual(zero, scheme_children["occurrence_cardinality"])
        self.assertEqual(("recursive_dependent_values", "markdown", None),
                         (inherited_scope["selection"], inherited_scope["value_format"], inherited_scope["value_cardinality"]))
        self.assertNotIn("effective_occurrence_cardinality", inherited_scope)
        self.assertEqual(optional, implicit["value_cardinality"])
        self.assertEqual({"minimum": 0, "maximum": None}, wildcard["effective_occurrence_cardinality"])
        self.assertEqual(("property_instance_population_constraint", "Node", "per_bearer_each_schema", one),
                         (prop_population["kind"], prop_population["bearer_selector"], prop_population["scope"], prop_population["population_cardinality"]))
        self.assertEqual(("instance_population_constraint", "PrimaryKind", "project", one),
                         (kind_population["kind"], kind_population["kind_selector"], kind_population["scope"], kind_population["population_cardinality"]))

    def test_bounded_extractor_preserves_structural_and_reverse_classification_notation(self) -> None:
        records, diagnostics = extract_claim_constraints(carrier("CA-R-1001", {}, """## Claim
```CFEL
Workflow// {:1+}<+{:1} Step//;
Independence |< Node == Primary Node
```
"""))
        self.assertEqual([], diagnostics)
        relation = next(row for row in records if row["kind"] == "relation_cardinality")
        self.assertEqual("<+", relation["relation_notation"])
        self.assertIsNone(relation["relation"])
        classification = next(row for row in records if row["kind"] == "classification_condition")
        self.assertEqual(("Node", "Independence", "Primary Node"),
                         (classification["subject_selector"], classification["axis"], classification["value"]))

    def test_model_renderer_keeps_constraints_and_unsupported_cfel_visible(self) -> None:
        graph, provenance = compose_enhanced_current_graph([
            carrier("CA-R-1001", {"active": "Node.Property: literal", "passive": []}, """## Claim
```CFEL
Node.Property: [string]{:1};
IF Node THEN Property
```
""", declaration=True),
        ])
        document = render_model(
            graph, provenance, updated_at="2026-11-01 00:00:00 +0000",
            source_selection="Current Atoms in sources",
            projection_identity={"projection_id": "CA-PROJ-901", "named_selection": "Current Atoms"},
        )
        for heading in ("## Model graph", "## Primary Nodes", "## Properties", "## Allowed literals", "## Constraints", "## Unsupported CFEL"):
            self.assertIn(heading, document)
        self.assertIn("Node.Property: [string]{:1}", document)
        self.assertIn("IF Node THEN Property", document)

    def test_fail_closed_claim_scope_controls_selectors_and_markdown_fences(self) -> None:
        records, diagnostics = fenced_scope_records()
        property_constraint = next(row for row in records if row["kind"] == "property_constraint")
        self.assertEqual("A", property_constraint["property_selector"])
        self.assertEqual({"minimum": 1, "maximum": 1}, property_constraint["occurrence_cardinality"])
        self.assertEqual({"minimum": 1, "maximum": 1}, property_constraint["value_cardinality"])
        default_relation = next(row for row in records if row["kind"] == "relation_cardinality")
        self.assertEqual(("Node", "*", None, "all_relations"), (
            default_relation["source_selector"], default_relation["relation"],
            default_relation["target_selector"], default_relation["selection"],
        ))
        grouped = next(row for row in records if row["kind"] == "classification_condition")
        self.assertEqual(("Journal", "Container", "yes"),
                         (grouped["subject_selector"], grouped["axis"], grouped["value"]))
        self.assertFalse(any(row.get("property_selector") == "Node >| Container" for row in records))
        self.assertFalse(any(row.get("relation") == "RUN" for row in records))
        unsupported = [row["expression"] for row in diagnostics if row["code"] == "cfel-expression-unsupported"]
        self.assertTrue(any(row["kind"] == "subject_expression" and row["expression"] == "Atom/(.Role := Requirement)/(.Form := Rule)" for row in records))
        self.assertIn("IF(A) THEN(B ((RUN)) C)", unsupported)
        self.assertTrue(any(row.get("kind") == "classification_allowed_value" and row.get("value") == "yes" for row in records))
        self.assertNotIn("Node >| Container: yes", unsupported)
        self.assertIn("Label: 'a;b'", unsupported)
        self.assertIn("FENCED_LABELS(Atom.Content.Claim): [in (CFEL)]{:0..1}", unsupported)
        self.assertIn("A + B{:1}", unsupported)
        self.assertEqual(1, sum(row["code"] == "cfel-fence-outside-claim" for row in diagnostics))

    def test_reverse_named_relation_clause_normalizes_endpoints_and_written_counts(self) -> None:
        records, diagnostics = extract_claim_constraints(carrier("CA-R-1001", {}, """## Claim
```CFEL
Step {:1}((IS_CONTAINED_BY)){:2} Workflow;
Workflow {:2}<((IS_CONTAINED_BY)){:1} Step;
```
"""))
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
                "## Claim\n```CFEL\nProjection.Form{:1}: [string]{:1};\nProjection.Form: Catalog;\nProjection.Form: Map\n```\n",
            )
            write("CA-R-9003", "Requirement", "Relation Definition", "Entity/CFEL <+ Relation//RUN")
            write("CA-R-9004", "Requirement", "Declaration", "Node/Continuant")
            write("CA-R-9005", "Requirement", "Declaration", "Node/Occurrent")
            write("CA-R-9006", "Requirement", "Rule", "(Node, Node/**, .**)")

            graph, _ = build_current_model_graph(source_root, root)

        self.assertEqual(
            ["Node", "Node/Continuant", "Node/Occurrent"],
            [row["identity"] for row in graph["model"]["primary_nodes"]],
        )
        self.assertEqual(["Projection.Form"], [row["identity"] for row in graph["model"]["properties"]])
        self.assertEqual(["Relation//RUN"], [row["identity"] for row in graph["model"]["relations"]])
        self.assertEqual(
            {"Projection.Form: Catalog", "Projection.Form: Map"},
            {row["expression"] for row in graph["constraints"] if row["kind"] == "allowed_literal"},
        )
        self.assertNotIn("CA-R-9006", [row["source"]["atom_id"] for row in graph["model"]["selected_subject_expressions"]])
