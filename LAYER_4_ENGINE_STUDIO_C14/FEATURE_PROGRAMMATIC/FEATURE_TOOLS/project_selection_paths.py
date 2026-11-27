"""Canonical Project root, control, and identity operations."""

from pathlib import Path
import hashlib
import os
import stat

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared \
    import (
        open_regular,
        protected,
    )  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared \
    import ProjectSelectionError  # fmt: skip

SETTINGS_FILENAME = "anechoic_project_settings.toml"
_CONTROL_PREFIX = ".anechoic_"


def _project_root(value: str | Path) -> Path:
    try:
        raw = Path(value).expanduser()
        if ".." in raw.parts or protected(raw):
            raise ProjectSelectionError("Project root is unsafe")
        path = Path(os.path.abspath(raw))
        if path.resolve(strict=True) != path:
            raise ProjectSelectionError(
                "Project root must not contain a symlink"
            )
        descriptor = open_regular(path, directory=True)
        try:
            if not stat.S_ISDIR(os.fstat(descriptor).st_mode):
                raise ProjectSelectionError("Project root is not a directory")
        finally:
            os.close(descriptor)
        return path
    except ProjectSelectionError:
        raise
    except (OSError, RuntimeError, TypeError, ValueError) as error:
        raise ProjectSelectionError(
            "Project root is unavailable or unsafe"
        ) from error


def _control_relative(value: str | Path) -> Path:
    if not isinstance(value, (str, Path)) or not str(value):
        raise ProjectSelectionError(
            "Control root must name one direct Project child"
        )
    path = Path(value)
    if (
        path.is_absolute()
        or len(path.parts) != 1
        or ".." in path.parts
        or not path.name.startswith(_CONTROL_PREFIX)
        or path.name == _CONTROL_PREFIX
        or str(value) != path.as_posix()
        or protected(path)
    ):
        raise ProjectSelectionError(
            "Control root must name one normalized direct Project child"
        )
    return path


def _control_candidates(root: Path) -> list[Path]:
    descriptor = open_regular(root, directory=True)
    try:
        with os.scandir(descriptor) as entries:
            candidates = []
            for entry in entries:
                if not entry.name.startswith(_CONTROL_PREFIX):
                    continue
                if entry.is_symlink():
                    raise ProjectSelectionError(
                        "Project control candidates must not be symlinks"
                    )
                if not entry.is_dir(follow_symlinks=False):
                    continue
                control = root / entry.name
                if os.path.lexists(control / SETTINGS_FILENAME):
                    candidates.append(_control_relative(entry.name))
            return sorted(candidates)
    finally:
        os.close(descriptor)


def _instance_id(root: Path, relative: Path) -> str:
    return hashlib.sha256(
        f"{root}\0{relative.as_posix()}".encode("utf-8")
    ).hexdigest()
