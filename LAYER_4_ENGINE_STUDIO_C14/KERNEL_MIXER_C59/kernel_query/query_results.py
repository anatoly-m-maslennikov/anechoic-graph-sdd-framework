"""Materialize and manage paged Workbench query results."""

from __future__ import annotations

from pydantic.dataclasses import dataclass
import re as re
import sys
import time
import uuid
from typing import Any

from ._result_lifecycle import ResultLifecycle
from ..errors import QueryExecutionError, WorkbenchUnavailableError
from ..graph_store import quote_identifier
from ..query_admission import is_duckdb_internal
from .result_columns import result_columns
from .result_values import group_key as group_key
from .result_values import result_value
from .result_view import (
    Grid,
    build_page_query,
    ctas_source_sql,
    parse_grid,
    validate_columns,
)


def _query_failure(error: Exception) -> str:
    import duckdb

    if isinstance(error, duckdb.ParserException):
        return "query failed: invalid SQL syntax"
    if isinstance(error, duckdb.BinderException):
        return "query failed: invalid column, table, or query binding"
    if isinstance(error, duckdb.ConversionException):
        return "query failed: Could not convert a query value"
    return "query failed during execution"


@dataclass(
    config={"strict": True, "extra": "forbid", "hide_input_in_errors": True}
)
class _Result:
    columns: list[dict[str, Any]]
    row_count: int
    sql: str
    stored_columns: tuple[str, ...]
    created_at: float
    table_name: str
    preview: int | None = None
    pinned: bool = False
    dependencies: frozenset[str] = frozenset()
    dependencies_unknown: bool = False
    released: bool = False


class QueryResults(ResultLifecycle):
    def _materialize(
        self,
        sql: str,
        preview: int | None = None,
        *,
        admitted: bool = False,
        source: _Result | None = None,
    ) -> tuple[str, _Result]:
        if not self._available:
            raise WorkbenchUnavailableError(
                "query store unavailable; Workbench restart required"
            )
        self._admit_query(sql, admitted)
        relation, columns = self._describe_relation(sql, preview)
        query_id = uuid.uuid4().hex
        table_name = f"query_{query_id}"
        table = quote_identifier(table_name)
        private_ordinal = f"__workbench_snapshot_{query_id}"
        columns, row_count, stored_columns = self._materialize_table(
            relation, columns, table, private_ordinal
        )
        dependencies, unknown = self._dependencies(sql, source)
        return query_id, _Result(
            columns,
            row_count,
            sql,
            stored_columns,
            time.monotonic(),
            table_name,
            preview,
            dependencies=dependencies,
            dependencies_unknown=unknown,
        )

    def _admit_query(self, sql, admitted):
        try:
            if not admitted:
                self._admit(sql)
                self._connection.execute(
                    'DELETE FROM query_log_records WHERE "at" <= '
                    "current_timestamp - INTERVAL 48 HOURS"
                )
                self._verify_read_only(sql)
        except ValueError as exc:
            print(f"query failed: {exc}", file=sys.stderr)
            raise
        except Exception as exc:
            print(_query_failure(exc), file=sys.stderr)
            raise QueryExecutionError(_query_failure(exc)) from exc

    def _materialize_table(self, relation, columns, table, private_ordinal):
        try:
            materialized_sql = ctas_source_sql(relation.sql_query())
            self._connection.execute(
                f"CREATE TABLE workbench_results.{table} AS "
                "SELECT row_number() OVER () AS "
                f"{quote_identifier(private_ordinal)}, * "
                f"FROM ({materialized_sql}\n) AS source"
            )
            stored_columns = tuple(
                self._connection.sql(
                    f"SELECT * FROM workbench_results.{table}"
                ).columns
            )
            columns, row_count = result_columns(
                self._connection, table, columns, private_ordinal=True
            )
        except Exception as exc:
            if is_duckdb_internal(exc):
                self._available = False
                print(f"query store unavailable: {exc}", file=sys.stderr)
                raise WorkbenchUnavailableError(
                    "query store unavailable; Workbench restart required"
                ) from exc
            print(_query_failure(exc), file=sys.stderr)
            raise QueryExecutionError(_query_failure(exc)) from exc
        return columns, row_count, stored_columns

    def _describe_relation(
        self, sql: str, preview: int | None
    ) -> tuple[Any, list[dict[str, Any]]]:
        try:
            relation = self._connection.sql(sql)
            if preview is not None:
                relation = relation.limit(preview)
            columns = [
                {"name": name, "type": str(column_type)}
                for name, column_type in zip(
                    relation.columns, relation.types, strict=True
                )
            ]
        except Exception as exc:
            print(_query_failure(exc), file=sys.stderr)
            raise QueryExecutionError(_query_failure(exc)) from exc
        return relation, columns

    def _read_page(
        self,
        query_id: str,
        result: _Result,
        offset: int,
        page_size: int,
        grid: Grid,
    ) -> dict[str, Any]:
        try:
            query, row_count, rows, shaped_rows = self._fetch_page(
                result, offset, page_size, grid
            )
        except ValueError as exc:
            print(f"query result delivery failed: {exc}", file=sys.stderr)
            raise QueryExecutionError(
                f"query result delivery failed: {exc}"
            ) from exc
        except Exception as exc:
            self._available = False
            print(f"query store unavailable: {exc}", file=sys.stderr)
            raise WorkbenchUnavailableError(
                "query store unavailable; Workbench restart required"
            ) from exc
        return self._page_response(
            query_id,
            result,
            offset,
            page_size,
            query,
            row_count,
            shaped_rows,
            rows,
        )

    def _fetch_page(self, result, offset, page_size, grid):
        query = build_page_query(
            result.table_name,
            result.stored_columns,
            grid,
            page_size=page_size,
            offset=offset,
        )
        row_count = self._connection.execute(
            query.count_sql, query.count_parameters
        ).fetchone()[0]
        rows = self._connection.execute(
            query.page_sql, query.page_parameters
        ).fetchall()
        shaped_rows = [
            [result_value(value) for value in row[1 : len(result.columns) + 1]]
            for row in rows
        ]
        return query, row_count, rows, shaped_rows

    def run(
        self,
        sql: str,
        page_size: int = 100,
        *,
        preview: int | None = None,
        include_rows: bool = True,
    ) -> dict[str, Any]:
        page_size = self._page_size(page_size)
        preview = self._preview(preview)
        if type(include_rows) is not bool:
            raise ValueError("include_rows must be a boolean")
        with self._lock:
            query_id, result = self._materialize(sql, preview)
            self._results[query_id] = result
            if not include_rows:
                return {
                    "query_id": query_id,
                    "sql": sql,
                    "columns": result.columns,
                    "row_count": result.row_count,
                    "column_count": len(result.columns),
                }
            try:
                return self._read_page(
                    query_id, result, 0, page_size, Grid((), (), None)
                )
            except QueryExecutionError, ValueError:
                self.drop(query_id)
                raise

    def page(
        self,
        query_id: str,
        offset: int,
        page_size: int = 100,
        *,
        preview: int | None = None,
        grid: object = None,
    ) -> dict[str, Any]:
        offset = self._offset(offset)
        page_size = self._page_size(page_size)
        preview = self._preview(preview)
        parsed_grid = parse_grid(grid)
        if not isinstance(query_id, str):
            raise ValueError("unknown query_id")
        with self._lock:
            if not self._available:
                raise WorkbenchUnavailableError(
                    "query store unavailable; Workbench restart required"
                )
            if (
                query_id not in self._results
                or self._results[query_id].released
            ):
                raise ValueError("unknown query_id")
            result = self._results[query_id]
            validate_columns(parsed_grid, len(result.columns))
            if preview is not None:
                page_size = min(page_size, preview)
            return self._read_page(
                query_id, result, offset, page_size, parsed_grid
            )

    def check(self, sql: str) -> dict[str, Any]:
        with self._lock:
            query_id, result = self._materialize(sql)
            table = quote_identifier(f"query_{query_id}")
            try:
                self._connection.execute(
                    f"DROP TABLE workbench_results.{table}"
                )
            except Exception as exc:
                self._available = False
                print(f"query store unavailable: {exc}", file=sys.stderr)
                raise WorkbenchUnavailableError(
                    "query store unavailable; Workbench restart required"
                ) from exc
        return {
            "valid": True,
            "columns": result.columns,
            "row_count": result.row_count,
            "column_count": len(result.columns),
            "sql": sql,
        }
