"""Private mixin for applicable methodology conflict tests."""

import importlib


BASE = (
    "FEATURE_PROGRAMMATIC.FEATURE_TOOLS."
    "COMPILE_APPLICABLE_METHODOLOGY."
    "COMPILE_APPLICABLE_METHODOLOGY__tests."
)
support = importlib.import_module(BASE + "methodology_test_support")
phases = importlib.import_module(BASE + "methodology_conflict_phases")
term_definition_carrier = support.term_definition_carrier


class ConflictMixin:
    def test_duplicate_governed_term_definition_blocks_apply(self) -> None:
        self.write(
            "001_CORE_META_MODEL",
            "04_requirement",
            "CA-R-010--define-shared-term.md",
            term_definition_carrier("CA-R-010", "Term//Shared Term"),
        )
        self.write(
            "003_PROJECT_CONFIGURATION",
            "04_requirement",
            "CA-R-011--redefine-shared-term.md",
            term_definition_carrier(
                "CA-R-011", "ANECHOIC_MODEL <+ Term//Shared Term"
            ),
        )

        code, report = self.invoke()

        self.assertEqual(2, code)
        conflict = next(
            row
            for row in report["conflicts"]
            if row["type"] == "duplicate_governed_term_definition"
        )
        self.assertEqual("Shared Term", conflict["details"]["term"])
        apply_code, applied = self.invoke("--apply")
        self.assertEqual(2, apply_code)
        self.assertFalse(applied["can_apply"])

    def test_current_and_legacy_term_definitions_conflict(self) -> None:
        current_subject = "ANECHOIC_MODEL <+ Term//Shared Term"
        self.write(
            "001_CORE_META_MODEL",
            "05_method",
            "CA-M-010--define.md",
            term_definition_carrier("CA-M-010", current_subject),
        )
        self.write(
            "003_PROJECT_CONFIGURATION",
            "05_method",
            "CA-M-011--define.md",
            term_definition_carrier("CA-M-011", "Term//Shared Term"),
        )
        legacy_subject = (
            "ANECHOIC_MODEL <+ Entity/Object/Continuant/Term//Shared Term"
        )
        self.write(
            "001_CORE_META_MODEL",
            "04_requirement",
            "CA-R-013--define.md",
            (
                "---\natom_id: CA-R-013\nrole: Requirement\n"
                "form: Term Definition\n"
                f"subjects:\n  active: {legacy_subject}\n"
                "status: Active\nversion: 1\nrelations: {}\n"
                "---\n# Define Shared Term\n"
            ).encode(),
        )

        code, report = self.invoke()

        self.assertEqual(2, code)
        conflict = next(
            row
            for row in report["conflicts"]
            if row["type"] == "duplicate_governed_term_definition"
        )
        self.assertEqual("Shared Term", conflict["details"]["term"])
        self.assertCountEqual(
            [current_subject, "Term//Shared Term", legacy_subject],
            conflict["details"]["definition_subject_paths"].values(),
        )
        apply_code, applied = self.invoke("--apply")
        self.assertEqual(2, apply_code)
        self.assertFalse(applied["can_apply"])

    def test_separate_model_term_definitions_do_not_conflict(self) -> None:
        self.write(
            "001_CORE_META_MODEL",
            "05_method",
            "CA-M-010--define.md",
            term_definition_carrier("CA-M-010", "ANECHOIC_MODEL <+ Term//ID"),
        )
        self.write(
            "003_PROJECT_CONFIGURATION",
            "05_method",
            "CA-M-011--define.md",
            term_definition_carrier("CA-M-011", "MODEL//Other <+ Term//ID"),
        )

        code, report = self.invoke()

        self.assertEqual(0, code)
        self.assertNotIn(
            "duplicate_governed_term_definition",
            {row["type"] for row in report["conflicts"]},
        )

    def test_escaped_term_name_does_not_collide_with_model_qualified_term(
        self,
    ) -> None:
        report = phases.escaped_setup(self)
        phases.escaped_output(self, report)
        phases.escaped_conflicts(self)
