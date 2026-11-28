"""Input schemas for Workbench tools."""

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
_STATUS_SCHEMA = {
    "type": "object",
    "properties": {"include_health": {"type": "boolean"}},
    "additionalProperties": False,
}
_RUN_SCHEMA = {
    "type": "object",
    "properties": {
        "sql": _SQL,
        "page_size": {"type": "integer", "minimum": 1, "maximum": 1000},
        "cursor_position": _CURSOR,
        "preview": _PREVIEW,
        "save": {"type": "boolean", "default": False},
        "name": _SQL,
        "result_delivery": {**_DELIVERY, "default": "auto"},
        "result_format": _RESULT_FORMAT,
    },
    "required": ["sql"],
    "additionalProperties": False,
}
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
_PAGE_SCHEMA = {
    "type": "object",
    "properties": {
        "grid": _GRID_SCHEMA,
        "query_id": _SQL,
        "offset": {"type": "integer", "minimum": 0, "default": 0},
        "page_size": {"type": "integer", "minimum": 1, "maximum": 1000},
        "preview": _PREVIEW,
        "result_delivery": _DELIVERY,
        "result_format": _RESULT_FORMAT,
    },
    "required": ["query_id"],
    "additionalProperties": False,
}
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
_VIEW_FETCH_SCHEMA = {
    "type": "object",
    "properties": {
        "grid": _GRID_SCHEMA,
        "workspace_id": _WORKSPACE_ID,
        "view_id": _VIEW_ID,
        "offset": {"type": "integer", "minimum": 0, "default": 0},
        "page_size": {
            "type": "integer",
            "minimum": 1,
            "maximum": 1000,
            "default": 100,
        },
        "preview": _PREVIEW,
        "result_delivery": _DELIVERY,
        "result_format": _RESULT_FORMAT,
    },
    "required": ["workspace_id", "view_id"],
    "additionalProperties": False,
}
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
