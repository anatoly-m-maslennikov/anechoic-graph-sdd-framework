"""Native Tool contract validation and the shared public schema adapter."""

from __future__ import annotations

import copy

from jsonschema import Draft202012Validator, SchemaError
from mcp import types


_UNADAPTABLE_ROOT_KEYS = frozenset(
    {
        "$ref",
        "$dynamicRef",
        "allOf",
        "anyOf",
        "not",
        "if",
        "then",
        "else",
        "dependentRequired",
        "dependentSchemas",
        "enum",
        "const",
        "maxProperties",
        "patternProperties",
        "propertyNames",
        "unevaluatedProperties",
    }
)


def _native_presence(predicate, fields):
    "Match predicates whose truth is unchanged by adding envelope properties."
    if not isinstance(predicate, dict) or predicate.keys() - {
        "required",
        "anyOf",
        "not",
    }:
        return False
    return (
        set(predicate.get("required", ())) <= fields
        and all(
            _native_presence(arm, fields) for arm in predicate.get("anyOf", ())
        )
        and (
            "not" not in predicate
            or _native_presence(predicate["not"], fields)
        )
    )


def public_tool(tool: types.Tool, *, required: bool = True) -> types.Tool:
    """Add the Project and caller-context envelope to a native Tool schema."""
    schema = copy.deepcopy(tool.input_schema)
    if not isinstance(schema, dict):
        raise ValueError("Native Tool input schema is invalid")
    try:
        Draft202012Validator.check_schema(schema)
    except SchemaError as error:
        raise ValueError("Native Tool input schema is invalid") from error
    properties = dict(schema.get("properties", {}))
    if _UNADAPTABLE_ROOT_KEYS.intersection(schema) or any(
        not _native_presence(arm, properties.keys())
        for arm in schema.get("oneOf", ())
    ):
        raise ValueError(
            "Native Tool input schema cannot safely add "
            "project_root at its root"
        )
    if {"project_root", "caller_context"} & properties.keys():
        raise ValueError(
            "Native Tool cannot use a reserved MCP envelope field"
        )
    if schema.get("type") not in (None, "object"):
        raise ValueError("Native Tool input is not a root object")
    properties["project_root"] = {"type": "string", "minLength": 1}
    properties["caller_context"] = {
        "type": "object",
        "properties": {
            "session_id": {"type": "string", "minLength": 1, "pattern": "\\S"}
        },
        "required": ["session_id"],
        "additionalProperties": False,
    }
    required_fields = list(schema.get("required", []))
    if required and "project_root" not in required_fields:
        required_fields.append("project_root")
    schema["type"] = "object"
    schema["properties"] = properties
    schema["required"] = required_fields
    try:
        Draft202012Validator.check_schema(schema)
    except SchemaError as error:
        raise ValueError("Public Tool input schema is invalid") from error
    return tool.model_copy(update={"input_schema": schema})


__all__ = ["public_tool"]
