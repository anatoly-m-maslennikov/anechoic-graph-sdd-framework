"""Control and inspect the selected Project's projection peers."""

import re
from datetime import UTC, datetime
from typing import Annotated, Literal

import httpx2
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    field_validator,
)

from ..CORE.CORE__shared import Readiness, failure, peer
from ..CORE.CORE__shared import WorkerRuns
from ..CORE.CORE__shared import ALIASES, FLOWS, TABLES


MODEL_TARGETS = ("model_tree", "model_primary_entities")


class StrictModel(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")


class StatusArguments(StrictModel):
    include_health: bool = False


class AbortArguments(StrictModel):
    run_id: str = Field(min_length=1)


class RebuildArguments(StrictModel):
    target: str


class PeerError(BaseModel):
    model_config = ConfigDict(strict=True, extra="allow")
    code: str
    message: str


class AbortResult(BaseModel):
    model_config = ConfigDict(strict=True, extra="allow")
    run_id: str
    state: Literal["aborting"]


class RebuildResult(BaseModel):
    model_config = ConfigDict(strict=True, extra="allow")
    result_ids: dict[str, str]


class _IssueRow(BaseModel):
    model_config = ConfigDict(strict=True, extra="allow")

    source: Literal["atom", "archive", "realization", "build"] | None = None
    relative_path: str | None = None
    code: str = Field(min_length=1)
    message: Annotated[str, Field(min_length=1)] | None = None
    atom_ref: str | None = None
    related_paths: list[str] | None = None

    @field_validator("source", "message", "related_paths")
    @classmethod
    def supplied_value(cls, value):
        if value is None:
            raise ValueError("Issue field cannot be null when present")
        return value


class IssueRows(BaseModel):
    model_config = ConfigDict(strict=True, extra="allow")
    rows: list[_IssueRow] = Field(max_length=1000)


def _definitions():
    return {
        "iwe_console_status": (
            "Read Project source indexing status and current "
            "ingestion issues.",
            {"include_health": {"type": "boolean"}},
            True,
        ),
        "iwe_console_abort": (
            "Abort the active Project Worker run.",
            {"run_id": {"type": "string", "minLength": 1}},
            False,
        ),
        "workbench_status": (
            "Read Project source indexing status and current "
            "ingestion issues.",
            {"include_health": {"type": "boolean"}},
            True,
        ),
        "workbench_abort": (
            "Abort the active Project Worker run.",
            {"run_id": {"type": "string", "minLength": 1}},
            False,
        ),
        "query_rebuild": (
            "Rebuild a Project projection or refresh retained query results.",
            {"target": {"type": "string", "minLength": 1}},
            False,
        ),
    }


def descriptors():
    definitions = _definitions()
    result = {}
    for name, (description, properties, read_only) in definitions.items():
        schema = {
            "type": "object",
            "properties": properties,
            "additionalProperties": False,
        }
        if properties:
            schema["required"] = list(properties)
        result[name] = {
            "name": name,
            "description": description,
            "inputSchema": schema,
            "annotations": {
                "readOnlyHint": read_only,
                "destructiveHint": False,
                "idempotentHint": read_only,
                "openWorldHint": False,
            },
        }
    return result


def target_scope(arguments):
    try:
        target = RebuildArguments.model_validate(arguments).target
    except ValidationError as error:
        raise ValueError(
            "Expected a target table or result selector"
        ) from error
    scope = target.removeprefix("main.")
    scope = ALIASES.get(scope, scope)
    if scope in (
        "all",
        "realization_graph",
        "workbench_results",
        *TABLES,
        *MODEL_TARGETS,
        *FLOWS,
    ):
        return scope, target
    match = re.fullmatch(
        r"(?:workbench_results\.)?(?:query_)?([0-9a-f]{32})", scope
    )
    if match is None:
        raise ValueError("Unknown Workbench rebuild target")
    return match[1], target


def response(value):
    return {"result": {"value": value, "text": None}}


def peer_error(value):
    error = PeerError.model_validate(value)
    return failure(error.code, error.message)


def _status_value(runs, raw):
    latest, active = runs.latest, runs.active
    finished = (
        latest.finished_at if latest and latest.state == "succeeded" else None
    )
    value = {
        "mode": "live_index",
        "syncing": active is not None,
        "last_synced_at": datetime.fromtimestamp(finished, UTC).isoformat()
        if finished is not None
        else None,
        "run_id": active.run_id if active else None,
        "worker_alive": active.worker_alive if active else None,
    }
    if "archive" in raw:
        value["archive"] = raw["archive"]
    return value


async def _add_ingestion_issues(database, instance, value):
    try:
        result = (
            await peer(
                database,
                "GET",
                "/ingestion/issues",
                params={"instance_id": instance},
            )
        )["result"]
        admitted = IssueRows.model_validate(result).model_dump(
            exclude_unset=True, include={"rows"}
        )
        value["ingestion_issues"] = [
            {key: row[key] for key in received}
            for received, row in zip(
                result["rows"], admitted["rows"], strict=True
            )
        ]
    except httpx2.HTTPError, ValueError, TypeError, KeyError, AttributeError:
        pass


async def status(database, orchestrator, instance, arguments, binding=None):
    try:
        request = StatusArguments.model_validate(arguments)
    except ValidationError:
        return failure(
            "tool_input_invalid", "The status request has no arguments"
        )
    if orchestrator is None:
        value = {
            "mode": "unavailable",
            "syncing": False,
            "last_synced_at": None,
        }
        if request.include_health:
            value["health"] = {"state": "unavailable"}
        return response(value)
    raw = (
        await peer(
            orchestrator,
            "GET",
            "/jobs/worker-runs",
            params={"instance_id": instance},
        )
    )["result"]
    runs = WorkerRuns.model_validate(raw)
    latest = runs.latest
    value = _status_value(runs, raw)
    if request.include_health:
        digest = binding.get("manifest_sha256") if binding else None
        value["health"] = (
            await Readiness(instance, digest, database, orchestrator).status()
            if digest
            else {"state": "unavailable"}
        )
        value["watcher_queue_depth"] = raw.get("watcher_queue_depth")
        value["last_run_state"] = latest.state if latest else None
    await _add_ingestion_issues(database, instance, value)
    return response(value)


async def abort(orchestrator, instance, arguments):
    try:
        run_id = AbortArguments.model_validate(arguments).run_id
    except ValidationError:
        return failure(
            "tool_input_invalid", "Expected an active Worker run_id"
        )
    if orchestrator is None:
        return failure("run_not_abortable", "Project has no active Worker")
    reply = await peer(
        orchestrator,
        "POST",
        "/jobs/abort",
        json={"instance_id": instance, "run_id": run_id},
    )
    if "error" in reply:
        return peer_error(reply["error"])
    result = AbortResult.model_validate(reply["result"])
    if result.run_id != run_id:
        raise ValueError("Invalid Worker run binding")
    return response(reply["result"])


async def rebuild(database, orchestrator, binding, instance, arguments):
    try:
        scope, target = target_scope(arguments)
    except ValueError as error:
        return failure("tool_input_invalid", str(error))
    if scope in ("all", "realization_graph", *TABLES, *MODEL_TARGETS):
        if binding is None:
            return failure(
                "workbench_unavailable",
                "Managed Orchestrator binding is unavailable",
            )
        reply = await peer(
            orchestrator,
            "POST",
            "/jobs/build",
            timeout=httpx2.Timeout(None, connect=10),
            json={**binding, "instance_id": instance, "refresh_target": scope},
        )
    else:
        reply = await peer(
            database,
            "POST",
            "/results/rebuild",
            json={"instance_id": instance, "target": scope},
        )
    if "error" in reply:
        return peer_error(reply["error"])
    result = RebuildResult.model_validate(reply["result"])
    return response(
        {"status": "ready", "target": target, "result_ids": result.result_ids}
    )


async def invoke(name, arguments, database, orchestrator, binding, instance):
    try:
        if name in {"iwe_console_status", "workbench_status"}:
            return await status(
                database, orchestrator, instance, arguments, binding
            )
        if name in {"iwe_console_abort", "workbench_abort"}:
            return await abort(orchestrator, instance, arguments)
        return await rebuild(
            database, orchestrator, binding, instance, arguments
        )
    except (
        httpx2.HTTPError,
        ValueError,
        TypeError,
        KeyError,
        AttributeError,
        OverflowError,
    ):
        return failure(
            "workbench_unavailable", "Projection service unavailable"
        )
