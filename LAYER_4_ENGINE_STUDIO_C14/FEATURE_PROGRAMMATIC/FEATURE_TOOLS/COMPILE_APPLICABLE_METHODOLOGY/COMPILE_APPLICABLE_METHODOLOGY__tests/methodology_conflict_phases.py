"""Private phases for the methodology conflict tests."""

import importlib

support = importlib.import_module(
    "FEATURE_PROGRAMMATIC.FEATURE_TOOLS."
    "COMPILE_APPLICABLE_METHODOLOGY."
    "COMPILE_APPLICABLE_METHODOLOGY__tests.methodology_test_support"
)
carrier = support.carrier
term_definition_carrier = support.term_definition_carrier


def escaped_setup(self):
    self.write(
        "001_CORE_META_MODEL",
        "05_method",
        "CA-M-010--define.md",
        term_definition_carrier(
            "CA-M-010", r"Term//MODEL\/\/Other \<\+ Term\/\/ID"
        ),
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
    return report


def escaped_output(self, report):
    output = {row["source_atom_id"]: row for row in report["output_plan"]}
    self.assertEqual(
        output["CA-M-010"]["definition_term"],
        output["CA-M-011"]["definition_term"],
    )
    self.assertEqual(
        ("", "MODEL//Other <+ Term//ID"),
        (
            output["CA-M-010"]["definition_namespace"],
            output["CA-M-010"]["definition_term_name"],
        ),
    )
    self.assertEqual(
        ("MODEL//Other", "ID"),
        (
            output["CA-M-011"]["definition_namespace"],
            output["CA-M-011"]["definition_term_name"],
        ),
    )


def escaped_conflicts(self):
    self.write(
        "001_CORE_META_MODEL",
        "05_method",
        "CA-M-012--define.md",
        term_definition_carrier("CA-M-012", "MODEL//Other <+ Term//ID"),
    )
    self.write(
        "003_PROJECT_CONFIGURATION",
        "05_method",
        "CA-M-013--define.md",
        term_definition_carrier(
            "CA-M-013", r"Term//MODEL\/\/Other \<\+ Term\/\/ID"
        ),
    )
    code, report = self.invoke()
    self.assertEqual(2, code)
    conflicts = [
        row["details"]
        for row in report["conflicts"]
        if row["type"] == "duplicate_governed_term_definition"
    ]
    self.assertEqual(2, len(conflicts))
    self.assertEqual(
        {"MODEL//Other <+ Term//ID"}, {row["term"] for row in conflicts}
    )
    self.assertEqual(
        {("", "MODEL//Other <+ Term//ID"), ("MODEL//Other", "ID")},
        {
            (row["definition_namespace"], row["definition_term_name"])
            for row in conflicts
        },
    )
    self.assertTrue(
        all(len(row["definition_subject_paths"]) == 2 for row in conflicts)
    )


def write_first_conflicts(self):
    self.write(
        "001_CORE_META_MODEL",
        "04_requirement",
        "CA-R-001-A--one.md",
        carrier("CA-R-001"),
    )
    self.write(
        "003_PROJECT_CONFIGURATION",
        "04_requirement",
        "CA-R-001-B--two.md",
        carrier("CA-R-001", version=2),
    )
    self.write(
        "001_CORE_META_MODEL",
        "04_requirement",
        "CA-R-002--replacer.md",
        carrier("CA-R-002", relations="\n  replacement_of:\n    - CA-R-003"),
    )
    self.write(
        "003_PROJECT_CONFIGURATION",
        "04_requirement",
        "CA-R-003--replaced.md",
        carrier("CA-R-003"),
    )
    self.write(
        "001_CORE_META_MODEL",
        "04_requirement",
        "CA-R-004--incompatible.md",
        carrier(
            "CA-R-004", relations="\n  incompatible_with:\n    - CA-R-005"
        ),
    )


def write_remaining_conflicts(self):
    self.write(
        "003_PROJECT_CONFIGURATION",
        "04_requirement",
        "CA-R-005--other.md",
        carrier("CA-R-005"),
    )
    self.write(
        "001_CORE_META_MODEL",
        "05_method",
        "CA-M-001--priority-a.md",
        carrier(
            "CA-M-001",
            extra=(
                "applicable_methodology_priority_group: group-one\n"
                "priority: 10\n"
            ),
        ),
    )
    self.write(
        "003_PROJECT_CONFIGURATION",
        "05_method",
        "CA-M-002--priority-b.md",
        carrier(
            "CA-M-002",
            extra=(
                "applicable_methodology_priority_group: group-one\n"
                "priority: 20\n"
            ),
        ),
    )
    self.write(
        "001_CORE_META_MODEL",
        "06_evaluation",
        "SHARED--collision.md",
        carrier("CA-E-001"),
    )
    self.write(
        "003_PROJECT_CONFIGURATION",
        "06_evaluation",
        "SHARED--collision.md",
        carrier("CA-E-002"),
    )
