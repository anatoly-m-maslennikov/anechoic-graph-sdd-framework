"""Execute admitted read-only SQL and keep bounded Project query results."""

import json
import re
import time
from uuid import uuid4

import duckdb

from .result_grid import grid_page, parse_grid
from .result_values import result_value
from .table_names import _REAL_GRAPH_NAMES, _DIAG_NAMES, PUBLIC_NAMES


def validate_preview(value):
    if value is not None and (type(value) is not int or value < 0):
        raise ValueError("preview must be a non-negative integer")
    return value


def validate_select(connection, sql):
    if not isinstance(sql, str) or not 1 <= len(sql) <= 16384:
        raise ValueError("SQL must be a non-empty string of at most 16384 characters")
    statements = connection.extract_statements(sql)
    if len(statements) != 1 or statements[0].type != duckdb.StatementType.SELECT:
        raise ValueError("SQL must contain exactly one SELECT statement")


class ProjectGraphPending(ValueError):
    """A query needs the configured Realization Graph before it is published."""


def _guard_pending_graph(connection, sql):
    try:
        row = connection.execute("SELECT witness FROM ops_generation_reuse").fetchone()
    except duckdb.CatalogException:
        return
    if not row or json.loads(row[0]).get("inputs", {}).get("graph") != "pending":
        return
    names = set(_REAL_GRAPH_NAMES) | set(_DIAG_NAMES)
    names |= {PUBLIC_NAMES[name] for name in names}
    names |= {"mrt_" + name for name in _REAL_GRAPH_NAMES | _DIAG_NAMES}
    names |= {"package_coupling", "architecture_code_metrics", "architecture_ratios", "package_review_profiles", "package_largest_files"}
    names |= {PUBLIC_NAMES[name] for name in names if name in PUBLIC_NAMES}
    tables = {name.lower().split('.')[-1] for name in connection.get_table_names(sql)}
    graph_labels = r"\b(importnode|codeunit|imports|tests|is_tested_by|tests_component|component_is_tested_by|moduleincludes|calls)\b"
    if tables & names or ("graph_table" in sql.lower() and re.search(graph_labels, sql, re.I)):
        raise ProjectGraphPending("Configured Realization Graph is pending")


def query(connection, sql, *, in_transaction=False, preview=None):
    validate_select(connection, sql)
    _guard_pending_graph(connection, sql)
    if not in_transaction:
        connection.execute("BEGIN TRANSACTION READ ONLY")
    try:
        if preview is None:
            cursor = connection.execute(sql)
            description = [(name, str(kind)) for name, kind, *_ in cursor.description]
            raw = cursor.fetchmany(1001)
        else:
            relation = connection.sql(sql).limit(min(preview, 1001))
            description = list(zip(relation.columns, map(str, relation.types), strict=True))
            raw = relation.fetchall()
        if len(raw) > 1000:
            raise ValueError("Query exceeds 1000 rows")
        rows = [tuple(result_value(value) for value in row) for row in raw]
        columns = [
            {"name": name, "type": str(data_type),
             "has_values": not rows or any(row[index] is not None and row[index] != "" for row in rows)}
            for index, (name, data_type) in enumerate(description)
        ]
        return {"columns": columns, "rows": rows}
    finally:
        if not in_transaction:
            connection.execute("ROLLBACK")


def _capture(connection, sql, *, in_transaction=False, preview=None):
    result = query(connection, sql, in_transaction=in_transaction, preview=preview)
    size = len(json.dumps(result, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))
    if size > 1024 * 1024:
        raise ValueError("Query result exceeds one MiB")
    return result, max(4096, size + len(sql.encode("utf-8")))


def _affected(connection, sql, sources):
    try:
        tables = connection.get_table_names(sql)
    except duckdb.Error:
        return True
    return sources <= {table.lower() for table in tables} or "graph_table" in sql.lower()


class QueryResults:
    def __init__(self, ttl_seconds=3600, history=None):
        if type(ttl_seconds) is not int or ttl_seconds <= 0:
            raise ValueError("result_ttl_seconds must be a positive integer")
        self.ttl_seconds = ttl_seconds
        self.history = history
        self.results = {}
        self.pins = set()

    def prune(self):
        now = time.monotonic()
        for query_id, (_, _, created, _, _) in list(self.results.items()):
            if query_id not in self.pins and now - created >= self.ttl_seconds:
                del self.results[query_id]

    def drop(self, query_id):
        self.pins.discard(query_id)
        self.results.pop(query_id, None)

    def run(self, connection, sql, page_size, grid=None, preview=None):
        try:
            result, size = _capture(connection, sql, preview=preview)
            parse_grid(grid, len(result["columns"]))
            self.prune()
            self._check_capacity(sum(item[4] for item in self.results.values()) + size)
            query_id = uuid4().hex
            self.results[query_id] = (sql, result, time.monotonic(), preview, size)
            page = self.page(query_id, 0, page_size, grid)
        except (duckdb.Error, TypeError, ValueError) as error:
            if self.history is not None and isinstance(sql, str) and sql.strip():
                self.history.append(sql, "failed", error=str(error))
            raise
        if self.history is not None:
            self.history.append(sql, "success", row_count=len(result["rows"]), column_count=len(result["columns"]))
        return page

    def _selection(self, connection, target, *, generation=False):
        if not isinstance(target, str):
            raise ValueError("Invalid rebuild target")
        selected = self.results
        if not generation and re.fullmatch(r"[0-9a-f]{32}", target):
            if target not in self.results:
                raise ValueError("Unknown query_id")
            selected = {target: self.results[target]}
        elif target != "all" and (generation or target != "workbench_results"):
            exists = connection.execute("SELECT 1 FROM information_schema.tables WHERE table_name = ?",
                                        [target]).fetchone()
            if not exists:
                raise ValueError("Projection table is unavailable")
            quoted = target.replace('"', '""')
            sources = {name.lower() for name in connection.get_table_names(f'SELECT * FROM "{quoted}"')}
            selected = {key: item for key, item in self.results.items() if _affected(connection, item[0], sources)}
        return selected

    @staticmethod
    def _check_capacity(size):
        if size > 16 * 1024 * 1024:
            raise ValueError("Query result cache is full")

    def stage_generation(self, connection, selected, *, in_transaction=True):
        captured = {}
        size = sum(item[4] for key, item in self.results.items() if key not in selected)
        for key, (sql, _, created, preview, _) in selected.items():
            result, result_size = _capture(connection, sql, in_transaction=in_transaction, preview=preview)
            size += result_size
            self._check_capacity(size)
            captured[key] = (uuid4().hex, sql, result, created, preview, result_size)
        self._check_capacity(size)
        return captured

    def rebuild(self, connection, target):
        self.prune()
        selected = self._selection(connection, target)
        return self.publish(self.stage_generation(connection, selected, in_transaction=False))

    def publish(self, captured):
        replacements = {}
        refreshed = {}
        for old_id, item in self.results.items():
            if old_id not in captured:
                refreshed[old_id] = item
                continue
            new_id, sql, result, created, preview, size = captured[old_id]
            refreshed[new_id] = (sql, result, created, preview, size)
            if old_id in self.pins:
                self.pins.remove(old_id)
                self.pins.add(new_id)
            replacements[old_id] = {"query_id": new_id, "row_count": len(result["rows"]),
                                    "column_count": len(result["columns"])}
        self.results = refreshed
        return replacements

    def page(self, query_id, offset, page_size, grid=None):
        self.prune()
        if not isinstance(query_id, str) or query_id not in self.results:
            raise ValueError("Unknown query_id")
        sql, result, _, _, _ = self.results[query_id]
        columns, rows = result["columns"], result["rows"]
        page, total, groups = grid_page(rows, len(columns), offset, page_size, grid, columns)
        response = {
            "query_id": query_id, "sql": sql, "columns": columns, "rows": page,
            "row_count": total, "source_row_count": len(rows), "column_count": len(columns),
            "offset": offset, "page_size": page_size, "has_more": offset + len(page) < total,
        }
        if groups is not None:
            response["groups"] = groups
        return response
