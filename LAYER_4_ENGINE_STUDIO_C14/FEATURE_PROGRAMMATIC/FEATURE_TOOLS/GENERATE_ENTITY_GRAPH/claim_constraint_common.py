"""Shared primitives for bounded Claim constraint extraction."""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    Name as _subject_Name,
    Path as _subject_Path,
    Qualification as _subject_Qualification,
    SubjectNotationError as _subject_SubjectNotationError,
    parse_subject_expression as _subject_parse_subject_expression,
)

Record = dict[str, Any]
_COUNT = r"(?P<minimum>0|[1-9][0-9]*)(?P<tail>\+|\.\.(?P<maximum>0|[1-9][0-9]*))?"
_MEMBERSHIP_QUALIFIER = re.compile(r"/\(\.[A-Za-z][A-Za-z0-9_. -]*\s+in\s+[A-Za-z][A-Za-z0-9_. -]*\)(?=\.|$)")
_ORDERING = re.compile(r"^(?P<left>.+?)\s*(?P<operator>;>|<;)\s*(?P<right>.+)$")
_ORDERING_ROLE = re.compile(r"^Atom/\(\.Header\.Context\.Role in (RMED|\([A-Za-z, ]+\))\)\.")
_RMED_ROLES = ("Requirement", "Method", "Evaluation", "Delivery")
_OPERATOR_SUBJECT = re.compile(r'(?:^|<\+\s*)CFEL\s*<\+\s*Operator//(?P<name>[A-Za-z_][A-Za-z_0-9]*)\s*$')


def _count(minimum: str | None, tail: str | None, maximum: str | None) -> Record | None:
    if minimum is None:
        return None
    return {
        "minimum": int(minimum),
        "maximum": None if tail == "+" else int(maximum) if maximum else int(minimum),
    }



def _named_property_count(count: Record | None, value_count: Record | None = None) -> Record | None:
    minimum = count["minimum"] if count is not None else int(bool(value_count and value_count["minimum"] > 0))
    maximum = min(1, count["maximum"]) if count and count["maximum"] is not None else 1
    if minimum > maximum:
        return None
    return {"minimum": minimum, "maximum": maximum}



def _record(source: Mapping[str, Any], expression: str, kind: str, **fields: Any) -> Record:
    return {"kind": kind, "expression": expression, "source": dict(source), **fields}



def _property_selector(value: str) -> str | None:
    """Accept only a plain Property path; functions and expressions stay opaque."""

    selector = value.strip()
    plain = _MEMBERSHIP_QUALIFIER.sub("", selector)
    if not plain or any(token in plain for token in ("(", ")", "+", "=", "<", ">", "|", "@", "*", ";", ":", "[", "]", "{", "}", "'", '"')):
        try:
            parsed = _subject_parse_subject_expression(selector, subject_profile="approved").expression
        except _subject_SubjectNotationError:
            return None
        if (not isinstance(parsed, _subject_Path) or parsed.value_format is not None or parsed.value_cardinality is not None
                or not isinstance(parsed.head, _subject_Name)
                or not any(isinstance(step.operand, _subject_Qualification) for step in parsed.steps)
                or any(step.operator not in {"/", "."} or not isinstance(step.operand, (_subject_Name, _subject_Qualification)) for step in parsed.steps)):
            return None
    return selector



def _sibling_order(expression: str) -> Record | None:
    match = _ORDERING.fullmatch(expression)
    if match is None:
        return None
    left, operator, right = match.group("left", "operator", "right")
    qualifier = _ORDERING_ROLE.match(left)
    roles = ()
    if qualifier is not None:
        if not right.startswith(qualifier[0]):
            return None
        role_names = qualifier[1]
        roles = _RMED_ROLES if role_names == "RMED" else tuple(name.strip() for name in role_names[1:-1].split(","))
        if not all(roles):
            return None
        left = "Atom." + left[qualifier.end():]
        right = "Atom." + right[qualifier.end():]
    if not (_property_selector(left) and _property_selector(right)) or "." not in left or "." not in right:
        return None
    bearer, first = left.rsplit(".", 1)
    other_bearer, second = right.rsplit(".", 1)
    if bearer != other_bearer or first == second:
        return None
    source, target = (left, right) if operator == ";>" else (right, left)
    return {"bearer": bearer, "relation": "IS_ORDERED_RIGHT_BEFORE", "relation_notation": operator,
            "source_selector": source, "target_selector": target,
            "source_cardinality": None, "target_cardinality": None,
            "written_direction": "forward" if operator == ";>" else "reverse",
            **({"ordering_roles": roles} if roles else {})}

