"""Validate Tool REST requests and construct public faults."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from starlette.responses import JSONResponse

from MCP_PATCHBAY_C21.FEATURE_MCP.transport_support.\
    shared_gateway_support import (
    record_observation,
)

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
        error.update(
            scope="tool", message=str(tool), tool_result=tool.tool_result
        )
    return JSONResponse(
        {"error": error, "project": project}, status_code=status
    )


async def json_body(request):
    content_types = request.headers.getlist("content-type")
    if (
        len(content_types) != 1
        or content_types[0].partition(";")[0].strip().lower()
        != "application/json"
    ):
        raise ValueError("application/json is required")
    body = bytearray()
    async for chunk in request.stream():
        if len(body) + len(chunk) > MAX_TOOL_REQUEST_BYTES:
            raise ValueError("invalid_tool_request")
        body.extend(chunk)
    return body


async def _invocation(request):
    data = Invocation.model_validate_json(await json_body(request))
    if any(
        value is not None and not value.strip()
        for value in (
            data.session_id,
            data.public_base_url,
        )
    ):
        raise ValueError("invalid_tool_request")
    return data


def request_origin(request):
    origin = f"{request.url.scheme}://{request.headers['host']}"
    sent = request.headers.getlist("origin")
    if sent and sent != [origin]:
        return None
    if not sent and request.headers.get("sec-fetch-site") in {
        "cross-site",
        "same-site",
    }:
        return None
    return origin


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
        and (
            error["tool_result"] is None
            or isinstance(error["tool_result"], dict)
        )
    )


def _observed_reply(gateway, data, status, envelope):
    project = envelope["project"] or {}
    if "result" in envelope:
        value = envelope["result"]["value"]
    else:
        error = envelope["error"]
        outcome = (
            {"outcome": "rejected"} if error["scope"] == "project" else {}
        )
        value = {**(error.get("tool_result") or outcome), "is_error": True}
    record_observation(
        gateway.health_observations,
        data.name,
        data.arguments,
        value,
        None,
        project_prefix=project.get("prefix"),
        project_instance_id=project.get("instance_id"),
    )
    return JSONResponse(envelope, status_code=status)


