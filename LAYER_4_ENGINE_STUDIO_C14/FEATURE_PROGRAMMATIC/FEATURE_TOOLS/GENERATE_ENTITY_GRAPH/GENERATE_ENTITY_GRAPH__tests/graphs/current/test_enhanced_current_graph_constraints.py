"""Source-bound graph constraints cases."""

from importlib import import_module
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(TOOL := Path(__file__).resolve().parents[3]))
sys.path.insert(0, str(TOOL.parent))

_graph = import_module(
    "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH."
    "GENERATE_ENTITY_GRAPH__shared"
)
_adapter = import_module(
    "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared"
)
_support = import_module(
    "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH."
    "GENERATE_ENTITY_GRAPH__tests.graphs.current.enhanced_graph_test_support"
)
_cases = import_module(
    "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH."
    "GENERATE_ENTITY_GRAPH__tests.graphs.current._constraint_graph_cases"
)
compose_enhanced_current_graph = _graph.compose_enhanced_current_graph
read_current_model_carriers = _adapter.read_current_model_carriers
render_model = _graph.render_model
carrier = _support.carrier


def grouped_carriers(block):
    return [
        carrier(
            "CA-R-1",
            {"active": "Node", "passive": []},
            declaration=True,
        ),
        carrier(
            "CA-R-2",
            {"active": "Node.Name", "passive": []},
            "## Claim\n```python\n" + block + "```\n",
            declaration=True,
        ),
        carrier(
            "CA-R-3",
            {"active": "Node.Name", "passive": []},
            """## Claim
```python
property_rule(address='Node.Name', value_format='integer', values='1')
```
""",
            declaration=True,
            form="Rule",
        ),
    ]


def separated_carriers():
    return [
        carrier(
            "CA-R-1001",
            {"active": "Node >| Independence", "passive": []},
            declaration=True,
        ),
        carrier(
            "CA-R-1002",
            {"active": "Node.Property: literal", "passive": []},
            (
                "## Claim\n```python\nproperty_rule(address"
                "='Node.Property', value_format='string',"
                " values='1')\nrelation(source='Journal//'"
                ", name='CONTAINS', target='Event Record/"
                "/', source_count='0+')\n```\n"
            ),
            declaration=True,
        ),
        carrier(
            "CA-R-1003",
            {"active": "Workflow//Daily", "passive": []},
            declaration=True,
        ),
        carrier(
            "CA-R-1004",
            {"active": "Node", "passive": []},
            declaration=True,
        ),
        carrier(
            "CA-R-1005",
            {"active": "Node.Property", "passive": []},
            declaration=True,
        ),
    ]


def write_frontier(source_root):
    def write(
        atom_id: str,
        role: str,
        form: str,
        active: str,
        claim: str = "",
    ) -> None:
        (source_root / f"{atom_id}.md").write_text(
            "---\n"
            f"atom_id: {atom_id}\nversion: 1\nstatus: Active\n"
            f"role: {role}\nform: {form}\n"
            f"subjects:\n  active: {active}\n  passive: []\n---\n" + claim,
            encoding="utf-8",
        )

    write("CA-R-9001", "Requirement", "Declaration", "Node")
    write(
        "CA-R-9002",
        "Requirement",
        "Declaration",
        "Projection.Form",
        (
            "## Claim\n```python\nfrom anechoic.formal_"
            "claims import declare_entity\ndeclare_ent"
            "ity(entity_name='Form', relation_name='I"
            "S_PROPERTY_OF', base_path='Projection', "
            "allowed_values=('Catalog', 'Map'), prope"
            "rty_occurrence_cardinality=1, value_card"
            "inality=1, value_format=str)\n```\n"
        ),
    )
    write(
        "CA-R-9003",
        "Requirement",
        "Relation Definition",
        "Entity/CFEL <+ Relation//RUN",
    )
    write("CA-R-9004", "Requirement", "Declaration", "Node/Continuant")
    write("CA-R-9005", "Requirement", "Declaration", "Node/Occurrent")
    write("CA-R-9006", "Requirement", "Rule", "(Node, Node/**, .**)")


class EnhancedCurrentGraphTests(
    _cases.ConstraintGraphCases, unittest.TestCase
):
    def _grouped_constraints(
        self,
    ):
        block = """# model
property_rule(address='Node.Name', value_format='string', values='1')
relation(source='Node', name='CONTAINS', target='Node')
# instances
property_rule(address='Node//$n.Name', value_format='integer', values='1')
relation(source='Node//$n', name='CONTAINS', target='Node//$child')
"""
        graph, _ = compose_enhanced_current_graph(grouped_carriers(block))
        self.assertEqual(
            ["string"],
            [row["value_format"] for row in graph["model_contracts"]],
        )
        self.assertEqual(
            ["integer"],
            [row["value_format"] for row in graph["source_constraints"]],
        )
        self.assertEqual(
            {"property_constraint", "relation_cardinality"},
            {row["kind"] for row in graph["instance_constraints"]},
        )
        self.assertTrue(
            any(
                row.get("relation") == "CONTAINS"
                for row in graph["constraints"]
            )
        )
        self.assertIn(
            block, [row["block"] for row in graph["formal_claim_blocks"]]
        )
        self.assertFalse(
            any(
                "$n" in row["identity"]
                for row in graph["model"]["primary_nodes"]
            )
        )

    locals()[
        (
            "test_grouped_constraints_keep_declarati"
            "on_model_and_instance_evidence_separate"
        )
    ] = _grouped_constraints

    def _separated_model(
        self,
    ) -> None:
        graph, _ = compose_enhanced_current_graph(separated_carriers())
        self.assertEqual("current_atom_model_graph", graph["kind"])
        self.assertEqual(
            {"Node"},
            {row["identity"] for row in graph["model"]["primary_nodes"]},
        )
        self.assertEqual(
            ["Node.Property"],
            [row["identity"] for row in graph["model"]["properties"]],
        )
        self.assertEqual(
            ["Workflow//Daily"],
            [row["identity"] for row in graph["model"]["instances"]],
        )
        self.assertEqual([], graph["model"]["relations"])
        self.assertEqual([], graph["model"]["axes"])
        self.assertEqual([], graph["model"]["allowed_literals"])
        self.assertIn(
            "Node >| Independence",
            [
                row["expression"]
                for row in graph["model"]["selected_subject_expressions"]
            ],
        )
        self.assertEqual(
            {"property_constraint", "relation_cardinality"},
            {row["kind"] for row in graph["constraints"]},
        )
        self.assertEqual([], graph["claim_diagnostics"])

    locals()[
        (
            "test_enhanced_view_separates_nodes_instance"
            "s_relations_classifications_and_constraints"
        )
    ] = _separated_model

    def test_model_renderer_keeps_constraint_and_unsupported_helper_visible(
        self,
    ):
        graph, provenance = compose_enhanced_current_graph(
            [
                carrier(
                    "CA-R-1001",
                    {"active": "Node.Property: literal", "passive": []},
                    """## Claim
```python
property_rule(address='Node.Property', value_format='string', values='1')
deliver(source='Atom//$atom', carrier='Carrier//$carrier')
```
""",
                    declaration=True,
                ),
            ]
        )
        document = render_model(
            graph,
            provenance,
            updated_at="2026-11-01 00:00:00 +0000",
            source_selection="Current Atoms in sources",
            projection_identity={
                "projection_id": "CA-PROJ-901",
                "named_selection": "Current Atoms",
            },
        )
        for heading in (
            "## Model graph",
            "## Primary Nodes",
            "## Properties",
            "## Allowed literals",
            "## Constraints",
            "## Python Formal Claim diagnostics",
        ):
            self.assertIn(heading, document)
        self.assertIn("Node.Property:: [string]{::1}", document)
        self.assertIn("Atom//$atom >> Carrier//$carrier", document)

    def _post_cutover(
        self,
    ) -> None:
        temporary_root = (
            Path.cwd() / ".anechoic_tmp/tests/test_enhanced_current_graph"
        )
        temporary_root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=temporary_root) as temporary:
            root = Path(temporary)
            source_root = root / "current-model"
            source_root.mkdir()

            write_frontier(source_root)

            graph, _ = compose_enhanced_current_graph(
                read_current_model_carriers(source_root, root)
            )

        self.assertEqual(
            ["Node", "Node/Continuant", "Node/Occurrent"],
            [row["identity"] for row in graph["model"]["primary_nodes"]],
        )
        self.assertEqual(
            ["Projection.Form"],
            [row["identity"] for row in graph["model"]["properties"]],
        )
        self.assertEqual(
            ["Relation//RUN"],
            [row["identity"] for row in graph["model"]["relations"]],
        )
        self.assertEqual(
            {"Projection.Form :: Catalog", "Projection.Form :: Map"},
            {
                row["expression"]
                for row in graph["constraints"]
                if row["kind"] == "allowed_literal"
            },
        )
        self.assertNotIn(
            "CA-R-9006",
            [
                row["source"]["atom_id"]
                for row in graph["model"]["selected_subject_expressions"]
            ],
        )

    locals()[
        (
            "test_post_cutover_role_form_frontier_k"
            "eeps_catalogue_and_constraints_separate"
        )
    ] = _post_cutover
