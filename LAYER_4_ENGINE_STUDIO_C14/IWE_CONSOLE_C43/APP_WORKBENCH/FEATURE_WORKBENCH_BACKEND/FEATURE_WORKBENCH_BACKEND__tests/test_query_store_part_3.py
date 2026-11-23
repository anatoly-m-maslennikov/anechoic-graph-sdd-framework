from __future__ import annotations

import datetime as dt
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


APP_ROOT = Path(__file__).resolve().parents[3]

from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import QueryStore  # noqa: E402
from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.FEATURE_WORKBENCH_BACKEND__tests.query_store_test_support import QueryStoreFixture, extension_directory


class QueryStoreTest(QueryStoreFixture, unittest.TestCase):
    def test_file_backed_warm_restart_reuses_validated_projection(self) -> None:
        with tempfile.TemporaryDirectory() as runtime:
            database = Path(runtime) / "projection.duckdb"
            options = {
                "extension_directory": extension_directory(APP_ROOT.parents[1]),
                "database_path": database, "retain_legacy": True,
                "journal_path": database, "journal_disk": True,
            }
            store = QueryStore(**options)
            store.replace([self.atom("CA-R-1")], [])
            store._connection.execute(
                "INSERT INTO work_journal VALUES ('test', 1, 'test', '2026-11-21', '{\"ok\":true}')"
            )
            store.close()
            inode = database.stat().st_ino
            warm = QueryStore(**options)
            try:
                with patch("KERNEL_MIXER_C59.query_store.insert_rows",
                           side_effect=AssertionError("Unexpected full projection write")):
                    warm.replace([self.atom("CA-R-1")], [])
                self.assertEqual([["CA-R-1"]], warm.run("SELECT reference FROM atoms")["rows"])
            finally:
                warm.close()
            changed = QueryStore(**options)
            try:
                changed.replace([self.atom("CA-R-2")], [])
                self.assertEqual([["CA-R-2"]], changed.run("SELECT reference FROM atoms")["rows"])
                self.assertEqual([{"ok": True}], changed.work_journal_events("test"))
            finally:
                changed.close(retain_projection=False)
            self.assertEqual(inode, database.stat().st_ino)

    def test_file_backed_materialized_pages_preserve_duplicate_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as runtime:
            database_path = Path(runtime) / "workbench" / "projection.duckdb"
            store = QueryStore(
                extension_directory=extension_directory(APP_ROOT.parents[1]), database_path=database_path,
            )
            try:
                result = store.run(
                    "SELECT value FROM (VALUES (1), (2), (3)) AS source(value)", page_size=2,
                )
                self._assert_materialized_pages(store, result, database_path)
                self._assert_materialized_refresh(store, result)
            finally:
                store.close()
            restarted = QueryStore(
                extension_directory=extension_directory(APP_ROOT.parents[1]), database_path=database_path,
            )
            try:
                with self.assertRaisesRegex(ValueError, "unknown query_id"):
                    restarted.page(result["query_id"], offset=0)
                self.assertEqual(
                    [[0]],
                    restarted.run(
                        "SELECT count(*) FROM information_schema.tables "
                        "WHERE table_schema = 'workbench_results' "
                        f"AND table_name = 'query_{result['query_id']}'"
                    )["rows"],
                )
            finally:
                restarted.close()

    def _assert_materialized_pages(self, store, result, database_path):
        self.assertTrue(database_path.is_file())
        self.assertEqual([[1], [2]], result["rows"])
        self.assertEqual(3, result["row_count"])
        self.assertEqual(1, result["column_count"])
        self.assertEqual(0, result["offset"])
        self.assertEqual(2, result["page_size"])
        self.assertTrue(result["has_more"])
        self.assertEqual(
            [[3]], store.page(result["query_id"], offset=2, page_size=2)["rows"],
        )
        self.assertFalse(store.page(result["query_id"], offset=2, page_size=2)["has_more"])
        boundary = store.run("SELECT range AS value FROM range(101)", page_size=100)
        self.assertEqual(100, len(boundary["rows"]))
        self.assertEqual([[100]], store.page(boundary["query_id"], offset=100)["rows"])
        duplicate = store.run("SELECT 1 AS duplicate, 2 AS duplicate")
        self.assertEqual(
            [
                {"name": "duplicate", "type": "INTEGER", "has_values": True},
                {"name": "duplicate", "type": "INTEGER", "has_values": True},
            ],
            duplicate["columns"],
        )
        self.assertEqual([[1, 2]], duplicate["rows"])
        visibility = store.run("SELECT NULL AS empty, 1 AS present")
        self.assertEqual(
            [
                {"name": "empty", "type": '"NULL"', "has_values": False},
                {"name": "present", "type": "INTEGER", "has_values": True},
            ],
            visibility["columns"],
        )

    def _assert_materialized_refresh(self, store, result):
        store.replace([self.atom("refreshed")], [])
        self.assertEqual(
            [[1], [2]], store.page(result["query_id"], offset=0, page_size=2)["rows"],
        )
        self.assertEqual(
            {
                "valid": True,
                "columns": [{"name": "value", "type": "INTEGER", "has_values": True}],
                "row_count": 3,
                "column_count": 1,
                "sql": "SELECT value FROM (VALUES (1), (2), (3)) AS source(value)",
            },
            store.check("SELECT value FROM (VALUES (1), (2), (3)) AS source(value)"),
        )
        with self.assertRaisesRegex(ValueError, "page_size"):
            store.run("SELECT 1", page_size=0)
        with self.assertRaisesRegex(ValueError, "page_size"):
            store.page(result["query_id"], offset=0, page_size=1001)
        with self.assertRaisesRegex(ValueError, "offset"):
            store.page(result["query_id"], offset=-1)

    def test_timezone_aware_values_are_delivered_as_iso_strings(self) -> None:
        result = self.store.run("SELECT TIMESTAMPTZ '2026-11-04 12:00:00+00' AS observed_at")
        self.assertEqual(
            dt.datetime(2026, 11, 4, 12, tzinfo=dt.UTC),
            dt.datetime.fromisoformat(result["rows"][0][0]),
        )
        self.assertEqual("TIMESTAMP WITH TIME ZONE", result["columns"][0]["type"])

