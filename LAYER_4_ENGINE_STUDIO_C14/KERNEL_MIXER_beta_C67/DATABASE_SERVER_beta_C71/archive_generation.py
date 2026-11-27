"""Admit the deferred Archived population without replacing live rows."""
import json
from pathlib import PurePosixPath

import duckdb
from starlette.concurrency import run_in_threadpool
from starlette.responses import JSONResponse

from .accepted_model import generation_rows
from .carrier_checkpoint import (
    archive_checkpoint_paths,
    checkpoint_exists,
    update_checkpoint,
)
from .generation import GenerationBaseChanged, _digest
from .generation_batch import unpack_batch
from .ingestion_issues import (
    archive_path,
    clear_archive_failure,
    duplicate_dependencies,
    replace_issues,
)
from .native_atoms import (
    DuplicateNativeAtom,
    stage_atom_rows,
    validate_native_snapshot,
    write_staged_atoms,
)
from .native_delta import (
    DeltaReconciliationRequired,
    _inverse,
    _validate_edges,
    apply_native_delta,
)
from .native_graph import replace_native_graph
from .realization_projection import has_table, restore_property_graph


def archive_pending(connection):
    if not has_table(connection, "main", "ops_archive_state"):
        return False
    row = connection.execute(
        "SELECT pending FROM ops_archive_state"
    ).fetchone()
    return bool(row and row[0])


def refresh_archive_versions(connection):
    connection.execute("""CREATE TABLE IF NOT EXISTS main.ops_archive_versions
        (atom_id VARCHAR PRIMARY KEY, max_version BIGINT NOT NULL)""")
    connection.execute("DELETE FROM main.ops_archive_versions")
    connection.execute("""INSERT INTO main.ops_archive_versions
        SELECT split_part(reference, '@', 1), max("header.state.version")
        FROM main.mrt_atoms WHERE status_group = 'Archived' GROUP BY 1""")


def seed_archive_versions(connection, versions):
    if versions is None or has_table(
        connection, "main", "ops_archive_versions"
    ):
        return
    connection.execute("""CREATE TABLE main.ops_archive_versions
        (atom_id VARCHAR PRIMARY KEY, max_version BIGINT NOT NULL)""")
    if versions:
        connection.execute(
            """INSERT INTO main.ops_archive_versions
            SELECT unnest(?::VARCHAR[]), unnest(?::BIGINT[])""",
            [list(versions), list(versions.values())],
        )


def backfill_archive_versions(connection):
    if (
        not has_table(connection, "main", "ops_archive_versions")
        and not archive_pending(connection)
        and has_table(connection, "main", "mrt_atom_references")
    ):
        refresh_archive_versions(connection)


def update_archive_versions(connection, old, atoms):
    """Preserve admitted maxima until the full Archive history is available."""
    affected = {ref.partition('@')[0] for ref, _ in old if '@' in ref and not ref.endswith('-draft')}
    affected.update(row['reference'].partition('@')[0] for row in atoms if row['status_group'] == 'Archived')
    if not affected or not has_table(connection, "main", "ops_archive_versions"):
        return
    if archive_pending(connection):
        connection.execute("""INSERT INTO main.ops_archive_versions
            SELECT split_part(reference, '@', 1), max("header.state.version")
            FROM int_admission_atoms WHERE status_group = 'Archived' GROUP BY 1
            ON CONFLICT (atom_id) DO UPDATE SET max_version = greatest(ops_archive_versions.max_version, excluded.max_version)""")
        return
    ids = [sorted(affected)]
    connection.execute("DELETE FROM main.ops_archive_versions WHERE atom_id IN (SELECT unnest(?))", ids)
    connection.execute("""INSERT INTO main.ops_archive_versions
        SELECT split_part(reference, '@', 1), max("header.state.version") FROM main.mrt_atoms
        WHERE status_group = 'Archived' AND split_part(reference, '@', 1) IN (SELECT unnest(?)) GROUP BY 1""", ids)


def set_archive_pending(connection, pending):
    connection.execute("CREATE TABLE IF NOT EXISTS ops_archive_state (pending BOOLEAN NOT NULL)")
    connection.execute("DELETE FROM ops_archive_state")
    connection.execute("INSERT INTO ops_archive_state VALUES (?)", [pending])


def change_archive_pending(connection, base, pending):
    connection.execute("BEGIN TRANSACTION")
    try:
        row = connection.execute("SELECT id FROM ops_generation").fetchone()
        if (
            row is None
            or row[0] != base
            or not has_table(connection, "native_graph", "int_labels")
            or (not pending and not archive_pending(connection))
        ):
            raise GenerationBaseChanged(
                "Generation base changed or archive is complete"
            )
        if not checkpoint_exists(connection):
            raise ValueError(
                "Archive transition requires a retained carrier checkpoint"
            )
        if pending:
            backfill_archive_versions(connection)
        set_archive_pending(connection, pending)
        if not pending:
            clear_archive_failure(connection)
        connection.execute("COMMIT")
        return row[0]
    except BaseException:
        connection.execute("ROLLBACK")
        raise


def _prepare_archive(data, manifest_sha256, model):
    replacing = data.get("replace", False)
    if type(replacing) is not bool:
        raise ValueError("Invalid archive replacement")
    if "batch_artifact" in data:
        unpack_batch(data, "anechoic-archive-")
        if data.pop("graph") is not None:
            raise ValueError(
                "Archive admission cannot replace the Realization Graph"
            )
    snapshot = data["snapshot"]
    if _digest(snapshot) != data["snapshot_sha256"]:
        raise ValueError("Archive snapshot digest mismatch")
    bindings = json.loads(model)["bindings"]
    try:
        atoms, relations = validate_native_snapshot(
            snapshot, manifest_sha256, bindings
        )
    except DuplicateNativeAtom as error:
        raise DeltaReconciliationRequired(
            "Archive snapshot contains a duplicate Atom group"
        ) from error
    if any(row.status_group != "Archived" for row in atoms):
        raise ValueError("Archive admission accepts only Archived Atoms")
    if snapshot.get("spec_sizes") or snapshot.get("lifecycle_lenses"):
        raise ValueError("Archive admission cannot replace live projections")
    inverse = _inverse(bindings, snapshot["relation_types"])
    keys = ("source_kind", "source_ref", "target_kind", "target_ref", "relation_type", "derived")
    edges = [tuple(getattr(row, key) for key in keys) for row in relations]
    _validate_edges(edges, inverse)
    if replacing and any(
        "09_archived" not in a.relative_path.split("/") for a in atoms
    ):
        raise ValueError(
            "Archive replacement requires canonical archive paths"
        )
    paths = [
        row["relative_path"] for row in snapshot.get("ingestion_issues", [])
    ]
    if replacing and any(not archive_path(path) for path in paths):
        raise ValueError(
            "Archive replacement requires canonical archive issue paths"
        )
    return replacing


def _validate_archive(connection, snapshot, *, replacing):
    if replacing:
        _remove_canonical_archive(connection)
    stage_atom_rows(connection, snapshot["atoms"])
    collision = connection.execute('''SELECT 1 FROM main.mrt_atom_references n
        JOIN int_admission_atoms a USING (relative_path, filename) LIMIT 1''').fetchone()
    if collision:
        raise ValueError("Archived Atom path collides with an admitted Atom")
    _validate_archive_issues(connection, snapshot)
    _check_archive_duplicates(connection, snapshot)


def _validate_archive_issues(connection, snapshot):
    paths = [row["relative_path"] for row in snapshot.get("ingestion_issues", [])]
    if paths and connection.execute("""SELECT 1 FROM main.mrt_atom_references
            WHERE concat(CASE WHEN relative_path = '.' THEN '' ELSE relative_path || '/' END, filename)
            IN (SELECT unnest(?)) LIMIT 1""", [paths]).fetchone():
        raise ValueError("Archive issue path collides with an admitted Atom")


def _check_archive_duplicates(connection, snapshot):
    excluded = [
        row["atom_ref"]
        for row in snapshot.get("ingestion_issues", [])
        if row["code"] == "duplicate_revision"
    ]
    collision = connection.execute(
        """SELECT 1 FROM main.mrt_atom_references n
        JOIN int_admission_atoms a USING (reference)
        UNION ALL SELECT 1 FROM main.mrt_atom_references n JOIN int_admission_atoms a USING (exact_ref)
        UNION ALL SELECT 1 FROM main.mrt_atom_references n
        WHERE exact_ref IN (SELECT unnest(?::VARCHAR[])) LIMIT 1""",
        [excluded],
    ).fetchone()
    if collision or duplicate_dependencies(connection, snapshot, set()):
        raise DeltaReconciliationRequired(
            "Archive Atom collides with another Atom phase"
        )


def _insert_edges(connection, edges):
    connection.execute('''INSERT INTO main.mrt_atom_graph_relations
        SELECT e.source_kind, e.source_ref, e.target_kind, e.target_ref, e.relation_type, e.derived
        FROM UNNEST(?::STRUCT(source_kind VARCHAR, source_ref VARCHAR, target_kind VARCHAR,
            target_ref VARCHAR, relation_type VARCHAR, derived BOOLEAN)[]) AS t(e)''', [edges])


def _remove_canonical_archive(connection):
    connection.execute("""CREATE TEMP TABLE int_archive_replaced AS
        SELECT relative_path, filename, reference FROM main.mrt_atom_references
        WHERE status_group = 'Archived' AND list_contains(string_split(relative_path, '/'), '09_archived')""")
    connection.execute("""DELETE FROM main.mrt_atom_graph_relations
        WHERE (NOT derived AND source_kind = 'Atom' AND source_ref IN (SELECT reference FROM int_archive_replaced))
        OR (derived AND target_kind = 'Atom' AND target_ref IN (SELECT reference FROM int_archive_replaced))""")
    for table in ("mrt_atoms", "mrt_atom_references"):
        connection.execute(f"""DELETE FROM main.{table}
            WHERE (relative_path, filename) IN (SELECT relative_path, filename FROM int_archive_replaced)""")
    connection.execute("DROP TABLE int_archive_replaced")


def _archive_checkpoint_paths(connection, data, *, replacing):
    if not checkpoint_exists(connection):
        raise ValueError(
            "Archive admission requires a retained carrier checkpoint"
        )
    snapshot = data["snapshot"]
    paths = set(data["carrier_hashes"])
    if replacing:
        removed = archive_checkpoint_paths(connection)
        if duplicate_dependencies(connection, snapshot, removed):
            raise DeltaReconciliationRequired(
                "Archive replacement touches a duplicate Atom group"
            )
        paths.update(removed)
    return [
        [PurePosixPath(path).parent.as_posix(), PurePosixPath(path).name]
        for path in sorted(paths)
    ]


def admit_archive(connection, data, binding, replacing):
    connection.execute("BEGIN TRANSACTION")
    graph_dropped = False
    try:
        row = next(iter(generation_rows(connection)), None)
        if (row is None or row != binding or row[0] != data["base_generation"] or not archive_pending(connection)
                or not has_table(connection, "native_graph", "int_labels")):
            raise GenerationBaseChanged("Generation base changed or archive is complete")
        _validate_archive(connection, data["snapshot"], replacing=replacing)
        paths = _archive_checkpoint_paths(connection, data, replacing=replacing)
        update_checkpoint(connection, {**data, "paths": paths}, delta=True)
        write_staged_atoms(connection)
        _insert_edges(connection, data["snapshot"]["relations"])
        connection.execute("DROP PROPERTY GRAPH IF EXISTS anechoic")
        graph_dropped = True
        components = {"C00", *json.loads(row[2])["components"]}
        replace_native_graph(connection, data["snapshot"]["relation_types"], components)
        restore_property_graph(connection)
        generation = _digest({"kind": "archive_complete", "base_generation": row[0],
                              "snapshot_sha256": data["snapshot_sha256"]})
        connection.execute("UPDATE ops_generation SET id = ?", [generation])
        refresh_archive_versions(connection)
        set_archive_pending(connection, False)
        replace_issues(connection, "archive", data["snapshot"].get("ingestion_issues", []))
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
            batch = (fields - {"snapshot", "carrier_hashes"}) | {"batch_artifact"}
            data = await read_object(request, 64 * 1024 * 1024, fields, fields | {"paths"},
                                     fields | {"replace"}, batch, batch | {"replace"},
                                     {"instance_id", "base_generation", "unchanged"})
            if data["instance_id"] != instance_id:
                return error_response("foreign_instance", "Instance does not match", 403)
            if "paths" not in data and "unchanged" not in data:
                with lock:
                    binding = next(iter(generation_rows(connection)), None)
                    if (binding is None or binding[0] != data["base_generation"]
                            or not archive_pending(connection)
                            or not has_table(connection, "native_graph", "int_labels")):
                        raise GenerationBaseChanged("Generation base changed or archive is complete")
                replacing = await run_in_threadpool(_prepare_archive, data, manifest_sha256, binding[1])
                with lock:
                    generation = admit_archive(connection, data, binding, replacing)
            else:
                with lock:
                    if "paths" in data:
                        generation = apply_native_delta(connection, data, manifest_sha256, archive=True)
                    else:
                        if data["unchanged"] is not True:
                            raise ValueError(
                                "Invalid unchanged archive result"
                            )
                        generation = change_archive_pending(
                            connection, data["base_generation"], False
                        )
            return JSONResponse({"result": {"generation": generation}})
        except GenerationBaseChanged as error:
            return error_response("generation_base_changed", str(error), 409)
        except DeltaReconciliationRequired as error:
            return error_response("delta_full_reconciliation", str(error), 409)
        except (ValueError, TypeError, UnicodeError, duckdb.Error) as error:
            return error_response("invalid_generation", str(error), 400)
    return admit
