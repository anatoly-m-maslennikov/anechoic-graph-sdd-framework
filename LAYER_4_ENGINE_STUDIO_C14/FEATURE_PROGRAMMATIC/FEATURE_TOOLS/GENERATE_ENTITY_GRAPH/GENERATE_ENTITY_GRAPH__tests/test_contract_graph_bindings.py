"""Source-bound graph bindings cases."""

from pathlib import Path
import sys
import unittest

TOOL = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(TOOL.parent), str(TOOL)]

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.GENERATE_ENTITY_GRAPH__shared import compose_contract_graph
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.GENERATE_ENTITY_GRAPH__shared import render_contract_graph
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.GENERATE_ENTITY_GRAPH__tests.contract_graph_test_support import carrier, body, scope_context_graph


class ContractGraphTests(unittest.TestCase):
    def test_explicit_namespace_header_qualifications_bind_declared_properties(self):
        graph = compose_contract_graph([
            carrier("CA-R-1", "ANECHOIC_MODEL <+ Atom", body("Atom.")),
            carrier("CA-R-2", "ANECHOIC_MODEL <+ Atom.Header", body("Header.")),
            carrier("CA-R-3", "ANECHOIC_MODEL <+ Atom.Header.Role", body("Role.")),
            carrier("CA-R-4", "ANECHOIC_MODEL <+ Atom.Header.Form", body("Form.")),
            carrier("CA-R-5", "ANECHOIC_MODEL <+ Atom/(.Header.Role:=Requirement)", body("Role rule."), form="Rule"),
            carrier("CA-R-6", "ANECHOIC_MODEL <+ Atom/(.Header.Form:=Declaration)", body("Form rule."), form="Rule"),
            carrier("CA-R-7", "ANECHOIC_MODEL <+ (Node, Node.**)", body("Scope."), form="Rule"),
            carrier("CA-R-8", "ANECHOIC_MODEL <+ Node", body("Node.")),
            carrier("CA-R-9", "ANECHOIC_MODEL <+ Atom/(.Header.Role:=Requirement)/(.Header.Form:=Declaration)", body("Combined rule."), form="Rule"),
            carrier("CA-R-10", "ANECHOIC_MODEL <+ Atom/(.Header.Role: Method)/(.Header.Form: Declaration)", body("Combined colon rule."), form="Rule"),
            carrier("CA-R-11", "ANECHOIC_MODEL <+ Atom.Content.Claim", body("Claim.")),
            carrier("CA-R-12", "ANECHOIC_MODEL <+ Atom/(.Header.Role: Delivery).Content.Claim", body("Claim rule."), form="Rule"),
        ])
        rows = {row["target"]: row for row in graph["entities"]}
        self.assertEqual({"Atom", "Atom.Header", "Atom.Header.Role", "Atom.Header.Form", "Atom.Content.Claim", "Node"}, set(rows))
        self.assertEqual({"Atom.Header.Role", "Atom.Header.Form"},
                         {row["binding_context"]["property"] for row in rows["Atom"]["shared"] if "property" in row["binding_context"]})
        combined = next(row for row in rows["Atom"]["shared"] if row["source"]["atom_id"] == "CA-R-9")
        self.assertEqual(["Atom.Header.Role", "Atom.Header.Form"], combined["binding_context"]["properties"])
        self.assertEqual("CA-R-12", rows["Atom.Content.Claim"]["shared"][0]["source"]["atom_id"])
        self.assertEqual([], rows["Node"]["shared"])
        self.assertIn("complex selection scope", graph["coverage_gaps"][0]["message"])

    def test_attaches_exact_shared_rmed_evidence_and_links_transitive_properties_without_copies(self):
        graph = compose_contract_graph([
            carrier("CA-R-1", "Node", body("Node declaration.")),
            carrier("CA-R-2", "Node/Parent", body("Parent declaration.")),
            carrier("CA-R-3", "Node/Parent/Child", body("Child declaration.")),
            carrier("CA-R-4", "Node/Parent.Status", body(
                "### Formal Claim", "```python", "from anechoic.formal_claims import declare_entity",
                "declare_entity(entity_name='Status', relation_name='IS_PROPERTY_OF', base_path='Node/Parent',",
                "  value_format=str, value_cardinality=1)", "```")),
            carrier("CA-R-5", "Node/Parent/Child", body("Rule for Child."), form="Rule"),
            carrier("CA-D-6", "Node/Parent/Child", body("Delivery for Child."), role="Delivery", form="Markdown"),
            carrier("CA-R-7", "Node/Unknown", body("### Formal Claim", "```python", "# model",
                "property_rule(address='Node/Unknown.Status', value_format='string', values='1')", "```"), form="Rule"),
        ])

        rows = {row["target"]: row for row in graph["entities"]}
        child = rows["Node/Parent/Child"]
        self.assertEqual(["CA-D-6@1", "CA-R-5@1"], child["shared_sources"])
        self.assertEqual(["Node/Parent", "Node"], [row["target"] for row in child["transitive_ancestors"]])
        self.assertEqual(["Node/Parent.Status"], [row["target"] for row in child["inherited_property_declarations"]])
        self.assertNotIn("Node/Parent/Child.Status", rows)
        self.assertEqual(1, graph["coverage"]["coverage_gaps"])
        self.assertIn("Node/Unknown.Status", graph["coverage_gaps"][0]["blocks"][0]["block"])
        rendered = render_contract_graph(graph)
        self.assertLess(rendered.index("## Declared Narrowing Tree"), rendered.index("## Entity and Property Contracts"))
        self.assertIn("Transitive ancestor Declarations", rendered)
        self.assertIn("Inherited Property Declaration refs", rendered)

    def test_keeps_cfel_component_and_semantics_without_inventing_a_node(self):
        graph = compose_contract_graph([
            carrier("CA-R-1", "CFEL <+ Format", body("Format declaration.", semantics="A CFEL component.")),
            carrier("CA-R-2", "CFEL", body("CFEL root declaration.")),
            carrier("CA-R-3", "Operator", body("Operator kind declaration.")),
            carrier("CA-R-4", "Operator//Anatoly", body("Operator instance declaration.")),
        ])

        self.assertEqual(["CFEL", "Format"], [row["target"] for row in graph["components"]])
        self.assertEqual({("Operator", "primary_node"), ("Operator//Anatoly", "instance")},
                         {(row["target"], row["kind"]) for row in graph["entities"]})
        instance = next(row for row in graph["entities"] if row["kind"] == "instance")
        self.assertEqual(["CA-R-3@1"], instance["instance_of"]["effective_source_refs"])
        rendered = render_contract_graph(graph)
        self.assertIn("CFEL, Carrier, and Term Component Contracts", rendered)
        self.assertIn("A CFEL component.", rendered)

    def test_keeps_explicit_cfel_component_properties_and_instances_out_of_narrowing_tree(self):
        graph = compose_contract_graph([
            carrier("CA-R-1", "CFEL", body("CFEL root declaration.")),
            carrier("CA-R-2", "CFEL <+ Format", body("Format declaration.")),
            carrier("CA-R-3", "CFEL <+ Format.Data Type", body("Format Property declaration.")),
            carrier("CA-R-4", "CFEL <+ Format//markdown", body("Markdown format declaration.")),
            carrier("CA-R-5", "CFEL <+ Operator", body("Operator declaration.")),
            carrier("CA-R-6", "CFEL <+ Operator//Addition", body("Addition declaration.")),
        ])

        rows = {row["target"]: row for row in graph["entities"]}
        self.assertEqual("property", rows["Format.Data Type"]["kind"])
        self.assertEqual("instance", rows["Format//markdown"]["kind"])
        self.assertEqual("instance", rows["Operator//Addition"]["kind"])
        self.assertEqual(["CA-R-2@1"], rows["Format//markdown"]["instance_of"]["effective_source_refs"])
        self.assertEqual(
            {"CFEL", "Format", "Operator"},
            {row["identity"] for row in graph["narrowing_tree"]["nodes"]},
        )
        self.assertEqual([], graph["narrowing_tree"]["edges"])
        self.assertFalse(graph["inheritance_diagnostics"])
        self.assertEqual(0, graph["coverage"]["coverage_gaps"])
        self.assertEqual(0, graph["coverage"]["instance_kind_gaps"])

    def test_binds_only_declared_value_and_qualifier_conditions_and_keeps_other_evidence_scoped(self):
        graph = compose_contract_graph([
            carrier("CA-R-1", "Atom", body("Atom declaration.")),
            carrier("CA-R-2", "Atom.Status", body("Status declaration.")),
            carrier("CA-R-3", "Projection", body("Projection declaration.")),
            carrier("CA-R-4", "Projection.Form", body("Form declaration.")),
            carrier("CA-R-5", "Atom.Status:Draft", body("Draft status rule."), form="Rule"),
            carrier("CA-R-6", "Projection/(.Form:=ApplicableMethodology)", body("Projection form rule."), form="Rule"),
            carrier("CA-R-7", "Atom.Kind:Unknown", body("Unknown property rule."), form="Rule"),
            carrier("CA-M-8", "Method/PlanProcess", body("Method evidence."), role="Method", form="Policy"),
        ])

        rows = {row["target"]: row for row in graph["entities"]}
        self.assertEqual("allowed_value_condition", rows["Atom.Status"]["shared"][0]["binding"])
        self.assertEqual("Atom.Status:Draft", rows["Atom.Status"]["shared"][0]["subject"])
        self.assertEqual("property_qualification", rows["Projection"]["shared"][0]["binding"])
        self.assertNotIn("Projection/(.Form:=ApplicableMethodology)", rows)
        self.assertEqual(1, graph["coverage"]["coverage_gaps"])
        self.assertEqual(1, graph["coverage"]["outside_model_scope_sources"])
        self.assertEqual("outside_model_scope", graph["outside_model_scope"][0]["selection_disposition"])

    def test_namespace_declaration_preserves_claim_without_creating_node(self):
        graph = compose_contract_graph([carrier("CA-R-1", "ANECHOIC_MODEL", body("```python", "classify(address='MODEL', axis='Container', value='yes', notation='relation')", "```")),
                                        carrier("CA-R-2", "UNKNOWN_MODEL", body("Unknown."))])
        self.assertEqual(["ANECHOIC_MODEL"], [row["target"] for row in graph["namespaces"]])
        self.assertEqual(["UNKNOWN_MODEL"], [row["target"] for row in graph["entities"]])
        self.assertEqual([], graph["coverage_gaps"])
        self.assertIn("`MODEL` — HAS_AXIS → `Container == yes`", render_contract_graph(graph))

    def test_render_written_and_effective_occurrence_and_value_bounds(self):
        graph = compose_contract_graph([
            carrier("CA-R-1", "Node", body("Node.")),
            carrier("CA-R-2", "Node.Name", body(
                "```python", "from anechoic.formal_claims import declare_entity, Cardinality", "declare_entity(entity_name='Name', relation_name='IS_PROPERTY_OF', base_path='Node', property_occurrence_cardinality=Cardinality(minimum=0, maximum=1), value_format='string', value_cardinality=Cardinality(minimum=0, maximum=1))", "```")),
        ])
        document = render_contract_graph(graph)
        self.assertIn("written names count=0..1; effective names count=0..1", document)
        self.assertIn("values count=0..1", document)

    def test_binds_only_source_proven_scope_unit_declaration_instance_contexts(self):
        graph = scope_context_graph()

        entities = {row["target"]: row for row in graph["entities"]}
        scope_shared = entities["Scope Unit"]["shared"]
        project_shared = entities["Project"]["shared"]
        projection_shared = entities["Projection"]["shared"]
        selection_shared = entities["Named Selection"]["shared"]
        structure_shared = entities["PROJECT STRUCTURE"]["shared"]
        self.assertEqual(["CA-R-3@1", "CA-R-5@1"], entities["Scope Unit"]["shared_sources"])
        self.assertEqual("scope_unit_declaration_context", scope_shared[0]["binding"])
        self.assertEqual("scope_unit_declaration_context", project_shared[0]["binding"])
        self.assertEqual(
            "current_scope_unit_declaration",
            scope_shared[0]["binding_context"]["existence_provenance"],
        )
        self.assertEqual(
            {"atom_id": "CA-R-3", "version": 1, "path": "sources/CA-R-3.md"},
            scope_shared[1]["binding_context"]["declaration_source"],
        )
        self.assertEqual(
            "CA-R-4", project_shared[1]["binding_context"]["declaration_source"]["atom_id"],
        )
        self.assertEqual("known_instance_context", projection_shared[0]["binding"])
        self.assertEqual("known_instance_context", selection_shared[0]["binding"])
        self.assertEqual("known_instance_context", structure_shared[0]["binding"])
        self.assertEqual(
            "bounded_named_contract_context",
            selection_shared[0]["binding_context"]["existence_provenance"],
        )
        self.assertEqual(
            ["CA-R-1"], [row["source"]["atom_id"] for row in entities["Scope Unit"]["own"]],
        )
        self.assertNotIn("Scope Unit//CORE_META_MODEL", entities)
        self.assertNotIn("Actor//ANATOLY", entities)
        self.assertEqual(2, graph["coverage"]["coverage_gaps"])
        self.assertEqual(2, graph["coverage"]["outside_model_scope_sources"])
        self.assertEqual(
            {"CA-R-7", "CA-R-15"},
            {row["source"]["atom_id"] for row in graph["coverage_gaps"]},
        )
        self.assertEqual(
            {"CA-R-8", "CA-R-14"},
            {row["source"]["atom_id"] for row in graph["outside_model_scope"]},
        )

    def test_binds_prefixed_namespaces_to_local_targets_without_losing_subject_provenance(self):
        graph = compose_contract_graph([
            carrier("CA-R-1", "ANECHOIC <+ MODEL <+ Node", body("Node declaration.")),
            carrier("CA-R-2", "ANECHOIC <+ MODEL <+ Node.Status", body("Status declaration.")),
            carrier("CA-R-3", "ANECHOIC <+ MODEL <+ Node//Example", body("Example declaration.")),
            carrier("CA-R-4", "ANECHOIC <+ MODEL <+ CFEL <+ Format", body("Format declaration.")),
            carrier("CA-R-5", "ANECHOIC <+ MODEL <+ CFEL <+ Relation//depends_on",
                    body("Relation declaration."), form="Relation Definition"),
            carrier("CA-R-6", "ANECHOIC <+ STRUCTURE <+ Project", body("Project declaration.")),
            carrier("CA-R-7", "ANECHOIC <+ STRUCTURE <+ Project//anechoic",
                    body("Project declaration context."), form="Scope Unit Declaration"),
            carrier("CA-R-8", "ANECHOIC <+ MODEL <+ Node", body("Node rule."), form="Rule"),
            carrier("CA-R-9", "ANECHOIC <+ MODEL <+ CFEL <+ Relation//depends_on",
                    body("Relation rule."), form="Rule"),
            carrier("CA-R-10", "ANECHOIC <+ STRUCTURE <+ Project//anechoic",
                    body("Project rule."), form="Rule"),
            carrier("CA-R-11", "ANECHOIC <+ MODEL <+ Projection", body("Projection declaration.")),
            carrier("CA-R-12", "ANECHOIC <+ MODEL <+ Named Selection", body("Selection declaration.")),
            carrier("CA-R-13", "ANECHOIC <+ MODEL <+ (Node, Node.**)", body("Node scope."), form="Rule"),
            carrier("CA-R-14", "ANECHOIC <+ MODEL <+ (Node, Node.**)", body("Node scope."), form="Rule"),
            carrier("CA-R-15", "ANECHOIC <+ STRUCTURE <+ Projection//PROJECT_SCOPE_UNIT_GRAPH",
                    body("Projection context."), form="Rule"),
            carrier("CA-R-16", "ANECHOIC <+ STRUCTURE <+ Projection//PROJECT_SCOPE_UNIT_GRAPH",
                    body("Projection context."), form="Rule"),
            carrier("CA-R-17", "ANECHOIC <+ STRUCTURE <+ Named Selection//Extension Sources",
                    body("Selection context."), form="Rule"),
        ])

        entities = {row["target"]: row for row in graph["entities"]}
        components = {row["target"]: row for row in graph["components"]}
        relations = {row["target"]: row for row in graph["relations"]}
        self.assertEqual("exact", entities["Node"]["shared"][0]["binding"])
        self.assertEqual("ANECHOIC <+ MODEL <+ Node", entities["Node"]["shared"][0]["subject"])
        self.assertEqual("property", entities["Node.Status"]["kind"])
        self.assertEqual("instance", entities["Node//Example"]["kind"])
        self.assertEqual("component", components["Format"]["kind"])
        self.assertEqual("Project", entities["Project"]["shared"][0]["target"])
        self.assertEqual("scope_unit_declaration_context", entities["Project"]["shared"][0]["binding"])
        self.assertEqual("depends_on", relations["depends_on"]["target"])
        self.assertEqual("ANECHOIC <+ MODEL <+ CFEL <+ Relation//depends_on",
                         relations["depends_on"]["shared"][0]["subject"])
        self.assertEqual(1, len(entities["Node"]["shared"]))
        self.assertEqual(2, len(entities["Projection"]["shared"]))
        self.assertEqual("known_instance_context", entities["Projection"]["shared"][0]["binding"])
        self.assertEqual("known_instance_context", entities["Named Selection"]["shared"][0]["binding"])
        self.assertEqual(2, graph["coverage"]["coverage_gaps"])

    def test_claim_scope_and_details_are_source_bound_context_before_claim(self):
        graph = compose_contract_graph([
            carrier("CA-R-1", "Atom.Status", body("Status declaration.")),
            carrier("CA-R-2", "Atom.Status:Draft", """## Claim Scope

Only Draft Atom instances.

## Claim

Draft status rule.

## Details

Carrier-specific constraint.
""", form="Rule"),
        ])

        rendered = render_contract_graph(graph)
        rule = rendered[rendered.index("CA-R-2@1"):]
        self.assertLess(rule.index("Claim Scope:"), rule.index("Remaining Claim prose:"))
        self.assertIn("Only Draft Atom instances.", rendered)
        self.assertIn("Details (source-bound):", rendered)
        self.assertIn("Carrier-specific constraint.", rendered)

    def test_renders_blank_outside_scope_prose_lines_without_trailing_whitespace(self):
        graph = compose_contract_graph([
            carrier("CA-R-1", "Node", body("Node declaration.")),
            carrier("CA-R-2", "Unknown", body("First outside line.", "", "Second outside line."), form="Rule"),
        ])

        rendered = render_contract_graph(graph)
        self.assertIn("    First outside line.\n\n    Second outside line.", rendered)
        self.assertFalse(any(line.endswith(" ") for line in rendered.splitlines()))
