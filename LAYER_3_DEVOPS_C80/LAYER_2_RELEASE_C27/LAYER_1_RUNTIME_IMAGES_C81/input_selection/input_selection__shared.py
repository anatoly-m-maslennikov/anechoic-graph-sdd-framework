"""Read Release fields from one native Project Manifest without execution.

This narrow input contract does not validate against the compiled Model.
"""

from __future__ import annotations

from hashlib import sha256
import os
from pathlib import Path
import re
import stat

import yaml

from ._release_manifest_parser import read_atom_header
from ._release_selection_manifest import (
    ReleaseSelection as ReleaseSelection,
    _manifest,
    _manifest_status,
    _protected,
    _canonical_root,
    _control_identity,
    _directory,
    _version,
)


_RESERVED = {
    prefix + name
    for prefix in (".anechoic_", "_anechoic_")
    for name in ("new", "legacy", "legacy_archive", "runtime", "tmp")
}
_MAX_FILE = 64 * 1024 * 1024


def _read(fd: int, name: str) -> tuple[bytes, tuple[int, ...]]:
    descriptor = os.open(
        name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd
    )
    with os.fdopen(descriptor, "rb") as stream:
        before = os.fstat(stream.fileno())
        if not stat.S_ISREG(before.st_mode) or before.st_size > _MAX_FILE:
            raise ValueError("Manifest source is not a bounded regular file")
        raw = stream.read(_MAX_FILE + 1)
        if len(raw) != before.st_size or _version(before) != _version(
            os.fstat(stream.fileno())
        ):
            raise ValueError("Manifest source changed during read")
        return raw, _version(before)


def _names(
    fd: int, *, controls: bool, ignore_control_symlinks: bool = False
) -> tuple[str, ...]:
    with os.scandir(fd) as entries:
        names = []
        for index, entry in enumerate(entries, 1):
            if index > 1_000_000:
                raise ValueError("Project inventory exceeds the host ceiling")
            if controls:
                if (
                    not entry.name.startswith((".anechoic_", "_anechoic_"))
                    or entry.name in _RESERVED
                ):
                    continue
                if entry.is_symlink():
                    if ignore_control_symlinks:
                        continue
                    raise ValueError(
                        "Project control candidates must not be symlinks"
                    )
                if entry.is_dir(follow_symlinks=False):
                    names.append(entry.name)
                    if len(names) > 64:
                        raise ValueError(
                            "Project control candidates exceed "
                            "the host ceiling"
                        )
            elif entry.name.endswith(".md"):
                names.append(entry.name)
        return tuple(sorted(names))


def _scan_records(fd, names, control, root, total_bytes, controls, explicit):
    has_manifest = False
    records = []
    candidates = []
    for name in names:
        if (
            control == "."
            and not re.match(r"[A-Z]+-S-", name)
            and "PROJECT_MANIFEST" not in name
        ):
            continue
        raw, version = _read(fd, name)
        total_bytes += len(raw)
        if total_bytes > 1024 * 1024 * 1024:
            raise ValueError("Project inventory exceeds the read ceiling")
        digest = sha256(raw).hexdigest()
        records.append((name, version, digest))
        try:
            metadata, body = read_atom_header(raw.decode("utf-8"))
        except ValueError, UnicodeError, yaml.YAMLError, RecursionError:
            if (control != "." and re.match(r"[A-Z]+-S-", name)) or (
                control == "." and "PROJECT_MANIFEST" in name
            ):
                raise
            continue
        is_manifest, active = _manifest_status(metadata, name)
        has_manifest |= is_manifest
        if active:
            candidates.append(
                _manifest(
                    metadata,
                    body,
                    name,
                    None if control == "." else Path(control),
                    digest,
                    root,
                    controls,
                    explicit,
                )
            )
    return records, candidates, has_manifest, total_bytes


def _scan_control(
    root_fd: int,
    control: str,
    root: Path,
    total_bytes: int,
    controls: tuple[str, ...] = (),
    explicit: Path | None = None,
):
    selection = None
    fd = (
        os.dup(root_fd)
        if control == "."
        else os.open(
            control,
            os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
            dir_fd=root_fd,
        )
    )
    try:
        control_identity = (os.fstat(fd).st_dev, os.fstat(fd).st_ino)
        names = _names(fd, controls=False)
        records, candidates, has_manifest, total_bytes = _scan_records(
            fd, names, control, root, total_bytes, controls, explicit
        )
        if has_manifest:
            if len(candidates) != 1:
                raise ValueError("Expected one Active Project Manifest")
            selection = candidates[0]
        snapshot = (control, control_identity, names, records)
    finally:
        os.close(fd)
    return selection, snapshot, total_bytes


def _verify_snapshots(root_fd: int, snapshots, total_bytes: int) -> None:
    for control, identity, names, records in snapshots:
        fd = (
            os.dup(root_fd)
            if control == "."
            else os.open(
                control,
                os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                dir_fd=root_fd,
            )
        )
        try:
            info = os.fstat(fd)
            if (info.st_dev, info.st_ino) != identity or _names(
                fd, controls=False
            ) != names:
                raise ValueError("Project control changed during selection")
            for name, version, digest in records:
                raw, current = _read(fd, name)
                total_bytes += len(raw)
                if total_bytes > 1024 * 1024 * 1024:
                    raise ValueError(
                        "Project inventory exceeds the read ceiling"
                    )
                if current != version or sha256(raw).hexdigest() != digest:
                    raise ValueError(
                        "Project carriers changed during selection"
                    )
            if _names(fd, controls=False) != names:
                raise ValueError("Project control changed during selection")
        finally:
            os.close(fd)


def _verify_selection(
    root: Path,
    root_fd: int,
    root_identity,
    selection: ReleaseSelection,
    controls,
    check_controls: bool,
    snapshots,
    total_bytes: int,
    control_identity,
) -> None:
    if check_controls and _names(root_fd, controls=True) != controls:
        raise ValueError("Project control candidates changed during selection")
    _verify_snapshots(root_fd, snapshots, total_bytes)
    if check_controls and _names(root_fd, controls=True) != controls:
        raise ValueError("Project control candidates changed during selection")
    if (
        control_identity is not None
        and _control_identity(root_fd, selection.control_relative)
        != control_identity
    ):
        raise ValueError("Project control changed during selection")
    current_root = _directory(root)
    try:
        info = os.fstat(current_root)
        if (info.st_dev, info.st_ino) != root_identity:
            raise ValueError("Project root changed during selection")
    finally:
        os.close(current_root)


def _explicit_control(control_relative):
    explicit = None
    if control_relative is not None:
        explicit = Path(control_relative)
        if (
            len(explicit.parts) != 1
            or str(control_relative) != explicit.as_posix()
            or not explicit.name.startswith((".anechoic_", "_anechoic_"))
            or explicit.name in {".anechoic_", "_anechoic_"}
            or _protected(explicit)
        ):
            raise ValueError(
                "Control root must be a normalized direct Project child"
            )
    return explicit


def _find_legacy(root_fd, root, controls, explicit, snapshots, total_bytes):
    legacy_controls = controls if explicit is None else (explicit.name,)
    selections = []
    for control in legacy_controls:
        candidate, snapshot, total_bytes = _scan_control(
            root_fd, control, root, total_bytes
        )
        if candidate is not None:
            selections.append(candidate)
        snapshots.append(snapshot)
    if len(selections) != 1:
        raise ValueError("A unique native Project Manifest is required")
    selection = selections[0]
    return selection, total_bytes


def _select_from_root(root, root_fd, control_relative):
    root_identity = (
        os.fstat(root_fd).st_dev,
        os.fstat(root_fd).st_ino,
    )
    explicit = _explicit_control(control_relative)
    controls = _names(
        root_fd,
        controls=True,
        ignore_control_symlinks=explicit is not None,
    )
    selection, root_snapshot, total_bytes = _scan_control(
        root_fd, ".", root, 0, controls, explicit
    )
    if selection is not None and explicit is not None:
        controls = _names(root_fd, controls=True)
    check_controls = selection is not None or explicit is None
    snapshots = [root_snapshot]
    control_identity = None
    if selection is not None:
        control_identity = _control_identity(
            root_fd, selection.control_relative
        )
    if selection is None:
        selection, total_bytes = _find_legacy(
            root_fd, root, controls, explicit, snapshots, total_bytes
        )
    _verify_selection(
        root,
        root_fd,
        root_identity,
        selection,
        controls,
        check_controls,
        snapshots,
        total_bytes,
        control_identity,
    )
    return selection


def read_release_selection(
    project_root: str | Path, control_relative: str | Path | None = None
) -> ReleaseSelection:
    """Select an active native Project Manifest and pin its inputs."""
    try:
        root = _canonical_root(project_root)
        root_fd = _directory(root)
        try:
            return _select_from_root(root, root_fd, control_relative)
        finally:
            os.close(root_fd)
    except (
        OSError,
        RuntimeError,
        TypeError,
        ValueError,
        AttributeError,
        yaml.YAMLError,
        RecursionError,
    ) as error:
        raise ValueError(
            "Project Manifest is unavailable, invalid, or unsafe"
        ) from error
