"""Bind qualified properties to declared contract targets."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import replace
from typing import Any

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model.notation.notation__shared import (
    Path as _subject_Path,
    Qualification as _subject_Qualification,
    RelationChain as _subject_RelationChain,
    render_subject as _subject_render_subject,
)
from ..subjects.subjects__shared import (
    _has_selection,
    namespace_local_expression,
)
from .contract_graph_targets import _target
from ._contract_graph_multi_qualification import (
    _multiple_qualification as _multiple_qualification,
)


Record = dict[str, Any]


def _axis_target(expression, catalog):
    if len(expression.links) != 1 or expression.links[0].operator not in {
        ">|",
        "|<",
    }:
        return None
    subject, axis = (
        (expression.endpoints[0], expression.endpoints[1])
        if expression.links[0].operator == ">|"
        else (expression.endpoints[1], expression.endpoints[0])
    )
    target = _target(subject)
    if target is not None and target in catalog:
        return (
            target,
            "axis_context",
            {"axis": _subject_render_subject(axis)},
        )
    return None


def _conditional_target(
    expression: _subject_Path | _subject_RelationChain,
    catalog: Mapping[tuple[str, str], list[Record]],
) -> tuple[tuple[str, str], str, Record] | None:
    """Bind only known value or qualifier conditions to an existing target.

    The condition remains on the source entry.  It neither admits a qualified
    Node nor expands a selector over possible model targets.
    """

    expression = namespace_local_expression(expression) or expression
    if _has_selection(expression):
        return None
    if isinstance(expression, _subject_RelationChain):
        return _axis_target(expression, catalog)
    if not isinstance(expression, _subject_Path):
        return None
    for index, step in enumerate(expression.steps):
        if step.operator not in {":", ":="}:
            continue
        base = replace(
            expression,
            steps=expression.steps[:index],
            value_format=None,
            value_cardinality=None,
        )
        target = _target(base)
        if (
            target is not None
            and target[0] == "property"
            and target in catalog
        ):
            return (
                target,
                "allowed_value_condition",
                {"condition": _subject_render_subject(expression)},
            )

    return (
        _multiple_qualification(expression, catalog)
        or _inherited_qualification(expression, catalog)
        or _single_qualification(expression, catalog)
    )


def _condition_marker(condition):
    marker = next(
        (
            position
            for position, item in enumerate(condition.steps)
            if item.operator == ":="
        ),
        None,
    )
    if marker is None or any(
        item.operator != ":=" for item in condition.steps[marker:]
    ):
        return None
    return marker


def _inherited_result(target, property_key, condition):
    return (
        target,
        "inherited_property_qualification",
        {
            "property": property_key[1],
            "condition": _subject_render_subject(condition),
        },
    )


def _inherited_at(expression, catalog, index):
    step = expression.steps[index]
    if step.operator != "/" or not isinstance(
        step.operand, (_subject_Path, _subject_Qualification)
    ):
        return None
    condition = (
        step.operand.relative_path
        if isinstance(step.operand, _subject_Qualification)
        else step.operand
    )
    marker = _condition_marker(condition)
    if marker is None:
        return None
    base = replace(
        expression,
        steps=expression.steps[:index],
        value_format=None,
        value_cardinality=None,
    )
    target = _target(base)
    if target is None or target not in catalog:
        return None
    root = replace(base, steps=(), value_format=None, value_cardinality=None)
    root_target = _target(root)
    property_path = replace(
        condition,
        steps=condition.steps[:marker],
        value_format=None,
        value_cardinality=None,
    )
    if root_target is None:
        return None
    property_key = (
        "property",
        root_target[1] + "." + _subject_render_subject(property_path),
    )
    if property_key in catalog:
        return _inherited_result(target, property_key, condition)


def _inherited_qualification(expression, catalog):
    for index in range(len(expression.steps) - 1, 0, -1):
        selected = _inherited_at(expression, catalog, index)
        if selected is not None:
            return selected


def _single_property(qualifier, target, catalog):
    relative = qualifier.relative_path
    conditional = next(
        (
            position
            for position, step in enumerate(relative.steps)
            if step.operator == ":="
        ),
        None,
    )
    if conditional is None or any(
        step.operator not in {":="} for step in relative.steps[conditional:]
    ):
        return None
    property_path = replace(
        relative,
        steps=relative.steps[:conditional],
        value_format=None,
        value_cardinality=None,
    )
    property_target = target[1] + "." + _subject_render_subject(property_path)
    property_key = ("property", property_target)
    return (
        (
            target,
            "property_qualification",
            {
                "property": property_key[1],
                "condition": _subject_render_subject(relative),
            },
        )
        if property_key in catalog
        else None
    )


def _single_qualification(expression, catalog):
    qualifiers = [
        (index, step.operand)
        for index, step in enumerate(expression.steps)
        if step.operator == "/"
        and isinstance(step.operand, _subject_Qualification)
    ]
    if len(qualifiers) != 1:
        return None
    index, qualifier = qualifiers[0]
    base = replace(
        expression,
        steps=expression.steps[:index],
        value_format=None,
        value_cardinality=None,
    )
    target = _target(base)
    if (
        target is None
        or target not in catalog
        or target[0] not in {"primary_node", "instance", "component"}
    ):
        return None
    return _single_property(qualifier, target, catalog)
