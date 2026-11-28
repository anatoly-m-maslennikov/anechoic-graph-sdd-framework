"""Private mechanical effects for already admitted lifecycle operations.

Callers must exclude concurrent writers to pinned source files. Portable file
APIs cannot conditionally replace or unlink by digest. Lifecycle choices belong
to the caller; this module accepts project-contained paths and bytes only.
"""

from __future__ import annotations


import fcntl as fcntl
import hashlib
import os
import re as re
import stat as stat
from contextlib import contextmanager as contextmanager, nullcontext
from dataclasses import field
from pathlib import Path

from . import effects_io as _io

from pydantic import ConfigDict, field_validator
from pydantic.dataclasses import dataclass

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.settings.project.project__shared import (
    atomic_tempfile,
    owned_temporary_root as owned_temporary_root,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.\
    PROJECT_SUPPORT.RUNTIME_SUPPORT.\
    RUNTIME_SUPPORT__shared import (
    repository_root as repository_root,
)
from ..ADAPTERS_C30.ADAPTERS_C30__shared import (
    open_regular as open_regular,
)


def _project_write_lock(root):
    return _io._project_write_lock(root)


@dataclass(config=ConfigDict(strict=True, extra="forbid"))
class Result:
    effects: list[dict[str, object]] = field(default_factory=list)
    errors: list[dict[str, object]] = field(default_factory=list)

    @field_validator("effects", "errors", mode="wrap")
    @classmethod
    def _preserve_receipts(cls, value, validate):
        validate(value)
        return value


def _error(result: Result, code: str, message: str) -> None:
    result.errors.append({"code": code, "message": message, "field": None})


def _effect(
    result: Result, operation: str, target: str, state: str, evidence: str
) -> None:
    result.effects.append(
        {
            "operation": operation,
            "target": target,
            "state": state,
            "evidence": evidence,
        }
    )


def _parent(root: Path, path: Path) -> tuple[int, str, str]:
    return _io._parent(root, path)


def _read(parent: int, name: str) -> bytes:
    return _io._read(parent, name)


def _pinned(parent: int, name: str, digest: str) -> bytes:
    return _io._pinned(parent, name, digest)


def _reader(path: Path):
    return _io._reader(path)


def publication_guard():
    return _io.publication_guard()


def _query_read(
    reader, root: Path, path: Path, parent: int, name: str
) -> bytes:
    return _io._query_read(reader, root, path, parent, name)


def _read_pinned(
    reader, root: Path, path: Path, parent: int, name: str, digest: str
) -> bytes:
    return _io._read_pinned(reader, root, path, parent, name, digest)


def _changed(reader, old: Path | None, new: Path | None) -> None:
    return _io._changed(reader, old, new)


def _message(exc: Exception) -> str:
    return _io._message(exc)


def _cleanup_temp(root: Path, temp: str | None, result: Result) -> None:
    return _io._cleanup_temp(root, temp, result)


class _DestinationExists(FileExistsError):
    pass


def _publish_new(temp, name, parent):
    try:
        os.link(temp, name, dst_dir_fd=parent, follow_symlinks=False)
    except FileExistsError as exc:
        raise _DestinationExists() from exc


def _write_error(result, operation, target, committed, exc):
    if committed:
        _effect(
            result,
            operation,
            target,
            "unknown",
            "publication occurred but synchronization or readback failed",
        )
        _error(result, "effect_uncertain", _message(exc))
    else:
        _error(
            result,
            "stale_state"
            if isinstance(exc, (ValueError, FileExistsError))
            else "backend_failure",
            "Destination already exists."
            if isinstance(exc, _DestinationExists)
            else _message(exc),
        )


def _write_bytes(fd, data):
    with os.fdopen(fd, "wb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())


@dataclass(config=ConfigDict(strict=True, extra="forbid"))
class _WriteState:
    temp: str | None = None
    parent: int | None = None
    target: str | None = None
    committed: bool = False


def _verify_written(reader, root, destination, parent, name, data, readback):
    if readback is None:
        readback = (
            _query_read(reader, root, destination, parent, name)
            if reader is not None
            else _read(parent, name)
        )
    if readback != data:
        raise OSError("readback differs")


def _perform_write(root, path, data, expected, result, operation, state):
    readback = None
    parent, name, target = _parent(root, path)
    state.parent, state.target = parent, target
    destination = Path(root).absolute() / target
    reader = _reader(destination)
    if expected is not None:
        old = _read_pinned(reader, root, destination, parent, name, expected)
        if old == data:
            return
    fd, temp = atomic_tempfile(
        repository_root(root), destination, "atom_lifecycle"
    )
    state.temp = temp
    _write_bytes(fd, data)
    if expected is None:
        lock = getattr(reader, "lifecycle_file_effect", None)
        with lock() if callable(lock) else nullcontext():
            _publish_new(temp, name, parent)
            state.committed = True
            if reader is None:
                readback = _read(parent, name)
            staging, temp = temp, None
            state.temp = None
            Path(staging).unlink(missing_ok=True)
    else:
        _read_pinned(reader, root, destination, parent, name, expected)
        os.replace(temp, name, dst_dir_fd=parent)
        temp = None
        state.temp, state.committed = None, True
    _changed(
        reader, destination if expected is not None else None, destination
    )
    _verify_written(reader, root, destination, parent, name, data, readback)
    _effect(
        result,
        operation,
        target,
        "known",
        hashlib.sha256(data).hexdigest(),
    )


def _write(
    root: Path, path: Path, data: bytes, expected: str | None, result: Result
) -> None:
    state = _WriteState()
    operation = "create" if expected is None else "modify"
    try:
        _perform_write(root, path, data, expected, result, operation, state)
    except (OSError, ValueError, RuntimeError) as exc:
        _write_error(result, operation, state.target, state.committed, exc)
    finally:
        if state.parent is not None:
            os.close(state.parent)
        _cleanup_temp(root, state.temp, result)


def create(root: Path, path: Path, content: bytes) -> Result:
    result = Result()
    _write(Path(root), Path(path), content, None, result)
    return result


def replace(
    root: Path, path: Path, expected_sha256: str, content: bytes
) -> Result:
    result = Result()
    _write(Path(root), Path(path), content, expected_sha256, result)
    return result


def _remove_error(result, target, committed, exc):
    if committed:
        _effect(
            result,
            "remove",
            target,
            "unknown",
            "removal occurred but synchronization or readback failed",
        )
        _error(result, "effect_uncertain", _message(exc))
    else:
        _error(
            result,
            "stale_state"
            if isinstance(exc, ValueError)
            else "backend_failure",
            _message(exc),
        )


def remove(root: Path, path: Path, expected_sha256: str) -> Result:
    result = Result()
    parent = None
    committed = False
    target = None
    try:
        parent, name, target = _parent(Path(root), Path(path))
        destination = Path(root).absolute() / target
        reader = _reader(destination)
        _read_pinned(
            reader, Path(root), destination, parent, name, expected_sha256
        )
        os.unlink(name, dir_fd=parent)
        committed = True
        _changed(reader, destination, None)
        try:
            os.stat(name, dir_fd=parent, follow_symlinks=False)
        except FileNotFoundError:
            pass
        else:
            raise OSError("source remains after removal")
        _effect(
            result,
            "remove",
            target,
            "known",
            f"absent after removal; prior sha256 {expected_sha256}",
        )
    except (OSError, ValueError, RuntimeError) as exc:
        _remove_error(result, target, committed, exc)
    finally:
        if parent is not None:
            os.close(parent)
    return result


def relocate(
    root: Path, source: Path, expected_sha256: str, destination: Path
) -> Result:
    result = Result()
    parent = None
    try:
        parent, name, target = _parent(Path(root), Path(source))
        source_path = Path(root).absolute() / target
        content = _read_pinned(
            _reader(source_path),
            Path(root),
            source_path,
            parent,
            name,
            expected_sha256,
        )
    except (OSError, ValueError, RuntimeError) as exc:
        _error(
            result,
            "stale_state"
            if isinstance(exc, ValueError)
            else "backend_failure",
            _message(exc),
        )
        return result
    finally:
        if parent is not None:
            os.close(parent)
    _write(Path(root), Path(destination), content, None, result)
    if not result.errors:
        removed = remove(root, source, expected_sha256)
        result.effects.extend(removed.effects)
        result.errors.extend(removed.errors)
    return result
