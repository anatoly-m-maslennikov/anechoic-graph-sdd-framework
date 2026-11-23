from __future__ import annotations

from pathlib import Path
import unittest
from unittest.mock import patch


APP_ROOT = Path(__file__).resolve().parents[3]
TOOLS_ROOT = APP_ROOT.parent / "FEATURE_PROGRAMMATIC" / "FEATURE_TOOLS"

from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared import write_scope_unit_declarations  # noqa: E402
from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND import source_reader_validation  # noqa: E402
from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.FEATURE_WORKBENCH_BACKEND__shared import SourceReader  # noqa: E402




from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.FEATURE_WORKBENCH_BACKEND__tests._source_reader_fixture import SourceReaderFixture  # noqa: E402


class SourceReaderTests(SourceReaderFixture, unittest.TestCase):
    def test_duplicate_declared_content_property_is_excluded(self) -> None:
        self._write_atom(
            "MAIN", "04_requirement", "CA-R-490-content-model.md", atom_id="CA-R-490",
            form="Declaration",
            body="## Claim\n\n### Formal Claim\n\n```CFEL\nAtom.Content.Summary{::1}:: {::1};\n```\n",
        )
        path = self._write_atom(
            "MAIN",
            "04_requirement",
            "CA-R-404-duplicate-summary.md",
            atom_id="CA-R-404",
            body="# Summary\n\nFirst.\n\n# Summary\n\nSecond.\n",
        )

        atoms, _scopes, stderr = self._capture()

        self.assertNotIn(path.relative_to(self.root).as_posix(), {row["source_path"] for row in atoms})
        self.assertIn("duplicate declared content property: summary", stderr)

        atoms_again, _scopes_again, second_stderr = self._capture()
        self.assertEqual({row["source_path"] for row in atoms_again}, {row["source_path"] for row in atoms})
        self.assertEqual(second_stderr, "")
        self.assertEqual(self.reader.excluded_count, 1)


    def test_editing_a_failed_source_makes_it_new_input(self) -> None:
        path = self._path("MAIN", "02_analysis", "repair.md")
        path.write_text(
            "---\natom_id: CA-R-410\natom_id: CA-R-411\nrole: Requirement\n"
            "form: Definition\nstatus: Active\nversion: 1\n---\n# Summary\nBad\n",
            encoding="utf-8",
        )
        atoms, _scopes, _stderr = self._capture()
        self.assertNotIn("CA-R-410", {row["id"] for row in atoms})
        self.assertEqual(self.reader.excluded_count, 1)

        path.write_text(
            "---\natom_id: CA-R-410\nrole: Requirement\nform: Definition\n"
            "status: Active\nversion: 2\nupdated_at: \"2026-11-04 00:00:00 +0000\"\n"
            "subjects: {}\nrelations: {}\n---\n# Summary\nRepaired.\n",
            encoding="utf-8",
        )
        atoms, _scopes, stderr = self._capture()

        self.assertEqual(stderr, "")
        self.assertEqual(next(row["version"] for row in atoms if row["id"] == "CA-R-410"), 2)
        self.assertEqual(self.reader.excluded_count, 0)


    def test_unchanged_success_reuses_row_but_changed_invalid_source_drops_it(self) -> None:
        path = self._write_atom("MAIN", "02_analysis", "cached.md", atom_id="CA-R-411")
        with patch.object(
            source_reader_validation,
            "parse_carrier",
            wraps=source_reader_validation.parse_carrier,
        ) as parse:
            atoms, _scopes, stderr = self._capture()
            first_calls = parse.call_count
            self.assertEqual(stderr, "")
            self.assertGreater(first_calls, 0)

            atoms_again, _scopes_again, stderr_again = self._capture()
            self.assertEqual(stderr_again, "")
            self.assertEqual(parse.call_count, first_calls)
            self.assertIn(path.relative_to(self.root).as_posix(), {row["source_path"] for row in atoms_again})

            path.write_text(
                "---\natom_id: CA-R-411\natom_id: CA-R-412\nrole: Requirement\n"
                "form: Definition\nstatus: Active\nversion: 2\n---\n# Summary\nBad\n",
                encoding="utf-8",
            )
            changed_atoms, _scopes_changed, changed_stderr = self._capture()
            self.assertNotIn(path.relative_to(self.root).as_posix(), {row["source_path"] for row in changed_atoms})
            self.assertIn(path.relative_to(self.root).as_posix(), changed_stderr)
            self.assertEqual(parse.call_count, first_calls + 1)
            self.assertEqual(self.reader.excluded_count, 1)

            path.write_text(
                "---\natom_id: CA-R-411\nrole: Requirement\nform: Definition\n"
                "status: Active\nversion: 3\n---\n# Summary\nRepaired.\n",
                encoding="utf-8",
            )
            repaired_atoms, _scopes_repaired, repaired_stderr = self._capture()

            self.assertEqual(parse.call_count, first_calls + 2)
        self.assertEqual(repaired_stderr, "")
        self.assertEqual(next(row["version"] for row in repaired_atoms if row["id"] == "CA-R-411"), 3)
        self.assertEqual(self.reader.excluded_count, 0)


    def test_release_cache_reparses_successes_but_keeps_failed_signatures(self) -> None:
        valid = self._write_atom("MAIN", "01_concern", "valid.md", atom_id="CA-R-415")
        invalid = self._path("MAIN", "04_requirement", "CA-R-416-bad.md")
        invalid.write_text(
            "---\natom_id: CA-R-416\natom_id: CA-R-417\nrole: Requirement\n"
            "form: Definition\nstatus: Active\nversion: 1\n---\n# Summary\nBad\n",
            encoding="utf-8",
        )

        with patch.object(
            source_reader_validation,
            "parse_carrier",
            wraps=source_reader_validation.parse_carrier,
        ) as parse:
            atoms, _scopes, first_stderr = self._capture()
            first_call_count = len(parse.call_args_list)
            self.assertIn(valid.relative_to(self.root).as_posix(), {row["source_path"] for row in atoms})
            self.assertIn(invalid.relative_to(self.root).as_posix(), first_stderr)

            self.reader.release_cache()
            atoms_again, _scopes_again, second_stderr = self._capture()

            second_parsed_paths = {
                Path(call.args[1]).resolve()
                for call in parse.call_args_list[first_call_count:]
            }
            self.assertIn(valid.resolve(), second_parsed_paths)
            self.assertNotIn(invalid.resolve(), second_parsed_paths)
            self.assertIn(valid.relative_to(self.root).as_posix(), {row["source_path"] for row in atoms_again})
            self.assertNotIn(invalid.relative_to(self.root).as_posix(), {row["source_path"] for row in atoms_again})
            self.assertEqual(second_stderr, "")
            self.assertEqual(self.reader.excluded_count, 1)


    def test_unrepresentable_source_and_nonregular_source_only_exclude_themselves(self) -> None:
        valid = self._write_atom("CHILD", "06_evaluation", "valid.md", atom_id="CA-R-420")
        unsupported = self._path("CHILD", "06_evaluation", "unsupported.md")
        unsupported.write_text(
            "---\natom_id: CA-R-421\nrole: Requirement\nform: Definition\n"
            "status: Active\nversion: 1\nunsupported: !!set\n  ? value\n---\n"
            "# Summary\nUnsupported JSON value.\n",
            encoding="utf-8",
        )
        nonregular = self._path("CHILD", "06_evaluation", "CA-E-422-directory.md")
        nonregular.mkdir()

        atoms, _scopes, stderr = self._capture()

        self.assertIn(valid.relative_to(self.root).as_posix(), {row["source_path"] for row in atoms})
        self.assertNotIn(unsupported.relative_to(self.root).as_posix(), {row["source_path"] for row in atoms})
        self.assertNotIn(nonregular.relative_to(self.root).as_posix(), {row["source_path"] for row in atoms})
        self.assertIn(unsupported.relative_to(self.root).as_posix(), stderr)
        self.assertIn(nonregular.relative_to(self.root).as_posix(), stderr)


    def test_plain_review_markdown_is_ignored_without_a_diagnostic(self) -> None:
        for name in ("README.md", "REPORT.md"):
            path = self._path("MAIN", "02_analysis", name, "draft")
            path.write_text("This is review prose, not an Atom carrier.\n", encoding="utf-8")
        copied_atom = self._write_atom(
            "MAIN",
            "02_analysis",
            "CA-R-499-proof-copy.md",
            atom_id="CA-R-499",
            parts=("draft", "frozen-inputs"),
        )

        atoms, _scopes, stderr = self._capture()

        self.assertEqual(stderr, "")
        self.assertNotIn("README.md", {row["source_path"] for row in atoms})
        self.assertNotIn("REPORT.md", {row["source_path"] for row in atoms})
        self.assertIn(copied_atom.relative_to(self.root).as_posix(), {row["source_path"] for row in atoms})
        self.assertEqual(self.reader.excluded_count, 0)


    def test_unterminated_plain_review_markdown_is_ignored_without_a_diagnostic(self) -> None:
        path = self._path("MAIN", "02_analysis", "README.md", "draft")
        path.write_text("---\nReview prose.\nrole: prose\n", encoding="utf-8")

        atoms, _scopes, stderr = self._capture()

        self.assertEqual(stderr, "")
        self.assertNotIn(path.relative_to(self.root).as_posix(), {row["source_path"] for row in atoms})
        self.assertEqual(self.reader.excluded_count, 0)


    def test_lifecycle_group_uses_paths_relative_to_the_selected_project(self) -> None:
        for parent_name in ("archive", "archived", "draft", "drafts"):
            root = self.root.parent / parent_name / "project"
            root.mkdir(parents=True)
            control = root / ".anechoic_anechoic"
            control.mkdir()
            (control / "anechoic_project_settings.toml").write_text(
                '[project]\nname = "fixture"\n[artifacts.identity]\nproject_prefix = "CA"\n'
                '[paths]\ncontrol_root = ".anechoic_anechoic"\n',
                encoding="utf-8",
            )
            declarations = write_scope_unit_declarations(
                root,
                ({
                    "scope_unit_name": "MAIN",
                    "scope_unit_type": "Ordered",
                    "scope_unit_label": "LAYER",
                    "local_order": 1,
                },),
                control_root=control,
            )
            source = Path(declarations["MAIN"]["authority_path"]) / "04_requirement" / "CA-R-701-current.md"
            source.parent.mkdir(parents=True, exist_ok=True)
            source.write_text(
                "---\natom_id: CA-R-701\nrole: Requirement\nform: Definition\n"
                "status: Active\nversion: 1\n---\n# Current\n",
                encoding="utf-8",
            )

            atoms, _scopes = SourceReader(root, control).capture()

            row = next(row for row in atoms if row["id"] == "CA-R-701")
            self.assertEqual(row["status_group"], "Current")



if __name__ == "__main__":
    unittest.main()
