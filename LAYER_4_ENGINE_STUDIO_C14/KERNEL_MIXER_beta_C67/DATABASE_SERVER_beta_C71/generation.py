"""Validate and atomically admit one Worker generation."""

from hashlib import sha256
import json
import re

from .analysis_projection import replace_spec, snapshot_sizes
from .carrier_checkpoint import update_checkpoint
from .native_atoms import replace_native_atoms, validate_native_snapshot
from .native_graph import replace_native_graph
from .realization_projection import has_table, replace, restore_property_graph, validate
from .table_names import sync_query_views

_HEX = re.compile(r"[0-9a-f]{64}\Z")


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
    if (sha256(model.encode("utf-8")).hexdigest() != receipt["model_descriptor_sha256"]
            or sha256(structure.encode("utf-8")).hexdigest() != receipt["structure_sha256"]):
        raise ValueError("Artifact digest mismatch")
    m = json.loads(model, object_pairs_hook=_unique)
    s = json.loads(structure, object_pairs_hook=_unique)
    if (not isinstance(m, dict) or not isinstance(s, dict)
            or m.get("binding_schema") != 1
            or not isinstance(m.get("modules"), dict) or "__init__.py" not in m["modules"]
            or not isinstance(m.get("module_order"), list)
            or not isinstance(m.get("class_modules"), dict) or not isinstance(m.get("bindings"), dict)
            or m.get("model_sha256") != receipt["model_sha256"]
            or s.get("model_sha256") != receipt["model_sha256"]
            or not isinstance(s.get("project"), dict)
            or s["project"].get("sha256") != manifest_sha256
            or not isinstance(s["project"].get("ref"), str) or not s["project"]["ref"]
            or not isinstance(s.get("components"), dict)
            or not isinstance(s.get("packages", {}), dict)):
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
    model, structure, descriptor, s = _artifacts(data, receipt, manifest_sha256)
    if native:
        if _digest(snapshot) != receipt["snapshot_sha256"]:
            raise ValueError("Native snapshot digest mismatch")
        validate_native_snapshot(snapshot, manifest_sha256)
        endpoints = descriptor["bindings"].get("endpoints")
        if not isinstance(endpoints, dict) or set(endpoints) != set(snapshot["relation_types"]):
            raise ValueError("Snapshot relation types differ from the admitted Model")
    else:
        _legacy_atoms(snapshot, manifest_sha256)
    graph = data["graph"]
    if _digest(graph) != receipt["graph_sha256"]:
        raise ValueError("Graph digest mismatch")
    components = {"C00", *s["components"]}
    return native, snapshot, model, structure, validate(graph, components), components


def _write_reuse(connection, data, model):
    witness = data.get("reuse")
    if witness is not None:
        if (not isinstance(witness, dict) or set(witness) != {"inputs", "graph_config", "endpoints"}
                or not isinstance(witness["inputs"], dict) or set(witness["inputs"]) != {"manifest", "graph"}
                or not isinstance(witness["inputs"]["manifest"], str)
                or _HEX.fullmatch(witness["inputs"]["manifest"]) is None
                or not isinstance(witness["inputs"]["graph"], str)
                or (witness["inputs"]["graph"] != "disabled" and _HEX.fullmatch(witness["inputs"]["graph"]) is None)
                or not (witness["graph_config"] is None or isinstance(witness["graph_config"], dict))
                or not isinstance(witness["endpoints"], dict)
                or witness["endpoints"] != json.loads(model, object_pairs_hook=_unique)["bindings"].get("endpoints")):
            raise ValueError("Invalid reuse witness")
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


def replace_generation(connection, data, manifest_sha256, *, stage_refresh=None):
    native, snapshot, model, structure, graph, components = _validate_generation(data, manifest_sha256)
    generation = _digest({"receipt": data["receipt"], "snapshot": snapshot})
    if not native and has_table(connection, "main", "mrt_atom_graph_relations"):
        raise ValueError("Cannot replace a native generation with the legacy snapshot format")
    connection.execute("BEGIN TRANSACTION")
    try:
        connection.execute("DROP PROPERTY GRAPH IF EXISTS anechoic")
        if native:
            replace_native_atoms(connection, snapshot)
            replace_native_graph(connection, snapshot["relation_types"], components)
        else:
            connection.execute("DELETE FROM mrt_atoms")
            if atoms := snapshot["atoms"]:
                connection.executemany("INSERT INTO mrt_atoms VALUES (?, ?)", [(a["reference"], a["summary"]) for a in atoms])
        replace(connection, graph, components)
        if native and has_table(connection, "main", "biz_architecture_spec_metrics"):
            replace_spec(connection, snapshot_sizes(snapshot))
        connection.execute("DELETE FROM ops_generation")
        connection.execute("INSERT INTO ops_generation VALUES (?, ?, ?)", [generation, model, structure])
        _write_reuse(connection, data, model)
        update_checkpoint(connection, data)
        sync_query_views(connection)
        captured = stage_refresh() if stage_refresh is not None else None
        connection.execute("COMMIT")
    except BaseException:
        connection.execute("ROLLBACK")
        restore_property_graph(connection)
        raise
    return generation, captured


class GenerationBaseChanged(ValueError):
    """The conditional native update no longer has its accepted base."""


def replace_native_generation(connection, data, manifest_sha256):
    """Replace native rows and optionally the Realization Graph, retaining artifacts."""
    connection.execute("BEGIN TRANSACTION")
    graph_dropped = False
    try:
        rows = connection.execute("SELECT id, model, structure FROM ops_generation").fetchall()
        if (len(rows) != 1 or rows[0][0] != data["base_generation"]
                or not has_table(connection, "native_graph", "int_labels")
                or not has_table(connection, "main", "mrt_atom_graph_relations")):
            raise GenerationBaseChanged("Generation base changed or is not native")
        base, model, structure = rows[0]
        snapshot, digest = data["snapshot"], data["snapshot_sha256"]
        if not isinstance(digest, str) or _HEX.fullmatch(digest) is None or _digest(snapshot) != digest:
            raise ValueError("Native snapshot digest mismatch")
        validate_native_snapshot(snapshot, manifest_sha256)
        endpoints = json.loads(model, object_pairs_hook=_unique)["bindings"].get("endpoints")
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
        update_checkpoint(connection, data)
        connection.execute("UPDATE ops_generation SET id = ?", [generation])
        sync_query_views(connection)
        connection.execute("COMMIT")
    except BaseException:
        connection.execute("ROLLBACK")
        if graph_dropped:
            restore_property_graph(connection)
        raise
    return generation
