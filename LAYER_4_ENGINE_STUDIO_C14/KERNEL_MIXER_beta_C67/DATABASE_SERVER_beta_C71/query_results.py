"""Execute admitted read-only SQL and keep bounded Project query results."""

import json
import re
import time
from uuid import uuid4

import duckdb

from .result_grid import grid_page, parse_grid
from .result_values import result_value


def validate_preview(value):
    if value is not None and (type(value) is not int or value < 0):
        raise ValueError("preview must be a non-negative integer")
    return value


def query(connection, sql, *, in_transaction=False, preview=None):
    if not isinstance(sql, str) or not 1 <= len(sql) <= 16384:
        raise ValueError("SQL must be a non-empty string of at most 16384 characters")
    statements = connection.extract_statements(sql)
    if len(statements) != 1 or statements[0].type != duckdb.StatementType.SELECT:
        raise ValueError("SQL must contain exactly one SELECT statement")
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
    if len(json.dumps(result, ensure_ascii=False, separators=(",", ":")).encode("utf-8")) > 1024 * 1024:
        raise ValueError("Query result exceeds one MiB")
    return result


def _affected(connection, sql, target):
    try:
        tables = connection.get_table_names(sql)
    except duckdb.Error:
        return True
    return target in {table.lower() for table in tables} or "graph_table" in sql.lower()


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
        for query_id, (_, _, created, _) in list(self.results.items()):
            if query_id not in self.pins and now - created >= self.ttl_seconds:
                del self.results[query_id]

    def drop(self, query_id):
        self.pins.discard(query_id)
        self.results.pop(query_id, None)

    def run(self, connection, sql, page_size, grid=None, preview=None):
        try:
            result = _capture(connection, sql, preview=preview)
            parse_grid(grid, len(result["columns"]))
            self.prune()
            if len(self.results) >= 16:
                victim = next((key for key in self.results if key not in self.pins), None)
                if victim is None:
                    raise ValueError("Query result cache is full")
                del self.results[victim]
            query_id = uuid4().hex
            self.results[query_id] = (sql, result, time.monotonic(), preview)
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
            selected = {key: item for key, item in self.results.items() if _affected(connection, item[0], target)}
        return selected

    def stage_generation(self, connection, selected):
        return {key: (uuid4().hex, sql, _capture(connection, sql, in_transaction=True, preview=preview), created, preview)
                for key, (sql, _, created, preview) in selected.items()}

    def rebuild(self, connection, target):
        self.prune()
        selected = self._selection(connection, target)
        captured = {key: (uuid4().hex, sql, _capture(connection, sql, preview=preview), created, preview)
                    for key, (sql, _, created, preview) in selected.items()}
        return self.publish(captured)

    def publish(self, captured):
        replacements = {}
        refreshed = {}
        for old_id, item in self.results.items():
            if old_id not in captured:
                refreshed[old_id] = item
                continue
            new_id, sql, result, created, preview = captured[old_id]
            refreshed[new_id] = (sql, result, created, preview)
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
        sql, result, _, _ = self.results[query_id]
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
