"""Exercise the durable Work Journal through the real Database Server socket."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from uuid import uuid7

from .DATABASE_SERVER_beta_C71__tests__shared import _generation, _query, _server


ROWS = "SELECT record_id, position, author, local_date FROM work_journal ORDER BY position"


def _stage(path, event):
    record = {"author": "test-author", "local_date": "2026-11-22", "event": event}
    path.write_text(json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":")), encoding="utf-8")


class WorkJournalTest(unittest.TestCase):
    def test_journal_survives_restart_with_either_projection_storage(self):
        for in_memory in (True, False):
            with self.subTest(in_memory=in_memory), TemporaryDirectory(dir="/tmp") as directory:
                root = Path(directory).resolve()
                projection = None if in_memory else root / "beta.duckdb"
                arguments = (projection, "--project-root", str(root), "--journal-storage", "duckdb")
                self.assert_import_restart(root, arguments)

    def assert_import_restart(self, root, arguments):
        inbox = root / ".anechoic_runtime/workbench/journal-inbox"
        inbox.mkdir(parents=True, mode=0o700)
        record = uuid7()
        source = inbox / f"{record}.json"
        _stage(source, {"value": 1})
        expected = [[str(record), 1, "test-author", "2026-11-22"]]
        with _server(*arguments) as client:
            self.assertEqual(200, client.put("/generation", json=_generation()).status_code)
            self.assert_rows(client, expected)
            self.assertFalse(source.exists())
            self.assertEqual(400, _query(client, "DELETE FROM work_journal").status_code)
            self.assertEqual(400, _query(client, "SELECT * FROM read_csv('/etc/passwd')").status_code)
        with _server(*arguments) as client:
            self.assertEqual(200, client.put("/generation", json=_generation()).status_code)
            _stage(source, {"value": 1})
            self.assert_rows(client, expected)
            self.assertFalse(source.exists())
            _stage(source, {"value": 2})
            collision = _query(client, ROWS)
            self.assertEqual(400, collision.status_code, collision.text)
            self.assertIn("identity collision", collision.text)
            self.assertTrue(source.is_file())
            source.unlink()
            self.assert_rows(client, expected)

    def assert_rows(self, client, expected):
        response = _query(client, ROWS)
        self.assertEqual(200, response.status_code, response.text)
        self.assertEqual(expected, response.json()["result"]["rows"])


class FileJournalTest(unittest.TestCase):
    def test_reopen_and_refresh_files_with_memory_and_disk_projection(self):
        for in_memory in (True, False):
            with self.subTest(in_memory=in_memory), TemporaryDirectory(dir="/tmp") as directory:
                root = Path(directory).resolve()
                journal = root / "custom/journal"
                journal.mkdir(parents=True)
                (journal / "alice-2026-11-22-part-1.ndjson").write_text('{"kind":"first"}\n{"kind":"second"}\n')
                db = None if in_memory else root / "projection.db"
                args = (db, "--project-root", str(root), "--journal-relative", "custom/journal")
                for iteration in range(2):
                    with _server(*args) as client:
                        self.assertEqual(200, client.put("/generation", json=_generation()).status_code)
                        self.assert_file_rows(client, 2 + iteration)
                        if not iteration:
                            (journal / "bob-2026-11-23-part-1.ndjson").write_text('{"kind":"third"}\n')
                            self.assert_file_rows(client, 3)

    def assert_file_rows(self, client, count):
        result = _query(client, "SELECT author, local_date, event FROM work_journal ORDER BY position")
        self.assertEqual(200, result.status_code, result.text)
        rows = result.json()["result"]["rows"]
        self.assertEqual(count, len(rows))
        self.assertEqual(["alice", "2026-11-22"], rows[0][:2])
        self.assertEqual("first", json.loads(rows[0][2])["kind"])

    def test_invalid_content_and_symlink_fail_closed(self):
        with TemporaryDirectory(dir="/tmp") as directory:
            root = Path(directory).resolve()
            journal = root / "custom/journal"
            journal.mkdir(parents=True)
            carrier = journal / "alice-2026-11-22-part-1.ndjson"
            carrier.write_text('{"kind":"first"}\n')
            with _server(None, "--project-root", str(root), "--journal-relative", "custom/journal") as client:
                self.assertEqual(200, client.put("/generation", json=_generation()).status_code)
                self.assert_file_rows(client, 1)
                carrier.write_text("invalid\n")
                self.assertEqual(409, _query(client, ROWS).status_code)
                carrier.unlink()
                carrier.symlink_to(root / "outside")
                self.assertEqual(409, _query(client, ROWS).status_code)
                carrier.unlink()
                carrier.write_text('{"kind":"first"}\n')
                self.assert_file_rows(client, 1)

    def test_unsafe_relative_path_refused_at_startup(self):
        with TemporaryDirectory(dir="/tmp") as directory:
            root = Path(directory).resolve()
            with self.assertRaisesRegex(AssertionError, "Database did not start"):
                with _server(None, "--project-root", str(root), "--journal-relative", "../foreign"):
                    self.fail("unsafe Journal path was accepted")
