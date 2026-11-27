"""Source-bound graph evidence cases."""

from importlib import import_module
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(TOOL := Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(TOOL.parent))

_graph = import_module(
    "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH."
    "GENERATE_ENTITY_GRAPH__shared"
)
_support = import_module(
    "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH."
    "GENERATE_ENTITY_GRAPH__tests.contract_graph_test_support"
)
_cases = import_module(
    "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH."
    "GENERATE_ENTITY_GRAPH__tests._contract_evidence_cases"
)
compose_contract_graph = _graph.compose_contract_graph
render_contract_graph = _graph.render_contract_graph
extract_claim_constraints = _graph.extract_claim_constraints
build_subject_projection_data = _graph.build_subject_projection_data
render_primary_projection = _graph.render_primary_projection
carrier, body = _support.carrier, _support.body


def grouped_claim_carriers():
    return [
        carrier("CA-R-1", "Atom", body("Atom.")),
        carrier(
            "CA-R-2",
            "Atom.Header.Name",
            body(
                "### Formal Claim",
                "```python",
                "# model",
                (
                    "property_rule(address='Atom.Header.Name'"
                    ", value_format='string', values='1')"
                ),
                "# a full-line comment",
                "# instances",
                (
                    "property_rule(address='Atom//$atom.Heade"
                    "r.Name', value_format='string', values='"
                    "1')"
                ),
                "```",
            ),
        ),
    ]


class ContractGraphTests(_cases.ContractEvidenceCases, unittest.TestCase):
    def _named_claim_children(
        self,
    ):
        graph = compose_contract_graph(
            [
                carrier(
                    "CA-R-1",
                    "Atom",
                    """## Claim

### Formal Claim

```python
property_rule(address='Atom.Header', value_format='YAML', values='1')
```

### Prose Claim

#### Context

Prose with an example:

```python
property_rule(address='Atom.Example', value_format='wrong', values='1')
```
""",
                ),
            ]
        )
        entry = graph["entities"][0]["own"][0]
        self.assertEqual(
            ["Atom.Header"],
            [row["property_selector"] for row in entry["clauses"]],
        )
        self.assertIn("#### Context", entry["prose"])
        self.assertIn("Atom.Example", entry["prose"])
        self.assertEqual(1, len(entry["python_blocks"]))

    locals()[
        (
            "test_named_claim_children_keep_prose_m"
            "arkdown_and_only_extract_formal_python"
        )
    ] = _named_claim_children

    def test_retired_claim_fence_is_only_authored_evidence(self):
        source = carrier(
            "CA-R-1",
            "Node",
            body("```CFEL", "Node.Name: [string]{:1};", "```"),
        )

        self.assertEqual(([], []), extract_claim_constraints(source))
        entry = compose_contract_graph([source])["entities"][0]["own"][0]
        self.assertEqual("CFEL", entry["blocks"][0]["label"])
        self.assertEqual([], entry["clauses"])
        self.assertEqual([], entry["diagnostics"])

    def test_prose_claim_keeps_unrecognized_headings_at_any_level(self):
        graph = compose_contract_graph(
            [
                carrier(
                    "CA-R-1",
                    "Atom",
                    """## Claim
### Prose Claim
Opening.
### Sibling Title
Sibling text.
## Dependent Selection
More text.
```text
Atom.Example
```
## Expression Lists
Last text.
## Details
Actual root detail.
""",
                )
            ]
        )
        entry = graph["entities"][0]["own"][0]
        self.assertIn("### Sibling Title\nSibling text.", entry["prose"])
        self.assertIn("## Dependent Selection\nMore text.", entry["prose"])
        self.assertIn("Atom.Example", entry["prose"])
        self.assertIn("## Expression Lists\nLast text.", entry["prose"])
        self.assertNotIn("Actual root detail", entry["prose"])
        self.assertEqual([], entry["diagnostics"])
        self.assertEqual([], entry["clauses"])

    def test_python_model_claim_retains_authored_source(self):
        raw = (
            '# model\nproperty_rule(address="Atom.Name'
            '", value_format="string", values="1")\n'
        )
        python = carrier(
            "CA-R-2", "Atom.Name", body("```python", raw.rstrip(), "```")
        )
        clauses, diagnostics = extract_claim_constraints(python)
        self.assertEqual([], diagnostics)
        self.assertEqual("Atom.Name", clauses[0]["property_selector"])
        self.assertEqual("string", clauses[0]["value_format"])
        self.assertEqual(
            {"minimum": 1, "maximum": 1}, clauses[0]["value_cardinality"]
        )
        graph = compose_contract_graph([python])
        entries = [entry for row in graph["entities"] for entry in row["own"]]
        entry = next(
            entry
            for entry in entries
            if entry["source"]["atom_id"] == "CA-R-2"
        )
        self.assertEqual(raw, entry["python_blocks"][0]["block"])
        self.assertEqual("python", entry["python_blocks"][0]["label"])
        projection = build_subject_projection_data(
            [carrier("CA-R-1", "Atom", body("Atom declaration.")), python]
        )
        self.assertIn(
            "```python\n" + raw + "```",
            render_primary_projection(projection, 4),
        )

    def _invalid_python_claim(
        self,
    ):
        bad = carrier(
            "CA-R-1",
            "Atom",
            body("### Formal Claim", "```python", "execute()", "```"),
        )
        _, diagnostics = extract_claim_constraints(bad)
        self.assertEqual("python-formal-claim-invalid", diagnostics[0]["code"])
        with self.assertRaisesRegex(ValueError, "CA-R-1@"):
            compose_contract_graph([bad])
        prose = carrier(
            "CA-R-2",
            "Atom",
            body("### Prose Claim", "```python", "execute()", "```"),
        )
        workflow = carrier(
            "CA-O-1",
            "Atom",
            body("### Formal Claim", "```python", "execute()", "```"),
            role="Operations",
        )
        self.assertEqual(([], []), extract_claim_constraints(prose))
        self.assertEqual(([], []), extract_claim_constraints(workflow))

    locals()[
        (
            "test_python_claim_invalid_is_diagnostic_"
            "and_prose_and_operations_are_not_executed"
        )
    ] = _invalid_python_claim

    def _grouped_formal_claims(
        self,
    ):
        graph = compose_contract_graph(grouped_claim_carriers())
        row = next(
            row
            for row in graph["entities"]
            if row["target"] == "Atom.Header.Name"
        )
        entry = row["own"][0]
        self.assertEqual(["model"], [x["group"] for x in entry["clauses"]])
        self.assertEqual(
            ["property_constraint"],
            [x["kind"] for x in entry["instance_clauses"]],
        )
        self.assertEqual(
            "Atom//$atom.Header.Name",
            entry["instance_clauses"][0]["property_selector"],
        )
        self.assertEqual([], entry["diagnostics"])
        self.assertIn("# instances", entry["python_blocks"][0]["block"])
        self.assertFalse(
            any("$atom" in x["target"] for x in graph["entities"])
        )
        self.assertIn("Instance constraints:", render_contract_graph(graph))

    locals()[
        (
            "test_grouped_formal_claims_keep_inst"
            "ance_variables_out_of_model_contracts"
        )
    ] = _grouped_formal_claims

    def test_unsupported_helper_is_partial_extraction_without_a_display_gap(
        self,
    ):
        graph = compose_contract_graph(
            [
                carrier(
                    "CA-R-1",
                    "Node",
                    body(
                        "```python",
                        (
                            "deliver(source='Atom//$atom', carrier='C"
                            "arrier//$carrier')"
                        ),
                        "```",
                    ),
                ),
            ]
        )

        self.assertEqual("complete", graph["display_coverage"])
        self.assertEqual("partial", graph["structured_claims"])
        self.assertEqual("complete", graph["outcome"])
        self.assertIn(
            "Atom//$atom >> Carrier//$carrier", render_contract_graph(graph)
        )

    def test_preserves_unlabelled_claim_blocks_and_reports_unbound_source(
        self,
    ):
        graph = compose_contract_graph(
            [
                carrier("CA-R-1", "Node", body("Node declaration.")),
                carrier(
                    "CA-R-2",
                    "Node/Missing",
                    body(
                        "Legacy formal evidence:",
                        "```",
                        "Node/Missing: [string]{:1}",
                        "```",
                    ),
                    form="Rule",
                ),
            ]
        )

        gap = graph["coverage_gaps"][0]
        self.assertEqual("", gap["blocks"][0]["label"])
        self.assertIn("Node/Missing", gap["blocks"][0]["block"])
        rendered = render_contract_graph(graph)
        self.assertIn("Unbound source evidence", rendered)
        self.assertIn("```\nNode/Missing", rendered)
