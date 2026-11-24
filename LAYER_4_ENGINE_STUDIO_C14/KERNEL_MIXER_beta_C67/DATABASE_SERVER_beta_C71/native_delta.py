"""Atomically replace addressed native carriers without rebuilding the graph."""

from collections import Counter
import json
from pathlib import PurePosixPath
import re

import duckdb
from starlette.responses import JSONResponse

from .analysis_projection import apply_spec_delta, snapshot_sizes
from .carrier_checkpoint import update_checkpoint
from .generation import GenerationBaseChanged, _digest, replace_native_generation
from .ingestion_issues import clear_issues
from .native_atoms import stage_atom_rows, validate_native_snapshot, write_staged_atoms
from .realization_projection import has_table


_CARRIER = re.compile(r"([A-Z][A-Z0-9]*-[STPC]-[0-9]+)(@[1-9][0-9]*(?:-draft)?)?[-.].*\.md\Z")
_EDGE = ("source_kind", "source_ref", "target_kind", "target_ref", "relation_type", "derived")


class DeltaReconciliationRequired(ValueError):
    """The retained state cannot safely receive a bounded delta."""


def _paths(value):
    if not isinstance(value, list) or not value or len(value) > 1024:
        raise ValueError("Native delta requires Ticket paths")
    result = set()
    for item in value:
        if not isinstance(item, list) or len(item) != 2 or any(not isinstance(part, str) for part in item):
            raise ValueError("Invalid Ticket path")
        parent, filename = item
        path = PurePosixPath(parent)
        if (path.is_absolute() or str(path) != parent or ".." in path.parts or "\\" in parent
                or not _CARRIER.fullmatch(filename) or "/" in filename or "\\" in filename):
            raise ValueError("Invalid Ticket path")
        result.add((parent, filename))
    if len(result) != len(value):
        raise ValueError("Duplicate Ticket path")
    return result


def _inverse(model, relation_types):
    endpoints = json.loads(model)["bindings"].get("endpoints")
    if not isinstance(endpoints, dict) or set(endpoints) != set(relation_types):
        raise ValueError("Snapshot relation types differ from the admitted Model")
    inverse = {}
    for name, entry in endpoints.items():
        if not isinstance(entry, list) or len(entry) != 2 or not isinstance(entry[0], dict) or type(entry[1]) is not bool:
            raise ValueError("Invalid Model relation binding")
        if not entry[1] and "inverse_alias" in entry[0]:
            target = entry[0]["inverse_alias"]
            if not isinstance(target, str) or target == name or target not in endpoints or name in inverse or target in inverse:
                raise ValueError("Ambiguous Model inverse binding")
            inverse[name], inverse[target] = target, name
    return inverse


def _validate_edges(rows, inverse):
    direct = Counter(tuple(row) for row in rows if not row[5])
    derived = Counter(tuple(row) for row in rows if row[5])
    expected = Counter()
    for (source_kind, source, target_kind, target, relation, _), count in direct.items():
        if relation in inverse:
            expected[(target_kind, target, source_kind, source, inverse[relation], True)] += count
    if derived != expected:
        raise DeltaReconciliationRequired("Ambiguous native relation ownership; full reconciliation required")


def _stage(connection, table, rows, width):
    for offset in range(0, len(rows), 256):
        batch = rows[offset:offset + 256]
        placeholders = ", ".join(["(" + ", ".join(["?"] * width) + ")"] * len(batch))
        connection.execute(f"INSERT INTO {table} VALUES {placeholders}", [value for row in batch for value in row])


def _old_rows(connection, paths, *, archive=False):
    connection.execute("CREATE TEMP TABLE int_delta_paths (relative_path VARCHAR, filename VARCHAR)")
    _stage(connection, "int_delta_paths", list(paths), 2)
    rows = connection.execute("""SELECT n.reference, n.exact_ref, n.relative_path, n.filename, n.status_group
        FROM main.mrt_atom_references n JOIN int_delta_paths p USING (relative_path, filename)""").fetchall()
    if (len({(row[2], row[3]) for row in rows}) != len(rows)
            or len({row[0] for row in rows}) != len(rows) or len({row[1] for row in rows}) != len(rows)):
        raise DeltaReconciliationRequired("Ambiguous Ticket path or identities; full reconciliation required")
    if archive and any(row[4] != "Archived" for row in rows):
        raise ValueError("Archive delta cannot replace live Atoms")
    return [(row[0], row[1]) for row in rows]


def _validate_delta(connection, data, model, manifest_sha256, *, archive=False):
    paths = _paths(data["paths"])
    snapshot = data["snapshot"]
    digest_data = {"paths": data["paths"], "snapshot": snapshot}
    if "carrier_hashes" in data:
        digest_data["carrier_hashes"] = data["carrier_hashes"]
    if _digest(digest_data) != data["snapshot_sha256"]:
        raise ValueError("Native delta digest mismatch")
    validate_native_snapshot(snapshot, manifest_sha256)
    if archive and (any("09_archived" not in PurePosixPath(parent).parts for parent, _ in paths)
                    or any(atom["status_group"] != "Archived" for atom in snapshot["atoms"])
                    or snapshot.get("spec_sizes") or snapshot.get("lifecycle_lenses")):
        raise ValueError("Archive delta requires canonical Archived carriers")
    inverse = _inverse(model, snapshot["relation_types"])
    for atom in snapshot["atoms"]:
        path = (atom["relative_path"], atom["filename"])
        match = _CARRIER.fullmatch(atom["filename"])
        if (path not in paths or not match or match.group(1) != atom["reference"].split("@")[0]
                or match.group(2) and match.group(1) + match.group(2) != atom["exact_ref"]):
            raise ValueError("Atom does not belong to an addressed native path")
    old = _old_rows(connection, paths, archive=archive)
    stage_atom_rows(connection, snapshot["atoms"])
    conflict = connection.execute("""SELECT 1 FROM (
        SELECT relative_path, filename FROM main.mrt_atom_references WHERE reference IN (SELECT reference FROM int_admission_atoms)
        UNION ALL
        SELECT relative_path, filename FROM main.mrt_atom_references WHERE exact_ref IN (SELECT exact_ref FROM int_admission_atoms)
        ) n WHERE NOT EXISTS (SELECT 1 FROM int_delta_paths p
            WHERE p.relative_path = n.relative_path AND p.filename = n.filename) LIMIT 1""").fetchone()
    if conflict:
        raise DeltaReconciliationRequired("Ticket identity was admitted at another path; reconcile both paths")
    new_edges = [tuple(edge[key] for key in _EDGE) for edge in snapshot["relations"]]
    _validate_edges(new_edges, inverse)
    return snapshot, old, new_edges, inverse


def _stage_owned_edges(connection, old, inverse):
    connection.execute("CREATE TEMP TABLE int_delta_old (reference VARCHAR)")
    _stage(connection, "int_delta_old", [(reference,) for reference, _ in old], 1)
    connection.execute("""CREATE TEMP TABLE int_delta_owned_edges AS
        SELECT r.* FROM main.mrt_atom_graph_relations r WHERE
        (NOT r.derived AND r.source_kind = 'Atom' AND r.source_ref IN (SELECT reference FROM int_delta_old)) OR
        (r.derived AND r.target_kind = 'Atom' AND r.target_ref IN (SELECT reference FROM int_delta_old))""")
    _validate_edges(connection.execute("SELECT * FROM int_delta_owned_edges").fetchall(), inverse)


def _write_atoms(connection):
    connection.execute("DELETE FROM main.mrt_atoms WHERE (relative_path, filename) IN (SELECT * FROM int_delta_paths)")
    connection.execute("DELETE FROM main.mrt_atom_references WHERE (relative_path, filename) IN (SELECT * FROM int_delta_paths)")
    write_staged_atoms(connection)


def _write_relations(connection, new_edges):
    connection.execute("""DELETE FROM main.mrt_atom_graph_relations WHERE
        (NOT derived AND source_kind = 'Atom' AND source_ref IN (SELECT reference FROM int_delta_old)) OR
        (derived AND target_kind = 'Atom' AND target_ref IN (SELECT reference FROM int_delta_old))""")
    connection.execute("CREATE TEMP TABLE int_delta_new_edges AS SELECT * FROM main.mrt_atom_graph_relations WHERE false")
    _stage(connection, "int_delta_new_edges", new_edges, 6)
    connection.execute("INSERT INTO main.mrt_atom_graph_relations SELECT * FROM int_delta_new_edges")


def _write_graph(connection, components):
    connection.execute("""CREATE TEMP TABLE int_delta_affected AS
        SELECT * FROM int_delta_owned_edges UNION SELECT * FROM int_delta_new_edges""")
    labels = connection.execute("""SELECT DISTINCT a.relation_type, l.ordinal FROM int_delta_affected a
        LEFT JOIN native_graph.int_labels l ON a.relation_type = l.name""").fetchall()
    if any(ordinal is None for _, ordinal in labels):
        raise DeltaReconciliationRequired("Native graph labels changed; full reconciliation required")
    connection.execute("""CREATE TEMP TABLE int_delta_vertices AS
        SELECT source_kind AS kind, source_ref AS ref FROM int_delta_affected
        UNION SELECT target_kind, target_ref FROM int_delta_affected
        UNION SELECT 'Atom', reference FROM int_delta_old
        UNION SELECT 'Atom', reference FROM int_admission_atoms""")
    connection.execute("INSERT INTO native_graph.int_reference SELECT * FROM int_delta_vertices ON CONFLICT DO NOTHING")
    for label, ordinal in labels:
        table = f'native_graph.int_relation_{int(ordinal)}'
        match = "r.source_kind = a.source_kind AND r.source_ref = a.source_ref AND r.target_kind = a.target_kind AND r.target_ref = a.target_ref AND r.derived = a.derived"
        connection.execute(f"DELETE FROM {table} r WHERE EXISTS (SELECT 1 FROM int_delta_affected a WHERE a.relation_type = ? AND {match})", [label])
        connection.execute(f"""INSERT INTO {table} SELECT DISTINCT a.source_kind, a.source_ref, a.target_kind, a.target_ref, a.derived
            FROM int_delta_affected a WHERE a.relation_type = ? AND EXISTS
            (SELECT 1 FROM main.mrt_atom_graph_relations r WHERE r.relation_type = a.relation_type AND {match})""", [label])
    connection.execute("CREATE TEMP TABLE int_delta_components (ref VARCHAR)")
    _stage(connection, "int_delta_components", [(ref,) for ref in components], 1)
    connection.execute("""DELETE FROM native_graph.int_reference v WHERE EXISTS
        (SELECT 1 FROM int_delta_vertices d WHERE d.kind = v.kind AND d.ref = v.ref)
        AND NOT (v.kind = 'Component' AND v.ref IN (SELECT ref FROM int_delta_components))
        AND NOT EXISTS (SELECT 1 FROM main.mrt_atom_references n WHERE v.kind = 'Atom' AND n.reference = v.ref)
        AND NOT EXISTS (SELECT 1 FROM main.mrt_atom_graph_relations r WHERE (r.source_kind = v.kind AND r.source_ref = v.ref)
                        OR (r.target_kind = v.kind AND r.target_ref = v.ref))""")


def _write_lenses(connection, snapshot):
    if has_table(connection, "main", "int_lifecycle_lenses"):
        if "lifecycle_lenses" in snapshot:
            connection.execute("DELETE FROM main.int_lifecycle_lenses WHERE reference IN (SELECT reference FROM int_delta_old)")
            _stage(connection, "main.int_lifecycle_lenses", snapshot["lifecycle_lenses"], 2)
        else:
            connection.execute("DROP TABLE main.int_lifecycle_lenses")
            connection.execute("DROP VIEW IF EXISTS main.lifecycle_lenses")


def apply_native_delta(connection, data, manifest_sha256, *, archive=False):
    from .archive_generation import archive_pending

    if "archive_pending" in data and (data["archive_pending"] is not True or "carrier_hashes" not in data):
        raise ValueError("Invalid startup archive transition")
    connection.execute("BEGIN TRANSACTION")
    try:
        rows = connection.execute("SELECT id, model, structure FROM ops_generation").fetchall()
        if (len(rows) != 1 or rows[0][0] != data["base_generation"]
                or not has_table(connection, "native_graph", "int_labels")
                or not has_table(connection, "main", "mrt_atom_graph_relations")
                or (archive and not archive_pending(connection))):
            raise GenerationBaseChanged("Generation base changed or is not native")
        base, model, structure = rows[0]
        snapshot, old, new_edges, inverse = _validate_delta(connection, data, model, manifest_sha256, archive=archive)
        update_checkpoint(connection, data, delta=True)
        _finish_delta(connection, data, archive)
        if not old and not snapshot["atoms"]:
            connection.execute("DROP TABLE int_delta_paths")
            connection.execute("DROP TABLE int_admission_atoms")
            connection.execute("COMMIT")
            return base
        _stage_owned_edges(connection, old, inverse)
        components = {"C00", *json.loads(structure)["components"]}
        if not archive:
            _write_lenses(connection, snapshot)
        _write_atoms(connection)
        _write_relations(connection, new_edges)
        if not archive and has_table(connection, "main", "biz_architecture_spec_metrics"):
            apply_spec_delta(connection, [exact for _, exact in old if "-S-" in exact], snapshot_sizes(snapshot))
        _write_graph(connection, components)
        generation = _digest({"kind": "native_ticket_delta", "base_generation": base,
                              "delta_sha256": data["snapshot_sha256"]})
        connection.execute("UPDATE ops_generation SET id = ?", [generation])
        for table in ("int_delta_paths", "int_delta_old", "int_admission_atoms", "int_delta_owned_edges",
                      "int_delta_new_edges", "int_delta_affected", "int_delta_vertices", "int_delta_components"):
            connection.execute(f"DROP TABLE {table}")
        connection.execute("COMMIT")
    except BaseException:
        connection.execute("ROLLBACK")
        raise
    return generation


def _finish_delta(connection, data, archive):
    from .archive_generation import set_archive_pending

    if archive:
        set_archive_pending(connection, False)
        clear_issues(connection, "archive")
    else:
        if data.get("archive_pending"):
            set_archive_pending(connection, True)
        clear_issues(connection, "atom", [str(PurePosixPath(parent) / name) for parent, name in data["paths"]])


def native_generation_route(connection, instance_id, manifest_sha256, lock, read_object, error_response):
    async def admit_native(request):
        try:
            delta = request.url.path.endswith("/native-delta")
            fields = {"instance_id", "base_generation", "snapshot", "snapshot_sha256"}
            allowed = fields | {"paths"} if delta else fields
            alternatives = (allowed,) if delta else (allowed, allowed | {"graph", "graph_sha256"},
                                                 allowed | {"graph", "graph_sha256", "reuse"})
            alternatives += tuple(fields | {"carrier_hashes"} for fields in alternatives)
            if delta:
                alternatives += (allowed | {"carrier_hashes", "archive_pending"},)
            data = await read_object(request, 64 * 1024 * 1024, *alternatives)
            if data["instance_id"] != instance_id:
                return error_response("foreign_instance", "Instance does not match", 403)
            with lock:
                generation = (apply_native_delta if delta else replace_native_generation)(connection, data, manifest_sha256)
            return JSONResponse({"result": {"generation": generation}})
        except GenerationBaseChanged as error:
            return error_response("generation_base_changed", str(error), 409)
        except DeltaReconciliationRequired as error:
            return error_response("delta_full_reconciliation", str(error), 409)
        except (ValueError, TypeError, UnicodeError, duckdb.Error) as error:
            return error_response("invalid_generation", str(error), 400)
    return admit_native


