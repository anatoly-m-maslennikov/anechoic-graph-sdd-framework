"""Filesystem operations for local Release package staging."""

from __future__ import annotations

import hashlib
import os
import shutil
import stat
import tempfile
from collections.abc import Mapping
from pathlib import Path, PurePosixPath

from .release_assets import LocalReleaseError

_BOOTSTRAP = Path("LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/docker/start_mcp.py")


def _relative(value: object, *, label: str) -> Path:
    if not isinstance(value, str) or not value or "\x00" in value:
        raise LocalReleaseError(f"local-release-{label}-invalid")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise LocalReleaseError(f"local-release-{label}-invalid")
    return Path(*path.parts)


def _root(value: Path | str) -> Path:
    supplied = Path(value)
    try:
        root = supplied.resolve(strict=True)
    except OSError as error:
        raise LocalReleaseError("local-release-project-root-invalid") from error
    if supplied.is_symlink() or not root.is_dir() or root == Path(root.anchor):
        raise LocalReleaseError("local-release-project-root-invalid")
    return root


def _project_path(root: Path, relative: Path, *, label: str, require_exists: bool = False) -> Path:
    candidate = root / relative
    try:
        resolved = candidate.resolve(strict=require_exists)
        resolved.relative_to(root)
    except (OSError, ValueError) as error:
        raise LocalReleaseError(f"local-release-{label}-unsafe") from error
    current = root
    for component in relative.parts:
        current /= component
        if os.path.lexists(current) and current.is_symlink():
            raise LocalReleaseError(f"local-release-{label}-unsafe")
    return candidate


def _ignored(name: str) -> bool:
    return name == ".DS_Store" or name.startswith((".env", ".venv-")) or name.endswith(".env")


def _walk_regular_files(root: Path, *, excluded_directories: frozenset[str] = frozenset(),
                        excluded_root_prefix: tuple[str, ...] = (),
                        excluded_root_directories: frozenset[str] = frozenset(),
                        excluded_root_files: frozenset[str] = frozenset()) -> list[Path]:
    def fail(error: OSError) -> None:
        raise LocalReleaseError("local-release-source-read-failed") from error

    collected: list[Path] = []
    for directory, directories, names in os.walk(root, followlinks=False, onerror=fail):
        base = Path(directory)
        directories[:] = [name for name in directories if not _ignored(name)
                          and name.casefold() not in excluded_directories
                          and (base != root or name.casefold() not in excluded_root_directories)
                          and (base != root or not excluded_root_prefix or not name.casefold().startswith(excluded_root_prefix))]
        for name in directories:
            child = base / name
            if child.is_symlink():
                raise LocalReleaseError("local-release-source-link-unsafe")
        for name in names:
            if _ignored(name) or (base == root and name in excluded_root_files):
                continue
            child = base / name
            try:
                mode = child.lstat().st_mode
            except OSError as error:
                raise LocalReleaseError("local-release-source-read-failed") from error
            if stat.S_ISLNK(mode) or not stat.S_ISREG(mode):
                raise LocalReleaseError("local-release-source-entry-unsafe")
            collected.append(child)
    return sorted(collected)


def _clear_target(target: Path, *, root: Path, preserve: frozenset[str], label: str) -> None:
    if target == root or target.parent == target:
        raise LocalReleaseError(f"local-release-{label}-unsafe")
    if target.exists():
        if target.is_symlink() or not target.is_dir():
            raise LocalReleaseError(f"local-release-{label}-unsafe")
    else:
        target.mkdir(parents=True, exist_ok=False)
    for child in target.iterdir():
        if child.name in preserve or _ignored(child.name):
            continue
        _clear_owned(child, label=label)


def _clear_owned(path: Path, *, label: str, remove_finder_metadata: bool = False) -> None:
    """Clear one owned entry and retain ignored input files by default."""

    try:
        mode = path.lstat().st_mode
    except OSError as error:
        raise LocalReleaseError(f"local-release-{label}-unsafe") from error
    if stat.S_ISLNK(mode):
        raise LocalReleaseError(f"local-release-{label}-unsafe")
    if stat.S_ISREG(mode):
        path.unlink()
        return
    if not stat.S_ISDIR(mode):
        raise LocalReleaseError(f"local-release-{label}-unsafe")
    for child in path.iterdir():
        finder_metadata = (
            remove_finder_metadata and child.name == ".DS_Store" and not child.is_symlink() and child.is_file()
        )
        if _ignored(child.name) and not finder_metadata:
            continue
        _clear_owned(child, label=label, remove_finder_metadata=remove_finder_metadata)
    try:
        path.rmdir()
    except OSError:
        return


def _target(root: Path, relative: Path, *, label: str) -> Path:
    target = _project_path(root, relative, label=label)
    if target == root or target.parent == target or (target.parent == root and target.name.startswith((".anechoic_", "_anechoic_"))):
        raise LocalReleaseError("local-release-target-invalid")
    if target.exists() and (target.is_symlink() or not target.is_dir()):
        raise LocalReleaseError(f"local-release-{label}-unsafe")
    return target


def _copy_tree(source: Path, destination: Path, *, preserve: frozenset[str]) -> None:
    if source.is_symlink() or not source.is_dir() or destination.is_symlink() or not destination.is_dir():
        raise LocalReleaseError("local-release-copy-unsafe")
    for directory, directories, names in os.walk(source, followlinks=False):
        base = Path(directory)
        relative_directory = base.relative_to(source)
        directories[:] = [
            name for name in directories if not _ignored(name) and not (base == source and name in preserve)
        ]
        for name in directories:
            if (base / name).is_symlink():
                raise LocalReleaseError("local-release-copy-unsafe")
        if relative_directory != Path("."):
            target_directory = destination / relative_directory
            if target_directory.exists() and target_directory.is_symlink():
                raise LocalReleaseError("local-release-copy-unsafe")
            target_directory.mkdir(parents=True, exist_ok=True)
            shutil.copystat(base, target_directory, follow_symlinks=False)
        for name in names:
            if _ignored(name):
                continue
            entry = base / name
            if entry.relative_to(source).parts[0] in preserve:
                continue
            try:
                mode = entry.lstat().st_mode
            except OSError as error:
                raise LocalReleaseError("local-release-copy-unsafe") from error
            if stat.S_ISLNK(mode) or not stat.S_ISREG(mode):
                raise LocalReleaseError("local-release-copy-unsafe")
            relative = entry.relative_to(source)
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists() and target.is_symlink():
                raise LocalReleaseError("local-release-copy-unsafe")
            shutil.copy2(entry, target)


def _file_identity(path: Path) -> tuple[str, int]:
    return hashlib.sha256(path.read_bytes()).hexdigest(), stat.S_IMODE(path.stat().st_mode)


def _verify_package(package: Path, expected: Mapping[str, tuple[str, int]], *,
                    preserve: frozenset[str] = frozenset()) -> None:
    preserved_directories = frozenset(name.casefold() for name in preserve)
    actual = {entry.relative_to(package).as_posix(): _file_identity(entry)
              for entry in _walk_regular_files(package, excluded_root_directories=preserved_directories,
                                                excluded_root_files=preserve)}
    if actual != expected:
        raise LocalReleaseError("local-release-package-verification-failed")


def _install_bootstrap(root: Path, package: Path, expected: Mapping[str, tuple[str, int]]) -> None:
    """Copy the verified restart script as data."""
    source = _project_path(root, (package / _BOOTSTRAP).relative_to(root), label="bootstrap-source")
    target = _project_path(root, Path(".anechoic_runtime/start_mcp.py"), label="bootstrap-target")
    if target.exists() and not target.is_file():
        raise LocalReleaseError("local-release-bootstrap-target-unsafe")
    digest, mode = expected[_BOOTSTRAP.as_posix()]
    if not source.is_file() or not mode & 0o111 or _file_identity(source) != (digest, mode):
        raise LocalReleaseError("local-release-bootstrap-source-invalid")
    with tempfile.NamedTemporaryFile(dir=target.parent, prefix=".start-mcp-", delete=False) as output:
        temporary = Path(output.name)
    try:
        shutil.copy2(source, temporary)
        if _file_identity(temporary) != (digest, mode):
            raise LocalReleaseError("local-release-bootstrap-source-changed")
        os.replace(temporary, target)
    finally:
        temporary.unlink(missing_ok=True)


