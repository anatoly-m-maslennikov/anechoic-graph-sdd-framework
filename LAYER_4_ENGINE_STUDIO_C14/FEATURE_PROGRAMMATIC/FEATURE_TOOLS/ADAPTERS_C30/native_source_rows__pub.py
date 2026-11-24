"""Capture native carriers without interpreting legacy Scope Units or folders."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from contextlib import nullcontext
from dataclasses import dataclass, field
from hashlib import sha256
from itertools import groupby
import os
from pathlib import Path, PurePosixPath
from threading import Lock
from typing import Any, Literal

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.native_carrier_header__pub import native_header_view
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.native_carrier_placement__pub import (
    ARCHIVE_DIRECTORY, PROJECT_CONFIG_DIRECTORY, TICKET_DIRECTORY, project_goal_filename,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carrier_read__pub import CarrierError
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__pub import (
    CEILINGS, LimitReached, ReadContext, open_regular,
)


@dataclass(frozen=True)
class NativeCapture:
    atoms: list[dict[str, Any]]
    containment: list[dict[str, Any]]
    errors: dict[str, str]
    versions: dict[str, tuple[int, ...]] = field(default_factory=dict, compare=False)
    ingestion_issues: list[dict[str, Any]] = field(default_factory=list, compare=False, kw_only=True)


class NativeManifestChanged(ValueError):
    """The capture no longer matches its validated Project Manifest."""


from .native_carrier_row import CURRENT_STATUSES as CURRENT_STATUSES, _carrier_row, _container as _container

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
                           include_content_properties, parse_lock):
    raw = manifest if path == selection.manifest_path else reader.read(
        path, metadata_guard=True, skip_version=version, directory_fd=directory_fd,
    )
    if raw is None:
        return None
    with parse_lock or nullcontext():
        return _parse_captured_carrier(selection, path, tree, raw, include_content_properties)


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
                    previous_rows, candidates, errors, issues, versions, missing, directory_fd=None, *,
                    include_content_properties, parse_lock=None, archives_only=False):
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
                include_content_properties=include_content_properties, parse_lock=parse_lock,
            )
            if captured is None:
                old = previous_rows.get(relative)
                if old is not None:
                    candidates[relative] = old
                elif relative in previous.errors:
                    errors[relative] = previous.errors[relative]
                continue
            if archives_only and captured[0]["status_group"] != "Archived":
                raise ValueError("Deferred archive directory contains a non-Archived Atom")
            candidates[relative] = captured
        except (OSError, RuntimeError, TypeError, ValueError, CarrierError) as error:
            errors[relative] = str(error)
            code = ("read_error" if isinstance(error, OSError) else
                    ("invalid_schema" if error.code in {"YAML_INVALID", "CARRIER_ALIAS_CONFLICT", "NATIVE_HEADER_SCHEMA"}
                     else "parse_error") if isinstance(error, CarrierError) else "invalid_value")
            issues.append(_issue(relative, code, str(error)))


def _full_carriers(reader, selection, defer_archives=None, archive_roots=None):
    installed = selection.control_root / "000_ANECHOIC_framework"
    if archive_roots is not None:
        paths = set()
        for root in archive_roots:
            paths.update(path for path in reader.inventory(root) if path.suffix == ".md")
            if len(paths) > reader.limits["max_candidates"]:
                raise LimitReached("max_candidates")
        return sorted(paths)

    def prune(path):
        if path == installed:
            return True
        if path.name == ARCHIVE_DIRECTORY:
            defer_archives.add(path)
            return True
        return False

    paths = [path for path in reader.inventory(selection.control_root,
                                               prune=prune if defer_archives is not None else None)
             if path.suffix == ".md" and not path.is_relative_to(installed)]
    return sorted(set(paths + _root_carriers(reader, selection)))


def _native_carrier_hashes(selection, *, foreground=False, archive_roots=None, watcher_guarded=False):
    reader = ReadContext(roots=[str(selection.root)], limits=dict(CEILINGS))
    manifest = check_native_manifest(reader, selection, None)
    hashes = {}
    deferred = set() if foreground else None
    for path in _full_carriers(reader, selection, defer_archives=deferred, archive_roots=archive_roots):
        raw = manifest if path == selection.manifest_path else reader.read(path, metadata_guard=True)
        hashes[path.relative_to(selection.root).as_posix()] = sha256(raw).hexdigest()
    if not watcher_guarded and reader.currentness()["state"] != "unchanged":
        raise ValueError("Native Project carriers changed during capture")
    return hashes


def _capture_full_inputs(reader, selection, manifest, candidates, errors, issues, *,
                         include_content_properties, defer_archives, archive_roots):
    paths = _full_carriers(reader, selection, defer_archives, archive_roots)
    parse_lock = Lock()
    for directory, members in groupby(sorted(paths, key=lambda path: (path.parent, path.name)),
                                      key=lambda path: path.parent):
        try:
            descriptor = open_regular(reader.allowed(directory), directory=True)
        except OSError:
            descriptor = None
        try:
            def capture(path, directory_fd=descriptor):
                _capture_inputs(reader, selection, (path,), manifest, False, None,
                                {}, candidates, errors, issues, {}, [], directory_fd=directory_fd,
                                include_content_properties=include_content_properties, parse_lock=parse_lock,
                                archives_only=archive_roots is not None)

            with ThreadPoolExecutor(max_workers=8) as pool:
                for _ in pool.map(capture, members, buffersize=16):
                    pass
        finally:
            if descriptor is not None:
                os.close(descriptor)


def _validate_capture_options(selection, paths, incremental, defer_currentness, manifest_admitted):
    if defer_currentness and incremental:
        raise ValueError("Deferred currentness requires a full capture")
    if manifest_admitted and (not incremental or selection.manifest_path.relative_to(selection.root) in paths):
        raise ValueError("Manifest admission requires addressed non-Manifest paths")


def capture_native(
    selection: Any, *, previous: NativeCapture | None = None,
    paths: set[PurePosixPath] | None = None, reader: ReadContext | None = None,
    include_content_properties: bool | Literal["archive-summary"] = True, manifest_admitted: bool = False,
    defer_currentness: bool = False,
    defer_archives: set[Path] | None = None, archive_roots: tuple[Path, ...] | None = None,
) -> NativeCapture:
    """Read one selected native tree. Callers must refuse a capture with errors.

    When validation is deferred, check the supplied reader before publishing.
    """
    if reader is None:
        if defer_currentness:
            raise ValueError("Deferred currentness requires a supplied reader")
        reader = ReadContext(roots=[str(selection.root)], limits=dict(CEILINGS))
    incremental = previous is not None and paths is not None
    if archive_roots is not None and (defer_archives is not None or incremental):
        raise ValueError("Deferred archive capture requires a separate full phase")
    if defer_archives is not None and incremental:
        raise ValueError("Deferring archives requires a full capture")
    if incremental and any(issue["code"].startswith("duplicate_") for issue in previous.ingestion_issues):
        return capture_native(selection, reader=reader, include_content_properties=include_content_properties)
    _validate_capture_options(selection, paths, incremental, defer_currentness, manifest_admitted)
    manifest = None if manifest_admitted else check_native_manifest(reader, selection, previous if incremental else None)
    versions = dict(previous.versions) if incremental else {}
    previous_rows = {row["source_path"]: (row, edge)
                     for row, edge in zip(previous.atoms, previous.containment)} if incremental else {}
    missing, issues = [], []
    if incremental:
        candidates, errors, input_paths = _changed_inputs(reader, selection, previous, paths)
        issues = [issue for issue in previous.ingestion_issues
                  if issue["relative_path"] in errors]
        _capture_inputs(reader, selection, input_paths, manifest, incremental, previous,
                        previous_rows, candidates, errors, issues, versions, missing,
                        include_content_properties=include_content_properties)
    else:
        candidates, errors = {}, {}
        _capture_full_inputs(reader, selection, manifest, candidates, errors, issues,
                             include_content_properties=include_content_properties,
                             defer_archives=defer_archives, archive_roots=archive_roots)
    if (not defer_currentness and reader.currentness()["state"] != "unchanged") or any(
        path.exists() or path.is_symlink() for path in missing
    ):
        raise ValueError("Native Project carriers changed during capture")
    versions.update(reader.versions)
    return _unique_revisions(candidates, errors, versions, issues)


def revalidate_native(selection: Any, previous: NativeCapture | None) -> NativeCapture:
    """Prove the indexed Atom population against disk before a write."""
    from .indexed_lifecycle_capture import IndexedLifecycleCapture, revalidate_indexed_lifecycle
    if isinstance(previous, IndexedLifecycleCapture):
        return revalidate_indexed_lifecycle(selection, previous)
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


def _issue(relative_path, code, message, atom_ref=None, related_paths=None):
    return {"relative_path": relative_path, "code": code, "message": message,
            "atom_ref": atom_ref, "related_paths": related_paths or []}


def _unique_revisions(candidates, errors, versions, issues):
    rows, containment = [], []
    revisions, currents = {}, {}
    ordered = sorted(candidates.items())
    for relative, (row, _) in ordered:
        revisions.setdefault(row["_exact_ref"], []).append(relative)
        if row["status_group"] == "Current":
            currents.setdefault(row["id"], []).append(relative)
    for groups, code in ((revisions, "duplicate_revision"), (currents, "duplicate_current")):
        for identity, paths in groups.items():
            if len(paths) < 2:
                continue
            for path in paths:
                issues.append(_issue(path, code, "Duplicate native revision or Current identity", identity, paths))
    exact_paths, current_paths = set(), set()
    for relative, (row, edge) in ordered:
        exact, group, atom_id = row["_exact_ref"], row["status_group"], row["id"]
        if exact in exact_paths or (group == "Current" and atom_id in current_paths):
            errors[relative] = "Duplicate native revision or Current identity"
            continue
        rows.append(row)
        containment.append(edge)
        exact_paths.add(exact)
        if group == "Current":
            current_paths.add(atom_id)
    issues.sort(key=lambda item: (item["relative_path"] or "", item["code"]))
    return NativeCapture(rows, containment, errors, versions, ingestion_issues=issues)
