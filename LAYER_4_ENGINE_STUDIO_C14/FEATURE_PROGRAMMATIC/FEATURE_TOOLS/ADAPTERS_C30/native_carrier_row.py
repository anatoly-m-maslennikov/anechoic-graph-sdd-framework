"""Parse one native carrier into source and containment rows."""

from pathlib import Path
import re

from .source_row__pub import atom, canonical_row
from .carrier_body__pub import source_body
from .atom_reference__pub import derive_atom_ref
from .native_carrier_header__pub import native_header_view
from .native_carrier_placement__pub import PROJECT_CONFIG_DIRECTORY, TICKET_DIRECTORY
from .carrier_read__pub import CarrierError, parse_carrier


CURRENT_STATUSES = {
    "S": {"active", "ready"}, "T": {"active", "in_queue", "backlog", "done", "canceled", "resolved", "complete"}, "P": {"active"}, "C": {"active"},
}


def _carrier_row(path: Path, root: Path, family: str, prefix: str, raw: bytes, *,
                 include_content_properties=True) -> tuple[dict, dict]:
    carrier = parse_carrier(raw, path)
    header = carrier.metadata
    canonical = "atom_family" in header
    try:
        normalized = native_header_view(header)
    except ValueError as error:
        raise CarrierError("NATIVE_HEADER_SCHEMA", str(error)) from error
    identity, context, state = (normalized.get(key) for key in ("identity", "context", "state"))
    if not all(isinstance(group, dict) for group in (identity, context, state)):
        raise CarrierError("NATIVE_HEADER_SCHEMA", "Native identity, context and state must be mappings")
    atom_id = identity.get("atom_id")
    pattern = rf"{re.escape(prefix)}-([STPC])-[0-9]+"
    match = re.fullmatch(pattern, atom_id) if isinstance(atom_id, str) else None
    version, status, container = state.get("version"), state.get("status"), context.get("container")
    if match is None or type(version) is not int or version < 1:
        raise ValueError("Invalid native Atom identity or version")
    if not canonical and match[1] not in family:
        raise ValueError("Native Atom family disagrees with its logical tree")
    if status in CURRENT_STATUSES[match[1]]:
        group = "Current"
    elif status in ("draft", "archived"):
        group = status.title()
    else:
        raise ValueError("Invalid native status for Atom family")
    exact = derive_atom_ref(atom_id, version, status)
    marker = atom_id if group == "Current" else exact
    if not canonical and (not path.name.startswith(marker + "-") or (
        group == "Archived" and path.name.startswith(exact + "-draft-")
    )):
        raise ValueError("Filename marker disagrees with native identity or status")
    kind, target = _container(container, atom_id, pattern)
    view = {"atom_id": atom_id, "version": version, "status": status,
            "tier": context.get("tier"), "updated_at": state.get("updated_at")}
    row = atom(path, root, header, view, source_body(raw, path), group,
               include_content_properties=include_content_properties)
    row["_source_bytes"] = len(raw)
    if group == "Current" and match[1] == "S":
        row["_source_lines"] = len(raw.splitlines())
    row["_exact_ref"] = exact
    canonical_row(row)
    edge = {"source_kind": "Atom", "source_ref": row["ref"], "relation_type": "CONTAINED_BY",
            "target_kind": kind.title(), "target_ref": target, "derived": False}
    return row, edge


def _container(container, atom_id: str, pattern: str) -> tuple[str, str]:
    if not isinstance(container, dict) or len(container) != 1:
        raise ValueError("Native container must identify one Component or Atom")
    kind, target = next(iter(container.items()))
    target_pattern = r"C[0-9]+" if kind == "component" else pattern
    if (kind not in {"component", "atom"} or not isinstance(target, str)
            or not re.fullmatch(target_pattern, target) or target == atom_id):
        raise ValueError("Invalid native container")
    return kind, target


def _parse_captured_carrier(selection, path, tree, raw, include_content_properties):
    family = {"_PMETA": "P", "__TKT": "T", "001_TICKETS": "T", "__TICKETS": "T",
              "002_PROJECT_CONFIG": "PC", "__PROJECT_CONFIG": "PC",
              PROJECT_CONFIG_DIRECTORY: "PC", TICKET_DIRECTORY: "T"}.get(tree, "S")
    row, edge = _carrier_row(path, selection.root, family, selection.project_prefix, raw,
                             include_content_properties=include_content_properties)
    if tree is None and path != selection.manifest_path:
        context = native_header_view(row["header_json"])["context"]
        if (row["status"] != "active" or context.get("template") != "project_goal"
                or context.get("container") != {"component": "C00"} or context.get("tier") != -1
                or context.get("lens") != "SPEC"
                or not path.name.startswith(row["id"] + "-")):
            raise ValueError("Invalid repository-root Project Goal")
    return row, edge

