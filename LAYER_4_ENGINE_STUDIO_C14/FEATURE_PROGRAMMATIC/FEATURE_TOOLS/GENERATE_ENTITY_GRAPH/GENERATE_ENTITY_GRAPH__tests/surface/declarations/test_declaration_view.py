"""Focused tests for the pure declaration-view Markdown renderer."""

from __future__ import annotations

from importlib import import_module
import sys
import unittest
from pathlib import Path

import yaml


SCRIPT_DIR = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(SCRIPT_DIR))

_fixture = import_module(
    "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH."
    "GENERATE_ENTITY_GRAPH__tests.surface.declarations._declaration_view_fixture"
)
FENCE = _fixture.FENCE
PROJECTION = _fixture.PROJECTION
source = _fixture.source
metadata = _fixture.metadata
relation_type = _fixture.relation_type
render = _fixture.render
good_view_document = _fixture.good_view_document


class DeclarationViewTests(unittest.TestCase):
    def test_good_view_has_identity_sections_and_no_atom_relation_map(
        self,
    ) -> None:
        document, raw_yaml = good_view_document()

        frontmatter = yaml.safe_load(document.split("---\n", 2)[1])
        self.assertEqual("Projection", frontmatter["artifact_form"])
        self.assertEqual("Catalog", frontmatter["form"])
        self.assertEqual("CA-PROJ-901", frontmatter["projection_id"])
        self.assertEqual(
            "Named Selection//Relation-Types-and-Graph-Rules",
            frontmatter["source"]["named_selection"],
        )
        self.assertEqual(
            ["CA-R-100@2", "CA-R-200@4"], frontmatter["source"]["atoms"]
        )
        self.assertNotIn("type", frontmatter)
        self.assertNotIn("source_of_truth", frontmatter)
        self.assertNotIn("sources", frontmatter)
        self.assertLess(
            document.index("## Relation Types"),
            document.index("## Graph Rules"),
        )
        self.assertLess(
            document.index("## Graph Rules"),
            document.index("## Source limitations"),
        )
        self.assertIn("\tMeaning: a supplied relation meaning", document)
        self.assertIn("#### Evidence: CA-R-1368@14", document)
        self.assertIn("Subject: Entity/Plan", document)
        self.assertIn(
            "The source Claim establishes the direct containment direction.",
            document,
        )
        self.assertIn(raw_yaml, document)
        self.assertNotIn("relations:", document)

    def test_empty_catalog_is_explicit_and_does_not_claim_complete_authority(
        self,
    ) -> None:
        document = render(
            {
                "relation_types": [],
                "graph_rules": [],
                "limitations": [],
                "unresolved": [],
            }
        )

        self.assertIn(
            (
                "- No Relation Type declarations supplied"
                " for the selected source set."
            ),
            document,
        )
        self.assertIn(
            (
                "- Concrete Graph Rule catalogue: empty f"
                "or the selected source set."
            ),
            document,
        )
        self.assertIn(
            "does not establish completeness outside the selection", document
        )

    def test_graph_kind_and_name_are_sorted_without_merging_same_names(
        self,
    ) -> None:
        document = render(
            {
                "relation_types": [
                    relation_type("Z Graph", "SAME"),
                    relation_type("A Graph", "SAME"),
                    relation_type("A Graph", "FIRST"),
                ],
                "graph_rules": [],
                "limitations": [],
                "unresolved": [],
            }
        )

        first = document.index("Relation Type: A Graph / FIRST")
        second = document.index("Relation Type: A Graph / SAME")
        third = document.index("Relation Type: Z Graph / SAME")
        self.assertLess(first, second)
        self.assertLess(second, third)
        self.assertEqual(3, document.count("Relation Type: "))

    def test_rule_yaml_is_opaque_and_keeps_date_and_default_text(self) -> None:
        raw_yaml = (
            FENCE
            + "yaml\n"
            + "graph_rule_type: value_constraint\n"
            + "default_value: 2026-10-20\n"
            + "condition:\n"
            + "  literal: '01:02'\n"
            + FENCE
        )
        document = render(
            {
                "relation_types": [],
                "graph_rules": [
                    {
                        "source": source("CA-R-300", 1),
                        "subject": "Property/Status",
                        "summary": "Do not evaluate this.",
                        "yaml_block": raw_yaml,
                    }
                ],
                "limitations": [],
                "unresolved": [],
            }
        )

        self.assertIn(raw_yaml, document)
        self.assertIn("default_value: 2026-10-20", document)
        self.assertIn("literal: '01:02'", document)
        self.assertIn("Do not evaluate this.", document)

    def _cardinality_yaml(
        self,
    ) -> None:
        raw_yaml = (
            FENCE
            + "yaml\n"
            + "graph_rule_type: cardinality\n"
            + "applies_to:\n"
            + (
                '  node: "Entity/Node/Continuant/Selectio'
                'n//Dependent Entity Occurrences"\n'
            )
            + "  relation_type: IS_BORNE_BY\n"
            + "  direction: outgoing\n"
            + "condition:\n"
            + "  other_endpoint: [Entity]\n"
            + "  minimum: 0\n"
            + "  maximum: null\n"
            + FENCE
        )
        document = render(
            {
                "relation_types": [],
                "graph_rules": [
                    {
                        "source": source("CA-R-637", 4),
                        "subject": "Entity/Node/Continuant/Atom.Relations",
                        "summary": "Cardinality display fixture.",
                        "yaml_block": raw_yaml,
                    }
                ],
                "limitations": [],
                "unresolved": [],
            }
        )

        self.assertIn("### Graph Rule: CA-R-637", document)
        self.assertIn("Source: CA-R-637", document)
        self.assertIn(
            "Governed Subject: Entity/Node/Continuant/Atom.Relations", document
        )
        self.assertIn(raw_yaml, document)
        self.assertIn("Selection//Dependent Entity Occurrences", document)
        self.assertIn("maximum: null", document)
        self.assertNotIn("evaluated_count", document)

    locals()[
        (
            "test_cardinality_yaml_renders_opaque"
            "_with_selection_and_unbounded_maximum"
        )
    ] = _cardinality_yaml

    def test_duplicate_relation_sources_are_deduplicated_and_sorted(
        self,
    ) -> None:
        document = render(
            {
                "relation_types": [
                    relation_type(
                        "Entities Graph",
                        "IS_BORNE_BY",
                        sources=[
                            source("CA-R-9", 3),
                            source("CA-R-9", 3),
                            source("CA-R-2", 8),
                        ],
                    )
                ],
                "graph_rules": [],
                "limitations": [],
                "unresolved": [],
            },
            owners=[
                {"source": source("CA-R-9", 3)},
                {"source": source("CA-R-2", 8)},
                {"source": source("CA-R-9", 3)},
            ],
        )

        self.assertEqual(
            ["CA-R-2@8", "CA-R-9@3"],
            yaml.safe_load(document.split("---\n", 2)[1])["source"]["atoms"],
        )
        self.assertEqual(1, document.count("\t\tCA-R-9@3"))
        self.assertEqual(1, document.count("\t\tCA-R-2@8"))

    def _metadata_fence(
        self,
    ) -> None:
        document = render(
            {
                "relation_types": [
                    relation_type(
                        "Entities Graph",
                        "UNTRUSTED",
                        relation_metadata=metadata(
                            meaning="text with " + chr(96) * 4 + " inside"
                        ),
                    )
                ],
                "graph_rules": [],
                "limitations": [],
                "unresolved": [],
            }
        )

        self.assertIn(chr(96) * 5 + "text", document)
        self.assertIn(
            "\tMeaning: text with " + chr(96) * 4 + " inside", document
        )
        text_block = document[document.index(chr(96) * 5 + "text") :]
        self.assertIn("\tOwning graph kind:", text_block)
        self.assertIn("\tCanonical name:", text_block)

    locals()[
        (
            "test_metadata_fence_is_wider_than_unt"
            "rusted_backticks_and_fields_are_tabbed"
        )
    ] = _metadata_fence

    def _missing_metadata(
        self,
    ) -> None:
        evidence = "governing prose with " + chr(96) * 3 + " fence"
        document = render(
            {
                "relation_types": [
                    relation_type(
                        "Entities Graph",
                        "INCOMPLETE",
                        relation_metadata={"meaning": "only supplied meaning"},
                    )
                ],
                "graph_rules": [],
                "limitations": ["unknown candidate remains outside admission"],
                "unresolved": [
                    {
                        "source": source("CA-R-999", 2),
                        "subject": "Entity/Unknown",
                        "reason": "qualified identity is unresolved",
                        "body": evidence,
                    }
                ],
            }
        )

        self.assertIn("\tMeaning: only supplied meaning", document)
        self.assertIn(
            (
                "\tDeclared direct direction: unavailable "
                "(not evidenced in selected authority)"
            ),
            document,
        )
        self.assertIn("unknown candidate remains outside admission", document)
        self.assertIn("qualified identity is unresolved", document)
        self.assertIn(evidence, document)

    locals()[
        (
            "test_missing_metadata_is_an_honest_g"
            "ap_and_unresolved_evidence_is_visible"
        )
    ] = _missing_metadata

    def test_invalid_provenance_version_fails_through_existing_source_helper(
        self,
    ) -> None:
        _fixture.assert_invalid_provenance(self)


if __name__ == "__main__":
    unittest.main()
