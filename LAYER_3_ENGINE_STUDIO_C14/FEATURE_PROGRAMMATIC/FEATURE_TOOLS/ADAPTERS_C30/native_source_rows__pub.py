"""Capture native carriers without interpreting legacy Scope Units or folders."""
from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
from pathlib import Path, PurePosixPath
import re
from typing import Any

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.source_row__pub import atom, canonical_row
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carrier_body__pub import source_body
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.atom_reference__pub import derive_atom_ref
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.native_carrier_header__pub import native_header_view
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.native_carrier_placement__pub import PROJECT_CONFIG_DIRECTORY, TICKET_DIRECTORY
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carrier_read__pub import CarrierError, parse_carrier
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__pub import CEILINGS, ReadContext


@dataclass(frozen=True)
class NativeCapture:
    atoms: list[dict[str, Any]]
    containment: list[dict[str, Any]]
    errors: dict[str, str]
    versions: dict[str, tuple[int, ...]] = field(default_factory=dict, compare=False)


class NativeManifestChanged(ValueError):
    """The capture no longer matches its validated Project Manifest."""


CURRENT_STATUSES = {
    "S": {"active", "ready"}, "T": {"active", "in_queue", "backlog", "done", "canceled", "resolved", "complete"}, "P": {"active"}, "C": {"active"},
}


def _carrier_row(path: Path, root: Path, family: str, prefix: str, raw: bytes) -> tuple[dict, dict]:
    carrier = parse_carrier(raw, path)
    header = carrier.metadata
    canonical = "atom_family" in header
    normalized = native_header_view(header)
    identity, context, state = (normalized.get(key) for key in ("identity", "context", "state"))
    if not all(isinstance(group, dict) for group in (identity, context, state)):
        raise ValueError("Native identity, context and state must be mappings")
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
    row = atom(path, root, header, view, source_body(raw, path), group)
    row["_source_bytes"] = len(raw)
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


def check_native_manifest(reader: ReadContext, selection: Any, previous: NativeCapture | None) -> bytes | None:
    try:
        raw = reader.read(selection.manifest_path, metadata_guard=previous is not None,
                          skip_version=previous.versions.get(str(selection.manifest_path)) if previous else None)
    except FileNotFoundError as error:
        raise NativeManifestChanged("Selected native Project Manifest moved or was removed") from error
    if raw is not None and sha256(raw).hexdigest() != selection.manifest_sha256:
        raise NativeManifestChanged("Selected native Project Manifest changed")
    return raw


def _changed_inputs(reader, root, control, previous, paths):
    scopes = set()
    for relative in paths:
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("Invalid changed carrier path")
        if (root / relative).is_relative_to(control):
            scopes.add(relative)
    changed, directories = set(), set()
    previous_paths = {row["source_path"] for row in previous.atoms} | previous.errors.keys()
    for relative in scopes:
        if any(parent in scopes for parent in relative.parents):
            continue
        path = root / relative
        name = relative.as_posix()
        changed.update(item for item in previous_paths if item.startswith(name + "/"))
        if relative.suffix == ".md":
            changed.add(name)
        if path.is_dir():
            directories.add(name)
            changed.update(item.relative_to(root).as_posix() for item in reader.inventory(path) if item.suffix == ".md")
    candidates = {row["source_path"]: (row, edge)
                  for row, edge in zip(previous.atoms, previous.containment)
                  if row["source_path"] not in changed}
    errors = {path: error for path, error in previous.errors.items() if path not in changed}
    return candidates, errors, [root / path for path in sorted(changed - directories)]


def _read_captured_carrier(reader, selection, path, tree, manifest, *, incremental, version):
    raw = manifest if path == selection.manifest_path else reader.read(
        path, metadata_guard=incremental, skip_version=version,
    )
    if raw is None:
        return None
    family = {"_PMETA": "P", "__TKT": "T", PROJECT_CONFIG_DIRECTORY: "PC", TICKET_DIRECTORY: "T"}.get(tree, "S")
    row, edge = _carrier_row(path, selection.root, family, selection.project_prefix, raw)
    row["_source_sha256"] = sha256(raw).hexdigest()
    return row, edge


def _incremental_carrier_present(reader: ReadContext, path: Path) -> bool:
    reader.allowed(path)
    try:
        path.lstat()
    except (FileNotFoundError, NotADirectoryError):
        return False
    return True


def capture_native(
    selection: Any, *, previous: NativeCapture | None = None,
    paths: set[PurePosixPath] | None = None,
) -> NativeCapture:
    """Read one selected native tree. Callers must refuse a capture with errors."""
    root, control = selection.root, selection.control_root
    reader = ReadContext(roots=[str(control)], limits=dict(CEILINGS))
    incremental = previous is not None and paths is not None
    manifest = check_native_manifest(reader, selection, previous if incremental else None)
    versions = dict(previous.versions) if incremental else {}
    previous_rows = {row["source_path"]: (row, edge)
                     for row, edge in zip(previous.atoms, previous.containment)} if incremental else {}
    missing = []
    if incremental:
        candidates, errors, input_paths = _changed_inputs(reader, root, control, previous, paths)
    else:
        candidates, errors = {}, {}
        input_paths = [path for path in reader.inventory(control) if path.suffix == ".md"]
    for path in input_paths:
        tree = path.relative_to(control).parts[0]
        if tree == "000_ANECHOIC_framework":
            continue
        relative = path.relative_to(root).as_posix()
        try:
            if incremental and not _incremental_carrier_present(reader, path):
                missing.append(path)
                versions.pop(str(path), None)
                continue
            captured = _read_captured_carrier(
                reader, selection, path, tree, manifest, incremental=incremental, version=versions.get(str(path)),
            )
            if captured is None:
                old = previous_rows.get(relative)
                if old is not None:
                    candidates[relative] = old
                elif relative in previous.errors:
                    errors[relative] = previous.errors[relative]
                continue
            candidates[relative] = captured
        except (OSError, RuntimeError, TypeError, ValueError, CarrierError) as error:
            errors[relative] = str(error)
    if reader.currentness()["state"] != "unchanged" or any(path.exists() or path.is_symlink() for path in missing):
        raise ValueError("Native Project carriers changed during capture")
    versions.update(reader.versions)
    return _unique_revisions(candidates, errors, versions)


def revalidate_native(selection: Any, previous: NativeCapture | None) -> NativeCapture:
    """Prove the indexed Atom population against disk before a write."""
    if previous is None or previous.errors:
        return capture_native(selection)
    control, root = selection.control_root, selection.root
    installed = control / "000_ANECHOIC_framework"
    reader = ReadContext(roots=[str(control)], limits=dict(CEILINGS))

    def versions():
        observed = {}
        paths = reader.inventory(control, remember=False, versions=observed)
        return {str(path): observed[str(path)] for path in paths
                if path.suffix == ".md" and not path.is_relative_to(installed)}

    before = versions()
    changed = {PurePosixPath(path).relative_to(root) for path in before.keys() | previous.versions.keys()
               if before.get(path) != previous.versions.get(path)}
    capture = capture_native(selection, previous=previous, paths=changed)
    if versions() != before:
        raise ValueError("Native Project carriers changed during capture")
    return capture


def _unique_revisions(candidates, errors, versions):
    rows, containment = [], []
    exact_paths: set[str] = set()
    current_paths: set[str] = set()
    for relative, (row, edge) in sorted(candidates.items()):
        exact, group, atom_id = row["_exact_ref"], row["status_group"], row["id"]
        if exact in exact_paths or (group == "Current" and atom_id in current_paths):
            errors[relative] = "Duplicate native revision or Current identity"
            continue
        rows.append(row)
        containment.append(edge)
        exact_paths.add(exact)
        if group == "Current":
            current_paths.add(atom_id)
    return NativeCapture(rows, containment, errors, versions)
