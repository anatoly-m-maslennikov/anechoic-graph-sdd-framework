"""Export the shared beta Backend Tool API at image build time."""

import argparse
import json
from copy import deepcopy
from pathlib import Path

import tomllib


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


def _invocation_schema(tools, invocation, *, current=False):
    schema = invocation.model_json_schema()
    for field in ("session_id", "public_base_url"):
        schema["properties"][field]["pattern"] = r"\S"
    if current:
        schema["properties"]["arguments"] = {
            "type": "object",
            "properties": {
                "project_root": {
                    "type": "string", "minLength": 1, "pattern": r"\S"
                }
            },
            "required": ["project_root"],
        }
        return schema
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


def export_openapi(version, registry=None):
    """Describe the beta API or derive the Current API from its registry."""
    title = "ANECHOIC Shared Beta Backend Tool API"
    description = "The Backend checks Project admission at runtime."
    if registry is None:
        from .api import descriptors
        from ._shared_runtime_support import TOOL_REST_PATH, Invocation
        from .shared_runtime import public_tool

        tools = [public_tool(tool) for tool in descriptors().values()]
    else:
        from IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IWE_CONSOLE_BACKEND.\
            shared_tool_contract import public_tool  # fmt: skip
        from MCP_PATCHBAY_C21.FEATURE_MCP.http_paths import TOOL_REST_PATH
        from MCP_PATCHBAY_C21.FEATURE_MCP.tool_rest import Invocation

        names = set(registry["public_tools"])
        tools = [
            public_tool(tool)
            for provider in registry["providers"]
            for tool in provider["tools"]
            if tool["name"] in names
        ]
        if len(tools) != len(names):
            raise ValueError("Registry public Tools do not match descriptors")
        title = "ANECHOIC Shared Backend Tool API"
        description += " The advertised Tool catalog can vary by Project."
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
    document = {
        "openapi": "3.1.0",
        "info": {
            "title": title,
            "version": version,
            "description": description,
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
                        "content": _content(
                            _invocation_schema(
                                tools, Invocation, current=registry is not None
                            )
                        ),
                    },
                    "responses": _invocation_responses(),
                },
            }
        },
    }
    if registry is not None:
        operations = document["paths"][TOOL_REST_PATH]
        operations["get"]["description"] = (
            "The example is derived from the packaged registry. "
            "The shared catalog can vary with admitted Projects."
        )
        responses = operations["post"]["responses"]
        failure_content = responses["503"]["content"]
        operations["get"]["responses"]["503"] = responses["503"]
        responses["403"] = {
            "description": "Request origin rejected.",
            "content": failure_content,
        }
        responses["502"] = {
            "description": "Project receipt mismatch.",
            "content": failure_content,
        }
    return document


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path)
    parser.add_argument(
        "--version-file", type=Path, default=Path("version.toml")
    )
    args = parser.parse_args()
    with args.version_file.open("rb") as version_file:
        version = tomllib.load(version_file)["framework"]["version"]
    registry = json.loads(args.registry.read_text()) if args.registry else None
    document = export_openapi(version, registry)
    print(json.dumps(document, indent=2, sort_keys=True))
