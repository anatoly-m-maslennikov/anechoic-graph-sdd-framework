
"""Small HTTP representation of the shared Project Workbench connector."""

from __future__ import annotations

import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from starlette.requests import Request
from starlette.responses import FileResponse, JSONResponse, Response, StreamingResponse
from starlette.routing import BaseRoute, Mount, Route
from starlette.staticfiles import StaticFiles

from MCP_PATCHBAY_C21.FEATURE_MCP.http_paths import PROJECT_API_PATH, WORKBENCH_PATH
from MCP_PATCHBAY_C21.FEATURE_MCP.backend_client import ToolProtocolError

from MCP_PATCHBAY_C21.FEATURE_MCP.mcp_startup_boundary import warning
from MCP_PATCHBAY_C21.FEATURE_MCP.project_tool_context import native_arguments
from MCP_PATCHBAY_C21.FEATURE_MCP.shared_backend import SharedGatewayRefusal


class WorkbenchRequestError(ValueError):
    """An explicit refusal from the HTTP transport."""



_INTERFACE_TOOLS = frozenset({
    "workspace_open", "workspace_list", "workspace_get", "view_create", "view_duplicate",
    "view_list", "view_get", "view_update", "view_run", "view_check", "view_fetch",
    "view_focus", "view_rename", "view_remove", "query_log_list", "query_log_get", "view_save",
})

_FRONTEND = (
    Path(__file__).resolve().parents[2]
    / "IWE_CONSOLE_C43"
    / "APP_WORKBENCH"
    / "FEATURE_WORKBENCH_FRONTEND"
    / "dist"
)


async def _arguments(request: Request, shared: bool) -> dict[str, Any]:
    try:
        if request.headers.get("content-type", "").split(";", 1)[0] == "application/json":
            value = await request.json()
        else:
            value = dict(await request.form())
    except ValueError as error:
        raise WorkbenchRequestError(str(error)) from error
    if not isinstance(value, dict):
        raise WorkbenchRequestError("query arguments must be an object")
    if shared and not isinstance(value.get("project_root"), str):
        raise WorkbenchRequestError("project_root must be a string")
    return value


def _error(error: Exception) -> JSONResponse:
    public = isinstance(error, (ToolProtocolError, WorkbenchRequestError, SharedGatewayRefusal))
    secondary = warning("workbench_request_failed")
    payload = {"error": str(error) if public else "operation failure"}
    if secondary is not None:
        payload["diagnostic_error"] = secondary
    return JSONResponse(payload, status_code=400)


def _json_stream(value: dict[str, Any]) -> Iterator[str]:
    return json.JSONEncoder(ensure_ascii=False, allow_nan=False, separators=(",", ":")).iterencode(value)


def _project_name_matches(selection: Any, project_name: str) -> bool:
    name = selection.get("project_name") if isinstance(selection, dict) else getattr(selection, "project_name", None)
    return isinstance(name, str) and bool(name) and name == project_name


def _unknown_project() -> JSONResponse:
    return JSONResponse({"error": "unknown Workbench project"}, status_code=404)


async def _selection(gateway: Any, project_root: Any, shared: bool) -> Any:
    if not shared:
        return getattr(gateway, "selection", None)
    return await gateway.select_project(project_root)


async def _execute(gateway: Any, name: str, arguments: dict[str, Any], shared: bool,
                   public_base_url: str, asserted_project_root: str | None) -> dict[str, Any]:
    if name == "query_run":
        arguments = {"result_delivery": "file", **arguments}
    if not shared:
        if name in getattr(gateway, "tool_blacklist", frozenset()):
            raise WorkbenchRequestError("Unknown Tool")
        result = await gateway.workbench.call_tool(
            name, arguments, public_base_url=public_base_url,
            asserted_project_root=asserted_project_root,
        )
        return result["value"]
    return await gateway.workbench_call(name, arguments, public_base_url=public_base_url)


async def _interface_arguments(request: Request, shared: bool) -> tuple[str, dict[str, Any]]:
    try:
        value = await request.json()
    except ValueError as error:
        raise WorkbenchRequestError(str(error)) from error
    if not isinstance(value, dict) or set(value) - {"operation", "arguments", "project_root"}:
        raise WorkbenchRequestError("interface body must contain operation and arguments")
    name, arguments = value.get("operation"), value.get("arguments")
    if not isinstance(name, str) or name not in _INTERFACE_TOOLS or not isinstance(arguments, dict):
        raise WorkbenchRequestError("unknown Workbench interface operation")
    root = value.get("project_root")
    if shared:
        if not isinstance(root, str):
            raise WorkbenchRequestError("project_root must be a string")
        arguments = {**arguments, "project_root": root}
    elif root is not None:
        arguments = {**arguments, "project_root": root}
    return name, arguments


def _page(gateway, shared):
    async def page(request: Request) -> Response:
        project_name = request.path_params["project_name"]
        try:
            selection = await _selection(gateway, request.query_params.get("project_root", ""), shared)
            if not shared and "project_root" in request.query_params:
                native_arguments({"project_root": request.query_params["project_root"]}, selection, gateway.root)
        except ToolProtocolError as error:
            return _error(error)
        except (TypeError, ValueError) as error:
            return JSONResponse({"error": str(error)}, status_code=400)
        if not _project_name_matches(selection, project_name):
            return _unknown_project()
        if not (_FRONTEND / "index.html").is_file():
            return JSONResponse(
                {"error": "Workbench frontend is unavailable; build required"}, status_code=503
            )
        return FileResponse(_FRONTEND / "index.html")

    return page


def _operation(gateway, shared, name):
    async def endpoint(request: Request) -> Response:  # noqa: C901
        try:
            arguments = await _arguments(request, shared)
            selection = await _selection(gateway, arguments.get("project_root"), shared)
            if not _project_name_matches(selection, request.path_params["project_name"]):
                return _unknown_project()
            asserted_root = arguments.get("project_root")
            if not shared:
                try:
                    arguments = native_arguments(arguments, selection, gateway.root)
                except ValueError as error:
                    raise WorkbenchRequestError(str(error)) from error
            value = await _execute(gateway, name, arguments, shared, str(request.base_url), asserted_root)
            return StreamingResponse(_json_stream(value), media_type="application/json")
        except Exception as error:
            return _error(error)
    return endpoint



def _interface(gateway, shared):
    async def interface(request: Request) -> Response:
        try:
            name, arguments = await _interface_arguments(request, shared)
            selection = await _selection(gateway, arguments.get("project_root"), shared)
            if not _project_name_matches(selection, request.path_params["project_name"]):
                return _unknown_project()
            asserted_root = arguments.get("project_root")
            if not shared:
                try:
                    arguments = native_arguments(arguments, selection, gateway.root)
                except ValueError as error:
                    raise WorkbenchRequestError(str(error)) from error
            value = await _execute(gateway, name, arguments, shared, str(request.base_url), asserted_root)
            return StreamingResponse(_json_stream(value), media_type="application/json")
        except Exception as error:
            return _error(error)

    return interface


def routes(gateway: Any, *, shared: bool = False) -> list[BaseRoute]:  # noqa: C901
    page = _page(gateway, shared)
    interface = _interface(gateway, shared)
    operations = [(path, _operation(gateway, shared, name)) for path, name in (
        ("run", "query_run"), ("page", "query_page"), ("check", "query_check"),
        ("schema", "query_schema"), ("status", "workbench_status"),
        ("rebuild", "query_rebuild"), ("view-save", "view_save"),
        ("load", "query_load"), ("saved-list", "query_saved_list"),
    )]
    return [
        Route(f"{WORKBENCH_PATH}/{{project_name}}", page),
        Route(f"{WORKBENCH_PATH}/{{project_name}}/interface", interface, methods=["POST"]),
        Route(f"{PROJECT_API_PATH}/interface", interface, methods=["POST"]),
        *[Route(f"{base}/{path}", handler, methods=["POST"])
          for path, handler in operations
          for base in (PROJECT_API_PATH, f"{WORKBENCH_PATH}/{{project_name}}")],
        Mount(
            f"{WORKBENCH_PATH}/assets",
            app=StaticFiles(directory=_FRONTEND / "assets", check_dir=False),
        ),
    ]


__all__ = ["routes"]
