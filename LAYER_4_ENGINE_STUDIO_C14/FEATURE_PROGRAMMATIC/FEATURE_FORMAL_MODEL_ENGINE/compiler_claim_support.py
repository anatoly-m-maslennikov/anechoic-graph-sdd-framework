"""Names, cardinalities, and formats for native Claim compilation."""
from __future__ import annotations
import re
from typing import Any

_PATH = re.compile(r"[A-Za-z_][A-Za-z_0-9 .-]*\Z")
_RELATION = re.compile(r"[A-Za-z_][A-Za-z_0-9]*\Z")
_FORMATS = {"str": "string", "int": "int", "float": "float", "bool": "bool", "datetime": "datetime",
            "markdown": "markdown", "atom_id": "atom id"}


def _name(value: Any, *, relation: bool = False) -> str:
    pattern = _RELATION if relation else _PATH
    if not isinstance(value, str) or not pattern.fullmatch(value) or value != value.strip():
        raise ValueError(f"unsupported compiler name: {value!r}")
    return value


def _model_base_path(value: Any) -> str:
    """Accept bounded Model paths, including a qualified narrowing step."""
    try:
        return _name(value)
    except ValueError:
        pass
    if not isinstance(value, str) or value != value.strip():
        raise ValueError(f"unsupported compiler name: {value!r}")
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
        Name as _subject_Name,
        Path as _subject_Path,
        Qualification as _subject_Qualification,
        SubjectNotationError as _subject_SubjectNotationError,
        ValueLiteral as _subject_ValueLiteral,
        parse_subject_expression as _subject_parse_subject_expression,
    )
    try:
        path = _subject_parse_subject_expression(value, subject_profile="approved").expression
        if not isinstance(path, _subject_Path) or not isinstance(path.head, _subject_Name):
            raise ValueError
        _name(path.head.value)
        if path.value_format is not None or path.value_cardinality is not None:
            raise ValueError
        for step in path.steps:
            if step.operator in ("/", ".") and isinstance(step.operand, _subject_Name):
                _name(step.operand.value)
            elif step.operator == "/" and isinstance(step.operand, _subject_Qualification):
                q = step.operand.relative_path
                if not isinstance(q.head, _subject_Name) or q.value_format is not None or q.value_cardinality is not None:
                    raise ValueError
                _name(q.head.value)
                if not q.steps or q.steps[-1].operator != ":=" or not isinstance(q.steps[-1].operand, _subject_ValueLiteral):
                    raise ValueError
                _name(q.steps[-1].operand.value)
                for part in q.steps[:-1]:
                    if part.operator != "." or not isinstance(part.operand, _subject_Name):
                        raise ValueError
                    _name(part.operand.value)
            else:
                raise ValueError
    except (_subject_SubjectNotationError, ValueError, TypeError):
        raise ValueError(f"unsupported compiler name: {value!r}") from None
    return value


def _count(value: Any) -> str:
    if type(value) is int and value >= 0:
        return str(value)
    if not isinstance(value, dict) or set(value) != {"minimum", "maximum"}:
        raise ValueError(f"unsupported cardinality: {value!r}")
    minimum, maximum = value["minimum"], value["maximum"]
    if type(minimum) is not int or minimum < 0 or (
        maximum is not None and (type(maximum) is not int or maximum < minimum)
    ):
        raise ValueError(f"unsupported cardinality: {value!r}")
    if maximum is None:
        return f"{minimum}+"
    if minimum == maximum:
        return str(minimum)
    return f"{minimum}..{maximum}"


def _format(value: Any) -> str:
    if not isinstance(value, str) or value not in _FORMATS:
        raise ValueError(f"unsupported compiler format: {value!r}")
    return _FORMATS[value]


def _form_role_statement(form: str, roles: Any) -> str:
    if not isinstance(roles, tuple) or not roles or len(set(roles)) != len(roles):
        raise ValueError("Form Roles must be a nonempty tuple of distinct Roles")
    names = ", ".join(_name(role) for role in roles)
    return (f"FOR EACH $item[<Atom>, (.Header.Context.Form = {_name(form)})]: "
            f"($item.Header.Context.Role:: [in ({names})]{{::1}})")


