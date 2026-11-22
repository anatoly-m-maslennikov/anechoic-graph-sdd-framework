"""Read native Model Claims without executing authored code."""

from __future__ import annotations

import ast
from typing import Any

from .native_model_claim_values import NativeModelClaimError, _DECLARATIONS, _DECLARATION_KEYS, _fail, _keywords, _validate_manifest_arguments
from .native_model_claim_aspects import validate_aspect_hierarchy, validate_aspect_instance
from .native_model_claim_decode import _read_tree, _decode
from .native_model_claim_validate_core import _validate_classification, _validate_aspects, _validate_fallback, _validate_callback, _validate_property_prerequisites, _validate_property
from .native_model_claim_validate_population import _validate_uniqueness, _validate_dependencies, _validate_ordered
from .native_model_claim_validate_relation import _validate_relation, _validate_constraints

__all__ = ("NativeModelClaimError", "parse_native_model_claim",
           "validate_aspect_hierarchy", "validate_aspect_instance")


def parse_native_model_claim(text: str) -> dict[str, Any] | None:  # noqa: C901
    """Parse one authored Declaration without executing its code."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    try:
        tree = ast.parse(text, mode="exec")
    except SyntaxError as error:
        raise NativeModelClaimError(
            f"line {error.lineno}, column {error.offset}: {error.msg}"
        ) from error
    candidates = [node for node in ast.walk(tree) if isinstance(node, ast.Call)
                  and isinstance(node.func, ast.Name) and node.func.id in _DECLARATIONS]
    if not candidates:
        return None
    if len(candidates) != 1:
        raise NativeModelClaimError("a Model Claim must contain exactly one declaration")

    imports, names, classes, functions, declaration = _read_tree(tree, text)
    function = declaration.func.id
    if imports.get(function) != "anechoic.formal_claims":
        _fail(declaration, f"{function} must be imported")
    keywords = _keywords(declaration)
    if unknown := keywords.keys() - _DECLARATION_KEYS[function]:
        _fail(declaration, f"unsupported {function} arguments: {', '.join(sorted(unknown))}")
    arguments, property_manifest = _decode(keywords, function, names, imports)
    _validate_manifest_arguments(arguments, declaration)
    _validate_classification(arguments, declaration, function, classes, functions, imports, property_manifest)
    _validate_aspects(arguments, declaration, function, classes, functions, imports, property_manifest)
    _validate_fallback(arguments, declaration, function, classes, functions, imports, property_manifest)
    _validate_callback(arguments, declaration, function, classes, functions, imports, property_manifest)
    _validate_property_prerequisites(arguments, declaration, function, classes, functions, imports, property_manifest)
    _validate_property(arguments, declaration, function, classes, functions, imports, property_manifest)
    _validate_uniqueness(arguments, declaration, function, classes, functions, imports, property_manifest)
    _validate_dependencies(arguments, declaration, function, classes, functions, imports, property_manifest)
    _validate_ordered(arguments, declaration, function, classes, functions, imports, property_manifest)
    _validate_relation(arguments, declaration, function, classes, functions, imports, property_manifest)
    _validate_constraints(arguments, declaration, function, classes, functions, imports, property_manifest)
    result = {"kind": _DECLARATIONS[function], "arguments": arguments, "classes": tuple(classes),
              "imports": imports, "line": declaration.lineno}
    value_format_node = keywords.get("value_format")
    if isinstance(value_format_node, ast.Name) and imports.get(value_format_node.id) == "anechoic.model":
        result["model_value_format"] = value_format_node.id
    if functions:
        result["instance_check"] = functions[0]
    return result
