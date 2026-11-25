"""Project Workspace and query-log operations through the Kernel."""

from typing import Any, Literal
from urllib.parse import quote, urlencode

import httpx2
from pydantic import BaseModel, ConfigDict, Field, RootModel, ValidationError, model_validator

from . import saved_sql, view_tools
from .admission import failure, peer
from .models import Page
from .projection import PeerError


class StrictModel(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")


class Empty(StrictModel):
    pass


class Open(StrictModel):
    session_id: str

    @model_validator(mode="after")
    def valid_id(self):
        validate_id(self.session_id)
        return self


class Get(StrictModel):
    workspace_id: str

    @model_validator(mode="after")
    def valid_id(self):
        validate_id(self.workspace_id)
        return self


class LogGet(StrictModel):
    log_id: str

    @model_validator(mode="after")
    def valid_id(self):
        validate_id(self.log_id)
        return self


class LogList(StrictModel):
    limit: int = Field(default=20, ge=1, le=1000)


class LogRecord(StrictModel):
    log_id: str
    at: str
    sql: str
    outcome: Literal["success", "failed"]
    error: str | None
    row_count: int | None
    column_count: int | None


class LogRecords(StrictModel):
    items: list[LogRecord]


class WorkspaceDocument(BaseModel):
    model_config = ConfigDict(strict=True, extra="allow")
    workspace_id: str = Field(min_length=1)


class WorkspaceResult(RootModel[dict[str, Any]]):
    model_config = ConfigDict(strict=True)


def validate_id(value):
    if not value.strip():
        raise ValueError("Expected a non-empty ID")
    value.encode("utf-8")


def descriptors():
    identity = {"type": "string", "minLength": 1}
    definitions = {
        "workspace_open": ("Initialize or resume the Workspace bound to one browser or native session.", {"session_id": identity}, True, False),
        "workspace_list": ("List known Workspace IDs for the selected Project.", {}, False, True),
        "workspace_get": ("Get Workspace Views, active View, and result metadata without result rows.", {"workspace_id": identity}, True, True),
        "query_log_list": ("List retained query-log records without result rows.", {"limit": {"type": "integer", "minimum": 1, "maximum": 1000}}, False, True),
        "query_log_get": ("Get one retained query-log record without result rows.", {"log_id": identity}, True, True),
    }
    result = {}
    for name, (description, properties, required, read_only) in definitions.items():
        schema = {"type": "object", "properties": properties, "additionalProperties": False}
        if required:
            schema["required"] = list(properties)
        result[name] = {"name": name, "description": description, "inputSchema": schema,
                        "annotations": {"readOnlyHint": read_only, "destructiveHint": False,
                                        "idempotentHint": read_only, "openWorldHint": False}}
    return result


def arguments(name, args, session):
    if name in view_tools.MODELS:
        return view_tools.arguments(name, args)
    if name == "workspace_open" and "session_id" not in args and session is not None:
        args = {**args, "session_id": session}
    model = {"workspace_open": Open, "workspace_get": Get, "workspace_list": Empty,
             "query_log_list": LogList, "query_log_get": LogGet}[name]
    return model.model_validate(args).model_dump(exclude_unset=True)


def present(name, value, context, args):
    WorkspaceResult.model_validate(value)
    if name == "query_log_list":
        LogRecords.model_validate(value)
    elif name == "query_log_get":
        LogRecord.model_validate(value)
    elif name == "view_fetch":
        Page.model_validate(value)
    elif name == "view_run" and args.get("save", False) and value.get("status") == "success":
        value = saved_sql.present_run(value, args, context)
    elif name in {"workspace_open", "workspace_get"}:
        document = WorkspaceDocument.model_validate(value)
        value = {**value, "project_name": context.project_name}
        if context.base is not None:
            query = {"workspace": document.workspace_id}
            if context.root is not None:
                query["project_root"] = context.root
            path = f"/anechoic/workbench/{quote(context.project_name, safe='')}"
            value["workspace_url"] = f"{context.base.rstrip('/')}{path}?{urlencode(query)}"
    return value


async def invoke(name, args, database, instance, session, context):
    try:
        fields = arguments(name, args, session)
        if name in {"workspace_open", "workspace_get"} and not context.project_name:
            raise ValueError("Workbench Project name is unavailable")
    except (ValidationError, ValueError, TypeError, UnicodeError) as error:
        return failure("tool_input_invalid", str(error))
    try:
        result = await peer(database, "POST", "/workspace", json={"instance_id": instance, "operation": name, "arguments": fields})
        if "error" in result:
            error = PeerError.model_validate(result["error"])
            return failure(error.code, error.message)
        return {"result": {"value": present(name, result["result"], context, args), "text": None}}
    except (httpx2.HTTPError, ValueError, TypeError, KeyError, UnicodeError):
        return failure("workbench_unavailable", "Workspace service unavailable")
