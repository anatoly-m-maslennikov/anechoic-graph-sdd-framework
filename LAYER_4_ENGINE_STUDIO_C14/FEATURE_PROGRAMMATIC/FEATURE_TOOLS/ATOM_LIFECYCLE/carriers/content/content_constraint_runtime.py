"""Validate compiled Content constraints and their records."""

from . import content_constraints__shared as owner


def _applies(row, record):
    roles, forms = record[2:4]
    return (
        roles is None
        or any(
            owner.matches_named_value(row.get("role"), role) for role in roles
        )
    ) and (
        forms is None
        or any(
            owner.matches_named_value(row.get("form"), form) for form in forms
        )
    )


def _check_children(path, low, high, children, source, paths, declared):
    if path not in paths:
        return
    actual = [
        item[-1] for item in paths if item[:-1] == path and item in declared
    ]
    if (
        (children and any(name not in children for name in actual))
        or not low <= len(actual) <= high
        or len(actual) != len(set(actual))
    ):
        raise ValueError(
            f"Content {'.'.join(path)} requires {low}..{high} unique children "
            f"from {', '.join(children)} ({source})"
        )


def _check_values(path, low, high, source, paths, declared, by_path, lines):
    if path not in paths:
        return
    declared_children = frozenset(
        child for child in declared if child[:-1] == path
    )
    count = sum(
        bool(
            owner.value_excluding_declared_children(
                item, by_path, declared_children, lines
            )[1]
        )
        for item in by_path.get(path, ())
    )
    if not low <= count <= high:
        raise ValueError(
            f"Content {'.'.join(path)} requires {low}..{high} "
            f"direct Markdown values ({source})"
        )


def _check_record(record, paths, declared, by_path, lines, ordering):
    kind, path, _roles, _forms, low, high, children, source = record
    if kind == "order":
        ordering.setdefault((path, source), []).append(children)
    elif kind == "children":
        _check_children(path, low, high, children, source, paths, declared)
    elif kind == "heading" and not low <= paths.count(path) <= high:
        raise ValueError(
            f"Content {'.'.join(path)} requires {low}..{high} "
            f"occurrences ({source})"
        )
    elif kind in {"value", "heading_value"}:
        _check_values(path, low, high, source, paths, declared, by_path, lines)


def _check_order(paths, ordering):
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.structure.structure__shared import (
        order_properties,
    )

    for (path, source), pairs in ordering.items():
        actual = [item[-1] for item in paths if item[:-1] == path]
        ordered_names = {name for pair in pairs for name in pair}
        relevant = [name for name in actual if name in ordered_names]
        if relevant != order_properties(relevant, pairs):
            raise ValueError(
                f"Content {'.'.join(path) or 'root'} Properties "
                f"are out of order ({source})"
            )


def validate(constraints, row):
    body = owner.source_markdown(row)
    parsed = (
        owner.parse_content(body, tolerate_duplicate_siblings=True)
        if isinstance(body, str)
        else []
    )
    paths = [tuple(item["property_path"]) for item in parsed]
    applicable = [
        record for record in constraints.records if _applies(row, record)
    ]
    declared = {
        path
        for kind, path, *_ in applicable
        if kind not in {"children", "order"}
    }
    for kind, path, _, _, _, _, children, _ in applicable:
        if kind in {"children", "order"}:
            declared.update((*path, child) for child in children)
    by_path = owner.records_by_path(parsed)
    lines = owner.content_lines(body) if isinstance(body, str) else None
    ordering = {}
    for record in applicable:
        _check_record(record, paths, declared, by_path, lines, ordering)
    _check_order(paths, ordering)


def _valid_names(value, nullable=False):
    return (value is None and nullable) or (
        isinstance(value, list)
        and all(isinstance(x, str) and x for x in value)
        and len(value) == len(set(value))
    )


def _record_fields(item, source_ids):
    if not isinstance(item, dict) or set(item) != {
        "kind",
        "path",
        "roles",
        "forms",
        "min",
        "max",
        "children",
        "source",
    }:
        raise ValueError("invalid Content constraint")
    return _checked_record_fields(item, source_ids)


def _checked_record_fields(item, source_ids):
    kind, path, roles, forms, low, high, children, source = (
        item[k]
        for k in (
            "kind",
            "path",
            "roles",
            "forms",
            "min",
            "max",
            "children",
            "source",
        )
    )
    if (
        kind not in ("heading", "value", "heading_value", "children", "order")
        or not _valid_names(path)
        or (not path and kind != "order")
        or not _valid_names(roles, True)
        or not _valid_names(forms, True)
        or not _valid_names(children)
        or type(low) is not int
        or type(high) is not int
        or (kind not in ("children", "order") and bool(children))
        or (kind == "order" and (len(children) != 2 or low != 0 or high != 0))
        or low < 0
        or high < low
        or not isinstance(source, str)
        or source not in source_ids
    ):
        raise ValueError("invalid Content constraint")
    return (
        kind,
        tuple(path),
        None if roles is None else tuple(roles),
        None if forms is None else tuple(forms),
        low,
        high,
        tuple(children),
        source,
    )


def load_content_constraints(records, source_ids):
    if not isinstance(records, list):
        raise ValueError("invalid Content constraints")
    result, seen = [], set()
    for item in records:
        key = _record_fields(item, source_ids)
        if key in seen:
            raise ValueError("duplicate Content constraint")
        seen.add(key)
        result.append(key)
    return owner.ContentConstraints(tuple(result))
