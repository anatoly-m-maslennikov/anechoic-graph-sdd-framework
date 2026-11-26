"""Validate Worker generation envelopes before contextual admission checks."""
import json
from pathlib import PurePosixPath
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, InstanceOf, ValidationError

from .startup_checkpoint import checkpoint_paths

FULL_FIELDS = {"snapshot", "receipt", "graph", "reuse"}
BATCH_FIELDS = {"batch_artifact", "receipt", "reuse"}
NATIVE_FIELDS = {"base_generation", "snapshot", "snapshot_sha256"}
DELTA_FIELDS = NATIVE_FIELDS | {"paths"}
GRAPH_FIELDS = NATIVE_FIELDS | {"graph", "graph_sha256", "reuse"}


class _Deferred(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    roots: InstanceOf[list]
    snapshot: InstanceOf[dict]
    carrier_hashes: InstanceOf[dict]
    endpoints: InstanceOf[dict]
    archive_versions: dict[str, int] | None = None


class _Archive(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    snapshot: InstanceOf[dict]
    carrier_hashes: InstanceOf[dict]


class _Reuse(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    inputs: Any
    graph_config: Any
    endpoints: Any


class _Reply(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    carrier_hashes: Any = None
    deferred_archive: Any = None


class _Full(_Reply):
    model_diagnostics: InstanceOf[list] | None = None
    snapshot: Any
    receipt: Any
    graph: Any
    reuse: InstanceOf[dict] | None


class _BatchArtifact(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    bytes: int = Field(gt=0, le=1024**3)


class _BatchedFull(_Reply):
    model_diagnostics: InstanceOf[list] | None = None
    batch_artifact: _BatchArtifact
    receipt: Any
    reuse: InstanceOf[dict] | None


class _Native(_Reply):
    base_generation: Any
    snapshot: Any
    snapshot_sha256: Any


class _Delta(_Native):
    paths: InstanceOf[list]


class _Graph(_Native):
    graph: Any
    graph_sha256: Any
    reuse: InstanceOf[dict]


class _Unchanged(_Reply):
    base_generation: Any
    unchanged: Literal[True]


class _GraphOnly(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    base_generation: str
    graph: InstanceOf[dict]
    graph_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    reuse: _Reuse


def _validate(model, value, message):
    try:
        return model.model_validate(value)
    except ValidationError:
        raise ValueError(message) from None


def _shallow(model, raw):
    return {key: getattr(model, key) for key in raw}


def _deferred(result, fields, foreground):
    if not foreground or "deferred_archive" not in fields:
        return None
    value = _validate(_Deferred, result["deferred_archive"], "Worker returned invalid deferred archive input")
    fields.remove("deferred_archive")
    return value


def _native(result, fields, reuse, paths, structure, checkpoint):
    if reuse is None or result["base_generation"] != reuse["base_generation"]:
        raise ValueError("Worker returned an unexpected generation base")
    witness = None
    if fields == GRAPH_FIELDS:
        if structure is None:
            raise ValueError("Worker returned invalid graph refresh")
        witness = _validate(_Reuse, result["reuse"], "Worker returned invalid graph refresh")
    if fields == DELTA_FIELDS:
        relatives = sorted(map(PurePosixPath, paths or ()))
        expected = [[path.parent.as_posix(), path.name] for path in relatives]
        if checkpoint:
            expected = checkpoint_paths(result["paths"])
        if not expected or result["paths"] != expected:
            raise ValueError("Worker returned unexpected Ticket delta paths")
    model = _Graph if fields == GRAPH_FIELDS else _Delta if fields == DELTA_FIELDS else _Native
    return model.model_validate(result), witness


def _select(result, fields, reuse, paths, structure, foreground):
    checkpoint = reuse is not None and "carrier_hashes" in reuse and paths is None
    if fields == {"base_generation", "unchanged"}:
        if not checkpoint or result.get("unchanged") is not True or result["base_generation"] != reuse["base_generation"] or "carrier_hashes" in result:
            raise ValueError("Worker returned invalid unchanged generation")
        return _Unchanged.model_validate(result), None
    if fields in (NATIVE_FIELDS, DELTA_FIELDS, GRAPH_FIELDS):
        return _native(result, fields, reuse, paths, structure, checkpoint)
    if fields not in (FULL_FIELDS, BATCH_FIELDS) or (foreground and "deferred_archive" not in result):
        raise ValueError("Worker returned invalid generation")
    if fields == BATCH_FIELDS and "carrier_hashes" in result:
        raise ValueError("Worker returned invalid generation")
    raw = result["reuse"]
    witness = None if raw is None else _validate(_Reuse, raw, "Worker returned invalid generation reuse witness")
    model = _BatchedFull if fields == BATCH_FIELDS else _Full
    return _validate(model, result, "Worker returned invalid generation"), witness


def parse_archive_result(stdout):
    result = json.loads(stdout)
    reply = _validate(_Archive, result, "Worker returned invalid Archive result")
    return _shallow(reply, result)


def parse_graph_result(stdout, base):
    result = json.loads(stdout)
    if not isinstance(result, dict) or result.get("base_generation") != base:
        raise ValueError("Worker returned an unexpected graph base")
    if set(result) == {"base_generation", "unchanged"} and result["unchanged"] is True:
        return result
    return _validate(_GraphOnly, result, "Worker returned an invalid startup graph").model_dump()


def parse_worker_result(stdout, reuse, paths, structure=None, *, foreground=False):
    return parse_worker_data(json.loads(stdout), reuse, paths, structure, foreground=foreground)


def parse_worker_data(result, reuse, paths, structure=None, *, foreground=False):
    if not isinstance(result, dict):
        raise TypeError("Worker returned invalid generation")
    fields = set(result) - {"carrier_hashes"}
    deferred = _deferred(result, fields, foreground)
    if "model_diagnostics" in fields:
        fields.remove("model_diagnostics")
        if fields not in (FULL_FIELDS, BATCH_FIELDS) or not isinstance(result["model_diagnostics"], list):
            raise ValueError("Worker returned invalid Model diagnostics")
    reply, witness = _select(result, fields, reuse, paths, structure, foreground)
    output = _shallow(reply, result)
    if "batch_artifact" in output:
        output["batch_artifact"] = output["batch_artifact"].model_dump()
    if deferred is not None:
        output["deferred_archive"] = _shallow(deferred, result["deferred_archive"])
    if witness is not None:
        output["reuse"] = _shallow(witness, result["reuse"])
    return output
