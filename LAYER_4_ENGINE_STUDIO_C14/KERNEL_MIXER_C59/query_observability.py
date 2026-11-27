"""Publish Workbench journal, diagnostics, and audit data."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .audit_tables import publish as publish_atom_audits
from .errors import WorkbenchUnavailableError
from .journal_table import journal_events, sync_journal
from .watcher_change_log import WatcherChangeLog, mirror_change_log


class QueryObservability:
    def sync_work_journal(self, root: Path) -> None:
        with self._lock:
            if self._journal_disk:
                sync_journal(
                    self._connection,
                    root,
                    self._database_path,
                    self._journal_path,
                )

    def work_journal_events(self, author: str) -> list[Any]:
        with self._lock:
            return journal_events(self._connection, author)

    def sync_change_log(
        self,
        log: WatcherChangeLog,
        events: list[dict[str, str | None]] | None = None,
        *,
        initialize: bool = False,
    ) -> None:
        """Mirror watcher history under the database-owner lock."""
        with self._lock:
            if not self._available:
                raise WorkbenchUnavailableError(
                    "query store unavailable; Workbench restart required"
                )
            try:
                mirror_change_log(
                    self._connection, log, events, initialize=initialize
                )
            except WorkbenchUnavailableError:
                self._available = False
                raise

    def record_query_attempts(self, records: list[dict[str, Any]]) -> None:
        if not records:
            return
        columns = (
            "log_id",
            "at",
            "sql",
            "outcome",
            "error",
            "row_count",
            "column_count",
        )
        with self._lock:
            self._connection.execute(
                (
                    'DELETE FROM query_log_records WHERE "at" <= '
                    "current_timestamp - INTERVAL 48 HOURS"
                )
            )
            self._connection.executemany(
                (
                    "INSERT OR REPLACE INTO query_log_records VALUES (?, ?, "
                    "?, ?, ?, ?, ?)"
                ),
                [tuple(record[key] for key in columns) for record in records],
            )

    def set_live_runs(self, rows: list[dict[str, str]]) -> None:
        values = tuple(
            (row["run_id"], row["session_id"], row["tool"], row["status"])
            for row in rows
        )
        with self._lock:
            if values == self._live_runs:
                return
            self._connection.execute("DELETE FROM live_runs")
            if values:
                self._connection.executemany(
                    "INSERT INTO live_runs VALUES (?, ?, ?, ?)",
                    values,
                )
            self._live_runs = values

    def set_runtime_diagnostics(self, rows: list[dict[str, str]]) -> None:
        columns = (
            "observed_at",
            "name",
            "outcome",
            "returned_outcome",
            "error_category",
            "project_prefix",
            "project_instance_id",
        )
        values = tuple(tuple(row.get(key) for key in columns) for row in rows)
        with self._lock:
            if values == self._diagnostic_rows:
                return
            self._connection.execute("DELETE FROM runtime_diagnostics")
            if values:
                self._connection.execute(
                    (
                        "INSERT INTO runtime_diagnostics SELECT "
                        "unnest(?::TIMESTAMPTZ[]), "
                    )
                    + ", ".join(["unnest(?::VARCHAR[])"] * (len(columns) - 1)),
                    [list(column) for column in zip(*values, strict=True)],
                )
            self._diagnostic_rows = values

    def audit_content_rows(self, paths: set[str]) -> dict:
        "Copy projected values briefly under the database lock for background audit."
        from .audit_tables import query_content_rows

        with self._lock:
            if not self._available:
                raise WorkbenchUnavailableError(
                    "query store unavailable; Workbench restart required"
                )
            return query_content_rows(self._connection, paths)

    def publish_audit(
        self, issues: dict, paths: set[str] | None, publication: Any
    ) -> bool:
        "Publish only if the audit generation remains current under the lock."
        with self._lock:
            with publication as current:
                if not current:
                    return False
                publish_atom_audits(
                    self._connection, issues, paths, available=self._available
                )
                return True
