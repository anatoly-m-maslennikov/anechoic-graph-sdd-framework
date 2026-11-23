"""Expose Project-scoped saved SQL and public links."""

import re
import uuid
from urllib.parse import parse_qs, quote, urlencode, urlparse

import httpx2

from .peer_transport import tool_failure, upstream
from .workspace_tools import _TEXT, _VIEW, _tool

TOOLS = {
    "query_load": _tool("query_load", "Load a Bookmark or saved View.", {"reference": {"type": "string"}}, read_only=True),
    "query_saved_list": _tool("query_saved_list", "List recent Bookmark and saved View metadata.", {}, read_only=True,
                              limit={"type": "integer", "minimum": 1, "maximum": 1000}),
    "view_save": _tool("view_save", "Save a View's exact SQL without executing it.", {}, **_VIEW, sql=_TEXT, name=_TEXT),
}
TOOLS["view_save"]["inputSchema"]["oneOf"] = [
    {"required": list(_VIEW), "not": {"anyOf": [{"required": ["sql"]}, {"required": ["name"]}]}},
    {"required": ["sql"], "not": {"anyOf": [{"required": [key]} for key in _VIEW]}},
]


def run_arguments(args):
    if type(args.get("save", False)) is not bool:
        raise ValueError("save must be a boolean")
    if "name" in args:
        if not args.get("save", False) or not isinstance(args["name"], str):
            raise ValueError("name requires save and must be a string")
        args["name"].encode("utf-8")
    return {key: args[key] for key in ("save", "name") if key in args}


def _new_id(value):
    if not isinstance(value, str):
        return False
    try:
        parsed = uuid.UUID(value)
    except ValueError:
        return False
    return parsed.version == 7 and str(parsed) == value


def _saved_id(value):
    return isinstance(value, str) and (re.fullmatch(r"[qw]_[0-9a-f]{32}", value) is not None or _new_id(value))


def _reference(value, name, base, root):
    if _saved_id(value):
        return value
    if not isinstance(value, str) or not base or not name:
        raise ValueError("saved query reference must be an ID or this Project's URL")
    parsed = urlparse(value)
    query = parse_qs(parsed.query, keep_blank_values=True)
    if (f"{parsed.scheme}://{parsed.netloc}" != base.rstrip("/")
            or parsed.path != f"/anechoic/workbench/{quote(name, safe='')}" or parsed.params or parsed.fragment
            or set(query) - {"query", "project_root"} or len(query.get("query", [])) != 1
            or ("project_root" in query and query["project_root"] != [root]) or not _saved_id(query["query"][0])):
        raise ValueError("saved query URL is not for this Project")
    return query["query"][0]


def _arguments(name, args, project_name, base, root):
    if name == "query_load":
        if set(args) != {"reference"}:
            raise ValueError("Expected reference")
        return {"reference": _reference(args["reference"], project_name, base, root)}
    if name == "view_save":
        if set(args) not in (_VIEW.keys(), {"sql"}, {"sql", "name"}) or any(
            not isinstance(value, str) or (key in _VIEW and not value.strip()) for key, value in args.items()
        ):
            raise ValueError("Expected Workspace and View IDs or SQL and optional name")
        for value in args.values():
            value.encode("utf-8")
        return args
    if set(args) - {"limit"}:
        raise ValueError("Unexpected arguments")
    limit = args.get("limit", 20)
    if type(limit) is not int or not 1 <= limit <= 1000:
        raise ValueError("limit must be an integer from 1 to 1000")
    return args


def _record(value, listed):
    required = {"saved_query_id", "kind", "preview", "saved_at"} if listed else {"saved_query_id", "kind", "sql"}
    optional = {"name"} if listed else {"name", "saved_at"}
    return (isinstance(value, dict) and required <= value.keys() <= required | optional
            and _saved_id(value["saved_query_id"]) and value["kind"] in ("query", "view")
            and all(isinstance(value[key], str) for key in value if key != "kind"))


def public_page(name, request_base, configured_url):
    if request_base is not None:
        return f"{request_base.rstrip('/')}/anechoic/workbench/{quote(name, safe='')}" if name and request_base else None
    if (not isinstance(configured_url, str) or not configured_url
            or any(char.isspace() or ord(char) < 32 or ord(char) == 127 for char in configured_url)
            or "?" in configured_url or "#" in configured_url):
        return None
    try:
        parsed = urlparse(configured_url)
        _ = parsed.port
    except ValueError:
        return None
    if (parsed.scheme not in {"http", "https"} or not parsed.hostname or not parsed.path
            or parsed.username is not None or parsed.password is not None or parsed.params):
        return None
    return configured_url


def _link(item, page, root):
    if page is None:
        return {**item, "saved_query_url": None, "saved_query_url_reason": "workbench_url_unknown"}
    query = {"query": item["saved_query_id"]}
    if root is not None:
        query["project_root"] = root
    return {**item, "saved_query_url": f"{page}?{urlencode(query)}"}


def present_run_save(value, args, page, root):
    """Link a saved Bookmark while preserving the completed query response."""
    if "saved_query_id" not in value:
        if value.get("outcome") != "partial" or not isinstance(value.get("save_error"), str) or not value["save_error"]:
            raise ValueError("Invalid saved query response")
        return value
    if not _new_id(value["saved_query_id"]) or "save_error" in value:
        raise ValueError("Invalid saved query response")
    name = args.get("name", "")
    named = {"name": name} if name.strip() else {}
    return _link({**value, "kind": "query", **named}, page, root)


async def invoke(name, args, socket, instance_id, project_name, base, root, *, page):
    try:
        fields = _arguments(name, args, project_name, base, root)
    except (ValueError, TypeError):
        return tool_failure("tool_input_invalid", "Invalid saved query arguments")
    try:
        result = await upstream(socket, "POST", "/workspace", json={
            "instance_id": instance_id, "operation": name, "arguments": fields})
        if "error" in result:
            error = result["error"]
            if not isinstance(error["code"], str) or not isinstance(error["message"], str):
                raise ValueError("Invalid Kernel response")
            return tool_failure(error["code"], error["message"])
        value = result["result"]
        if name == "query_saved_list":
            if (not isinstance(value, dict) or set(value) != {"items"} or not isinstance(value["items"], list)
                    or not all(_record(item, True) for item in value["items"])):
                raise ValueError("Invalid Kernel response")
            value = {"items": [_link(item, page, root) for item in value["items"]]}
        else:
            if not _record(value, False):
                raise ValueError("Invalid Kernel response")
            if name == "view_save":
                if value["kind"] != "view" or "saved_at" not in value or not _new_id(value["saved_query_id"]):
                    raise ValueError("Invalid Kernel response")
                value |= {key: fields[key] for key in _VIEW if key in fields}
            value = _link(value, page, root)
        return {"result": {"value": value, "text": None}}
    except (ValueError, TypeError, KeyError, httpx2.HTTPError):
        return tool_failure("workbench_unavailable", "Saved query service unavailable")
