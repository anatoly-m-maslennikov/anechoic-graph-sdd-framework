"""Replace addressed native carriers atomically without a graph rebuild."""

import json
from pathlib import PurePosixPath

import duckdb
from starlette.responses import JSONResponse

from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.realization_support.model.accepted_model import generation_rows
from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.realization_support.model.analysis_projection import apply_spec_delta, snapshot_sizes
from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.storage.checkpoint.checkpoint__shared import update_checkpoint
from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.storage.generation.generation__shared import FULL_GENERATION_BODY_LIMIT, GenerationBaseChanged, _digest, replace_native_generation
from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.realization_support.delta.ingestion_issues import clear_archive_failure, replace_carrier_issues
from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.realization_support.native.pending_graph import replace_pending_graph
from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.realization_support.delta.native_delta_validation import DeltaReconciliationRequired as DeltaReconciliationRequired, _CARRIER as _CARRIER, _EDGE as _EDGE, _paths as _paths, _inverse as _inverse, _validate_edges as _validate_edges, _stage as _stage, _old_rows as _old_rows, _validate_atom_paths as _validate_atom_paths, _check_conflicts as _check_conflicts, _validate_delta as _validate_delta, _validate_delta_issues as _validate_delta_issues
from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.realization_support.delta.native_delta_rows import _write_atoms as _write_atoms, _write_relations as _write_relations, _prune_vertices as _prune_vertices

from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.realization_projection import has_table


def _stage_owned_edges(connection, old, inverse):
    connection.execute("CREATE TEMP TABLE int_delta_old (reference VARCHAR)")
    _stage(
        connection, "int_delta_old", [(reference,) for reference, _ in old], 1
    )
    connection.execute("""CREATE TEMP TABLE int_delta_owned_edges AS
        SELECT r.* FROM main.mrt_atom_graph_relations r WHERE
        (NOT r.derived AND r.source_kind = 'Atom' AND r.source_ref IN (SELECT
            reference FROM int_delta_old)) OR
        (r.derived AND r.target_kind = 'Atom' AND r.target_ref IN (SELECT
            reference FROM int_delta_old))""")
    _validate_edges(
        connection.execute("SELECT * FROM int_delta_owned_edges").fetchall(),
        inverse,
    )


def _write_graph(connection, components):
    connection.execute("""CREATE TEMP TABLE int_delta_affected AS
        SELECT * FROM int_delta_owned_edges UNION SELECT * FROM
            int_delta_new_edges""")
    labels = connection.execute("""SELECT DISTINCT a.relation_type, l.ordinal
        FROM int_delta_affected a
        LEFT JOIN native_graph.int_labels l ON a.relation_type =
            l.name""").fetchall()
    if any(ordinal is None for _, ordinal in labels):
        raise DeltaReconciliationRequired(
            "Native graph labels changed; full reconciliation required"
        )
    connection.execute("""CREATE TEMP TABLE int_delta_vertices AS
        SELECT source_kind AS kind, source_ref AS ref FROM int_delta_affected
        UNION SELECT target_kind, target_ref FROM int_delta_affected
        UNION SELECT 'Atom', reference FROM int_delta_old
        UNION SELECT 'Atom', reference FROM int_admission_atoms""")
    connection.execute(
        (
            "INSERT INTO native_graph.int_reference SELECT * FROM int_delta_v"
            "ertices ON CONFLICT DO NOTHING"
        )
    )
    for label, ordinal in labels:
        table = f"native_graph.int_relation_{int(ordinal)}"
        match = (
            "r.source_kind = a.source_kind AND r.source_ref = a.sourc"
            "e_ref AND r.target_kind = a.target_kind AND r.target_ref"
            " = a.target_ref AND r.derived = a.derived"
        )
        connection.execute(
            f"DELETE FROM {table} r WHERE EXISTS (SELECT 1 FROM int_delta_"
            f"affected a WHERE a.relation_type = ? AND {match})",
            [label],
        )
        connection.execute(
            f"""INSERT INTO {table}
            SELECT DISTINCT a.source_kind, a.source_ref, a.target_kind,
                a.target_ref, a.derived
            FROM int_delta_affected a WHERE a.relation_type = ? AND EXISTS
            (SELECT 1 FROM main.mrt_atom_graph_relations r
             WHERE r.relation_type = a.relation_type AND {match})""",
            [label],
        )
    _prune_vertices(connection, components)


def _write_lenses(connection, snapshot):
    if has_table(connection, "main", "int_lifecycle_lenses"):
        if "lifecycle_lenses" in snapshot:
            connection.execute(
                (
                    "DELETE FROM main.int_lifecycle_lenses WHERE reference IN"
                    " (SELECT reference FROM int_delta_old)"
                )
            )
            _stage(
                connection,
                "main.int_lifecycle_lenses",
                snapshot["lifecycle_lenses"],
                2,
            )
        else:
            connection.execute("DROP TABLE main.int_lifecycle_lenses")
            connection.execute("DROP VIEW IF EXISTS main.lifecycle_lenses")


def _drop_delta_tables(connection):
    for table in (
        "int_delta_paths",
        "int_delta_old",
        "int_admission_atoms",
        "int_delta_owned_edges",
        "int_delta_new_edges",
        "int_delta_affected",
        "int_delta_vertices",
        "int_delta_components",
    ):
        connection.execute(f"DROP TABLE {table}")


def apply_native_delta_in_transaction(
    connection, data, manifest_sha256, base, model, structure, *, archive=False
):
    """Apply a validated delta in the caller's transaction."""
    from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.realization_support.archive_generation.archive_generation__shared import backfill_archive_versions

    if data.get("archive_pending"):
        backfill_archive_versions(connection)
    snapshot, old, new_edges, inverse = _validate_delta(
        connection, data, model, manifest_sha256, archive=archive
    )
    generation = _delta_generation(base, data["snapshot_sha256"])
    update_checkpoint(connection, data, delta=True)
    if not old and not snapshot["atoms"]:
        changed = _finish_delta(
            connection, data, archive, old, check_changes=True
        )
        if changed:
            connection.execute(
                "UPDATE ops_generation SET id = ?", [generation]
            )
        connection.execute("DROP TABLE int_delta_paths")
        connection.execute("DROP TABLE int_admission_atoms")
        return generation if changed else base
    _stage_owned_edges(connection, old, inverse)
    components = {"C00", *json.loads(structure)["components"]}
    if not archive:
        _write_lenses(connection, snapshot)
    _write_atoms(connection)
    _finish_delta(connection, data, archive, old)
    _write_relations(connection, new_edges)
    if not archive and has_table(
        connection, "main", "biz_architecture_spec_metrics"
    ):
        apply_spec_delta(
            connection,
            [exact for _, exact in old if "-S-" in exact],
            snapshot_sizes(snapshot),
        )
    _write_graph(connection, components)
    connection.execute("UPDATE ops_generation SET id = ?", [generation])
    _drop_delta_tables(connection)
    return generation


def apply_native_delta(connection, data, manifest_sha256, *, archive=False):
    from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.realization_support.archive_generation.archive_generation__shared import archive_pending

    if "archive_pending" in data and (
        data["archive_pending"] is not True or "carrier_hashes" not in data
    ):
        raise ValueError("Invalid startup archive transition")
    connection.execute("BEGIN TRANSACTION")
    try:
        rows = generation_rows(connection)
        if (
            len(rows) != 1
            or rows[0][0] != data["base_generation"]
            or not has_table(connection, "native_graph", "int_labels")
            or not has_table(connection, "main", "mrt_atom_graph_relations")
            or (archive and not archive_pending(connection))
        ):
            raise GenerationBaseChanged(
                "Generation base changed or is not native"
            )
        generation = apply_native_delta_in_transaction(
            connection, data, manifest_sha256, *rows[0], archive=archive
        )
        connection.execute("COMMIT")
    except BaseException:
        connection.execute("ROLLBACK")
        raise
    return generation


def _delta_generation(base, digest):
    return _digest(
        {
            "kind": "native_ticket_delta",
            "base_generation": base,
            "delta_sha256": digest,
        }
    )


def _finish_delta(connection, data, archive, old, *, check_changes=False):
    from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.realization_support.archive_generation.archive_generation__shared import refresh_archive_versions, set_archive_pending, update_archive_versions

    snapshot = data["snapshot"]
    paths = [
        str(PurePosixPath(parent) / name) for parent, name in data["paths"]
    ]
    changed = bool(snapshot.get("ingestion_issues"))
    if check_changes and not changed:
        changed = connection.execute(
            """SELECT EXISTS (SELECT 1 FROM main.ops_ingestion_issues
            WHERE source IN ('atom', 'archive') AND relative_path IN (SELECT
                unnest(?)))""",
            [paths],
        ).fetchone()[0]
    replace_carrier_issues(connection, snapshot, paths=paths)
    if archive:
        set_archive_pending(connection, False)
        clear_archive_failure(connection)
    elif data.get("archive_pending"):
        set_archive_pending(connection, True)
    if archive and not has_table(connection, "main", "ops_archive_versions"):
        refresh_archive_versions(connection)
    else:
        update_archive_versions(connection, old, snapshot["atoms"])
    return changed


def _request_fields(delta):
    fields = {
        "instance_id",
        "base_generation",
        "snapshot",
        "snapshot_sha256",
    }
    allowed = fields | {"paths"} if delta else fields
    alternatives = (
        (allowed,)
        if delta
        else (
            allowed,
            allowed | {"graph", "graph_sha256"},
            allowed | {"graph", "graph_sha256", "reuse"},
        )
    )
    alternatives += tuple(
        fields | {"carrier_hashes"} for fields in alternatives
    )
    if not delta:
        graph_only = {
            "instance_id",
            "base_generation",
            "graph",
            "graph_sha256",
            "reuse",
        }
        alternatives += (graph_only, graph_only | {"force_graph"})
    if delta:
        alternatives += (allowed | {"carrier_hashes", "archive_pending"},)
    return alternatives


def native_generation_route(
    connection, instance_id, manifest_sha256, lock, read_object, error_response
):
    async def admit_native(request):
        try:
            delta = request.url.path.endswith("/native-delta")
            alternatives = _request_fields(delta)
            limit = 64 * 1024 * 1024 if delta else FULL_GENERATION_BODY_LIMIT
            data = await read_object(request, limit, *alternatives)
            if data["instance_id"] != instance_id:
                return error_response(
                    "foreign_instance", "Instance does not match", 403
                )
            with lock:
                generation = (
                    replace_pending_graph(connection, data)
                    if "snapshot" not in data
                    else (
                        apply_native_delta
                        if delta
                        else replace_native_generation
                    )(connection, data, manifest_sha256)
                )
            return JSONResponse({"result": {"generation": generation}})
        except GenerationBaseChanged as error:
            return error_response("generation_base_changed", str(error), 409)
        except DeltaReconciliationRequired as error:
            return error_response("delta_full_reconciliation", str(error), 409)
        except (ValueError, TypeError, UnicodeError, duckdb.Error) as error:
            return error_response("invalid_generation", str(error), 400)

    return admit_native
