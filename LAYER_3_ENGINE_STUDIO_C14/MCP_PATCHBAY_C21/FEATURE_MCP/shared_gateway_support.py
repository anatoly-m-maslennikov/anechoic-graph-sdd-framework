"""Map wire results and fixed transport failures to MCP responses."""

from __future__ import annotations

import asyncio
import json
from concurrent.futures import CancelledError as FutureCancelledError
from typing import Any

from mcp import types

from MCP_PATCHBAY_C21.FEATURE_MCP.mcp_startup_boundary import warning


def result(value, error=False, *, text=None):
    return types.CallToolResult(
        content=[types.TextContent(type="text", text=json.dumps(value) if text is None else text)],
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
        return unexpected_failure("tool_runtime_failure", "Backend unavailable")
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
