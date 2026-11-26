"""Expose the admitted read-only Kernel query slice."""

import json
import os

import httpx2
from pydantic import ValidationError
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from .admission import Readiness, failure, peer
from .models import Page, PageRequest, Query, Sql, SqlResult, ToolRequest, WorkerRuns
from . import lifecycle, projection, saved_sql, view_tools, workspace
from .query_contract import query_schema
from .schema import read_schema

PROJECTION_TOOLS = frozenset({"workbench_status", "workbench_abort", "query_rebuild"})
SAVED_TOOLS = frozenset({"query_load", "query_saved_list", "view_save"})
WORKSPACE_TOOLS = frozenset({"workspace_open", "workspace_list", "workspace_get", "query_log_list", "query_log_get"})
WORKSPACE_TOOLS |= frozenset(view_tools.MODELS)
LIFECYCLE_TOOLS = frozenset(lifecycle.descriptors())


def descriptor():
    return {"name": "query_run", "description": "Run one read-only SQL query and optionally save a Bookmark in the selected Project.",
            "annotations": {"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False,
                            "openWorldHint": False},
            "inputSchema": query_schema()}


def descriptors():
    annotations = {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False}
    number = {"type": "integer", "minimum": 0}
    page_size = {"type": "integer", "minimum": 1, "maximum": 1000}
    order = {"type": "object", "properties": {"column": number, "direction": {"type": "string", "enum": ["asc", "desc"]}},
             "required": ["column", "direction"], "additionalProperties": False}
    filt = {"type": "object", "properties": {"column": number, "operator": {"const": "contains"},
                                               "value": {"type": "string"}},
            "required": ["column", "operator", "value"], "additionalProperties": False}
    grid = {"type": "object", "properties": {"sort": {"type": "array", "items": order},
            "filters": {"type": "array", "items": filt}, "group_by": order}, "additionalProperties": False}
    delivery = {"type": "string", "enum": ["file", "inline", "auto"], "default": "file"}
    fmt = {"type": "string", "enum": ["json_matrix", "csv", "toon"]}
    definitions = {
        "query_check": ("Check read-only SQL without retaining the result.",
                        {"sql": {"type": "string"}, "cursor_position": number}, ["sql"]),
        "query_page": ("Read a page of a retained Project query result.",
                       {"query_id": {"type": "string"}, "offset": number, "page_size": page_size,
                        "preview": number, "result_delivery": delivery, "result_format": fmt, "grid": grid}, ["query_id"]),
        "query_schema": ("Read the selected Project's public SQL schema.", {}, []),
    }
    result = {"query_run": descriptor()}
    for name, (description, properties, required) in definitions.items():
        result[name] = {"name": name, "description": description, "annotations": annotations,
                        "inputSchema": {"type": "object", "properties": properties, "required": required,
                                        "additionalProperties": False}}
    result.update(projection.descriptors())
    result.update(saved_sql.descriptors())
    result.update(workspace.descriptors())
    result.update(view_tools.descriptors())
    result.update(lifecycle.descriptors())
    return result


async def body(request):
    data = bytearray()
    async for chunk in request.stream():
        if len(data) + len(chunk) > 65536:
            raise ValueError("Request is too large")
        data.extend(chunk)
    return data


def refusal(status):
    if "error" in status:
        return JSONResponse({"error": status["error"]}, status_code=503 if status["state"] == "unavailable" else 200)
    code = "project_build_pending" if status["state"] == "pending" else "project_build_unavailable"
    message = "The Project projection is still starting" if code == "project_build_pending" else "The Project projection is unavailable"
    return JSONResponse(failure(code, message), status_code=503 if status["state"] == "unavailable" else 200)


def worker_runs_route(jobs, instance):
    async def worker_runs(request):
        if list(request.query_params.multi_items()) != [("instance_id", instance)]:
            return JSONResponse(failure("value_error", "Invalid Worker Run request binding"))
        try:
            result = await peer(jobs, "GET", "/jobs/worker-runs", params={"instance_id": instance})
            WorkerRuns.model_validate(result["result"])
            return JSONResponse(result)
        except (httpx2.HTTPError, ValueError, TypeError, KeyError):
            return JSONResponse(failure("workbench_unavailable", "Orchestrator unavailable"), status_code=503)
    return worker_runs


async def run_query(database, instance, name, arguments, *, context=None):
    try:
        if any(value is None for value in arguments.values()):
            raise ValueError("Null query arguments are not supported")
        model = {"query_run": Query, "query_page": PageRequest, "query_check": Sql}[name]
        query = model.model_validate(arguments)
        fields = {"sql": query.sql} if name == "query_check" else query.kernel_fields()
    except (ValidationError, ValueError, UnicodeError) as error:
        return failure("tool_input_invalid", str(error))
    try:
        response = await peer(database, "POST", "/database", json={"instance_id": instance, **fields})
        if "error" in response:
            error = response["error"]
            if isinstance(error, dict) and error.get("code") == "project_graph_pending":
                return failure("project_graph_pending", error["message"])
            return failure("query_error", str(error.get("message", "Query failed")) if isinstance(error, dict) else "Query failed")
        value = response["result"]
        if name == "query_check":
            result = SqlResult.model_validate(value)
            value = {"valid": True, "columns": value["columns"], "sql": query.sql,
                     "row_count": len(result.rows), "column_count": len(result.columns)}
        else:
            Page.model_validate(value)
            if name == "query_run" and query.save:
                try:
                    value = saved_sql.present_run(value, arguments, context or saved_sql.LinkContext())
                except ValueError:
                    return failure("workbench_unavailable", "Invalid saved query response")
        return {"result": {"value": value, "text": None}}
    except (ValidationError, ValueError, TypeError, KeyError):
        return failure("workbench_unavailable", "Invalid Kernel response")
    except httpx2.HTTPError:
        return failure("workbench_unavailable", "Kernel unavailable")


def create_app(instance, digest, project_root, database, jobs, *, host_root=None, blacklist=(), worker_binding=None,
               project_name=None, workbench_public_url=None):
    readiness = Readiness(instance, digest, database, jobs)
    tools = descriptors()
    async def health(_request):
        status = await readiness.status()
        result = {"instance_id": instance, "manifest_sha256": digest, "pid": os.getpid(),
                  "state": "unavailable", "kernel_pid": None, **status}
        return JSONResponse(result, status_code=503 if status["state"] == "unavailable" else 200)
    async def catalog(request):
        if list(request.query_params.multi_items()) != [("instance_id", instance)]:
            return JSONResponse(failure("value_error", "Invalid Tool request binding"))
        visible = [tool for name, tool in tools.items() if name not in blacklist]
        return JSONResponse({"result": {"tools": visible, "blacklist": list(blacklist)}})
    async def invoke(request):
        try:
            data = ToolRequest.model_validate(json.loads(await body(request)))
            if data.instance_id != instance:
                raise ValueError("Invalid Tool request envelope")
            if data.asserted_project_root not in (None, project_root, host_root):
                raise ValueError("project_root does not match the bound Project")
        except (ValueError, TypeError, ValidationError) as error:
            return JSONResponse(failure("value_error", str(error)))
        if data.name not in tools or data.name in blacklist:
            return JSONResponse(failure("tool_unavailable", "Unknown Tool"))
        if problem := readiness.guard():
            return refusal({"state": "unavailable" if problem["error"]["code"] == "admission_gate_unavailable" else "pending", **problem})
        if data.name not in PROJECTION_TOOLS and not readiness.admitted:
            status = await readiness.status()
            if status["state"] != "ready":
                return refusal(status)
        if data.name in PROJECTION_TOOLS:
            result = await projection.invoke(data.name, data.arguments, database, jobs, worker_binding, instance)
        elif data.name in LIFECYCLE_TOOLS:
            result = await lifecycle.invoke(data.name, data.arguments, jobs, worker_binding, instance)
        elif data.name == "query_schema":
            result = await read_schema(database, instance, data.arguments)
        else:
            context = saved_sql.LinkContext(project_name=project_name, base=data.public_base_url,
                                            root=data.asserted_project_root, configured_url=workbench_public_url)
            result = await execute_core(database, instance, data.name, data.arguments, context, data.session_id)
        code = result.get("error", {}).get("code")
        return JSONResponse(result, status_code=503 if code == "workbench_unavailable" else 200)
    return Starlette(routes=[Route("/health", health), Route("/tools", catalog), Route("/tools", invoke, methods=["POST"]),
                             Route("/jobs/worker-runs", worker_runs_route(jobs, instance))])


async def execute_core(database, instance, name, args, context, session):
    if name in SAVED_TOOLS:
        return await saved_sql.invoke(name, args, database, instance, context)
    if name in WORKSPACE_TOOLS:
        return await workspace.invoke(name, args, database, instance, session, context)
    return await run_query(database, instance, name, args, context=context)
