"""Materialize and manage paged Workbench query results."""

from __future__ import annotations

from pydantic.dataclasses import dataclass
import re
import sys
import time
import uuid
from typing import Any

from .errors import QueryExecutionError, WorkbenchUnavailableError
from .graph_store import quote_identifier
from .query_admission import is_duckdb_internal
from .result_columns import result_columns
from .result_values import group_key, result_value
from .result_view import Grid, build_page_query, ctas_source_sql, parse_grid, validate_columns


def _query_failure(error: Exception) -> str:
    import duckdb

    if isinstance(error, duckdb.ParserException):
        return "query failed: invalid SQL syntax"
    if isinstance(error, duckdb.BinderException):
        return "query failed: invalid column, table, or query binding"
    if isinstance(error, duckdb.ConversionException):
        return "query failed: Could not convert a query value"
    return "query failed during execution"


@dataclass(config={"strict": True, "extra": "forbid", "hide_input_in_errors": True})
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


class QueryResults:
    def _materialize(self, sql: str, preview: int | None = None, *, admitted: bool = False,
                     source: _Result | None = None) -> tuple[str, _Result]:
        if not self._available:
            raise WorkbenchUnavailableError("query store unavailable; Workbench restart required")
        try:
            if not admitted:
                self._admit(sql)
                self._connection.execute(
                    'DELETE FROM query_log_records WHERE "at" <= current_timestamp - INTERVAL 48 HOURS'
                )
                self._verify_read_only(sql)
        except ValueError as exc:
            print(f"query failed: {exc}", file=sys.stderr)
            raise
        except Exception as exc:
            print(_query_failure(exc), file=sys.stderr)
            raise QueryExecutionError(_query_failure(exc)) from exc
        relation, columns = self._describe_relation(sql, preview)
        query_id = uuid.uuid4().hex
        table_name = f"query_{query_id}"
        table = quote_identifier(table_name)
        private_ordinal = f"__workbench_snapshot_{query_id}"
        try:
            materialized_sql = ctas_source_sql(relation.sql_query())
            self._connection.execute(
                f"CREATE TABLE workbench_results.{table} AS "
                f"SELECT row_number() OVER () AS {quote_identifier(private_ordinal)}, * "
                f"FROM ({materialized_sql}\n) AS source"
            )
            stored_columns = tuple(self._connection.sql(f"SELECT * FROM workbench_results.{table}").columns)
            columns, row_count = result_columns(self._connection, table, columns, private_ordinal=True)
        except Exception as exc:
            if is_duckdb_internal(exc):
                self._available = False
                print(f"query store unavailable: {exc}", file=sys.stderr)
                raise WorkbenchUnavailableError("query store unavailable; Workbench restart required") from exc
            print(_query_failure(exc), file=sys.stderr)
            raise QueryExecutionError(_query_failure(exc)) from exc
        dependencies, unknown = self._dependencies(sql, source)
        return query_id, _Result(columns, row_count, sql, stored_columns, time.monotonic(), table_name,
                                 preview, dependencies=dependencies, dependencies_unknown=unknown)

    def _dependencies(self, sql: str, source: _Result | None) -> tuple[frozenset[str], bool]:
        if source is not None:
            dependencies, unknown = source.dependencies, source.dependencies_unknown
        else:
            try:
                dependencies = frozenset(name.lower() for name in self._connection.get_table_names(sql))
                unknown = False
            except Exception:
                dependencies = frozenset(name.lower() for name in re.findall(r"(?i)\bquery_[0-9a-f]{32}\b", sql))
                unknown = True
        return dependencies, unknown

    def _describe_relation(self, sql: str, preview: int | None) -> tuple[Any, list[dict[str, Any]]]:
        try:
            relation = self._connection.sql(sql)
            if preview is not None:
                relation = relation.limit(preview)
            columns = [
                {"name": name, "type": str(column_type)}
                for name, column_type in zip(relation.columns, relation.types, strict=True)
            ]
        except Exception as exc:
            print(_query_failure(exc), file=sys.stderr)
            raise QueryExecutionError(_query_failure(exc)) from exc
        return relation, columns

    def _read_page(
        self, query_id: str, result: _Result, offset: int, page_size: int, grid: Grid,
    ) -> dict[str, Any]:
        try:
            query = build_page_query(
                result.table_name, result.stored_columns, grid, page_size=page_size, offset=offset,
            )
            row_count = self._connection.execute(query.count_sql, query.count_parameters).fetchone()[0]
            rows = self._connection.execute(query.page_sql, query.page_parameters).fetchall()
            shaped_rows = [[result_value(value) for value in row[1:len(result.columns) + 1]] for row in rows]
        except ValueError as exc:
            print(f"query result delivery failed: {exc}", file=sys.stderr)
            raise QueryExecutionError(f"query result delivery failed: {exc}") from exc
        except Exception as exc:
            self._available = False
            print(f"query store unavailable: {exc}", file=sys.stderr)
            raise WorkbenchUnavailableError("query store unavailable; Workbench restart required") from exc
        response: dict[str, Any] = {
            "query_id": query_id,
            "sql": result.sql,
            "columns": result.columns,
            "rows": shaped_rows,
            "row_count": row_count,
            "source_row_count": result.row_count,
            "column_count": len(result.columns),
            "offset": offset,
            "page_size": page_size,
            "has_more": offset + len(shaped_rows) < row_count,
        }
        if query.group_column is not None:
            groups: list[dict[str, Any]] = []
            seen: set[str] = set()
            for values, raw in zip(shaped_rows, rows, strict=True):
                value = values[query.group_column]
                key = group_key(value)
                if key not in seen:
                    seen.add(key)
                    groups.append({"value": value, "count": raw[-1]})
            response["groups"] = groups
        return response

    def run(
        self, sql: str, page_size: int = 100, *, preview: int | None = None,
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
                    "query_id": query_id, "sql": sql, "columns": result.columns,
                    "row_count": result.row_count, "column_count": len(result.columns),
                }
            try:
                return self._read_page(query_id, result, 0, page_size, Grid((), (), None))
            except (QueryExecutionError, ValueError):
                self.drop(query_id)
                raise

    def resolve_result_selector(self, selector: str) -> str:
        """Resolve a current result ID or its stable physical table ID."""
        table_name = selector.removeprefix("workbench_results.")
        result_id = table_name.removeprefix("query_")
        if result_id in self._results and not self._results[result_id].released:
            return result_id
        if not table_name.startswith("query_"):
            table_name = f"query_{table_name}"
        for query_id, result in self._results.items():
            if result.table_name == table_name and not result.released:
                return query_id
        raise ValueError("unknown query_id")

    def prepare_result_rebuild(
        self, query_id: str | None = None, *, tables: set[str] | None = None,
    ) -> dict[str, tuple[str, _Result]]:
        """Stage replacement tables inside the caller's transaction and store lock."""
        selected = self.resolve_result_selector(query_id) if query_id is not None else None
        retained = self._retained_result_tables(expire=True)
        if selected is not None and self._results[selected].table_name.lower() not in retained:
            raise ValueError("unknown query_id")
        affected_tables = {name.rsplit(".", 1)[-1].lower() for name in tables or ()}
        staged = {}
        for old_id, old in self._results.items():
            if old.table_name.lower() not in retained:
                continue
            if (selected is not None or tables is not None) and old_id != selected:
                if not affected_tables:
                    continue
                if not old.dependencies_unknown and not affected_tables.intersection(old.dependencies):
                    continue
            new_id, result = self._stage_result_replacement(old)
            staged[old_id] = (new_id, result)
            affected_tables.add(old.table_name)
        return staged

    def _stage_result_replacement(self, old: _Result) -> tuple[str, _Result]:
        new_id, result = self._materialize(old.sql, old.preview, admitted=True, source=old)
        result.created_at, result.pinned, result.released = old.created_at, old.pinned, old.released
        self._connection.execute(f"DROP TABLE workbench_results.{quote_identifier(old.table_name)}")
        self._connection.execute(
            f"ALTER TABLE workbench_results.{quote_identifier(result.table_name)} "
            f"RENAME TO {quote_identifier(old.table_name)}"
        )
        result.table_name = old.table_name
        return new_id, result

    def commit_result_rebuild(self, staged: dict[str, tuple[str, _Result]]) -> dict[str, dict[str, Any]]:
        """Publish staged bookkeeping only after the caller commits SQL."""
        self._results = {
            (staged[key][0] if key in staged else key): (staged[key][1] if key in staged else value)
            for key, value in self._results.items()
        }
        return {old_id: {"query_id": new_id, "row_count": result.row_count,
                         "column_count": len(result.columns)}
                for old_id, (new_id, result) in staged.items() if not result.released}

    def _retained_result_tables(self, *, expire: bool) -> set[str]:
        now = time.monotonic()
        retained = {result.table_name.lower() for result in self._results.values()
                    if not result.released and (not expire or result.pinned
                                                or now - result.created_at < self._result_ttl_seconds)}
        by_table = {result.table_name.lower(): result for result in self._results.values()}
        pending = list(retained)
        while pending:
            result = by_table[pending.pop()]
            for dependency in result.dependencies & by_table.keys() - retained:
                retained.add(dependency)
                pending.append(dependency)
        return retained

    def _prune_results(self, *, expire: bool) -> None:
        retained = self._retained_result_tables(expire=expire)
        for query_id, result in list(self._results.items()):
            if result.table_name.lower() not in retained:
                self._connection.execute(f"DROP TABLE workbench_results.{quote_identifier(result.table_name)}")
                del self._results[query_id]

    def drop(self, query_id: str) -> None:
        """Release one process-local materialized result."""
        with self._lock:
            if not isinstance(query_id, str) or query_id not in self._results or self._results[query_id].released:
                raise ValueError("unknown query_id")
            try:
                self._results[query_id].released = True
                self._prune_results(expire=False)
            except Exception as exc:
                self._available = False
                print(f"query store unavailable: {exc}", file=sys.stderr)
                raise WorkbenchUnavailableError("query store unavailable; Workbench restart required") from exc

    def pin(self, query_id: str) -> None:
        """Keep an existing result while its owner View remains open."""
        with self._lock:
            if not isinstance(query_id, str) or query_id not in self._results:
                raise ValueError("unknown query_id")
            self._results[query_id].pinned = True

    def unpin(self, query_id: str) -> None:
        """Release a View pin without dropping a still-young result."""
        with self._lock:
            if not isinstance(query_id, str) or query_id not in self._results:
                raise ValueError("unknown query_id")
            self._results[query_id].pinned = False

    def prune_results(self) -> None:
        """Drop expired unpinned results when the existing owner performs cleanup."""
        with self._lock:
            try:
                self._prune_results(expire=True)
            except Exception as exc:
                self._available = False
                print(f"query store unavailable: {exc}", file=sys.stderr)
                raise WorkbenchUnavailableError("query store unavailable; Workbench restart required") from exc

    def page(
        self, query_id: str, offset: int, page_size: int = 100, *, preview: int | None = None,
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
                raise WorkbenchUnavailableError("query store unavailable; Workbench restart required")
            if query_id not in self._results or self._results[query_id].released:
                raise ValueError("unknown query_id")
            result = self._results[query_id]
            validate_columns(parsed_grid, len(result.columns))
            if preview is not None:
                page_size = min(page_size, preview)
            return self._read_page(query_id, result, offset, page_size, parsed_grid)

    def check(self, sql: str) -> dict[str, Any]:
        with self._lock:
            query_id, result = self._materialize(sql)
            table = quote_identifier(f"query_{query_id}")
            try:
                self._connection.execute(f"DROP TABLE workbench_results.{table}")
            except Exception as exc:
                self._available = False
                print(f"query store unavailable: {exc}", file=sys.stderr)
                raise WorkbenchUnavailableError("query store unavailable; Workbench restart required") from exc
        return {"valid": True, "columns": result.columns, "row_count": result.row_count,
                "column_count": len(result.columns), "sql": sql}

