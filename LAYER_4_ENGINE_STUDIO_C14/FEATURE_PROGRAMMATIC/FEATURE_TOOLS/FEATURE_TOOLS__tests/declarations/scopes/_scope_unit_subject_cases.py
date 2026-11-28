"""Scope Unit subject declaration cases."""

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.structure.scope.scope_carrier__pub import (
    ScopeDeclarationError,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.structure.scope.scope_declaration_parse__pub import (
    parse_scope_unit_declaration,
)
from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared import (
    PROJECT,
)


class ScopeUnitSubjectCases:
    def test_prefixed_active_subjects_roundtrip_while_claims_stay_local(
        self,
    ) -> None:
        root_source = self.declaration(
            "anechoic",
            "CA-R-1",
            source=self.control / "CA-R-1-anechoic.md",
            project=True,
            project_name="anechoic",
        )
        parent_source = self.declaration(
            "PARENT",
            "CA-R-2",
            scope_id="CA-SU-1",
            label="LAYER",
            ordered=True,
            order_number=1,
            parent=PROJECT,
            project_name="anechoic",
        )
        child_source = self.declaration(
            "CHILD",
            "CA-R-3",
            source=self.control
            / "CA-SU-1_LAYER_1_PARENT"
            / "04_requirement"
            / "child.md",
            scope_id="CA-SU-2",
            label="FEATURE",
            parent="PARENT",
            project_name="anechoic",
        )

        self._assert_subject_roundtrip(
            root_source, parent_source, child_source
        )

    def _assert_subject_roundtrip(
        self, root_source, parent_source, child_source
    ):
        for source, local_subject in (
            (root_source, "Project//anechoic"),
            (parent_source, "Scope Unit//PARENT"),
            (child_source, "Scope Unit//CHILD"),
        ):
            text = source.read_text(encoding="utf-8")
            self.assertIn(
                f'active: "ANECHOIC_STRUCTURE <+ {local_subject}"', text
            )
            self.assertIn(
                f'entity_name="{local_subject.split("//", 1)[1]}"',
                text.split("## Claim", 1)[1],
            )
            self.assertNotIn("ANECHOIC", text.split("## Claim", 1)[1])
            parsed = parse_scope_unit_declaration(text.encode(), source)
            self.assertEqual(parsed.name, local_subject.split("//", 1)[1])

    def test_legacy_bare_active_subject_remains_compatible(self) -> None:
        source = self.declaration(
            "UNIT",
            "CA-R-2",
            scope_id="CA-SU-2",
            parent=PROJECT,
            project_name="anechoic",
        )
        raw = source.read_text(encoding="utf-8").replace(
            "ANECHOIC_STRUCTURE <+ Scope Unit//UNIT",
            "Scope Unit//UNIT",
        )
        source.write_text(raw, encoding="utf-8")

        self.assertEqual(
            parse_scope_unit_declaration(source.read_bytes(), source).name,
            "UNIT",
        )

    def test_current_main_subject_replaces_legacy_active_subject(self) -> None:
        source = self.declaration(
            "UNIT",
            "CA-R-2",
            scope_id="CA-SU-2",
            parent=PROJECT,
            project_name="anechoic",
        )
        source.write_text(
            source.read_text(encoding="utf-8")
            .replace(
                "subjects:\n  active:",
                "topics:\n  main_subject:",
            )
            .replace("\n  passive: []", ""),
            encoding="utf-8",
        )

        self.assertEqual(
            parse_scope_unit_declaration(source.read_bytes(), source).name,
            "UNIT",
        )

    def test_formal_identity_allows_missing_but_not_ambiguous_main_subject(
        self,
    ) -> None:
        source = self.declaration(
            "UNIT",
            "CA-R-2",
            scope_id="CA-SU-2",
            parent=PROJECT,
            project_name="anechoic",
        )
        current = source.read_text(encoding="utf-8")
        missing = current.replace(
            'subjects:\n  active: "ANECHOIC_STRUCTURE <+ Scope Unit//UNIT"\n  passive: []\n',
            "",
        )
        equal_aliases = current.replace(
            "subjects:\n",
            'topics:\n  main_subject: "ANECHOIC_STRUCTURE <+ Scope Unit//UNIT"\nsubjects:\n',
        )
        ambiguous = equal_aliases.replace(
            'main_subject: "ANECHOIC_STRUCTURE <+ Scope Unit//UNIT"',
            'main_subject: "ANECHOIC_STRUCTURE <+ Scope Unit//OTHER"',
        )
        invalid_current = current.replace(
            "subjects:\n",
            "topics:\n  main_subject: 1\nsubjects:\n",
        )

        self.assertEqual(
            "UNIT", parse_scope_unit_declaration(missing.encode(), source).name
        )
        self.assertEqual(
            "UNIT",
            parse_scope_unit_declaration(equal_aliases.encode(), source).name,
        )
        with self.assertRaisesRegex(
            ScopeDeclarationError, "invalid declaration carrier"
        ):
            parse_scope_unit_declaration(ambiguous.encode(), source)
        with self.assertRaisesRegex(
            ScopeDeclarationError, "invalid declaration carrier"
        ):
            parse_scope_unit_declaration(invalid_current.encode(), source)

    def test_prefixed_active_subject_wrong_branch_refuses(self) -> None:
        source = self.declaration(
            "UNIT",
            "CA-R-2",
            scope_id="CA-SU-2",
            parent=PROJECT,
            project_name="anechoic",
        )
        source.write_text(
            source.read_text(encoding="utf-8").replace(
                "ANECHOIC_STRUCTURE <+ Scope Unit//UNIT",
                "ANECHOIC_MODEL <+ Scope Unit//UNIT",
            ),
            encoding="utf-8",
        )

        with self.assertRaisesRegex(ScopeDeclarationError, "namespace branch"):
            parse_scope_unit_declaration(source.read_bytes(), source)

    def test_named_structure_namespace_is_read_without_changing_the_source(
        self,
    ) -> None:
        source = self.declaration(
            "UNIT",
            "CA-R-2",
            scope_id="CA-SU-2",
            parent=PROJECT,
            project_name="anechoic",
        )
        carrier = source.read_bytes().replace(
            b"ANECHOIC_STRUCTURE <+ Scope Unit//UNIT",
            b"PROJECT STRUCTURE//ANECHOIC <+ Scope Unit//UNIT",
        )
        self.assertEqual(
            "UNIT", parse_scope_unit_declaration(carrier, source).name
        )
        with self.assertRaisesRegex(ScopeDeclarationError, "namespace branch"):
            parse_scope_unit_declaration(
                carrier.replace(b"PROJECT STRUCTURE//", b"MODEL//"), source
            )
