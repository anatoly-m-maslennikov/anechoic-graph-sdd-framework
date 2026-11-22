"""Serve the stateless Beta Workbench API on a private Unix socket."""
import argparse
import json
import os
import re
import socket
import stat
import sys
import threading
from pathlib import Path

import httpx2
import uvicorn
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from . import lifecycle_tools, projection_tools, saved_sql_tools, schema_tools, workspace_tools
from .peer_transport import tool_failure, upstream

_FIELDS = {"name", "arguments", "instance_id", "session_id", "public_base_url", "asserted_project_root"}
_ANNOTATIONS = {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False}
_PAGE_SIZE = {"type": "integer", "minimum": 1, "maximum": 1000}
_OFFSET = {"type": "integer", "minimum": 0}
_DELIVERY = {"enum": ["auto", "inline"], "type": "string"}
_FORMAT = {"enum": ["json_matrix"], "type": "string"}


def _descriptor(name, description, properties, required=()):
    return {
        "name": name, "description": description, "annotations": _ANNOTATIONS,
        "inputSchema": {"type": "object", "properties": properties,
                        "required": list(required), "additionalProperties": False},
    }


TOOLS = {
    "query_run": json.loads(Path(__file__).with_name("query_run.json").read_text(encoding="utf-8")),
    "query_schema": _descriptor("query_schema", "Read the selected Project's public SQL schema.", {}),
    "query_check": _descriptor("query_check", "Check read-only SQL without retaining the result.",
                               {"sql": {"type": "string"}, "cursor_position": _OFFSET}, ("sql",)),
    "query_page": _descriptor("query_page", "Read a page of a retained Project query result.",
                              {"query_id": {"type": "string"}, "offset": _OFFSET, "page_size": _PAGE_SIZE,
                               "result_delivery": _DELIVERY, "result_format": _FORMAT,
                               "grid": workspace_tools.GRID}, ("query_id",)),
    **projection_tools.TOOLS,
    **saved_sql_tools.TOOLS,
    **lifecycle_tools.TOOLS,
    **workspace_tools.WORKSPACE_TOOLS,
}



async def read_tool_request(request):
    body = bytearray()
    async for chunk in request.stream():
        if len(body) + len(chunk) > 65536:
            raise ValueError("Request is too large")
        body.extend(chunk)
    return json.loads(body)


async def _query(database_socket, instance_id, fields):
    try:
        result = await upstream(database_socket, "POST", "/database", json={"instance_id": instance_id, **fields})
        if "error" in result:
            error = result["error"]
            message = error.get("message", "Query failed") if isinstance(error, dict) else "Query failed"
            return tool_failure("query_error", str(message))
        value = result["result"]
        if not isinstance(value, dict) or not {"columns", "rows"} <= value.keys():
            raise ValueError("Invalid Kernel response")
        return {"result": {"value": value, "text": None}}
    except (ValueError, TypeError) as error:
        return tool_failure("value_error", str(error))
    except httpx2.HTTPError:
        return tool_failure("workbench_unavailable", "Kernel unavailable")


def _sql(args):
    sql = args.get("sql")
    if not isinstance(sql, str):
        raise ValueError("SQL must be a string")
    cursor = args.get("cursor_position")
    if "cursor_position" in args:
        encoded = sql.encode("utf-16-le")
        if type(cursor) is not int or not 0 <= cursor <= len(encoded) // 2:
            raise ValueError("cursor_position is outside SQL")
        encoded[:cursor * 2].decode("utf-16-le")
    return sql


def _query_fields(name, args):
    if set(args) - TOOLS[name]["inputSchema"]["properties"].keys():
        raise ValueError("Unexpected arguments")
    if name == "query_check":
        return {"sql": _sql(args)}
    delivery = args.get("result_delivery", "auto" if name == "query_run" else "inline")
    if delivery not in ("auto", "inline") or args.get("result_format", "json_matrix") != "json_matrix":
        raise ValueError("Only inline JSON matrix delivery is supported")
    default_size = 1000 if name == "query_run" and delivery == "auto" else 100
    size = args.get("page_size", default_size)
    if type(size) is not int or not 1 <= size <= 1000:
        raise ValueError("page_size must be an integer from 1 to 1000")
    if name == "query_run":
        if type(args.get("save", False)) is not bool:
            raise ValueError("save must be a boolean")
        if "name" in args and (not args.get("save", False) or not isinstance(args["name"], str)):
            raise ValueError("name requires save and must be a string")
        if "name" in args:
            args["name"].encode("utf-8")
        return {"sql": _sql(args), "page_size": size}
    query_id, offset = args.get("query_id"), args.get("offset", 0)
    if not isinstance(query_id, str) or type(offset) is not int or offset < 0:
        raise ValueError("Expected query_id and a non-negative offset")
    fields = {"query_id": query_id, "offset": offset, "page_size": size}
    if "grid" in args:
        if not isinstance(args["grid"], dict):
            raise ValueError("grid must be an object")
        fields["grid"] = args["grid"]
    return fields


async def _workspace(database_socket, instance_id, name, args, session_id, project_name, public_base_url, project_root):
    try:
        fields = workspace_tools.workspace_arguments(name, args, session_id)
        if name == "view_run":
            fields = {k: v for k, v in fields.items() if k not in {"save", "name"}}
        if name in workspace_tools.LINKED_TOOLS and not project_name:
            raise ValueError("Workbench Project name is unavailable")
    except ValueError as error:
        return tool_failure("tool_input_invalid", str(error))
    try:
        result = await upstream(database_socket, "POST", "/workspace", json={
            "instance_id": instance_id, "operation": name, "arguments": fields,
        })
        if "error" in result:
            error = result["error"]
            if not isinstance(error["code"], str) or not isinstance(error["message"], str):
                raise ValueError("Invalid Workspace response")
            return tool_failure(error["code"], error["message"])
        value = result["result"]
        if not workspace_tools.valid_workspace_response(name, value):
            raise TypeError("Invalid Workspace response")
        if name == "view_run" and args.get("save", False) and value.get("status") == "success":
            value |= {"outcome": "partial", "save_error": "No admitted actor is available for saving"}
        if name in workspace_tools.LINKED_TOOLS:
            value = workspace_tools.present_workspace(value, project_name, public_base_url, project_root)
        return {"result": {"value": value, "text": None}}
    except (ValueError, TypeError, KeyError, httpx2.HTTPError):
        return tool_failure("workbench_unavailable", "Workspace service unavailable")


async def execute_tool(database_socket, instance_id, name, args, *, session_id=None, project_name=None,
                       public_base_url=None, project_root=None, orchestrator_socket=None, worker_binding=None):
    if name in saved_sql_tools.TOOLS:
        return await saved_sql_tools.invoke(name, args, database_socket, instance_id, project_name,
                                            public_base_url, project_root)
    if name in lifecycle_tools.TOOLS:
        return await lifecycle_tools.invoke(name, args, orchestrator_socket, worker_binding, instance_id)
    if name in projection_tools.TOOLS:
        return await projection_tools.invoke(name, args, database_socket, orchestrator_socket, worker_binding, instance_id)
    if name in workspace_tools.WORKSPACE_TOOLS:
        return await _workspace(database_socket, instance_id, name, args, session_id, project_name,
                                public_base_url, project_root)
    if name == "query_schema":
        return await schema_tools.schema(database_socket, instance_id, args)
    if name not in TOOLS:
        return tool_failure("tool_unavailable", "Unknown Tool")
    try:
        fields = _query_fields(name, args)
    except ValueError as error:
        return tool_failure("tool_input_invalid", str(error))
    result = await _query(database_socket, instance_id, fields)
    if name == "query_run" and args.get("save", False) and "result" in result:
        result["result"]["value"].update(outcome="partial", save_error="No admitted actor is available for saving")
    if name == "query_check" and "result" in result:
        value = result["result"]["value"]
        result["result"]["value"] = {"valid": True, "columns": value["columns"], "sql": fields["sql"],
                                     "row_count": len(value["rows"]), "column_count": len(value["columns"])}
    return result


def _tool_route(database_socket, instance_id, project_root, host_root, blacklist, project_name,
                orchestrator_socket, worker_binding):
    async def invoke(request):
        try:
            data = await read_tool_request(request)
            if (not isinstance(data, dict) or set(data) != _FIELDS or data["instance_id"] != instance_id
                    or not isinstance(data["name"], str) or not isinstance(data["arguments"], dict)
                    or any(data[k] is not None and (not isinstance(data[k], str) or not data[k].strip())
                           for k in ("session_id", "public_base_url", "asserted_project_root"))):
                raise ValueError("Invalid Tool request envelope")
            if data["asserted_project_root"] not in (None, project_root, host_root):
                raise ValueError("project_root does not match the bound Project")
            if data["name"] not in TOOLS or data["name"] in blacklist:
                return JSONResponse(tool_failure("tool_unavailable", "Unknown Tool"))
            return JSONResponse(await execute_tool(database_socket, instance_id, data["name"], data["arguments"],
                session_id=data["session_id"], project_name=project_name, public_base_url=data["public_base_url"],
                project_root=data["asserted_project_root"], orchestrator_socket=orchestrator_socket,
                worker_binding=worker_binding))
        except (ValueError, TypeError) as error:
            return JSONResponse(tool_failure("value_error", str(error)))
    return invoke


def create_app(instance_id, manifest_sha256, project_root, database_socket, orchestrator_socket,
               *, host_root=None, blacklist=(), project_name=None, worker_binding=None):
    async def health(_request):
        try:
            data = await upstream(database_socket, "GET", "/health")
            result = data.get("result", {})
            if (result.get("instance_id") != instance_id or result.get("manifest_sha256") != manifest_sha256
                    or type(result.get("pid")) is not int or result.get("ready") is not True):
                raise ValueError("Invalid Kernel binding")
            return JSONResponse({"ready": True, "instance_id": instance_id, "manifest_sha256": manifest_sha256,
                                 "pid": os.getpid(), "kernel_pid": result["pid"], "generation": result["generation"]})
        except (httpx2.HTTPError, ValueError, TypeError, AttributeError):
            return JSONResponse({"ready": False, "instance_id": instance_id, "manifest_sha256": manifest_sha256,
                                 "pid": os.getpid(), "kernel_pid": None}, status_code=503)

    def bound(request):
        return list(request.query_params.multi_items()) == [("instance_id", instance_id)]

    async def catalog(request):
        if not bound(request):
            return JSONResponse(tool_failure("value_error", "Invalid Tool request binding"))
        tools = [tool for name, tool in TOOLS.items() if name not in blacklist]
        return JSONResponse({"result": {"tools": tools, "blacklist": list(blacklist)}})

    async def worker_runs(request):
        if not bound(request):
            return JSONResponse(tool_failure("value_error", "Invalid Worker Run request binding"))
        try:
            result = await upstream(orchestrator_socket, "GET", "/jobs/worker-runs", params={"instance_id": instance_id})
            return JSONResponse(result)
        except (httpx2.HTTPError, ValueError, TypeError):
            return JSONResponse(tool_failure("workbench_unavailable", "Orchestrator unavailable"))

    invoke = _tool_route(database_socket, instance_id, project_root, host_root, blacklist, project_name,
                         orchestrator_socket, worker_binding)
    return Starlette(routes=[Route("/health", health), Route("/tools", catalog),
                             Route("/tools", invoke, methods=["POST"]), Route("/jobs/worker-runs", worker_runs)])


def socket_path(value):
    path = Path(value)
    parent = path.parent
    info = parent.stat()
    if (not path.is_absolute() or str(path) != value or path.exists() or path.is_symlink()
            or parent.resolve(strict=True) != parent or parent.is_symlink()
            or not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid()
            or stat.S_IMODE(info.st_mode) & 0o077):
        raise ValueError("Socket directory is unavailable or unsafe")
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("socket", "database-socket", "orchestrator-socket", "instance-id", "manifest-sha256", "project-root"):
        parser.add_argument("--" + name, required=True)
    parser.add_argument("--project-name")
    args = parser.parse_args()
    if not args.instance_id or re.fullmatch(r"[0-9a-f]{64}", args.manifest_sha256) is None:
        parser.error("Invalid Project binding")
    if not Path(args.project_root).is_absolute():
        parser.error("Project root must be absolute")
    path = socket_path(args.socket)
    app = create_app(args.instance_id, args.manifest_sha256, args.project_root, args.database_socket,
                     args.orchestrator_socket, project_name=args.project_name)
    serve(path, app)


def serve(path, app, *, shutdown_timeout=None):
    server = uvicorn.Server(uvicorn.Config(app, log_level="warning", timeout_graceful_shutdown=shutdown_timeout))
    def watch_parent():
        while os.read(sys.stdin.fileno(), 4096):
            pass
        server.should_exit = True
    threading.Thread(target=watch_parent, daemon=True).start()
    os.umask(0o077)
    bound = False
    try:
        with socket.socket(socket.AF_UNIX) as listener:
            listener.bind(str(path))
            bound = True
            listener.listen(128)
            server.run(sockets=[listener])
    finally:
        if bound:
            path.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
