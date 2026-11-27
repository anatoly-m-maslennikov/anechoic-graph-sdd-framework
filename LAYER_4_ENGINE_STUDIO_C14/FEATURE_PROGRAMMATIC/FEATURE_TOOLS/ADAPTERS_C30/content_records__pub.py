"""Decode content-record paths and source spans."""

from collections.abc import Mapping
from typing import Any


def records_by_path(
    records: object,
) -> dict[tuple[str, ...], list[Mapping[str, Any]]]:
    result: dict[tuple[str, ...], list[Mapping[str, Any]]] = {}
    if not isinstance(records, list):
        return result
    for record in records:
        if not isinstance(record, Mapping):
            continue
        raw_path = record.get("property_path")
        if not isinstance(raw_path, list) or not all(
            isinstance(part, str) for part in raw_path
        ):
            continue
        result.setdefault(tuple(raw_path), []).append(record)
    return result


def value_excluding_declared_children(
    record: Mapping[str, Any],
    records: Mapping[tuple[str, ...], list[Mapping[str, Any]]],
    declared_children: frozenset[tuple[str, ...]],
    lines: list[str] | None,
) -> tuple[bool, str | None]:
    """Keep presentation headings, subtracting only declared child spans."""
    span = content_record_span(record)
    if span is None or lines is None:
        return False, None
    body_start, end = span[1:]
    children = sorted(
        (
            child_span
            for child_path in declared_children
            for child in records.get(child_path, ())
            if (child_span := content_record_span(child)) is not None
            and body_start <= child_span[0] < end
        ),
        key=lambda child_span: child_span[0],
    )
    parts: list[str] = []
    cursor = body_start
    for child_start, _child_body_start, child_end in children:
        parts.extend(lines[cursor:child_start])
        cursor = child_end
    parts.extend(lines[cursor:end])
    value = "".join(parts)
    return True, value.strip() or None


def content_record_span(
    record: Mapping[str, Any],
) -> tuple[int, int, int] | None:
    start = record.get("_start_line")
    body_start = record.get("_body_start_line")
    end = record.get("_end_line")
    if type(start) is int and type(body_start) is int and type(end) is int:
        return start, body_start, end
    return None
