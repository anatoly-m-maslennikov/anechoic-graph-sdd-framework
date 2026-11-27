"""Current-source ``//`` instance paths remain typed and non-authoritative."""

from __future__ import annotations

from importlib import import_module
from pathlib import Path
import sys
import unittest


sys.path.insert(0, str(TOOL := Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(TOOL.parent))

_fixture = import_module(
    "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH."
    "GENERATE_ENTITY_GRAPH__tests._instance_graph_fixture"
)
_adapter = import_module(
    "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared"
)
_cases = import_module(
    "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH."
    "GENERATE_ENTITY_GRAPH__tests._instance_graph_cases"
)
compose_current_graph = _fixture.compose_current_graph
source, graph_for = _fixture.source, _fixture.graph_for
_subject_GrammarPin = _adapter.GrammarPin
_subject_SubjectNotationError = _adapter.SubjectNotationError
_subject_get_profile = _adapter.get_profile
_subject_parse_subject_expression = _adapter.parse_subject_expression
_subject_profile_evidence = _adapter.profile_evidence
_subject_render_subject = _adapter.render_subject


class CurrentInstanceGraphTests(_cases.InstanceGraphCases, unittest.TestCase):
    def assert_graph_path(self, graph, expected):
        names = {row["id"]: row["identity"] for row in graph["nodes"]}
        self.assertEqual(
            [name for name, _, _ in expected], list(names.values())
        )
        self.assertEqual(
            {
                (name, parent, kind)
                for name, parent, kind in expected
                if parent is not None
            },
            {
                (
                    names[row["relation_source"]],
                    names[row["relation_target"]],
                    row["kind"],
                )
                for row in graph["edges"]
            },
        )

    def test_approved_grammar_uses_current_evaluation_and_legacy_stays_pinned(
        self,
    ) -> None:
        approved = _subject_get_profile("approved").grammar_pins
        self.assertEqual("CA-E-833", approved[-1].atom_id)
        self.assertTrue(
            approved[-1].path.endswith(
                (
                    "CA-E-833-CORE_META_MODEL-EVAL_POLICY--validate-entity-"
                    "and-topic-r"
                    "eference-expressions.md"
                )
            )
        )
        legacy = _subject_get_profile("legacy").grammar_pins
        self.assertEqual(
            ("CA-E-383", 13), (legacy[-1].atom_id, legacy[-1].version)
        )
        observed = tuple(
            _subject_GrammarPin(item.atom_id, 1, item.path, "a" * 64)
            for item in approved
        )
        self.assertEqual(
            "CA-E-833",
            _subject_profile_evidence("approved", grammar_pins=observed)[
                "grammar_pins"
            ][-1]["atom_id"],
        )
        wrong = (
            *observed[:-1],
            _subject_GrammarPin("CA-E-383", 46, observed[-1].path, "a" * 64),
        )
        with self.assertRaises(_subject_SubjectNotationError):
            _subject_profile_evidence("approved", grammar_pins=wrong)

    def test_instance_path_preserves_full_prefix_and_direction(self) -> None:
        subject = "Entity/Workflow//Daily.Status:Active"
        graph, provenance = graph_for(subject)
        self.assert_graph_path(
            graph,
            [
                ("Entity", None, None),
                ("Entity/Workflow", "Entity", "NARROWER_THAN"),
                ("Entity/Workflow//Daily", "Entity/Workflow", "INSTANCE_OF"),
                (
                    "Entity/Workflow//Daily.Status",
                    "Entity/Workflow//Daily",
                    "IS_PROPERTY_OF",
                ),
                (
                    "Entity/Workflow//Daily.Status:Active",
                    "Entity/Workflow//Daily.Status",
                    "IS_ALLOWED_VALUE_OF",
                ),
            ],
        )
        self.assertEqual("not_performed", graph["native_admission"])
        self.assertEqual(
            "Entity/Workflow//Daily.Status:Active",
            provenance["occurrences"][0]["subject"],
        )

    def test_value_and_instance_steps_remain_distinct(self) -> None:
        graph, _ = graph_for("Entity/Type:Workflow//Daily")
        self.assert_graph_path(
            graph,
            [
                ("Entity", None, None),
                ("Entity/Type", "Entity", "NARROWER_THAN"),
                ("Entity/Type:Workflow", "Entity/Type", "IS_ALLOWED_VALUE_OF"),
                (
                    "Entity/Type:Workflow//Daily",
                    "Entity/Type:Workflow",
                    "INSTANCE_OF",
                ),
            ],
        )

    def test_old_operators_keep_their_existing_kinds(self) -> None:
        graph, _ = graph_for("Entity/Property.Status:Active")
        self.assert_graph_path(
            graph,
            [
                ("Entity", None, None),
                ("Entity/Property", "Entity", "NARROWER_THAN"),
                (
                    "Entity/Property.Status",
                    "Entity/Property",
                    "IS_PROPERTY_OF",
                ),
                (
                    "Entity/Property.Status:Active",
                    "Entity/Property.Status",
                    "IS_ALLOWED_VALUE_OF",
                ),
            ],
        )

    def test_containment_directions_and_counts_normalize_to_one_fact(
        self,
    ) -> None:
        first, _ = graph_for("Part {1+}+>{2} Whole")
        second, _ = graph_for("Whole {2}<+{1+} Part")
        self.assertEqual(first["edges"], second["edges"])
        edge = first["edges"][0]
        names = {row["id"]: row["identity"] for row in first["nodes"]}
        self.assertEqual(
            ("IS_CONTAINED_BY", "Part", "Whole"),
            (
                edge["kind"],
                names[edge["relation_source"]],
                names[edge["relation_target"]],
            ),
        )
        self.assertEqual(
            {"minimum": 1, "maximum": None}, edge["forward_cardinality"]
        )
        self.assertEqual(
            {"minimum": 2, "maximum": 2}, edge["reverse_cardinality"]
        )

    def _relative_qualification(
        self,
    ) -> None:
        graph, _ = graph_for("Root/X/(.Property:Value)")
        names = {row["id"]: row["identity"] for row in graph["nodes"]}
        edges = {
            (
                row["kind"],
                names[row["relation_source"]],
                names[row["relation_target"]],
            )
            for row in graph["edges"]
        }
        self.assertIn(
            ("NARROWER_THAN", "Root/X/(.Property:Value)", "Root/X"), edges
        )
        self.assertIn(("IS_PROPERTY_OF", "Root/X.Property", "Root/X"), edges)
        self.assertIn(
            (
                "IS_ALLOWED_VALUE_OF",
                "Root/X.Property:Value",
                "Root/X.Property",
            ),
            edges,
        )
        self.assertNotIn("Property:Value", names.values())

    locals()[
        (
            "test_relative_qualification_is_whole"
            "_entity_and_resolves_property_context"
        )
    ] = _relative_qualification

    def _reverse_named_relation(
        self,
    ) -> None:
        forward, _ = graph_for("Step {1}((IS_CONTAINED_BY)){2} Workflow")
        reverse, _ = graph_for("Workflow {2}<((IS_CONTAINED_BY)){1} Step")
        self.assertEqual(forward["edges"], reverse["edges"])
        names = {row["id"]: row["identity"] for row in reverse["nodes"]}
        edge = reverse["edges"][0]
        self.assertEqual(
            ("IS_CONTAINED_BY", "Step", "Workflow"),
            (
                edge["kind"],
                names[edge["relation_source"]],
                names[edge["relation_target"]],
            ),
        )
        self.assertEqual(
            {"minimum": 1, "maximum": 1}, edge["forward_cardinality"]
        )
        self.assertEqual(
            {"minimum": 2, "maximum": 2}, edge["reverse_cardinality"]
        )
        parsed = _subject_parse_subject_expression(
            "Workflow {2}<((IS_CONTAINED_BY)){1} Step"
        )
        self.assertEqual(
            "Workflow {2}<((IS_CONTAINED_BY)){1} Step",
            _subject_render_subject(parsed),
        )

    locals()[
        (
            "test_reverse_named_relation_normalizes_one"
            "_canonical_fact_and_preserves_written_form"
        )
    ] = _reverse_named_relation

    def test_named_relation_chains_and_groups_keep_each_written_direction(
        self,
    ) -> None:
        graph, _ = graph_for(
            "(Step) ((RUN)) Workflow <((IS_CONTAINED_BY)) Part"
        )
        names = {row["id"]: row["identity"] for row in graph["nodes"]}
        edges = {
            (
                row["kind"],
                names[row["relation_source"]],
                names[row["relation_target"]],
            )
            for row in graph["edges"]
        }
        self.assertEqual(
            {
                ("RUN", "Step", "Workflow"),
                ("IS_CONTAINED_BY", "Part", "Workflow"),
            },
            edges,
        )
        for invalid in (
            "Step <((IS_CONTAINED_BY) Workflow",
            "Step ((IS_CONTAINED_BY))> Workflow",
        ):
            with (
                self.subTest(invalid=invalid),
                self.assertRaises(_subject_SubjectNotationError),
            ):
                _subject_parse_subject_expression(invalid)

    def test_logical_head_grouping_does_not_create_another_entity(
        self,
    ) -> None:
        direct, _ = graph_for("Root/X.Property")
        grouped, _ = graph_for("(Root/X).Property")
        self.assertEqual(direct["nodes"], grouped["nodes"])
        self.assertEqual(direct["edges"], grouped["edges"])

    def _conflicting_value_annotations(
        self,
    ) -> None:
        with self.assertRaisesRegex(
            ValueError, "conflicting Subject projection metadata"
        ):
            compose_current_graph(
                [
                    {
                        "source": source(),
                        "subjects": {
                            "governs": "X:Value[Text]",
                            "depends_on": ["X:Value[Number]"],
                        },
                    }
                ]
            )

    locals()[
        (
            "test_conflicting_value_annotations_fa"
            "il_instead_of_discarding_a_constraint"
        )
    ] = _conflicting_value_annotations

    def test_invalid_expression_fails_without_a_literal_node(self) -> None:
        with self.assertRaisesRegex(ValueError, "Subject projection failed"):
            graph_for("X///Broken")


if __name__ == "__main__":
    unittest.main()
