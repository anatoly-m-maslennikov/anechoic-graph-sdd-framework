"""Read legacy Settings for the selected Project."""

from __future__ import annotations

from collections.abc import Callable, Iterator, Mapping
from contextlib import contextmanager
from contextvars import ContextVar
from pathlib import Path
import re
import tomllib
from typing import Any

from .ADAPTERS_C30__pub import CEILINGS, ReadContext
from .settings_carrier__pub import read_settings_carrier


_SELECTION: ContextVar[
    tuple[Any, Callable[[Any, str | Path], None]] | None
] = ContextVar("anechoic_project_selection", default=None)


@contextmanager
def bind_settings_selection(
    selection: Any, validate_root: Callable[[Any, str | Path], None]
) -> Iterator[Any]:
    token = _SELECTION.set((selection, validate_root))
    try:
        yield selection
    finally:
        _SELECTION.reset(token)


def bound_selection(root: str | Path | None = None) -> Any | None:
    binding = _SELECTION.get()
    if binding is None:
        return None
    selection, validate_root = binding
    if root is not None:
        validate_root(selection, root)
    return selection


_SETTINGS_PATH = Path(".anechoic_anechoic/anechoic_project_settings.toml")
_CONTROL_ROOT = Path(".anechoic_anechoic")


class ProjectSettingsValueError(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


def _settings(root: Path) -> Mapping[str, Any]:
    root = root.resolve()
    selection = bound_selection(root)
    if selection is not None:
        return selection.settings
    try:
        reader = ReadContext(roots=[str(root)], limits=dict(CEILINGS))
        return read_settings_carrier(
            root / _SETTINGS_PATH, read_bytes=reader.read
        )
    except (
        OSError,
        RuntimeError,
        UnicodeError,
        tomllib.TOMLDecodeError,
    ) as error:
        raise ProjectSettingsValueError(
            "project-settings-unavailable",
            "cannot read current Project Settings",
        ) from error


def control_root(root: Path) -> Path:
    "Return the selected control root or the one canonical unbound carrier root."
    root = root.resolve()
    selection = bound_selection(root)
    if selection is not None:
        return selection.control_root
    settings = _settings(root)
    configured = settings.get("paths", {}).get("control_root")
    candidate = (
        Path(configured)
        if isinstance(configured, str) and configured
        else None
    )
    if (
        candidate is None
        or candidate.is_absolute()
        or ".." in candidate.parts
        or candidate != _CONTROL_ROOT
    ):
        raise ProjectSettingsValueError(
            "project-settings-invalid",
            "paths.control_root must be .anechoic_anechoic",
        )
    return (root / candidate).resolve()


def project_identity_prefix(root: Path) -> str:
    """Return the selected or canonical-carrier Project Atom prefix."""
    return project_identity(root)[0]


def project_identity(
    root: Path, *, control_relative: Path | None = None
) -> tuple[str, str | None]:
    "Return the Atom prefix and the Project name from the same Settings read."
    settings = _settings(root)
    prefix = (
        settings.get("artifacts", {}).get("identity", {}).get("project_prefix")
    )
    if (
        not isinstance(prefix, str)
        or re.fullmatch(r"[A-Za-z0-9]+", prefix) is None
    ):
        raise ProjectSettingsValueError(
            "project-settings-invalid",
            "artifacts.identity.project_prefix is invalid",
        )
    project = settings.get("project")
    name = project.get("name") if isinstance(project, Mapping) else None
    paths = settings.get("paths")
    if control_relative is not None and (
        not isinstance(paths, Mapping)
        or paths.get("control_root") != control_relative.as_posix()
    ):
        name = None
    return prefix, name if isinstance(name, str) and name else None
