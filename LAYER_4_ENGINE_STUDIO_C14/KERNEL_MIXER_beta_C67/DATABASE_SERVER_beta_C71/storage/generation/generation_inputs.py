"""Validate generation receipts, snapshot pins, and reuse witnesses."""

from hashlib import sha256
import json
import re

from pydantic import BaseModel, ConfigDict, ValidationError, field_validator

from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.realization_support.native.native__shared import validate_native_snapshot
from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.realization_projection import validate


_HEX = re.compile(r"[0-9a-f]{64}\Z")


class _ReuseInputs(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    manifest: str
    graph: str
    carrier_schema: str | None = None

    @field_validator("manifest", "graph", "carrier_schema", mode="before")
    @classmethod
    def validate_digest(cls, value, info):
        if (
            not isinstance(value, str)
            or (
                info.field_name != "graph"
                or value not in {"disabled", "pending"}
            )
            and _HEX.fullmatch(value) is None
        ):
            raise ValueError("Invalid reuse witness")
        return value


class _ReuseWitness(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    inputs: _ReuseInputs
    graph_config: dict | None
    endpoints: dict


def _legacy_atoms(snapshot, manifest_sha256):
    if _HEX.fullmatch(manifest_sha256) is None:
        raise ValueError("Invalid manifest SHA-256")
    if (
        not isinstance(snapshot, dict)
        or set(snapshot) != {"manifest_sha256", "atoms"}
        or snapshot["manifest_sha256"] != manifest_sha256
        or not isinstance(snapshot["atoms"], list)
    ):
        raise ValueError("Invalid snapshot binding or format")
    atoms = snapshot["atoms"]
    if any(
        not isinstance(atom, dict)
        or set(atom) != {"reference", "summary"}
        or not all(
            isinstance(atom[key], str) for key in ("reference", "summary")
        )
        for atom in atoms
    ):
        raise ValueError("Invalid snapshot atoms")
    return atoms


def _unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key")
        result[key] = value
    return result


def _artifacts(data, receipt, manifest_sha256):
    model, structure = data["model"], data["structure"]
    if not isinstance(model, str) or not isinstance(structure, str):
        raise ValueError("Artifacts must be JSON strings")
    if (
        sha256(model.encode("utf-8")).hexdigest()
        != receipt["model_descriptor_sha256"]
        or sha256(structure.encode("utf-8")).hexdigest()
        != receipt["structure_sha256"]
    ):
        raise ValueError("Artifact digest mismatch")
    m = json.loads(model, object_pairs_hook=_unique)
    s = json.loads(structure, object_pairs_hook=_unique)
    if (
        not isinstance(m, dict)
        or not isinstance(s, dict)
        or m.get("binding_schema") != 1
        or not isinstance(m.get("modules"), dict)
        or "__init__.py" not in m["modules"]
        or not isinstance(m.get("module_order"), list)
        or not isinstance(m.get("class_modules"), dict)
        or not isinstance(m.get("bindings"), dict)
        or m.get("model_sha256") != receipt["model_sha256"]
        or s.get("model_sha256") != receipt["model_sha256"]
        or not isinstance(s.get("project"), dict)
        or s["project"].get("sha256") != manifest_sha256
        or not isinstance(s["project"].get("ref"), str)
        or not s["project"]["ref"]
        or not isinstance(s.get("components"), dict)
        or not isinstance(s.get("packages", {}), dict)
    ):
        raise ValueError("Invalid artifact shape or binding")
    return model, structure, m, s


def _digest(value):
    return sha256(
        json.dumps(
            value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode()
    ).hexdigest()


def _validate_generation(data, manifest_sha256):
    receipt, snapshot = data["receipt"], data["snapshot"]
    native = isinstance(snapshot, dict) and snapshot.get("schema_version") == 2
    _validate_receipt(receipt, manifest_sha256, native)
    model, structure, descriptor, s = _artifacts(
        data, receipt, manifest_sha256
    )
    if native:
        if _digest(snapshot) != receipt["snapshot_sha256"]:
            raise ValueError("Native snapshot digest mismatch")
        _validate_snapshot_binding(
            snapshot, manifest_sha256, descriptor["bindings"]
        )
    else:
        _legacy_atoms(snapshot, manifest_sha256)
    graph = data["graph"]
    if _digest(graph) != receipt["graph_sha256"]:
        raise ValueError("Graph digest mismatch")
    components = {"C00", *s["components"]}
    return (
        native,
        snapshot,
        model,
        structure,
        validate(graph, components),
        components,
        descriptor,
    )


def _write_reuse(connection, data, model):
    witness = data.get("reuse")
    if witness is not None:
        if not isinstance(witness, dict) or not isinstance(
            witness.get("inputs"), dict
        ):
            raise ValueError("Invalid reuse witness")
        try:
            record = _ReuseWitness.model_validate(witness)
        except ValidationError as error:
            raise ValueError("Invalid reuse witness") from error
        if record.endpoints != json.loads(model, object_pairs_hook=_unique)[
            "bindings"
        ].get("endpoints"):
            raise ValueError("Invalid reuse witness")
        witness = record.model_dump(exclude_unset=True)
    elif "reuse" in data:
        raise ValueError("Invalid reuse witness")
    connection.execute(
        "CREATE TABLE IF NOT EXISTS ops_generation_reuse (witness VARCHAR)"
    )
    connection.execute("DELETE FROM ops_generation_reuse")
    if witness is not None:
        connection.execute(
            "INSERT INTO ops_generation_reuse VALUES (?)",
            [json.dumps(witness, ensure_ascii=False)],
        )


def _validate_receipt(receipt, manifest_sha256, native):
    fields = {
        "manifest_sha256",
        "model_sha256",
        "model_descriptor_sha256",
        "structure_sha256",
        "graph_sha256",
    }
    if native:
        fields.add("snapshot_sha256")
    if (
        not isinstance(receipt, dict)
        or set(receipt) != fields
        or any(
            not isinstance(v, str) or _HEX.fullmatch(v) is None
            for v in receipt.values()
        )
        or receipt["manifest_sha256"] != manifest_sha256
    ):
        raise ValueError("Invalid receipt")


def _validate_snapshot_binding(snapshot, manifest_sha256, bindings):
    validate_native_snapshot(snapshot, manifest_sha256, bindings)
    endpoints = bindings.get("endpoints")
    if not isinstance(endpoints, dict) or set(endpoints) != set(
        snapshot["relation_types"]
    ):
        raise ValueError(
            "Snapshot relation types differ from the admitted Model"
        )
