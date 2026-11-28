"""Compare declared Content to projected Atom values."""

from pathlib import Path
from typing import Any, Mapping
from ...content_schema import ContentSchema, _declared_children, _value
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    carriers.content.content__shared import (
        records_by_path,
        content_lines,
        source_markdown,
    )  # fmt: skip


def _text(value: object) -> str | None:
    return None if value is None else str(value)


def _content_issues(
    path: Path,
    row: Mapping[str, Any],
    schema: ContentSchema | None,
    public: Mapping[str, Any] | None,
    layouts: dict[tuple[str | None, str | None], dict[tuple[str, ...], str]],
) -> list[tuple[str | None, ...]]:
    reference = row.get("ref") if isinstance(row.get("ref"), str) else None
    prefix = (
        reference,
        path.parent.as_posix(),
        path.name,
        "query_inaccessible_atom",
    )
    if public is None:
        return [
            (
                *prefix,
                None,
                None,
                None,
                "Accepted Atom source has no queryable row.",
            )
        ]
    if schema is None:
        return []
    records, candidates = _content_candidates(row, schema, layouts)
    if not candidates:
        return []
    return _compare_content(row, schema, public, records, candidates, prefix)


def _content_candidates(row, schema, layouts):
    role = row.get("role") if isinstance(row.get("role"), str) else None
    form = row.get("form") if isinstance(row.get("form"), str) else None
    key = (role, form)
    if key not in layouts:
        layouts[key] = {
            rule.path: "content." + ".".join(rule.path)
            for rule in schema.rules
            if rule.value_bearing
            and rule.applies(row)
            and not any(part in {"*", "**"} for part in rule.path)
        }
    records = row.get("content_properties_json")
    if not isinstance(records, list):
        return (), []
    present = {
        tuple(record["property_path"])
        for record in records
        if isinstance(record, dict)
        and isinstance(record.get("property_path"), list)
        and all(isinstance(part, str) for part in record["property_path"])
    }
    candidates = [
        (column_path, name)
        for column_path, name in layouts[key].items()
        if (
            column_path in present
            or column_path[-1:] == ("prose_claim",)
            and column_path[:-1] in present
        )
    ]
    return records, candidates


def _compare_content(row, schema, public, records, candidates, prefix):
    records_by_path_map = records_by_path(records)
    body = source_markdown(row)
    lines = content_lines(body) if body is not None else None
    result = []
    for column_path, name in candidates:
        expected = _value(
            records_by_path_map,
            column_path,
            True,
            _declared_children(schema.rules, column_path, row),
            lines,
        )
        actual = public.get(name)
        if actual != expected:
            result.append(
                (
                    *prefix,
                    name,
                    _text(actual),
                    _text(expected),
                    "Declared Content differs from the query projection.",
                )
            )
    return result
