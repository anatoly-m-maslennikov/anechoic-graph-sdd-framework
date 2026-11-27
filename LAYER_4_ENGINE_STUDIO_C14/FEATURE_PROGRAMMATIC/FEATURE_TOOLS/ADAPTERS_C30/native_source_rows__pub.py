"""Capture native carriers without interpreting legacy folders."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor as ThreadPoolExecutor
from contextlib import (
    contextmanager as contextmanager,
    nullcontext as nullcontext,
)
from itertools import groupby as groupby
import os as os
from threading import Lock as Lock
from hashlib import sha256
from pathlib import Path, PurePosixPath
from typing import Any, Literal

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__pub import (
    CEILINGS,
    LimitReached as LimitReached,
    ReadContext,
    open_regular as open_regular,
)

from .carrier_read__pub import CarrierError as CarrierError
from .native_carrier_placement__pub import (
    ARCHIVE_DIRECTORY as ARCHIVE_DIRECTORY,
    project_goal_filename as project_goal_filename,
)
from .native_carrier_row import (
    _parse_captured_carrier as _parse_captured_carrier,
)
from . import native_carrier_inventory as _native_inventory
from .native_carrier_inventory import (
    StartupReadContext as StartupReadContext,
    startup_reader as startup_reader,
)
from .native_capture_types import (
    NativeCapture,
    _preserve_capture_data as _preserve_capture_data,
)
from .native_carrier_row import (
    CURRENT_STATUSES as CURRENT_STATUSES,
    _container as _container,
)
from .native_carrier_inventory import (
    root_carriers as _root_carriers,
)

from .native_capture_batch import collect_native_capture
from .native_capture_changes import (
    _changed_inputs as _changed_inputs,
    _issue as _issue,
    _unique_revisions as _unique_revisions,
)
from .native_capture_hashes import (
    _native_carrier_hashes as _native_carrier_hashes_impl,
    _carrier_groups as _carrier_groups,
    _carrier_directory as _carrier_directory,
)
from .native_capture_readers import (
    _capture_full_inputs as _capture_full_inputs,
    _capture_inputs as _capture_inputs,
    _incremental_carrier_present as _incremental_carrier_present,
    _read_captured_carrier as _read_captured_carrier,
    _record_capture_error as _record_capture_error,
)


_full_carriers = _native_inventory.full_carriers


class NativeManifestChanged(ValueError):
    """The capture no longer matches its validated Project Manifest."""


def check_native_manifest(
    reader: ReadContext, selection: Any, previous: NativeCapture | None
) -> bytes | None:
    try:
        raw = reader.read(
            selection.manifest_path,
            metadata_guard=previous is not None,
            skip_version=previous.versions.get(str(selection.manifest_path))
            if previous
            else None,
        )
    except FileNotFoundError as error:
        raise NativeManifestChanged(
            "Selected native Project Manifest moved or was removed"
        ) from error
    if (
        raw is not None
        and sha256(raw).hexdigest() != selection.manifest_sha256
    ):
        raise NativeManifestChanged("Selected native Project Manifest changed")
    return raw


def _validate_archive_capture(incremental, defer_archives, archive_roots):
    if archive_roots is not None and (
        defer_archives is not None or incremental
    ):
        raise ValueError(
            "Deferred archive capture requires a separate full phase"
        )
    if defer_archives is not None and incremental:
        raise ValueError("Deferring archives requires a full capture")


def _validate_capture_options(
    selection, paths, incremental, defer_currentness, manifest_admitted
):
    if defer_currentness and incremental:
        raise ValueError("Deferred currentness requires a full capture")
    if manifest_admitted and (
        not incremental
        or selection.manifest_path.relative_to(selection.root) in paths
    ):
        raise ValueError(
            "Manifest admission requires addressed non-Manifest paths"
        )


def _native_carrier_hashes(
    selection, *, foreground=False, archive_roots=None, watcher_guarded=False
):
    return _native_carrier_hashes_impl(
        selection,
        foreground=foreground,
        archive_roots=archive_roots,
        watcher_guarded=watcher_guarded,
        check_manifest=check_native_manifest,
    )


def _capture_reader(selection, reader, defer_currentness):
    if reader is None:
        if defer_currentness:
            raise ValueError("Deferred currentness requires a supplied reader")
        return ReadContext(roots=[str(selection.root)], limits=dict(CEILINGS))
    return reader


def _validated_domains(previous, domains):
    if previous is not None and domains is None:
        domains = previous.status_domains
    if (
        previous is not None
        and previous.status_domains != domains
        and (previous.atoms or previous.errors)
    ):
        raise ValueError(
            "Incremental capture requires the same admitted Status domains"
        )
    return domains


def _capture_admitted(selection, reader, previous, paths, settings):
    (
        incremental,
        include_content_properties,
        manifest_admitted,
        defer_currentness,
        defer_archives,
        archive_roots,
        domains,
    ) = settings
    _validate_capture_options(
        selection, paths, incremental, defer_currentness, manifest_admitted
    )
    manifest = (
        None
        if manifest_admitted
        else check_native_manifest(
            reader, selection, previous if incremental else None
        )
    )
    options = (
        incremental,
        include_content_properties,
        defer_currentness,
        defer_archives,
        archive_roots,
        domains,
    )
    callbacks = (
        _changed_inputs,
        _capture_inputs,
        _capture_full_inputs,
        _capture_changed,
        _unique_revisions,
    )
    return collect_native_capture(
        selection, reader, previous, paths, manifest, options, callbacks
    )


def capture_native(
    selection: Any,
    *,
    previous: NativeCapture | None = None,
    paths: set[PurePosixPath] | None = None,
    reader: ReadContext | None = None,
    include_content_properties: bool | Literal["summary"] = True,
    manifest_admitted: bool = False,
    defer_currentness: bool = False,
    defer_archives: set[Path] | None = None,
    archive_roots: tuple[Path, ...] | None = None,
    domains: dict[str, set[str]] | None = None,
) -> NativeCapture:
    """Read a native tree; write callers must refuse capture errors.

    Check the supplied reader before publishing if validation is deferred.
    """
    reader = _capture_reader(selection, reader, defer_currentness)
    domains = _validated_domains(previous, domains)
    incremental = previous is not None and paths is not None
    _validate_archive_capture(incremental, defer_archives, archive_roots)
    if incremental and any(
        issue["code"].startswith("duplicate_")
        for issue in previous.ingestion_issues
    ):
        return capture_native(
            selection,
            reader=reader,
            include_content_properties=include_content_properties,
            domains=domains,
        )
    settings = (
        incremental,
        include_content_properties,
        manifest_admitted,
        defer_currentness,
        defer_archives,
        archive_roots,
        domains,
    )
    return _capture_admitted(selection, reader, previous, paths, settings)


def _capture_changed(reader, missing, defer_currentness):
    return (
        not defer_currentness and reader.currentness()["state"] != "unchanged"
    ) or any(path.exists() or path.is_symlink() for path in missing)


def revalidate_native(
    selection: Any, previous: NativeCapture | None
) -> NativeCapture:
    """Prove the indexed Atom population against disk before a write."""
    from .indexed_lifecycle_capture import (
        IndexedLifecycleCapture,
        revalidate_indexed_lifecycle,
    )

    if isinstance(previous, IndexedLifecycleCapture):
        return revalidate_indexed_lifecycle(selection, previous)
    if previous is None or previous.errors:
        return capture_native(
            selection,
            domains=previous.status_domains if previous is not None else None,
        )
    control, root = selection.control_root, selection.root
    installed = control / "000_ANECHOIC_framework"
    reader = ReadContext(roots=[str(root)], limits=dict(CEILINGS))

    def versions():
        observed = {}
        paths = reader.inventory(control, remember=False, versions=observed)
        for path in _root_carriers(reader, selection, remember=False):
            observed[str(path)] = reader.version(path.lstat())
            paths.append(path)
        return {
            str(path): observed[str(path)]
            for path in paths
            if path.suffix == ".md" and not path.is_relative_to(installed)
        }

    before = versions()
    changed = {
        PurePosixPath(path).relative_to(root)
        for path in before.keys() | previous.versions.keys()
        if before.get(path) != previous.versions.get(path)
    }
    capture = capture_native(selection, previous=previous, paths=changed)
    if versions() != before:
        raise ValueError("Native Project carriers changed during capture")
    return capture
