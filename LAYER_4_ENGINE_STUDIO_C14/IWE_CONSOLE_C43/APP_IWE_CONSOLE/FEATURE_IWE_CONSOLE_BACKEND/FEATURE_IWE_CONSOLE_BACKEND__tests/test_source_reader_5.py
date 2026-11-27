from __future__ import annotations

from pathlib import Path
import unittest


APP_ROOT = Path(__file__).resolve().parents[3]
TOOLS_ROOT = APP_ROOT.parent / "FEATURE_PROGRAMMATIC" / "FEATURE_TOOLS"

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import ScopeDeclarationError  # noqa: E402




from IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IWE_CONSOLE_BACKEND.FEATURE_IWE_CONSOLE_BACKEND__tests._source_reader_fixture import SourceReaderFixture  # noqa: E402


class SourceReaderTests(SourceReaderFixture, unittest.TestCase):
    def test_incremental_capture_marks_invalid_content_and_full_refreshes_changed(self) -> None:
        source = self._write_atom("MAIN", "04_requirement", "invalid.md", atom_id="CA-R-443")
        self._capture()

        source.write_text(
            source.read_text(encoding="utf-8").replace("# Summary", "# Summary\n\n# Summary"),
            encoding="utf-8",
        )
        self.reader.capture([{
            "operation": "update", "old_path": None,
            "new_path": source.relative_to(self.root).as_posix(),
        }])
        self.assertTrue(self.reader.capture_changed)

        self.reader.capture()
        self.assertTrue(self.reader.capture_changed)


    def capture_header_edit(self, before: str, after: str) -> bool:
        path = self._write_atom("MAIN", "04_requirement", "typed.md", atom_id="CA-R-901")
        template = path.read_text().replace("subjects: {}", "subjects: {}\ncustom:\n  values: VALUE")
        path.write_text(template.replace("VALUE", before))
        rows, _, diagnostics = self._capture()
        self.assertEqual("", diagnostics)
        self.assertIn("CA-R-901", {row["id"] for row in rows})
        path.write_text(template.replace("VALUE", after))
        rows, _ = self.reader.capture([{
            "operation": "update", "old_path": None,
            "new_path": path.relative_to(self.root).as_posix(),
        }])
        self.assertIn("CA-R-901", {row["id"] for row in rows})
        return self.reader.capture_changed

    def test_capture_keeps_boolean_and_integer_distinct(self) -> None:
        self.assertTrue(self.capture_header_edit("[true]", "[1]"))


    def test_watcher_declaration_change_rechecks_the_declaration_snapshot(self) -> None:
        self._capture()
        declaration = Path(self.declarations["MAIN"]["declaration_path"])
        declaration.write_text(
            declaration.read_text(encoding="utf-8").replace(
                'atom_id: "CA-R-990001"',
                'atom_id: "CA-R-990001"\natom_id: "CA-R-990099"',
            ),
            encoding="utf-8",
        )

        with self.source_reads() as reads, self.assertRaises(ScopeDeclarationError):
            self.reader.capture([{
                "operation": "update", "old_path": None,
                "new_path": declaration.relative_to(self.root).as_posix(),
            }])

        self.assertEqual(1, reads.count(declaration.resolve()))


    def test_watcher_draft_declaration_does_not_recheck_current_declarations(self) -> None:
        declaration = Path(self.declarations["MAIN"]["declaration_path"])
        draft = declaration.parent / "draft" / "scope-declaration.md"
        draft.parent.mkdir()
        draft.write_text(
            declaration.read_text(encoding="utf-8")
            .replace('atom_id: "CA-R-990001"', 'atom_id: "CA-R-990001@2-draft"')
            .replace("version: 1", "version: 2")
            .replace('status: "Active"', 'status: "Draft"'),
            encoding="utf-8",
        )
        self._capture()
        draft.write_text(
            draft.read_text(encoding="utf-8").replace("version: 2", "version: 3"),
            encoding="utf-8",
        )

        with self.source_reads() as reads:
            _atoms, scopes = self.reader.capture([{
                "operation": "update", "old_path": None,
                "new_path": draft.relative_to(self.root).as_posix(),
            }])

        self.assertEqual(len(self.declarations), len(scopes))
        self.assertTrue(self.declaration_paths().isdisjoint(reads))


    def test_noop_comparison_preserves_yaml_date_and_nested_value_types(self) -> None:
        cases = [
            ("[2026-01-01]", '["2026-01-01"]'),
            ("[2026-01-01T00:00:00+00:00]", '["2026-01-01T00:00:00+00:00"]'),
            ("[true]", "[1]"),
            ("[1]", "[1.0]"),
        ]
        for before, after in cases:
            with self.subTest(before=before, after=after):
                self.assertTrue(self.capture_header_edit(before, after))
        self.assertFalse(self.capture_header_edit("[2026-01-01]", "[2026-01-01] # same value"))



if __name__ == "__main__":
    unittest.main()
