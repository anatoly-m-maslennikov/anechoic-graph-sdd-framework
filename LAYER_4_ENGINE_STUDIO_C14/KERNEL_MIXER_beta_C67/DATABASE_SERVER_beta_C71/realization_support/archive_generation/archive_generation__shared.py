"""Admit the deferred Archived population without replacing live rows."""

import json
from pathlib import PurePosixPath

import duckdb
from starlette.concurrency import run_in_threadpool
from starlette.responses import JSONResponse

from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.realization_support.model.accepted_model import generation_rows
from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.realization_support.archive_generation.archive_versions import archive_pending as archive_pending, refresh_archive_versions as refresh_archive_versions, seed_archive_versions as seed_archive_versions, backfill_archive_versions as backfill_archive_versions, update_archive_versions as update_archive_versions, set_archive_pending as set_archive_pending
from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.realization_support.archive_generation.archive_rows import _archive_fields as _archive_fields, _check_replacement_paths as _check_replacement_paths, _validate_archive_issues as _validate_archive_issues, _check_archive_duplicates as _check_archive_duplicates, _insert_edges as _insert_edges, _remove_canonical_archive as _remove_canonical_archive
from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.storage.checkpoint.checkpoint__shared import archive_checkpoint_paths, checkpoint_exists, update_checkpoint
from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.storage.generation.generation__shared import GenerationBaseChanged, _digest
from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.storage.generation.generation_batch import unpack_batch
from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.realization_support.delta.ingestion_issues import clear_archive_failure, duplicate_dependencies, replace_issues
from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.realization_support.native.native__shared import DuplicateNativeAtom, stage_atom_rows, validate_native_snapshot, write_staged_atoms
from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.realization_support.delta.delta__shared import DeltaReconciliationRequired, _inverse, _validate_edges, apply_native_delta
from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.realization_support.native.native_graph import replace_native_graph
from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.realization_projection import has_table, restore_property_graph


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
    keys = (
        "source_kind",
        "source_ref",
        "target_kind",
        "target_ref",
        "relation_type",
        "derived",
    )
    edges = [tuple(getattr(row, key) for key in keys) for row in relations]
    _validate_edges(edges, inverse)
    _check_replacement_paths(replacing, atoms, snapshot)
    return replacing


def _validate_archive(connection, snapshot, *, replacing):
    if replacing:
        _remove_canonical_archive(connection)
    stage_atom_rows(connection, snapshot["atoms"])
    collision = connection.execute("""SELECT 1 FROM main.mrt_atom_references n
        JOIN int_admission_atoms a USING (relative_path, filename) LIMIT
            1""").fetchone()
    if collision:
        raise ValueError("Archived Atom path collides with an admitted Atom")
    _validate_archive_issues(connection, snapshot)
    _check_archive_duplicates(connection, snapshot)


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


def _publish_archive(connection, data, row):
    generation = _digest(
        {
            "kind": "archive_complete",
            "base_generation": row[0],
            "snapshot_sha256": data["snapshot_sha256"],
        }
    )
    connection.execute("UPDATE ops_generation SET id = ?", [generation])
    refresh_archive_versions(connection)
    set_archive_pending(connection, False)
    replace_issues(
        connection, "archive", data["snapshot"].get("ingestion_issues", [])
    )
    connection.execute("DROP TABLE int_admission_atoms")
    return generation


def admit_archive(connection, data, binding, replacing):
    connection.execute("BEGIN TRANSACTION")
    graph_dropped = False
    try:
        row = next(iter(generation_rows(connection)), None)
        if (
            row is None
            or row != binding
            or row[0] != data["base_generation"]
            or not archive_pending(connection)
            or not has_table(connection, "native_graph", "int_labels")
        ):
            raise GenerationBaseChanged(
                "Generation base changed or archive is complete"
            )
        _validate_archive(connection, data["snapshot"], replacing=replacing)
        paths = _archive_checkpoint_paths(
            connection, data, replacing=replacing
        )
        update_checkpoint(connection, {**data, "paths": paths}, delta=True)
        write_staged_atoms(connection)
        _insert_edges(connection, data["snapshot"]["relations"])
        connection.execute("DROP PROPERTY GRAPH IF EXISTS anechoic")
        graph_dropped = True
        components = {"C00", *json.loads(row[2])["components"]}
        replace_native_graph(
            connection, data["snapshot"]["relation_types"], components
        )
        restore_property_graph(connection)
        generation = _publish_archive(connection, data, row)
        connection.execute("COMMIT")
        return generation
    except BaseException:
        connection.execute("ROLLBACK")
        if graph_dropped:
            restore_property_graph(connection)
        raise


async def _admit_full(connection, data, manifest_sha256, lock):
    with lock:
        binding = next(iter(generation_rows(connection)), None)
        if (
            binding is None
            or binding[0] != data["base_generation"]
            or not archive_pending(connection)
            or not has_table(connection, "native_graph", "int_labels")
        ):
            raise GenerationBaseChanged(
                "Generation base changed or archive is complete"
            )
    replacing = await run_in_threadpool(
        _prepare_archive, data, manifest_sha256, binding[1]
    )
    with lock:
        generation = admit_archive(connection, data, binding, replacing)
    return generation


def archive_route(
    connection, instance_id, manifest_sha256, lock, read_object, error_response
):
    async def admit(request):
        try:
            data = await read_object(
                request, 64 * 1024 * 1024, *_archive_fields()
            )
            if data["instance_id"] != instance_id:
                return error_response(
                    "foreign_instance", "Instance does not match", 403
                )
            if "paths" not in data and "unchanged" not in data:
                generation = await _admit_full(
                    connection, data, manifest_sha256, lock
                )
            else:
                with lock:
                    if "paths" in data:
                        generation = apply_native_delta(
                            connection, data, manifest_sha256, archive=True
                        )
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
