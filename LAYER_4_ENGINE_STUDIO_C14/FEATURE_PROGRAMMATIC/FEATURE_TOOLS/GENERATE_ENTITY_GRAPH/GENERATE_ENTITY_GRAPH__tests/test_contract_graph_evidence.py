"""Source-bound graph evidence cases."""

from pathlib import Path
import sys
import unittest

TOOL = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(TOOL.parent), str(TOOL)]

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.GENERATE_ENTITY_GRAPH__shared import compose_contract_graph
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.GENERATE_ENTITY_GRAPH__shared import render_contract_graph
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.GENERATE_ENTITY_GRAPH__shared import extract_claim_constraints
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.GENERATE_ENTITY_GRAPH__shared import build_subject_projection_data, render_primary_projection
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.GENERATE_ENTITY_GRAPH__tests.contract_graph_test_support import carrier, body


class ContractGraphTests(unittest.TestCase):
    def test_named_claim_children_keep_prose_markdown_and_only_extract_formal_cfel(self):
        graph = compose_contract_graph([
            carrier("CA-R-1", "Atom", """## Claim

### Formal Claim

```CFEL
Atom.Header: [YAML]{:1};
```

### Prose Claim

#### Context

Prose with an example:

```CFEL
Atom.Example: [wrong]{:1};
```
"""),
        ])
        entry = graph["entities"][0]["own"][0]
        self.assertEqual(["Atom.Header"], [row["property_selector"] for row in entry["clauses"]])
        self.assertIn("#### Context", entry["prose"])
        self.assertIn("Atom.Example", entry["prose"])
        self.assertEqual(1, len(entry["cfel_blocks"]))

    def test_prose_only_claim_does_not_interpret_cfel_examples(self):
        graph = compose_contract_graph([
            carrier("CA-R-1", "Atom", """## Claim

### Prose Claim

```CFEL
Atom.Example: [wrong]{:1};
```
"""),
        ])
        entry = graph["entities"][0]["own"][0]
        self.assertEqual([], entry["clauses"])
        self.assertEqual([], entry["cfel_blocks"])
        self.assertEqual([], entry["diagnostics"])
        self.assertIn("Atom.Example", entry["prose"])

    def test_prose_claim_keeps_unrecognized_headings_at_any_level(self):
        graph = compose_contract_graph([carrier("CA-R-1", "Atom", """## Claim
### Prose Claim
Opening.
### Sibling Title
Sibling text.
## Dependent Selection
More text.
```CFEL
Atom.Example: [wrong]{:1};
```
## Expression Lists
Last text.
## Details
Actual root detail.
""")])
        entry = graph["entities"][0]["own"][0]
        self.assertIn("### Sibling Title\nSibling text.", entry["prose"])
        self.assertIn("## Dependent Selection\nMore text.", entry["prose"])
        self.assertIn("Atom.Example", entry["prose"])
        self.assertIn("## Expression Lists\nLast text.", entry["prose"])
        self.assertNotIn("Actual root detail", entry["prose"])
        self.assertEqual([], entry["diagnostics"])
        self.assertEqual([], entry["clauses"])

    def test_python_model_claim_retains_authored_source(self):
        raw = '# model\nproperty_rule(address="Atom.Name", value_format="string", values="1")\n'
        python = carrier("CA-R-2", "Atom.Name", body("```python", raw.rstrip(), "```"))
        clauses, diagnostics = extract_claim_constraints(python)
        self.assertEqual([], diagnostics)
        self.assertEqual("Atom.Name", clauses[0]["property_selector"])
        self.assertEqual("string", clauses[0]["value_format"])
        self.assertEqual({"minimum": 1, "maximum": 1}, clauses[0]["value_cardinality"])
        graph = compose_contract_graph([python])
        entries = [entry for row in graph["entities"] for entry in row["own"]]
        entry = next(entry for entry in entries if entry["source"]["atom_id"] == "CA-R-2")
        self.assertEqual(raw, entry["python_blocks"][0]["block"])
        self.assertEqual("python", entry["python_blocks"][0]["label"])
        projection = build_subject_projection_data([carrier("CA-R-1", "Atom", body("Atom declaration.")), python])
        self.assertIn("```python\n" + raw + "```", render_primary_projection(projection, 4))

    def test_python_claim_invalid_is_diagnostic_and_prose_and_operations_are_not_executed(self):
        bad = carrier("CA-R-1", "Atom", body("### Formal Claim", "```python", "execute()", "```"))
        _, diagnostics = extract_claim_constraints(bad)
        self.assertEqual("python-formal-claim-invalid", diagnostics[0]["code"])
        with self.assertRaisesRegex(ValueError, "CA-R-1@"):
            compose_contract_graph([bad])
        prose = carrier("CA-R-2", "Atom", body("### Prose Claim", "```python", "execute()", "```"))
        workflow = carrier("CA-O-1", "Atom", body("### Formal Claim", "```python", "execute()", "```"), role="Operations")
        self.assertEqual(([], []), extract_claim_constraints(prose))
        self.assertEqual(([], []), extract_claim_constraints(workflow))

    def test_grouped_formal_claims_keep_instance_variables_out_of_model_contracts(self):
        graph = compose_contract_graph([
            carrier("CA-R-1", "Atom", body("Atom.")),
            carrier("CA-R-2", "Atom.Header.Name", body(
                "### Formal Claim", "```CFEL", "# model",
                "Atom.Header.Name: [string]{:1};", 'alias(Relation//CONTAINS) == "# instances";',
                "# a full-line comment", "# instances", "Atom//$atom;", "$atom.Header.Name: [string]{:1};", "```")),
        ])
        row = next(row for row in graph["entities"] if row["target"] == "Atom.Header.Name")
        entry = row["own"][0]
        self.assertEqual(["model", "model"], [x["group"] for x in entry["clauses"]])
        self.assertEqual(["instance_binding", "property_constraint"], [x["kind"] for x in entry["instance_clauses"]])
        self.assertEqual("$atom.Header.Name", entry["instance_clauses"][1]["property_selector"])
        self.assertEqual("# instances", entry["clauses"][1]["glyph"])
        self.assertEqual([], entry["diagnostics"])
        self.assertIn("# instances", entry["cfel_blocks"][0]["block"])
        self.assertFalse(any("$atom" in x["target"] for x in graph["entities"]))
        self.assertIn("Instance constraints:", render_contract_graph(graph))

    def test_preserved_unsupported_cfel_is_partial_extraction_not_a_display_gap(self):
        graph = compose_contract_graph([
            carrier("CA-R-1", "Node", body("```CFEL", "IF Node THEN Property", "```")),
        ])

        self.assertEqual("complete", graph["display_coverage"])
        self.assertEqual("partial", graph["structured_cfel"])
        self.assertEqual("complete", graph["outcome"])
        self.assertIn("IF Node THEN Property", render_contract_graph(graph))

    def test_preserves_unlabelled_claim_blocks_and_reports_unbound_source(self):
        graph = compose_contract_graph([
            carrier("CA-R-1", "Node", body("Node declaration.")),
            carrier("CA-R-2", "Node/Missing", body("Legacy formal evidence:", "```", "Node/Missing: [string]{:1}", "```"), form="Rule"),
        ])

        gap = graph["coverage_gaps"][0]
        self.assertEqual("", gap["blocks"][0]["label"])
        self.assertIn("Node/Missing", gap["blocks"][0]["block"])
        rendered = render_contract_graph(graph)
        self.assertIn("Unbound source evidence", rendered)
        self.assertIn("```\nNode/Missing", rendered)

    def test_content_recursion_is_general_and_ordering_is_rmed_only(self):
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.GENERATE_ENTITY_GRAPH__shared import build_subject_projection_data

        roles = ("Requirement", "Method", "Evaluation", "Delivery")
        atom = carrier("CA-R-1", "Atom", body())
        role_rows = [carrier(f"CA-R-{index}", f"Atom/(.Header.Context.Role:={name})", body(
            "### Formal Claim", "```python", "from anechoic.formal_claims import declare_entity",
            "from anechoic.model import Atom", f"class {name}(Atom):", "    pass",
            f"declare_entity(entity_class={name}, entity_name='{name}', qualification_property_path='Atom.Header.Context.Role')", "```"))
            for index, name in enumerate((*roles, "Analysis"), start=2)]
        native = body("### Formal Claim", "```python", "from anechoic.formal_claims import Cardinality, declare_entity",
                      "from anechoic.model import Requirement, Method, Evaluation, Delivery",
                      "declare_entity(entity_name='Content', relation_name='IS_PROPERTY_OF', base_path='Atom',",
                      "  property_occurrence_cardinality=1, value_cardinality=0,",
                      "  dependent_property_cardinality=Cardinality(minimum=0, maximum=None), dependent_property_name_format=str,",
                      "  recursive_dependent_property_cardinality=Cardinality(minimum=0, maximum=None),",
                      "  recursive_dependent_property_name_format=str, recursive_dependent_property_value_format='markdown',",
                      "  ordered_dependent_property_roles=(Requirement, Method, Evaluation, Delivery),",
                      "  ordered_dependent_property_pairs=(('Summary', 'Claim'), ('Claim', 'Semantics'), ('Semantics', 'Details')))",
                      "```")
        extra = carrier("CA-R-8", "Atom.Content.Extra.Nested", body())
        projection = build_subject_projection_data([atom, *role_rows, carrier("CA-R-7", "Atom.Content", native), extra])
        entries = projection["declarations"]["properties"]["Atom.Content"]
        self.assertFalse(entries[0]["diagnostics"])
        for name in (*roles, "Analysis"):
            entity = next(row for row in projection["entities"] if row["identity"].endswith(f":={name})"))
            props = {item["identity"]: item for item in entity["inherited_properties"]}
            self.assertEqual("markdown", props["Atom.Content.Extra.Nested"]["effective_value_format"])
            contracts = props["Atom.Content"]["contracts"]
            self.assertTrue(any(c.get("selection") == "recursive_dependents" for c in contracts))
            pairs = [(c["source_selector"].rsplit(".", 1)[1], c["target_selector"].rsplit(".", 1)[1])
                     for c in contracts if c.get("relation") == "IS_ORDERED_RIGHT_BEFORE"]
            self.assertEqual([("Summary", "Claim"), ("Claim", "Semantics"), ("Semantics", "Details")]
                             if name in roles else [], pairs)
