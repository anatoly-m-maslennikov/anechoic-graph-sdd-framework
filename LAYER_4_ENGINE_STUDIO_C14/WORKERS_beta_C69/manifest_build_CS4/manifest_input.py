"""Validate Manifest bindings and read pinned inputs."""

import os
import re
import stat
from hashlib import sha256
from pathlib import Path, PurePosixPath

FIELDS = {
    "root",
    "control_root",
    "manifest_path",
    "manifest_sha256",
    "project_prefix",
}
_COMPONENT_DIRECTORY = re.compile(r"(?!__).+_C[0-9]+$")
_TIER_ONE_DIRECTORY = re.compile(r"01_[A-Z][A-Z0-9_]*$")


def _validate_binding(binding):
    if (
        not isinstance(binding, dict)
        or set(binding) != FIELDS
        or not all(isinstance(v, str) for v in binding.values())
    ):
        raise ValueError("Invalid binding fields")
    root = Path(binding["root"])
    path = PurePosixPath(binding["manifest_path"])
    control = PurePosixPath(binding["control_root"])
    if (
        not root.is_absolute()
        or root.as_posix() != binding["root"]
        or root.resolve(strict=True) != root
        or control.is_absolute()
        or len(control.parts) != 1
        or control.name != binding["control_root"]
        or control.name == ".."
        or not binding["manifest_path"]
        or path.is_absolute()
        or path.as_posix() != binding["manifest_path"]
        or any(part in {".", ".."} for part in path.parts)
        or (len(path.parts) > 1 and path.parts[0] != control.name)
        or not re.fullmatch(r"[0-9a-f]{64}", binding["manifest_sha256"])
        or not re.fullmatch(r"[A-Z][A-Z0-9]*", binding["project_prefix"])
    ):
        raise ValueError("Invalid binding identity or path")


def validate(binding, output):
    _validate_binding(binding)
    control = Path(binding["root"]) / binding["control_root"]
    if (
        not output.is_absolute()
        or output.is_symlink()
        or not output.is_dir()
        or output.resolve(strict=True) != output
        or any(output.iterdir())
    ):
        raise ValueError(
            "Output must be an existing empty canonical directory"
        )
    if output == control or control in output.parents:
        raise ValueError("Output must be outside the Project control root")


def _bound_manifest(binding):
    control = Path(binding["root"]) / binding["control_root"]
    manifest = Path(binding["root"]) / binding["manifest_path"]
    if (
        not manifest.exists()
        and len(PurePosixPath(binding["manifest_path"]).parts) == 1
    ):
        manifest = control / binding["manifest_path"]
    return manifest


def _open_path(path, *, directory=False):
    if any(
        part == ".env"
        or part.startswith(".env.")
        or part.endswith(".env")
        or part in {".ssh", ".aws", ".gnupg"}
        for part in path.parts
    ):
        raise ValueError("Protected Manifest path")
    descriptor = os.open("/", os.O_RDONLY | os.O_DIRECTORY)
    try:
        for part in path.parts[1:-1]:
            child = os.open(
                part,
                os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                dir_fd=descriptor,
            )
            os.close(descriptor)
            descriptor = child
        flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK
        return os.open(
            path.name,
            flags | (os.O_DIRECTORY if directory else 0),
            dir_fd=descriptor,
        )
    finally:
        os.close(descriptor)


def _read_digest(path, limit):
    descriptor = _open_path(path)
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode) or before.st_size > limit:
            raise ValueError("Invalid Manifest file")
        with os.fdopen(descriptor, "rb", closefd=False) as stream:
            data = stream.read(before.st_size)
        after = os.fstat(descriptor)
    finally:
        os.close(descriptor)
    version = (
        before.st_dev,
        before.st_ino,
        before.st_size,
        before.st_mtime_ns,
        before.st_ctime_ns,
    )
    if len(data) != before.st_size or version != (
        after.st_dev,
        after.st_ino,
        after.st_size,
        after.st_mtime_ns,
        after.st_ctime_ns,
    ):
        raise ValueError("Project Manifest changed during read")
    return sha256(data).hexdigest(), len(data), version


def _directory_candidates(directory, consume):
    descriptor = _open_path(directory, directory=True)
    try:
        names = []
        with os.scandir(descriptor) as entries:
            for entry in entries:
                consume()
                if (
                    entry.name.endswith((".md", ".py"))
                    or _COMPONENT_DIRECTORY.fullmatch(entry.name)
                    or _TIER_ONE_DIRECTORY.fullmatch(entry.name)
                ):
                    names.append(entry.name)
        return names
    finally:
        os.close(descriptor)
