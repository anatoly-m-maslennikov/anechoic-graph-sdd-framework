
"""The DuckDB and DuckPGQ owner for disk-backed, paged Workbench queries."""

from __future__ import annotations

from hashlib import sha256
import sys
import threading
from pathlib import Path
from typing import Any

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import attach_framework

from .errors import WorkbenchUnavailableError
from .audit_tables import (
    create_tables as create_audit_tables,
)
from .graph_store import register_graph
from .header_columns import HeaderSchema, HeaderSchemaState
from .content_schema import compile_content_schema
from .projection_delta import ProjectionSnapshot, snapshot
from .public_rows import insert_rows
from .query_admission import is_one_tokenized_read_query
from .query_schema import public_schema
from .query_projection import ProjectionPublication
from .query_lifecycle import QueryLifecycle
from .query_observability import QueryObservability
from .query_results import QueryResults, _Result
from .journal_table import initialize_journal


def _connect(extension_directory: Path | None, database_path: Path | None,
             journal_path: Path | None = None, journal_disk: bool = False) -> Any:
    try:
        import duckdb
    except ImportError as exc:
        raise WorkbenchUnavailableError("DuckDB runtime is unavailable") from exc
    config: dict[str, str | bool | int | float | list[str]] = {"temp_directory": "", "memory_limit": "256MB"}
    database = ":memory:"
    if database_path is not None:
        database_path.parent.mkdir(parents=True, exist_ok=True)
        spill_directory = database_path.parent / "duckdb-temp"
        spill_directory.mkdir(exist_ok=True)
        database = str(database_path)
        config["temp_directory"] = str(spill_directory)
    if extension_directory is not None:
        config["extension_directory"] = str(extension_directory)
    connection = duckdb.connect(database, config=config)
    try:
        connection.execute("LOAD duckpgq")
        connection.execute("SET active_grammar_extensions = ['duckpgq']")
    except Exception as exc:
        connection.close()
        raise WorkbenchUnavailableError("DuckPGQ runtime initialization failed") from exc
    try:
        initialize_journal(connection, database_path, journal_path, journal_disk)
    except Exception as exc:
        connection.close()
        raise WorkbenchUnavailableError(f"Work Journal database initialization failed: {exc}") from exc
    try:
        attach_framework(connection)
    except Exception as exc:
        connection.close()
        raise WorkbenchUnavailableError(f"Framework database initialization failed: {exc}") from exc
    try:
        connection.execute("SET enable_external_access = false")
        connection.execute("SET autoinstall_known_extensions = false")
        connection.execute("SET autoload_known_extensions = false")
        connection.execute("SET lock_configuration = true")
    except Exception as exc:
        connection.close()
        raise WorkbenchUnavailableError("DuckPGQ runtime initialization failed") from exc
    return connection


def _legacy_projection_fingerprint(projection: ProjectionSnapshot) -> str:
    graph = projection.graph
    return sha256(repr((
        1, projection.header_schema.shape, projection.content_schema.shape,
        sorted((key, row["hash"]) for key, row in projection.atoms.items()),
        sorted((key, row["hash"]) for key, row in projection.scopes.items()),
        sorted(graph.references),
        sorted((name, sorted(edges)) for name, edges in graph.edges.items()),
    )).encode()).hexdigest()


class QueryStore(ProjectionPublication, QueryResults, QueryLifecycle, QueryObservability):
    """Serialize trusted refresh and paged public native SQL over one DuckDB connection."""

    def __init__(
        self, *, extension_directory: Path | None = None, database_path: Path | None = None,
        result_ttl_seconds: int = 3600, schema_mode: int = 2, native: bool = False,
        inline_result_limit_kib: int = 4, journal_path: Path | None = None, journal_disk: bool = False,
        retain_legacy: bool = False,
    ) -> None:
        if type(result_ttl_seconds) is not int or result_ttl_seconds <= 0:
            raise ValueError("result_ttl_seconds must be a positive integer")
        if type(schema_mode) is not int or schema_mode not in {1, 2}:
            raise ValueError("workbench.schema_mode must be 1 or 2")
        if type(inline_result_limit_kib) is not int or inline_result_limit_kib < 1:
            raise ValueError("workbench.inline_result_limit_kib must be a positive integer")
        if type(journal_disk) is not bool or (journal_disk and journal_path is None):
            raise ValueError("disk journal requires a journal_path")
        self._extension_directory = extension_directory
        self._database_path = database_path
        self._native = native
        self._result_ttl_seconds = result_ttl_seconds
        self._schema_mode = schema_mode
        self.inline_result_limit_bytes = inline_result_limit_kib * 1024
        self._lock = threading.RLock()
        self._journal_path = journal_path
        self._journal_disk = journal_disk
        self._connection = _connect(extension_directory, database_path, journal_path, journal_disk)
        self._available = True
        self._initialized = False
        self._live_runs: tuple[tuple[str, ...], ...] = ()
        self._diagnostic_rows: tuple[tuple[str | None, ...], ...] = ()
        self._results: dict[str, _Result] = {}
        self._projection: ProjectionSnapshot | None = None
        self._header_state = HeaderSchemaState()
        self._header_schema = HeaderSchema(())
        self._content_schema = compile_content_schema([])
        self._schema_changed = False
        self._retain_legacy = retain_legacy and not native and database_path is not None
        self._legacy_frontier = self._take_legacy_frontier()
        self._clear_startup_projection()
        if native or self._legacy_frontier is not None:
            self._initialized = bool(self._connection.execute(
                "SELECT 1 FROM information_schema.tables "
                "WHERE table_catalog = current_database() AND table_schema = 'main' AND table_name = 'atoms'"
            ).fetchone())
        else:
            self.replace([], [])

    def _take_legacy_frontier(self) -> str | None:
        if not self._retain_legacy or self._connection.execute(
            "SELECT count(*) FROM information_schema.tables WHERE table_catalog = current_database() "
            "AND ((table_schema = 'internal' AND table_name IN ('legacy_frontier', 'reference')) "
            "OR (table_schema = 'main' AND table_name IN ('atoms', 'scope_units')))"
        ).fetchone() != (4,):
            return None
        row = self._connection.execute("SELECT fingerprint FROM internal.legacy_frontier").fetchone()
        self._connection.execute("DROP TABLE internal.legacy_frontier")
        return row[0] if row is not None else None

    def _clear_startup_projection(self) -> None:
        """Discard the disposable projection and any prior process's query cache."""
        try:
            if not self._native and self._legacy_frontier is None:
                self._connection.execute("DROP PROPERTY GRAPH IF EXISTS anechoic")
                self._connection.execute("DROP SCHEMA IF EXISTS internal CASCADE")
                self._connection.execute("DROP TABLE IF EXISTS main.atoms")
                self._connection.execute("DROP TABLE IF EXISTS main.scope_units")
            self._connection.execute("DROP SCHEMA IF EXISTS workbench_results CASCADE")
            self._connection.execute("DROP SCHEMA IF EXISTS lifecycle_private CASCADE")
            self._connection.execute("DROP TABLE IF EXISTS main.change_log")
            self._connection.execute("DROP VIEW IF EXISTS main.query_log")
            for table in ("live_runs", "query_log_records", "runtime_diagnostics"):
                self._connection.execute(f"DROP TABLE IF EXISTS main.{table}")
            temporary = "" if self._database_path is not None else "TEMP "
            self._connection.execute("CREATE SCHEMA workbench_results")
            self._connection.execute(
                "CREATE TABLE main.change_log (observed_at TIMESTAMPTZ NOT NULL, "
                "operation VARCHAR NOT NULL, old_path VARCHAR, new_path VARCHAR)"
            )
            self._connection.execute(
                f"CREATE {temporary}TABLE live_runs (run_id VARCHAR, session_id VARCHAR, tool VARCHAR, status VARCHAR)"
            )
            self._connection.execute(
                f'CREATE {temporary}TABLE query_log_records (log_id VARCHAR PRIMARY KEY, "at" TIMESTAMPTZ, sql VARCHAR, '
                "outcome VARCHAR, error VARCHAR, row_count BIGINT, column_count BIGINT)"
            )
            self._connection.execute(
                f'CREATE {temporary}VIEW query_log AS SELECT * FROM query_log_records '
                'WHERE "at" > current_timestamp - INTERVAL 48 HOURS'
            )
            self._connection.execute(
                f"CREATE {temporary}TABLE runtime_diagnostics (observed_at TIMESTAMPTZ, name VARCHAR, outcome VARCHAR, "
                "returned_outcome VARCHAR, error_category VARCHAR, project_prefix VARCHAR, project_instance_id VARCHAR)"
            )
            create_audit_tables(self._connection)
        except Exception as exc:
            self._connection.close()
            raise WorkbenchUnavailableError("query store initialization failed") from exc

    def _replace_projection(self, atom_rows, scope_rows, relation_types, header_schema, content_schema, reuse):
        projection = None
        legacy_reuse = False
        if self._legacy_frontier is not None:
            projection = snapshot(atom_rows, scope_rows, relation_types, header_schema, content_schema)
            legacy_reuse = self._initialized and _legacy_projection_fingerprint(projection) == self._legacy_frontier
            self._legacy_frontier = None
            reuse = legacy_reuse
        if self._initialized and not reuse:
            self.mark_graph_registration_changed()
            self._connection.execute("DROP PROPERTY GRAPH IF EXISTS anechoic")
            self._connection.execute("DROP SCHEMA internal CASCADE")
            self._connection.execute("DROP TABLE main.atoms")
            self._connection.execute("DROP TABLE main.scope_units")
        public_rows = None if reuse else insert_rows(
            self._connection, atom_rows, scope_rows, header_schema=header_schema,
            content_schema=content_schema, relation_types=relation_types,
        )
        projection = projection or snapshot(
            atom_rows, scope_rows, relation_types, header_schema, content_schema, public_rows=public_rows,
        )
        if legacy_reuse:
            self.mark_graph_registration_changed()
            self._connection.execute("DROP PROPERTY GRAPH IF EXISTS anechoic")
            register_graph(self._connection, projection.graph)
        return projection, reuse

    def mark_graph_registration_changed(self) -> None:
        """Mark non-transactional DuckPGQ registration as potentially changed."""
        self._graph_registration_changed = True

    def _admit(self, sql: str) -> None:
        if not isinstance(sql, str):
            raise ValueError("SQL must be a string")
        import duckdb

        try:
            statements = self._connection.extract_statements(sql)
        except Exception:
            if is_one_tokenized_read_query(sql):
                return
            raise ValueError("public SQL must contain one native read query") from None
        if len(statements) != 1 or statements[0].type is not duckdb.StatementType.SELECT:
            raise ValueError("public SQL must contain exactly one native SELECT statement")

    def _verify_read_only(self, sql: str) -> None:
        """Native planning under DuckDB's read-only transaction rejects writable CTEs."""
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
                raise WorkbenchUnavailableError("query store unavailable; Workbench restart required")
            result = public_schema(self._connection, self._header_schema)
            rows = self._connection.execute(
                "SELECT column_name, data_type FROM information_schema.columns "
                "WHERE table_catalog = current_database() AND table_schema = 'main' "
                "AND table_name = 'work_journal' ORDER BY ordinal_position"
            ).fetchall()
            if rows:
                result["tables"]["work_journal"] = [{"name": name, "type": kind} for name, kind in rows]
            return result

    def close(self, *, retain_projection: bool = True) -> None:
        with self._lock:
            if self._retain_legacy and retain_projection and self._available and self._projection is not None:
                try:
                    self._connection.execute(
                        "CREATE TABLE internal.legacy_frontier AS SELECT ?::VARCHAR AS fingerprint",
                        [_legacy_projection_fingerprint(self._projection)],
                    )
                except Exception as error:
                    print(f"Workbench projection could not be retained: {error}", file=sys.stderr)
            self._retain_legacy = False
            self._connection.close()
