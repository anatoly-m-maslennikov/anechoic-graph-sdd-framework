---
atom_family: SPEC
atom_id: AN-S-999999
container: {component: C45}
tier: 1
context: {template: component_manifest}
state: {status: draft, version: 1}
---
## Summary

Declare an isolated Workbench query pilot.

## Purpose

Describe one read-only Tool Action for the HTTP export pilot.

## Component Identity

```python
from anechoic.model import ComponentManifest

ComponentManifest(component_id="C45", name="Workbench query pilot")
```

## Component Boundaries

```python
{
    "io": {
        "server": {
            "tools": {"transport": "http", "routes": {"POST /tools": "invoke"}}
        }
    }
}
```

## Component Contract

```python contract
declare_http_contract(
    interface="tools",
    action="query_run",
    route_name="invoke",
    endpoint="POST /tools",
    outcomes={
        "success": (200, "result"),
        "invalid_input": (400, "typed_error"),
        "internal_error": (500, "typed_error"),
    },
    request_schema={
        "type": "object",
        "properties": {
            "name": {"const": "query_run"},
            "arguments": {
                "type": "object",
                "properties": {
                    "sql": {"type": "string"},
                    "cursor_position": {"type": "integer", "minimum": 0},
                    "page_size": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 1000,
                    },
                    "preview": {"type": "integer", "minimum": 0},
                    "result_delivery": {"enum": ["file", "inline", "auto"]},
                    "result_format": {"enum": ["json_matrix", "csv", "toon"]},
                    "save": {"type": "boolean"},
                    "name": {"type": "string"},
                },
                "required": ["sql"],
                "additionalProperties": False,
                "allOf": [
                    {
                        "if": {"required": ["name"]},
                        "then": {
                            "properties": {"save": {"const": True}},
                            "required": ["save"],
                        },
                    }
                ],
            },
            "instance_id": {"type": "string"},
            "session_id": {"type": ["string", "null"], "pattern": "\\S"},
            "public_base_url": {"type": ["string", "null"], "pattern": "\\S"},
            "asserted_project_root": {
                "type": ["string", "null"],
                "pattern": "\\S",
            },
        },
        "required": [
            "name",
            "arguments",
            "instance_id",
            "session_id",
            "public_base_url",
            "asserted_project_root",
        ],
        "additionalProperties": False,
    },
    response_schemas={
        "success": {
            "type": "object",
            "properties": {
                "result": {
                    "type": "object",
                    "properties": {
                        "value": {"type": "object"},
                        "text": {"type": ["string", "null"]},
                    },
                    "required": ["value", "text"],
                    "additionalProperties": False,
                }
            },
            "required": ["result"],
            "additionalProperties": False,
        },
        "invalid_input": {
            "type": "object",
            "properties": {
                "error": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string"},
                        "message": {"type": "string"},
                        "tool_result": {
                            "type": "object",
                            "properties": {
                                "outcome": {"enum": ["rejected", "failed"]},
                                "diagnostics": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                            },
                            "required": ["outcome", "diagnostics"],
                            "additionalProperties": False,
                        },
                    },
                    "required": ["code", "message", "tool_result"],
                    "additionalProperties": False,
                }
            },
            "required": ["error"],
            "additionalProperties": False,
        },
        "internal_error": {
            "type": "object",
            "properties": {
                "error": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string"},
                        "message": {"type": "string"},
                        "tool_result": {
                            "type": "object",
                            "properties": {
                                "outcome": {"enum": ["rejected", "failed"]},
                                "diagnostics": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                            },
                            "required": ["outcome", "diagnostics"],
                            "additionalProperties": False,
                        },
                    },
                    "required": ["code", "message", "tool_result"],
                    "additionalProperties": False,
                }
            },
            "required": ["error"],
            "additionalProperties": False,
        },
    },
)
```
