"""Plain Journal append/read behavior, without first-change or receipt policy."""

from __future__ import annotations

import copy
import json
import os
import sys
import tempfile
import unittest
import uuid
from contextlib import chdir
from pathlib import Path
from unittest.mock import patch

TOOLS = Path(__file__).resolve().parents[2]
PROJECT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(TOOLS))

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (  # noqa: E402
    append_record, append_sealed_events, configured_journal_root, journal_inbox, journal_storage,
)


def read_records(directory: Path) -> list[object]:
    def order(path: Path) -> tuple[str, int]:
        partition, _, part = path.stem.rpartition("-part-")
        return partition, int(part) if partition and part.isdecimal() else 0
    return [record for path in sorted(directory.glob("*.ndjson"), key=order)
            for record in (json.loads(line) for line in path.read_text(encoding="utf-8").splitlines())]


class PlainJournalTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary_root = PROJECT / ".anechoic_tmp/tests/work_journal_plain_append"
        temporary_root.mkdir(parents=True, exist_ok=True)
        temporary = tempfile.TemporaryDirectory(dir=temporary_root)
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        control = self.root / ".anechoic_anechoic"
        control.mkdir()
        (control / "anechoic_project_settings.toml").write_text(
            '[paths]\ncontrol_root = ".anechoic_anechoic"\n'
            'journal_root = ".anechoic_anechoic/_journal"\n',
            encoding="utf-8",
        )
        self.partition = {"author": "observer", "local_date": "2026-10-14", "timezone": "UTC"}
        self.directory = control / "_journal"

    def append(self, rows: list[object]) -> list[dict]:
        return append_sealed_events(self.root, rows, **self.partition)

    def test_append_and_read_preserve_input_order_and_content(self) -> None:
        rows = [{"custom": "first\nline", "nested": ["Ω", {"value": 7}]}, {"custom": "second"}]
        original = copy.deepcopy(rows)
        locations = self.append(rows)
        self.assertEqual(rows, read_records(self.directory))
        self.assertEqual(original, rows)
        self.assertEqual([1, 2], [row["line"] for row in locations])
        self.assertEqual([None, None], [row["event_id"] for row in locations])

    def test_later_append_extends_stored_rows_in_order(self) -> None:
        first, second = [{"value": 1}], [{"value": 2}, {"value": 3}]
        self.append(first)
        self.append(second)
        self.assertEqual(first + second, read_records(self.directory))

    def test_visible_control_root_discovery_and_ambiguity(self) -> None:
        visible = self.root / "_anechoic_anechoic"
        (self.root / ".anechoic_anechoic").rename(visible)
        settings = visible / "anechoic_project_settings.toml"
        settings.write_text(settings.read_text().replace(".anechoic_anechoic", "_anechoic_anechoic"))
        self.assertEqual(Path("_anechoic_anechoic/_journal"), configured_journal_root(self.root))
        self.append([{"visible": True}])
        self.assertEqual([{"visible": True}], read_records(visible / "_journal"))
        other = self.root / ".anechoic_other"
        other.mkdir()
        (other / "anechoic_project_settings.toml").write_text('[paths]\ncontrol_root = ".anechoic_other"\n')
        with self.assertRaisesRegex(RuntimeError, "missing or ambiguous"):
            configured_journal_root(self.root)
        self.assertEqual(Path("_anechoic_anechoic/_journal"),
                         configured_journal_root(self.root, control_root="_anechoic_anechoic"))

    def test_storage_setting_defaults_and_validation(self) -> None:
        self.assertEqual("files", journal_storage({}))
        self.assertEqual("duckdb", journal_storage({"runtime": {"journal": {"storage": "duckdb"}}}))
        for value in (None, "invalid", [], {}):
            with self.subTest(value=value), self.assertRaises(ValueError):
                journal_storage({"runtime": {"journal": {"storage": value}}})

    def test_disk_inbox_keeps_duplicate_records_in_order(self) -> None:
        rows = [{"value": 1}, {"value": 1}, {"value": 2}]
        legacy = self.root / ".anechoic_runtime/workbench"
        legacy.mkdir(parents=True)
        with chdir(self.root / ".anechoic_anechoic"):
            receipts = append_sealed_events(
                self.root, rows, **self.partition, storage="duckdb",
            )
        inbox = journal_inbox(self.root)
        self.assertEqual(legacy / "journal-inbox", inbox)
        self.assertFalse(legacy.with_name("iwe_console").exists())
        files = sorted(inbox.glob("*.json"))
        self.assertEqual([receipt["record_id"] for receipt in receipts], [path.stem for path in files])
        self.assertEqual(rows, [json.loads(path.read_text())["event"] for path in files])
        self.assertEqual(3, len({path.stem for path in files}))
        for path, receipt, row in zip(files, receipts, rows):
            self.assertEqual(7, uuid.UUID(path.stem).version)
            self.assertEqual(0o600, path.stat().st_mode & 0o777)
            self.assertEqual({"author": "observer", "local_date": "2026-10-14", "event": row},
                             json.loads(path.read_text()))
            self.assertEqual(".anechoic_runtime/db/project.duckdb", receipt["carrier"])
            self.assertEqual("staged", receipt["status"])
            self.assertNotIn("line", receipt)
        self.assertFalse(self.directory.exists())

    def test_disk_inbox_rejects_symlink_directory(self) -> None:
        outside = self.root / "outside"
        outside.mkdir()
        (self.root / ".anechoic_runtime").symlink_to(outside, target_is_directory=True)
        with self.assertRaises(OSError) as caught:
            append_sealed_events(self.root, [{}], **self.partition, storage="duckdb")
        self.assertEqual("journal-append-incomplete", caught.exception.code)
        self.assertEqual([], list(outside.iterdir()))

    def test_disk_failure_reports_completed_receipts(self) -> None:
        inbox = journal_inbox(self.root)
        publish = os.rename

        def fail_second_publish(source, destination, **kwargs):
            if any(inbox.glob("*.json")):
                raise OSError("failed")
            return publish(source, destination, **kwargs)

        with patch.object(os, "rename", side_effect=fail_second_publish):
            with self.assertRaises(OSError) as caught:
                append_sealed_events(self.root, [1, 2], **self.partition, storage="duckdb")
        self.assertEqual("journal-append-incomplete", caught.exception.code)
        self.assertEqual(1, len(caught.exception.completed_receipts))
        self.assertEqual(1, caught.exception.uncertain_event_index)
        records = list(inbox.iterdir())
        self.assertEqual(1, len(records))
        self.assertEqual(1, json.loads(records[0].read_text())["event"])

    def test_duplicate_rows_and_reused_ids_are_not_filtered(self) -> None:
        row = {"event_id": "same-id", "value": "original", "event_digest": "supplied-value"}
        changed = {**row, "value": "different"}
        self.append([row, row])
        self.append([changed])
        self.assertEqual([row, row, changed], read_records(self.directory))

    def test_missing_prior_history_does_not_block_append(self) -> None:
        rows = [{"action_type": "UPDATE"}, {"action_type": "MOVE+UPDATE"}]
        self.append(rows)
        self.assertEqual(rows, read_records(self.directory))
        self.assertFalse((self.root / ".anechoic_runtime").exists())

    def test_read_returns_stored_json_values_without_shape_filtering(self) -> None:
        rows = [5, "stored string", ["stored", "list"], {"unknown": True}]
        self.directory.mkdir()
        (self.directory / "observer-2026-10-14-part-1.ndjson").write_text(
            "".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8"
        )
        self.assertEqual(rows, read_records(self.directory))

    def test_scalar_and_list_rows_append_without_shape_gate(self) -> None:
        rows = [5, "stored string", ["stored", "list"]]
        locations = self.append(rows)
        self.assertEqual(rows, read_records(self.directory))
        self.assertEqual([None] * len(rows), [row["event_id"] for row in locations])

    def test_partition_components_stay_inside_selected_journal_directory(self) -> None:
        row = {"author": "team/operator", "value": "unchanged"}
        locations = append_sealed_events(
            self.root, [row], author=row["author"], local_date="2026/10/14", timezone="UTC"
        )
        path = self.root / locations[0]["carrier"]
        self.assertEqual(self.directory, path.parent)
        self.assertIn("team%2Foperator-2026%2F10%2F14", path.name)
        self.assertEqual([row], read_records(self.directory))

    def test_empty_read_creates_no_journal_files(self) -> None:
        self.assertEqual([], read_records(self.directory))
        self.assertFalse(self.directory.exists())

    def test_declared_row_rotation_preserves_append_order(self) -> None:
        rows = [{"row": number} for number in range(1001)]
        locations = self.append(rows)
        self.assertEqual(rows, read_records(self.directory))
        self.assertEqual((1000, 1), (locations[999]["line"], locations[1000]["line"]))
        self.assertNotEqual(locations[999]["carrier"], locations[1000]["carrier"])

    def test_numeric_parts_read_in_numeric_order(self) -> None:
        self.directory.mkdir()
        for number in range(1, 13):
            (self.directory / f"observer-2026-10-14-part-{number}.ndjson").write_text(
                json.dumps({"part": number}) + "\n", encoding="utf-8"
            )
        self.assertEqual(
            [{"part": number} for number in range(1, 13)], read_records(self.directory)
        )

    def test_legacy_append_caps_new_parts_and_preserves_old_date_carrier(self) -> None:
        self.directory.mkdir()
        old = self.directory / "src-work-journal-2026-10-14.ndjson"
        original = b'{"retained": "old date carrier"}\n'
        old.write_bytes(original)
        rows = [{"occurred_at": "2026-10-14 01:02:03 +0000", "row": number,
                 "custom": ["unchanged", number]} for number in range(1001)]
        locations = [append_record(self.root, row) for row in rows]
        parts = sorted(self.directory.glob("src-work-journal-2026-10-14-part-*.ndjson"))
        self.assertEqual([1000, 1], [len(path.read_bytes().splitlines()) for path in parts])
        self.assertEqual(parts[0], locations[999])
        self.assertEqual(parts[1], locations[1000])
        self.assertEqual(original, old.read_bytes())
        self.assertEqual([{"retained": "old date carrier"}, *rows], read_records(self.directory))

    def test_leaf_symlink_cannot_read_or_append_outside_journal(self) -> None:
        self.directory.mkdir()
        outside = self.root / "outside.ndjson"
        original = b'{"outside": "unchanged"}\n'
        outside.write_bytes(original)
        (self.directory / "observer-2026-10-14-part-1.ndjson").symlink_to(outside)
        with self.assertRaises(OSError):
            self.append([{"new": True}])
        self.assertEqual(original, outside.read_bytes())

    def test_actual_filesystem_failure_is_reported(self) -> None:
        self.directory.write_text("occupied by a file", encoding="utf-8")
        with self.assertRaises(OSError):
            self.append([{"value": "not appended"}])
        self.assertEqual("occupied by a file", self.directory.read_text(encoding="utf-8"))

    def test_legacy_append_reports_fsync_failure_after_writing_unchanged_row(self) -> None:
        row = {"occurred_at": "2026-10-14 01:02:03 +0000", "unchanged": True}
        with patch.object(os, "fsync", side_effect=OSError("sync unavailable")):
            with self.assertRaisesRegex(OSError, "sync unavailable"):
                append_record(self.root, row)
        self.assertEqual([row], read_records(self.directory))

if __name__ == "__main__":
    unittest.main()
