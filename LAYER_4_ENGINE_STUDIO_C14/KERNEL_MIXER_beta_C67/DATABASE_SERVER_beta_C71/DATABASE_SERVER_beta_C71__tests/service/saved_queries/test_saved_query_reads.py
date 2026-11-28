"""Exercise Saved SQL through the Project's private Database Server socket."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from uuid import uuid7

from ...DATABASE_SERVER_beta_C71__tests__shared import (
    BINDING,
    _generation,
    _query,
    _server,
)


AUTHOR = "workbench-saved-items"
RELATIVE = "control/journal"
FILE_ID = "01940000-0000-7000-8000-000000000001"
DISK_ID = "01940000-0000-7000-8000-000000000002"
QUERY_ID = "q_" + "a" * 32
VIEW_ID = "w_" + "b" * 32
EXACT_SQL = " \r\n SELECT 'ქართული'; -- old SQL\r\n\t"


def _event(saved_id, kind="query", **changes):
    return {
        "saved_query_id": saved_id,
        "kind": kind,
        "sql": EXACT_SQL,
        "saved_at": "9999"
        if saved_id == DISK_ID
        else "2025-12-01T00:00:00+00:00",
    } | changes


def _call(client, operation, arguments):
    return client.post(
        "/workspace",
        json=BINDING | {"operation": operation, "arguments": arguments},
    )


def _line(event):
    return json.dumps(event, ensure_ascii=False).encode("utf-8") + b"\n"


class SavedQueryReadsTest(unittest.TestCase):
    def setUp(self):
        temporary = TemporaryDirectory(dir="/tmp")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.workbench = self.root / ".anechoic_runtime/workbench"
        self.journal = self.root / RELATIVE
        self.journal.mkdir(parents=True)
        self.source = self.journal / f"{AUTHOR}-2025-12-01-part-1.ndjson"

    def server(self, mode):
        return _server(
            None,
            "--project-root",
            str(self.root),
            "--journal-storage",
            mode,
            "--journal-relative",
            RELATIVE,
        )

    def stage(self, event):
        directory = self.workbench / "journal-inbox"
        directory.mkdir(parents=True, exist_ok=True)
        carrier = directory / f"{uuid7()}.json"
        payload = {
            "author": AUTHOR,
            "local_date": "2025-12-01",
            "event": event,
        }
        carrier.write_text(
            json.dumps(
                payload,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ),
            encoding="utf-8",
        )
        return carrier

    def result(self, response):
        self.assertEqual(200, response.status_code, response.text)
        return response.json()["result"]

    def test_both_sources_remain_available_after_switching_journal_mode(self):
        initial = _line(
            _event(FILE_ID, "worksheet", name=" historical view ")
        ) + _line({"wrong": "shape"})
        self.source.write_bytes(initial)
        carrier = self.stage(_event(DISK_ID))
        with self.server("duckdb") as client:
            self.result(client.put("/generation", json=_generation()))
            self.assertEqual(
                [[1]],
                self.result(
                    _query(client, "SELECT count(*) FROM work_journal")
                )["rows"],
            )
            self.assertFalse(carrier.exists())
            self.assert_saved_journal_items(client)
            pending = self.stage(_event(str(uuid7())))
            pending_bytes = pending.read_bytes()
            self.assert_saved_journal_items(client)
            self.assertEqual(pending_bytes, pending.read_bytes())
        native = self.root / ".anechoic_runtime/db/project.duckdb"
        native_bytes = native.read_bytes()
        self.assert_file_mode(initial)
        self.assertEqual(native_bytes, native.read_bytes())
        with self.server("duckdb") as client:
            self.assert_saved_journal_items(client)
        self.assertEqual(pending_bytes, pending.read_bytes())
        self.assertEqual(initial, self.source.read_bytes())

    def assert_file_mode(self, initial):
        with self.server("files") as client:
            self.result(client.put("/generation", json=_generation()))
            self.assertEqual(
                [[2]],
                self.result(
                    _query(client, "SELECT count(*) FROM work_journal")
                )["rows"],
            )
            self.assertEqual(
                400,
                _query(
                    client, "SELECT event FROM journal_store.main.work_journal"
                ).status_code,
            )
            self.assert_saved_journal_items(client)
            self.source.write_bytes(
                initial + _line(_event(DISK_ID, sql="SELECT 99"))
            )
            conflict = _call(client, "query_load", {"reference": DISK_ID})
            self.assertEqual(400, conflict.status_code, conflict.text)
            self.assertIn("conflicting saved query ID", conflict.text)
            self.source.write_bytes(initial)

    def assert_saved_journal_items(self, client):
        loaded = self.result(
            _call(client, "query_load", {"reference": FILE_ID})
        )
        self.assertEqual(
            _event(FILE_ID, "view", name=" historical view "), loaded
        )
        self.assertEqual(
            _event(DISK_ID),
            self.result(_call(client, "query_load", {"reference": DISK_ID})),
        )
        items = self.result(_call(client, "query_saved_list", {"limit": 2}))[
            "items"
        ]
        self.assertEqual(
            [DISK_ID, FILE_ID], [item["saved_query_id"] for item in items]
        )
        self.assertEqual(" historical view ", items[1]["name"])
        self.assertEqual(["query", "view"], [item["kind"] for item in items])
        self.assertTrue(
            all(
                "sql" not in item
                and item["preview"] == "SELECT 'ქართული'; -- old SQL"
                for item in items
            )
        )
        self.assertEqual(
            [], self.result(_call(client, "query_log_list", {}))["items"]
        )

    def test_legacy_cache_exact_sql_and_guarded_reads(self):
        cache = self.workbench / "saved_queries"
        cache.mkdir(parents=True)
        query, view = cache / f"{QUERY_ID}.sql", cache / f"{VIEW_ID}.json"
        query.write_bytes(EXACT_SQL.encode("utf-8"))
        view.write_bytes(json.dumps({"sql": EXACT_SQL}).encode("utf-8"))
        invalid = "q_" + "c" * 32
        (cache / f"{invalid}.sql").symlink_to(query)
        before = {path: path.read_bytes() for path in (query, view)}
        with self.server("files") as client:
            for saved_id, kind in ((QUERY_ID, "query"), (VIEW_ID, "view")):
                loaded = self.result(
                    _call(client, "query_load", {"reference": saved_id})
                )
                self.assertEqual(
                    {
                        "saved_query_id": saved_id,
                        "kind": kind,
                        "sql": EXACT_SQL,
                    },
                    loaded,
                )
            self.assertEqual(
                400,
                _call(
                    client, "query_load", {"reference": invalid}
                ).status_code,
            )
            items = self.result(_call(client, "query_saved_list", {}))["items"]
            self.assertEqual(
                {QUERY_ID, VIEW_ID}, {item["saved_query_id"] for item in items}
            )
            self.assertTrue(
                all("sql" not in item and "saved_at" in item for item in items)
            )
        self.assertEqual(before, {path: path.read_bytes() for path in before})
        self.assertTrue((cache / f"{invalid}.sql").is_symlink())

    def test_list_bounds_and_invalid_rows(self):
        rows = b"invalid json\n" + _line({"wrong": "shape"})
        rows += b"".join(
            _line(_event(str(uuid7()), sql="x" * 149 + "   y"))
            for _ in range(21)
        )
        self.source.write_bytes(rows)
        with self.server("files") as client:
            for limit in (True, False, "20", 0, 1001):
                self.assertEqual(
                    400,
                    _call(
                        client, "query_saved_list", {"limit": limit}
                    ).status_code,
                )
            self.assertEqual(
                400,
                _call(
                    client, "query_load", {"reference": "../foreign"}
                ).status_code,
            )
            items = self.result(_call(client, "query_saved_list", {}))["items"]
            self.assertEqual(20, len(items))
            self.assertTrue(
                all(
                    "sql" not in item and item["preview"] == "x" * 149 + " "
                    for item in items
                )
            )
            self.assertEqual(
                21,
                len(
                    self.result(
                        _call(client, "query_saved_list", {"limit": 1000})
                    )["items"]
                ),
            )
        self.assertEqual(rows, self.source.read_bytes())

    def test_journal_record_keeps_legacy_normalization(self):
        event = _event(FILE_ID, "worksheet", name="  ")
        malformed = [
            _event(str(uuid7())) | changes
            for changes in ({"extra": 1}, {"name": 1}, {"sql": None})
        ]
        self.source.write_bytes(b"".join(map(_line, [event, *malformed])))
        with self.server("files") as client:
            self.assertEqual(
                _event(FILE_ID, "view"),
                self.result(
                    _call(client, "query_load", {"reference": FILE_ID})
                ),
            )
            items = self.result(_call(client, "query_saved_list", {}))["items"]
            self.assertEqual(
                [FILE_ID], [item["saved_query_id"] for item in items]
            )
