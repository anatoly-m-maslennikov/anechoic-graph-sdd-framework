"""Serve the public Tool REST contract on the loopback transport."""

import json

from starlette.responses import JSONResponse
from starlette.routing import Route

from MCP_PATCHBAY_C21.FEATURE_MCP.transport_support._tool_rest_support import (
    MAX_TOOL_REQUEST_BYTES,
    Invocation as Invocation,
    _invocation,
    _observed_reply,
    _valid_fault,
    fault,
    json_body as json_body,
    request_origin,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.backend_client import ToolProtocolError
from MCP_PATCHBAY_C21.FEATURE_MCP.transport_support.paths.\
    paths__shared import (
    TOOL_REST_PATH,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.transport_support.\
    project_tool_context import (
    native_arguments,
    valid_project_instance,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.runtime_request_context import (
    RuntimeRequestContext,
    bind_request_context,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.transport_support.\
    shared_gateway_support import (
    parse_tool_catalog,
    project_receipt_mismatch,
    valid_project_receipt,
    valid_tool_response,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.transport_support.\
    shared_tool_contract import (
    public_tool,
)

INSTANCE_HEADER = "X-Anechoic-Project-Instance"


def _project_receipt(prefix, instance):
    if isinstance(prefix, str) and prefix and valid_project_instance(instance):
        return {"prefix": prefix, "instance_id": instance}
    return None


def _shared_result(gateway, data, status, envelope, expected):
    project = envelope.get("project")
    if project is not None and not valid_project_receipt(project, expected):
        return _receipt_mismatch()
    if "result" in envelope and 200 <= status < 300:
        if project is None:
            return _receipt_mismatch()
        if set(envelope) == {"result", "project"} and valid_tool_response(
            envelope["result"]
        ):
            return _observed_reply(gateway, data, status, envelope)
    if set(envelope) == {"error", "project"} and _valid_fault(
        envelope["error"]
    ):
        return _observed_reply(gateway, data, status, envelope)
    return fault("shared_gateway_failure", status=503)


def _receipt_mismatch():
    error = project_receipt_mismatch()
    return fault(error.code, status=error.status_code, tool=error)


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
    try:
        with bind_request_context(
            RuntimeRequestContext(session_id=data.session_id)
        ):
            value = await gateway.call_tool(
                data.name,
                arguments,
                public_base_url=data.public_base_url,
                asserted_project_root=root,
            )
    except ToolProtocolError as error:
        if error.tool_result is None:
            return fault("shared_gateway_failure", status=503, project=project)
        return fault(
            error.code, project=project, status=error.status_code, tool=error
        )
    return JSONResponse({"result": value, "project": project})


async def _catalog(gateway, shared):
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
    if 200 <= status < 300 and set(envelope) == {"result"}:
        try:
            parse_tool_catalog(envelope["result"])
        except ValueError:
            return fault("shared_gateway_failure", status=503)
        return JSONResponse(envelope, status_code=status)
    if set(envelope) == {"error", "project"} and _valid_fault(
        envelope["error"]
    ):
        return JSONResponse(envelope, status_code=status)
    return fault("shared_gateway_failure", status=503)


async def _invoke(request, gateway, shared):
    origin = request_origin(request)
    if origin is None:
        return fault("origin_rejected", status=403)
    headers = request.headers.getlist(INSTANCE_HEADER)
    if headers and (
        len(headers) != 1 or not valid_project_instance(headers[0])
    ):
        return fault("project_declarations_stale")
    expected = headers[0] if headers else None
    try:
        data = await _invocation(request)
        data.public_base_url = origin + "/"
        content = json.dumps(
            data.model_dump(),
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
        ).encode()
    except ValueError, RecursionError:
        return fault("invalid_tool_request")
    if not shared:
        return await _direct_result(gateway, data, expected)
    if len(content) > MAX_TOOL_REQUEST_BYTES:
        return fault("invalid_tool_request")
    forwarded = {"Content-Type": "application/json"}
    if expected is not None:
        forwarded[INSTANCE_HEADER] = expected
    try:
        status, envelope = await gateway.tool_rest(
            "POST", content=content, headers=forwarded
        )
    except ToolProtocolError:
        return fault("shared_gateway_failure", status=503)
    return _shared_result(gateway, data, status, envelope, expected)


def routes(gateway, *, shared):
    async def catalog(_request):
        return await _catalog(gateway, shared)

    async def invoke(request):
        return await _invoke(request, gateway, shared)

    return [
        Route(TOOL_REST_PATH, catalog),
        Route(TOOL_REST_PATH, invoke, methods=["POST"]),
    ]
