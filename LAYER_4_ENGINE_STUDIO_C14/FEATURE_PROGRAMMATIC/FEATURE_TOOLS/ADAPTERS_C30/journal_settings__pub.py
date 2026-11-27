"""Resolve settings for Project-local Journal storage."""

import datetime as dt
import os
from pathlib import Path
from typing import Any, Mapping
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from .ADAPTERS_C30__pub import CEILINGS, ReadContext, open_regular, protected
from .settings_carrier__pub import read_settings_carrier


def _settings_control_relative(value: str | Path) -> Path:
    path = Path(value)
    if (
        path.is_absolute()
        or len(path.parts) != 1
        or path.name in {".anechoic_", "_anechoic_"}
        or not path.name.startswith((".anechoic_", "_anechoic_"))
        or str(value) != path.as_posix()
        or protected(path)
    ):
        raise RuntimeError(
            "paths.control_root must name one normalized direct Project child"
        )
    return path


def _discover_control_relative(project: Path, descriptor: int) -> Path:
    candidates = []
    with os.scandir(descriptor) as entries:
        for entry in entries:
            if not entry.name.startswith((".anechoic_", "_anechoic_")):
                continue
            if entry.is_symlink():
                raise RuntimeError(
                    "Project control candidates must not be symlinks"
                )
            if entry.is_dir(follow_symlinks=False) and os.path.lexists(
                project / entry.name / "anechoic_project_settings.toml"
            ):
                candidates.append(_settings_control_relative(entry.name))
    if len(candidates) != 1:
        raise RuntimeError(
            "Project Settings control root is missing or ambiguous"
        )
    return candidates[0]


def _read_project_settings(
    root: Path, control_root: str | Path | None = None
) -> tuple[Path, dict[str, Any]]:
    """Read one Project-local settings carrier without repository fallback."""
    try:
        supplied = Path(root).expanduser()
        if (
            ".." in supplied.parts
            or protected(supplied)
            or supplied.is_symlink()
        ):
            raise RuntimeError("Project root must not be unsafe or a symlink")
        project = supplied.resolve(strict=True)
        if protected(project):
            raise RuntimeError("Project root is protected")
        descriptor = open_regular(project, directory=True)
        try:
            if control_root is None:
                relative = _discover_control_relative(project, descriptor)
            else:
                relative = _settings_control_relative(control_root)
        finally:
            os.close(descriptor)
        settings_path = project / relative / "anechoic_project_settings.toml"
        reader = ReadContext(roots=[str(project)], limits=dict(CEILINGS))
        settings = read_settings_carrier(settings_path, read_bytes=reader.read)
        paths = settings.get("paths")
        if not isinstance(paths, dict):
            raise RuntimeError("Project Settings requires a paths table")
        declared = paths.get("control_root")
        if not isinstance(declared, str) or not declared:
            raise RuntimeError("Project Settings requires paths.control_root")
        if _settings_control_relative(declared) != relative:
            raise RuntimeError(
                "paths.control_root must be exactly the selected settings carrier's Project child"
            )
        if reader.currentness()["state"] != "unchanged":
            raise RuntimeError("Project Settings changed during resolution")
        return settings_path, settings
    except (OSError, UnicodeError, ValueError) as error:
        raise RuntimeError(
            "Project Settings carrier is unavailable, invalid, or unsafe"
        ) from error


def _assert_project_relative_path(
    root: Path, relative: Path, label: str
) -> None:
    project = root.resolve(strict=True)
    path = project / relative
    if path.resolve() != path:
        raise RuntimeError(
            f"{label} must not contain a symlink or escape the Project root"
        )


def current_timestamp(root: Path) -> str:
    _, settings = _read_project_settings(root)
    value = settings.get("artifact_timestamps", {}).get("timezone", "local")
    if value == "local":
        moment = dt.datetime.now().astimezone()
    elif value == "UTC":
        moment = dt.datetime.now(dt.UTC)
    else:
        try:
            moment = dt.datetime.now(ZoneInfo(value))
        except ZoneInfoNotFoundError as error:
            raise RuntimeError(
                f"unknown artifact timestamp timezone: {value}"
            ) from error
    return moment.strftime("%Y-%m-%d %H:%M:%S %z")


def journal_storage(parameters: Mapping[str, Any]) -> str:
    value: object = parameters
    for key in ("runtime", "journal"):
        if not isinstance(value, Mapping):
            raise ValueError("runtime.journal.storage must be files or duckdb")
        value = value.get(key, {})
    if not isinstance(value, Mapping):
        raise ValueError("runtime.journal.storage must be files or duckdb")
    storage = value.get("storage", "files")
    if storage not in ("files", "duckdb"):
        raise ValueError("runtime.journal.storage must be files or duckdb")
    return storage


def configured_journal_root(
    root: Path, *, control_root: str | Path | None = None
) -> Path:
    _, settings = _read_project_settings(root, control_root)
    paths = settings.get("paths", {})
    control_value = paths.get("control_root")
    if not isinstance(control_value, str) or not control_value:
        raise RuntimeError("Project Settings requires paths.control_root")
    control = Path(control_value)
    if control.is_absolute() or ".." in control.parts or not control.parts:
        raise RuntimeError(
            "paths.control_root must be a safe repository-relative path"
        )
    canonical = control / "_journal"
    value = paths.get("journal_root", canonical.as_posix())
    if not isinstance(value, str) or not value:
        raise RuntimeError(
            "paths.journal_root must be a non-empty string when provided"
        )
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        raise RuntimeError(
            "paths.journal_root must be a safe repository-relative path"
        )
    if path != canonical:
        raise RuntimeError(
            "paths.journal_root must be exactly paths.control_root/_journal"
        )
    return validated_journal_root(root, canonical.as_posix())


def validated_journal_root(root: Path, value: object) -> Path:
    """Validate an explicitly selected Project-relative Journal location."""
    if not isinstance(value, str) or not value:
        raise RuntimeError("paths.journal_root must be a non-empty string")
    path = Path(value)
    if (
        path.is_absolute()
        or not path.parts
        or ".." in path.parts
        or value != path.as_posix()
        or protected(path)
    ):
        raise RuntimeError(
            "paths.journal_root must be a safe repository-relative path"
        )
    _assert_project_relative_path(root, path, "paths.journal_root")
    return path
