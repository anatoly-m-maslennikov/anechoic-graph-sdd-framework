"""Collect and count observed Header values."""

from collections.abc import Mapping
import datetime as dt
import re
from typing import Any

from pydantic import ConfigDict
from pydantic.dataclasses import dataclass

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    sources.inventory.inventory__shared import (
        canonical,
    )  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    sources.inventory.inventory__shared import (
        json_value,
    )  # fmt: skip

_NAME = re.compile(r"[^a-z0-9_]")
_SEPARATORS = re.compile(r"[\s-]+")


@dataclass(config=ConfigDict(strict=True, extra="forbid"), frozen=True)
class _Contribution:
    values: tuple[tuple[tuple[str, ...], str | None, bool], ...]
    direct: frozenset[tuple[str, ...]]


def _source_key(row: Mapping[str, Any], index: int) -> str:
    path = row.get("source_path")
    return path if isinstance(path, str) and path else f"<row:{index}>"


def _contribution(row: Mapping[str, Any]) -> _Contribution | None:
    header = row.get("header_json")
    if not isinstance(header, Mapping):
        return None
    values: list[tuple[tuple[str, ...], str | None, bool]] = []
    direct: set[tuple[str, ...]] = set()
    _collect_contribution(header, values, direct)
    return _Contribution(tuple(values), frozenset(direct))


def _collect_contribution(
    value: Mapping[str, Any],
    values: list[tuple[tuple[str, ...], str | None, bool]],
    direct: set[tuple[str, ...]],
    prefix: tuple[str, ...] = (),
) -> None:
    for key, item in value.items():
        if not isinstance(key, str):
            raise ValueError("Header SQL properties require string keys")
        path = (*prefix, key)
        if not path[:-1] and key == "relations":
            continue
        values.append(
            (
                path,
                _value_format(item) if item is not None else None,
                not _empty(item),
            )
        )
        if path == ("context", "container"):
            direct.add(path)
        if isinstance(item, Mapping):
            if item:
                _collect_contribution(item, values, direct, path)
            else:
                direct.add(path)
        else:
            direct.add(path)


def _add(
    contribution: _Contribution,
    direct_counts: dict[tuple[str, ...], int],
    format_counts: dict[tuple[str, ...], dict[str, int]],
    populated_counts: dict[tuple[str, ...], int],
) -> None:
    for path in contribution.direct:
        direct_counts[path] = direct_counts.get(path, 0) + 1
    for path, format_name, populated in contribution.values:
        if format_name is not None:
            formats = format_counts.setdefault(path, {})
            formats[format_name] = formats.get(format_name, 0) + 1
        if populated:
            populated_counts[path] = populated_counts.get(path, 0) + 1


def _remove(
    contribution: _Contribution,
    direct_counts: dict[tuple[str, ...], int],
    format_counts: dict[tuple[str, ...], dict[str, int]],
    populated_counts: dict[tuple[str, ...], int],
) -> None:
    for path in contribution.direct:
        _decrement(direct_counts, path)
    for path, format_name, populated in contribution.values:
        if format_name is not None:
            formats = format_counts[path]
            _decrement(formats, format_name)
            if not formats:
                format_counts.pop(path)
        if populated:
            _decrement(populated_counts, path)


def _decrement(counts: dict[Any, int], key: Any) -> None:
    if counts[key] == 1:
        counts.pop(key)
    else:
        counts[key] -= 1


def _column_name(path: tuple[str, ...]) -> str:
    parts = []
    for part in path:
        normalized = _NAME.sub(
            "", _SEPARATORS.sub("_", part.casefold())
        ).strip("_")
        if not normalized:
            raise ValueError(
                f"Header SQL property has no usable name: {'.'.join(path)}"
            )
        parts.append(normalized)
    return "header." + ".".join(parts)


def _empty(value: object) -> bool:
    return value is None or value == "" or value == [] or value == {}


def _value_format(value: object) -> str:
    if type(value) is bool:
        return "BOOLEAN"
    if type(value) is int and -(2**63) <= value < 2**63:
        return "BIGINT"
    if type(value) is float:
        return "DOUBLE"
    if isinstance(value, str):
        return "VARCHAR"
    if isinstance(value, dt.datetime):
        return "TIMESTAMPTZ" if value.tzinfo is not None else "TIMESTAMP"
    if isinstance(value, dt.date):
        return "DATE"
    if isinstance(value, dt.time):
        return "TIME"
    try:
        canonical(json_value(value))
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"Header SQL property has unsupported value: {value!r}"
        ) from exc
    return "JSON"


def _matches_format(value: object, format_name: str) -> bool:
    if format_name == "VARCHAR":
        return isinstance(value, str)
    if format_name == "BIGINT":
        return type(value) is int and -(2**63) <= value < 2**63
    if format_name == "BOOLEAN":
        return type(value) is bool
    if format_name == "TIMESTAMPTZ":
        return (
            isinstance(value, dt.datetime)
            and value.tzinfo is not None
            and value.utcoffset() is not None
        )
    if format_name != "JSON":
        return False
    try:
        canonical(json_value(value))
    except TypeError, ValueError:
        return False
    return True
