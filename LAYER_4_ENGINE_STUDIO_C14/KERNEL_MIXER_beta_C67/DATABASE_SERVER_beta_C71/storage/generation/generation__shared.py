"""Validate and atomically admit one Worker generation."""

import json
import re
from typing import Any

from pydantic import BaseModel, ConfigDict

from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.realization_support.model.accepted_model import discard, generation_rows, prepare, publish
from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.realization_support.model.analysis_projection import replace_spec, snapshot_sizes
from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.storage.checkpoint.checkpoint__shared import update_checkpoint
from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.realization_support.delta.ingestion_issues import clear_issues, replace_carrier_issues
from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.realization_support.native.native__shared import replace_native_atoms
from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.realization_support.native.native_graph import replace_native_graph
from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.realization_projection import has_table, replace, restore_property_graph, validate
from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.analysis_sql.query.table_names import sync_query_views
from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.realization_support.model.project_structure import replace_structure
from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.realization_support.model.model__shared import replace_model_diagnostics, replace_model_projection, validate_model_diagnostics

from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.storage.generation.generation_inputs import _artifacts as _artifacts, _HEX, _digest, _unique, _validate_generation, _validate_snapshot_binding, _write_reuse

FULL_GENERATION_BODY_LIMIT = 128 * 1024 * 1024


def _native_graph_payload(data, components, identity):
    if "graph" not in data:
        return None
    digest = data["graph_sha256"]
    if (
        not isinstance(data["graph"], dict)
        or not isinstance(digest, str)
        or _HEX.fullmatch(digest) is None
        or _digest(data["graph"]) != digest
    ):
        raise ValueError("Invalid graph or digest mismatch")
    graph = validate(data["graph"], components)
    identity["graph_sha256"] = digest
    return graph


def _archive_seed(data, pending):
    if "archive_versions" not in data:
        return None
    versions = data["archive_versions"]
    if (
        not pending
        or not isinstance(versions, dict)
        or len(versions) > 1_000_000
        or any(
            not isinstance(key, str)
            or re.fullmatch(r"[A-Z][A-Z0-9]*-[STPC]-[0-9]+", key) is None
            or type(value) is not int
            or not 0 < value <= 2**63 - 1
            for key, value in versions.items()
        )
    ):
        raise ValueError("Invalid archive version seed")
    return versions


def _replace_snapshot(
    connection,
    native,
    snapshot,
    components,
    *,
    archive_pending,
    archive_versions,
):
    if native:
        from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.realization_support.archive_generation.archive_generation__shared import backfill_archive_versions, refresh_archive_versions, seed_archive_versions

        if archive_pending:
            backfill_archive_versions(connection)
            seed_archive_versions(connection, archive_versions)
        replace_native_atoms(connection, snapshot)
        if not archive_pending:
            refresh_archive_versions(connection)
        replace_native_graph(
            connection, snapshot["relation_types"], components
        )
    else:
        connection.execute("DELETE FROM mrt_atoms")
        if atoms := snapshot["atoms"]:
            connection.executemany(
                "INSERT INTO mrt_atoms VALUES (?, ?)",
                [(a["reference"], a["summary"]) for a in atoms],
            )


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
    native, snapshot, model, structure, graph, components, descriptor = (
        _validate_generation(data, manifest_sha256)
    )
    diagnostics = (
        validate_model_diagnostics(
            data["model_diagnostics"], descriptor["model_sha256"]
        )
        if "model_diagnostics" in data
        else None
    )
    pending = data.get("archive_pending", False)
    if type(pending) is not bool or (
        pending
        and (
            not native
            or "carrier_hashes" not in data
            or any(
                row["status_group"] == "Archived" for row in snapshot["atoms"]
            )
        )
    ):
        raise ValueError("Invalid pending archive generation")
    versions = _archive_seed(data, pending)
    identity = {"receipt": data["receipt"], "snapshot": snapshot}
    if pending:
        identity["archive_pending"] = True
    if diagnostics is not None:
        identity["model_diagnostics"] = diagnostics
    return _PreparedGeneration.model_construct(
        native=native,
        snapshot=snapshot,
        model=model,
        structure=structure,
        graph=graph,
        components=components,
        descriptor=descriptor,
        diagnostics=diagnostics,
        pending=pending,
        versions=versions,
        generation=_digest(identity),
    )


def replace_generation(connection, data, prepared, *, stage_refresh=None):
    model = prepared.model
    if not prepared.native and has_table(
        connection, "main", "mrt_atom_graph_relations"
    ):
        raise ValueError(
            (
                "Cannot replace a native generation with the legacy snapshot "
                "format"
            )
        )
    pending_file = None
    connection.execute("BEGIN TRANSACTION")
    try:
        _replace_generation_projections(connection, prepared)
        stored_model, pending_file = prepare(connection, model)
        _store_generation_state(connection, data, prepared, stored_model)
        captured = stage_refresh() if stage_refresh is not None else None
        connection.execute("COMMIT")
    except BaseException:
        connection.execute("ROLLBACK")
        discard(pending_file)
        restore_property_graph(connection)
        raise
    publish(connection, model, pending_file)
    return prepared.generation, captured


def _replace_generation_projections(connection, prepared):
    connection.execute("DROP PROPERTY GRAPH IF EXISTS anechoic")
    _replace_snapshot(
        connection,
        prepared.native,
        prepared.snapshot,
        prepared.components,
        archive_pending=prepared.pending,
        archive_versions=prepared.versions,
    )
    replace(connection, prepared.graph, prepared.components)
    if prepared.native and has_table(
        connection, "main", "biz_architecture_spec_metrics"
    ):
        replace_spec(connection, snapshot_sizes(prepared.snapshot))
    connection.execute("DELETE FROM ops_generation")
    replace_model_projection(connection, prepared.descriptor)
    if prepared.diagnostics is not None:
        replace_model_diagnostics(connection, prepared.diagnostics)
    replace_structure(connection, prepared.structure)


def _store_generation_state(connection, data, prepared, stored_model):
    connection.execute(
        "INSERT INTO ops_generation VALUES (?, ?, ?)",
        [prepared.generation, stored_model, prepared.structure],
    )
    from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.realization_support.archive_generation.archive_generation__shared import set_archive_pending

    set_archive_pending(connection, prepared.pending)
    _write_reuse(connection, data, prepared.model)
    update_checkpoint(connection, data)
    replace_carrier_issues(
        connection, prepared.snapshot, archive_pending=prepared.pending
    )
    clear_issues(connection, "build")
    sync_query_views(connection)


class GenerationBaseChanged(ValueError):
    """The conditional native update no longer has its accepted base."""


def _finish_native_checkpoint(connection, data):
    from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.realization_support.archive_generation.archive_generation__shared import refresh_archive_versions, set_archive_pending

    refresh_archive_versions(connection)
    set_archive_pending(connection, False)
    update_checkpoint(connection, data)
    replace_carrier_issues(connection, data["snapshot"])
    clear_issues(connection, "build")


def replace_native_generation(connection, data, manifest_sha256):
    "Replace native rows and optionally the Realization Graph, retaining artifacts."
    connection.execute("BEGIN TRANSACTION")
    graph_dropped = False
    try:
        model, snapshot, components, graph, generation = (
            _prepare_native_refresh(connection, data, manifest_sha256)
        )
        connection.execute("DROP PROPERTY GRAPH IF EXISTS anechoic")
        graph_dropped = True
        replace_native_atoms(connection, snapshot)
        replace_native_graph(
            connection, snapshot["relation_types"], components
        )
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


def _prepare_native_refresh(connection, data, manifest_sha256):
    rows = generation_rows(connection)
    if (
        len(rows) != 1
        or rows[0][0] != data["base_generation"]
        or not has_table(connection, "native_graph", "int_labels")
        or not has_table(connection, "main", "mrt_atom_graph_relations")
    ):
        raise GenerationBaseChanged("Generation base changed or is not native")
    base, model, structure = rows[0]
    snapshot, digest = data["snapshot"], data["snapshot_sha256"]
    if (
        not isinstance(digest, str)
        or _HEX.fullmatch(digest) is None
        or _digest(snapshot) != digest
    ):
        raise ValueError("Native snapshot digest mismatch")
    bindings = json.loads(model, object_pairs_hook=_unique)["bindings"]
    _validate_snapshot_binding(snapshot, manifest_sha256, bindings)
    components = {
        "C00",
        *json.loads(structure, object_pairs_hook=_unique)["components"],
    }
    identity = {
        "kind": "native_snapshot_refresh",
        "base_generation": base,
        "snapshot_sha256": digest,
    }
    graph = _native_graph_payload(data, components, identity)
    generation = _digest(identity)
    return model, snapshot, components, graph, generation
