"""Select generation-pinned lifecycle context from the private database."""

from contextlib import closing
import json
from pathlib import PurePosixPath
import re

from ORCHESTRATOR_beta_C68.jobs import UnixConnection
from ORCHESTRATOR_beta_C68.lifecycle._lifecycle_sql import _allocation_references, lifecycle_sql

_CUSTOM_MODEL_ROOTS = frozenset(
    PurePosixPath(directory, "CUSTOM_MODEL")
    for directory in ("__PROJECT_CONFIG", "002_PROJECT_CONFIG")
)


def ticket_allocation(
    socket_path,
    instance_id,
    base_generation,
    prefix,
    *,
    archive_versions=False,
):
    if re.fullmatch(r"[A-Z][A-Z0-9]*", prefix) is None:
        raise ValueError("Invalid Project prefix")
    sql = f"""WITH allocation_refs AS ({_allocation_references(archive_versions)}), numbers AS (
        SELECT ltrim(regexp_extract(reference, '^{prefix}-T-([0-9]+)(@|$)', 1), '0') AS number
        FROM allocation_refs WHERE starts_with(reference, '{prefix}-T-')
    )
    SELECT id, coalesce(nullif((SELECT arg_max(number, (length(number), number)) FROM numbers), ''), '0'),
        json_extract(model, '$.ticket_labels')::VARCHAR
    FROM main.int_lifecycle_generation"""
    rows = _query_rows(socket_path, instance_id, sql, "Ticket allocation")
    if (
        not isinstance(rows, list)
        or len(rows) != 1
        or not isinstance(rows[0], list)
        or len(rows[0]) != 3
        or rows[0][0] != base_generation
    ):
        raise ValueError("Kernel generation changed before Ticket allocation")
    number = rows[0][1]
    if (
        not isinstance(number, str)
        or re.fullmatch(r"0|[1-9][0-9]*", number) is None
    ):
        raise ValueError("Kernel returned an invalid Ticket number")
    if rows[0][2] is None:
        raise ValueError("The admitted Model lacks Ticket label rules")
    labels = json.loads(rows[0][2])
    if not isinstance(labels, list) or not all(
        isinstance(label, str) for label in labels
    ):
        raise ValueError("Kernel returned invalid Ticket label rules")
    return number, labels


def _query_rows(socket_path, instance_id, sql, purpose):
    request = json.dumps({"instance_id": instance_id, "sql": sql})
    with closing(UnixConnection(socket_path)) as connection:
        connection.request(
            "POST", "/database", request, {"Content-Type": "application/json"}
        )
        response = connection.getresponse()
        payload = json.loads(response.read())
        if response.status != 200:
            message = payload.get("error", {}).get("message", "query failed")
            raise ValueError(
                f"Kernel refused {purpose}: {str(message)[:1024]}"
            )
        return payload["result"]["rows"]


def archive_versions_available(socket_path, instance_id):
    sql = """SELECT EXISTS (SELECT 1 FROM duckdb_tables() WHERE database_name=current_database()
        AND schema_name='main' AND table_name='ops_archive_versions')"""
    return _query_rows(
        socket_path, instance_id, sql, "Archive version checkpoint"
    ) == [[True]]


def lifecycle_context(
    socket_path,
    instance_id,
    base,
    prefix,
    name,
    arguments,
    *,
    archive_versions=False,
):
    sql = lifecycle_sql(
        prefix, name, arguments, archive_versions=archive_versions
    )
    rows = _query_rows(
        socket_path, instance_id, sql, "lifecycle context query"
    )
    if (
        not isinstance(rows, list)
        or len(rows) != 1
        or len(rows[0]) != 10
        or rows[0][0] != base
    ):
        raise ValueError(
            "Kernel generation changed before lifecycle context query"
        )
    return _decode_lifecycle_context(rows[0])


def _decode_lifecycle_context(row):
    (
        _,
        structure,
        model,
        labels,
        ticket,
        spec,
        carriers,
        descendants,
        lenses,
        archived_version,
    ) = row
    model = json.loads(model) if model is not None else None
    structure, labels, carriers, lenses = map(
        json.loads, (structure, labels, carriers, lenses)
    )
    if not _valid_context(
        structure,
        model,
        labels,
        carriers,
        lenses,
        descendants,
        (ticket, spec, archived_version),
    ):
        raise ValueError("Kernel returned invalid lifecycle context")
    return {
        "structure": structure,
        "model": model,
        "ticket_labels": labels,
        "max_numbers": {"T": ticket, "S": spec},
        "carriers": carriers,
        "has_descendants": descendants,
        "lenses": lenses,
        "max_archived_version": int(archived_version),
    }


def _valid_context(
    structure, model, labels, carriers, lenses, descendants, versions
):
    return not (
        not isinstance(structure, dict)
        or model is not None
        and not isinstance(model, dict)
        or not isinstance(labels, list)
        or not all(isinstance(x, str) for x in labels)
        or not isinstance(carriers, list)
        or not isinstance(lenses, list)
        or not all(isinstance(x, str) for x in lenses)
        or type(descendants) is not bool
        or any(
            not isinstance(x, str) or not re.fullmatch(r"0|[1-9][0-9]*", x)
            for x in versions
        )
    )


def requires_project_capture(job, context, control):
    target = job.arguments.get("target")
    ref = target.get("ref_id") if isinstance(target, dict) else None
    operation = job.name
    if not isinstance(ref, str):
        return False
    if "-T-" in ref:
        return context["has_descendants"] and operation in {
            "atom_lifecycle_promote_draft",
            "atom_lifecycle_change_status",
        }
    if operation not in {
        "atom_lifecycle_promote_draft",
        "atom_lifecycle_change_status",
        "atom_lifecycle_archive",
    }:
        return False
    return _requires_spec_capture(job, context, control, ref, operation)


def _requires_spec_capture(job, context, control, ref, operation):
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model.model__shared import (
        is_ontology_model_source,
        ontology_component_path,
    )

    atom_id = ref.partition("@")[0]
    archiving_spec = "-S-" in atom_id and (
        operation == "atom_lifecycle_archive"
        or (
            operation == "atom_lifecycle_change_status"
            and job.arguments.get("targetStatus") == "archived"
        )
    )
    control_path = PurePosixPath(control)

    for carrier in context["carriers"]:
        if carrier["id"] != atom_id:
            continue
        try:
            path = PurePosixPath(carrier["source_path"]).relative_to(
                control_path
            )
        except ValueError:
            continue
        plain_des_archive = (
            archiving_spec
            and path.parent.name == "_DES"
            and path.name.startswith(f"{atom_id}-DES--")
        )
        active_model = (
            not plain_des_archive and is_ontology_model_source(path)
        ) or path.parent in _CUSTOM_MODEL_ROOTS
        scope = ontology_component_path(path)
        if (carrier["status"] == "active" and active_model) or (
            job.arguments.get("targetStatus") == "active"
            and (
                scope is not None
                or any(
                    path.is_relative_to(root) for root in _CUSTOM_MODEL_ROOTS
                )
            )
        ):
            return True
    return False


def needs_exact_archive(job, context):
    target = job.arguments.get("target")
    ref = target.get("ref_id") if isinstance(target, dict) else None
    if not isinstance(ref, str):
        return False
    will_archive = (
        job.name == "atom_lifecycle_archive"
        and not ref.endswith("-draft")
        or job.name == "atom_lifecycle_change_status"
        and job.arguments.get("targetStatus") == "archived"
    )
    if not will_archive and job.name != "atom_lifecycle_promote_draft":
        return False
    atom_id = ref.partition("@")[0]
    return any(
        row["read"]
        and row["id"] == atom_id
        and row["version"] <= context["max_archived_version"]
        for row in context["carriers"]
    )
