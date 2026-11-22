"""Map public projection operations to Kernel and Orchestrator requests."""

from datetime import datetime, UTC
import re

import httpx2

from .peer_transport import tool_failure, upstream
from .workspace_tools import _tool


TABLES = ("atoms", "native_references", "relations", "import_nodes", "module_imports", "import_edges",
          "package_imports", "test_edges", "tested_by_edges", "import_read_issues", "package_external_imports")
TOOLS = {
    "workbench_status": _tool("workbench_status", "Read Project source indexing status.", {}, read_only=True),
    "query_rebuild": _tool("query_rebuild", "Rebuild a Project projection or refresh retained query results.",
                           {"target": {"type": "string", "minLength": 1}}),
}


async def _status(socket, instance_id, args):
    if args:
        return tool_failure("tool_input_invalid", "The status request has no arguments")
    result = await upstream(socket, "GET", "/jobs/worker-runs", params={"instance_id": instance_id})
    runs = result["result"]
    latest = runs.get("latest") or {}
    finished = latest.get("finished_at") if latest.get("state") == "succeeded" else None
    synced = datetime.fromtimestamp(finished, UTC).isoformat() if finished is not None else None
    return {"result": {"value": {"mode": "live_index", "syncing": runs.get("active") is not None,
                                 "last_synced_at": synced}, "text": None}}


def _target(args):
    target = args.get("target")
    if set(args) != {"target"} or not isinstance(target, str):
        raise ValueError("Expected a target table or result selector")
    scope = target.removeprefix("main.")
    if scope in ("all", "workbench_results", *TABLES):
        return scope, target
    match = re.fullmatch(r"(?:workbench_results\.)?(?:query_)?([0-9a-f]{32})", scope)
    if match is None:
        raise ValueError("Unknown Workbench rebuild target")
    return match[1], target


async def _rebuild(database, orchestrator, binding, instance_id, args):
    try:
        scope, target = _target(args)
    except ValueError as error:
        return tool_failure("tool_input_invalid", str(error))
    if scope in ("all", *TABLES):
        if binding is None:
            return tool_failure("workbench_unavailable", "Managed Orchestrator binding is unavailable")
        refreshed = await upstream(orchestrator, "POST", "/jobs/build", timeout=320,
                                   json={**binding, "instance_id": instance_id, "refresh_target": scope})
    else:
        refreshed = await upstream(database, "POST", "/results/rebuild",
                                   json={"instance_id": instance_id, "target": scope})
    if "error" in refreshed:
        return tool_failure(refreshed["error"]["code"], refreshed["error"]["message"])
    value = {"status": "ready", "target": target, "result_ids": refreshed["result"]["result_ids"]}
    return {"result": {"value": value, "text": None}}


async def invoke(name, args, database, orchestrator, binding, instance_id):
    try:
        if name == "workbench_status":
            return await _status(orchestrator, instance_id, args)
        return await _rebuild(database, orchestrator, binding, instance_id, args)
    except (httpx2.HTTPError, ValueError, TypeError, KeyError, AttributeError, OverflowError):
        return tool_failure("workbench_unavailable", "Projection service unavailable")
