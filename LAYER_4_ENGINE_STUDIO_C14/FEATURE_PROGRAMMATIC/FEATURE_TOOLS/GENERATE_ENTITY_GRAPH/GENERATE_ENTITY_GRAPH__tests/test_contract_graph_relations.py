"""Source-bound graph relations cases."""

from pathlib import Path
import sys
import unittest

TOOL = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(TOOL.parent), str(TOOL)]

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.GENERATE_ENTITY_GRAPH__shared import compose_contract_graph
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.GENERATE_ENTITY_GRAPH__shared import render_contract_graph
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.GENERATE_ENTITY_GRAPH__shared import extract_claim_constraints
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.GENERATE_ENTITY_GRAPH__tests.contract_graph_test_support import carrier, body


class ContractGraphTests(unittest.TestCase):
    def test_minimal_inverse_uses_corroborated_direct_meaning_and_reversed_endpoint_view(self):
        direct = carrier("CA-R-1", "CFEL <+ Relation//DIRECT", body(
            "### Formal Claim", "```CFEL", "$left ((DIRECT)) $right;",
            "Relation//DIRECT ((HAS_INVERSE)) Relation//INVERSE;",
            "Relation//DIRECT ((HAS_CLASSIFICATION)) Derivation == Direct", "```",
            "### Prose Claim", "Direct meaning."))
        inverse = carrier("CA-R-2", "CFEL <+ Relation//INVERSE", body(
            "### Formal Claim", "```CFEL", "Relation//INVERSE <((HAS_INVERSE)) Relation//DIRECT", "```"))
        graph = compose_contract_graph([direct, inverse])
        row = next(row for row in graph["relations"] if row["target"] == "INVERSE")
        self.assertEqual("Derived", row["derived_view"]["classification"])
        self.assertEqual("Direct meaning.", row["derived_view"]["meaning"])
        self.assertEqual([{"host": "$right", "target": "$left"}], row["derived_view"]["endpoints"])
        self.assertEqual([], row["host_target"])
        self.assertEqual(0, graph["coverage"]["missing_relation_semantics"])
        self.assertIn("not new permissions", render_contract_graph(graph))

        missing = compose_contract_graph([inverse])
        self.assertEqual(1, missing["coverage"]["missing_relation_semantics"])
        self.assertNotIn("derived_view", missing["relations"][0])
        conflicting = carrier("CA-R-3", "CFEL <+ Relation//OTHER", body(
            "### Formal Claim", "```CFEL", "Relation//OTHER ((HAS_INVERSE)) Relation//INVERSE;",
            "Relation//OTHER ((HAS_CLASSIFICATION)) Derivation == Direct", "```",
            "### Prose Claim", "Other meaning."))
        ambiguous = compose_contract_graph([direct, inverse, conflicting])
        inverse_row = next(row for row in ambiguous["relations"] if row["target"] == "INVERSE")
        self.assertNotIn("derived_view", inverse_row)

    def test_relation_bounds_and_quoted_counterpart_alias_remain_distinct(self):
        clauses, diagnostics = extract_claim_constraints(carrier("CA-R-1", "Node", body(
            "```CFEL", 'alias(HAS_INVERSE) == "<-->";',
            "Node{:1}((REL)){:2}Node;", "Node:{:1}((REL)){:2}Node;", "```")))
        alias = next(row for row in clauses if row["kind"] == "relation_alias")
        relation = next(row for row in clauses if row["kind"] == "relation_cardinality")
        self.assertEqual("<-->", alias["glyph"])
        self.assertEqual({"minimum": 2, "maximum": 2}, relation["target_cardinality"])
        self.assertEqual(1, len(diagnostics))

    def test_relation_declaration_and_scoped_property_projection(self):
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.GENERATE_ENTITY_GRAPH__shared import build_subject_projection_data

        rows = [carrier("CA-R-1", "Atom", body())]
        for index, role in enumerate(("Method", "Plan"), 2):
            rows.append(carrier(f"CA-R-{index}", f"Atom/(.Header.Context.Role := {role})", body(
                "### Formal Claim", "```python", "from anechoic.formal_claims import declare_entity",
                "from anechoic.model import Atom", f"class {role}(Atom):", "    pass",
                f"declare_entity(entity_class={role}, entity_name='{role}')", "```")))
        rows.append(carrier("CA-R-6", "Atom.Content", body(
            "### Formal Claim", "```python", "from anechoic.formal_claims import declare_entity",
            "declare_entity(entity_name='Content', relation_name='IS_PROPERTY_OF', base_path='Atom',",
            "  recursive_dependent_property_value_format='markdown')", "```")))
        rows.append(carrier("CA-R-4", "Atom.Content.Semantics", body(
            "### Formal Claim", "```python", "from anechoic.formal_claims import declare_entity",
            "from anechoic.model import Method",
            "declare_entity(entity_name='Semantics', relation_name='IS_PROPERTY_OF', base_path='Atom.Content', applies_to_entity_classes=(Method,), value_cardinality=1)",
            "```")))
        rows.append(carrier("CA-R-5", "Relation//CARRIES", body(
            "### Formal Claim", "```python", "from anechoic.formal_claims import declare_relation",
            "declare_relation(relation_name='CARRIES', source_endpoint={'level':'instances'}, target_endpoint={'level':'instances'})",
            "```"), form="Relation Declaration"))
        data = build_subject_projection_data(rows)
        entities = {row["identity"]: row for row in data["entities"]}
        method = entities["Atom/(.Header.Context.Role:=Method)"]
        plan = entities["Atom/(.Header.Context.Role:=Plan)"]
        self.assertIn("Content.Semantics", [row["relative_name"] for row in method["inherited_properties"]])
        semantics = next(row for row in method["inherited_properties"] if row["relative_name"] == "Content.Semantics")
        self.assertEqual("markdown", semantics["effective_value_format"])
        self.assertEqual("CA-R-6", semantics["effective_value_format_sources"][0]["atom_id"])
        self.assertNotIn("Content.Semantics", [row["relative_name"] for row in plan["inherited_properties"]])
        self.assertIn("CARRIES", data["declarations"]["relations"])

    def test_python_order_claim_preserves_graph_relation(self):
        python = carrier("CA-R-1", "Atom", body("```python", "# model",
                         'order_before(first="Atom.A", second="Atom.B")', "```"))
        clauses, diagnostics = extract_claim_constraints(python)
        self.assertEqual([], diagnostics)
        self.assertEqual("IS_ORDERED_RIGHT_BEFORE", clauses[0]["relation"])
        self.assertEqual(("Atom.A", "Atom.B"), (clauses[0]["source_selector"], clauses[0]["target_selector"]))

    def test_operator_symbol_is_bound_to_its_declared_subject(self):
        address = "ANECHOIC_MODEL <+ CFEL <+ Operator//Delivery"
        python = carrier("CA-R-1", address, body("### Formal Claim", "```python", "# model",
                         "set_value(address='Operator//Delivery', value='\">>\"')", "```"))
        clauses, diagnostics = extract_claim_constraints(python)
        self.assertFalse(diagnostics)
        self.assertEqual([(row["kind"], row["operator"], row["symbol"]) for row in clauses],
                         [("operator_symbol", "Delivery", ">>")])
        python["subjects"]["active"] = address.replace("Delivery", "Alias")
        records, issues = extract_claim_constraints(python)
        self.assertFalse(records)
        self.assertEqual(len(issues), 1)
        python["subjects"]["active"] = address
        python["body"] = body("### Formal Claim", "```python", "# model",
                              r'''set_value(address="Operator//Delivery", value='"\\q"')''', "```")
        records, issues = extract_claim_constraints(python)
        self.assertFalse(records)
        self.assertEqual(len(issues), 1)

    def test_unary_relation_counts_keep_source_scope_and_no_target(self):
        graph = compose_contract_graph([
            carrier("CA-R-1", "Node", body("```CFEL", "# model", "(Node, Node.**) {:1}((IS_DECLARED_BY));", "```")),
            carrier("CA-R-2", "Atom", body("```CFEL", "# instances", "Atom//$atom {:0..1}((HAS_ACTIVE_SUBJECT));", "Atom//$atom {:0..1}((GOVERNS));", "```")),
        ])
        node = next(row for row in graph["entities"] if row["target"] == "Node")
        atom = next(row for row in graph["entities"] if row["target"] == "Atom")
        clauses = node["own"][0]["clauses"] + atom["own"][0]["instance_clauses"]
        self.assertEqual(["IS_DECLARED_BY", "HAS_ACTIVE_SUBJECT", "GOVERNS"], [row["relation"] for row in clauses])
        self.assertEqual(["model", "instances", "instances"], [row["group"] for row in clauses])
        self.assertEqual(["(Node, Node.**)", "Atom//$atom", "Atom//$atom"], [row["source_selector"] for row in clauses])
        self.assertEqual([{"minimum": 1, "maximum": 1}, {"minimum": 0, "maximum": 1}, {"minimum": 0, "maximum": 1}],
                         [row["source_cardinality"] for row in clauses])
        self.assertTrue(all(row["target_selector"] is None and row["target_domain"] == "unresolved" and row["written_direction"] == "forward" for row in clauses))
        self.assertEqual([], graph["relations"])
        self.assertEqual({"Node", "Atom"}, {row["target"] for row in graph["entities"]})
        document = render_contract_graph(graph)
        self.assertIn("`(Node, Node.**)` — IS_DECLARED_BY; outgoing count=1; target domain unresolved", document)
        self.assertIn("`Atom//$atom` — HAS_ACTIVE_SUBJECT; outgoing count=0..1; target domain unresolved", document)
        self.assertIn("`Atom//$atom` — GOVERNS; outgoing count=0..1; target domain unresolved", document)
        self.assertNotIn("→ `None`", document)

    def test_qualified_declared_by_derivation_is_not_an_unconditional_inverse(self):
        graph = compose_contract_graph([carrier("CA-R-1", "CFEL <+ Relation//IS_DECLARED_BY", body(
            "### Formal Claim", "```CFEL", "# model",
            "Relation//IS_DECLARED_BY ((IS_DERIVED_RELATION_OF)) Relation//GOVERNS;", "```",
            "### Prose Claim", "Only governing links satisfying the Declaration ownership rule."))])
        relation = graph["relations"][0]
        self.assertEqual(["GOVERNS"], [row["name"] for row in relation["derivation_links"]])
        self.assertEqual([], relation["inverses"])
        self.assertNotIn("derived_view", relation)
        self.assertIn("not structurally interpreted", relation["derivation_scope"])

    def test_instance_group_does_not_supply_relation_classification_or_alias(self):
        graph = compose_contract_graph([carrier("CA-R-1", "CFEL <+ Relation//TEST", body(
            "### Formal Claim", "```CFEL", "# instances",
            "Relation//TEST ((HAS_CLASSIFICATION)) Derivation == Direct;",
            'alias(Relation//TEST) == "/";', "```"))])
        relation = graph["relations"][0]
        self.assertEqual([], relation["metadata"])
        self.assertEqual(2, len(relation["own"][0]["instance_clauses"]))

    def test_relation_metadata_is_case_preserving_and_inverse_is_not_another_declaration(self):
        graph = compose_contract_graph([
            carrier(
                "CA-R-1", "CFEL <+ Relation//depends_on",
                body(
                    "```CFEL", "Step// {:1}((depends_on)){:1} Action//;",
                    "((depends_on)) ((HAS_INVERSE)) ((is_depended_on));",
                    "((depends_on)) ((IS_DERIVED_RELATION_OF)) ((is_depended_on));",
                    "((depends_on)) == <<;", "((depends_on)) >| Derivation == Direct;", "```",
                    semantics="Dependency direction.",
                ),
            ),
        ])

        relation = graph["relations"][0]
        self.assertEqual("depends_on", relation["target"])
        self.assertEqual(["is_depended_on"], [row["name"] for row in relation["inverses"]])
        self.assertEqual(["is_depended_on"], [row["name"] for row in relation["derivation_links"]])
        self.assertEqual({"notation", "derivation"}, {row["kind"] for row in relation["metadata"]})
        self.assertEqual(0, graph["coverage"]["missing_relation_semantics"])
        rendered = render_contract_graph(graph)
        self.assertIn("does not certify an undeclared inverse Relation", rendered)
        self.assertIn("Derivation interpretation gap", rendered)
        self.assertNotIn("((is_depended_on)) — declared Relation", rendered)

    def test_typed_relation_alias_and_inverse_are_source_bound_in_either_direction(self):
        def read(binding):
            return compose_contract_graph([
                carrier("CA-R-1", "CFEL <+ Relation//IS_NARROWER_THAN", body(
                    "### Formal Claim", "```CFEL",
                    'alias(Relation//IS_NARROWER_THAN) == "/";',
                    binding,
                    "Node ((IS_NARROWER_THAN)) Node;", "```")),
            ])["relations"][0]

        forward = read("Relation//IS_NARROWER_THAN ((HAS_INVERSE)) Relation//BROADER_THAN;")
        reverse = read("Relation//BROADER_THAN <((HAS_INVERSE)) Relation//IS_NARROWER_THAN;")
        glyph = read("Relation//IS_NARROWER_THAN <--> Relation//BROADER_THAN;")
        self.assertEqual(["BROADER_THAN"], [row["name"] for row in forward["inverses"]])
        self.assertEqual(forward["inverses"], reverse["inverses"])
        self.assertEqual(forward["inverses"], glyph["inverses"])
        self.assertEqual(["/"], [row["value"] for row in forward["metadata"]])
        self.assertEqual(["Node"], [row["source_selector"] for row in forward["host_target"]])
        self.assertEqual(1, len(forward["host_target"]))

        graph = compose_contract_graph([carrier("CA-R-2", "CFEL <+ Relation//CONTAINS", body(
            "### Formal Claim", "```CFEL", 'alias(Relation//CONTAINS) == "<+";', "```"))])
        self.assertEqual([], graph["entities"])
        self.assertEqual([], graph["relations"][0]["host_target"])
        self.assertEqual("<+", graph["relations"][0]["metadata"][0]["value"])

    def test_declared_derived_relation_keeps_its_own_metadata(self):
        graph = compose_contract_graph([
            carrier(
                "CA-R-1", "CFEL <+ Relation//is_depended_on",
                body("### Formal Claim", "```python", "from anechoic.formal_claims import declare_relation",
                     "declare_relation(relation_name='is_depended_on', derived_from='depends_on',",
                     "  source_endpoint={'level': 'instances'}, target_endpoint={'level': 'instances'})",
                     "```", semantics="Reverse dependency."),
            ),
        ])

        relation = graph["relations"][0]
        self.assertEqual("is_depended_on", relation["target"])
        self.assertEqual(["Derived"], [row["value"] for row in relation["metadata"]])
        self.assertIn("`((is_depended_on))` — declared Relation", render_contract_graph(graph))

    def test_duplicate_declaration_and_missing_relation_semantics_are_coverage_failures(self):
        graph = compose_contract_graph([
            carrier("CA-R-1", "Node", body("One.")),
            carrier("CA-R-2", "Node", body("Two.")),
            carrier("CA-R-3", "CFEL <+ Relation//RUN", body(
                "### Formal Claim", "```python", "from anechoic.formal_claims import declare_relation",
                "declare_relation(relation_name='RUN', written_alias='>>')", "```")),
        ])

        self.assertEqual(1, graph["coverage"]["duplicate_declarations"])
        self.assertEqual(1, graph["coverage"]["missing_relation_semantics"])
        self.assertEqual("incomplete", graph["outcome"])

    def test_relation_metadata_reads_structured_python_helper(self):
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.contract_graph_relations import _metadata
        source = {"atom_id": "CA-R-1"}
        entry = {"clauses": [], "cfel_blocks": [], "python_blocks": [{"source": source, "block": (
            "# model\nclassify(address='Relation//RUNS', axis='Derivation', value='Direct', notation='relation')\n"
            "# instances\nclassify(address='Relation//RUNS', axis='Derivation', value='Derived', notation='relation')\n"
        )}]}
        self.assertEqual(_metadata([entry], "RUNS"), [{"kind": "derivation", "value": "Direct", "source": source}])
