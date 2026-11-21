"""Bound all reads, reject protected paths, and fingerprint actual inputs."""

from dataclasses import dataclass, field
import hashlib
import os
from pathlib import Path
import stat
import time
from typing import Any


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
    """Open every path component with O_NOFOLLOW to close symlink TOCTOU gaps."""
    descriptor = os.open("/", os.O_RDONLY | os.O_DIRECTORY)
    try:
        for part in path.parts[1:-1]:
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = child
        flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK
        return os.open(path.name, flags | (os.O_DIRECTORY if directory else 0), dir_fd=descriptor)
    finally:
        os.close(descriptor)


@dataclass
class ReadContext:
    roots: list[str]
    limits: dict[str, int]
    started: float = field(default_factory=time.monotonic)
    bytes_read: int = 0
    fingerprints: dict[str, str] = field(default_factory=dict)
    sizes: dict[str, int] = field(default_factory=dict)
    versions: dict[str, tuple[int, ...]] = field(default_factory=dict)
    metadata_inputs: set[str] = field(default_factory=set)
    inventories: dict[str, tuple[str, ...]] = field(default_factory=dict)
    shallow_inventories: dict[str, tuple[str, ...]] = field(default_factory=dict)
    candidates: set[str] = field(default_factory=set)

    def checkpoint(self) -> None:
        if time.monotonic() - self.started >= self.limits["timeout_seconds"]:
            raise LimitReached("timeout_seconds")

    def allowed(self, path: Path) -> Path:
        self.checkpoint()
        normalized = Path(os.path.abspath(path))
        if protected(normalized):
            raise ReadFailure("Protected path.")
        if not any(normalized.is_relative_to(Path(root)) for root in self.roots):
            raise ReadFailure("Path is outside allowed_read_roots.")
        if normalized.resolve() != normalized:
            raise ReadFailure("Symlink paths are not admitted.")
        return normalized

    def read(self, path: Path, *, remember: bool = True, directory_fd: int | None = None,
             metadata_guard: bool = False, skip_version: tuple[int, ...] | None = None) -> bytes | None:
        if directory_fd is None:
            path = self.allowed(path)
            descriptor = open_regular(path)
        else:
            self.checkpoint()
            if protected(path) or not any(path.is_relative_to(root) for root in self.roots):
                raise ReadFailure("Path is outside the admitted read boundary.")
            descriptor = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory_fd)
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
            self.check_size(info.st_size)
            raw = stream.read(info.st_size)
            self.bytes_read += len(raw)
            self.checkpoint()
            after = os.fstat(stream.fileno())
            if self.version(after) != version:
                raise ReadFailure("Input changed during read.")
        if remember and not metadata_guard:
            self.fingerprints.setdefault(str(path), hashlib.sha256(raw).hexdigest())
            self.sizes[str(path)] = len(raw)
        return raw

    @staticmethod
    def version(info: os.stat_result) -> tuple[int, ...]:
        return (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns)

    def check_size(self, size: int) -> None:
        if size > self.limits["max_file_bytes"]:
            raise LimitReached("max_file_bytes")
        if self.bytes_read + size > self.limits["max_total_read_bytes"]:
            raise LimitReached("max_total_read_bytes")

    def inventory(self, root: Path, *, remember: bool = True,
                  versions: dict[str, tuple[int, ...]] | None = None) -> list[Path]:
        root = self.allowed(root)
        pending = [root]
        found: list[Path] = []
        while pending:
            path = pending.pop()
            self.checkpoint()
            try:
                info = path.lstat()
            except OSError:
                if versions is not None:
                    raise
                info = None
            mode = info.st_mode if info is not None else 0
            if stat.S_ISDIR(mode):
                self.allowed(path)
                descriptor = open_regular(path, directory=True)
                try:
                    with os.scandir(descriptor) as entries:
                        for entry in entries:
                            self.checkpoint()
                            if entry.name != ".DS_Store":
                                pending.append(path / entry.name)
                            if len(pending) > 1_000_000:
                                raise ReadFailure("Directory traversal exceeds host ceiling.")
                finally:
                    os.close(descriptor)
            elif stat.S_ISLNK(mode) or path.suffix.lower() == ".md" or protected(path):
                found.append(path)
                if versions is not None and info is not None:
                    versions[str(path)] = self.version(info)
            if len(found) > self.limits["max_candidates"]:
                raise LimitReached("max_candidates")
        names = tuple(sorted(str(path) for path in found))
        if remember:
            self.inventories[str(root)] = names
        return [Path(name) for name in names]

    def discover(self, roots: list[str]) -> list[Path]:
        found = set()
        for root in sorted(roots):
            found.update(self.inventory(Path(root)))
            if len(found) > self.limits["max_candidates"]:
                raise LimitReached("max_candidates")
        return sorted(found)

    def inventory_shallow(self, root: Path, *, remember: bool = True) -> list[Path]:
        root = self.allowed(root)
        descriptor = open_regular(root, directory=True)
        try:
            names = []
            with os.scandir(descriptor) as entries:
                for count, entry in enumerate(entries, 1):
                    self.checkpoint()
                    if count > self.limits["max_candidates"]:
                        raise LimitReached("max_candidates")
                    if entry.name.endswith(".md"):
                        names.append(str(root / entry.name))
        finally:
            os.close(descriptor)
        members = tuple(sorted(names))
        if remember:
            self.shallow_inventories[str(root)] = members
        return [Path(name) for name in members]

    def currentness(self) -> dict[str, Any]:
        affected: list[dict[str, str]] = []
        for name, digest in sorted(self.fingerprints.items()):
            try:
                current = hashlib.sha256(self.read(Path(name), remember=False)).hexdigest()
            except OSError:
                current = ""
            if current != digest:
                affected.append({"path": name, "sha256": digest})
        for name in sorted(self.metadata_inputs):
            try:
                path = self.allowed(Path(name))
                descriptor = open_regular(path)
                try:
                    info = os.fstat(descriptor)
                    current = self.version(info) if stat.S_ISREG(info.st_mode) else None
                finally:
                    os.close(descriptor)
            except OSError:
                current = None
            if current != self.versions[name]:
                affected.append({"path": name})
        for root, members in sorted(self.inventories.items()):
            try:
                names = tuple(str(path) for path in self.inventory(Path(root), remember=False))
            except OSError:
                names = ()
            if names != members:
                affected.append({"path": root})
        for root, members in sorted(self.shallow_inventories.items()):
            try:
                names = tuple(str(path) for path in self.inventory_shallow(Path(root), remember=False))
            except OSError:
                names = None
            if names != members:
                affected.append({"path": root})
        return {"state": "changed" if affected else "unchanged", "affected_inputs": affected}
