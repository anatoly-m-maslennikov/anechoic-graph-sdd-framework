"""Read declarative Python model Claims without executing their contents."""

from __future__ import annotations

import ast
import io
import tokenize
from collections.abc import Callable

from .python_claim_values import PythonModelClaimError, _error
from . import python_claim_legacy
from .python_claim_validation import _validate_structured_call


_FUNCTIONS = {
    "property_rule": (
        {"address"},
        {"address", "value_format", "occurrences", "values"},
    ),
    "allowed_children": (
        {"address", "names", "occurrences"},
        {"address", "names", "occurrences", "name_format"},
    ),
    "order_before": ({"first", "second"}, {"first", "second"}),
    "allowed_values": (
        {"address", "values"},
        {"address", "values", "occurrences", "quoted"},
    ),
    "children": (
        {"address", "occurrences"},
        {"address", "occurrences", "name_format", "recursive"},
    ),
    "composition": ({"container", "parts"}, {"container", "parts"}),
    "deliver": ({"source", "carrier"}, {"source", "carrier"}),
    "classify": (
        {"address", "axis", "value"},
        {"address", "axis", "value", "grouped", "notation"},
    ),
    "path_template": ({"address", "template"}, {"address", "template"}),
    "copy_value": ({"address", "source"}, {"address", "source"}),
    "minimum_value": ({"address", "minimum"}, {"address", "minimum"}),
    "unique": ({"population", "keys"}, {"population", "keys"}),
    "population": ({"address", "count"}, {"address", "count"}),
    "allow_roles_for_form": (
        {"form", "roles"},
        {"form", "roles", "participant"},
    ),
    "relation": (
        {"source", "name"},
        {
            "source",
            "name",
            "target",
            "source_count",
            "target_count",
            "reverse",
        },
    ),
    "set_value": ({"address", "value"}, {"address", "value"}),
    "subject_path": ({"address"}, {"address"}),
}


def _group_markers(text: str) -> list[tuple[int, str]]:
    markers: list[tuple[int, str]] = []
    depth = 0
    for token in tokenize.generate_tokens(io.StringIO(text).readline):
        if token.type == tokenize.OP and token.string in "([{":
            depth += 1
        elif token.type == tokenize.OP and token.string in ")]}":
            depth -= 1
        elif (
            token.type == tokenize.COMMENT
            and depth == 0
            and token.line.lstrip().startswith("#")
        ):
            label = token.string[1:].strip().casefold()
            if label in {"model", "instances"}:
                markers.append((token.start[0], label))
    return markers


def _literal_call(item: ast.stmt) -> tuple[str, dict]:
    if not isinstance(item, ast.Expr) or not isinstance(item.value, ast.Call):
        raise _error(item, "expected a declarative function call")
    call = item.value
    if not isinstance(call.func, ast.Name) or call.func.id not in _FUNCTIONS:
        raise _error(item, "unknown declarative function")
    name = call.func.id
    if call.args or any(keyword.arg is None for keyword in call.keywords):
        raise _error(item, "only named literal arguments are supported")
    args = {}
    for keyword in call.keywords:
        if keyword.arg in args:
            raise _error(keyword, f"duplicate argument: {keyword.arg}")
        try:
            args[keyword.arg] = ast.literal_eval(keyword.value)
        except (ValueError, TypeError, SyntaxError, RecursionError) as error:
            raise _error(
                keyword, f"{keyword.arg} must be a literal"
            ) from error
    required, allowed = _FUNCTIONS[name]
    missing = required - args.keys()
    unexpected = args.keys() - allowed
    if missing:
        raise _error(item, f"missing arguments: {', '.join(sorted(missing))}")
    if unexpected:
        raise _error(
            item, f"unexpected arguments: {', '.join(sorted(unexpected))}"
        )
    return name, args


def parse_grouped_python_model_claim(
    text: str,
    *,
    validate_reference: Callable[[str], object] | None = None,
    validate_relation_endpoint: Callable[[str, object, str], object]
    | None = None,
    _structured: bool = False,
) -> tuple[tuple[str, str | None], ...]:
    "Return statements with their preceding top-level model/instances marker."
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    if validate_reference is not None and not callable(validate_reference):
        raise TypeError("validate_reference must be callable")
    try:
        tree = ast.parse(text, mode="exec")
    except SyntaxError as error:
        raise PythonModelClaimError(
            f"line {error.lineno}, column {error.offset}: {error.msg}"
        ) from error
    markers = _group_markers(text)
    statements = _grouped_statements(
        tree,
        markers,
        _structured,
        validate_reference,
        validate_relation_endpoint,
    )
    if not statements:
        raise PythonModelClaimError(
            "line 1, column 1: expected a declarative function call"
        )
    return tuple(statements)


def _grouped_statements(
    tree, markers, structured, validate_reference, validate_relation_endpoint
):
    statements: list[tuple[str, str | None]] = []
    for item in tree.body:
        name, args = _literal_call(item)
        group = next(
            (label for line, label in reversed(markers) if line < item.lineno),
            None,
        )
        if structured:
            _validate_structured_call(
                name,
                args,
                item,
                validate_reference,
                validate_relation_endpoint,
            )
            statements.append(
                {"name": name, "arguments": args, "scope": group}
            )
        else:
            statements.extend(
                (statement, group)
                for statement in python_claim_legacy._render(
                    name,
                    args,
                    item,
                    validate_reference,
                    validate_relation_endpoint,
                )
            )
    return statements


def parse_python_model_claim(
    text: str,
    *,
    validate_reference: Callable[[str], object] | None = None,
    validate_relation_endpoint: Callable[[str, object, str], object]
    | None = None,
) -> tuple[str, ...]:
    """Return compatible statements without evaluating the source text.

    The optional callback checks each address and may return False or raise
    ValueError/LookupError to reject an unknown reference.
    """
    return tuple(
        statement
        for statement, _group in parse_grouped_python_model_claim(
            text,
            validate_reference=validate_reference,
            validate_relation_endpoint=validate_relation_endpoint,
        )
    )


def parse_structured_python_model_claim(
    text: str,
    *,
    validate_reference: Callable[[str], object] | None = None,
    validate_relation_endpoint: Callable[[str, object, str], object]
    | None = None,
) -> tuple[dict, ...]:
    """Return validated helper names, literal arguments, and \
model/instance scope."""
    return parse_grouped_python_model_claim(
        text,
        validate_reference=validate_reference,
        validate_relation_endpoint=validate_relation_endpoint,
        _structured=True,
    )
