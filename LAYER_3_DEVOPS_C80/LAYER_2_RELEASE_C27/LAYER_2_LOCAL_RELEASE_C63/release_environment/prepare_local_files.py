"""Validate scoped paths and copy source files safely."""

from contextlib import ExitStack
from hashlib import file_digest
import os
from pathlib import Path
import shutil
import stat

from LAYER_1_RUNTIME_IMAGES_C81.LAYER_1_RUNTIME_IMAGES_C81__shared import (
    LocalReleaseError,
    _project_path,
)

_PROTECTED = {".git", ".ssh", ".aws", ".gnupg"}
_RUNTIME = {".anechoic_tmp", ".anechoic_runtime", ".anechoic_install"}


def _parts(value, *, overlay):
    if not isinstance(value, str):
        raise LocalReleaseError("prepare-local-path-unsafe")
    path = Path(value)
    if (
        path.is_absolute()
        or not path.parts
        or path.as_posix() != value
        or "\\" in value
        or any(ord(char) < 32 or ord(char) == 127 for char in value)
        or any(
            part == ".."
            or part.casefold() in _PROTECTED
            or part.casefold().startswith(".env")
            or part.casefold().endswith(".env")
            for part in path.parts
        )
        or (
            overlay and any(part.casefold() in _RUNTIME for part in path.parts)
        )
    ):
        raise LocalReleaseError("prepare-local-path-unsafe")
    return path


def _open_source(root, relative):
    flags = os.O_RDONLY | os.O_NOFOLLOW
    with ExitStack() as directories:
        parent = os.open(root, flags | os.O_DIRECTORY)
        directories.callback(os.close, parent)
        for part in relative.parts[:-1]:
            parent = os.open(part, flags | os.O_DIRECTORY, dir_fd=parent)
            directories.callback(os.close, parent)
        return os.open(relative.name, flags | os.O_NONBLOCK, dir_fd=parent)


def _version(info):
    return (
        info.st_dev,
        info.st_ino,
        info.st_mode,
        info.st_size,
        info.st_mtime_ns,
        info.st_ctime_ns,
    )


def _overlay(root, checkout, relative):
    destination = _project_path(
        checkout, relative, label="prepare-local-destination"
    )
    try:
        descriptor = _open_source(root, relative)
    except FileNotFoundError:
        if not destination.is_file():
            raise LocalReleaseError(
                "prepare-local-deletion-missing-from-base"
            ) from None
        destination.unlink()
        return None
    with os.fdopen(descriptor, "rb") as source:
        before = os.fstat(source.fileno())
        if not stat.S_ISREG(before.st_mode):
            raise LocalReleaseError("prepare-local-source-entry-unsafe")
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("wb") as output:
            shutil.copyfileobj(source, output)
        destination.chmod(0o755 if before.st_mode & stat.S_IXUSR else 0o644)
        source.seek(0)
        digest = file_digest(source, "sha256").hexdigest()
        if _version(before) != _version(os.fstat(source.fileno())):
            raise LocalReleaseError("prepare-local-source-changed")
        return digest
