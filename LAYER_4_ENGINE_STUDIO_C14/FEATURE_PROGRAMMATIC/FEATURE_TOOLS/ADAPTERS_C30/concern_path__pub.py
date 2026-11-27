"""Parse the syntax allowed in an authored Concern Path."""

from . import subject_notation__pub as notation
from .subject_notation_expression import _ExpressionParser


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
