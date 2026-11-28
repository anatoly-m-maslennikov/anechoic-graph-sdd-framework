"""Parse the syntax allowed in an authored Concern Path."""

from dataclasses import replace

from ...model.notation import subject_notation__pub as notation
from ...model.notation.subject_notation_expression import _ExpressionParser

PROJECT_COMPONENTS_CONCERN_PATH = "Project Structure.components"

CONCERN_OPERATORS = {
    "is_contained_by": "/",
    "is_narrower_than": "//",
    "is_property_of": ".",
    "has_axis": " >| ",
    "classifies": " >| ",
}


def parse_concern_path(text):
    if not isinstance(text, str) or not text.strip() or len(text) > 16384:
        raise ValueError(
            "Concern Path must be nonempty text within the length limit"
        )
    parser = _ExpressionParser(text, concern_path=True)
    expression = parser.expression(initial=False)
    parser.whitespace()
    if parser.position != len(text):
        raise ValueError("Invalid Concern Path")
    _check_expression(expression)
    return expression


def _check_expression(expression):
    if isinstance(expression, notation.RelationChain):
        if any(
            link.operator not in {">|", "|<"}
            or link.relation_type is not None
            or link.forward_cardinality is not None
            or link.reverse_cardinality is not None
            for link in expression.links
        ):
            raise ValueError("Unsupported Concern Path relation")
        for endpoint in expression.endpoints:
            _check_expression(endpoint)
        return
    if (
        not isinstance(expression, notation.Path)
        or expression.value_format is not None
        or expression.value_cardinality is not None
    ):
        raise ValueError("Invalid Concern Path")
    if not isinstance(expression.head, notation.Name):
        _check_expression(expression.head)
    for index, step in enumerate(expression.steps):
        _check_step(expression, index, step)


def _check_step(expression, index, step):
    if step.operator not in {"/", "//", ".", ":="}:
        raise ValueError("Unsupported Concern Path operator")
    if isinstance(step.operand, notation.SelectionSuffix):
        if (
            step.operator != "//"
            or step.operand.value != ""
            or index == 0
            or expression.steps[index - 1].operator != "//"
            or index + 1 == len(expression.steps)
            or expression.steps[index + 1].operator != "."
        ):
            raise ValueError("Invalid Concern Path scope boundary")
    elif step.operator == ":=":
        if not isinstance(step.operand, notation.ValueLiteral):
            raise ValueError("Invalid Concern Path value")
    elif isinstance(step.operand, notation.Qualification):
        _check_expression(step.operand.relative_path)
    elif not isinstance(
        step.operand, (notation.Name, notation.MembershipPredicate)
    ):
        _check_expression(step.operand)


def concern_path_parts(text):
    """Return the ordered operators and labels of an authored Concern Path."""
    expression = parse_concern_path(text)
    if isinstance(expression, notation.RelationChain):
        return _chain_parts(expression)
    prefix = notation.render_subject(replace(expression, steps=()))
    parts = [("", prefix)]
    for index, step in enumerate(expression.steps, 1):
        address = notation.render_subject(
            replace(expression, steps=expression.steps[:index])
        )
        label = address.removeprefix(prefix + step.operator)
        if label:
            parts.append((step.operator, label))
        prefix = address
    return tuple(parts)


def _chain_parts(expression):
    parts = concern_path_parts(
        notation.render_subject(expression.endpoints[0])
    )
    return parts + tuple(
        (link.operator, notation.render_subject(endpoint))
        for link, endpoint in zip(
            expression.links, expression.endpoints[1:], strict=True
        )
    )


def concern_locator_parts(concern):
    """Place the Subject after its authored path, retaining edge notation."""
    path, relation, label = (
        concern[key] for key in ("path", "relation", "subject")
    )
    if relation == ".":
        path, _, prefix = path.rpartition("//.")
        relation, label = "is_narrower_than", f"({prefix}.{label})"
    return concern_path_parts(path) + (
        (CONCERN_OPERATORS.get(relation, relation).strip(), label),
    )
