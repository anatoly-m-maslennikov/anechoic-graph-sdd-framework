"""Small HTTP representation of the shared Project Workbench connector."""

from __future__ import annotations

import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from starlette.requests import Request
from starlette.responses import (
    HTMLResponse,
    JSONResponse,
    Response,
    StreamingResponse,
)
from starlette.routing import BaseRoute, Mount, Route
from starlette.staticfiles import StaticFiles

from MCP_PATCHBAY_C21.FEATURE_MCP.http_paths import (
    IWE_CONSOLE_PATH,
    PROJECT_API_PATH,
    WORKBENCH_PATH,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.backend_client import ToolProtocolError

from MCP_PATCHBAY_C21.FEATURE_MCP.mcp_startup_boundary import warning
from MCP_PATCHBAY_C21.FEATURE_MCP.project_tool_context import (
    native_arguments,
    valid_project_instance,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.shared_backend import SharedGatewayRefusal
from MCP_PATCHBAY_C21.FEATURE_MCP.tool_rest import json_body, request_origin


class WorkbenchRequestError(ValueError):
    """An explicit refusal from the HTTP transport."""


_FRONTEND = (
    Path(__file__).resolve().parents[2]
    / "IWE_CONSOLE_C43"
    / "APP_IWE_CONSOLE"
    / "FEATURE_IWE_CONSOLE_FRONTEND"
    / "dist"
)


async def _arguments(request: Request, shared: bool) -> dict[str, Any]:
    try:
        if (
            request.headers.get("content-type", "").split(";", 1)[0]
            == "application/json"
        ):
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
    public = isinstance(
        error, (ToolProtocolError, WorkbenchRequestError, SharedGatewayRefusal)
    )
    secondary = warning("workbench_request_failed")
    payload = {"error": str(error) if public else "operation failure"}
    if isinstance(error, ToolProtocolError) and error.tool_result is not None:
        payload["code"] = error.code
        payload["tool_result"] = error.tool_result
    if secondary is not None:
        payload["diagnostic_error"] = secondary
    status = (
        502
        if isinstance(error, ToolProtocolError)
        and error.code == "project_receipt_mismatch"
        else 400
    )
    return JSONResponse(payload, status_code=status)


def _json_stream(value: dict[str, Any]) -> Iterator[str]:
    return json.JSONEncoder(
        ensure_ascii=False, allow_nan=False, separators=(",", ":")
    ).iterencode(value)


def _project_name_matches(selection: Any, project_name: str) -> bool:
    name = (
        selection.get("project_name")
        if isinstance(selection, dict)
        else getattr(selection, "project_name", None)
    )
    return isinstance(name, str) and bool(name) and name == project_name


def _unknown_project() -> JSONResponse:
    return JSONResponse(
        {"error": "unknown Workbench project"}, status_code=404
    )


async def _selection(gateway: Any, project_root: Any, shared: bool) -> Any:
    if not shared:
        return getattr(gateway, "selection", None)
    return await gateway.select_project(project_root)


async def _interface_arguments(
    request: Request, shared: bool
) -> tuple[str, dict[str, Any]]:
    try:
        value = json.loads(await json_body(request))
    except ValueError as error:
        raise WorkbenchRequestError(str(error)) from error
    if not isinstance(value, dict) or set(value) - {
        "operation",
        "arguments",
        "project_root",
    }:
        raise WorkbenchRequestError(
            "interface body must contain operation and arguments"
        )
    name, arguments = value.get("operation"), value.get("arguments")
    if (
        not isinstance(name, str)
        or not name
        or not isinstance(arguments, dict)
    ):
        raise WorkbenchRequestError(
            "interface body must contain operation and arguments"
        )
    root = value.get("project_root")
    if shared:
        if not isinstance(root, str):
            raise WorkbenchRequestError("project_root must be a string")
        arguments = {**arguments, "project_root": root}
    elif root is not None:
        arguments = {**arguments, "project_root": root}
    return name, arguments


def _page(gateway, shared, frontend):
    async def page(request: Request) -> Response:
        project_name = request.path_params["project_name"]
        try:
            selection = await _selection(
                gateway, request.query_params.get("project_root", ""), shared
            )
            if not shared and "project_root" in request.query_params:
                native_arguments(
                    {"project_root": request.query_params["project_root"]},
                    selection,
                    gateway.root,
                )
        except ToolProtocolError as error:
            return _error(error)
        except (TypeError, ValueError) as error:
            return JSONResponse({"error": str(error)}, status_code=400)
        if not _project_name_matches(selection, project_name):
            return _unknown_project()
        return _frontend_page(frontend, selection)

    return page


def _frontend_page(frontend, selection):
    instance = (
        selection.get("instance_id")
        if isinstance(selection, dict)
        else getattr(selection, "instance_id", None)
    )
    if not valid_project_instance(instance):
        return _error(
            ToolProtocolError(
                "tool_runtime_failure", "Invalid Workbench Project selection"
            )
        )
    try:
        html = (frontend / "index.html").read_text(encoding="utf-8")
    except OSError, UnicodeError:
        html = ""
    if "</head>" not in html:
        return JSONResponse(
            {"error": "Workbench frontend is unavailable; build required"},
            status_code=503,
        )
    meta = f'<meta name="anechoic-project-instance" content="{instance}">'
    return HTMLResponse(
        html.replace("</head>", f"{meta}</head>", 1),
        headers={"Cache-Control": "no-store"},
    )


def _operation(gateway, shared, fixed_name=None):
    async def endpoint(request: Request) -> Response:
        public_base_url = str(request.base_url)
        if fixed_name is None:
            origin = request_origin(request)
            if origin is None:
                return JSONResponse(
                    {"error": "origin_rejected"}, status_code=403
                )
            public_base_url = origin + "/"
        try:
            if fixed_name is None:
                name, arguments = await _interface_arguments(request, shared)
            else:
                name, arguments = fixed_name, await _arguments(request, shared)
                if name == "query_run":
                    arguments = {"result_delivery": "file", **arguments}
            selection = await _selection(
                gateway, arguments.get("project_root"), shared
            )
            if not _project_name_matches(
                selection, request.path_params["project_name"]
            ):
                return _unknown_project()
            asserted_root = arguments.get("project_root")
            if not shared:
                try:
                    arguments = native_arguments(
                        arguments, selection, gateway.root
                    )
                except ValueError as error:
                    raise WorkbenchRequestError(str(error)) from error
            routing = (
                {"project_instance_id": selection["instance_id"]}
                if shared
                else {"asserted_project_root": asserted_root}
            )
            response = await gateway.call_tool(
                name,
                arguments,
                public_base_url=public_base_url,
                **routing,
            )
            return StreamingResponse(
                _json_stream(response["value"]), media_type="application/json"
            )
        except Exception as error:
            return _error(error)

    return endpoint


def routes(
    gateway: Any, *, shared: bool = False, frontend: Path | None = None
) -> list[BaseRoute]:  # noqa: C901
    frontend = _FRONTEND if frontend is None else frontend
    page = _page(gateway, shared, frontend)
    interface = _operation(gateway, shared)
    operations = [
        (path, _operation(gateway, shared, name))
        for path, name in (
            ("run", "query_run"),
            ("page", "query_page"),
            ("check", "query_check"),
            ("schema", "query_schema"),
            ("status", "workbench_status"),
            ("rebuild", "query_rebuild"),
            ("view-save", "view_save"),
            ("load", "query_load"),
            ("saved-list", "query_saved_list"),
        )
    ]
    prefixes = (IWE_CONSOLE_PATH, WORKBENCH_PATH)
    pages = [f"{prefix}/{{project_name}}" for prefix in prefixes]
    bases = [PROJECT_API_PATH, *pages]
    assets = StaticFiles(directory=frontend / "assets", check_dir=False)
    return [
        *[Route(path, page) for path in pages],
        *[
            Route(f"{base}/interface", interface, methods=["POST"])
            for base in bases
        ],
        *[
            Route(f"{base}/{path}", handler, methods=["POST"])
            for path, handler in operations
            for base in bases
        ],
        *[Mount(f"{prefix}/assets", app=assets) for prefix in prefixes],
    ]


__all__ = ["routes"]
