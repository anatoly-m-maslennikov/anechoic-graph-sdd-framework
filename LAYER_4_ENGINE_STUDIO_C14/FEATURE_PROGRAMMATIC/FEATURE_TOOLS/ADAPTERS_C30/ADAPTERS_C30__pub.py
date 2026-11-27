"""Bound all reads, reject protected paths, and fingerprint actual inputs."""

from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor as ThreadPoolExecutor
from dataclasses import field
import hashlib
from itertools import groupby as groupby
import os
from pathlib import Path
import stat
import sys
from threading import Lock
import time
from typing import Any

from pydantic import (
    ConfigDict,
    InstanceOf,
    ValidatorFunctionWrapHandler,
    field_validator,
)
from pydantic.dataclasses import dataclass


__all__ = [
    "CEILINGS",
    "LimitReached",
    "ReadContext",
    "ReadFailure",
    "open_regular",
    "protected",
    "TemporaryBoundaryError",
    "validate_directory_components",
]


CEILINGS = dict(
    max_candidates=1_000_000,
    max_file_bytes=64 * 1024 * 1024,
    max_total_read_bytes=1024 * 1024 * 1024,
    timeout_seconds=300,
    max_findings=100_000,
)


if __package__:
    from .temporary_boundary import (
        TemporaryBoundaryError,
        validate_directory_components,
    )


class ReadFailure(OSError):
    pass


class LimitReached(RuntimeError):
    def __init__(self, limit: str) -> None:
        super().__init__(limit)
        self.limit = limit


def protected(path: Path) -> bool:
    return any(
        part == ".env"
        or part.startswith(".env.")
        or part.endswith(".env")
        or part in {".ssh", ".aws", ".gnupg"}
        for part in path.parts
    )


def open_regular(path: Path, *, directory: bool = False) -> int:
    """Open every path component with O_NOFOLLOW to close \
symlink TOCTOU gaps."""
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


def _remember_fingerprint(reader, path, raw):
    reader.fingerprints.setdefault(str(path), hashlib.sha256(raw).hexdigest())
    reader.sizes[str(path)] = len(raw)


if __package__:
    from .reader_filesystem import _ReaderFilesystem
else:
    from reader_filesystem import _ReaderFilesystem


@dataclass(config=ConfigDict(strict=True, extra="forbid"))
class ReadContext(_ReaderFilesystem):
    roots: list[str]
    limits: dict[str, int]
    started: float = field(default_factory=time.monotonic)
    bytes_read: int = 0
    fingerprints: dict[str, str] = field(default_factory=dict)
    sizes: dict[str, int] = field(default_factory=dict)
    versions: dict[str, tuple[int, ...]] = field(default_factory=dict)
    metadata_inputs: set[str] = field(default_factory=set)
    inventories: dict[str, tuple[str, ...]] = field(default_factory=dict)
    inventory_prunes: dict[str, Callable[[Path], bool]] = field(
        default_factory=dict, init=False
    )
    shallow_inventories: dict[str, tuple[str, ...]] = field(
        default_factory=dict
    )
    candidates: set[str] = field(default_factory=set)
    _read_budget: InstanceOf[Lock] = field(
        default_factory=Lock, init=False, repr=False, compare=False
    )

    @field_validator(
        "roots",
        "limits",
        "started",
        "fingerprints",
        "sizes",
        "versions",
        "metadata_inputs",
        "inventories",
        "shallow_inventories",
        "candidates",
        mode="wrap",
    )
    def _preserve_state(
        cls, value: Any, validate: ValidatorFunctionWrapHandler
    ) -> Any:
        validate(value)
        return value

    def checkpoint(self) -> None:
        if (
            "timeout_seconds" in self.limits
            and time.monotonic() - self.started
            >= self.limits["timeout_seconds"]
            and os.getenv("ANECHOIC_TEST_IMAGE_DEADLINES") != "0"
        ):
            raise LimitReached("timeout_seconds")

    def _allowed_lexical(self, path: Path) -> Path:
        self.checkpoint()
        normalized = Path(os.path.abspath(path))
        if protected(normalized):
            raise ReadFailure("Protected path.")
        if not any(
            normalized.is_relative_to(Path(root)) for root in self.roots
        ):
            raise ReadFailure("Path is outside allowed_read_roots.")
        return normalized

    def allowed(self, path: Path) -> Path:
        normalized = self._allowed_lexical(path)
        if normalized.resolve() != normalized:
            raise ReadFailure("Symlink paths are not admitted.")
        return normalized

    def _open_input(self, path: Path) -> tuple[Path, int]:
        path = self._allowed_lexical(path)
        try:
            return path, open_regular(path)
        except OSError:
            self.allowed(path)
            raise

    def read(
        self,
        path: Path,
        *,
        remember: bool = True,
        directory_fd: int | None = None,
        metadata_guard: bool = False,
        skip_version: tuple[int, ...] | None = None,
    ) -> bytes | None:
        if directory_fd is None:
            path, descriptor = self._open_input(path)
        else:
            self.checkpoint()
            if protected(path) or not any(
                path.is_relative_to(root) for root in self.roots
            ):
                raise ReadFailure(
                    "Path is outside the admitted read boundary."
                )
            descriptor = os.open(
                path.name,
                os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK,
                dir_fd=directory_fd,
            )
        with os.fdopen(descriptor, "rb") as stream:
            info = os.fstat(stream.fileno())
            if not stat.S_ISREG(info.st_mode):
                raise ReadFailure("Input is not a regular file.")
            version = self.version(info)
            if remember:
                self.versions[str(path)] = version
            if metadata_guard:
                self.metadata_inputs.add(str(path))
            if skip_version is not None and version == skip_version:
                return None
            raw = self._read_bytes(stream, info.st_size)
            self.checkpoint()
            after = os.fstat(stream.fileno())
            if self.version(after) != version:
                raise ReadFailure("Input changed during read.")
        if remember and not metadata_guard:
            _remember_fingerprint(self, path, raw)
        return raw

    def _read_bytes(self, stream, size: int) -> bytes:
        with self._read_budget:
            self.check_size(size)
            self.bytes_read += size
        raw = b""
        try:
            raw = stream.read(size)
            return raw
        finally:
            if len(raw) != size:
                with self._read_budget:
                    self.bytes_read -= size - len(raw)

    @staticmethod
    def version(info: os.stat_result) -> tuple[int, ...]:
        return (
            info.st_dev,
            info.st_ino,
            info.st_size,
            info.st_mtime_ns,
            info.st_ctime_ns,
        )

    def check_size(self, size: int) -> None:
        if size > self.limits["max_file_bytes"]:
            raise LimitReached("max_file_bytes")
        if self.bytes_read + size > self.limits["max_total_read_bytes"]:
            raise LimitReached("max_total_read_bytes")


def _main(argv: list[str]) -> int:
    """Read one explicitly named file with a small, fixed ceiling."""
    if (
        len(argv) != 2
        or argv[0] != "--read-bounded"
        or not Path(argv[1]).is_absolute()
    ):
        return 2
    limits = {**CEILINGS, "max_file_bytes": 65536, "timeout_seconds": 5}
    try:
        raw = ReadContext(roots=["/"], limits=limits).read(Path(argv[1]))
        sys.stdout.buffer.write(raw)
        return 0
    except OSError, ValueError, LimitReached:
        return 1


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))
