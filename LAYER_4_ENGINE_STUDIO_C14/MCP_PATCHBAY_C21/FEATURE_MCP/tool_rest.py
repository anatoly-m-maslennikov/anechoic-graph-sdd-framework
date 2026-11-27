"""Serve the public Tool REST contract on the loopback transport."""

import json
from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from starlette.responses import JSONResponse
from starlette.routing import Route

from MCP_PATCHBAY_C21.FEATURE_MCP.backend_client import ToolProtocolError
from MCP_PATCHBAY_C21.FEATURE_MCP.http_paths import TOOL_REST_PATH
from MCP_PATCHBAY_C21.FEATURE_MCP.project_tool_context import (
    native_arguments,
    valid_project_instance,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.runtime_request_context import (
    RuntimeRequestContext,
    bind_request_context,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.shared_gateway_support import (
    valid_tool_response,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.shared_tool_contract import public_tool

INSTANCE_HEADER = "X-Anechoic-Project-Instance"
MAX_TOOL_REQUEST_BYTES = 65_536


class Invocation(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    name: str = Field(min_length=1)
    arguments: dict[str, Any] | None
    session_id: str | None
    public_base_url: str | None


def fault(code, *, project=None, status=200, tool=None):
    error = {"code": code, "message": code, "scope": "project"}
    if tool is not None:
        error.update(scope="tool", message=str(tool), tool_result=tool.tool_result)
    return JSONResponse({"error": error, "project": project}, status_code=status)


async def _invocation(request):
    body = bytearray()
    async for chunk in request.stream():
        if len(body) + len(chunk) > MAX_TOOL_REQUEST_BYTES:
            raise ValueError("invalid_tool_request")
        body.extend(chunk)
    data = Invocation.model_validate_json(body)
    if any(value is not None and not value.strip() for value in (
        data.session_id, data.public_base_url,
    )):
        raise ValueError("invalid_tool_request")
    return data


def _request_origin(request):
    origin = f"{request.url.scheme}://{request.headers['host']}"
    sent = request.headers.getlist("origin")
    if sent and sent != [origin]:
        return None
    if not sent and request.headers.get("sec-fetch-site") in {
        "cross-site", "same-site",
    }:
        return None
    return origin


def _project_receipt(prefix, instance):
    if isinstance(prefix, str) and prefix and valid_project_instance(instance):
        return {"prefix": prefix, "instance_id": instance}
    return None


def _valid_fault(error):
    if not isinstance(error, dict):
        return False
    codes = {"code", "message", "scope"}
    if not all(isinstance(error.get(key), str) for key in codes):
        return False
    if error["scope"] == "project":
        return set(error) == codes
    return (
        error["scope"] == "tool"
        and set(error) == codes | {"tool_result"}
        and (error["tool_result"] is None or isinstance(error["tool_result"], dict))
    )


def _valid_receipt(project, expected):
    return (
        isinstance(project, dict)
        and set(project) == {"prefix", "instance_id"}
        and _project_receipt(project["prefix"], project["instance_id"])
        and (expected is None or project["instance_id"] == expected)
    )


def _shared_result(status, envelope, expected):
    project = envelope.get("project")
    if project is not None and not _valid_receipt(project, expected):
        return _receipt_mismatch()
    if "result" in envelope and 200 <= status < 300:
        if project is None:
            return _receipt_mismatch()
        if set(envelope) == {"result", "project"} and valid_tool_response(envelope["result"]):
            return JSONResponse(envelope, status_code=status)
    if set(envelope) == {"error", "project"} and _valid_fault(envelope["error"]):
        return JSONResponse(envelope, status_code=status)
    return fault("shared_gateway_failure", status=503)


def _receipt_mismatch():
    code = "project_receipt_mismatch"
    message = "The API receipt does not identify the selected Project."
    tool = ToolProtocolError(code, message, {
        "outcome": "failed", "diagnostics": [f"{code}: {message}"],
    })
    return fault(code, status=502, tool=tool)


async def _direct_result(gateway, data, expected):
    selection = getattr(gateway, "selection", None)
    project = _project_receipt(
        getattr(selection, "project_prefix", None),
        getattr(selection, "instance_id", None),
    )
    if project is None:
        return fault("shared_gateway_failure", status=503)
    if expected is not None and expected != project["instance_id"]:
        return fault("project_declarations_stale")
    arguments = data.arguments or {}
    root = arguments.get("project_root")
    try:
        arguments = native_arguments(arguments, selection, gateway.root)
    except ValueError:
        return fault("invalid_project_root")
    if not any(tool.name == data.name for tool in gateway.tools):
        return fault("tool_unavailable")
    try:
        with bind_request_context(RuntimeRequestContext(session_id=data.session_id)):
            value = await gateway.call_tool(
                data.name,
                arguments,
                public_base_url=data.public_base_url,
                asserted_project_root=root,
            )
    except ToolProtocolError as error:
        if error.tool_result is None:
            return fault("shared_gateway_failure", status=503, project=project)
        return fault(error.code, project=project, status=error.status_code, tool=error)
    return JSONResponse({"result": value, "project": project})


def routes(gateway, *, shared):
    async def catalog(_request):
        if not shared:
            tools = [
                public_tool(tool, required=False).model_dump(
                    mode="json", by_alias=True, exclude_none=True
                )
                for tool in gateway.tools
            ]
            return JSONResponse({"result": {"tools": tools}})
        try:
            status, envelope = await gateway.tool_rest("GET")
        except ToolProtocolError:
            return fault("shared_gateway_failure", status=503)
        result = envelope.get("result")
        if (isinstance(result, dict) and set(result) == {"tools"}
                and isinstance(result["tools"], list)):
            return JSONResponse(envelope, status_code=status)
        if set(envelope) == {"error", "project"} and _valid_fault(envelope["error"]):
            return JSONResponse(envelope, status_code=status)
        return fault("shared_gateway_failure", status=503)

    async def invoke(request):
        origin = _request_origin(request)
        if origin is None:
            return fault("origin_rejected", status=403)
        headers = request.headers.getlist(INSTANCE_HEADER)
        if headers and (len(headers) != 1 or not valid_project_instance(headers[0])):
            return fault("project_declarations_stale")
        expected = headers[0] if headers else None
        try:
            data = await _invocation(request)
            data.public_base_url = origin + "/"
            content = json.dumps(
                data.model_dump(), ensure_ascii=False, allow_nan=False,
                separators=(",", ":"),
            ).encode()
        except (ValueError, RecursionError):
            return fault("invalid_tool_request")
        if not shared:
            return await _direct_result(gateway, data, expected)
        forwarded = {"Content-Type": "application/json"}
        if expected is not None:
            forwarded[INSTANCE_HEADER] = expected
        try:
            status, envelope = await gateway.tool_rest(
                "POST", content=content, headers=forwarded
            )
        except ToolProtocolError:
            return fault("shared_gateway_failure", status=503)
        return _shared_result(status, envelope, expected)

    return [
        Route(TOOL_REST_PATH, catalog),
        Route(TOOL_REST_PATH, invoke, methods=["POST"]),
    ]
