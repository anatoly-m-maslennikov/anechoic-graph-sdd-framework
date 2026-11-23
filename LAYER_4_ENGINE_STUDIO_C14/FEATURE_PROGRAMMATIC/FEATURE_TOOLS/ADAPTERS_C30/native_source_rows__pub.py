"""Capture native carriers without interpreting legacy Scope Units or folders."""
from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
from itertools import groupby
import os
from pathlib import Path, PurePosixPath
import re
from typing import Any

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.source_row__pub import atom, canonical_row
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carrier_body__pub import source_body
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.atom_reference__pub import derive_atom_ref
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.native_carrier_header__pub import native_header_view
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.native_carrier_placement__pub import (
    PROJECT_CONFIG_DIRECTORY, TICKET_DIRECTORY, project_goal_filename,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carrier_read__pub import CarrierError, parse_carrier
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__pub import CEILINGS, ReadContext, open_regular


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


def _carrier_row(path: Path, root: Path, family: str, prefix: str, raw: bytes, *,
                 include_content_properties=True) -> tuple[dict, dict]:
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


def check_native_manifest(reader: ReadContext, selection: Any, previous: NativeCapture | None) -> bytes | None:
    try:
        raw = reader.read(selection.manifest_path, metadata_guard=previous is not None,
                          skip_version=previous.versions.get(str(selection.manifest_path)) if previous else None)
    except FileNotFoundError as error:
        raise NativeManifestChanged("Selected native Project Manifest moved or was removed") from error
    if raw is not None and sha256(raw).hexdigest() != selection.manifest_sha256:
        raise NativeManifestChanged("Selected native Project Manifest changed")
    return raw


def _changed_inputs(reader, selection, previous, paths):
    root, control = selection.root, selection.control_root
    scopes = set()
    for relative in paths:
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("Invalid changed carrier path")
        if ((root / relative).is_relative_to(control) or root / relative == selection.manifest_path
                or (relative.parent == PurePosixPath('.') and project_goal_filename(relative.name))):
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


def _read_captured_carrier(reader, selection, path, tree, manifest, *, version, directory_fd,
                           include_content_properties):
    raw = manifest if path == selection.manifest_path else reader.read(
        path, metadata_guard=True, skip_version=version, directory_fd=directory_fd,
    )
    if raw is None:
        return None
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
    row["_source_sha256"] = sha256(raw).hexdigest()
    return row, edge


def _incremental_carrier_present(reader: ReadContext, path: Path) -> bool:
    reader.allowed(path)
    try:
        path.lstat()
    except (FileNotFoundError, NotADirectoryError):
        return False
    return True


def _root_carriers(reader, selection, *, remember=True):
    return [path for path in reader.inventory_shallow(selection.root, remember=remember)
            if path == selection.manifest_path or project_goal_filename(path.name)]


def _capture_inputs(reader, selection, input_paths, manifest, incremental, previous,
                    previous_rows, candidates, errors, versions, missing, directory_fd=None, *,
                    include_content_properties):
    root, control = selection.root, selection.control_root
    for path in input_paths:
        tree = path.relative_to(control).parts[0] if path.is_relative_to(control) else None
        if tree == "000_ANECHOIC_framework":
            continue
        relative = path.relative_to(root).as_posix()
        try:
            if incremental and not _incremental_carrier_present(reader, path):
                missing.append(path)
                versions.pop(str(path), None)
                continue
            captured = _read_captured_carrier(
                reader, selection, path, tree, manifest, version=versions.get(str(path)), directory_fd=directory_fd,
                include_content_properties=include_content_properties,
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


def _full_carriers(reader, selection):
    installed = selection.control_root / "000_ANECHOIC_framework"
    paths = [path for path in reader.inventory(selection.control_root)
             if path.suffix == ".md" and not path.is_relative_to(installed)]
    return sorted(set(paths + _root_carriers(reader, selection)))


def _native_carrier_hashes(selection):
    reader = ReadContext(roots=[str(selection.root)], limits=dict(CEILINGS))
    manifest = check_native_manifest(reader, selection, None)
    hashes = {}
    for path in _full_carriers(reader, selection):
        raw = manifest if path == selection.manifest_path else reader.read(path, metadata_guard=True)
        hashes[path.relative_to(selection.root).as_posix()] = sha256(raw).hexdigest()
    if reader.currentness()["state"] != "unchanged":
        raise ValueError("Native Project carriers changed during capture")
    return hashes


def _capture_full_inputs(reader, selection, manifest, candidates, errors, *, include_content_properties):
    paths = _full_carriers(reader, selection)
    for directory, members in groupby(sorted(paths, key=lambda path: (path.parent, path.name)),
                                      key=lambda path: path.parent):
        try:
            descriptor = open_regular(reader.allowed(directory), directory=True)
        except OSError:
            descriptor = None
        try:
            _capture_inputs(reader, selection, members, manifest, False, None,
                            {}, candidates, errors, {}, [], directory_fd=descriptor,
                            include_content_properties=include_content_properties)
        finally:
            if descriptor is not None:
                os.close(descriptor)


def capture_native(
    selection: Any, *, previous: NativeCapture | None = None,
    paths: set[PurePosixPath] | None = None, reader: ReadContext | None = None,
    include_content_properties: bool = True, manifest_admitted: bool = False,
) -> NativeCapture:
    """Read one selected native tree. Callers must refuse a capture with errors."""
    if reader is None:
        reader = ReadContext(roots=[str(selection.root)], limits=dict(CEILINGS))
    incremental = previous is not None and paths is not None
    if manifest_admitted and (not incremental or selection.manifest_path.relative_to(selection.root) in paths):
        raise ValueError("Manifest admission requires addressed non-Manifest paths")
    manifest = None if manifest_admitted else check_native_manifest(reader, selection, previous if incremental else None)
    versions = dict(previous.versions) if incremental else {}
    previous_rows = {row["source_path"]: (row, edge)
                     for row, edge in zip(previous.atoms, previous.containment)} if incremental else {}
    missing = []
    if incremental:
        candidates, errors, input_paths = _changed_inputs(reader, selection, previous, paths)
        _capture_inputs(reader, selection, input_paths, manifest, incremental, previous,
                        previous_rows, candidates, errors, versions, missing,
                        include_content_properties=include_content_properties)
    else:
        candidates, errors = {}, {}
        _capture_full_inputs(reader, selection, manifest, candidates, errors,
                             include_content_properties=include_content_properties)
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
    reader = ReadContext(roots=[str(root)], limits=dict(CEILINGS))

    def versions():
        observed = {}
        paths = reader.inventory(control, remember=False, versions=observed)
        for path in _root_carriers(reader, selection, remember=False):
            observed[str(path)] = reader.version(path.lstat())
            paths.append(path)
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
