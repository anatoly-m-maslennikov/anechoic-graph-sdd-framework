from __future__ import annotations

from .subject_notation_expression import _RESERVED
from .subject_notation_types import (
    Cardinality,
    DeclaredReference,
    InitialAtomSelector,
    MembershipPredicate,
    Name,
    ParsedSubject,
    Path,
    Qualification,
    RelationChain,
    SelectionGroup,
    SelectionSuffix,
    ValueLiteral,
)


def _escaped_name(value: str) -> str:
    return "".join(
        "\\" + character
        if character in _RESERVED
        or (character.isspace() and index in (0, len(value) - 1))
        else character
        for index, character in enumerate(value)
    )


def render_subject(parsed: ParsedSubject | Path | RelationChain) -> str:
    """Render a canonical, idempotent Subject while \
preserving written direction."""

    if isinstance(parsed, ParsedSubject):
        return render_subject(parsed.expression)
    if isinstance(parsed, RelationChain):
        result = render_subject(parsed.endpoints[0])
        for link, endpoint in zip(
            parsed.links, parsed.endpoints[1:], strict=True
        ):
            operator = (
                ("<((" if link.operator == "<((" else "((")
                + _escaped_name(link.relation_type.value)
                + "))"
                if link.relation_type
                else link.operator
            )
            result += (
                " "
                + _render_cardinality(link.forward_cardinality)
                + operator
                + _render_cardinality(link.reverse_cardinality)
                + " "
                + render_subject(endpoint)
            )
        return result
    head = parsed.head
    if isinstance(head, (Path, RelationChain)):
        result = "(" + render_subject(head) + ")"
    else:
        result = _render_operand(head)
    for step in parsed.steps:
        result += step.operator + _render_operand(step.operand)
    if parsed.value_format is not None:
        result += "[" + _escaped_name(parsed.value_format.value) + "]"
    return result + _render_cardinality(parsed.value_cardinality)


def _render_operand(
    node: Name
    | ValueLiteral
    | MembershipPredicate
    | InitialAtomSelector
    | Qualification
    | DeclaredReference
    | Path
    | RelationChain
    | SelectionGroup
    | SelectionSuffix,
) -> str:
    if isinstance(node, MembershipPredicate):
        values = ", ".join(_render_operand(value) for value in node.values)
        return f"(.{_escaped_name(node.property.value)} in ({values}))"
    if isinstance(node, SelectionGroup):
        return (
            "("
            + ",".join(render_subject(member) for member in node.members)
            + ")"
        )
    if isinstance(node, SelectionSuffix):
        return node.value
    if isinstance(node, InitialAtomSelector):
        return (
            "atom("
            + ",".join(
                key + '="' + value + '"'
                for key, value in node.selector.items()
            )
            + ")"
        )
    if isinstance(node, Qualification):
        return "(." + render_subject(node.relative_path) + ")"
    if isinstance(node, DeclaredReference):
        if isinstance(node.entity, Path):
            return "@(" + render_subject(node.entity) + ")"
        return "@" + _escaped_name(node.entity.value)
    if isinstance(node, (Path, RelationChain)):
        return "(" + render_subject(node) + ")"
    return _render_literal(node)


def _render_literal(node):
    if (
        isinstance(node, ValueLiteral)
        and '"' not in node.value
        and "\\" not in node.value
        and any(character in _RESERVED for character in node.value)
    ):
        return '"' + node.value + '"'
    return _escaped_name(node.value)


def _render_cardinality(cardinality: Cardinality | None) -> str:
    if cardinality is None:
        return ""
    minimum, maximum = cardinality.minimum, cardinality.maximum
    value = str(minimum) + (
        "+"
        if maximum is None
        else ""
        if minimum == maximum
        else ".." + str(maximum)
    )
    return "{" + value + "}"
