"""Check the durable Saved SQL record through both private Journal bindings."""

from datetime import UTC, datetime, timedelta
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from uuid import UUID, uuid7

from .DATABASE_SERVER_beta_C71__tests__shared import (
    BINDING,
    _generation,
    _query,
    _server,
)


SQL = " \r\n SELECT 'ქართული' AS value; -- keep formatting\r\n\t"
NAME = " Example name "
AUTHOR = "workbench-saved-items"
JOURNAL = "control/journal"


class SavedQueryWriteTests(unittest.TestCase):
    def test_file_journal_appends_after_full_part_and_reopens(self):
        with TemporaryDirectory(dir="/tmp") as directory:
            root = Path(directory).resolve()
            journal = root / JOURNAL
            journal.mkdir(parents=True)
            now = datetime.now(UTC)
            earlier = {
                "saved_query_id": str(uuid7()),
                "kind": "query",
                "sql": "SELECT 1",
                "saved_at": now.isoformat(),
            }
            previous = (json.dumps(earlier) + "\n").encode() * 1000
            full = [
                journal
                / f"{AUTHOR}-{now.date() + timedelta(days=day)}-part-1.ndjson"
                for day in (0, 1)
            ]
            for carrier in full:
                carrier.write_bytes(previous)
            arguments = (
                None,
                "--project-root",
                str(root),
                "--journal-relative",
                JOURNAL,
            )
            with _server(*arguments) as client:
                saved = self.save_and_read(client)
            for carrier in full:
                self.assertEqual(previous, carrier.read_bytes())
            (successor,) = (
                (journal / f"{AUTHOR}-{saved['saved_at'][:10]}-part-2.ndjson")
                .read_bytes()
                .splitlines()
            )
            self.assertEqual(saved, json.loads(successor))
            with _server(*arguments) as client:
                self.assertEqual(
                    saved, self.load(client, saved["saved_query_id"])
                )
                self.assertEqual(
                    earlier, self.load(client, earlier["saved_query_id"])
                )

    def test_duckdb_journal_commits_immediately_and_reopens(self):
        with TemporaryDirectory(dir="/tmp") as directory:
            root = Path(directory).resolve()
            arguments = (
                None,
                "--project-root",
                str(root),
                "--journal-storage",
                "duckdb",
            )
            with _server(*arguments) as client:
                saved = self.save_and_read(client)
                events = _query(
                    client, "SELECT author, event FROM work_journal"
                )
                self.assertEqual(200, events.status_code, events.text)
                ((author, event),) = events.json()["result"]["rows"]
                self.assertEqual((AUTHOR, saved), (author, json.loads(event)))
            self.assertFalse(
                (root / ".anechoic_runtime/iwe_console/journal-inbox").exists()
            )
            with _server(*arguments) as client:
                self.assertEqual(
                    saved, self.load(client, saved["saved_query_id"])
                )

    def save_and_read(self, client):
        response = client.put("/generation", json=_generation())
        self.assertEqual(200, response.status_code, response.text)
        run = _query(client, SQL, page_size=1, save=True, name=NAME)
        self.assertEqual(200, run.status_code, run.text)
        saved_id = run.json()["result"]["saved_query_id"]
        self.assertEqual(
            (7, saved_id), (UUID(saved_id).version, str(UUID(saved_id)))
        )
        saved = self.load(client, saved_id)
        self.assertEqual(
            {
                "saved_query_id": saved_id,
                "kind": "query",
                "sql": SQL,
                "name": NAME,
                "saved_at": saved["saved_at"],
            },
            saved,
        )
        self.assertEqual(
            UTC.utcoffset(None),
            datetime.fromisoformat(saved["saved_at"]).utcoffset(),
        )
        return saved

    def load(self, client, saved_id):
        response = client.post(
            "/workspace",
            json=BINDING
            | {
                "operation": "query_load",
                "arguments": {"reference": saved_id},
            },
        )
        self.assertEqual(200, response.status_code, response.text)
        return response.json()["result"]
