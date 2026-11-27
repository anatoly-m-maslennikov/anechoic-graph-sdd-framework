"""Request models and public Tool responses for shared API."""

from copy import deepcopy
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator
from starlette.responses import JSONResponse


TOOL_REST_PATH = "/tools"


class SelectionRequest(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    project_root: str


class Invocation(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    name: str = Field(min_length=1)
    arguments: dict[str, Any] | None
    session_id: str | None
    public_base_url: str | None

    @model_validator(mode="after")
    def nonblank_context(self):
        if any(
            value is not None and not value.strip()
            for value in (self.session_id, self.public_base_url)
        ):
            raise ValueError("invalid_tool_request")
        return self


def fault(
    code,
    *,
    scope="project",
    project=None,
    message=None,
    tool_result=None,
    status=200,
):
    error = {"code": code, "message": message or code, "scope": scope}
    if scope == "tool":
        error["tool_result"] = tool_result
    return JSONResponse(
        {"error": error, "project": project}, status_code=status
    )


def public_tool(native):
    tool = deepcopy(native)
    schema = tool["inputSchema"]
    schema["properties"]["project_root"] = {"type": "string", "minLength": 1}
    schema["properties"]["caller_context"] = {
        "type": "object",
        "properties": {
            "session_id": {"type": "string", "minLength": 1, "pattern": "\\S"}
        },
        "required": ["session_id"],
        "additionalProperties": False,
    }
    schema.setdefault("required", []).append("project_root")
    return tool


def owner_fault(error, *, project=None):
    allowed = {
        "invalid_project_root",
        "missing_project_root",
        "outside_project_root",
        "host_configuration_stale",
        "host_configuration_invalid",
        "tool_unavailable",
        "project_gateway_busy",
        "project_declarations_stale",
    }
    code = (
        str(error)
        if isinstance(error, ValueError) and str(error) in allowed
        else "shared_gateway_failure"
    )
    return fault(
        code,
        project=project,
        status=503 if code == "shared_gateway_failure" else 200,
    )


def tool_unavailable(name, selected, tools):
    return name not in tools or any(
        alias in selected.tool_blacklist
        for alias in (
            name,
            name.replace("iwe_console_", "workbench_", 1),
            name.replace("workbench_", "iwe_console_", 1),
        )
    )
