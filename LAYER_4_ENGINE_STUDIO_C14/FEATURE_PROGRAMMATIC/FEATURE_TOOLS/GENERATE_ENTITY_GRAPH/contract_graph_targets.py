"""Map exact Subjects to declared contract target categories."""

from __future__ import annotations

from typing import Any

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared \
    import (
        Name as _subject_Name,
        Path as _subject_Path,
        RelationChain as _subject_RelationChain,
        render_subject as _subject_render_subject,
    )  # fmt: skip

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.\
    current_subject_common \
    import (
        _has_selection,
        _model_target,
        _relation_definition_target,
        _target_kind,
        namespace_local_expression,
    )  # fmt: skip

Record = dict[str, Any]

_COMPONENT_ROOTS = {"CFEL", "Carrier", "Term"}


def _relation_name(value: str) -> str:
    return value.removeprefix("Relation//")


def _component_target(
    expression: _subject_Path | _subject_RelationChain,
) -> tuple[str, str] | None:
    """Admit an explicit CFEL component target without making a tree edge.

    ``CFEL <+`` declares a component family. Its right endpoint can itself be
    a component, a dependent Property of a component, or one named component
    instance. These are catalog records only: composition never becomes
    NARROWER_THAN evidence.
    """

    expression = namespace_local_expression(expression) or expression
    if isinstance(expression, _subject_Path):
        return (
            ("component", _subject_render_subject(expression))
            if isinstance(expression.head, _subject_Name)
            and expression.head.value in _COMPONENT_ROOTS
            else None
        )
    first = expression.endpoints[0]
    if (
        isinstance(first.head, _subject_Name)
        and first.head.value == "CFEL"
        and len(expression.endpoints) == 2
        and len(expression.links) == 1
        and expression.links[0].operator == "<+"
        and expression.links[0].relation_type is None
        and isinstance(expression.endpoints[1], _subject_Path)
    ):
        right = expression.endpoints[1]
        kind = _target_kind(right)
        if kind == "primary_node":
            return "component", _subject_render_subject(right)
        if kind in {"property", "instance"}:
            return kind, _model_target(right)
    return None


def _target(
    expression: _subject_Path | _subject_RelationChain,
) -> tuple[str, str] | None:
    "Map an exact active Subject to one already-declarable target category."

    if (
        isinstance(expression, _subject_Path)
        and isinstance(expression.head, _subject_Name)
        and expression.head.value == "ANECHOIC_MODEL"
        and not expression.steps
    ):
        return "namespace", expression.head.value
    expression = namespace_local_expression(expression) or expression
    if _has_selection(expression):
        return None
    relation = _relation_definition_target(expression)
    if relation is not None:
        target, _ = relation
        return "relation", _relation_name(target)
    component = _component_target(expression)
    if component is not None:
        return component
    if isinstance(expression, _subject_Path):
        kind = _target_kind(expression)
        if kind in {"primary_node", "property", "instance"}:
            return kind, _model_target(expression)
        if kind == "relation":
            return "relation", _relation_name(_model_target(expression))
    return None
