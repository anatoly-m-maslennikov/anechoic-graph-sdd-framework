"""Subject audit scope and declaration cases."""

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.GENERATE_ENTITY_GRAPH__shared import (
    build_subject_projection_data,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.subjects.audit.\
    audit__shared import (
    build_subject_audits,
    render_subject_audit,
    select_model_subjects,
)  # fmt: skip

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.GENERATE_ENTITY_GRAPH__tests.subjects.audits._subject_projection_audit_fixture import (
    carrier,
)


class SubjectAuditCases:
    def test_existing_model_relation_path_survives_projection_scope(self):
        address = "ANECHOIC_MODEL/CFEL/Relation//IS_ORDERED_RIGHT_AFTER"
        selected, diagnostics = select_model_subjects(
            [
                carrier("CA-R-2965", address, form="Relation Declaration"),
            ]
        )
        self.assertEqual(address, selected[0]["subjects"]["active"])
        self.assertEqual([], diagnostics)

    def _case_model_scope(
        self,
    ):
        sources = self._scope_sources()
        selected, diagnostics = select_model_subjects(sources)
        self.assertEqual(3, len(selected))
        self.assertEqual(
            ["Legacy Node", "{'legacy': 'not a Subject'}"],
            [row["raw_value"] for row in diagnostics],
        )
        passive = selected[0]["subjects"]["passive"]
        self.assertEqual(4, len(passive))
        self.assertTrue(any("Relation//RUN" in row for row in passive))
        self.assertTrue(any("Operator//Alias" in row for row in passive))
        self.assertTrue(any("Format//markdown" in row for row in passive))
        self.assertTrue(any("Term//Word" in row for row in passive))
        self.assertNotIn("active", selected[1]["subjects"])
        data = build_subject_projection_data([selected[0]])
        audits = build_subject_audits(
            selected, data, scope_diagnostics=diagnostics
        )
        identities = {
            row["identity"]
            for row in audits["entity_definition_summary"]["entities"]
        }
        self.assertNotIn("Project", identities)
        self.assertFalse(any("Example" in identity for identity in identities))
        self.assertTrue(
            {"RUN", "Operator//Alias", "Format//markdown", "Term//Word"}
            <= identities
        )
        self.assertIn(
            "Legacy Node",
            [
                row["subject"]
                for row in audits["subjects_without_declaration_coverage"][
                    "unresolved"
                ]
            ],
        )
        self.assertEqual(
            "ANECHOIC_STRUCTURE <+ Project", sources[1]["subjects"]["active"]
        )

    def _scope_sources(self):
        return [
            carrier(
                "CA-R-1",
                "ANECHOIC_MODEL <+ Node",
                [
                    "ANECHOIC_STRUCTURE <+ Project",
                    "ANECHOIC_MODEL <+ Node//Example",
                    "ANECHOIC_MODEL <+ Node//Example.Name",
                    "ANECHOIC_MODEL <+ CFEL <+ Relation//RUN",
                    "ANECHOIC_MODEL <+ CFEL <+ Operator//Alias",
                    "ANECHOIC_MODEL <+ CFEL <+ Format//markdown",
                    "ANECHOIC_MODEL <+ Term//Word",
                    "Legacy Node",
                ],
            ),
            carrier(
                "CA-R-2",
                "ANECHOIC_STRUCTURE <+ Project",
                ["ANECHOIC_MODEL <+ Node"],
            ),
            carrier(
                "CA-R-3",
                "ANECHOIC_STRUCTURE <+ Project",
                [{"legacy": "not a Subject"}],
            ),
        ]

    def test_selection_groups_keep_model_scope_and_exclude_instance_scope(
        self,
    ):
        model = "ANECHOIC <+ MODEL <+ (Node, Node.**)"
        instance = "ANECHOIC <+ MODEL <+ (Node//,(Node//).**)"
        selected, diagnostics = select_model_subjects(
            [
                carrier("CA-R-1", model, [instance], form="Rule"),
                carrier("CA-R-2", instance, form="Rule"),
                carrier("CA-R-3", "ANECHOIC_STRUCTURE", form="Rule"),
            ]
        )
        self.assertEqual(model, selected[0]["subjects"]["active"])
        self.assertNotIn("passive", selected[0]["subjects"])
        self.assertEqual({}, selected[1]["subjects"])
        self.assertEqual({}, selected[2]["subjects"])
        self.assertEqual([], diagnostics)
        audits = build_subject_audits(selected)
        unresolved = audits["subjects_without_declaration_coverage"][
            "unresolved"
        ]
        self.assertTrue(
            any(
                row["subject"] == "ANECHOIC <+ MODEL <+ (Node,Node.**)"
                for row in unresolved
            )
        )

    def test_passive_set_difference_does_not_confuse_owner_active_subjects(
        self,
    ):
        audits = build_subject_audits(
            [
                carrier("CA-R-1", "OwnerA", ["Shared", "Passive Only"]),
                carrier("CA-R-2", "OwnerB", ["Shared"]),
                carrier("CA-R-3", "Shared"),
            ]
        )
        rows = audits["passive_only_subjects"]["subjects"]
        self.assertEqual(["Passive Only"], [row["subject"] for row in rows])
        self.assertEqual("passive", rows[0]["occurrences"][0]["source_key"])

    def _case_exact_requirement(
        self,
    ):
        audits = build_subject_audits(
            [
                carrier("CA-R-1", "Node"),
                carrier("CA-R-2", "Rule Only", form="Rule"),
                carrier("CA-R-3", "CFEL", form="Entity Definition"),
            ]
        )
        report = audits["subjects_without_declaration_coverage"]
        self.assertEqual(
            ["Rule Only"], [row["subject"] for row in report["subjects"]]
        )
        self.assertEqual(
            ["CFEL"], [row["subject"] for row in report["informational"]]
        )

    def test_inherited_property_is_covered_by_its_original_declaration(self):
        audits = build_subject_audits(
            [
                carrier("CA-R-1", "Node"),
                carrier("CA-R-2", "Node/Child"),
                carrier("CA-R-3", "Node.Status"),
                carrier("CA-R-4", "Node/Child.Status", ["Node/Child.Status"]),
            ]
        )
        report = audits["subjects_without_declaration_coverage"]
        self.assertNotIn(
            "Node/Child.Status", [row["subject"] for row in report["subjects"]]
        )

    def _case_namespaced_subject(
        self,
    ):
        legacy = carrier("CA-R-1", "Node", ["ANECHOIC <+ MODEL <+ Node"])
        legacy["subjects"] = {
            "governs": "Node",
            "depends_on": ["ANECHOIC <+ MODEL <+ Node", "not valid ("],
        }
        audits = build_subject_audits([legacy])
        row = audits["passive_only_subjects"]["subjects"][0]
        self.assertEqual("depends_on", row["occurrences"][0]["source_key"])
        report = audits["subjects_without_declaration_coverage"]
        self.assertTrue(report["unresolved"])
        self.assertEqual(
            "not valid (",
            audits["passive_only_subjects"]["subjects"][1]["subject"],
        )
        self.assertTrue(
            audits["passive_only_subjects"]["subjects"][1]["unresolved"]
        )
        self.assertIn(
            "# Subjects Used Only Passively",
            render_subject_audit(audits, "passive_only_subjects"),
        )


setattr(
    SubjectAuditCases,
    "test_model_scope_excludes_structure_and_concrete"
    "_instances_but_keeps_descriptors",
    SubjectAuditCases._case_model_scope,
)

setattr(
    SubjectAuditCases,
    "test_exact_requirement_declaration_excludes_rule"
    "s_and_entity_definitions_are_informational",
    SubjectAuditCases._case_exact_requirement,
)

setattr(
    SubjectAuditCases,
    "test_namespaced_subject_and_unsupported_subject_"
    "keep_provenance_and_review_state",
    SubjectAuditCases._case_namespaced_subject,
)
