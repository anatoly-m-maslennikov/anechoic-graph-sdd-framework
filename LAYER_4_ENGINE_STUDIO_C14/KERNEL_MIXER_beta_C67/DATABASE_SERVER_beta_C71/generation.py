"""Validate and atomically admit one Worker generation."""

from hashlib import sha256
import json
import re
from typing import Any

from pydantic import BaseModel, ConfigDict, ValidationError, field_validator

from .accepted_model import discard, generation_rows, prepare, publish
from .analysis_projection import replace_spec, snapshot_sizes
from .carrier_checkpoint import update_checkpoint
from .ingestion_issues import clear_issues, replace_carrier_issues
from .native_atoms import replace_native_atoms, validate_native_snapshot
from .native_graph import replace_native_graph
from .realization_projection import has_table, replace, restore_property_graph, validate
from .table_names import sync_query_views
from .project_structure import replace_structure
from .model_projection import replace_model_diagnostics, replace_model_projection, validate_model_diagnostics

FULL_GENERATION_BODY_LIMIT = 128 * 1024 * 1024

_HEX = re.compile(r"[0-9a-f]{64}\Z")
class _ReuseInputs(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    manifest: str
    graph: str
    carrier_schema: str | None = None

    @field_validator("manifest", "graph", "carrier_schema", mode="before")
    @classmethod
    def validate_digest(cls, value, info):
        if not isinstance(value, str) or (info.field_name != "graph" or value not in {"disabled", "pending"}) and _HEX.fullmatch(value) is None:
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
    if (not isinstance(snapshot, dict) or set(snapshot) != {"manifest_sha256", "atoms"}
            or snapshot["manifest_sha256"] != manifest_sha256
            or not isinstance(snapshot["atoms"], list)):
        raise ValueError("Invalid snapshot binding or format")
    atoms = snapshot["atoms"]
    if any(not isinstance(atom, dict) or set(atom) != {"reference", "summary"}
           or not all(isinstance(atom[key], str) for key in ("reference", "summary"))
           for atom in atoms):
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
    return sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _validate_generation(data, manifest_sha256):
    receipt, snapshot = data["receipt"], data["snapshot"]
    native = isinstance(snapshot, dict) and snapshot.get("schema_version") == 2
    fields = {"manifest_sha256", "model_sha256", "model_descriptor_sha256", "structure_sha256", "graph_sha256"}
    if native:
        fields.add("snapshot_sha256")
    if (not isinstance(receipt, dict) or set(receipt) != fields
            or any(not isinstance(v, str) or _HEX.fullmatch(v) is None for v in receipt.values())
            or receipt["manifest_sha256"] != manifest_sha256):
        raise ValueError("Invalid receipt")
    model, structure, descriptor, s = _artifacts(
        data, receipt, manifest_sha256
    )
    if native:
        if _digest(snapshot) != receipt["snapshot_sha256"]:
            raise ValueError("Native snapshot digest mismatch")
        validate_native_snapshot(
            snapshot, manifest_sha256, descriptor["bindings"]
        )
        endpoints = descriptor["bindings"].get("endpoints")
        if not isinstance(endpoints, dict) or set(endpoints) != set(
            snapshot["relation_types"]
        ):
            raise ValueError(
                "Snapshot relation types differ from the admitted Model"
            )
    else:
        _legacy_atoms(snapshot, manifest_sha256)
    graph = data["graph"]
    if _digest(graph) != receipt["graph_sha256"]:
        raise ValueError("Graph digest mismatch")
    components = {"C00", *s["components"]}
    return native, snapshot, model, structure, validate(graph, components), components, descriptor


def _write_reuse(connection, data, model):
    witness = data.get("reuse")
    if witness is not None:
        if not isinstance(witness, dict) or not isinstance(witness.get("inputs"), dict):
            raise ValueError("Invalid reuse witness")
        try:
            record = _ReuseWitness.model_validate(witness)
        except ValidationError as error:
            raise ValueError("Invalid reuse witness") from error
        if record.endpoints != json.loads(model, object_pairs_hook=_unique)["bindings"].get("endpoints"):
            raise ValueError("Invalid reuse witness")
        witness = record.model_dump(exclude_unset=True)
    elif "reuse" in data:
        raise ValueError("Invalid reuse witness")
    connection.execute("CREATE TABLE IF NOT EXISTS ops_generation_reuse (witness VARCHAR)")
    connection.execute("DELETE FROM ops_generation_reuse")
    if witness is not None:
        connection.execute("INSERT INTO ops_generation_reuse VALUES (?)", [json.dumps(witness, ensure_ascii=False)])


def _native_graph_payload(data, components, identity):
    if "graph" not in data:
        return None
    digest = data["graph_sha256"]
    if (not isinstance(data["graph"], dict) or not isinstance(digest, str)
            or _HEX.fullmatch(digest) is None or _digest(data["graph"]) != digest):
        raise ValueError("Invalid graph or digest mismatch")
    graph = validate(data["graph"], components)
    identity["graph_sha256"] = digest
    return graph


def _archive_seed(data, pending):
    if "archive_versions" not in data:
        return None
    versions = data["archive_versions"]
    if (not pending or not isinstance(versions, dict) or len(versions) > 1_000_000
            or any(not isinstance(key, str) or re.fullmatch(r"[A-Z][A-Z0-9]*-[STPC]-[0-9]+", key) is None
                   or type(value) is not int or not 0 < value <= 2**63 - 1
                   for key, value in versions.items())):
        raise ValueError("Invalid archive version seed")
    return versions


def _replace_snapshot(connection, native, snapshot, components, *, archive_pending, archive_versions):
    if native:
        from .archive_generation import backfill_archive_versions, refresh_archive_versions, seed_archive_versions
        if archive_pending:
            backfill_archive_versions(connection)
            seed_archive_versions(connection, archive_versions)
        replace_native_atoms(connection, snapshot)
        if not archive_pending:
            refresh_archive_versions(connection)
        replace_native_graph(connection, snapshot["relation_types"], components)
    else:
        connection.execute("DELETE FROM mrt_atoms")
        if atoms := snapshot["atoms"]:
            connection.executemany("INSERT INTO mrt_atoms VALUES (?, ?)", [(a["reference"], a["summary"]) for a in atoms])


class _PreparedGeneration(BaseModel):
    model_config = ConfigDict(frozen=True)

    native: bool
    snapshot: dict[str, Any]
    model: str
    structure: str
    graph: dict[str, Any] | None
    components: set[str]
    descriptor: dict[str, Any]
    diagnostics: list[dict[str, Any]] | None
    pending: bool
    versions: dict[str, int] | None
    generation: str


def prepare_generation(data, manifest_sha256):
    native, snapshot, model, structure, graph, components, descriptor = _validate_generation(data, manifest_sha256)
    diagnostics = (validate_model_diagnostics(data["model_diagnostics"], descriptor["model_sha256"])
                   if "model_diagnostics" in data else None)
    pending = data.get("archive_pending", False)
    if type(pending) is not bool or (pending and (not native or "carrier_hashes" not in data
            or any(row["status_group"] == "Archived" for row in snapshot["atoms"]))):
        raise ValueError("Invalid pending archive generation")
    versions = _archive_seed(data, pending)
    identity = {"receipt": data["receipt"], "snapshot": snapshot}
    if pending:
        identity["archive_pending"] = True
    if diagnostics is not None:
        identity["model_diagnostics"] = diagnostics
    return _PreparedGeneration.model_construct(
        native=native, snapshot=snapshot, model=model, structure=structure, graph=graph,
        components=components, descriptor=descriptor, diagnostics=diagnostics,
        pending=pending, versions=versions, generation=_digest(identity))


def replace_generation(connection, data, prepared, *, stage_refresh=None):
    native, snapshot, model = prepared.native, prepared.snapshot, prepared.model
    structure, graph, components = prepared.structure, prepared.graph, prepared.components
    descriptor, diagnostics, pending = prepared.descriptor, prepared.diagnostics, prepared.pending
    versions, generation = prepared.versions, prepared.generation
    if not native and has_table(connection, "main", "mrt_atom_graph_relations"):
        raise ValueError("Cannot replace a native generation with the legacy snapshot format")
    pending_file = None
    connection.execute("BEGIN TRANSACTION")
    try:
        connection.execute("DROP PROPERTY GRAPH IF EXISTS anechoic")
        _replace_snapshot(connection, native, snapshot, components, archive_pending=pending, archive_versions=versions)
        replace(connection, graph, components)
        if native and has_table(connection, "main", "biz_architecture_spec_metrics"):
            replace_spec(connection, snapshot_sizes(snapshot))
        connection.execute("DELETE FROM ops_generation")
        replace_model_projection(connection, descriptor)
        if diagnostics is not None:
            replace_model_diagnostics(connection, diagnostics)
        replace_structure(connection, structure)
        stored_model, pending_file = prepare(connection, model)
        connection.execute("INSERT INTO ops_generation VALUES (?, ?, ?)", [generation, stored_model, structure])
        from .archive_generation import set_archive_pending
        set_archive_pending(connection, pending)
        _write_reuse(connection, data, model)
        update_checkpoint(connection, data)
        replace_carrier_issues(connection, snapshot, archive_pending=pending)
        clear_issues(connection, "build")
        sync_query_views(connection)
        captured = stage_refresh() if stage_refresh is not None else None
        connection.execute("COMMIT")
    except BaseException:
        connection.execute("ROLLBACK")
        discard(pending_file)
        restore_property_graph(connection)
        raise
    publish(connection, model, pending_file)
    return generation, captured


class GenerationBaseChanged(ValueError):
    """The conditional native update no longer has its accepted base."""


def _finish_native_checkpoint(connection, data):
    from .archive_generation import (
        refresh_archive_versions,
        set_archive_pending,
    )

    refresh_archive_versions(connection)
    set_archive_pending(connection, False)
    update_checkpoint(connection, data)
    replace_carrier_issues(connection, data["snapshot"])
    clear_issues(connection, "build")


def replace_native_generation(connection, data, manifest_sha256):
    """Replace native rows and optionally the Realization Graph, retaining artifacts."""
    connection.execute("BEGIN TRANSACTION")
    graph_dropped = False
    try:
        rows = generation_rows(connection)
        if (len(rows) != 1 or rows[0][0] != data["base_generation"]
                or not has_table(connection, "native_graph", "int_labels")
                or not has_table(connection, "main", "mrt_atom_graph_relations")):
            raise GenerationBaseChanged("Generation base changed or is not native")
        base, model, structure = rows[0]
        snapshot, digest = data["snapshot"], data["snapshot_sha256"]
        if not isinstance(digest, str) or _HEX.fullmatch(digest) is None or _digest(snapshot) != digest:
            raise ValueError("Native snapshot digest mismatch")
        bindings = json.loads(model, object_pairs_hook=_unique)["bindings"]
        validate_native_snapshot(snapshot, manifest_sha256, bindings)
        endpoints = bindings.get("endpoints")
        if not isinstance(endpoints, dict) or set(endpoints) != set(snapshot["relation_types"]):
            raise ValueError("Snapshot relation types differ from the admitted Model")
        components = {"C00", *json.loads(structure, object_pairs_hook=_unique)["components"]}
        identity = {"kind": "native_snapshot_refresh", "base_generation": base, "snapshot_sha256": digest}
        graph = _native_graph_payload(data, components, identity)
        generation = _digest(identity)
        connection.execute("DROP PROPERTY GRAPH IF EXISTS anechoic")
        graph_dropped = True
        replace_native_atoms(connection, snapshot)
        replace_native_graph(connection, snapshot["relation_types"], components)
        if graph is None:
            restore_property_graph(connection)
        else:
            replace(connection, graph, components)
            _write_reuse(connection, data, model)
        if has_table(connection, "main", "biz_architecture_spec_metrics"):
            replace_spec(connection, snapshot_sizes(snapshot))
        _finish_native_checkpoint(connection, data)
        connection.execute("UPDATE ops_generation SET id = ?", [generation])
        sync_query_views(connection)
        connection.execute("COMMIT")
    except BaseException:
        connection.execute("ROLLBACK")
        if graph_dropped:
            restore_property_graph(connection)
        raise
    return generation
