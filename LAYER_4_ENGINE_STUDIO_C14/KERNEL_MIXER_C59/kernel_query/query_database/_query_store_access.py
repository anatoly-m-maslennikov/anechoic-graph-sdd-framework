"""Query admission, validation, reporting and shutdown."""

from __future__ import annotations

from typing import Any

from . import query_store as runtime


class QueryStoreAccess:
    def _admit(self, sql: str) -> None:
        if not isinstance(sql, str):
            raise ValueError("SQL must be a string")
        import duckdb

        try:
            statements = self._connection.extract_statements(sql)
        except Exception:
            if runtime.is_one_tokenized_read_query(sql):
                return
            raise ValueError(
                "public SQL must contain one native read query"
            ) from None
        if (
            len(statements) != 1
            or statements[0].type is not duckdb.StatementType.SELECT
        ):
            raise ValueError(
                "public SQL must contain exactly one native SELECT statement"
            )

    def _verify_read_only(self, sql: str) -> None:
        """Use read-only planning to reject writable CTEs."""
        self._connection.execute("BEGIN TRANSACTION READ ONLY")
        try:
            self._connection.execute(f"EXPLAIN {sql}").fetchall()
        finally:
            self._connection.execute("COMMIT")

    @staticmethod
    def _page_size(value: int) -> int:
        if type(value) is not int or not 1 <= value <= 1000:
            raise ValueError("page_size must be an integer from 1 to 1000")
        return value

    @staticmethod
    def _offset(value: int) -> int:
        if type(value) is not int or value < 0:
            raise ValueError("offset must be a non-negative integer")
        return value

    @staticmethod
    def _preview(value: int | None) -> int | None:
        if value is None:
            return None
        if type(value) is not int or value < 0:
            raise ValueError("preview must be a non-negative integer")
        return value

    def schema(self) -> dict[str, dict[str, list[dict[str, Any]]]]:
        with self._lock:
            if not self._available:
                raise runtime.WorkbenchUnavailableError(
                    "query store unavailable; Workbench restart required"
                )
            result = runtime.public_schema(
                self._connection, self._header_schema
            )
            rows = self._connection.execute(
                "SELECT column_name, data_type FROM "
                "information_schema.columns "
                "WHERE table_catalog = current_database() AND table_schema "
                "= 'main' "
                "AND table_name = 'work_journal' ORDER BY ordinal_position"
            ).fetchall()
            if rows:
                result["tables"]["work_journal"] = [
                    {"name": name, "type": kind} for name, kind in rows
                ]
            return result

    def close(self, *, retain_projection: bool = True) -> None:
        with self._lock:
            if (
                self._retain_legacy
                and retain_projection
                and self._available
                and self._projection is not None
            ):
                try:
                    self._connection.execute(
                        "CREATE TABLE internal.legacy_frontier AS SELECT "
                        "?::VARCHAR AS fingerprint",
                        [
                            runtime._legacy_projection_fingerprint(
                                self._projection
                            )
                        ],
                    )
                except Exception as error:
                    print(
                        f"Workbench projection could not be retained: {error}",
                        file=runtime.sys.stderr,
                    )
            self._retain_legacy = False
            self._connection.close()


def _initialize_connection(
    connection, database_path, journal_path, journal_disk
):
    try:
        connection.execute("LOAD duckpgq")
        connection.execute("SET active_grammar_extensions = ['duckpgq']")
    except Exception as exc:
        connection.close()
        raise runtime.WorkbenchUnavailableError(
            "DuckPGQ runtime initialization failed"
        ) from exc
    try:
        runtime.initialize_journal(
            connection, database_path, journal_path, journal_disk
        )
    except Exception as exc:
        connection.close()
        raise runtime.WorkbenchUnavailableError(
            f"Work Journal database initialization failed: {exc}"
        ) from exc
    try:
        runtime.attach_framework(connection)
    except Exception as exc:
        connection.close()
        raise runtime.WorkbenchUnavailableError(
            f"Framework database initialization failed: {exc}"
        ) from exc
    try:
        connection.execute("SET enable_external_access = false")
        connection.execute("SET autoinstall_known_extensions = false")
        connection.execute("SET autoload_known_extensions = false")
        connection.execute("SET lock_configuration = true")
    except Exception as exc:
        connection.close()
        raise runtime.WorkbenchUnavailableError(
            "DuckPGQ runtime initialization failed"
        ) from exc


def _legacy_projection_fingerprint(
    projection: runtime.ProjectionSnapshot,
) -> str:
    graph = projection.graph
    return runtime.sha256(
        repr(
            (
                1,
                projection.header_schema.shape,
                projection.content_schema.shape,
                sorted(
                    (key, row["hash"]) for key, row in projection.atoms.items()
                ),
                sorted(
                    (key, row["hash"])
                    for key, row in projection.scopes.items()
                ),
                sorted(graph.references),
                sorted(
                    (name, sorted(edges))
                    for name, edges in graph.edges.items()
                ),
            )
        ).encode()
    ).hexdigest()


def _create_runtime_tables(self):
    temporary = "" if self._database_path is not None else "TEMP "
    self._connection.execute("CREATE SCHEMA workbench_results")
    self._connection.execute(
        "CREATE TABLE main.change_log (observed_at TIMESTAMPTZ NOT NULL, "
        "operation VARCHAR NOT NULL, old_path VARCHAR, new_path VARCHAR)"
    )
    self._connection.execute(
        f"CREATE {temporary}TABLE live_runs (run_id VARCHAR, session_id "
        f"VARCHAR, tool VARCHAR, status VARCHAR)"
    )
    self._connection.execute(
        f"CREATE {temporary}TABLE query_log_records (log_id VARCHAR "
        f'PRIMARY KEY, "at" TIMESTAMPTZ, sql VARCHAR, '
        "outcome VARCHAR, error VARCHAR, row_count BIGINT, column_count "
        "BIGINT)"
    )
    self._connection.execute(
        f"CREATE {temporary}VIEW query_log AS SELECT * FROM query_log_records "
        'WHERE "at" > current_timestamp - INTERVAL 48 HOURS'
    )
    self._connection.execute(
        f"CREATE {temporary}TABLE runtime_diagnostics (observed_at "
        f"TIMESTAMPTZ, name VARCHAR, outcome VARCHAR, "
        "returned_outcome VARCHAR, error_category VARCHAR, project_prefix "
        "VARCHAR, project_instance_id VARCHAR)"
    )
    runtime.create_audit_tables(self._connection)
