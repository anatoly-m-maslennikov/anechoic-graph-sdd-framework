
"""Native MCP adapters for the Project-owned Workbench service."""

from __future__ import annotations

from mcp import types

RUN, PAGE, CHECK, SCHEMA = (
    "query_run",
    "query_page",
    "query_check",
    "query_schema",
)
SAVE_VIEW, LOAD, SAVED_LIST = "view_save", "query_load", "query_saved_list"
REBUILD = "query_rebuild"
ATOM_DOCUMENT = "iwe_console_atom_document"
SYNC_STATUS, LEGACY_SYNC_STATUS = "iwe_console_status", "workbench_status"
WORKSPACE_OPEN, WORKSPACE_LIST, WORKSPACE_GET = (
    "workspace_open",
    "workspace_list",
    "workspace_get",
)
VIEW_CREATE, VIEW_DUPLICATE, VIEW_LIST, VIEW_GET, VIEW_UPDATE = (
    "view_create", "view_duplicate", "view_list", "view_get", "view_update"
)
VIEW_RUN, VIEW_CHECK, VIEW_FETCH, VIEW_FOCUS = (
    "view_run",
    "view_check",
    "view_fetch",
    "view_focus",
)
VIEW_RENAME, VIEW_REMOVE = "view_rename", "view_remove"
QUERY_LOG_LIST, QUERY_LOG_GET = "query_log_list", "query_log_get"
INTERFACE_TOOLS = (
    WORKSPACE_OPEN,
    WORKSPACE_LIST,
    WORKSPACE_GET,
    VIEW_CREATE,
    VIEW_DUPLICATE,
    VIEW_LIST,
    VIEW_GET,
    VIEW_UPDATE,
    VIEW_RUN,
    VIEW_CHECK,
    VIEW_FETCH,
    VIEW_FOCUS,
    VIEW_RENAME,
    VIEW_REMOVE,
    QUERY_LOG_LIST,
    QUERY_LOG_GET,
)
NATIVE_TOOLS = (
    RUN,
    PAGE,
    CHECK,
    SCHEMA,
    SAVE_VIEW,
    LOAD,
    SAVED_LIST,
    *INTERFACE_TOOLS,
    SYNC_STATUS,
    LEGACY_SYNC_STATUS,
    REBUILD,
    ATOM_DOCUMENT,
)

_CURSOR = {"type": "integer", "minimum": 0}
_SQL = {"type": "string"}
_DELIVERY = {
    "type": "string",
    "enum": ["file", "inline", "auto"],
    "default": "file",
}
_RESULT_FORMAT = {
    "type": "string",
    "enum": ["json_matrix", "csv", "toon"],
    "default": "json_matrix",
}
_PREVIEW = {"type": "integer", "minimum": 0}
_RUN_SCHEMA = {"type": "object", "properties": {"sql": _SQL, "page_size": {"type": "integer", "minimum": 1, "maximum": 1000}, "cursor_position": _CURSOR, "preview": _PREVIEW, "save": {"type": "boolean", "default": False}, "name": _SQL, "result_delivery": {**_DELIVERY, "default": "auto"}, "result_format": _RESULT_FORMAT}, "required": ["sql"], "additionalProperties": False}
_CHECK_SCHEMA = {
    "type": "object",
    "properties": {"sql": _SQL, "cursor_position": _CURSOR},
    "required": ["sql"],
    "additionalProperties": False,
}
_COLUMN_INDEX = {"type": "integer", "minimum": 0}
_GRID_ORDER = {
    "type": "object",
    "properties": {
        "column": _COLUMN_INDEX,
        "direction": {"type": "string", "enum": ["asc", "desc"]},
    },
    "required": ["column", "direction"],
    "additionalProperties": False,
}
_GRID_FILTER = {
    "type": "object",
    "properties": {
        "column": _COLUMN_INDEX,
        "operator": {"type": "string", "enum": ["contains"]},
        "value": _SQL,
    },
    "required": ["column", "operator", "value"],
    "additionalProperties": False,
}
_GRID_SCHEMA = {
    "type": "object",
    "properties": {
        "sort": {"type": "array", "items": _GRID_ORDER},
        "filters": {"type": "array", "items": _GRID_FILTER},
        "group_by": _GRID_ORDER,
    },
    "additionalProperties": False,
}
_PAGE_SCHEMA = {"type": "object", "properties": {"grid": _GRID_SCHEMA, "query_id": _SQL, "offset": {"type": "integer", "minimum": 0, "default": 0}, "page_size": {"type": "integer", "minimum": 1, "maximum": 1000}, "preview": _PREVIEW, "result_delivery": _DELIVERY, "result_format": _RESULT_FORMAT}, "required": ["query_id"], "additionalProperties": False}
_VIEW_SCHEMA = {
    "type": "object",
    "properties": {"sql": _SQL, "name": _SQL},
    "required": ["sql"],
    "additionalProperties": False,
}
_LOAD_SCHEMA = {
    "type": "object",
    "properties": {"reference": _SQL},
    "required": ["reference"],
    "additionalProperties": False,
}
_LIST_SCHEMA = {
    "type": "object",
    "properties": {
        "limit": {"type": "integer", "minimum": 1, "maximum": 1000}
    },
    "additionalProperties": False,
}
_EMPTY_SCHEMA = {
    "type": "object",
    "properties": {},
    "additionalProperties": False,
}
_WORKSPACE_ID = {"type": "string", "minLength": 1}
_VIEW_ID = {"type": "string", "minLength": 1}
_POSITION = {"type": "string", "enum": ["first", "last"], "default": "last"}
_WORKSPACE_OPEN_SCHEMA = {
    "type": "object",
    "properties": {"session_id": _WORKSPACE_ID},
    "required": ["session_id"],
    "additionalProperties": False,
}
_WORKSPACE_GET_SCHEMA = {
    "type": "object",
    "properties": {"workspace_id": _WORKSPACE_ID},
    "required": ["workspace_id"],
    "additionalProperties": False,
}
_VIEW_CREATE_SCHEMA = {
    "type": "object",
    "properties": {
        "workspace_id": _WORKSPACE_ID,
        "position": _POSITION,
        "name": _SQL,
    },
    "required": ["workspace_id"],
    "additionalProperties": False,
}
_VIEW_DUPLICATE_SCHEMA = {
    "type": "object",
    "properties": {"workspace_id": _WORKSPACE_ID, "view_id": _VIEW_ID},
    "required": ["workspace_id", "view_id"],
    "additionalProperties": False,
}
_VIEW_GET_SCHEMA = {
    "type": "object",
    "properties": {"workspace_id": _WORKSPACE_ID, "view_id": _VIEW_ID},
    "required": ["workspace_id", "view_id"],
    "additionalProperties": False,
}
_VIEW_UPDATE_SCHEMA = {
    "type": "object",
    "properties": {
        "workspace_id": _WORKSPACE_ID,
        "view_id": _VIEW_ID,
        "sql": _SQL,
        "cursor_position": _CURSOR,
        "expected_revision": {"type": "integer", "minimum": 0},
    },
    "required": ["workspace_id", "view_id", "sql", "expected_revision"],
    "additionalProperties": False,
}
_VIEW_RUN_SCHEMA = {
    "type": "object",
    "properties": {
        "workspace_id": _WORKSPACE_ID,
        "view_id": _VIEW_ID,
        "cursor_position": _CURSOR,
        "preview": _PREVIEW,
        "save": {"type": "boolean", "default": False},
        "name": _SQL,
    },
    "required": ["workspace_id", "view_id"],
    "additionalProperties": False,
}
_VIEW_FETCH_SCHEMA = {"type": "object", "properties": {"grid": _GRID_SCHEMA, "workspace_id": _WORKSPACE_ID, "view_id": _VIEW_ID, "offset": {"type": "integer", "minimum": 0, "default": 0}, "page_size": {"type": "integer", "minimum": 1, "maximum": 1000, "default": 100}, "preview": _PREVIEW, "result_delivery": _DELIVERY, "result_format": _RESULT_FORMAT}, "required": ["workspace_id", "view_id"], "additionalProperties": False}
_VIEW_CHECK_SCHEMA = {
    "type": "object",
    "properties": {
        "workspace_id": _WORKSPACE_ID,
        "view_id": _VIEW_ID,
        "cursor_position": _CURSOR,
    },
    "required": ["workspace_id", "view_id"],
    "additionalProperties": False,
}
_VIEW_RENAME_SCHEMA = {
    "type": "object",
    "properties": {
        "workspace_id": _WORKSPACE_ID,
        "view_id": _VIEW_ID,
        "name": _SQL,
    },
    "required": ["workspace_id", "view_id", "name"],
    "additionalProperties": False,
}
_QUERY_LOG_GET_SCHEMA = {
    "type": "object",
    "properties": {"log_id": _WORKSPACE_ID},
    "required": ["log_id"],
    "additionalProperties": False,
}
_SAVE_VIEW_SCHEMA = {
    "type": "object",
    "properties": {
        "workspace_id": _WORKSPACE_ID,
        "view_id": _VIEW_ID,
        "sql": _SQL,
        "name": _SQL,
    },
    "additionalProperties": False,
}


_DESCRIPTIONS = {
    RUN: "Run SQL. Automatic delivery returns small results inline and larger results as files.",
    ATOM_DOCUMENT: (
        "Read an admitted Atom revision and its authored Markdown body."
    ),
    REBUILD: "Rebuild one query table or all query tables; return replacement result IDs.",
    LOAD: "Load an explicitly requested Bookmark or saved View.",
    SAVED_LIST: "List recent Bookmark and saved View metadata.",
    SYNC_STATUS: "Read source-indexing status without starting or restarting IWE Console.",
    LEGACY_SYNC_STATUS: "Legacy alias for iwe_console_status.",
    WORKSPACE_OPEN: "Initialize or resume the Workspace bound to one browser or native session.",
    WORKSPACE_LIST: "List known Workspace IDs for the selected Project.",
    WORKSPACE_GET: "Get Workspace Views, active View, and result metadata without result rows.",
    VIEW_CREATE: "Create a stable View in a Workspace.",
    VIEW_DUPLICATE: "Duplicate one View's query and cursor into a new independent View.",
    VIEW_LIST: "List ordered Workspace Views and their result metadata.",
    VIEW_GET: "Get one View's SQL, revision, and result metadata without rows.",
    VIEW_UPDATE: "Update one View using its expected revision.",
    VIEW_RUN: "Run one View and return metadata without result rows.",
    VIEW_CHECK: "Check one View without recording a query log entry.",
    VIEW_FETCH: "Fetch an optional page from one View's current result.",
    VIEW_FOCUS: "Set the active View for a Workspace.",
    VIEW_RENAME: "Rename one View.",
    VIEW_REMOVE: "Remove one View while retaining at least one View.",
    QUERY_LOG_LIST: "List retained query-log records without result rows.",
    QUERY_LOG_GET: "Get one retained query-log record without result rows.",
}


def native_tools() -> tuple[types.Tool, ...]:
    schemas = {RUN: _RUN_SCHEMA, PAGE: _PAGE_SCHEMA, CHECK: _CHECK_SCHEMA, SCHEMA: _EMPTY_SCHEMA,
               SAVE_VIEW: _SAVE_VIEW_SCHEMA, LOAD: _LOAD_SCHEMA, SAVED_LIST: _LIST_SCHEMA,
               WORKSPACE_OPEN: _WORKSPACE_OPEN_SCHEMA, WORKSPACE_LIST: _EMPTY_SCHEMA,
               WORKSPACE_GET: _WORKSPACE_GET_SCHEMA, VIEW_CREATE: _VIEW_CREATE_SCHEMA,
               VIEW_DUPLICATE: _VIEW_DUPLICATE_SCHEMA,
               VIEW_LIST: _WORKSPACE_GET_SCHEMA, VIEW_GET: _VIEW_GET_SCHEMA,
               VIEW_UPDATE: _VIEW_UPDATE_SCHEMA, VIEW_RUN: _VIEW_RUN_SCHEMA,
               VIEW_CHECK: _VIEW_CHECK_SCHEMA, VIEW_FETCH: _VIEW_FETCH_SCHEMA,
               VIEW_FOCUS: _VIEW_GET_SCHEMA, VIEW_RENAME: _VIEW_RENAME_SCHEMA,
               VIEW_REMOVE: _VIEW_GET_SCHEMA, QUERY_LOG_LIST: _LIST_SCHEMA,
               QUERY_LOG_GET: _QUERY_LOG_GET_SCHEMA,
               SYNC_STATUS: _EMPTY_SCHEMA, LEGACY_SYNC_STATUS: _EMPTY_SCHEMA,
               REBUILD: {"type": "object", "properties": {"target": {"type": "string", "minLength": 1}}, "required": ["target"], "additionalProperties": False}}
    schemas[ATOM_DOCUMENT] = {
        "type": "object",
        "properties": {"ref_id": {"type": "string"}},
        "required": ["ref_id"],
        "additionalProperties": False,
    }
    writes = {
        RUN,
        SAVE_VIEW,
        WORKSPACE_OPEN,
        VIEW_CREATE,
        VIEW_DUPLICATE,
        VIEW_UPDATE,
        VIEW_RUN,
        VIEW_FOCUS,
        VIEW_RENAME,
        VIEW_REMOVE,
        REBUILD,
    }
    return tuple(
        types.Tool(
            name=name,
            description=_DESCRIPTIONS.get(
                name, f"Workbench {name.replace('_', ' ')}."
            ),
            annotations=types.ToolAnnotations(
                read_only_hint=name not in writes,
                destructive_hint=False,
                idempotent_hint=name not in writes,
                open_world_hint=False,
            ),
            input_schema=schemas[name],
        )
        for name in NATIVE_TOOLS
    )


__all__ = ["CHECK", "INTERFACE_TOOLS", "LOAD", "NATIVE_TOOLS", "PAGE", "QUERY_LOG_GET", "QUERY_LOG_LIST", "REBUILD", "RUN", "SAVED_LIST", "SAVE_VIEW", "SCHEMA", "SYNC_STATUS", "VIEW_CHECK", "VIEW_CREATE", "VIEW_DUPLICATE", "VIEW_FETCH", "VIEW_FOCUS", "VIEW_GET", "VIEW_LIST", "VIEW_REMOVE", "VIEW_RENAME", "VIEW_RUN", "VIEW_UPDATE", "WORKSPACE_GET", "WORKSPACE_LIST", "WORKSPACE_OPEN", "native_tools"]
