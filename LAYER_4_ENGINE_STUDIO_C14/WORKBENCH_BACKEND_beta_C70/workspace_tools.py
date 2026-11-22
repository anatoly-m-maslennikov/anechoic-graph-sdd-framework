"""Validate Beta Workspace tool inputs and present public Workspace results."""

from urllib.parse import quote, urlencode

_TEXT = {"type": "string"}
_ID = {"type": "string", "minLength": 1}
_NUMBER = {"type": "integer", "minimum": 0}
_PAGE_SIZE = {"type": "integer", "minimum": 1, "maximum": 1000}
_DELIVERY = {"type": "string", "enum": ["auto", "inline"]}
_FORMAT = {"type": "string", "enum": ["json_matrix"]}
_SAVE = {"type": "boolean", "default": False}
_COLUMN = {"type": "integer", "minimum": 0}
_DIRECTION = {"type": "string", "enum": ["asc", "desc"]}
_ORDER = {"type": "object", "properties": {"column": _COLUMN, "direction": _DIRECTION},
          "required": ["column", "direction"], "additionalProperties": False}
_FILTER = {"type": "object", "properties": {"column": _COLUMN, "operator": {"const": "contains"}, "value": _TEXT},
           "required": ["column", "operator", "value"], "additionalProperties": False}
GRID = {"type": "object", "properties": {"sort": {"type": "array", "items": _ORDER},
        "filters": {"type": "array", "items": _FILTER}, "group_by": _ORDER}, "additionalProperties": False}
_POSITION = {"type": "string", "enum": ["first", "last"], "default": "last"}
_WORKSPACE = {"workspace_id": _ID}
_VIEW = {**_WORKSPACE, "view_id": _ID}
LINKED_TOOLS = {"workspace_open", "workspace_get"}


def _tool(tool_name, description, required, *, read_only=False, **optional):
    schema = {"type": "object", "properties": {**required, **optional}, "additionalProperties": False}
    if required:
        schema["required"] = list(required)
    return {
        "name": tool_name, "description": description,
        "annotations": {"readOnlyHint": read_only, "destructiveHint": False,
                        "idempotentHint": read_only, "openWorldHint": False},
        "inputSchema": schema,
    }


WORKSPACE_TOOLS = {tool["name"]: tool for tool in (
    _tool("workspace_open", "Initialize or resume the Workspace bound to one browser or native session.",
          {"session_id": _ID}),
    _tool("workspace_list", "List known Workspace IDs for the selected Project.", {}, read_only=True),
    _tool("workspace_get", "Get Workspace Views, active View, and result metadata without result rows.",
          _WORKSPACE, read_only=True),
    _tool("view_create", "Create a stable View in a Workspace.", _WORKSPACE, position=_POSITION, name=_TEXT),
    _tool("view_duplicate", "Duplicate one View's query and cursor into a new independent View.", _VIEW),
    _tool("view_list", "List ordered Workspace Views and their result metadata.", _WORKSPACE, read_only=True),
    _tool("view_get", "Get one View's SQL, revision, and result metadata without rows.", _VIEW, read_only=True),
    _tool("view_update", "Update one View using its expected revision.",
          {**_VIEW, "sql": _TEXT, "expected_revision": _NUMBER}, cursor_position=_NUMBER),
    _tool("view_run", "Run one View and return metadata without result rows.", _VIEW,
          cursor_position=_NUMBER, preview=_NUMBER, save=_SAVE, name=_TEXT),
    _tool("view_check", "Check one View without recording a query log entry.", _VIEW,
          read_only=True, cursor_position=_NUMBER),
    _tool("view_fetch", "Fetch an inline JSON matrix page from one View’s current result.", _VIEW,
          read_only=True, offset=_NUMBER, page_size=_PAGE_SIZE, preview=_NUMBER, grid=GRID,
          result_delivery=_DELIVERY, result_format=_FORMAT),
    _tool("view_focus", "Set the active View for a Workspace.", _VIEW),
    _tool("view_rename", "Rename one View.", {**_VIEW, "name": _TEXT}),
    _tool("view_remove", "Remove one View while retaining at least one View.", _VIEW),
    _tool("query_log_list", "List retained query-log records without result rows.", {},
          read_only=True, limit=_PAGE_SIZE),
    _tool("query_log_get", "Get one retained query-log record without result rows.",
          {"log_id": _ID}, read_only=True),
)}


def workspace_arguments(name, arguments, session_id):
    if name == "workspace_open" and "session_id" not in arguments and session_id is not None:
        arguments = {**arguments, "session_id": session_id}
    schema = WORKSPACE_TOOLS[name]["inputSchema"]
    properties = schema["properties"]
    if set(arguments) - properties.keys() or set(schema.get("required", ())) - arguments.keys():
        raise ValueError("Unexpected or missing Workspace arguments")
    if name == "view_run" and "name" in arguments and not arguments.get("save", False):
        raise ValueError("name is only supported when save is true")
    for key, value in arguments.items():
        field = properties[key]
        if field is _NUMBER:
            if type(value) is not int or value < 0:
                raise ValueError(f"{key} must be a non-negative integer")
        elif field is _PAGE_SIZE:
            if type(value) is not int or not 1 <= value <= 1000:
                raise ValueError(f"{key} must be an integer from 1 to 1000")
        elif field is _SAVE:
            continue
        elif field is GRID:
            if not isinstance(value, dict):
                raise ValueError("grid must be an object")
        elif not isinstance(value, str) or (field is _ID and not value.strip()):
            raise ValueError(f"Invalid {key}")
        elif field in (_POSITION, _DELIVERY, _FORMAT) and value not in field["enum"]:
            raise ValueError(f"Unsupported {key}")
        else:
            value.encode("utf-8")
    return arguments


def valid_workspace_response(name, value):
    if not isinstance(value, dict):
        return False
    if name not in {"query_log_list", "query_log_get"}:
        return True
    if name == "query_log_list":
        if set(value) != {"items"} or not isinstance(value["items"], list):
            return False
        return all(_valid_log_record(record) for record in value["items"])
    return _valid_log_record(value)


def _valid_log_record(value):
    keys = {"log_id", "at", "sql", "outcome", "error", "row_count", "column_count"}
    return (isinstance(value, dict) and set(value) == keys
            and all(isinstance(value[key], str) for key in ("log_id", "at", "sql", "outcome"))
            and value["outcome"] in {"success", "failed"}
            and (value["error"] is None or isinstance(value["error"], str))
            and all(value[key] is None or type(value[key]) is int for key in ("row_count", "column_count")))


def present_workspace(value, project_name, public_base_url, project_root):
    workspace_id = value.get("workspace_id")
    if not isinstance(workspace_id, str) or not workspace_id:
        raise ValueError("Invalid Workspace response")
    result = {**value, "project_name": project_name}
    if public_base_url is not None:
        query = {"workspace": workspace_id}
        if project_root is not None:
            query["project_root"] = project_root
        base = public_base_url.rstrip("/")
        path = f"/anechoic/workbench/{quote(project_name, safe='')}"
        result["workspace_url"] = f"{base}{path}?{urlencode(query)}"
    return result
