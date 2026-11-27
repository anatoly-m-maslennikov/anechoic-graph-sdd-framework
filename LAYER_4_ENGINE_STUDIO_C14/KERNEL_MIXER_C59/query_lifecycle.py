"""Lifecycle and consistency queries over the Workbench projection."""

from __future__ import annotations

from typing import Any

from .audit_tables import TABLES as ATOM_AUDIT_TABLES, revision_query
from .graph_store import quote_identifier


class QueryLifecycle:
    def lifecycle_candidates(
        self, atom_ids=(), references=(), prefix=None, under=None
    ):
        clauses = ["regexp_full_match(atom_id, '.+-[A-Z]-[0-9]+')"]
        parameters = []
        if atom_ids:
            clauses.append("atom_id IN (SELECT unnest(?::VARCHAR[]))")
            parameters.append(list(atom_ids))
        if references:
            clauses.append("reference IN (SELECT unnest(?::VARCHAR[]))")
            parameters.append(list(references))
        if prefix is not None:
            clauses.append("starts_with(atom_id, ?)")
            parameters.append(prefix)
        if under is not None:
            clauses.append(
                "(relative_path = ? OR starts_with(relative_path, ?))"
            )
            parameters.extend((under, under.rstrip("/") + "/"))
        with self._lock:
            return self._connection.execute(
                "SELECT reference, relative_path, filename FROM (SELECT "
                "reference, relative_path, filename, "
                f"split_part(reference, '@', 1) AS atom_id FROM main.atoms "
                f"WHERE TRUE{self._native_atom_clause()}) WHERE "
                + " AND ".join(clauses)
                + " ORDER BY relative_path || '/' || filename",
                parameters,
            ).fetchall()

    def lifecycle_archive_candidates(self, atom_id: str):
        "Return exact archived references in descending numeric Version order."
        with self._lock:
            return self._connection.execute(
                "SELECT reference, relative_path, filename FROM main.atoms "
                "WHERE status_group = 'Archived' AND split_part(reference, "
                "'@', 1) = ? "
                "AND regexp_full_match(reference, '[^@]+@[1-9][0-9]*')"
                f"{self._native_atom_clause()} "
                "ORDER BY length(split_part(reference, '@', 2)) DESC, "
                "split_part(reference, '@', 2) DESC, "
                "relative_path || '/' || filename",
                [atom_id],
            ).fetchall()

    def _native_atom_clause(self) -> str:
        return "".join(
            f" AND {quote_identifier(name)} IS NULL"
            for name in self._header_schema.names
            if name == "header.projection"
            or name.startswith("header.projection.")
        )

    def lifecycle_contexts(self, reference: str) -> list[dict[str, Any]]:
        candidates = (
            "header.identity.atom_id",
            "header.identity.id",
            "header.atom_id",
            "header.identity.ref_id",
            "header.ref_id",
            "header.state.version",
            "header.state.version_number",
            "header.version",
            "header.version_number",
            "header.state.status",
            "header.status",
            "header.context.role",
            "header.role",
            "header.content_role",
            "header.context.form",
            "header.form",
            "header.type",
            "header.context.container",
            "header.container",
            "header.context.container.atom",
            "header.context.container.scope_unit",
            "header.container.atom",
            "header.container.scope_unit",
            "content.summary",
        )
        with self._lock:
            available = set(self._header_schema.names) | set(
                self._content_schema.names
            )
            names = [
                "relative_path",
                "filename",
                *(name for name in candidates if name in available),
            ]
            columns = ", ".join(map(quote_identifier, names))
            rows = self._connection.execute(
                f"SELECT {columns} FROM main.atoms WHERE status_group IN "
                f"('Current', 'Backlog') "
                f"AND reference = ?{self._native_atom_clause()} ORDER BY "
                f"relative_path || '/' || filename",
                [reference],
            ).fetchall()
        return [dict(zip(names, row, strict=False)) for row in rows]

    def lifecycle_last_id(
        self, prefix: str, *, ceiling: int | None = None, eligible=None
    ) -> str | None:
        suffix_start = len(prefix) + 1
        parameters: list[str | int] = [suffix_start, prefix, suffix_start]
        limit = ""
        if ceiling is not None:
            limit = "AND (length(number), number) <= (?, ?) "
            digits = str(ceiling)
            parameters.extend([len(digits), digits])
        with self._lock:
            rows = self._connection.execute(
                "SELECT atom_id, relative_path, filename FROM (SELECT "
                "relative_path, filename, split_part(reference, '@', 1) AS "
                "atom_id, "
                "ltrim(substr(split_part(reference, '@', 1), ?), '0') AS "
                "number FROM main.atoms) "
                "WHERE starts_with(atom_id, ?) AND "
                "regexp_full_match(substr(atom_id, ?), '[0-9]+') "
                f"{limit}ORDER BY length(number) DESC, number DESC, atom_id "
                f"DESC",
                parameters,
            )
            while row := rows.fetchone():
                if eligible is None or eligible(row[1], row[2]):
                    return row[0]
            return None

    def _create_atom_version_max(self) -> None:
        if not self._connection.execute(
            "SELECT count(*) FROM information_schema.tables "
            "WHERE table_catalog = current_database() AND table_schema = "
            "'main' "
            "AND table_name = 'archive_version_max'"
        ).fetchall()[0][0]:
            return
        source = revision_query(self._connection, stable_only=False)
        self._connection.execute(
            f"CREATE OR REPLACE VIEW main.atom_version_max AS WITH "
            f"revisions AS ({source}) "
            "SELECT atom_id, arg_max(version, (length(version), version)) "
            "AS max_version FROM ("
            "SELECT atom_id, cast(version AS VARCHAR) AS version FROM "
            "revisions "
            "JOIN main.atoms USING (reference, relative_path, filename) "
            "WHERE status_group = 'Current' AND version > 0 "
            f"{self._native_atom_clause()} "
            "UNION ALL SELECT atom_id, max_version FROM "
            "main.archive_version_max"
            ") GROUP BY atom_id"
        )

    def lifecycle_latest_draft_version(
        self, atom_id: str, *, eligible=None
    ) -> int | None:
        with self._lock:
            source = revision_query(self._connection, stable_only=False)
            rows = self._connection.execute(
                f"SELECT revisions.version, revisions.relative_path, "
                f"revisions.filename FROM ({source}) revisions "
                "JOIN main.atoms USING (reference, relative_path, filename) "
                "WHERE revisions.atom_id = ? AND revisions.version > 0 "
                "AND status_group IN ('Current', 'Backlog', 'Draft') "
                f"{self._native_atom_clause()}",
                [atom_id],
            ).fetchall()
            return max(
                (
                    version
                    for version, directory, filename in rows
                    if eligible is None or eligible(directory, filename)
                ),
                default=None,
            )

    def project_consistency(self) -> dict[str, int]:
        with self._lock:
            duplicates, extra = self._connection.execute(
                "SELECT count(*), coalesce(sum(carriers - 1), 0) FROM "
                "(SELECT count(*) AS carriers FROM main.atoms WHERE "
                "reference IS NOT NULL "
                "GROUP BY reference HAVING count(*) > 1)"
            ).fetchone()
            issues = sum(
                self._connection.execute(
                    f"SELECT count(*) FROM main.{table}"
                ).fetchone()[0]
                for table in ATOM_AUDIT_TABLES
            )
            revisions = self._connection.execute(
                (
                    "SELECT count(*) FROM (SELECT observed, expected FROM "
                    "main.atom_duplicate_revision_issues GROUP BY ALL)"
                )
            ).fetchone()[0]
            return {
                "duplicate_references": duplicates,
                "duplicate_carriers": extra,
                "duplicate_revisions": revisions,
                "carrier_issues": issues,
            }

    def lifecycle_descendants(
        self, references: tuple[str, ...], relation: str
    ) -> set[str]:
        with self._lock:
            rows = self._connection.execute(
                """
                WITH RECURSIVE selected AS (
                    SELECT DISTINCT ON (reference) reference, \
"header.relations"
                    FROM main.atoms WHERE status_group <> 'Archived' AND \
reference IS NOT NULL
                    ORDER BY reference, relative_path || '/' || filename
                ), reached(reference) AS (
                    SELECT reference FROM selected WHERE reference IN \
(SELECT unnest(?::VARCHAR[]))
                    UNION
                    SELECT edge.value ->> 'reference'
                    FROM reached JOIN selected USING (reference),
                         LATERAL json_each(selected."header.relations", ?) \
AS edge
                    WHERE (edge.value ->> 'kind') = 'Atom'
                )
                SELECT reference FROM reached
                """,
                [list(references), f"$.{relation}"],
            ).fetchall()
            return {row[0] for row in rows}
