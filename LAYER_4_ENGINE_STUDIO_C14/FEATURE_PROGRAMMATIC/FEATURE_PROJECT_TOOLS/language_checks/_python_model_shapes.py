"""Recognize structured Python model shapes."""

import ast
from io import StringIO
import tokenize


RECORD_METHODS = {
    "__init__",
    "__eq__",
    "__hash__",
    "__iter__",
    "__repr__",
    "__str__",
}


def _name(node, bindings):
    if isinstance(node, ast.Name):
        return bindings.get(node.id, "")
    if isinstance(node, ast.Attribute):
        prefix = _name(node.value, bindings)
        return f"{prefix}.{node.attr}" if prefix else ""
    return ""


def _instance_field(item, bindings):
    if not isinstance(item, ast.AnnAssign) or not isinstance(
        item.target, ast.Name
    ):
        return False
    annotation = item.annotation
    if isinstance(annotation, ast.Subscript):
        annotation = annotation.value
    return _name(annotation, bindings) not in {
        "typing.ClassVar",
        "typing_extensions.ClassVar",
    }


def _plain_record(node, bindings):
    if (
        node.decorator_list
        or node.keywords
        or any(
            not isinstance(base, ast.Name) or base.id != "object"
            for base in node.bases
        )
    ):
        return False
    methods = [
        item
        for item in node.body
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]
    if any(method.name not in RECORD_METHODS for method in methods):
        return False
    if any(_instance_field(item, bindings) for item in node.body):
        return True
    return any(
        isinstance(item, ast.Attribute)
        and isinstance(item.ctx, ast.Store)
        and isinstance(item.value, ast.Name)
        and item.value.id == "self"
        for method in methods
        if method.name == "__init__"
        for item in ast.walk(method)
    )


def _named_fields(keys):
    return len(keys) >= 2 and all(
        isinstance(key, str) and key.isidentifier() for key in keys
    )


def _dictionary_fields(value, bindings):
    if isinstance(value, ast.Dict):
        return [
            key.value if isinstance(key, ast.Constant) else None
            for key in value.keys
        ]
    if (
        isinstance(value, ast.Call)
        and isinstance(value.func, ast.Name)
        and value.func.id == "dict"
        and not _name(value.func, bindings)
        and not value.args
    ):
        return [keyword.arg for keyword in value.keywords]
    return []


def _dictionary_record(node, bindings):
    annotation = node.annotation
    if not isinstance(annotation, ast.Subscript) or not isinstance(
        annotation.slice, ast.Tuple
    ):
        return False
    name = _name(annotation.value, bindings)
    builtin = (
        isinstance(annotation.value, ast.Name)
        and annotation.value.id == "dict"
        and not name
    )
    if (
        not (builtin or name == "typing.Dict")
        or len(annotation.slice.elts) != 2
    ):
        return False
    key, value = annotation.slice.elts
    if not isinstance(key, ast.Name) or key.id != "str":
        return False
    heterogeneous = (
        (isinstance(value, ast.Name) and value.id == "object")
        or _name(value, bindings) in {"typing.Any", "typing_extensions.Any"}
        or (isinstance(value, ast.BinOp) and isinstance(value.op, ast.BitOr))
        or (
            isinstance(value, ast.Subscript)
            and _name(value.value, bindings) == "typing.Union"
        )
    )
    return heterogeneous and _named_fields(
        _dictionary_fields(node.value, bindings)
    )


def _exemptions(source, pragma):
    if pragma not in source:
        return set()
    return {
        token.start[0]
        for token in tokenize.generate_tokens(StringIO(source).readline)
        if token.type == tokenize.COMMENT
        and token.string.startswith(pragma)
        and token.string.removeprefix(pragma).strip()
    }


def _literal_tags(node, bindings):
    tags = {}
    for item in node.body:
        if not isinstance(item, ast.AnnAssign) or not isinstance(
            item.target, ast.Name
        ):
            continue
        annotation = item.annotation
        if (
            isinstance(annotation, ast.Subscript)
            and _name(annotation.value, bindings)
            in {"typing.Literal", "typing_extensions.Literal"}
            and isinstance(annotation.slice, ast.Constant)
            and isinstance(annotation.slice.value, str)
        ):
            tags[item.target.id] = annotation.slice.value
    return tags


def _union_types(node, bindings):
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
        return _union_types(node.left, bindings) + _union_types(
            node.right, bindings
        )
    if (
        isinstance(node, ast.Subscript)
        and isinstance(node.slice, ast.Tuple)
        and _name(node.value, bindings) == "typing.Union"
    ):
        return node.slice.elts
    return [node]
