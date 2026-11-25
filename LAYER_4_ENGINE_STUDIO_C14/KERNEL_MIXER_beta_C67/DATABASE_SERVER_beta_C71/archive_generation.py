"""Admit the deferred Archived population without replacing live rows."""
import duckdb
from starlette.responses import JSONResponse

from .carrier_checkpoint import read_checkpoint, update_checkpoint
from .generation import GenerationBaseChanged, _digest
from .ingestion_issues import clear_issues
from .native_atoms import stage_atom_rows, validate_native_snapshot, write_staged_atoms
from .native_delta import DeltaReconciliationRequired, _inverse, _validate_edges, apply_native_delta
from .native_graph import replace_native_graph
from .realization_projection import has_table, restore_property_graph


def archive_pending(connection):
    if not has_table(connection, "main", "ops_archive_state"):
        return False
    row = connection.execute("SELECT pending FROM ops_archive_state").fetchone()
    return bool(row and row[0])


def set_archive_pending(connection, pending):
    connection.execute("CREATE TABLE IF NOT EXISTS ops_archive_state (pending BOOLEAN NOT NULL)")
    connection.execute("DELETE FROM ops_archive_state")
    connection.execute("INSERT INTO ops_archive_state VALUES (?)", [pending])


def change_archive_pending(connection, base, pending):
    connection.execute("BEGIN TRANSACTION")
    try:
        row = connection.execute("SELECT id FROM ops_generation").fetchone()
        if (row is None or row[0] != base or not has_table(connection, "native_graph", "int_labels")
                or (not pending and not archive_pending(connection))):
            raise GenerationBaseChanged("Generation base changed or archive is complete")
        if read_checkpoint(connection) is None:
            raise ValueError("Archive transition requires a retained carrier checkpoint")
        set_archive_pending(connection, pending)
        if not pending:
            clear_issues(connection, "archive")
        connection.execute("COMMIT")
        return row[0]
    except BaseException:
        connection.execute("ROLLBACK")
        raise


def _validate_archive(connection, data, manifest_sha256, model, *, replacing):
    snapshot = data["snapshot"]
    if _digest(snapshot) != data["snapshot_sha256"]:
        raise ValueError("Archive snapshot digest mismatch")
    validate_native_snapshot(snapshot, manifest_sha256)
    if any(row["status_group"] != "Archived" for row in snapshot["atoms"]):
        raise ValueError("Archive admission accepts only Archived Atoms")
    if snapshot.get("spec_sizes") or snapshot.get("lifecycle_lenses"):
        raise ValueError("Archive admission cannot replace live projections")
    inverse = _inverse(model, snapshot["relation_types"])
    keys = ("source_kind", "source_ref", "target_kind", "target_ref", "relation_type", "derived")
    edges = [tuple(row[key] for key in keys) for row in snapshot["relations"]]
    _validate_edges(edges, inverse)
    if replacing and any("09_archived" not in a["relative_path"].split("/") for a in snapshot["atoms"]):
        raise ValueError("Archive replacement requires canonical archive paths")
    removed = _remove_canonical_archive(connection) if replacing else []
    stage_atom_rows(connection, snapshot["atoms"])
    collision = connection.execute('''SELECT 1 FROM main.mrt_atom_references n
        JOIN int_admission_atoms a USING (reference)
        UNION ALL SELECT 1 FROM main.mrt_atom_references n
        JOIN int_admission_atoms a USING (exact_ref)
        UNION ALL SELECT 1 FROM main.mrt_atom_references n
        JOIN int_admission_atoms a USING (relative_path, filename) LIMIT 1''').fetchone()
    if collision:
        raise ValueError("Archived Atom collides with an admitted Atom")
    return edges, removed


def _insert_edges(connection, edges):
    keys = ("source_kind", "source_ref", "target_kind", "target_ref", "relation_type", "derived")
    values = [dict(zip(keys, row)) for row in edges]
    connection.execute('''INSERT INTO main.mrt_atom_graph_relations
        SELECT e.source_kind, e.source_ref, e.target_kind, e.target_ref, e.relation_type, e.derived
        FROM UNNEST(?::STRUCT(source_kind VARCHAR, source_ref VARCHAR, target_kind VARCHAR,
            target_ref VARCHAR, relation_type VARCHAR, derived BOOLEAN)[]) AS t(e)''', [values])


def _remove_canonical_archive(connection):
    connection.execute("""CREATE TEMP TABLE int_archive_replaced AS
        SELECT relative_path, filename, reference FROM main.mrt_atom_references
        WHERE status_group = 'Archived' AND list_contains(string_split(relative_path, '/'), '09_archived')""")
    paths = connection.execute("SELECT relative_path, filename FROM int_archive_replaced").fetchall()
    connection.execute("""DELETE FROM main.mrt_atom_graph_relations
        WHERE (NOT derived AND source_kind = 'Atom' AND source_ref IN (SELECT reference FROM int_archive_replaced))
        OR (derived AND target_kind = 'Atom' AND target_ref IN (SELECT reference FROM int_archive_replaced))""")
    for table in ("mrt_atoms", "mrt_atom_references"):
        connection.execute(f"""DELETE FROM main.{table}
            WHERE (relative_path, filename) IN (SELECT relative_path, filename FROM int_archive_replaced)""")
    connection.execute("DROP TABLE int_archive_replaced")
    return paths


def admit_archive(connection, data, manifest_sha256):
    connection.execute("BEGIN TRANSACTION")
    graph_dropped = False
    try:
        row = connection.execute("SELECT id, model FROM ops_generation").fetchone()
        if (row is None or row[0] != data["base_generation"] or not archive_pending(connection)
                or not has_table(connection, "native_graph", "int_labels")):
            raise GenerationBaseChanged("Generation base changed or archive is complete")
        replacing = data.get("replace", False)
        if type(replacing) is not bool:
            raise ValueError("Invalid archive replacement")
        edges, removed = _validate_archive(connection, data, manifest_sha256, row[1], replacing=replacing)
        if read_checkpoint(connection) is None:
            raise ValueError("Archive admission requires a retained carrier checkpoint")
        paths = [[a["relative_path"], a["filename"]] for a in data["snapshot"]["atoms"]]
        update_checkpoint(connection, {**data, "paths": [*removed, *paths]}, delta=True)
        write_staged_atoms(connection)
        _insert_edges(connection, edges)
        connection.execute("DROP PROPERTY GRAPH IF EXISTS anechoic")
        graph_dropped = True
        from .project_structure import component_ids
        components = component_ids(connection)
        replace_native_graph(connection, data["snapshot"]["relation_types"], components)
        restore_property_graph(connection)
        generation = _digest({"kind": "archive_complete", "base_generation": row[0],
                              "snapshot_sha256": data["snapshot_sha256"]})
        connection.execute("UPDATE ops_generation SET id = ?", [generation])
        set_archive_pending(connection, False)
        clear_issues(connection, "archive")
        connection.execute("DROP TABLE int_admission_atoms")
        connection.execute("COMMIT")
        return generation
    except BaseException:
        connection.execute("ROLLBACK")
        if graph_dropped:
            restore_property_graph(connection)
        raise


def archive_route(connection, instance_id, manifest_sha256, lock, read_object, error_response):
    async def admit(request):
        try:
            fields = {"instance_id", "base_generation", "snapshot", "snapshot_sha256", "carrier_hashes"}
            data = await read_object(request, 64 * 1024 * 1024, fields, fields | {"paths"},
                                     fields | {"replace"}, {"instance_id", "base_generation", "unchanged"})
            if data["instance_id"] != instance_id:
                return error_response("foreign_instance", "Instance does not match", 403)
            with lock:
                if "paths" in data:
                    generation = apply_native_delta(connection, data, manifest_sha256, archive=True)
                elif "unchanged" in data:
                    if data["unchanged"] is not True:
                        raise ValueError("Invalid unchanged archive result")
                    generation = change_archive_pending(connection, data["base_generation"], False)
                else:
                    generation = admit_archive(connection, data, manifest_sha256)
            return JSONResponse({"result": {"generation": generation}})
        except GenerationBaseChanged as error:
            return error_response("generation_base_changed", str(error), 409)
        except DeltaReconciliationRequired as error:
            return error_response("delta_full_reconciliation", str(error), 409)
        except (ValueError, TypeError, UnicodeError, duckdb.Error) as error:
            return error_response("invalid_generation", str(error), 400)
    return admit
