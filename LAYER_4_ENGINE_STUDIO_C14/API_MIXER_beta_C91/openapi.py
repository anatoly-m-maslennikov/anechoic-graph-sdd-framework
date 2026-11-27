"""Export the shared beta Backend Tool API at image build time."""

import json
from copy import deepcopy
from pathlib import Path

import tomllib

from .api import descriptors
from ._shared_runtime_support import TOOL_REST_PATH
from .shared_runtime import Invocation, public_tool

_TEXT = {"type": "string"}
_NULLABLE_TEXT = {"type": ["string", "null"]}
_INSTANCE = {"type": "string", "pattern": "^[a-f0-9]{64}$"}


def _object(properties):
    return {
        "type": "object",
        "properties": properties,
        "required": list(properties),
        "additionalProperties": False,
    }


def _content(schema, **media):
    return {"application/json": {"schema": schema, **media}}


def _invocation_schema(tools):
    schema = Invocation.model_json_schema()
    for field in ("session_id", "public_base_url"):
        schema["properties"][field]["pattern"] = r"\S"
    branches = []
    for tool in tools:
        arguments = deepcopy(tool["inputSchema"])
        del arguments["properties"]["caller_context"]
        arguments["properties"]["project_root"]["pattern"] = r"\S"
        branches.append(
            {
                "description": tool["description"],
                "properties": {
                    "name": {"const": tool["name"]},
                    "arguments": arguments,
                },
            }
        )
    schema["oneOf"] = branches
    return schema


def _invocation_responses():
    project = _object(
        {"prefix": _TEXT.copy(), "instance_id": _INSTANCE.copy()}
    )
    success = _object(
        {
            "result": _object(
                {"value": {"type": "object"}, "text": _NULLABLE_TEXT.copy()}
            ),
            "project": project,
        }
    )
    error = _object(
        {
            "code": _TEXT.copy(),
            "message": _TEXT.copy(),
            "scope": {"enum": ["project", "tool"]},
        }
    )
    error["properties"]["tool_result"] = {"type": ["object", "null"]}
    failure = _object(
        {"error": error, "project": {"anyOf": [project, {"type": "null"}]}}
    )
    return {
        "200": {
            "description": "Tool result or request failure.",
            "content": _content({"oneOf": [success, failure]}),
        },
        "503": {
            "description": "Backend or Workbench unavailable.",
            "content": _content(failure),
        },
    }


def export_openapi(version):
    """Describe the HTTP transport and the installed Tool descriptors."""
    tools = [public_tool(tool) for tool in descriptors().values()]
    descriptor = {
        "type": "object",
        "properties": {
            "name": _TEXT.copy(),
            "description": _TEXT.copy(),
            "inputSchema": {"type": "object"},
            "annotations": {"type": "object"},
        },
        "required": ["name", "description", "inputSchema"],
    }
    entries = {"type": "array", "items": descriptor}
    catalog = _object({"result": _object({"tools": entries})})
    return {
        "openapi": "3.1.0",
        "info": {
            "title": "ANECHOIC Shared Beta Backend Tool API",
            "version": version,
            "description": "The Backend checks Project admission at runtime.",
        },
        "paths": {
            TOOL_REST_PATH: {
                "get": {
                    "operationId": "listTools",
                    "responses": {
                        "200": {
                            "description": "Installed Tool descriptors.",
                            "content": _content(
                                catalog, example={"result": {"tools": tools}}
                            ),
                        }
                    },
                },
                "post": {
                    "operationId": "invokeTool",
                    "parameters": [
                        {
                            "name": "X-Anechoic-Project-Instance",
                            "in": "header",
                            "schema": _INSTANCE.copy(),
                        }
                    ],
                    "requestBody": {
                        "required": True,
                        "content": _content(_invocation_schema(tools)),
                    },
                    "responses": _invocation_responses(),
                },
            }
        },
    }


if __name__ == "__main__":
    with Path("version.toml").open("rb") as version_file:
        version = tomllib.load(version_file)["framework"]["version"]
    print(json.dumps(export_openapi(version), indent=2, sort_keys=True))
