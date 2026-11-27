"""Read an admitted Atom's authored carrier within its bound Project."""

import json
from pathlib import Path, PurePosixPath
import re

from importlib import import_module

_adapters = import_module(
    "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared"
)
CEILINGS = _adapters.CEILINGS
ReadContext = _adapters.ReadContext
native_carrier_path = _adapters.native_carrier_path
native_header_view = _adapters.native_header_view
parse_carrier = _adapters.parse_carrier
source_body = _adapters.source_body
_lifecycle = import_module(
    "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.ATOM_LIFECYCLE__shared"
)
ticket_status_options = _lifecycle.ticket_status_options


FIELDS = import_module(".jobs", __package__).FIELDS
_query_rows = import_module(".lifecycle_queries", __package__)._query_rows

_REF = re.compile(r"[A-Z]+-[STPC]-[0-9]+(?:@[1-9][0-9]*(?:-draft)?)?")


def _error(code, message, status=400):
    return status, {"error": {"code": code, "message": message}}


def _sql(atom_id):
    """Build the query from a validated native Atom ID."""
    return (
        "WITH selected AS (\n      SELECT a.reference"
        ", n.exact_ref, a.relative_path, a.filename,"
        '\n        a."header.state.version" AS versio'
        'n, a."header.state.status" AS status, a.sta'
        'tus_group,\n        a."content.summary" AS s'
        "ummary\n      FROM main.atoms a JOIN main.na"
        "tive_references n ON a.reference=n.referenc"
        "e\n      WHERE split_part(n.exact_ref, '@', "
        f"1)='{atom_id}'\n    )\n    SELECT g.id,\n      coalesc"
        "e((SELECT to_json(list(struct_pack(ref_id :"
        "= reference, exact_ref := exact_ref,\n      "
        "  relative_path := relative_path, filename "
        ":= filename, version := version, status := "
        "status,\n        status_group := status_grou"
        "p, summary := summary)))::VARCHAR FROM sele"
        "cted), '[]'),\n      coalesce((SELECT to_jso"
        "n(list(struct_pack(type := relation_type,\n "
        "       source_kind := source_kind, source_r"
        "ef := source_ref, target_kind := target_kin"
        "d,\n        target_ref := target_ref, derive"
        "d := derived)))::VARCHAR FROM main.relation"
        "s\n        WHERE (source_kind='Atom' AND (so"
        "urce_ref IN (SELECT reference FROM selected"
        ")\n               OR source_ref IN (SELECT e"
        "xact_ref FROM selected)))\n           OR (ta"
        f"rget_kind='Atom' AND (target_ref='{atom_id}'\n      "
        "         OR target_ref IN (SELECT exact_ref"
        " FROM selected)))), '[]'),\n      coalesce(("
        "SELECT to_json(list(struct_pack(ref_id := a"
        ".reference, filename := a.filename)))::VARC"
        "HAR\n        FROM main.atoms a JOIN main.rel"
        "ations r ON r.source_kind='Atom' AND r.sour"
        "ce_ref=a.reference\n        WHERE r.target_k"
        f"ind='Atom' AND r.target_ref='{atom_id}' AND NOT r.d"
        "erived\n          AND r.relation_type IN ('I"
        "S_CONTAINED_BY', 'CONTAINED_BY')), '[]')\n  "
        "  FROM main.generation g"
    )


def _select(jobs, base, ref, atom_id):
    rows = _query_rows(
        jobs.database_socket, jobs.instance_id, _sql(atom_id), "Atom document"
    )
    if len(rows) != 1 or len(rows[0]) != 4 or rows[0][0] != base:
        raise ValueError("Generation changed during Atom document read")
    entries, relations, contained = map(json.loads, rows[0][1:])
    matches = [
        entry
        for entry in entries
        if (
            entry["exact_ref"] == ref
            if "@" in ref
            else entry["status_group"] == "Current"
        )
    ]
    if len(matches) != 1:
        return None, entries, relations, contained
    return matches[0], entries, relations, contained


def _carrier(jobs, item, atom_id):
    relative = PurePosixPath(item["relative_path"]) / item["filename"]
    if (
        relative.is_absolute()
        or ".." in relative.parts
        or len(PurePosixPath(item["filename"]).parts) != 1
        or not item["filename"].endswith(".md")
    ):
        raise ValueError("Invalid admitted carrier path")
    root = Path(jobs.binding["root"])
    path = root.joinpath(*relative.parts)
    reader = ReadContext(roots=[str(root)], limits=CEILINGS.copy())
    raw = reader.read(path)
    carrier = parse_carrier(raw, path)
    header = native_header_view(carrier.metadata)
    state = header["state"]
    if (
        header["identity"]["atom_id"] != atom_id
        or state["version"] != item["version"]
        or state["status"] != item["status"]
    ):
        raise ValueError("Carrier identity differs from admitted generation")
    return header, carrier.metadata, source_body(raw, path).decode("utf-8")


def _relations(relations, item):
    links = []
    aliases = {item["ref_id"], item["exact_ref"]}
    for edge in relations:
        if edge["source_kind"] == "Atom" and edge["source_ref"] in aliases:
            links.append(
                {
                    "type": edge["type"],
                    "ref_id": edge["target_ref"],
                    "direction": "outgoing",
                    "derived": edge["derived"],
                }
            )
        if edge["target_kind"] == "Atom" and edge["target_ref"] in aliases:
            links.append(
                {
                    "type": edge["type"],
                    "ref_id": edge["source_ref"],
                    "direction": "incoming",
                    "derived": edge["derived"],
                }
            )
    return links


def _filename(item, header):
    summary = item.get("summary")
    if not summary:
        return item["filename"]
    try:
        return native_carrier_path(
            header, summary, project_root="/", owner_directory="/"
        ).name
    except ValueError, TypeError, KeyError:
        return item["filename"]


def _history(entries):
    return [
        {
            "ref_id": entry["exact_ref"],
            "version": entry["version"],
            "status": entry["status"],
            "filename": entry["filename"],
        }
        for entry in sorted(
            entries,
            key=lambda row: (
                row["version"],
                row["status"],
                row["exact_ref"],
            ),
        )
    ]


def _value(
    item,
    entries,
    relations,
    contained,
    atom_id,
    header,
    metadata,
    body,
    pending,
):
    updated = header["state"].get("updated_at")
    value = {
        "ref_id": atom_id,
        "exact_ref": item["exact_ref"],
        "version": item["version"],
        "status": item["status"],
        "filename": _filename(item, metadata),
        "body": body,
        "template": header.get("context", {}).get("template"),
        "updated_at": updated.isoformat()
        if hasattr(updated, "isoformat")
        else updated,
        "history": _history(entries),
        "relations": _relations(relations, item),
        "contained": contained,
        "archive_pending": pending,
    }
    authored = metadata.get("relations")
    if item["status_group"] == "Draft" and isinstance(authored, dict):
        value["authored_relations"] = [
            {"type": relation, "ref_id": ref}
            for relation, refs in authored.items()
            if isinstance(relation, str) and isinstance(refs, list)
            for ref in refs
            if isinstance(ref, str)
        ]
    return value


def document(jobs, request):
    error = _validate_request(jobs, request)
    if error is not None:
        return error
    ref = request["ref_id"]
    atom_id = ref.partition("@")[0]
    with jobs.lock:
        base = jobs.live_generation
        pending = jobs.deferred_archive is not None or jobs.skip_archives
        reuse = jobs.generation_reuse
    if not base:
        return _error("workbench_unavailable", "No admitted generation", 503)
    try:
        item, entries, relations, contained = _select(jobs, base, ref, atom_id)
        if item is None:
            return _error(
                "atom_not_found",
                "Atom revision is unavailable or ambiguous",
                404,
            )
        header, metadata, body = _carrier(jobs, item, atom_id)
        value = _value(
            item,
            entries,
            relations,
            contained,
            atom_id,
            header,
            metadata,
            body,
            pending,
        )
        if "-T-" in atom_id and item["status_group"] == "Current":
            domains = (
                reuse.status_domains
                if reuse is not None and reuse.base_generation == base
                else None
            )
            value["ticket_statuses"] = ticket_status_options(metadata, domains)
        return 200, {"result": value}
    except ValueError, TypeError, KeyError, OSError, RuntimeError:
        return _document_unavailable()


def _validate_request(jobs, request):
    if not isinstance(request, dict) or set(request) != FIELDS | {"ref_id"}:
        return _error("invalid_request", "Invalid document fields")
    if request["instance_id"] != jobs.instance_id:
        return _error("instance_mismatch", "Instance does not match", 409)
    if {key: request[key] for key in FIELDS - {"instance_id"}} != jobs.binding:
        return _error("binding_mismatch", "Binding does not match", 409)
    ref = request["ref_id"]
    if not isinstance(ref, str) or not _REF.fullmatch(ref):
        return _error("invalid_request", "Invalid Atom reference")


def _document_unavailable():
    return _error(
        "workbench_unavailable", "Atom document is unavailable or changed", 503
    )
