"""Manage the lifetime of materialized query results."""

from __future__ import annotations

from typing import Any

from . import query_results as runtime


class ResultLifecycle:
    def resolve_result_selector(self, selector: str) -> str:
        """Resolve a current result ID or its stable physical table ID."""
        table_name = selector.removeprefix("workbench_results.")
        result_id = table_name.removeprefix("query_")
        if (
            result_id in self._results
            and not self._results[result_id].released
        ):
            return result_id
        if not table_name.startswith("query_"):
            table_name = f"query_{table_name}"
        for query_id, result in self._results.items():
            if result.table_name == table_name and not result.released:
                return query_id
        raise ValueError("unknown query_id")

    def prepare_result_rebuild(
        self,
        query_id: str | None = None,
        *,
        tables: set[str] | None = None,
    ) -> dict[str, tuple[str, runtime._Result]]:
        """Stage replacement tables under the caller's transaction and lock."""
        selected = (
            self.resolve_result_selector(query_id)
            if query_id is not None
            else None
        )
        retained = self._retained_result_tables(expire=True)
        if (
            selected is not None
            and self._results[selected].table_name.lower() not in retained
        ):
            raise ValueError("unknown query_id")
        affected_tables = {
            name.rsplit(".", 1)[-1].lower() for name in tables or ()
        }
        staged = {}
        for old_id, old in self._results.items():
            if old.table_name.lower() not in retained:
                continue
            if (
                selected is not None or tables is not None
            ) and old_id != selected:
                if not affected_tables:
                    continue
                if (
                    not old.dependencies_unknown
                    and not affected_tables.intersection(old.dependencies)
                ):
                    continue
            new_id, result = self._stage_result_replacement(old)
            staged[old_id] = (new_id, result)
            affected_tables.add(old.table_name)
        return staged

    def _stage_result_replacement(
        self, old: runtime._Result
    ) -> tuple[str, runtime._Result]:
        new_id, result = self._materialize(
            old.sql, old.preview, admitted=True, source=old
        )
        result.created_at, result.pinned, result.released = (
            old.created_at,
            old.pinned,
            old.released,
        )
        self._connection.execute(
            "DROP TABLE workbench_results."
            f"{runtime.quote_identifier(old.table_name)}"
        )
        self._connection.execute(
            "ALTER TABLE workbench_results."
            f"{runtime.quote_identifier(result.table_name)} "
            f"RENAME TO {runtime.quote_identifier(old.table_name)}"
        )
        result.table_name = old.table_name
        return new_id, result

    def commit_result_rebuild(
        self, staged: dict[str, tuple[str, runtime._Result]]
    ) -> dict[str, dict[str, Any]]:
        """Publish staged bookkeeping only after the caller commits SQL."""
        self._results = {
            (staged[key][0] if key in staged else key): (
                staged[key][1] if key in staged else value
            )
            for key, value in self._results.items()
        }
        return {
            old_id: {
                "query_id": new_id,
                "row_count": result.row_count,
                "column_count": len(result.columns),
            }
            for old_id, (new_id, result) in staged.items()
            if not result.released
        }

    def _retained_result_tables(self, *, expire: bool) -> set[str]:
        now = runtime.time.monotonic()
        retained = {
            result.table_name.lower()
            for result in self._results.values()
            if not result.released
            and (
                not expire
                or result.pinned
                or now - result.created_at < self._result_ttl_seconds
            )
        }
        by_table = {
            result.table_name.lower(): result
            for result in self._results.values()
        }
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
                self._connection.execute(
                    "DROP TABLE workbench_results."
                    f"{runtime.quote_identifier(result.table_name)}"
                )
                del self._results[query_id]

    def drop(self, query_id: str) -> None:
        """Release one process-local materialized result."""
        with self._lock:
            if (
                not isinstance(query_id, str)
                or query_id not in self._results
                or self._results[query_id].released
            ):
                raise ValueError("unknown query_id")
            try:
                self._results[query_id].released = True
                self._prune_results(expire=False)
            except Exception as exc:
                self._available = False
                print(
                    f"query store unavailable: {exc}", file=runtime.sys.stderr
                )
                raise runtime.WorkbenchUnavailableError(
                    "query store unavailable; Workbench restart required"
                ) from exc

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
        """Drop expired unpinned results during owner cleanup."""
        with self._lock:
            try:
                self._prune_results(expire=True)
            except Exception as exc:
                self._available = False
                print(
                    f"query store unavailable: {exc}", file=runtime.sys.stderr
                )
                raise runtime.WorkbenchUnavailableError(
                    "query store unavailable; Workbench restart required"
                ) from exc

    def _dependencies(
        self, sql: str, source: runtime._Result | None
    ) -> tuple[frozenset[str], bool]:
        if source is not None:
            dependencies, unknown = (
                source.dependencies,
                source.dependencies_unknown,
            )
        else:
            try:
                dependencies = frozenset(
                    name.lower()
                    for name in self._connection.get_table_names(sql)
                )
                unknown = False
            except Exception:
                dependencies = frozenset(
                    name.lower()
                    for name in runtime.re.findall(
                        r"(?i)\bquery_[0-9a-f]{32}\b", sql
                    )
                )
                unknown = True
        return dependencies, unknown

    def _page_response(
        self,
        query_id,
        result,
        offset,
        page_size,
        query,
        row_count,
        shaped_rows,
        rows,
    ):
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
                key = runtime.group_key(value)
                if key not in seen:
                    seen.add(key)
                    groups.append({"value": value, "count": raw[-1]})
            response["groups"] = groups
        return response
