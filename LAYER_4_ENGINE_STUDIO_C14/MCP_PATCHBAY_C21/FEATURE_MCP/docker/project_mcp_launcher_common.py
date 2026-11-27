"""Shared launcher conditions and selected Project validation."""

from pathlib import Path
import re

_IMAGE = re.compile(r"sha256:[0-9a-f]{64}\Z")
_FINGERPRINT = re.compile(r"[0-9a-f]{64}\Z")
_CONDITIONS = frozenset(
    {
        "READY_STARTED",
        "READY_REUSED",
        "PROJECT_SELECTION_REFUSED",
        "IMAGE_INPUT_UNAVAILABLE",
        "IMAGE_REFUSED",
        "PROJECT_LOCK_BUSY",
        "RUNTIME_MISMATCH",
        "RUNTIME_UNHEALTHY",
        "BUILD_FAILED",
        "DOCKER_START_FAILED",
        "DOCKER_PUBLICATION_FAILED",
        "READINESS_FAILED",
    }
)
_DISPOSITIONS = {
    "READY_STARTED": "started",
    "READY_REUSED": "reused",
    "PROJECT_SELECTION_REFUSED": "refused",
    "IMAGE_INPUT_UNAVAILABLE": "failed",
    "IMAGE_REFUSED": "refused",
    "PROJECT_LOCK_BUSY": "busy",
    "RUNTIME_MISMATCH": "refused",
    "RUNTIME_UNHEALTHY": "refused",
    "BUILD_FAILED": "failed",
    "DOCKER_START_FAILED": "failed",
    "DOCKER_PUBLICATION_FAILED": "failed",
    "READINESS_FAILED": "failed",
}


class LaunchError(RuntimeError):
    """A safe non-secret launcher condition."""

    def __init__(self, code: str = "DOCKER_START_FAILED") -> None:
        self.code = code if code in _CONDITIONS else "DOCKER_START_FAILED"
        super().__init__(self.code)


def _selection_root(selection: object) -> Path:
    root = getattr(selection, "root", getattr(selection, "rootPath", None))
    try:
        path = Path(root)
    except (TypeError, ValueError) as error:
        raise LaunchError("PROJECT_SELECTION_REFUSED") from error
    if not path.is_absolute() or path.is_symlink() or not path.is_dir():
        raise LaunchError("PROJECT_SELECTION_REFUSED")
    return path
