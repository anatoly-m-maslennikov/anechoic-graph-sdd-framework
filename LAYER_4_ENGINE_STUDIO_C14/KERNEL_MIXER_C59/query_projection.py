"""Transactional publication of Workbench projections."""

from __future__ import annotations

import sys
import time
from typing import Any

from .content_schema import ContentSchema, compile_content_schema, content_schema_asset_path
from .errors import WorkbenchUnavailableError
from .header_columns import HeaderSchema, HeaderSchemaState, header_schema_for_mode, schema_asset_path
from .index_delta import MaterializationDelta
from .projection_delta import apply as apply_projection_delta
from .query_admission import is_duckdb_internal


class ProjectionPublication:
    def replace(
        self, atom_rows: list[dict[str, Any]], scope_rows: list[dict[str, Any]],
        *, relation_types: set[str] | None = None, content_schema: ContentSchema | None = None,
        header_schema: HeaderSchema | None = None, reuse: bool = False, before_commit=None,
    ) -> None:
        with self._lock:
            if not self._available:
                raise WorkbenchUnavailableError("query store unavailable; Workbench restart required")
            transaction = False
            self._graph_registration_changed = False
            try:
                header_state, header_schema = self._replacement_header(atom_rows, header_schema)
                if content_schema is None:
                    content_schema = compile_content_schema(atom_rows)
                self._connection.execute("BEGIN TRANSACTION")
                transaction = True
                started = time.monotonic()
                projection, reuse = self._replace_projection(
                    atom_rows, scope_rows, relation_types, header_schema, content_schema, reuse,
                )
                if before_commit is not None:
                    before_commit(projection.graph)
                self._connection.execute("COMMIT")
                transaction = False
                self._initialized = True
                self._header_state = header_state
                self._header_schema = header_schema
                self._content_schema = content_schema
                self._schema_changed = False
                if not self._native:
                    self._create_atom_version_max()
                    header_schema.write(schema_asset_path(self._database_path))
                    content_schema.write(content_schema_asset_path(self._database_path))
                self._projection = projection
                self._info_edit(
                    "reuse" if reuse else "replace", "projection",
                    len(self._projection.atoms) + len(self._projection.scopes), started,
                )
            except Exception as exc:
                self._projection_failure(exc, transaction)

    def _replacement_header(self, atom_rows, header_schema):
        if header_schema is not None:
            return self._header_state, header_schema
        if self._schema_mode == 2:
            header_state = HeaderSchemaState.from_atoms(atom_rows)
            return header_state, header_state.schema
        return self._header_state, header_schema_for_mode(self._schema_mode, atom_rows)

    def _info_edit(
        self, operation: str, table: str, row_count: int, started: float, reference: str | None = None,
    ) -> None:
        if row_count:
            elapsed_ms = round((time.monotonic() - started) * 1000, 1)
            suffix = f" reference={reference}" if reference is not None else ""
            print(
                f"Workbench INFO database_edit operation={operation} table={table} "
                f"row_count={row_count} elapsed_ms={elapsed_ms}{suffix}",
                flush=True,
            )

    def apply(  # noqa: C901
        self, atom_rows: list[dict[str, Any]], scope_rows: list[dict[str, Any]],
        *, relation_types: set[str], content_schema: ContentSchema | None = None,
        delta: MaterializationDelta | None = None, header_schema: HeaderSchema | None = None,
        before_commit=None,
    ) -> bool:
        """Apply the materialized delta without replacing unaffected public rows."""
        with self._lock:
            if not self._available:
                raise WorkbenchUnavailableError("query store unavailable; Workbench restart required")
            if self._projection is None:
                self.replace(
                    atom_rows, scope_rows, relation_types=relation_types,
                    content_schema=content_schema, header_schema=header_schema, before_commit=before_commit,
                )
                return True
            transaction = False
            self._graph_registration_changed = False
            try:
                header_state, header_schema, content_schema = self._apply_schemas(
                    atom_rows, delta, header_schema, content_schema,
                )
                if self._schema_changed:
                    return True
                self._connection.execute("BEGIN TRANSACTION")
                transaction = True
                started = time.monotonic()
                projection, change = apply_projection_delta(
                    self._connection, self._projection, atom_rows, scope_rows, relation_types,
                    header_schema, content_schema, delta=delta,
                )
                if before_commit is not None:
                    before_commit(projection.graph)
                self._connection.execute("COMMIT")
                transaction = False
                self._projection = projection
                self._header_state = header_state
                self._header_schema = header_schema
                self._content_schema = content_schema
                if not self._native:
                    header_schema.write(schema_asset_path(self._database_path))
                    content_schema.write(content_schema_asset_path(self._database_path))
                return self._record_projection_change(change, started)
            except Exception as exc:
                self._projection_failure(exc, transaction)

    def _record_projection_change(self, change, started):
        self._info_edit("delete", "atoms", change.deleted_atoms, started, change.reference)
        self._info_edit("delete", "scope_units", change.deleted_scopes, started)
        self._info_edit("insert", "atoms", change.inserted_atoms, started, change.reference)
        self._info_edit("insert", "scope_units", change.inserted_scopes, started)
        self._info_edit("update", "graph", change.graph_rows, started, change.reference)
        return bool(
            change.deleted_atoms or change.deleted_scopes or change.inserted_atoms
            or change.inserted_scopes or change.graph_rows
        )

    def _projection_failure(self, exc: Exception, transaction: bool) -> None:
        if not self._native or self._graph_registration_changed or is_duckdb_internal(exc):
            self._available = False
        if transaction:
            self._connection.execute("ROLLBACK")
        print(f"query store refresh failed: {exc}", file=sys.stderr)
        if self._native and self._available:
            raise
        raise WorkbenchUnavailableError("query store unavailable; Workbench restart required") from exc

    def _apply_schemas(self, atom_rows, delta, header_schema, content_schema):
        if header_schema is not None or self._schema_mode == 1:
            header_state = self._header_state
        elif delta is None:
            header_state = HeaderSchemaState.from_atoms(atom_rows)
        else:
            header_state = self._header_state.updated(delta.old_atoms, delta.new_atoms)
        header_schema = header_schema or (
            self._header_schema if self._schema_mode == 1 else header_state.schema
        )
        if content_schema is None:
            content_schema = compile_content_schema(atom_rows)
        self._schema_changed = (
            header_schema.shape != self._header_schema.shape
            or content_schema.shape != self._content_schema.shape
        )
        return header_state, header_schema, content_schema

    @property
    def schema_changed(self) -> bool:
        """Whether the last delta needs a complete source reread and table rebuild."""
        return self._schema_changed

