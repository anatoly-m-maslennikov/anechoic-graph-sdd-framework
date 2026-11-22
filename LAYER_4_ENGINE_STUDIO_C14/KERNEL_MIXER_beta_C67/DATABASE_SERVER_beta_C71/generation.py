"""Validate and atomically admit one Worker generation."""

from hashlib import sha256
import json
import re

from .native_atoms import replace_native_atoms, validate_native_snapshot
from .native_graph import replace_native_graph
from .realization_projection import has_table, replace, restore_property_graph, validate

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


def replace_generation(connection, data, manifest_sha256, *, stage_refresh=None):
    native, snapshot, model, structure, graph, components = _validate_generation(data, manifest_sha256)
    generation = _digest({"receipt": data["receipt"], "snapshot": snapshot})
    if not native and has_table(connection, "main", "relations"):
        raise ValueError("Cannot replace a native generation with the legacy snapshot format")
    connection.execute("BEGIN TRANSACTION")
    try:
        connection.execute("DROP PROPERTY GRAPH IF EXISTS anechoic")
        if native:
            replace_native_atoms(connection, snapshot)
            replace_native_graph(connection, snapshot["relation_types"], components)
        else:
            connection.execute("DELETE FROM atoms")
            if atoms := snapshot["atoms"]:
                connection.executemany("INSERT INTO atoms VALUES (?, ?)", [(a["reference"], a["summary"]) for a in atoms])
        replace(connection, graph, components)
        connection.execute("DELETE FROM generation")
        connection.execute("INSERT INTO generation VALUES (?, ?, ?)", [generation, model, structure])
        captured = stage_refresh() if stage_refresh is not None else None
        connection.execute("COMMIT")
    except BaseException:
        connection.execute("ROLLBACK")
        restore_property_graph(connection)
        raise
    return generation, captured
