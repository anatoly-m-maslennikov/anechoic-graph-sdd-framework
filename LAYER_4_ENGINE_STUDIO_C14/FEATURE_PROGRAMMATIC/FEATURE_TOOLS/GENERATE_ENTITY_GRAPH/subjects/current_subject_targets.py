"""Classify and normalize selected Subject targets."""

import re
from dataclasses import replace

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model.notation.notation__shared import (
    DeclaredReference as _subject_DeclaredReference,
    Name as _subject_Name,
    Path as _subject_Path,
    Qualification as _subject_Qualification,
    RelationChain as _subject_RelationChain,
    SelectionGroup as _subject_SelectionGroup,
    SelectionSuffix as _subject_SelectionSuffix,
    namespace_local_expression as _subject_namespace_local_expression,
    render_subject as _subject_render_subject,
)


def namespace_local_expression(
    expression: _subject_Path | _subject_RelationChain | None,
) -> _subject_Path | _subject_RelationChain | None:
    local = (
        _subject_namespace_local_expression(expression)
        if expression is not None
        else None
    )
    if local is not None:
        expression = local
    if isinstance(expression, _subject_Path) and isinstance(
        expression.head, (_subject_Path, _subject_RelationChain)
    ):
        head = namespace_local_expression(expression.head) or expression.head
        if (
            isinstance(head, _subject_Path)
            and head.value_format is None
            and head.value_cardinality is None
        ):
            return replace(
                expression,
                head=head.head,
                steps=(*head.steps, *expression.steps),
            )
    return local


_NAMESPACE_ROOTS = {"ANECHOIC_MODEL", "ANECHOIC_STRUCTURE"}


def _has_selection(node: object) -> bool:
    if isinstance(node, (_subject_SelectionGroup, _subject_SelectionSuffix)):
        return True
    if isinstance(node, _subject_RelationChain):
        return any(_has_selection(endpoint) for endpoint in node.endpoints)
    if isinstance(node, _subject_Path):
        return _has_selection(node.head) or any(
            _has_selection(step.operand) for step in node.steps
        )
    if isinstance(node, _subject_Qualification):
        return _has_selection(node.relative_path)
    if isinstance(node, _subject_DeclaredReference):
        return _has_selection(node.entity)
    return False


def _target_kind(
    expression: _subject_Path | _subject_RelationChain,
) -> str | None:
    ("Classify one declared Path; qualifiers remain "
     "part of that declaration.")  # fmt: skip

    expression = namespace_local_expression(expression) or expression
    if _has_selection(expression):
        return None
    if not isinstance(expression, _subject_Path) or not isinstance(
        expression.head, _subject_Name
    ):
        return None
    if expression.head.value in _NAMESPACE_ROOTS and not expression.steps:
        return None
    if any(
        step.operator in {":", ":="}
        or isinstance(step.operand, _subject_DeclaredReference)
        for step in expression.steps
    ):
        return None
    operators = {step.operator for step in expression.steps}
    root = expression.head.value
    if root == "Relation" and "//" in operators and "." not in operators:
        return "relation"
    if "//" in operators and "." not in operators:
        return "instance"
    if "." in operators and "//" not in operators:
        return "property"
    if not operators or operators == {"/"}:
        return "primary_node"
    return None


def _model_target(expression: _subject_Path) -> str:
    ("Keep top-level allowed literals as constraints "
     "rather than target identities.")  # fmt: skip

    cutoff = next(
        (
            index
            for index, step in enumerate(expression.steps)
            if step.operator in {":", ":="}
        ),
        len(expression.steps),
    )
    if cutoff == len(expression.steps):
        return _subject_render_subject(expression)
    return _subject_render_subject(
        replace(expression, steps=expression.steps[:cutoff])
    )


def _relation_definition_target(
    expression: _subject_Path | _subject_RelationChain,
) -> tuple[str, str] | None:
    ("Find the one direct Relation endpoint declared "
     "by a Relation Definition.")  # fmt: skip

    expression = namespace_local_expression(expression) or expression
    if isinstance(expression, _subject_Path):
        legacy = re.fullmatch(
            r"(?:ANECHOIC_MODEL/)?CFEL/Relation//([A-Za-z_][A-Za-z_0-9]*)",
            _subject_render_subject(expression),
        )
        if legacy is not None:
            return f"Relation//{legacy[1]}", "relation"
    paths = (
        expression.endpoints
        if isinstance(expression, _subject_RelationChain)
        else (expression,)
    )
    candidates = [path for path in paths if _target_kind(path) == "relation"]
    if len(candidates) != 1:
        return None
    target = candidates[0]
    return _model_target(target), "relation"
