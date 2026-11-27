"""Capture native carriers without interpreting legacy Scope Units or folders."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager, nullcontext
from hashlib import sha256
from itertools import groupby
import os
from pathlib import Path, PurePosixPath
from threading import Lock
from typing import Any, Literal

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.native_carrier_placement__pub import (
    ARCHIVE_DIRECTORY, project_goal_filename,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carrier_read__pub import CarrierError
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__pub import (
    CEILINGS, LimitReached, ReadContext, open_regular,
)

from .native_capture_types import NativeCapture, _preserve_capture_data as _preserve_capture_data
from .native_carrier_row import CURRENT_STATUSES as CURRENT_STATUSES, _container as _container, _parse_captured_carrier
from .native_carrier_inventory import StartupReadContext, full_carriers as _full_carriers, root_carriers as _root_carriers, startup_reader


class NativeManifestChanged(ValueError):
    """The capture no longer matches its validated Project Manifest."""


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
                           include_content_properties, parse_lock, relative, hashes, domains, classified):
    try:
        raw = manifest if path == selection.manifest_path else reader.read(
            path, metadata_guard=True, skip_version=version, directory_fd=directory_fd,
        )
    except (OSError, LimitReached):
        hashes.pop(relative, None)
        raise
    if raw is None:
        return None
    digest = hashes[relative] = reader.digest(raw) if isinstance(reader, StartupReadContext) else sha256(raw).hexdigest()
    with parse_lock or nullcontext():
        classified.pop(relative, None)
        row, edge = _parse_captured_carrier(selection, path, tree, raw, include_content_properties, domains, classified)
    row["_source_sha256"] = digest
    return row, edge


def _incremental_carrier_present(reader: ReadContext, path: Path) -> bool:
    reader.allowed(path)
    try:
        path.lstat()
    except (FileNotFoundError, NotADirectoryError):
        return False
    return True


def _capture_inputs(reader, selection, input_paths, manifest, incremental, previous,
                    previous_rows, candidates, errors, issues, versions, missing, hashes, directory_fd=None, *,
                    include_content_properties, parse_lock=None, domains=None, classified=None):
    root, control = selection.root, selection.control_root
    for path in input_paths:
        tree = path.relative_to(control).parts[0] if path.is_relative_to(control) else None
        if tree == "000_ANECHOIC_framework":
            continue
        relative = path.relative_to(root).as_posix()
        captured = None
        try:
            if incremental and not _incremental_carrier_present(reader, path):
                missing.append(path)
                versions.pop(str(path), None)
                hashes.pop(relative, None)
                classified.pop(relative, None)
                continue
            captured = _read_captured_carrier(
                reader, selection, path, tree, manifest, version=versions.get(str(path)), directory_fd=directory_fd,
                include_content_properties=include_content_properties, parse_lock=parse_lock,
                relative=relative, hashes=hashes, domains=domains, classified=classified,
            )
            if captured is None:
                old = previous_rows.get(relative)
                if old is not None:
                    candidates[relative] = old
                elif relative in previous.errors:
                    errors[relative] = previous.errors[relative]
                continue
            if ARCHIVE_DIRECTORY in PurePosixPath(relative).parts[:-1] and captured[0]["status_group"] != "Archived":
                raise ValueError("Archive directory contains a non-Archived Atom")
            candidates[relative] = captured
        except (OSError, RuntimeError, TypeError, ValueError, CarrierError) as error:
            if path == selection.manifest_path or isinstance(error, LimitReached) and error.limit != "max_file_bytes":
                raise
            if isinstance(error, (OSError, LimitReached)):
                classified.pop(relative, None)
            errors[relative] = str(error)
            code = ("read_error" if isinstance(error, OSError) else
                    ("invalid_schema" if error.code in {"YAML_INVALID", "CARRIER_ALIAS_CONFLICT", "NATIVE_HEADER_SCHEMA"}
                     else "parse_error") if isinstance(error, CarrierError) else "invalid_value")
            issues.append(_issue(relative, code, str(error), captured[0]["_exact_ref"] if captured else None))


def _native_carrier_hashes(selection, *, foreground=False, archive_roots=None, watcher_guarded=False):
    reader = startup_reader(selection.root, "foreground_hashes" if foreground else None,
                            archive=archive_roots is not None)
    manifest = check_native_manifest(reader, selection, None)
    hashes = {}
    deferred = set() if foreground else None
    paths = _full_carriers(reader, selection, defer_archives=deferred, archive_roots=archive_roots)
    for directory, members in _carrier_groups(paths):
        with _carrier_directory(reader, directory) as descriptor:
            for path in members:
                raw = manifest if path == selection.manifest_path else reader.read(
                    path, metadata_guard=True, directory_fd=descriptor)
                digest = reader.digest(raw) if isinstance(reader, StartupReadContext) else sha256(raw).hexdigest()
                hashes[path.relative_to(selection.root).as_posix()] = digest
    if isinstance(reader, StartupReadContext):
        reader.emit_scan_metrics()
    if not watcher_guarded and reader.currentness()["state"] != "unchanged":
        raise ValueError("Native Project carriers changed during capture")
    return hashes


def _carrier_groups(paths):
    return groupby(sorted(paths, key=lambda path: (path.parent, path.name)), key=lambda path: path.parent)


@contextmanager
def _carrier_directory(reader, directory):
    try:
        descriptor = open_regular(reader.allowed(directory), directory=True)
    except OSError:
        descriptor = None
    try:
        yield descriptor
    finally:
        if descriptor is not None:
            os.close(descriptor)


def _capture_full_inputs(reader, selection, manifest, candidates, errors, issues, hashes, *, classified,
                         include_content_properties, defer_archives, archive_roots, domains):
    paths = _full_carriers(reader, selection, defer_archives, archive_roots)
    parse_lock = Lock()
    for directory, members in _carrier_groups(paths):
        with _carrier_directory(reader, directory) as descriptor:
            def capture(path, directory_fd=descriptor):
                _capture_inputs(reader, selection, (path,), manifest, False, None,
                                {}, candidates, errors, issues, {}, [], hashes, directory_fd=directory_fd,
                                include_content_properties=include_content_properties, parse_lock=parse_lock, domains=domains, classified=classified)

            with ThreadPoolExecutor(max_workers=8) as pool:
                for _ in pool.map(capture, members, buffersize=16):
                    pass
    if isinstance(reader, StartupReadContext):
        reader.emit_scan_metrics()


def _validate_archive_capture(incremental, defer_archives, archive_roots):
    if archive_roots is not None and (defer_archives is not None or incremental):
        raise ValueError("Deferred archive capture requires a separate full phase")
    if defer_archives is not None and incremental:
        raise ValueError("Deferring archives requires a full capture")


def _validate_capture_options(selection, paths, incremental, defer_currentness, manifest_admitted):
    if defer_currentness and incremental:
        raise ValueError("Deferred currentness requires a full capture")
    if manifest_admitted and (not incremental or selection.manifest_path.relative_to(selection.root) in paths):
        raise ValueError("Manifest admission requires addressed non-Manifest paths")


def _capture_reader(selection, reader, defer_currentness):
    if reader is None:
        if defer_currentness:
            raise ValueError("Deferred currentness requires a supplied reader")
        return ReadContext(roots=[str(selection.root)], limits=dict(CEILINGS))
    return reader


def capture_native(
    selection: Any, *, previous: NativeCapture | None = None,
    paths: set[PurePosixPath] | None = None, reader: ReadContext | None = None,
    include_content_properties: bool | Literal["summary"] = True, manifest_admitted: bool = False,
    defer_currentness: bool = False,
    defer_archives: set[Path] | None = None, archive_roots: tuple[Path, ...] | None = None,
    domains: dict[str, set[str]] | None = None,
) -> NativeCapture:
    """Read one selected native tree and report invalid individual carriers.

    Write callers must refuse a capture with errors. When validation is deferred,
    check the supplied reader before publishing.
    """
    reader = _capture_reader(selection, reader, defer_currentness)
    if previous is not None and domains is None:
        domains = previous.status_domains
    if previous is not None and previous.status_domains != domains and (previous.atoms or previous.errors):
        raise ValueError("Incremental capture requires the same admitted Status domains")
    incremental = previous is not None and paths is not None
    _validate_archive_capture(incremental, defer_archives, archive_roots)
    if incremental and any(issue["code"].startswith("duplicate_") for issue in previous.ingestion_issues):
        return capture_native(selection, reader=reader, include_content_properties=include_content_properties, domains=domains)
    _validate_capture_options(selection, paths, incremental, defer_currentness, manifest_admitted)
    manifest = None if manifest_admitted else check_native_manifest(reader, selection, previous if incremental else None)
    versions, hashes = (dict(previous.versions), dict(previous.carrier_hashes)) if incremental else ({}, {})
    classified = dict(previous.classified_templates) if incremental else {}
    previous_rows = {row["source_path"]: (row, edge)
                     for row, edge in zip(previous.atoms, previous.containment)} if incremental else {}
    missing, issues = [], []
    if incremental:
        candidates, errors, input_paths = _changed_inputs(reader, selection, previous, paths)
        issues = [issue for issue in previous.ingestion_issues
                  if issue["relative_path"] in errors]
        _capture_inputs(reader, selection, input_paths, manifest, incremental, previous,
                        previous_rows, candidates, errors, issues, versions, missing, hashes,
                        include_content_properties=include_content_properties, domains=domains, classified=classified)
    else:
        candidates, errors = {}, {}
        _capture_full_inputs(reader, selection, manifest, candidates, errors, issues, hashes,
                             include_content_properties=include_content_properties,
                             defer_archives=defer_archives, archive_roots=archive_roots, domains=domains, classified=classified)
    if _capture_changed(reader, missing, defer_currentness):
        raise ValueError("Native Project carriers changed during capture")
    versions.update(reader.versions)
    return _unique_revisions(candidates, errors, versions, issues, hashes,
                             selection.manifest_path.relative_to(selection.root).as_posix(), domains, classified)


def _capture_changed(reader, missing, defer_currentness):
    return ((not defer_currentness and reader.currentness()["state"] != "unchanged")
            or any(path.exists() or path.is_symlink() for path in missing))


def revalidate_native(selection: Any, previous: NativeCapture | None) -> NativeCapture:
    """Prove the indexed Atom population against disk before a write."""
    from .indexed_lifecycle_capture import IndexedLifecycleCapture, revalidate_indexed_lifecycle
    if isinstance(previous, IndexedLifecycleCapture):
        return revalidate_indexed_lifecycle(selection, previous)
    if previous is None or previous.errors:
        return capture_native(selection, domains=previous.status_domains if previous is not None else None)
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


def _unique_revisions(candidates, errors, versions, issues, hashes, manifest_path, domains, classified):
    rows, containment = [], []
    revisions, currents = {}, {}
    ordered = sorted(candidates.items())
    for relative, (row, _) in ordered:
        revisions.setdefault(row["_exact_ref"], []).append(relative)
        if row["status_group"] == "Current":
            currents.setdefault(row["id"], []).append(relative)
    for groups, code in ((revisions, "duplicate_revision"), (currents, "duplicate_current")):
        for paths in groups.values():
            if len(paths) < 2:
                continue
            for path in paths:
                if path == manifest_path:
                    continue
                message = "Duplicate native revision or Current identity"
                issues.append(_issue(path, code, message, candidates[path][0]["_exact_ref"], paths))
                errors[path] = message
    for relative, (row, edge) in ordered:
        if relative in errors:
            continue
        rows.append(row)
        containment.append(edge)
    issues.sort(key=lambda item: (item["relative_path"] or "", item["code"]))
    classified = {path: value for path, value in classified.items() if path in errors}
    return NativeCapture(rows, containment, errors, versions, ingestion_issues=issues, carrier_hashes=hashes, status_domains=domains, classified_templates=classified)
