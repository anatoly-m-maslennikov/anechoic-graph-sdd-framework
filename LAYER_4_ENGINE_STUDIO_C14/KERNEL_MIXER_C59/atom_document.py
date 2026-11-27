"""Read the authored carrier of one admitted native Atom revision."""

from hashlib import sha256
from pathlib import PurePosixPath

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    CEILINGS,
    LimitReached,
    ReadContext,
    native_carrier_path,
    native_header_view,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.atom_reference__pub import (
    is_native_atom_reference,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.markdown_content__pub import (
    summary_title,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.ATOM_LIFECYCLE__shared import (
    ticket_status_options,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__shared import (
    ExplicitBlockingRuntimeFailure,
)


def _revision(row):
    return {
        "ref_id": row["_exact_ref"],
        "version": row["version"],
        "status": row["status"],
        "filename": PurePosixPath(row["source_path"]).name,
    }


def _confirmed_body(root, row):
    relative = PurePosixPath(row["source_path"])
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError("Invalid admitted carrier path")
    reader = ReadContext(roots=[str(root)], limits=dict(CEILINGS))
    raw = reader.read(root.joinpath(*relative.parts))
    if sha256(raw).hexdigest() != row["_source_sha256"]:
        raise ValueError("Admitted carrier changed")
    return row["_content_bytes"]


def _filename(row, body):
    title = summary_title(body)
    if title:
        try:
            return native_carrier_path(
                row["header_json"],
                title,
                project_root="/",
                owner_directory="/",
            ).name
        except (ValueError, TypeError, KeyError):
            pass
    return PurePosixPath(row["source_path"]).name


def _links(store, row):
    ref, exact = row["ref"], row["_exact_ref"]
    aliases = {ref, exact}
    with store._lock:
        edges = store._connection.execute(
            "SELECT source_kind, source_ref, target_kind, target_ref, "
            "relation_type, derived FROM main.relations "
            "WHERE (source_kind = 'Atom' AND source_ref IN (?, ?)) "
            "OR (target_kind = 'Atom' AND target_ref IN (?, ?))",
            [ref, exact, ref, exact],
        ).fetchall()
        children = store._connection.execute(
            "SELECT a.reference, a.filename FROM main.atoms a "
            "JOIN main.relations r ON r.source_kind = 'Atom' "
            "AND r.source_ref = a.reference "
            "WHERE r.target_kind = 'Atom' AND r.target_ref = ? "
            "AND NOT r.derived AND r.relation_type "
            "IN ('IS_CONTAINED_BY', 'CONTAINED_BY') "
            "ORDER BY a.reference, a.filename",
            [row["id"]],
        ).fetchall()
    relations = []
    for source_kind, source, target_kind, target, name, derived in edges:
        if source_kind == "Atom" and source in aliases:
            relations.append(
                {
                    "type": name,
                    "ref_id": target,
                    "direction": "outgoing",
                    "derived": derived,
                }
            )
        if target_kind == "Atom" and target in aliases:
            relations.append(
                {
                    "type": name,
                    "ref_id": source,
                    "direction": "incoming",
                    "derived": derived,
                }
            )
    return relations, [
        {"ref_id": child, "filename": name} for child, name in children
    ]


def atom_document(root, store, capture, ref):
    if not is_native_atom_reference(ref):
        raise ExplicitBlockingRuntimeFailure(
            "tool_input_invalid", "Invalid Atom reference"
        )
    atom_id, exact_lookup, _ = ref.partition("@")
    entries = [row for row in capture.atoms if row["id"] == atom_id]
    matches = [
        row
        for row in entries
        if (
            row["_exact_ref"] == ref
            if exact_lookup
            else row["status_group"] == "Current"
        )
    ]
    if len(matches) != 1:
        raise ExplicitBlockingRuntimeFailure(
            "atom_not_found", "Atom revision is unavailable or ambiguous"
        )
    row = matches[0]
    try:
        body = _confirmed_body(root, row)
    except (OSError, LimitReached, RuntimeError, ValueError) as error:
        raise ExplicitBlockingRuntimeFailure(
            "workbench_unavailable", "Atom document is unavailable or changed"
        ) from error

    metadata = row["header_json"]
    header = native_header_view(metadata)
    updated = row["updated_at"]
    relations, contained = _links(store, row)
    value = {
        "ref_id": atom_id,
        "exact_ref": row["_exact_ref"],
        "version": row["version"],
        "status": row["status"],
        "filename": _filename(row, body),
        "body": body.decode("utf-8"),
        "template": header["context"].get("template"),
        "updated_at": updated.isoformat()
        if hasattr(updated, "isoformat")
        else updated,
        "history": sorted(
            map(_revision, entries),
            key=lambda entry: (
                entry["version"],
                entry["status"],
                entry["ref_id"],
            ),
        ),
        "relations": relations,
        "contained": contained,
        "archive_pending": False,
    }
    if row["status_group"] == "Draft" and isinstance(
        metadata.get("relations"), dict
    ):
        value["authored_relations"] = [
            {"type": name, "ref_id": target}
            for name, targets in metadata["relations"].items()
            for target in targets
        ]
    if row["status_group"] == "Current" and "-T-" in atom_id:
        value["ticket_statuses"] = ticket_status_options(
            metadata, capture.status_domains
        )
    return value
