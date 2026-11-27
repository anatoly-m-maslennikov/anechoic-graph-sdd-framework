"""Read-only Project Settings values retain explicit selection semantics."""

from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest


sys.path.insert(0, str(TOOLS := Path(__file__).resolve().parents[1]))

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__shared import (
    ProjectSelection,
    bind_selection,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared \
    import (
        ProjectSelectionError,
        bound_selection,
    )  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (  # noqa: E402
    ProjectSettingsValueError,
    control_root,
    project_identity_prefix,
)


class ProjectSettingsValuesTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "project"
        self.root.mkdir()
        self.control = self.root / ".anechoic_anechoic"
        self.control.mkdir()
        self.settings = self.control / "anechoic_project_settings.toml"
        self.settings.write_text(
            (
                "[artifacts.identity]\nproject_prefix = "
                '"CA"\n[paths]\ncontrol_root = ".anechoic_anechoic"\n'
            ),
            encoding="utf-8",
        )

    def test_unbound_uses_only_the_canonical_settings_carrier(self) -> None:
        self.assertEqual(self.control.resolve(), control_root(self.root))
        self.assertEqual("CA", project_identity_prefix(self.root))

    def test_unbound_does_not_require_scope_declarations(self) -> None:
        self.assertEqual("CA", project_identity_prefix(self.root))

    def test_invalid_values_remain_attributable(self) -> None:
        self.settings.write_text(
            '[paths]\ncontrol_root = ".anechoic_other"\n', encoding="utf-8"
        )
        with self.assertRaises(ProjectSettingsValueError) as control_error:
            control_root(self.root)
        self.assertEqual(
            "project-settings-invalid", control_error.exception.code
        )
        with self.assertRaises(ProjectSettingsValueError) as prefix_error:
            project_identity_prefix(self.root)
        self.assertEqual(
            "project-settings-invalid", prefix_error.exception.code
        )

    def test_bound_selection_is_used_without_opening_settings(self) -> None:
        def selection(prefix):
            return ProjectSelection(
                root=self.root.resolve(),
                control_root=self.control.resolve(),
                control_relative=Path(".anechoic_anechoic"),
                instance_id="a" * 64,
                settings={
                    "artifacts": {"identity": {"project_prefix": prefix}}
                },
                structure={},
                declaration_paths=(),
                declaration_source_pins={},
                declaration_digest="",
            )

        outer, inner = selection("OUTER"), selection("INNER")
        self.settings.unlink()
        with bind_selection(outer):
            self.assertEqual(self.control.resolve(), control_root(self.root))
            self.assertEqual("OUTER", project_identity_prefix(self.root))
            with bind_selection(inner):
                self.assertEqual("INNER", project_identity_prefix(self.root))
            self.assertEqual("OUTER", project_identity_prefix(self.root))
            with self.assertRaisesRegex(
                ProjectSelectionError,
                "Active Project selection belongs to another root",
            ):
                control_root(self.root.parent)
        self.assertIsNone(bound_selection())
        with self.assertRaisesRegex(
            ProjectSelectionError,
            "Only a validated ProjectSelection can be bound",
        ):
            with bind_selection(object()):
                pass


if __name__ == "__main__":
    unittest.main()
