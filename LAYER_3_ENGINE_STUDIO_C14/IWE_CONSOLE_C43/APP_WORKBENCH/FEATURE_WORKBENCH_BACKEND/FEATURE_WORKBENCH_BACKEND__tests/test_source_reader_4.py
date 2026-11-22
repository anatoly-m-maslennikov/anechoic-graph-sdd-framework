from __future__ import annotations

from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path
import unittest
from unittest.mock import patch


APP_ROOT = Path(__file__).resolve().parents[3]
TOOLS_ROOT = APP_ROOT.parent / "FEATURE_PROGRAMMATIC" / "FEATURE_TOOLS"

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.scope_carrier__pub import ScopeDeclarationError  # noqa: E402
from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND import source_reader_capture  # noqa: E402
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__pub import ReadContext  # noqa: E402
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.markdown_content__pub import source_markdown  # noqa: E402
from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.source_reader import SourceReader  # noqa: E402




from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.FEATURE_WORKBENCH_BACKEND__tests._source_reader_fixture import SourceReaderFixture  # noqa: E402


class SourceReaderTests(SourceReaderFixture, unittest.TestCase):
    def test_mixed_frontmatter_line_endings_preserve_the_exact_body(self) -> None:
        path = self._path("MAIN", "04_requirement", "mixed.md")
        body = b"# Summary\r\n\r\nMixed body.\r\n"
        path.write_bytes(
            b"---\r\n"
            b"atom_id: CA-R-702\n"
            b"role: Requirement\r\n"
            b"form: Definition\n"
            b"status: Active\r\n"
            b"version: 1\n"
            b"---\r\n"
            + body
        )

        atoms, _scopes, stderr = self._capture()

        self.assertEqual(stderr, "")
        row = next(row for row in atoms if row["id"] == "CA-R-702")
        self.assertNotIn("content_markdown", row)
        self.assertEqual(row["_content_bytes"], body)
        self.assertEqual(source_markdown(row), body.decode("utf-8"))


    def test_unreadable_matching_atom_is_reported_even_in_another_role_folder(self) -> None:
        proof_copy = self._write_atom(
            "MAIN", "02_analysis", "CA-R-703-proof-copy.md", atom_id="CA-R-703"
        )
        original_read = ReadContext.read

        def fail_proof_copy(context, path, **kwargs):
            if Path(path).resolve() == proof_copy.resolve():
                raise OSError("proof copy unavailable")
            return original_read(context, path, **kwargs)

        stderr = StringIO()
        with patch.object(ReadContext, "read", new=fail_proof_copy), redirect_stderr(stderr):
            atoms, _scopes = self.reader.capture()

        self.assertIn("proof copy unavailable", stderr.getvalue())
        self.assertNotIn(proof_copy.relative_to(self.root).as_posix(), {row["source_path"] for row in atoms})
        self.assertEqual(self.reader.excluded_count, 1)


    def test_broken_scope_declaration_reports_and_raises(self) -> None:
        declaration = Path(self.declarations["MAIN"]["declaration_path"])
        declaration.write_text(
            declaration.read_text(encoding="utf-8").replace(
                'atom_id: "CA-R-990001"',
                'atom_id: "CA-R-990001"\natom_id: "CA-R-990099"',
            ),
            encoding="utf-8",
        )

        stderr = StringIO()
        with redirect_stderr(stderr), self.assertRaises(ScopeDeclarationError):
            self.reader.capture()

        self.assertIn(str(self.root), stderr.getvalue())
        self.assertEqual(self.reader.excluded_count, 0)


    def test_explicit_control_root_uses_uppercase_configured_project_prefix(self) -> None:
        source = self._write_atom("MAIN", "04_requirement", "explicit.md", atom_id="CA-R-501")
        settings = self.control / "anechoic_project_settings.toml"
        settings.write_text(settings.read_text().replace('project_prefix = "CA"', 'project_prefix = "demo"'))
        source = source.rename(source.with_name("demo-R-explicit.md"))

        reader = SourceReader(self.root, self.control)
        atoms, scopes = reader.capture()

        self.assertIn(source.relative_to(self.root).as_posix(), {row["source_path"] for row in atoms})
        self.assertEqual(len(scopes), len(self.declarations))
        self.assertEqual("DEMO-SU-00", scopes[0]["scope_unit_id"])
        self.assertEqual("fixture", scopes[0]["name"])


    def test_project_scope_id_requires_configured_prefix(self) -> None:
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.settings_context__pub import ProjectSettingsValueError

        (self.control / "anechoic_project_settings.toml").unlink()
        with self.assertRaisesRegex(ProjectSettingsValueError, "current Project Settings") as raised:
            SourceReader(self.root, self.control).capture()
        self.assertEqual("project-settings-unavailable", raised.exception.code)


    def test_move_remove_and_capture_do_not_write_sources(self) -> None:
        source = self._write_atom("MAIN", "07_delivery", "moving.md", atom_id="CA-R-430")
        before = self._snapshot_files()
        atoms, _scopes, stderr = self._capture()
        self.assertEqual(stderr, "")
        self.assertIn("CA-R-430", {row["id"] for row in atoms})
        self.assertEqual(self._snapshot_files(), before)

        destination = self._path("MAIN", "09_operations", "moved.md")
        source.rename(destination)
        atoms, _scopes, stderr = self._capture()
        paths = {row["source_path"] for row in atoms}
        self.assertEqual(stderr, "")
        self.assertIn(destination.relative_to(self.root).as_posix(), paths)
        self.assertNotIn(source.relative_to(self.root).as_posix(), paths)

        destination.unlink()
        atoms, _scopes, stderr = self._capture()
        self.assertEqual(stderr, "")
        self.assertNotIn("CA-R-430", {row["id"] for row in atoms})
        self.assertEqual(
            {path: content for path, content in self._snapshot_files().items() if path != destination},
            {path: content for path, content in before.items() if path != source},
        )


    def test_watcher_changes_update_only_affected_sources(self) -> None:
        source = self._write_atom("MAIN", "07_delivery", "changing.md", atom_id="CA-R-440")
        self._capture()
        source.write_text(
            source.read_text(encoding="utf-8").replace("version: 1", "version: 2"),
            encoding="utf-8",
        )
        created = self._write_atom("MAIN", "07_delivery", "created.md", atom_id="CA-R-441")
        renamed = self._path("MAIN", "09_operations", "renamed.md")

        with (
            patch.object(
                source_reader_capture,
                "read_scope_unit_declarations",
                wraps=source_reader_capture.read_scope_unit_declarations,
            ) as declarations,
            patch.object(self.reader, "_inventory_paths", wraps=self.reader._inventory_paths) as inventory,
        ):
            atoms, _scopes = self.reader.capture([{
                "operation": "update", "old_path": None,
                "new_path": source.relative_to(self.root).as_posix(),
            }])
            self.assertEqual(2, next(row["version"] for row in atoms if row["id"] == "CA-R-440"))
            atoms, _scopes = self.reader.capture([{
                "operation": "create", "old_path": None,
                "new_path": created.relative_to(self.root).as_posix(),
            }])
            self.assertIn("CA-R-441", {row["id"] for row in atoms})
            source.rename(renamed)
            atoms, _scopes = self.reader.capture([{
                "operation": "rename",
                "old_path": source.relative_to(self.root).as_posix(),
                "new_path": renamed.relative_to(self.root).as_posix(),
            }])
            self.assertIn(renamed.relative_to(self.root).as_posix(), {row["source_path"] for row in atoms})
            renamed.unlink()
            atoms, _scopes = self.reader.capture([{
                "operation": "remove",
                "old_path": renamed.relative_to(self.root).as_posix(), "new_path": None,
            }])

        self.assertNotIn("CA-R-440", {row["id"] for row in atoms})
        declarations.assert_not_called()
        inventory.assert_not_called()


    def test_incremental_capture_marks_only_effective_source_changes(self) -> None:
        source = self._write_atom("MAIN", "04_requirement", "stable.md", atom_id="CA-R-442")
        self._capture()

        self.reader.capture([{
            "operation": "update", "old_path": None,
            "new_path": "unrelated.txt",
        }])
        self.assertFalse(self.reader.capture_changed)

        source.write_text(
            source.read_text(encoding="utf-8").replace("Fixture source.", "Changed source."),
            encoding="utf-8",
        )
        self.reader.capture([{
            "operation": "update", "old_path": None,
            "new_path": source.relative_to(self.root).as_posix(),
        }])
        self.assertTrue(self.reader.capture_changed)

        source.unlink()
        self.reader.capture([{
            "operation": "remove",
            "old_path": source.relative_to(self.root).as_posix(), "new_path": None,
        }])
        self.assertTrue(self.reader.capture_changed)



if __name__ == "__main__":
    unittest.main()
