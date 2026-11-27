"""Primitives for source-bound native Claim helpers."""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

from .claim_constraint_common import _COUNT, _count, _record

Record = dict[str, Any]


def _native_count(value: Any) -> Record | None:
    if type(value) is int and value >= 0:
        return {"minimum": value, "maximum": value}
    if isinstance(value, dict) and set(value) == {"minimum", "maximum"}:
        return value
    return None


def _native_relation(
    source: Mapping[str, Any],
    left: str,
    right: str,
    *,
    relation: str | None = None,
    notation: str | None = None,
    left_count: Record | None = None,
    right_count: Record | None = None,
    expression: str,
    group: str | None,
) -> Record:
    return _record(
        source,
        expression,
        "relation_cardinality",
        source_selector=left,
        relation=relation,
        relation_notation=notation,
        target_selector=right,
        source_cardinality=left_count,
        target_cardinality=right_count,
        written_direction="forward",
        written_source_selector=left,
        written_target_selector=right,
        written_source_cardinality=left_count,
        written_target_cardinality=right_count,
        **({"group": group} if group else {}),
    )


def _helper_count(value: str | None) -> Record | None:
    if value is None:
        return None
    match = re.fullmatch(_COUNT, value)
    if match is None:
        raise ValueError(f"invalid cardinality: {value}")
    return _count(match["minimum"], match["tail"], match["maximum"])


def _count_text(count: Record) -> str:
    minimum, maximum = count["minimum"], count["maximum"]
    return (
        f"{minimum}+"
        if maximum is None
        else str(minimum)
        if maximum == minimum
        else f"{minimum}..{maximum}"
    )
