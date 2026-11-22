"""Expose Project-scoped saved SQL reads and public links."""

import re
from urllib.parse import parse_qs, quote, urlencode, urlparse
import uuid

import httpx2

from .peer_transport import tool_failure, upstream
from .workspace_tools import _tool

TOOLS = {
    "query_load": _tool("query_load", "Load a Bookmark or saved View.", {"reference": {"type": "string"}}, read_only=True),
    "query_saved_list": _tool("query_saved_list", "List recent Bookmark and saved View metadata.", {}, read_only=True,
                              limit={"type": "integer", "minimum": 1, "maximum": 1000}),
}


def _saved_id(value):
    if not isinstance(value, str):
        return False
    if re.fullmatch(r"[qw]_[0-9a-f]{32}", value):
        return True
    try:
        parsed = uuid.UUID(value)
    except ValueError:
        return False
    return parsed.version == 7 and str(parsed) == value


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


def _link(item, name, base, root):
    if not base or not name:
        return {**item, "saved_query_url": None, "saved_query_url_reason": "workbench_url_unknown"}
    query = {"query": item["saved_query_id"]}
    if root is not None:
        query["project_root"] = root
    return {**item, "saved_query_url": f"{base.rstrip('/')}/anechoic/workbench/{quote(name, safe='')}?{urlencode(query)}"}


async def invoke(name, args, socket, instance_id, project_name, base, root):
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
            value = {"items": [_link(item, project_name, base, root) for item in value["items"]]}
        else:
            if not _record(value, False):
                raise ValueError("Invalid Kernel response")
            value = _link(value, project_name, base, root)
        return {"result": {"value": value, "text": None}}
    except (ValueError, TypeError, KeyError, httpx2.HTTPError):
        return tool_failure("workbench_unavailable", "Saved query service unavailable")
