"""Read native class and callback syntax."""

from __future__ import annotations

import ast
from typing import Any

from pydantic import BaseModel, ConfigDict

from .native_model_claim_values import _BUILTINS, _annotation, _fail, _keywords, _value


class _NativeField(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    name: str
    annotation: Any
    field: dict[str, Any] | None = None
    default: Any = None


def _field(node: ast.AnnAssign, names: set[str]) -> _NativeField:
    if not isinstance(node.target, ast.Name) or node.simple != 1:
        _fail(node, "field must be a simple annotated name")
    if node.target.id.startswith("__") and node.target.id.endswith("__"):
        _fail(node, "Model field names cannot be Python special attributes")
    result = _NativeField(name=node.target.id, annotation=_annotation(node.annotation, names))
    if node.value is None:
        return result
    if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name) and node.value.func.id == "field":
        if "field" not in names:
            _fail(node, "field must be imported")
        options = _keywords(node.value)
        if set(options) - {"default", "default_factory", "metadata", "kw_only"}:
            _fail(node, "unsupported field argument")
        if "default" in options and "default_factory" in options:
            _fail(node, "field has both default and default_factory")
        if "default_factory" in options:
            factory = options["default_factory"]
            if not isinstance(factory, ast.Name) or factory.id not in {"list", "dict", "set", "tuple"}:
                _fail(factory, "default_factory must be a collection type")
        result.field = {key: _value(value, names) for key, value in options.items()}
    else:
        result.default = _value(node.value, names)
    return result


def _class(node: ast.ClassDef, names: set[str]) -> dict[str, Any]:  # noqa: C901
    if node.keywords:
        _fail(node, "class keyword arguments are unsupported")
    if node.type_params:
        _fail(node, "class type parameters are unsupported")
    bases = []
    for base in node.bases:
        if not isinstance(base, ast.Name) or base.id not in names | _BUILTINS:
            _fail(base, "class base must be an imported or declared class")
        bases.append(base.id)
    decorators = []
    for decorator in node.decorator_list:
        if isinstance(decorator, ast.Name) and decorator.id == "dataclass" and "dataclass" in names:
            decorators.append({})
        elif (isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name)
              and decorator.func.id == "dataclass" and "dataclass" in names):
            options = _keywords(decorator)
            if set(options) - {"frozen", "kw_only", "slots"}:
                _fail(decorator, "unsupported dataclass option")
            values = {key: _value(value, names) for key, value in options.items()}
            if any(type(value) is not bool for value in values.values()):
                _fail(decorator, "dataclass options must be booleans")
            decorators.append(values)
        else:
            _fail(decorator, "unsupported class decorator")
    if len(decorators) > 1:
        _fail(node, "duplicate dataclass decorator")
    fields = []
    for item in node.body:
        if isinstance(item, ast.Pass):
            continue
        if isinstance(item, ast.AnnAssign):
            fields.append(_field(item, names | {node.name}))
            continue
        _fail(item, "class body supports annotated fields and pass")
    if len({field.name for field in fields}) != len(fields):
        _fail(node, "duplicate class field")
    return {"name": node.name, "bases": tuple(bases),
            "fields": tuple(field.model_dump(exclude_unset=True) for field in fields),
            "dataclass": decorators[0] if decorators else None}


def _instance_check(node: ast.FunctionDef, names: set[str], text: str) -> dict[str, Any]:
    args = node.args
    if (node.decorator_list or node.type_comment or args.posonlyargs or args.vararg or args.kwarg
            or args.kwonlyargs or args.defaults or args.kw_defaults or len(args.args) != 1):
        _fail(node, "instance check requires one typed argument without defaults or decorators")
    parameter = args.args[0]
    if (not isinstance(parameter.annotation, ast.Name) or parameter.annotation.id not in names
            or not isinstance(node.returns, ast.Name) or node.returns.id != "bool"):
        _fail(node, "instance check requires a bound Model type and bool return")
    return {
        "name": node.name,
        "parameter": parameter.arg,
        "parameter_type": parameter.annotation.id,
        "source": ast.get_source_segment(text, node),
        "line": node.lineno,
    }


