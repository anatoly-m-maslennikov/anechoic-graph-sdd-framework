from __future__ import annotations

from contextlib import redirect_stderr
from io import StringIO
import unittest
from pathlib import Path


APP_ROOT = Path(__file__).resolve().parents[3]

from KERNEL_MIXER_C59.errors import (  # noqa: E402
    QueryExecutionError,
    WorkbenchUnavailableError,
)
from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.FEATURE_WORKBENCH_BACKEND__tests.query_store_test_support import QueryStoreFixture
from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.FEATURE_WORKBENCH_BACKEND__tests.query_store_test_support import extension_directory as extension_directory


class QueryStoreTest(QueryStoreFixture, unittest.TestCase):
    def test_rebuild_stages_until_commit_and_preserves_preview_and_pin(self) -> None:
        old = self.store.run("SELECT * FROM range(5)", preview=2)["query_id"]
        self.store.pin(old)
        self.store._connection.execute("BEGIN")
        staged = self.store.prepare_result_rebuild(old)
        self.store._connection.execute("ROLLBACK")
        self.assertEqual(2, self.store.page(old, 0)["row_count"])
        self.store._connection.execute("BEGIN")
        staged = self.store.prepare_result_rebuild(old)
        self.store._connection.execute("COMMIT")
        replacements = self.store.commit_result_rebuild(staged)
        new = replacements[old]["query_id"]
        self.assertNotEqual(old, new)
        self.assertEqual(2, self.store.page(new, 0)["row_count"])
        self.assertTrue(self.store._results[new].pinned)
        with self.assertRaises(ValueError):
            self.store.page(old, 0)

    def test_rebuild_updates_dependent_results_and_keeps_physical_name(self) -> None:
        self.store._connection.execute("CREATE TABLE source_values (value INTEGER)")
        self.store._connection.execute("INSERT INTO source_values VALUES (1)")
        first = self.store.run("SELECT value FROM source_values")["query_id"]
        second = self.store.run(f"SELECT value FROM workbench_results.query_{first}")["query_id"]
        self.store._connection.execute("UPDATE source_values SET value = 2")
        self.store._connection.execute("BEGIN")
        staged = self.store.prepare_result_rebuild(first)
        self.store._connection.execute("COMMIT")
        replacements = self.store.commit_result_rebuild(staged)
        new_first = replacements[first]["query_id"]
        new_second = replacements[second]["query_id"]
        self.assertEqual([[2]], self.store.page(new_second, 0)["rows"])
        self.assertEqual(new_first, self.store.resolve_result_selector(f"workbench_results.query_{first}"))
        self.store._connection.execute("UPDATE source_values SET value = 3")
        self.store._connection.execute("BEGIN")
        staged = self.store.prepare_result_rebuild()
        self.store._connection.execute("ROLLBACK")
        self.assertEqual([[2]], self.store.page(new_second, 0)["rows"])
        self.store._connection.execute("BEGIN")
        staged = self.store.prepare_result_rebuild()
        self.store._connection.execute("COMMIT")
        replacements = self.store.commit_result_rebuild(staged)
        self.assertEqual([[3]], self.store.page(replacements[new_second]["query_id"], 0)["rows"])

    def test_rebuild_dependency_failure_can_roll_back(self) -> None:
        self.store._connection.execute("CREATE TABLE source_fail (value INTEGER)")
        self.store._connection.execute("INSERT INTO source_fail VALUES (1)")
        first = self.store.run("SELECT * FROM source_fail")["query_id"]
        second = self.store.run(f"SELECT value FROM workbench_results.query_{first}")["query_id"]
        self.store._connection.execute("ALTER TABLE source_fail RENAME value TO changed")
        self.store._connection.execute("BEGIN")
        with self.assertRaises(QueryExecutionError):
            self.store.prepare_result_rebuild(first)
        self.store._connection.execute("ROLLBACK")
        self.assertEqual([[1]], self.store.page(first, 0)["rows"])
        self.assertEqual([[1]], self.store.page(second, 0)["rows"])

    def test_expiry_retains_transitive_sources_until_last_dependent_expires(self) -> None:
        first = self.store.run("SELECT 1 AS value")["query_id"]
        second = self.store.run(f"SELECT value FROM workbench_results.query_{first}")["query_id"]
        third = self.store.run(f"SELECT value FROM workbench_results.query_{second}")["query_id"]
        self.store._results[first].created_at -= 4000
        self.store._results[second].created_at -= 4000
        self.store.prune_results()
        self.assertEqual([[1]], self.store.page(third, 0)["rows"])
        self.store._connection.execute("BEGIN")
        staged = self.store.prepare_result_rebuild(first)
        self.store._connection.execute("COMMIT")
        replaced = self.store.commit_result_rebuild(staged)
        third = replaced[third]["query_id"]
        self.assertEqual([[1]], self.store.page(third, 0)["rows"])
        self.store._results[third].created_at -= 4000
        self.store.prune_results()
        self.assertFalse(self.store._results)

    def test_rebuild_skips_expired_unrelated_result_without_cleanup(self) -> None:
        self.store._connection.execute("CREATE TABLE expired_source (value INTEGER)")
        expired = self.store.run("SELECT value FROM expired_source")["query_id"]
        current = self.store.run("SELECT 42 AS value")["query_id"]
        self.store._results[expired].created_at -= 4000
        self.store._connection.execute("DROP TABLE expired_source")
        self.store._connection.execute("BEGIN")
        with self.assertRaises(ValueError):
            self.store.prepare_result_rebuild(expired)
        staged = self.store.prepare_result_rebuild()
        self.store._connection.execute("COMMIT")
        replacements = self.store.commit_result_rebuild(staged)
        self.assertNotIn(expired, replacements)
        self.assertIn(expired, self.store._results)
        self.assertEqual([[42]], self.store.page(replacements[current]["query_id"], 0)["rows"])
        self.store.prune_results()
        self.assertNotIn(expired, self.store._results)

    def test_unclassified_dependencies_only_retain_named_snapshots(self) -> None:
        first = self.store.run("SELECT 1 AS value")["query_id"]
        unrelated = self.store.run("SELECT 2 AS value")["query_id"]
        connection = self.store._connection
        class UnclassifiedConnection:
            def __getattr__(self, name):
                if name == "get_table_names":
                    raise RuntimeError("cannot classify")
                return getattr(connection, name)
        self.store._connection = UnclassifiedConnection()
        try:
            dependent = self.store.run(f"SELECT value FROM workbench_results.query_{first}")["query_id"]
        finally:
            self.store._connection = connection
        self.store._results[first].created_at -= 4000
        self.store._results[unrelated].created_at -= 4000
        self.store.prune_results()
        self.assertIn(first, self.store._results)
        self.assertNotIn(unrelated, self.store._results)
        self.assertEqual([[1]], self.store.page(dependent, 0)["rows"])

    def test_rebuild_uses_cached_unclassified_dependencies(self) -> None:
        self.store._connection.execute("CREATE TABLE source_join (id INTEGER, value INTEGER)")
        self.store._connection.execute("INSERT INTO source_join VALUES (1, 10)")
        first = self.store.run("SELECT * FROM source_join")["query_id"]
        connection = self.store._connection

        class UnclassifiedConnection:
            def __getattr__(self, name):
                if name == "get_table_names":
                    return lambda _sql: connection.execute("SELECT * FROM missing_dependency_table")
                return getattr(connection, name)

        self.store._connection = UnclassifiedConnection()
        try:
            sql = (f"SELECT value FROM workbench_results.query_{first} "
                   "JOIN (SELECT 1 AS id) USING (id)")
            dependent = self.store.run(sql)["query_id"]
            self.assertTrue(self.store._results[dependent].dependencies_unknown)
            connection.execute("UPDATE source_join SET value = 20")
            connection.execute("BEGIN")
            staged = self.store.prepare_result_rebuild(first)
            connection.execute("COMMIT")
            replacements = self.store.commit_result_rebuild(staged)
            new_dependent = replacements[dependent]["query_id"]
            self.assertEqual([[20]], self.store.page(new_dependent, 0)["rows"])
            self.assertTrue(self.store._results[new_dependent].dependencies_unknown)
        finally:
            self.store._connection = connection

    def test_drop_retains_source_for_dependent_rebuild(self) -> None:
        first = self.store.run("SELECT 1 AS value")["query_id"]
        second = self.store.run(f"SELECT value FROM workbench_results.query_{first}")["query_id"]
        self.store.drop(first)
        with self.assertRaises(ValueError):
            self.store.page(first, 0)
        self.store._connection.execute("BEGIN")
        staged = self.store.prepare_result_rebuild()
        self.store._connection.execute("COMMIT")
        replacements = self.store.commit_result_rebuild(staged)
        self.assertNotIn(first, replacements)
        second = replacements[second]["query_id"]
        self.assertEqual([[1]], self.store.page(second, 0)["rows"])
        self.store.drop(second)
        self.assertFalse(self.store._results)

    def test_native_rebuild_failure_after_graph_drop_fails_closed(self) -> None:
        self.store._native = True
        self.store._connection.execute("CREATE TABLE rollback_evidence (value INTEGER)")
        self.store._connection.execute("INSERT INTO rollback_evidence VALUES (1)")
        def fail_after_drop(_graph):
            self.store.mark_graph_registration_changed()
            self.store._connection.execute("DROP PROPERTY GRAPH IF EXISTS anechoic")
            self.store._connection.execute("DELETE FROM rollback_evidence")
            raise RuntimeError("rebuild failed")
        stderr = StringIO()
        with redirect_stderr(stderr), self.assertRaises(WorkbenchUnavailableError):
            self.store.replace([], [], reuse=True, before_commit=fail_after_drop)
        self.assertIn("rebuild failed", stderr.getvalue())
        self.assertEqual([(1,)], self.store._connection.execute("SELECT * FROM rollback_evidence").fetchall())
        with self.assertRaises(WorkbenchUnavailableError):
            self.store.run("SELECT 1")

    def test_query_log_expiry_applies_to_backing_rows(self) -> None:
        self.store._connection.execute(
            "INSERT INTO query_log_records VALUES "
            "('expired', current_timestamp - INTERVAL 49 HOURS, 'SELECT 1', 'success', NULL, 1, 1)"
        )
        self.assertEqual([[0]], self.store.run("SELECT count(*) FROM query_log_records")["rows"])
        self.assertEqual([[0]], self.store.run("SELECT count(*) FROM query_log")["rows"])

