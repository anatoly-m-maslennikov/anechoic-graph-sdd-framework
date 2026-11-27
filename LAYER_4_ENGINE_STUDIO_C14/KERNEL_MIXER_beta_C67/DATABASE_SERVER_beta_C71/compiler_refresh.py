(
    'Atomically refresh compiler artifacts against an accepted native '
    'generation.'
)

import json

import duckdb
from starlette.responses import JSONResponse

from .accepted_model import discard, generation_rows, prepare, publish
from .archive_generation import backfill_archive_versions, set_archive_pending
from .carrier_checkpoint import checkpoint_exists
from .generation import (
    FULL_GENERATION_BODY_LIMIT,
    GenerationBaseChanged,
    _HEX,
    _artifacts,
    _digest,
    _unique,
    _write_reuse,
)
from .model_projection import replace_model_projection
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import status_domains as _status_domains

from .native_atoms import NATIVE_PROJECTION_COLUMNS
from .native_delta import _inverse, apply_native_delta_in_transaction
from .project_structure import replace_structure
from .realization_projection import (
    _replace_test_projection,
    has_table,
    restore_property_graph,
)


class ModelColumnsChanged(ValueError):
    """The existing native tables do not match their projected DDL."""


def _check_columns(connection):
    for table, columns in NATIVE_PROJECTION_COLUMNS.items():
        actual = set(
            connection.execute(
                """SELECT column_name, data_type FROM information_schema.columns
            WHERE table_catalog = current_database() AND table_schema = 'main' AND table_name = ?""",
                [table],
            ).fetchall()
        )
        if actual != set(columns):
            raise ModelColumnsChanged(
                f"Native projected columns changed: {table}"
            )


def _compiler(data, manifest_sha256):
    if not isinstance(data, dict) or set(data) != {
        "receipt",
        "model",
        "structure",
    }:
        raise ValueError("Invalid compiler artifacts")
    receipt = data["receipt"]
    if (
        not isinstance(receipt, dict)
        or set(receipt)
        != {
            "manifest_sha256",
            "model_sha256",
            "model_descriptor_sha256",
            "structure_sha256",
        }
        or any(
            not isinstance(value, str) or _HEX.fullmatch(value) is None
            for value in receipt.values()
        )
        or receipt["manifest_sha256"] != manifest_sha256
    ):
        raise ValueError("Invalid compiler receipt")
    return _artifacts(data, receipt, manifest_sha256)


def _check_semantics(connection, old, descriptor):
    labels = [
        row[0]
        for row in connection.execute(
            "SELECT name FROM native_graph.int_labels ORDER BY ordinal"
        ).fetchall()
    ]
    old_bindings, bindings = (
        json.loads(old, object_pairs_hook=_unique)["bindings"],
        descriptor["bindings"],
    )
    old_inverse = _inverse(old_bindings, labels)
    inverse = _inverse(bindings, labels)
    if inverse != old_inverse or any(
        old_bindings["endpoints"][name][1] != bindings["endpoints"][name][1]
        for name in labels
    ):
        raise ValueError(
            (
                'Model inverse relations changed; native projection requires '
                'reconciliation'
            )
        )


def _check_status(connection, previous_model, descriptor):
    domains = _status_domains(descriptor["bindings"])
    if domains == _status_domains(
        json.loads(previous_model, object_pairs_hook=_unique)["bindings"]
    ):
        return
    rows = connection.execute(
        (
            "SELECT DISTINCT split_part(reference, '-', 2), "
            '"header.state.status" FROM main.mrt_atoms'
        )
    ).fetchall()
    if any(
        status not in domains.get(family, set()) for family, status in rows
    ):
        raise ValueError("Model Status domain excludes retained native Atoms")


def _components(connection, previous, structure):
    old = {
        "C00",
        *json.loads(previous, object_pairs_hook=_unique)["components"],
    }
    new = {"C00", *structure["components"]}
    if old == new:
        return False
    if has_table(connection, "main", "mrt_real_graph_test_edges"):
        targets = {
            row[0]
            for row in connection.execute(
                "SELECT target_key FROM main.mrt_real_graph_test_edges"
            ).fetchall()
        }
        if (old - new) & targets:
            raise ValueError(
                "Removed Component is referenced by the Realization Graph"
            )
    connection.execute("DROP PROPERTY GRAPH IF EXISTS anechoic")
    connection.execute(
        (
            "INSERT INTO native_graph.int_reference SELECT 'Component', "
            'unnest(?::VARCHAR[]) ON CONFLICT DO NOTHING'
        ),
        [sorted(new)],
    )
    connection.execute(
        """DELETE FROM native_graph.int_reference v WHERE v.kind = 'Component' AND v.ref IN (SELECT unnest(?::VARCHAR[]))
        AND NOT EXISTS (SELECT 1 FROM main.mrt_atom_graph_relations r WHERE
        (r.source_kind = v.kind AND r.source_ref = v.ref) OR (r.target_kind = v.kind AND r.target_ref = v.ref))""",
        [sorted(old - new)],
    )
    if has_table(connection, "main", "mrt_real_graph_import_nodes"):
        _replace_test_projection(connection, new)
    restore_property_graph(connection)
    return True


def _refresh_delta(data):
    if "archive_pending" in data and data["archive_pending"] is not True:
        raise ValueError("Invalid startup archive transition")
    delta = data.get("delta")
    if delta is not None and (
        not isinstance(delta, dict)
        or set(delta)
        != {"paths", "snapshot", "snapshot_sha256", "carrier_hashes"}
    ):
        raise ValueError("Invalid native delta fields")
    if "delta" in data and delta is None:
        raise ValueError("Invalid native delta fields")
    return delta


def refresh_compiler(connection, data, manifest_sha256):
    model, structure, descriptor, document = _compiler(
        data["compiler"], manifest_sha256
    )
    delta = _refresh_delta(data)
    connection.execute("BEGIN TRANSACTION")
    graph_changed = False
    pending_file = None
    try:
        rows = generation_rows(connection)
        if (len(rows) != 1 or rows[0][0] != data["base_generation"]
                or not has_table(connection, "native_graph", "int_labels")):
            raise GenerationBaseChanged("Generation base changed or is not native")
        base, previous_model, previous_structure = rows[0]
        _check_columns(connection)
        _check_semantics(connection, previous_model, descriptor)
        if data.get("archive_pending"):
            if not checkpoint_exists(connection):
                raise ValueError("Archive transition requires a retained carrier checkpoint")
            backfill_archive_versions(connection)
            set_archive_pending(connection, True)
        if delta is not None:
            apply_native_delta_in_transaction(connection, delta | {"base_generation": base}, manifest_sha256,
                                              base, model, structure)
        _check_status(connection, previous_model, descriptor)
        graph_changed = True
        _components(connection, previous_structure, document)
        replace_model_projection(connection, descriptor)
        replace_structure(connection, structure)
        _write_reuse(connection, data, model)
        generation = _digest({"kind": "compiler_refresh", "base_generation": base,
                              "receipt": data["compiler"]["receipt"], "delta_sha256": delta["snapshot_sha256"] if delta else None,
                              "archive_pending": data.get("archive_pending", False)})
        stored_model, pending_file = prepare(connection, model)
        connection.execute("UPDATE ops_generation SET id = ?, model = ?, structure = ?", [generation, stored_model, structure])
        connection.execute("COMMIT")
    except BaseException:
        connection.execute("ROLLBACK")
        discard(pending_file)
        if graph_changed:
            restore_property_graph(connection)
        raise
    publish(connection, model, pending_file)
    return generation


def compiler_refresh_route(
    connection, instance_id, manifest_sha256, lock, read_object, error_response
):
    async def admit(request):
        try:
            fields = {"instance_id", "base_generation", "compiler", "reuse"}
            data = await read_object(
                request,
                FULL_GENERATION_BODY_LIMIT,
                fields,
                fields | {"delta"},
                fields | {"archive_pending"},
                fields | {"delta", "archive_pending"},
            )
            if data["instance_id"] != instance_id:
                return error_response(
                    "foreign_instance", "Instance does not match", 403
                )
            with lock:
                generation = refresh_compiler(
                    connection, data, manifest_sha256
                )
            return JSONResponse({"result": {"generation": generation}})
        except OSError:
            return error_response(
                "model_publication_failed",
                "Accepted Model publication failed; reconciliation required",
                409,
            )
        except GenerationBaseChanged as error:
            return error_response("generation_base_changed", str(error), 409)
        except ModelColumnsChanged as error:
            return error_response("model_columns_changed", str(error), 409)
        except (
            ValueError,
            TypeError,
            KeyError,
            UnicodeError,
            duckdb.Error,
        ) as error:
            return error_response("invalid_generation", str(error), 400)

    return admit
