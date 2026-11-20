"""Capture native carriers without interpreting legacy Scope Units or folders."""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import re
from typing import Any

from .source_rows import atom, canonical_row, source_body
from VALIDATE_ATOMS.validate_atoms_workers.parsing import CarrierError, parse_carrier
from VALIDATE_ATOMS.validate_atoms_workers.read_io import ReadContext
from VALIDATE_ATOMS.validate_atoms_workers.settings import CEILINGS


@dataclass(frozen=True)
class NativeCapture:
    atoms: list[dict[str, Any]]
    containment: list[dict[str, Any]]
    errors: dict[str, str]


CURRENT_STATUSES = {
    "S": {"active"}, "T": {"active", "backlog", "done", "canceled", "resolved"}, "P": {"active"},
}


def _carrier_row(path: Path, root: Path, family: str, prefix: str, raw: bytes) -> tuple[dict, dict]:
    carrier = parse_carrier(raw, path)
    header = carrier.metadata
    identity, context, state = (header.get(key) for key in ("identity", "context", "state"))
    if not all(isinstance(group, dict) for group in (identity, context, state)):
        raise ValueError("Native identity, context and state must be mappings")
    atom_id = identity.get("atom_id")
    pattern = rf"{re.escape(prefix)}-([STP])-[0-9]+"
    match = re.fullmatch(pattern, atom_id) if isinstance(atom_id, str) else None
    version, status, container = state.get("version"), state.get("status"), context.get("container")
    if match is None or type(version) is not int or version < 1:
        raise ValueError("Invalid native Atom identity or version")
    if match[1] != family:
        raise ValueError("Native Atom family disagrees with its logical tree")
    if status in CURRENT_STATUSES[match[1]]:
        group = "Current"
    elif status in ("draft", "archived"):
        group = status.title()
    else:
        raise ValueError("Invalid native status for Atom family")
    exact = f"{atom_id}@{version}" + ("-draft" if group == "Draft" else "")
    marker = atom_id if group == "Current" else exact
    if not path.name.startswith(marker + "-") or (
        group == "Archived" and path.name.startswith(exact + "-draft-")
    ):
        raise ValueError("Filename marker disagrees with native identity or status")
    kind, target = _container(container, atom_id, pattern)
    view = {"atom_id": atom_id, "version": version, "status": status,
            "tier": context.get("tier"), "updated_at": state.get("updated_at")}
    row = atom(path, root, header, view, source_body(raw, path), group)
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


def capture_native(selection: Any) -> NativeCapture:
    """Read one selected native tree. Callers must refuse a capture with errors."""
    root, control = selection.root, selection.control_root
    reader = ReadContext(roots=[str(control)], limits=dict(CEILINGS))
    if sha256(reader.read(selection.manifest_path)).hexdigest() != selection.manifest_sha256:
        raise ValueError("Selected native Project Manifest changed")
    paths = [path for path in reader.inventory(control) if path.suffix == ".md"]
    rows, containment, errors = [], [], {}
    exact_paths: dict[str, str] = {}
    current_paths: dict[str, str] = {}
    for path in paths:
        relative = path.relative_to(root).as_posix()
        try:
            tree = path.relative_to(control).parts[0]
            family = {"_PMETA": "P", "__TKT": "T"}.get(tree, "S")
            row, edge = _carrier_row(path, root, family, selection.project_prefix, reader.read(path))
            row["_source_sha256"] = reader.fingerprints[str(path)]
            exact, group, atom_id = row["_exact_ref"], row["status_group"], row["header_json"]["identity"]["atom_id"]
            if exact in exact_paths or (group == "Current" and atom_id in current_paths):
                raise ValueError("Duplicate native revision or Current identity")
            rows.append(row)
            containment.append(edge)
            exact_paths[exact] = relative
            if group == "Current":
                current_paths[atom_id] = relative
        except (OSError, RuntimeError, TypeError, ValueError, CarrierError) as error:
            errors[relative] = str(error)
    if reader.currentness()["state"] != "unchanged":
        raise ValueError("Native Project carriers changed during capture")
    return NativeCapture(rows, containment, errors)
