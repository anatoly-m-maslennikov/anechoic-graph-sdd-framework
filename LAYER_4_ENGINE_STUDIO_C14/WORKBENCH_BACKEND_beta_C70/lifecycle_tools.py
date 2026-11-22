"""Expose the admitted Ticket lifecycle operations through Orchestrator."""

import httpx2

from .peer_transport import tool_failure, upstream
from .workspace_tools import _tool

_FIELDS = {"type": "object"}
TOOLS = {tool["name"]: tool for tool in (
    _tool("atom_lifecycle_create_draft", "Create a Task or Epic Draft or revise a Current Ticket.", {},
          newAtom=_FIELDS, sourceCurrent=_FIELDS, changes=_FIELDS),
    _tool("atom_lifecycle_update", "Create a Draft revision of a Current Task or Epic.",
          {"sourceCurrent": _FIELDS}, changes=_FIELDS),
    _tool("atom_lifecycle_promote_draft", "Publish an exact Task or Epic Draft revision.",
          {"target": _FIELDS}, targetStatus={"type": "string"}),
    _tool("atom_lifecycle_change_status", "Change a Current Task or Epic Status.",
          {"target": _FIELDS}, targetStatus={"type": "string"}),
    _tool("atom_lifecycle_archive", "Archive an exact Task or Epic revision with an admitted replacement.",
          {"target": _FIELDS}),
)}
_UNKNOWN = {
    "code": "write_outcome_unknown",
    "message": "The lifecycle write outcome is unknown. Check the Project before retrying.",
}


def _failure(native, errors):
    return {"status": "blocked" if native.get("outcome") == "blocked" and not errors else "failed",
            "effects": native.get("effects", []), "warnings": native.get("warnings", []),
            "errors": [*native.get("errors", []), *errors]}


def _result(name, reply):
    projection = reply["projection"]
    if projection["state"] not in {"ready", "failed"} or reply["write_state"] not in {"known", "unknown"}:
        raise ValueError("Invalid lifecycle outcome")
    failure = [projection["error"]] if projection["state"] == "failed" else []
    if reply["write_state"] == "unknown":
        return _failure({}, [_UNKNOWN, *failure])
    native = reply["lifecycle"]
    if failure or native["outcome"] != "completed" or native.get("errors"):
        input_errors = [
            {"code": "invalid_input", "field": field, "message": detail["error"]}
            for field, detail in native.get("requested_input", {}).items()
        ]
        value = _failure(native, [*input_errors, *failure])
        if not value["errors"]:
            value["errors"] = [{"code": "backend_failure", "message": "Lifecycle operation failed."}]
        return value
    status = "draft_created" if name == "atom_lifecycle_update" and "savedDraft" in native else "completed"
    return {"status": status, **{field: native[field] for field in ("savedDraft", "artifact", "sourceRef")
                                 if field in native}}


def _response(value):
    return {"result": {"value": value, "text": None}}


async def invoke(name, args, orchestrator, binding, instance_id):
    schema = TOOLS[name]["inputSchema"]
    if not set(schema.get("required", ())) <= args.keys() <= schema["properties"].keys():
        return tool_failure("tool_input_invalid", "Invalid lifecycle arguments")
    if binding is None:
        return tool_failure("workbench_unavailable", "Managed Orchestrator binding is unavailable")
    try:
        reply = await upstream(orchestrator, "POST", "/jobs/lifecycle", timeout=625,
                               json={**binding, "instance_id": instance_id, "name": name, "arguments": args})
        if "error" in reply:
            error = reply["error"]
            return tool_failure(error["code"], error["message"])
        return _response(_result(name, reply["result"]))
    except (httpx2.HTTPError, ValueError, TypeError, KeyError, AttributeError):
        return _response(_failure({}, [_UNKNOWN]))
