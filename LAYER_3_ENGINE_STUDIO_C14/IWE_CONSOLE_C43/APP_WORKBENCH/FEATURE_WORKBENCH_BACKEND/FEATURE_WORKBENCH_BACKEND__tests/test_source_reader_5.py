from __future__ import annotations

from pathlib import Path
import unittest
from unittest.mock import patch


APP_ROOT = Path(__file__).resolve().parents[3]
TOOLS_ROOT = APP_ROOT.parent / "FEATURE_PROGRAMMATIC" / "FEATURE_TOOLS"

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.scope_carrier__pub import ScopeDeclarationError  # noqa: E402
from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND import source_reader_capture  # noqa: E402
from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.source_rows import same_row as _same_row  # noqa: E402




from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.FEATURE_WORKBENCH_BACKEND__tests._source_reader_fixture import SourceReaderFixture  # noqa: E402


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


    def test_same_row_keeps_boolean_and_integer_distinct(self) -> None:
        before = ((1,), {"header_json": {"enabled": True}})
        after = ((2,), {"header_json": {"enabled": 1}})

        self.assertFalse(_same_row(before, after))


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

        with patch.object(
            source_reader_capture,
            "read_scope_unit_declarations",
            wraps=source_reader_capture.read_scope_unit_declarations,
        ) as declarations, self.assertRaises(ScopeDeclarationError):
            self.reader.capture([{
                "operation": "update", "old_path": None,
                "new_path": declaration.relative_to(self.root).as_posix(),
            }])

        declarations.assert_called_once()


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

        with patch.object(
            source_reader_capture,
            "read_scope_unit_declarations",
            wraps=source_reader_capture.read_scope_unit_declarations,
        ) as declarations:
            _atoms, scopes = self.reader.capture([{
                "operation": "update", "old_path": None,
                "new_path": draft.relative_to(self.root).as_posix(),
            }])

        self.assertEqual(len(self.declarations), len(scopes))
        declarations.assert_not_called()


    def test_noop_comparison_preserves_yaml_date_and_nested_value_types(self) -> None:
        import datetime as dt
        from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.source_rows import same_row
        cases = [
            (dt.date(2026, 1, 1), "2026-01-01"),
            (dt.datetime(2026, 1, 1, tzinfo=dt.UTC), "2026-01-01T00:00:00+00:00"),
            (True, 1),
            (1, 1.0),
        ]
        for before, after in cases:
            with self.subTest(before=before, after=after):
                self.assertFalse(same_row(((1,), {"header": {"values": [before]}}), ((2,), {"header": {"values": [after]}})))
        self.assertTrue(same_row(((1,), {"value": cases[0][0]}), ((2,), {"value": cases[0][0]})))



if __name__ == "__main__":
    unittest.main()
