"""Read native Model Claims without executing authored code."""

from __future__ import annotations

import ast
from typing import Any

from .native_model_claim_values import (
    NativeModelClaimError,
    _DECLARATIONS,
    _DECLARATION_KEYS,
    _fail,
    _keywords,
    _validate_manifest_arguments,
)
from .native_model_claim_aspects import (
    validate_aspect_hierarchy,
    validate_aspect_instance,
)
from .native_model_claim_decode import _read_tree, _decode, _instance
from .native_model_claim_validate_core import (
    _validate_axes,
    _validate_aspects,
    _validate_fallback,
    _validate_callback,
    _validate_property_prerequisites,
    _validate_property,
)
from .native_model_claim_validate_population import (
    _validate_uniqueness,
    _validate_dependencies,
    _validate_ordered,
)
from .native_model_claim_validate_relation import (
    _validate_relation,
    _validate_constraints,
)

__all__ = (
    "NativeModelClaimError",
    "parse_native_model_claim",
    "validate_aspect_hierarchy",
    "validate_aspect_instance",
)


def _claim_tree(text):
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    try:
        tree = ast.parse(text, mode="exec")
    except SyntaxError as error:
        raise NativeModelClaimError(
            f"line {error.lineno}, column {error.offset}: {error.msg}"
        ) from error
    candidates = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id in _DECLARATIONS
    ]
    if not candidates:
        return None
    if len(candidates) != 1:
        raise NativeModelClaimError(
            "a Model Claim must contain exactly one declaration"
        )

    return tree


def _claim_keywords(declaration, function):
    keywords = _keywords(declaration)
    for old, new in (
        ("classifications", "axes"),
        ("inverse_classifications", "inverse_axes"),
        ("allowed_classification_values", "allowed_axis_values"),
    ):
        if old in keywords:
            if new in keywords:
                _fail(declaration, f"duplicate {new} declaration")
            keywords[new] = keywords.pop(old)
    if unknown := keywords.keys() - _DECLARATION_KEYS[function]:
        _fail(
            declaration,
            f"unsupported {function} arguments: {', '.join(sorted(unknown))}",
        )
    return keywords


def parse_native_model_claim(text: str) -> dict[str, Any] | None:  # noqa: C901
    """Parse one authored Declaration without executing its code."""
    tree = _claim_tree(text)
    if tree is None:
        return None

    imports, names, classes, functions, declaration = _read_tree(tree, text)
    function = declaration.func.id
    if imports.get(function) != "anechoic.formal_claims":
        _fail(declaration, f"{function} must be imported")
    keywords = _claim_keywords(declaration, function)
    arguments, property_manifest = _decode(keywords, function, names, imports)
    _validate_claim(
        arguments,
        declaration,
        function,
        classes,
        functions,
        imports,
        property_manifest,
    )
    result = {
        "kind": _DECLARATIONS[function],
        "arguments": arguments,
        "classes": tuple(classes),
        "imports": imports,
        "line": declaration.lineno,
    }
    value_format_node = keywords.get("value_format")
    if (
        isinstance(value_format_node, ast.Name)
        and imports.get(value_format_node.id) == "anechoic.model"
    ):
        result["model_value_format"] = value_format_node.id
    if functions:
        result["instance_check"] = functions[0]
    return result


def _validate_claim(
    arguments,
    declaration,
    function,
    classes,
    functions,
    imports,
    property_manifest,
):
    _validate_manifest_arguments(arguments, declaration)
    inputs = (
        arguments,
        declaration,
        function,
        classes,
        functions,
        imports,
        property_manifest,
    )
    _validate_axes(*inputs)
    _validate_aspects(*inputs)
    _validate_fallback(*inputs)
    _validate_callback(*inputs)
    _validate_property_prerequisites(*inputs)
    _validate_property(*inputs)
    _validate_uniqueness(*inputs)
    _validate_dependencies(*inputs)
    _validate_ordered(*inputs)
    _validate_relation(*inputs)
    _validate_constraints(*inputs)


def parse_manifest_declaration(text, *, entity_name, class_name, wrapped=None):
    """Read a wrapped instance or an imported Manifest constructor."""
    claim = parse_native_model_claim(text)
    if wrapped is not None and wrapped != (claim is not None):
        raise ValueError(f"Expected one formal {class_name} instance")
    if claim is None:
        imports, _, classes, functions, instance = _read_tree(
            ast.parse(text), text, {class_name}
        )
        if classes or functions or imports.get(class_name) != "anechoic.model":
            _fail(instance, f"Expected one imported {class_name} constructor")
        return _instance(instance)["fields"]
    args = claim["arguments"] if claim["kind"] == "entity" else {}
    instance = args.get("instance", {})
    if (
        set(args) != {"entity_name", "instance"}
        or args["entity_name"] != entity_name
        or instance.get("type") != class_name
    ):
        raise ValueError(f"Expected one formal {class_name} instance")
    return instance["fields"]
