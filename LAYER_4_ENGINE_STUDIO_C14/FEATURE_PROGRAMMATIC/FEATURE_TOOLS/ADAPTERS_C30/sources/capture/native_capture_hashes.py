"""Support native carrier capture."""

from contextlib import contextmanager
from hashlib import sha256
from itertools import groupby
import os
from ...ADAPTERS_C30__pub import open_regular
from ...sources.inventory.native_carrier_inventory import (
    StartupReadContext,
    full_carriers as _full_carriers,
    startup_reader,
)


def _native_carrier_hashes(
    selection,
    *,
    foreground=False,
    archive_roots=None,
    watcher_guarded=False,
    check_manifest,
):
    reader = startup_reader(
        selection.root,
        "foreground_hashes" if foreground else None,
        archive=archive_roots is not None,
    )
    manifest = check_manifest(reader, selection, None)
    hashes = {}
    deferred = set() if foreground else None
    paths = _full_carriers(
        reader, selection, defer_archives=deferred, archive_roots=archive_roots
    )
    for directory, members in _carrier_groups(paths):
        with _carrier_directory(reader, directory) as descriptor:
            for path in members:
                raw = (
                    manifest
                    if path == selection.manifest_path
                    else reader.read(
                        path, metadata_guard=True, directory_fd=descriptor
                    )
                )
                digest = (
                    reader.digest(raw)
                    if isinstance(reader, StartupReadContext)
                    else sha256(raw).hexdigest()
                )
                hashes[path.relative_to(selection.root).as_posix()] = digest
    if isinstance(reader, StartupReadContext):
        reader.emit_scan_metrics()
    if not watcher_guarded and reader.currentness()["state"] != "unchanged":
        raise ValueError("Native Project carriers changed during capture")
    return hashes


def _carrier_groups(paths):
    return groupby(
        sorted(paths, key=lambda path: (path.parent, path.name)),
        key=lambda path: path.parent,
    )


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
