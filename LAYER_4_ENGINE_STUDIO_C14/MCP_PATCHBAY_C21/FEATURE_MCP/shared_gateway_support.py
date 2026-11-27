"""Map wire results and fixed transport failures to MCP responses."""

from __future__ import annotations

import asyncio
import json
from concurrent.futures import CancelledError as FutureCancelledError
from contextlib import nullcontext
from typing import Any

from mcp import types
from mcp.server.lowlevel import Server

from MCP_PATCHBAY_C21.FEATURE_MCP.backend_client import ToolProtocolError
from MCP_PATCHBAY_C21.FEATURE_MCP.caller_context import take_caller_context
from MCP_PATCHBAY_C21.FEATURE_MCP.mcp_startup_boundary import warning
from MCP_PATCHBAY_C21.FEATURE_MCP.project_tool_context import (
    valid_project_instance,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.runtime_request_context import (
    bind_request_context,
)


def make_server(catalog, call):
    async def list_tools(_context, _params):
        return types.ListToolsResult(tools=catalog())

    return Server(
        "ANECHOIC",
        version="0.2.0",
        on_list_tools=list_tools,
        on_call_tool=call,
    )


def valid_tool_response(response):
    return (
        isinstance(response, dict)
        and set(response) == {"value", "text"}
        and isinstance(response["value"], dict)
        and (response["text"] is None or isinstance(response["text"], str))
    )


def parse_tool_catalog(result):
    if (
        not isinstance(result, dict)
        or set(result) != {"tools"}
        or not isinstance(result["tools"], list)
    ):
        raise ValueError("Invalid Shared Backend catalog")
    return [types.Tool.model_validate(tool) for tool in result["tools"]]


def valid_project_receipt(project, expected):
    return (
        isinstance(project, dict)
        and set(project) == {"prefix", "instance_id"}
        and isinstance(project["prefix"], str)
        and bool(project["prefix"])
        and valid_project_instance(project["instance_id"])
        and (expected is None or project["instance_id"] == expected)
    )


def project_receipt_mismatch():
    code = "project_receipt_mismatch"
    message = "The API receipt does not identify the selected Project."
    return ToolProtocolError(
        code,
        message,
        {"outcome": "failed", "diagnostics": [f"{code}: {message}"]},
        status_code=502,
    )


async def call_mcp(call_tool, context, name, arguments, **routing):
    arguments, caller = take_caller_context(arguments)
    with bind_request_context(caller) if caller else nullcontext():
        base = getattr(getattr(context, "request", None), "base_url", None)
        response = await call_tool(
            name,
            arguments,
            public_base_url=str(base) if base is not None else None,
            **routing,
        )
    return result(response["value"], text=response["text"])


def result(value, error=False, *, text=None):
    return types.CallToolResult(
        content=[
            types.TextContent(
                type="text", text=json.dumps(value) if text is None else text
            )
        ],
        structured_content=value,
        is_error=error,
    )


def refusal(code: str) -> types.CallToolResult:
    diagnostics = [code]
    if warning(code) is not None:
        diagnostics.append("technical_diagnostics_unavailable")
    return result({"outcome": "rejected", "diagnostics": diagnostics}, True)


def unexpected_failure(code="internal_failure", message="operation failure"):
    diagnostics = [f"{code}: {message}"]
    if warning(code) is not None:
        diagnostics.append("technical diagnostic unavailable")
    return result({"outcome": "failed", "diagnostics": diagnostics}, True)


def tool_failure(error):
    if error.tool_result is None:
        return unexpected_failure(
            "tool_runtime_failure", "Backend unavailable"
        )
    return result(error.tool_result, True)


def record_observation(
    observer: Any,
    name: Any,
    arguments: Any,
    response: Any,
    error: BaseException | None,
    *,
    project_prefix: str | None = None,
    project_instance_id: str | None = None,
) -> None:
    """Keep a successful native result when bounded health recording fails."""
    try:
        observer.record(
            name,
            arguments,
            response,
            error=error,
            project_prefix=project_prefix,
            project_instance_id=project_instance_id,
        )
    except asyncio.CancelledError, FutureCancelledError:
        raise
    except Exception:
        warning("health_observation_failed")
