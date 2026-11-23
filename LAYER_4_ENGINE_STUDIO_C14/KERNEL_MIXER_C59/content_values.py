"""Extract declared Content values from Markdown records."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import value_excluding_declared_children
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import direct_markdown, section_markdown


def _value(
    records: Mapping[tuple[str, ...], list[Mapping[str, Any]]], path: tuple[str, ...], applies: bool,
    declared_children: frozenset[tuple[str, ...]], lines: list[str] | None,
) -> str | None:
    if not applies:
        return None
    if path[-1:] == ("prose_claim",):
        prose = _prose_claim(records, path, declared_children, lines)
        if prose is not None:
            return prose
    record = next(iter(records.get(path, ())), None)
    if record is not None:
        spans_available, value = value_excluding_declared_children(
            record, records, declared_children, lines,
        )
        if not spans_available:
            value = direct_markdown(
                record, (candidate for group in records.values() for candidate in group), lines,
            )
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _prose_claim(
    records: Mapping[tuple[str, ...], list[Mapping[str, Any]]], path: tuple[str, ...],
    declared_children: frozenset[tuple[str, ...]], lines: list[str] | None,
) -> str | None:
    """Keep undeclared prose headings, subtracting exact declared child spans."""
    record = next(iter(records.get(path, ())), None)
    if record is None:
        return _legacy_prose_claim(records, path[:-1], lines)
    spans_available, value = value_excluding_declared_children(
        record, records, declared_children, lines,
    )
    if spans_available:
        return value
    section = section_markdown(record, lines)
    if section is None:
        return None
    value = section.split("\n", 1)[1] if "\n" in section else ""
    return value.strip() or None


def _legacy_prose_claim(
    records: Mapping[tuple[str, ...], list[Mapping[str, Any]]], parent_path: tuple[str, ...],
    lines: list[str] | None,
) -> str | None:
    """Retain admitted direct Claim prose while removing declared Claim children."""
    parent = next(iter(records.get(parent_path, ())), None)
    if parent is None:
        return None
    section = section_markdown(parent, lines)
    if section is None:
        return None
    value = section.split("\n", 1)[1] if "\n" in section else ""
    for child_name in ("formal_claim", "prose_claim"):
        child = next(iter(records.get((*parent_path, child_name), ())), None)
        child_section = section_markdown(child, lines) if child is not None else None
        if child_section is not None:
            value = value.replace(child_section, "", 1)
    return value.strip() or None


