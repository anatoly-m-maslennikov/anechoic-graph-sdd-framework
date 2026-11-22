"""Shared literal and reference validation for legacy Python Claims."""

from __future__ import annotations

import ast
import json
import re
from collections.abc import Callable


class PythonModelClaimError(ValueError):
    """A Python model Claim contains invalid or unsupported syntax."""


_COUNT = re.compile(r"(?:0|[1-9][0-9]*)(?:\+|\.\.(?:0|[1-9][0-9]*))?\Z")
_NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_ -]*\Z")
_RELATION = re.compile(r"[A-Za-z_][A-Za-z0-9_]*\Z")
_BARE_VALUE = re.compile(r"[A-Za-z_][A-Za-z0-9_ -]*\Z")


def _error(node: ast.AST, message: str) -> PythonModelClaimError:
    return PythonModelClaimError(f"line {node.lineno}, column {node.col_offset + 1}: {message}")


def _text(value: object, label: str, node: ast.AST, *, empty: bool = False) -> str:
    if not isinstance(value, str) or (not empty and not value.strip()) or value != value.strip():
        raise _error(node, f"{label} must be a {'string' if empty else 'nonempty string'}")
    if any(ord(char) < 32 or ord(char) == 127 for char in value):
        raise _error(node, f"{label} contains a control character")
    return value


def _reference(value: object, label: str, node: ast.AST,
               validate_reference: Callable[[str], object] | None) -> str:
    text = _text(value, label, node)
    if any(char in text for char in ";#\\{}\n\r`") or "::" in text or re.search(r"\(\s*\(", text):
        raise _error(node, f"{label} contains an unsupported character")
    if not re.fullmatch(r"[\w\s.*/():=,!'\"<>|+@$\[\]-]+", text):
        raise _error(node, f"{label} contains an unsupported character")
    _check_delimiters(text, label, node)
    if validate_reference is not None:
        try:
            valid = validate_reference(text)
        except (ValueError, LookupError) as error:
            raise _error(node, f"invalid {label}: {error}") from error
        if valid is False:
            raise _error(node, f"unknown {label}: {text}")
    return text


def _check_delimiters(text: str, label: str, node: ast.AST) -> None:
    stack: list[str] = []
    quote = None
    for char in text:
        if quote:
            if char == quote:
                quote = None
        elif char in "\"'":
            quote = char
        elif char in "([":
            stack.append(char)
        elif char in ")]":
            if not stack or stack.pop() != {')': '(', ']': '['}[char]:
                raise _error(node, f"{label} has unbalanced delimiters")
    if quote or stack:
        raise _error(node, f"{label} has unbalanced delimiters")


def _count(value: object, label: str, node: ast.AST) -> str:
    text = _text(value, label, node)
    if not _COUNT.fullmatch(text):
        raise _error(node, f"{label} is not a cardinality")
    if ".." in text:
        minimum, maximum = (int(number) for number in text.split(".."))
        if minimum > maximum:
            raise _error(node, f"{label} has a reversed range")
    return text


def _name(value: object, label: str, node: ast.AST) -> str:
    text = _text(value, label, node)
    if not _NAME.fullmatch(text):
        raise _error(node, f"{label} must be a name")
    return text


def _literal(value: object, node: ast.AST) -> str:
    text = _text(value, "value", node)
    return text if _BARE_VALUE.fullmatch(text) else json.dumps(text, ensure_ascii=False)


def _items(value: object, label: str, node: ast.AST) -> tuple:
    if not isinstance(value, tuple) or not value:
        raise _error(node, f"{label} must be a nonempty tuple")
    if len(value) != len(set(item for item in value if isinstance(item, str))):
        raise _error(node, f"{label} must contain distinct strings")
    return value


def _optional_count(args: dict, key: str, node: ast.AST) -> str:
    value = args.get(key)
    return "" if value is None else f"{{::{_count(value, key, node)}}}"


