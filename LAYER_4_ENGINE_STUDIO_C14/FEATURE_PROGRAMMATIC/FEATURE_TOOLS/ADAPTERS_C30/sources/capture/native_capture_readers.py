"""Support native carrier capture."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from contextlib import nullcontext
from hashlib import sha256
from pathlib import Path, PurePosixPath
from threading import Lock
from ...ADAPTERS_C30__pub import LimitReached, ReadContext
from ...carriers.content.carrier_read__pub import CarrierError
from ...carriers.header.native_carrier_placement__pub import ARCHIVE_DIRECTORY
from ...sources.inventory.native_carrier_inventory import (
    StartupReadContext,
    full_carriers as _full_carriers,
)
from ...carriers.header.native_carrier_row import _parse_captured_carrier
from ...sources.capture.native_capture_changes import _issue
from ...sources.capture.native_capture_hashes import _carrier_groups, _carrier_directory


def _read_carrier_bytes(
    reader, selection, path, manifest, version, directory_fd, hashes, relative
):
    try:
        raw = (
            manifest
            if path == selection.manifest_path
            else reader.read(
                path,
                metadata_guard=True,
                skip_version=version,
                directory_fd=directory_fd,
            )
        )
    except OSError, LimitReached:
        hashes.pop(relative, None)
        raise
    return raw


def _parse_carrier_locked(
    selection,
    path,
    tree,
    raw,
    include_content_properties,
    domains,
    classified,
    relative,
    parse_lock,
):
    with parse_lock or nullcontext():
        classified.pop(relative, None)
        row, edge = _parse_captured_carrier(
            selection,
            path,
            tree,
            raw,
            include_content_properties,
            domains,
            classified,
        )
    return row, edge


def _carrier_digest(reader, raw):
    if isinstance(reader, StartupReadContext):
        return reader.digest(raw)
    return sha256(raw).hexdigest()


def _read_captured_carrier(
    reader,
    selection,
    path,
    tree,
    manifest,
    *,
    version,
    directory_fd,
    include_content_properties,
    parse_lock,
    relative,
    hashes,
    domains,
    classified,
):
    raw = _read_carrier_bytes(
        reader,
        selection,
        path,
        manifest,
        version,
        directory_fd,
        hashes,
        relative,
    )
    if raw is None:
        return None
    digest = hashes[relative] = _carrier_digest(reader, raw)
    row, edge = _parse_carrier_locked(
        selection,
        path,
        tree,
        raw,
        include_content_properties,
        domains,
        classified,
        relative,
        parse_lock,
    )
    row["_source_sha256"] = digest
    return row, edge


def _incremental_carrier_present(reader: ReadContext, path: Path) -> bool:
    reader.allowed(path)
    try:
        path.lstat()
    except FileNotFoundError, NotADirectoryError:
        return False
    return True


_MISSING = object()


def _capture_path(path, tree, relative, source, state, options):
    reader, selection, manifest, incremental, _, _ = source
    _, _, _, versions, missing, hashes, classified = state
    directory_fd, include_content_properties, parse_lock, domains = options
    if incremental and not _incremental_carrier_present(reader, path):
        missing.append(path)
        versions.pop(str(path), None)
        hashes.pop(relative, None)
        classified.pop(relative, None)
        return _MISSING
    return _read_captured_carrier(
        reader,
        selection,
        path,
        tree,
        manifest,
        version=versions.get(str(path)),
        directory_fd=directory_fd,
        include_content_properties=include_content_properties,
        parse_lock=parse_lock,
        relative=relative,
        hashes=hashes,
        domains=domains,
        classified=classified,
    )


def _handle_capture_error(error, path, selection, relative, captured, state):
    _, errors, issues, _, _, _, classified = state
    if (
        path == selection.manifest_path
        or isinstance(error, LimitReached)
        and error.limit != "max_file_bytes"
    ):
        raise
    _record_capture_error(
        error, relative, captured, classified, errors, issues
    )


def _capture_one(path, source, state, options):
    _, selection, _, _, previous, previous_rows = source
    candidates, errors, _, _, _, _, _ = state
    root, control = selection.root, selection.control_root
    tree = (
        path.relative_to(control).parts[0]
        if path.is_relative_to(control)
        else None
    )
    if tree == "000_ANECHOIC_framework":
        return
    relative = path.relative_to(root).as_posix()
    captured = None
    try:
        captured = _capture_path(path, tree, relative, source, state, options)
        if captured is _MISSING:
            return
        if captured is None:
            old = previous_rows.get(relative)
            if old is not None:
                candidates[relative] = old
            elif relative in previous.errors:
                errors[relative] = previous.errors[relative]
            return
        if (
            ARCHIVE_DIRECTORY in PurePosixPath(relative).parts[:-1]
            and captured[0]["status_group"] != "Archived"
        ):
            raise ValueError("Archive directory contains a non-Archived Atom")
        candidates[relative] = captured
    except (
        OSError,
        RuntimeError,
        TypeError,
        ValueError,
        CarrierError,
    ) as error:
        _handle_capture_error(
            error, path, selection, relative, captured, state
        )


def _capture_inputs(
    reader,
    selection,
    input_paths,
    manifest,
    incremental,
    previous,
    previous_rows,
    candidates,
    errors,
    issues,
    versions,
    missing,
    hashes,
    directory_fd=None,
    *,
    include_content_properties,
    parse_lock=None,
    domains=None,
    classified=None,
):
    source = (
        reader,
        selection,
        manifest,
        incremental,
        previous,
        previous_rows,
    )
    state = (candidates, errors, issues, versions, missing, hashes, classified)
    options = (directory_fd, include_content_properties, parse_lock, domains)
    for path in input_paths:
        _capture_one(path, source, state, options)


def _record_capture_error(
    error, relative, captured, classified, errors, issues
):
    if isinstance(error, (OSError, LimitReached)):
        classified.pop(relative, None)
    errors[relative] = str(error)
    code = (
        "read_error"
        if isinstance(error, OSError)
        else (
            "invalid_schema"
            if error.code
            in {
                "YAML_INVALID",
                "CARRIER_ALIAS_CONFLICT",
                "NATIVE_HEADER_SCHEMA",
            }
            else "parse_error"
        )
        if isinstance(error, CarrierError)
        else "invalid_value"
    )
    issues.append(
        _issue(
            relative,
            code,
            str(error),
            captured[0]["_exact_ref"] if captured else None,
        )
    )


def _capture_full_inputs(
    reader,
    selection,
    manifest,
    candidates,
    errors,
    issues,
    hashes,
    *,
    classified,
    include_content_properties,
    defer_archives,
    archive_roots,
    domains,
):
    paths = _full_carriers(reader, selection, defer_archives, archive_roots)
    parse_lock = Lock()
    for directory, members in _carrier_groups(paths):
        with _carrier_directory(reader, directory) as descriptor:

            def capture(path, directory_fd=descriptor):
                _capture_inputs(
                    reader,
                    selection,
                    (path,),
                    manifest,
                    False,
                    None,
                    {},
                    candidates,
                    errors,
                    issues,
                    {},
                    [],
                    hashes,
                    directory_fd=directory_fd,
                    include_content_properties=include_content_properties,
                    parse_lock=parse_lock,
                    domains=domains,
                    classified=classified,
                )

            with ThreadPoolExecutor(max_workers=8) as pool:
                for _ in pool.map(capture, members, buffersize=16):
                    pass
    if isinstance(reader, StartupReadContext):
        reader.emit_scan_metrics()
