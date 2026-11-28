"""Focused checks for the first four source-bound primary views."""

from pathlib import Path
import sys
import unittest


from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.GENERATE_ENTITY_GRAPH__tests.subjects.views._subject_projection_view_fixtures import (
    _additional_carriers as _additional_carriers,
    _base_carriers as _base_carriers,
    carrier as carrier,
    carriers as carriers,
    claim as claim,
    native_property as native_property,
    projection as projection,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.GENERATE_ENTITY_GRAPH__tests.subjects.views._subject_projection_view_cases import (
    SubjectProjectionViewCases,
)

TOOL = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(TOOL.parent), str(TOOL)]

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.\
    GENERATE_ENTITY_GRAPH__shared import (  # noqa: E402
        build_subject_projection_data,
    )  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.\
    GENERATE_ENTITY_GRAPH__shared import (  # noqa: E402
        subject_projection_views as views,
    )  # fmt: skip


class SubjectProjectionViewTests(
    SubjectProjectionViewCases, unittest.TestCase
):
    def test_conflicting_local_and_recursive_formats_are_diagnostic(self):
        data = build_subject_projection_data(
            [
                carrier("CA-R-1", "Node", claim("Node.")),
                carrier(
                    "CA-R-2",
                    "Node.Section",
                    native_property(
                        "Section",
                        "Node",
                        "recursive_dependent_property_car"
                        "dinality=Cardinality(minimum=0, "
                        "maximum=None)",
                        "recursive_dependent_property_value_format='markdown'",
                    ),
                ),
                carrier(
                    "CA-R-3",
                    "Node.Section.Summary",
                    native_property(
                        "Summary",
                        "Node.Section",
                        "value_format=int",
                        "value_cardinality=Cardinality(minimum=0, maximum=1)",
                    ),
                ),
            ]
        )
        document = views.render_primary_projection(data, 3)
        self.assertNotIn("effective value format:", document)
        self.assertIn(
            "Conflicting applicable value formats for Node.Section.Summary",
            document,
        )
        self.assertIn("CA-R-2@1, CA-R-3@1", document)

    def test_level_three_shows_effective_occurrence_and_value_counts(self):
        data = build_subject_projection_data(
            [
                carrier("CA-R-1", "Node", claim("Node.")),
                carrier(
                    "CA-R-2",
                    "Node.Name",
                    claim(
                        "```python",
                        "from anechoic.formal_claims impo"
                        "rt declare_entity, Cardinality",
                        "declare_entity(entity_name='Name"
                        "', relation_name='IS_PROPERTY_OF"
                        "', base_path='Node', property_oc"
                        "currence_cardinality=Cardinality"
                        "(minimum=0, maximum=1), value_fo"
                        "rmat='string', value_cardinality"
                        "=Cardinality(minimum=0, maximum="
                        "1))",
                        "```",
                    ),
                ),
            ]
        )
        document = views.render_primary_projection(data, 3)
        self.assertIn("occurrence cardinality: `0..1`", document)
        self.assertIn("effective occurrence cardinality: `0..1`", document)
        self.assertIn("value cardinality: `0..1`", document)

    def test_explicit_new_namespace_roots_render_without_invented_parent(self):
        data = projection()
        data["namespaces"] = [
            {
                "subject": "ANECHOIC_MODEL",
                "source": {"atom_id": "CA-R-1", "version": 1},
            },
            {
                "subject": "ANECHOIC_STRUCTURE <+ Project",
                "source": {"atom_id": "CA-R-2", "version": 1},
            },
        ]
        document = views.render_primary_projection(data, 1)
        self.assertIn("\nANECHOIC_MODEL\n", document)
        self.assertIn("\nANECHOIC_STRUCTURE\n  <+ Project", document)
        self.assertNotIn("\nANECHOIC\n", document)

    def test_level_one_keeps_primary_tree_and_source_backed_namespace(self):
        document = views.render_primary_projection(
            projection(namespace=True), 1
        )
        self.assertIn("NARROWER_THAN: `/`", document)
        self.assertIn("Node", document)
        self.assertIn("\t/ Child", document)
        self.assertIn("## Namespace context", document)
        self.assertIn("<+ MODEL [CA-R-NS@1]", document)
        self.assertNotIn("Node.Status", document)

    def test_level_two_lists_direct_properties_only(self):
        document = views.render_primary_projection(projection(), 2)
        self.assertIn("## Direct properties", document)
        self.assertIn("property: `Node/Child.Status`", document)
        self.assertNotIn("[inherited]", document)
        child_section = document.split("### `Node/Child`", 1)[1]
        self.assertNotIn("property: `Node.Status`", child_section)

    def test_namespace_context_is_not_invented_without_source_evidence(self):
        document = views.render_primary_projection(projection(), 1)
        self.assertNotIn("## Namespace context", document)

    def test_level_three_keeps_inherited_origin_and_all_constraint_channels(
        self,
    ):
        document = views.render_primary_projection(projection(), 3)
        self.assertIn("## Effective properties", document)
        self.assertIn(
            "property: `Node.Status` (relative `Status`) [inherited]", document
        )
        self.assertIn("origin: `Node`", document)
        self.assertIn(
            "property_occurrence_cardinality="
            "Cardinality(minimum=0, maximum=1"
            ")",
            document,
        )
        self.assertIn("nesting: `property`", document)
        self.assertIn("occurrence cardinality: `0..1`", document)
        self.assertIn("value format: `integer`", document)
        self.assertIn("value cardinality: `2`", document)
        self.assertIn("CA-R-CHILD-STATUS@1", document)
        self.assertIn("CA-R-STATUS@1", document)

    def test_level_four_copies_formal_claim_blocks_verbatim_without_prose(
        self,
    ):
        document = views.render_primary_projection(projection(), 4)
        self.assertIn("## Primary Declaration Formal Claims", document)
        self.assertIn(
            "value_cardinality=Cardinality(minimum=1, maximum=None)", document
        )
        self.assertIn(
            "value_format='integer', value_cardinality=2)\n```", document
        )
        self.assertIn("ancestor Declaration `Node`", document)
        self.assertIn("Property Declaration Formal Claim", document)
        self.assertNotIn("Child declaration.", document)
        self.assertNotIn("Semantics", document)
        self.assertNotIn("Details", document)

    def test_non_declaration_source_is_not_rendered(self):
        document = views.render_primary_projection(projection(), 4)
        self.assertNotIn("Poison", document)
        self.assertNotIn("CA-M-POISON", document)

    def test_invalid_level_is_rejected(self):
        with self.assertRaises(ValueError):
            views.render_primary_projection(projection(), 5)


if __name__ == "__main__":
    unittest.main()
