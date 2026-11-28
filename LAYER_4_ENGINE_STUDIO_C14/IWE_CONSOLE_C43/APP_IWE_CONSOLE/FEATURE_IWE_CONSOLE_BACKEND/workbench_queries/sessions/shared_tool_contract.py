"""Native Tool contract validation and the shared public schema adapter."""

from __future__ import annotations

from pydantic import ConfigDict, InstanceOf
from pydantic.dataclasses import dataclass

import copy
import hashlib
import json

from jsonschema import Draft202012Validator, SchemaError
from typing import Annotated, Any


_UNADAPTABLE_ROOT_KEYS = frozenset(
    {
        "$ref",
        "$dynamicRef",
        "allOf",
        "anyOf",
        "oneOf",
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


@dataclass(config=ConfigDict(strict=True, extra="forbid"), frozen=True)
class ToolContract:
    tool: Annotated[dict[str, Any], InstanceOf()]
    digest: str


def contract_digest(tool: dict[str, Any]) -> str:
    value = {
        "input_schema": tool["inputSchema"],
        "output_schema": tool.get("outputSchema"),
    }
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def public_tool(tool: dict[str, Any]) -> dict[str, Any]:
    """Add the shared Project and caller-context arguments to a native Tool."""
    schema = copy.deepcopy(tool["inputSchema"])
    if not isinstance(schema, dict):
        raise ValueError("Native Tool input schema is invalid")
    try:
        Draft202012Validator.check_schema(schema)
    except SchemaError as error:
        raise ValueError("Native Tool input schema is invalid") from error
    if _UNADAPTABLE_ROOT_KEYS.intersection(schema):
        raise ValueError(
            "Native Tool input schema cannot safely add project_root at its "
            "root"
        )
    if {"project_root", "caller_context"} & schema.get(
        "properties", {}
    ).keys():
        raise ValueError(
            "Native Tool cannot use a reserved MCP envelope field"
        )
    if schema.get("type") not in (None, "object"):
        raise ValueError("Native Tool input is not a root object")
    properties = dict(schema.get("properties", {}))
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
    if "project_root" not in required_fields:
        required_fields.append("project_root")
    schema["type"], schema["properties"], schema["required"] = (
        "object",
        properties,
        required_fields,
    )
    try:
        Draft202012Validator.check_schema(schema)
    except SchemaError as error:
        raise ValueError("Public Tool input schema is invalid") from error
    return {**tool, "inputSchema": schema}


__all__ = ["ToolContract", "contract_digest", "public_tool"]
