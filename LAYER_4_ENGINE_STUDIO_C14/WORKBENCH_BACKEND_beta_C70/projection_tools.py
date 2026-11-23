"""Map public projection operations to Kernel and Orchestrator requests."""

from datetime import datetime, UTC
import re

import httpx2

from .peer_transport import tool_failure, upstream
from .workspace_tools import _tool


TABLES = ("atoms", "native_references", "relations", "import_nodes", "module_imports", "import_edges",
          "package_imports", "test_edges", "tested_by_edges", "import_read_issues", "package_external_imports",
          "state_effect_findings", "code_access_findings", "code_units", "code_unit_calls",
          "import_cycles", "package_coupling", "antipattern_findings",
          "architecture_code_metrics", "architecture_spec_metrics", "architecture_ratios",
          "package_review_profiles", "package_largest_files", "architecture_package_bindings")
FLOW_HISTORY = ("component_flows", "flow_events", "flow_overlap_candidates", "flow_similar_actions")
BIZ_TABLES = ("package_coupling", "architecture_code_metrics", "architecture_spec_metrics",
              "architecture_ratios", "package_review_profiles", "package_largest_files")
TABLE_ALIASES = {f"{'biz' if name in BIZ_TABLES else 'mrt'}_{name}": name for name in TABLES}
TABLE_ALIASES.update({f"{'src' if name == 'flow_events' else 'mrt'}_{name}": name for name in FLOW_HISTORY})
TABLE_ALIASES.update({f"ops_{name}": name for name in ("work_journal", "query_log")})
TABLE_ALIASES.update({f"mrt_real_graph_{name}": name for name in (
    "import_edges", "package_imports", "package_external_imports", "code_units", "code_unit_calls",
    "test_edges", "tested_by_edges")})
TABLE_ALIASES.update({
    "mrt_atom_graph_relations": "relations",
    "mrt_atom_references": "native_references",
    "mrt_flow_actions": "component_flows",
    "mrt_real_graph_import_nodes": "import_nodes",
    "mrt_real_graph_import_occurrences": "module_imports",
    "mrt_real_graph_package_spec_bindings": "architecture_package_bindings",
    "mrt_diag_import_read_issues": "import_read_issues",
    "mrt_diag_import_cycles": "import_cycles",
    "mrt_diag_antipatterns": "antipattern_findings",
    "mrt_diag_code_access": "code_access_findings",
    "mrt_diag_state_effects": "state_effect_findings",
    **{f"mrt_{family}_atoms": "atoms" for family in ("spec", "ticket", "project_config")},
})
TOOLS = {
    "workbench_status": _tool("workbench_status", "Read Project source indexing status and current ingestion issues.",
                             {}, read_only=True),
    "workbench_abort": _tool("workbench_abort", "Abort the active Project Worker run.",
                             {"run_id": {"type": "string", "minLength": 1}}),
    "query_rebuild": _tool("query_rebuild", "Rebuild a Project projection or refresh retained query results.",
                           {"target": {"type": "string", "minLength": 1}}),
}


async def _status(socket, database, instance_id, args):
    if args:
        return tool_failure("tool_input_invalid", "The status request has no arguments")
    result = await upstream(socket, "GET", "/jobs/worker-runs", params={"instance_id": instance_id})
    runs = result["result"]
    latest = runs.get("latest") or {}
    active = runs.get("active") or {}
    finished = latest.get("finished_at") if latest.get("state") == "succeeded" else None
    synced = datetime.fromtimestamp(finished, UTC).isoformat() if finished is not None else None
    value = {"mode": "live_index", "syncing": runs.get("active") is not None,
             "last_synced_at": synced, "run_id": active.get("run_id"),
             "worker_alive": active.get("worker_alive")}
    try:
        issues = await upstream(database, "GET", "/ingestion/issues", params={"instance_id": instance_id})
        rows = issues["result"]["rows"]
        if isinstance(rows, list) and len(rows) <= 1000 and all(isinstance(row, dict) for row in rows):
            value["ingestion_issues"] = rows
    except (httpx2.HTTPError, ValueError, TypeError, KeyError, AttributeError):
        pass
    return {"result": {"value": value, "text": None}}


async def _abort(socket, instance_id, args):
    if set(args) != {"run_id"} or not isinstance(args["run_id"], str) or not args["run_id"]:
        return tool_failure("tool_input_invalid", "Expected an active Worker run_id")
    if socket is None:
        return tool_failure("run_not_abortable", "Project has no active Worker")
    result = await upstream(socket, "POST", "/jobs/abort", json={"instance_id": instance_id, "run_id": args["run_id"]})
    if "error" in result:
        return tool_failure(result["error"]["code"], result["error"]["message"])
    return {"result": {"value": result["result"], "text": None}}


def _target(args):
    target = args.get("target")
    if set(args) != {"target"} or not isinstance(target, str):
        raise ValueError("Expected a target table or result selector")
    scope = target.removeprefix("main.")
    scope = TABLE_ALIASES.get(scope, scope)
    if scope in ("all", "workbench_results", *TABLES, *FLOW_HISTORY):
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
        refreshed = await upstream(orchestrator, "POST", "/jobs/build", timeout=httpx2.Timeout(None, connect=10),
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
            return await _status(orchestrator, database, instance_id, args)
        if name == "workbench_abort":
            return await _abort(orchestrator, instance_id, args)
        return await _rebuild(database, orchestrator, binding, instance_id, args)
    except (httpx2.HTTPError, ValueError, TypeError, KeyError, AttributeError, OverflowError):
        return tool_failure("workbench_unavailable", "Projection service unavailable")
