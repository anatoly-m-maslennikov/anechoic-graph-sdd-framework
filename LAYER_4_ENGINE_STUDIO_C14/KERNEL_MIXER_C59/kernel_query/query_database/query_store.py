"""The DuckDB and DuckPGQ owner for disk-backed, paged Workbench queries."""

from __future__ import annotations

from hashlib import sha256 as sha256
import sys as sys
import threading
from pathlib import Path
from typing import Any

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    settings.project.project__shared import (
        attach_framework as attach_framework,
    )  # fmt: skip

from ._query_store_access import (
    QueryStoreAccess,
    _create_runtime_tables,
    _initialize_connection,
    _legacy_projection_fingerprint as _legacy_projection_fingerprint,
)
from ...errors import WorkbenchUnavailableError
from ... import audit_tables as _audit_tables
from ...graph_store import register_graph
from ...header_columns import HeaderSchema, HeaderSchemaState
from ...content_schema import compile_content_schema
from ...projection_delta import ProjectionSnapshot, snapshot
from ...public_rows import insert_rows
from ...query_admission import (
    is_one_tokenized_read_query as is_one_tokenized_read_query,
)
from .query_schema import public_schema as public_schema
from ...query_projection import ProjectionPublication
from ...query_lifecycle import QueryLifecycle
from ...query_observability import QueryObservability
from ...query_results import QueryResults, _Result
from ...journal_table import initialize_journal as initialize_journal


create_audit_tables = _audit_tables.create_tables


def _connect(
    extension_directory: Path | None,
    database_path: Path | None,
    journal_path: Path | None = None,
    journal_disk: bool = False,
) -> Any:
    try:
        import duckdb
    except ImportError as exc:
        raise WorkbenchUnavailableError(
            "DuckDB runtime is unavailable"
        ) from exc
    config: dict[str, str | bool | int | float | list[str]] = {
        "temp_directory": "",
        "memory_limit": "256MB",
    }
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
    _initialize_connection(
        connection, database_path, journal_path, journal_disk
    )
    return connection


def _validate_settings(
    result_ttl_seconds,
    schema_mode,
    inline_result_limit_kib,
    journal_disk,
    journal_path,
):
    if type(result_ttl_seconds) is not int or result_ttl_seconds <= 0:
        raise ValueError("result_ttl_seconds must be a positive integer")
    if type(schema_mode) is not int or schema_mode not in {1, 2}:
        raise ValueError("workbench.schema_mode must be 1 or 2")
    if type(inline_result_limit_kib) is not int or inline_result_limit_kib < 1:
        raise ValueError(
            "workbench.inline_result_limit_kib must be a positive integer"
        )
    if type(journal_disk) is not bool or (
        journal_disk and journal_path is None
    ):
        raise ValueError("disk journal requires a journal_path")


class QueryStore(
    QueryStoreAccess,
    ProjectionPublication,
    QueryResults,
    QueryLifecycle,
    QueryObservability,
):
    """Serialize refresh and public SQL over one DuckDB connection."""

    def __init__(
        self,
        *,
        extension_directory: Path | None = None,
        database_path: Path | None = None,
        result_ttl_seconds: int = 3600,
        schema_mode: int = 2,
        native: bool = False,
        inline_result_limit_kib: int = 4,
        journal_path: Path | None = None,
        journal_disk: bool = False,
        retain_legacy: bool = False,
    ) -> None:
        _validate_settings(
            result_ttl_seconds,
            schema_mode,
            inline_result_limit_kib,
            journal_disk,
            journal_path,
        )
        self._extension_directory = extension_directory
        self._database_path = database_path
        self._native = native
        self._result_ttl_seconds = result_ttl_seconds
        self._schema_mode = schema_mode
        self.inline_result_limit_bytes = inline_result_limit_kib * 1024
        self._lock = threading.RLock()
        self._journal_path = journal_path
        self._journal_disk = journal_disk
        self._connection = _connect(
            extension_directory, database_path, journal_path, journal_disk
        )
        self._initialize_tracking()
        self._projection: ProjectionSnapshot | None = None
        self._header_state = HeaderSchemaState()
        self._header_schema = HeaderSchema(())
        self._content_schema = compile_content_schema([])
        self._schema_changed = False
        self._retain_legacy = (
            retain_legacy and not native and database_path is not None
        )
        self._legacy_frontier = self._take_legacy_frontier()
        self._clear_startup_projection()
        self._start_projection()

    def _initialize_tracking(self):
        self._available = True
        self._initialized = False
        self._live_runs: tuple[tuple[str, ...], ...] = ()
        self._diagnostic_rows: tuple[tuple[str | None, ...], ...] = ()
        self._results: dict[str, _Result] = {}

    def _start_projection(self):
        if self._native or self._legacy_frontier is not None:
            self._initialized = bool(
                self._connection.execute(
                    "SELECT 1 FROM information_schema.tables "
                    "WHERE table_catalog = current_database() AND "
                    "table_schema = 'main' AND table_name = 'atoms'"
                ).fetchone()
            )
        else:
            self.replace([], [])

    def _take_legacy_frontier(self) -> str | None:
        if not self._retain_legacy or self._connection.execute(
            "SELECT count(*) FROM information_schema.tables WHERE "
            "table_catalog = current_database() "
            "AND ((table_schema = 'internal' AND table_name IN "
            "('legacy_frontier', 'reference')) "
            "OR (table_schema = 'main' AND table_name IN ('atoms', "
            "'scope_units')))"
        ).fetchone() != (4,):
            return None
        row = self._connection.execute(
            "SELECT fingerprint FROM internal.legacy_frontier"
        ).fetchone()
        self._connection.execute("DROP TABLE internal.legacy_frontier")
        return row[0] if row is not None else None

    def _clear_startup_projection(self) -> None:
        """Discard the disposable projection and prior query cache."""
        try:
            if not self._native and self._legacy_frontier is None:
                self._connection.execute(
                    "DROP PROPERTY GRAPH IF EXISTS anechoic"
                )
                self._connection.execute(
                    "DROP SCHEMA IF EXISTS internal CASCADE"
                )
                self._connection.execute("DROP TABLE IF EXISTS main.atoms")
                self._connection.execute(
                    "DROP TABLE IF EXISTS main.scope_units"
                )
            self._connection.execute(
                "DROP SCHEMA IF EXISTS workbench_results CASCADE"
            )
            self._connection.execute(
                "DROP SCHEMA IF EXISTS lifecycle_private CASCADE"
            )
            self._connection.execute("DROP TABLE IF EXISTS main.change_log")
            self._connection.execute("DROP VIEW IF EXISTS main.query_log")
            for table in (
                "live_runs",
                "query_log_records",
                "runtime_diagnostics",
            ):
                self._connection.execute(f"DROP TABLE IF EXISTS main.{table}")
            self._create_runtime_tables()
        except Exception as exc:
            self._connection.close()
            raise WorkbenchUnavailableError(
                "query store initialization failed"
            ) from exc

    def _create_runtime_tables(self):
        _create_runtime_tables(self)

    def _replace_projection(
        self,
        atom_rows,
        scope_rows,
        relation_types,
        header_schema,
        content_schema,
        reuse,
    ):
        projection, reuse, legacy_reuse = self._legacy_projection(
            atom_rows,
            scope_rows,
            relation_types,
            header_schema,
            content_schema,
            reuse,
        )
        if self._initialized and not reuse:
            self._drop_projection()
        public_rows = (
            None
            if reuse
            else insert_rows(
                self._connection,
                atom_rows,
                scope_rows,
                header_schema=header_schema,
                content_schema=content_schema,
                relation_types=relation_types,
            )
        )
        projection = projection or snapshot(
            atom_rows,
            scope_rows,
            relation_types,
            header_schema,
            content_schema,
            public_rows=public_rows,
        )
        if legacy_reuse:
            self.mark_graph_registration_changed()
            self._connection.execute("DROP PROPERTY GRAPH IF EXISTS anechoic")
            register_graph(self._connection, projection.graph)
        return projection, reuse

    def _drop_projection(self):
        self.mark_graph_registration_changed()
        self._connection.execute("DROP PROPERTY GRAPH IF EXISTS anechoic")
        self._connection.execute("DROP SCHEMA internal CASCADE")
        self._connection.execute("DROP TABLE main.atoms")
        self._connection.execute("DROP TABLE main.scope_units")

    def _legacy_projection(
        self,
        atom_rows,
        scope_rows,
        relation_types,
        header_schema,
        content_schema,
        reuse,
    ):
        projection = None
        legacy_reuse = False
        if self._legacy_frontier is not None:
            projection = snapshot(
                atom_rows,
                scope_rows,
                relation_types,
                header_schema,
                content_schema,
            )
            legacy_reuse = (
                self._initialized
                and _legacy_projection_fingerprint(projection)
                == self._legacy_frontier
            )
            self._legacy_frontier = None
            reuse = legacy_reuse
        return projection, reuse, legacy_reuse

    def mark_graph_registration_changed(self) -> None:
        """Mark DuckPGQ registration as potentially changed."""
        self._graph_registration_changed = True
