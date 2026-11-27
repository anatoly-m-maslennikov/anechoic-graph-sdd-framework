"""Expose Atom lifecycle calls through the selected Project Orchestrator."""
import os
from typing import Annotated, Any, Literal

import httpx2
from pydantic import BaseModel, ConfigDict, Field, ValidationError, create_model

from .admission import failure, peer

_FIELDS = {"type": "object"}
_TEXT = {"type": "string"}
_DEFINITIONS = {
    "atom_lifecycle_create_draft": ("Create an eligible Atom Draft or revise a Current Atom.", {},
                                    {"newAtom": _FIELDS, "sourceCurrent": _FIELDS, "changes": _FIELDS}),
    "atom_lifecycle_update": ("Create a Draft revision of a Current Atom or update an exact Draft.",
                              {}, {"sourceCurrent": _FIELDS, "target": _FIELDS, "changes": _FIELDS,
                                   "expectedUpdatedAt": _TEXT}),
    "atom_lifecycle_promote_draft": ("Publish an exact Atom Draft revision.", {"target": _FIELDS},
                                     {"targetStatus": _TEXT}),
    "atom_lifecycle_change_status": ("Apply a supported Status transition to a Current Atom.",
                                     {"target": _FIELDS}, {"targetStatus": _TEXT}),
    "atom_lifecycle_archive": ("Archive an eligible exact Atom revision.", {"target": _FIELDS}, {}),
    "atom_lifecycle_create_asset": ("Create a detached or attached Ticket Asset.", {"newAtom": _FIELDS}, {}),
    "atom_lifecycle_direct_update": ("Update the Markdown body of a Ticket Asset.",
                                     {"target": _FIELDS, "changes": _FIELDS}, {}),
}
_UNKNOWN = {"code": "write_outcome_unknown", "message": "The lifecycle write outcome is unknown."}


def descriptors():
    tools = {}
    for name, (description, required, optional) in _DEFINITIONS.items():
        schema = {"type": "object", "properties": {**required, **optional}, "additionalProperties": False}
        if required:
            schema["required"] = list(required)
        tools[name] = {"name": name, "description": description, "inputSchema": schema,
                       "annotations": {"readOnlyHint": False, "destructiveHint": False,
                                       "idempotentHint": False, "openWorldHint": False}}
    return tools


class Arguments(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")


_MODELS = {}
for _name, (_, _required, _optional) in _DEFINITIONS.items():
    _fields = {key: (dict[str, Any] if value is _FIELDS else str, ...) for key, value in _required.items()}
    _fields.update({key: (dict[str, Any] | None if value is _FIELDS else str | None, None)
                    for key, value in _optional.items()})
    _MODELS[_name] = create_model(_name, __base__=Arguments, **_fields)


class Native(BaseModel):
    model_config = ConfigDict(strict=True, extra="allow")
    outcome: str
    effects: list[Any] = Field(default_factory=list)
    warnings: list[Any] = Field(default_factory=list)
    errors: list[Any] = Field(default_factory=list)
    requested_input: dict[str, dict[str, Any]] = Field(default_factory=dict)


class ProjectionReady(BaseModel):
    model_config = ConfigDict(strict=True, extra="allow")
    state: Literal["ready"]
    error: dict[str, Any] | None = None


class ProjectionFailed(BaseModel):
    model_config = ConfigDict(strict=True, extra="allow")
    state: Literal["failed"]
    error: dict[str, Any]


class ProjectionBlocked(BaseModel):
    model_config = ConfigDict(strict=True, extra="allow")
    state: Literal["blocked"]


class Outcome(BaseModel):
    model_config = ConfigDict(strict=True, extra="allow")
    write_state: Literal["known", "unknown"]
    projection: Annotated[ProjectionReady | ProjectionFailed | ProjectionBlocked, Field(discriminator="state")]
    lifecycle: Any = None


def _failure(native, errors):
    return {"status": "blocked" if native.get("outcome") == "blocked" and not errors else "failed",
            "effects": native.get("effects", []), "warnings": native.get("warnings", []),
            "errors": [*native.get("errors", []), *errors]}


def _result(name, reply):
    parsed = Outcome.model_validate(reply)
    projection = parsed.projection
    errors = [projection.error] if projection.state == "failed" else []
    if projection.state == "blocked" and (parsed.write_state != "known"
            or not isinstance(parsed.lifecycle, dict) or parsed.lifecycle.get("outcome") != "blocked"):
        raise ValueError("Invalid lifecycle outcome")
    if parsed.write_state == "unknown":
        return _failure({}, [_UNKNOWN, *errors])
    if parsed.lifecycle is None:
        raise ValueError("Missing lifecycle result")
    native = Native.model_validate(parsed.lifecycle).model_dump(exclude_unset=True)
    if errors or native["outcome"] != "completed" or native.get("errors"):
        inputs = [{"code": "invalid_input", "field": key, "message": detail["error"]}
                  for key, detail in native.get("requested_input", {}).items()]
        value = _failure(native, [*inputs, *errors])
        if not value["errors"]:
            value["errors"] = [{"code": "backend_failure", "message": "Lifecycle operation failed."}]
        return value
    if name == "atom_lifecycle_direct_update":
        return {"status": "completed"}
    status = "draft_created" if name == "atom_lifecycle_update" and "savedDraft" in native else "completed"
    return {"status": status, **{key: native[key] for key in ("savedDraft", "artifact", "sourceRef") if key in native}}


async def invoke(name, args, orchestrator, binding, instance_id):
    try:
        validated = _MODELS[name].model_validate(args)
        if any(value is None for value in args.values()):
            raise ValueError("Null lifecycle arguments are not supported")
    except (KeyError, TypeError, ValueError, ValidationError):
        return failure("tool_input_invalid", "Invalid lifecycle arguments")
    if binding is None:
        return failure("workbench_unavailable", "Managed Orchestrator binding is unavailable")
    timeout = httpx2.Timeout(None, connect=10) if os.getenv("ANECHOIC_TEST_IMAGE_DEADLINES") == "0" else 625
    try:
        reply = await peer(orchestrator, "POST", "/jobs/lifecycle", timeout=timeout,
                           json={**binding, "instance_id": instance_id, "name": name,
                                 "arguments": validated.model_dump(exclude_unset=True)})
        if "error" in reply:
            error = reply["error"]
            return failure(error["code"], error["message"])
        return {"result": {"value": _result(name, reply["result"]), "text": None}}
    except (httpx2.HTTPError, ValueError, TypeError, KeyError, AttributeError):
        return {"result": {"value": _failure({}, [_UNKNOWN]), "text": None}}
