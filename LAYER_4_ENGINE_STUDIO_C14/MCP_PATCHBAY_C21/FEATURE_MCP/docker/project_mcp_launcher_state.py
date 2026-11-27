"""Project-local launcher locks, legacy fence, and safe metadata."""

from contextlib import contextmanager
import fcntl
import json
import os
from pathlib import Path
import time
from typing import Any, Iterator, Mapping

from MCP_PATCHBAY_C21.FEATURE_MCP.docker.project_mcp_launcher_common import (
    LaunchError,
    _FINGERPRINT,
    _selection_root,
)

_LOCK_RETRY_SECONDS = 0.01
_SAFE_RESULT_KEYS = (
    "disposition",
    "condition",
    "project_root",
    "control_root",
    "project_id",
    "image_id",
    "fingerprint",
    "container_id",
    "service",
    "port",
    "readiness",
)


def _state_root(selection: object) -> Path:
    root = _selection_root(selection)
    value = getattr(selection, "launcher_state", None)
    if value is None:
        instance = getattr(selection, "instance_id", "")
        if (
            not isinstance(instance, str)
            or _FINGERPRINT.fullmatch(instance) is None
        ):
            raise LaunchError("PROJECT_SELECTION_REFUSED")
        value = (
            root / ".anechoic_runtime" / "runtime" / "project_mcp" / instance
        )
    try:
        state = Path(value)
        relative = state.relative_to(root)
    except (TypeError, ValueError) as error:
        raise LaunchError("PROJECT_SELECTION_REFUSED") from error
    if not relative.parts:
        raise LaunchError("PROJECT_SELECTION_REFUSED")
    current = root
    try:
        for part in relative.parts:
            current = current / part
            if os.path.lexists(current):
                if current.is_symlink() or not current.is_dir():
                    raise LaunchError("PROJECT_SELECTION_REFUSED")
            else:
                current.mkdir(mode=0o700)
        return state
    except LaunchError:
        raise
    except OSError as error:
        raise LaunchError("PROJECT_SELECTION_REFUSED") from error


@contextmanager
def _project_lock(selection: object, timeout: float) -> Iterator[None]:
    """Hold one non-blocking flock for the selected Project identity."""
    state = _state_root(selection)
    lock_path = state / "launch.lock"
    descriptor = None
    deadline = time.monotonic() + timeout
    try:
        flags = os.O_RDWR | os.O_CREAT
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        descriptor = os.open(lock_path, flags, 0o600)
        while True:
            try:
                fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise LaunchError("PROJECT_LOCK_BUSY")
                time.sleep(min(_LOCK_RETRY_SECONDS, remaining))
        yield
    except LaunchError:
        raise
    except OSError as error:
        raise LaunchError("PROJECT_SELECTION_REFUSED") from error
    finally:
        if descriptor is not None:
            try:
                fcntl.flock(descriptor, fcntl.LOCK_UN)
            except OSError:
                pass
            os.close(descriptor)


class _LegacyProcessFence:
    """Keep the launch writer fence held while retained coverage is open."""

    def __init__(self, admission: object, deadline: float) -> None:
        selection = getattr(admission, "selection", None)
        root = getattr(admission, "project_root", None)
        instance = getattr(admission, "project_instance_id", None)
        remaining = deadline - time.monotonic()
        if (
            selection is None
            or getattr(selection, "root", None) != root
            or getattr(selection, "instance_id", None) != instance
            or remaining <= 0
        ):
            raise LaunchError("PROJECT_SELECTION_REFUSED")
        self._admission = admission
        self._lock = _project_lock(selection, min(30.0, remaining))
        self._lock.__enter__()
        self._closed = False

    def snapshot(self, deadline: float):
        if self._closed or time.monotonic() >= deadline:
            return {"outcome": "unavailable", "records": []}
        from MCP_PATCHBAY_C21.FEATURE_MCP.docker.project_mcp_backend import (
            collect_legacy_processes,
        )

        return collect_legacy_processes(self._admission, deadline)

    def close(self) -> None:
        if not self._closed:
            self._closed = True
            self._lock.__exit__(None, None, None)


def open_legacy_process_fence(
    admission: object, deadline: float
) -> _LegacyProcessFence:
    """Acquire the same Project-MCP writer fence used by launch/start."""
    return _LegacyProcessFence(admission, deadline)


def _atomic_metadata(
    state: Path, name: str, payload: Mapping[str, Any]
) -> None:
    """Replace a fixed, Project-local metadata file without following links."""
    target = state / name
    temporary = state / ("." + name + "." + str(os.getpid()) + ".tmp")
    descriptor = None
    try:
        if os.path.lexists(target) and (
            target.is_symlink() or not target.is_file()
        ):
            return
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        descriptor = os.open(temporary, flags, 0o600)
        encoded = (
            json.dumps(
                dict(payload),
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=True,
            )
            + "\n"
        ).encode("utf-8")
        os.write(descriptor, encoded)
        os.fsync(descriptor)
        os.close(descriptor)
        descriptor = None
        os.replace(temporary, target)
    except OSError, TypeError, ValueError:
        if descriptor is not None:
            os.close(descriptor)
        try:
            temporary.unlink(missing_ok=True)
        except OSError:
            pass


def _record_safe_metadata(
    selection: object, result: Mapping[str, Any]
) -> None:
    ("Persist only attributable lifecycle metadata; "
     "credentials and URL stay out.")  # fmt: skip
    try:
        state = _state_root(selection)
        metadata = {key: result.get(key) for key in _SAFE_RESULT_KEYS}
        _atomic_metadata(state, "last_launch.json", metadata)
        if result.get("readiness") is True:
            _atomic_metadata(state, "ready.json", metadata)
    except LaunchError, OSError, TypeError, ValueError:
        pass
