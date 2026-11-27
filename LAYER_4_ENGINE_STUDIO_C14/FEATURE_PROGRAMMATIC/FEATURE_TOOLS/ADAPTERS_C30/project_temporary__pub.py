"""Allocate filesystem staging below a caller-selected Project root."""

import os
from pathlib import Path
import re
import tempfile

from .temporary_boundary import (
    TemporaryBoundaryError,
    validate_directory_components,
)

TEMPORARY_DIRECTORY = Path(".anechoic_tmp")
_OWNER = re.compile(r"[a-z0-9][a-z0-9_-]{0,63}\Z")


def _owner_directory(root: Path, owner: str) -> Path:
    if not _OWNER.fullmatch(owner):
        raise TemporaryBoundaryError(f"invalid temporary-state owner: {owner}")
    if root.is_symlink() or not root.is_dir():
        raise TemporaryBoundaryError(
            f"invalid Project root for temporary state: {root}"
        )
    return root / TEMPORARY_DIRECTORY / owner


def owned_temporary_root(root: Path, owner: str) -> Path:
    """Create and return one Component's temporary directory."""
    directory = _owner_directory(root, owner)
    validate_directory_components(root, directory)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def atomic_tempfile(
    root: Path,
    destination: Path,
    owner: str,
    *,
    prefix: str | None = None,
    suffix: str = "",
) -> tuple[int, str]:
    """Allocate a temporary file on the same filesystem as its destination."""
    directory = _owner_directory(root, owner) / "atomic"
    validate_directory_components(root, directory)
    staging_device = os.stat(_existing_directory(directory)).st_dev
    destination_device = os.stat(
        _existing_directory(destination.parent)
    ).st_dev
    if staging_device != destination_device:
        raise TemporaryBoundaryError(
            f"temporary state and destination are on different filesystems: {directory} -> {destination}"
        )
    directory.mkdir(parents=True, exist_ok=True)
    destination.parent.mkdir(parents=True, exist_ok=True)
    return tempfile.mkstemp(
        prefix=prefix or f".{destination.name}.",
        suffix=suffix,
        dir=directory,
    )


def _existing_directory(path: Path) -> Path:
    """Return the nearest existing directory used for a pre-mutation device check."""

    candidate = path
    while not candidate.exists():
        parent = candidate.parent
        if parent == candidate:
            raise TemporaryBoundaryError(
                f"cannot resolve destination directory: {path}"
            )
        candidate = parent
    if not candidate.is_dir():
        raise TemporaryBoundaryError(
            f"destination path is not a directory: {candidate}"
        )
    return candidate
