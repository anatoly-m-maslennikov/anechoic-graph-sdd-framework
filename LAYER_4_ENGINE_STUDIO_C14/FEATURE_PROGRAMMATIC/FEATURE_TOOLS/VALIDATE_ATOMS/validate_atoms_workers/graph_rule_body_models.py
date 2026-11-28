"""Schemas and cardinality checks for Graph Rule bodies."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from .check_support import Check


class _GraphRulePayload(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    graph_rule_type: str
    applies_to: dict[str, Any]
    condition: dict[str, Any]
    default_value: Any = None


class _WhitelistAppliesTo(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    relation_type: str


class _WhitelistCondition(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    source: list[str]
    target: list[str]


class _CardinalityAppliesTo(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    node: str
    relation_type: str
    direction: str


class _CardinalityCondition(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    other_endpoint: list[str]
    minimum: int = Field(ge=0)
    maximum: int | None = Field(ge=0)


def validate_cardinality(
    rule: _GraphRulePayload,
    payload: dict[str, Any],
    check: Check,
    valid_subjects: Callable[[list[str]], bool],
) -> None:
    if "default_value" in payload:
        check.fail(
            "GRAPH_RULE_BODY",
            "default_value",
            "Cardinality does not allow default_value.",
        )
        return
    try:
        applies_to = _CardinalityAppliesTo.model_validate(rule.applies_to)
        condition = _CardinalityCondition.model_validate(rule.condition)
    except ValidationError:
        check.fail(
            "GRAPH_RULE_BODY",
            "body",
            "Cardinality fields do not match the declared schema.",
        )
        return
    _check_cardinality_values(applies_to, condition, check, valid_subjects)


def _check_cardinality_values(
    applies_to: _CardinalityAppliesTo,
    condition: _CardinalityCondition,
    check: Check,
    valid_subjects: Callable[[list[str]], bool],
) -> None:
    if not applies_to.node.strip() or not valid_subjects([applies_to.node]):
        check.fail(
            "GRAPH_RULE_BODY",
            "applies_to.node",
            "Cardinality node must use Subject notation.",
        )
    if not applies_to.relation_type.strip():
        check.fail(
            "GRAPH_RULE_BODY",
            "applies_to.relation_type",
            "Cardinality relation_type must be nonempty.",
        )
    if applies_to.direction not in {"outgoing", "incoming"}:
        check.fail(
            "GRAPH_RULE_BODY",
            "applies_to.direction",
            "Cardinality direction must be outgoing or incoming.",
        )
    if not valid_subjects(condition.other_endpoint):
        check.fail(
            "GRAPH_RULE_BODY",
            "condition.other_endpoint",
            "Cardinality endpoints must use Subject notation.",
        )
    if condition.maximum is not None and condition.maximum < condition.minimum:
        check.fail(
            "GRAPH_RULE_BODY",
            "condition.maximum",
            "Cardinality maximum must be at least minimum.",
        )


def support_sections_valid(
    body: str, closing: int, check: Check, headings: Any
) -> bool:
    lines = body.splitlines()
    sections: list[tuple[str, int]] = []
    seen: set[str] = set()
    active = False
    for level, title, index in headings(body):
        if index <= closing:
            continue
        if level <= 2:
            active = (
                level == 2
                and title in {"Semantics", "Details"}
                and title not in seen
            )
            if active:
                seen.add(title)
                sections.append((title, index))
            else:
                check.fail(
                    "GRAPH_RULE_BODY",
                    "body",
                    "Only one optional ## Semantics and ## Details section "
                    "may follow the operative block.",
                )
                return False
        elif not active:
            check.fail(
                "GRAPH_RULE_BODY",
                "body",
                "Unsectioned content may not follow the operative block.",
            )
            return False
    return _support_tail_valid(lines, closing, sections, check)


def _support_tail_valid(
    lines: list[str],
    closing: int,
    sections: list[tuple[str, int]],
    check: Check,
) -> bool:
    if not sections:
        if any(line.strip() for line in lines[closing + 1 :]):
            check.fail(
                "GRAPH_RULE_BODY",
                "body",
                "Unsectioned content may not follow the operative block.",
            )
            return False
        return True
    if any(line.strip() for line in lines[closing + 1 : sections[0][1]]):
        check.fail(
            "GRAPH_RULE_BODY",
            "body",
            "Only optional ## Semantics or ## Details sections may follow "
            "the operative block.",
        )
        return False
    return True
