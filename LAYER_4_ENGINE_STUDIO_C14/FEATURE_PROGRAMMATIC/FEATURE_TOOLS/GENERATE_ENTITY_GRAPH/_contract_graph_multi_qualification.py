"""Resolve multi-qualification conditions against declared targets."""

from dataclasses import replace

from ..ADAPTERS_C30.ADAPTERS_C30__shared import (
    Qualification as _subject_Qualification,
    render_subject as _subject_render_subject,
)
from .contract_graph_targets import _target


def _multiple_qualification(expression, catalog):
    qualifiers = [
        (index, step.operand)
        for index, step in enumerate(expression.steps)
        if step.operator == "/"
        and isinstance(step.operand, _subject_Qualification)
    ]
    return _multi_colon(expression, catalog, qualifiers) or _multi_assignment(
        expression, catalog, qualifiers
    )


def _colon_properties(expression, qualifiers):
    properties = []
    for index, qualifier in qualifiers:
        relative = qualifier.relative_path
        marker = next(
            (
                i
                for i, step in enumerate(relative.steps)
                if step.operator == ":"
            ),
            None,
        )
        anchor_steps = tuple(
            step
            for step in expression.steps[:index]
            if not (
                step.operator == "/"
                and isinstance(step.operand, _subject_Qualification)
            )
        )
        anchor = _target(
            replace(
                expression,
                steps=anchor_steps,
                value_format=None,
                value_cardinality=None,
            )
        )
        if (
            marker is None
            or anchor is None
            or any(step.operator != ":" for step in relative.steps[marker:])
        ):
            break
        path = replace(
            relative,
            steps=relative.steps[:marker],
            value_format=None,
            value_cardinality=None,
        )
        properties.append(anchor[1] + "." + _subject_render_subject(path))
    return properties


def _multi_colon(expression, catalog, qualifiers):
    if qualifiers and all(
        any(step.operator == ":" for step in qualifier.relative_path.steps)
        for _, qualifier in qualifiers
    ):
        base = replace(
            expression,
            steps=tuple(
                step
                for step in expression.steps
                if not (
                    step.operator == "/"
                    and isinstance(step.operand, _subject_Qualification)
                )
            ),
            value_format=None,
            value_cardinality=None,
        )
        target = _target(base)
        properties = _colon_properties(expression, qualifiers)
        if (
            target in catalog
            and len(properties) == len(qualifiers)
            and all(("property", prop) in catalog for prop in properties)
        ):
            return (
                target,
                "property_qualification",
                {
                    "properties": properties,
                    "condition": _subject_render_subject(expression),
                },
            )


def _assignment_properties(qualifiers, target):
    properties = []
    for _, qualifier in qualifiers:
        relative = qualifier.relative_path
        marker = next(
            (
                i
                for i, step in enumerate(relative.steps)
                if step.operator == ":="
            ),
            None,
        )
        if marker is None or any(
            step.operator != ":=" for step in relative.steps[marker:]
        ):
            break
        path = replace(
            relative,
            steps=relative.steps[:marker],
            value_format=None,
            value_cardinality=None,
        )
        properties.append(
            target[1] + "." + _subject_render_subject(path) if target else ""
        )
    return properties


def _multi_assignment(expression, catalog, qualifiers):
    if len(qualifiers) > 1 and [index for index, _ in qualifiers] == list(
        range(qualifiers[0][0], len(expression.steps))
    ):
        base = replace(
            expression,
            steps=expression.steps[: qualifiers[0][0]],
            value_format=None,
            value_cardinality=None,
        )
        target = _target(base)
        properties = _assignment_properties(qualifiers, target)
        if (
            target in catalog
            and target[0] in {"primary_node", "instance", "component"}
            and len(properties) == len(qualifiers)
            and all(
                ("property", property) in catalog for property in properties
            )
        ):
            return (
                target,
                "property_qualification",
                {
                    "properties": properties,
                    "condition": _subject_render_subject(expression),
                },
            )
