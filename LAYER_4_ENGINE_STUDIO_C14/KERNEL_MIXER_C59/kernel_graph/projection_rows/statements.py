"""Validate caret metadata while DuckDB admits one complete query."""

from __future__ import annotations

import re
from typing import Any

_VIEW = re.compile(
    r"VIEW (?:TABLE|DOC(?:UMENT)?|STRUCTURE|"
    r"(?:GRAPH|IMPORTS)(?: (?:VERTICAL|HORIZONTAL))?)(?: ;)?",
    re.IGNORECASE | re.ASCII,
)


def _utf8(sql: str) -> bytes:
    if not isinstance(sql, str):
        raise ValueError("SQL must be a string")
    try:
        return sql.encode("utf-8")
    except UnicodeEncodeError as error:
        raise ValueError("SQL must be valid UTF-8") from error


def _utf8_offset(sql: str, cursor_position: int) -> int:
    if isinstance(cursor_position, bool) or not isinstance(
        cursor_position, int
    ):
        raise ValueError("cursor_position must be a UTF-16 integer")
    if cursor_position < 0:
        raise ValueError("cursor_position must be a UTF-16 integer")
    units = 0
    byte_offset = 0
    for character in sql:
        if units == cursor_position:
            return byte_offset
        width = 2 if ord(character) > 0xFFFF else 1
        units += width
        byte_offset += len(character.encode("utf-8"))
        if units > cursor_position:
            raise ValueError("cursor_position must be a UTF-16 boundary")
    if units == cursor_position:
        return byte_offset
    raise ValueError("cursor_position is outside SQL")


def token_spans(sql: str) -> list[tuple[bytes, Any]]:
    """Return native DuckDB tokens with their UTF-8 byte slices."""
    import duckdb

    raw = _utf8(sql)
    tokens = duckdb.tokenize(sql)
    return [
        (
            raw[
                position : tokens[index + 1][0]
                if index + 1 < len(tokens)
                else len(raw)
            ],
            token_type,
        )
        for index, (position, token_type) in enumerate(tokens)
    ]


def _execution_sql(sql: str, source: bytes) -> str:
    if "VIEW" not in sql.upper():
        return sql

    import duckdb

    tokens = duckdb.tokenize(sql)
    words, depth = [], 0
    for index, (start, kind) in enumerate(tokens):
        end = tokens[index + 1][0] if index + 1 < len(tokens) else len(source)
        value = source[start:end].decode("utf-8").strip()
        if kind == duckdb.token_type.comment:
            if value.startswith("/*"):
                markers = re.findall(r"/\*|\*/", value)
                if markers.count("/*") != markers.count("*/"):
                    return sql
            continue
        words.append((value, depth, start))
        depth += (value in ("(", "[", "{")) - (value in (")", "]", "}"))

    for index, (value, level, start) in enumerate(words):
        if value.upper() == "VIEW" and level == 0:
            suffix = words[index:]
            if all(item[1] == 0 for item in suffix) and _VIEW.fullmatch(
                " ".join(item[0] for item in suffix)
            ):
                return source[:start].decode("utf-8").rstrip()
    return sql


def select_statement(sql: str, cursor_position: int | None = None) -> str:
    """Validate the caret and omit the trailing View directive."""
    source = _utf8(sql)
    if cursor_position is not None:
        _utf8_offset(sql, cursor_position)
    return _execution_sql(sql, source)
