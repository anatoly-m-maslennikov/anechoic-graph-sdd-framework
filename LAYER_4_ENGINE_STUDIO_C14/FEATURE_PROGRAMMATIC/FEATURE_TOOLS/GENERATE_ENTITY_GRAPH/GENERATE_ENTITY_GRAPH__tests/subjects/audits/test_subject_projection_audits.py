"""Focused checks for the additive Subject audit layer."""

from pathlib import Path
import sys
import unittest


TOOL = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(TOOL.parent), str(TOOL)]

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.GENERATE_ENTITY_GRAPH__shared import (  # noqa: E402
    build_subject_projection_data as build_subject_projection_data,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.subjects.audit.\
    audit__shared import (  # noqa: E402
    build_subject_audits,
    render_subject_audit,
    select_model_subjects,  # noqa: F401
)  # fmt: skip


from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.GENERATE_ENTITY_GRAPH__tests.subjects.audits._subject_projection_audit_fixture import (  # noqa: E402
    carrier as carrier,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.GENERATE_ENTITY_GRAPH__tests.subjects.audits._subject_projection_audit_cases import (  # noqa: E402
    SubjectAuditCases,
)


class SubjectProjectionAuditTests(SubjectAuditCases, unittest.TestCase):
    def test_entity_summary_keeps_definition_and_active_flags_orthogonal(self):
        scope = carrier(
            "CA-R-1", "Scope Unit//Alpha", form="Scope Unit Declaration"
        )
        term = carrier(
            "CA-M-2", "Term//Word", role="Method", form="Term Definition"
        )
        entity = carrier("CA-R-3", "CFEL", form="Entity Definition")
        rule = carrier("CA-R-4", "Rule Only", form="Rule")
        passive = carrier("CA-R-5", "Owner", ["Passive Only"])
        report = build_subject_audits([scope, term, entity, rule, passive])[
            "entity_definition_summary"
        ]
        rows = {row["identity"]: row for row in report["entities"]}
        self.assertFalse(rows["Scope Unit//Alpha"]["missing_definition"])
        self.assertFalse(rows["Term//Word"]["missing_definition"])
        self.assertFalse(rows["CFEL"]["missing_definition"])
        self.assertTrue(rows["Rule Only"]["missing_definition"])
        self.assertFalse(rows["Rule Only"]["missing_active"])
        self.assertTrue(rows["Passive Only"]["missing_active"])
        self.assertIn(
            "| Entity |",
            render_subject_audit(
                {"entity_definition_summary": report},
                "entity_definition_summary",
            ),
        )

    def test_term_definition_is_informational_only_for_its_exact_term(self):
        audits = self._term_audits()
        report = audits["subjects_without_declaration_coverage"]
        info = {row["subject"]: row for row in report["informational"]}
        missing = {row["subject"] for row in report["subjects"]}
        self.assertEqual(
            ["CA-M-1@1"], info["Term//Word"]["term_definition_refs"]
        )
        self.assertIn(
            "Term Definition: CA-M-1@1",
            render_subject_audit(
                audits, "subjects_without_declaration_coverage"
            ),
        )
        self.assertTrue(
            {"Term//Unregistered", "Term//Wrong", "Format//markdown"}
            <= missing
        )
        summary = {
            row["identity"]: row
            for row in audits["entity_definition_summary"]["entities"]
        }
        self.assertFalse(summary["Term//Word"]["missing_definition"])
        self.assertFalse(summary["Term//Word"]["missing_active"])
        self.assertTrue(summary["Term//Unregistered"]["missing_definition"])
        self.assertTrue(summary["Term//Unregistered"]["missing_active"])
        self.assertTrue(summary["Term//Wrong.Name"]["missing_definition"])
        self.assertTrue(summary["Format//markdown"]["missing_definition"])

    def _term_audits(self):
        return build_subject_audits(
            [
                carrier(
                    "CA-M-1",
                    "ANECHOIC <+ MODEL <+ Term//Word",
                    role="Method",
                    form="Term Definition",
                ),
                carrier(
                    "CA-M-2",
                    "Term//Wrong.Name",
                    role="Method",
                    form="Term Definition",
                ),
                carrier(
                    "CA-M-3",
                    "Format//markdown",
                    role="Method",
                    form="Term Definition",
                ),
                carrier(
                    "CA-R-4",
                    "Owner",
                    [
                        "Term//Word",
                        "Term//Unregistered",
                        "Term//Wrong",
                        "Format//markdown",
                    ],
                ),
            ]
        )

    def test_exact_relation_and_instance_declarations_cover_their_own_targets(
        self,
    ):
        audits = build_subject_audits(
            [
                carrier("CA-R-1", "Relation//RUN"),
                carrier("CA-R-2", "Node"),
                carrier("CA-R-3", "Node//Example"),
            ]
        )
        missing = audits["subjects_without_declaration_coverage"]["subjects"]
        self.assertNotIn("Relation//RUN", [row["subject"] for row in missing])
        self.assertNotIn("Node//Example", [row["subject"] for row in missing])

    def test_prefixed_cfel_relation_and_known_qualified_selector_are_covered(
        self,
    ):
        audits = build_subject_audits(
            [
                carrier(
                    "CA-R-1",
                    "ANECHOIC <+ MODEL <+ CFEL <+ Relation//IS_PROPERTY_OF",
                ),
                carrier("CA-R-2", "Atom"),
                carrier("CA-R-3", "Atom.Role"),
                carrier("CA-R-4", "Atom.Form"),
                carrier(
                    "CA-R-5",
                    "Owner",
                    ["Atom/(.Role:=Analysis)/(.Form:=Report)"],
                ),
            ]
        )
        missing = audits["subjects_without_declaration_coverage"]["subjects"]
        self.assertNotIn(
            "ANECHOIC <+ MODEL <+ CFEL <+ Relation//IS_PROPERTY_OF",
            [row["subject"] for row in missing],
        )
        self.assertNotIn(
            "Atom/(.Role := Analysis)/(.Form := Report)",
            [row["subject"] for row in missing],
        )

    def _case_prefixed_selector(
        self,
    ):
        audits = build_subject_audits(
            [
                carrier("CA-R-1", "ANECHOIC <+ MODEL <+ Atom"),
                carrier("CA-R-2", "ANECHOIC <+ MODEL <+ Atom.Status"),
                carrier(
                    "CA-R-3",
                    "Owner",
                    ["ANECHOIC <+ MODEL <+ Atom.Status: Draft"],
                ),
            ]
        )
        missing = audits["subjects_without_declaration_coverage"]["subjects"]
        self.assertNotIn(
            "ANECHOIC <+ MODEL <+ Atom.Status: Draft",
            [row["subject"] for row in missing],
        )

    def test_entity_summary_uses_original_inherited_property_declaration(self):
        audits = build_subject_audits(
            [
                carrier("CA-R-1", "Node"),
                carrier("CA-R-2", "Node/Child"),
                carrier("CA-R-3", "Node.Status"),
                carrier("CA-R-4", "Owner", ["Node/Child.Status"]),
            ]
        )
        row = next(
            row
            for row in audits["entity_definition_summary"]["entities"]
            if row["identity"] == "Node/Child.Status"
        )
        self.assertEqual(["CA-R-3@1"], row["defining_refs"])
        self.assertTrue(row["missing_active"])

    def test_invalid_passive_values_render_as_diagnostics(self):
        audits = build_subject_audits(
            [carrier("CA-R-1", "Node", [None, "", 3])]
        )
        rendered = render_subject_audit(audits, "passive_only_subjects")
        self.assertIn("## Diagnostics (3)", rendered)
        self.assertIn("CA-R-1@1", rendered)

    def test_metadata_subject_keys_win_over_alias_normalized_read_view(self):
        source = carrier("CA-R-1", "wrong", ["wrong"])
        source["metadata"] = {
            "subjects": {"active": "Owner", "passive": ["Dependency"]}
        }
        source["subjects"] = {
            "active": "Owner",
            "governs": "Owner",
            "passive": ["Dependency"],
            "depends_on": ["Dependency"],
        }
        audits = build_subject_audits([source])
        report = audits["passive_only_subjects"]
        self.assertEqual(2, report["coverage"]["subject_occurrences"])
        self.assertEqual(
            ["Dependency"], [row["subject"] for row in report["subjects"]]
        )
        self.assertEqual(
            "passive", report["subjects"][0]["occurrences"][0]["source_key"]
        )


setattr(
    SubjectProjectionAuditTests,
    "test_prefixed_allowed_value_selector_binds_exist"
    "ing_property_without_a_value_node",
    SubjectProjectionAuditTests._case_prefixed_selector,
)


if __name__ == "__main__":
    unittest.main()
