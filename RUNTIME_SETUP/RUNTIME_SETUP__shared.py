"""Read or create machine-local Runtime Setup settings."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import os
from pathlib import Path
import stat
import tempfile
import tomllib


_MAX_SETTINGS_BYTES = 4096


@dataclass(frozen=True)
class Settings:
    path: Path
    folder: Path
    single_project: bool
    port: int
    workbench_storage: str
    journal_storage: str


def _path(supplied: Path | None) -> Path:
    base = os.environ.get("XDG_CONFIG_HOME") or str(Path.home() / ".config")
    path = (supplied or Path(base) / "anechoic/runtime.toml").expanduser()
    return path.parent.resolve() / path.name


def _read(path: Path) -> dict | None:
    try:
        descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    except FileNotFoundError:
        return None
    with os.fdopen(descriptor, "rb") as stream:
        mode = os.fstat(stream.fileno()).st_mode
        if not stat.S_ISREG(mode) or mode & 0o022:
            raise ValueError("Settings must be a regular file writable only by its owner")
        raw = stream.read(_MAX_SETTINGS_BYTES + 1)
    if len(raw) > _MAX_SETTINGS_BYTES:
        raise ValueError("Runtime settings exceed the size limit")
    return tomllib.loads(raw.decode("utf-8"))


def _folder(value: Path | str) -> Path:
    path = Path(value).expanduser()
    if path.is_symlink():
        raise ValueError("Use the repository folder itself")
    folder = path.resolve(strict=True)
    if not folder.is_dir() or folder == Path(folder.anchor) or any(ord(ch) < 32 for ch in str(folder)):
        raise ValueError("Select an existing repository or repositories directory")
    return folder


def _validate(values: Settings) -> Settings:
    if type(values.port) is not int or not 1 <= values.port <= 65535:
        raise ValueError("The HTTP port must be between 1 and 65535")
    if values.workbench_storage not in ("disk", "memory") or values.journal_storage not in ("files", "duckdb"):
        raise ValueError("Invalid Project storage defaults")
    return values


def _existing(path: Path, document: dict) -> Settings:
    if type(document.get("schema_version")) is not int or document["schema_version"] != 1:
        raise ValueError("Runtime settings require schema_version = 1")
    shared = document.get("shared_mcp")
    defaults = document.get("project_defaults", {})
    if not isinstance(shared, dict) or not isinstance(defaults, dict):
        raise ValueError("Invalid runtime settings sections")
    if (document.keys() - {"schema_version", "shared_mcp", "project_defaults"}
            or shared.keys() - {"project_root", "projects_root", "http_port", "max_loaded_projects"}
            or defaults.keys() - {"workbench_storage", "journal_storage"}):
        raise ValueError("Unrecognized runtime settings keys")
    maximum = shared.get("max_loaded_projects", 2)
    if type(maximum) is not int or not 1 <= maximum <= 64:
        raise ValueError("max_loaded_projects must be between 1 and 64")
    modes = set(shared) & {"project_root", "projects_root"}
    if len(modes) != 1:
        raise ValueError("Set either project_root or projects_root in [shared_mcp]")
    key = next(iter(modes))
    value = shared[key]
    if not isinstance(value, str) or not Path(value).is_absolute():
        raise ValueError("The configured repository directory must be an absolute path")
    return _validate(Settings(
        path, _folder(value), key == "project_root", shared.get("http_port"),
        defaults.get("workbench_storage", "disk"), defaults.get("journal_storage", "files"),
    ))


def select_settings(arguments: argparse.Namespace) -> tuple[Settings, bool]:
    path = _path(arguments.settings)
    directory = arguments.project or arguments.projects_root
    selected = _folder(directory) if directory is not None else None
    document = _read(path)
    if document is None:
        if selected is None:
            raise ValueError("Choose --project or --projects-root for the first installation")
        return _validate(Settings(
            path, selected, arguments.project is not None,
            arguments.port if arguments.port is not None else 8092,
            arguments.workbench_storage or "disk", arguments.journal_storage or "files",
        )), True
    values = _existing(path, document)
    if selected is not None and (selected != values.folder or (arguments.project is not None) != values.single_project):
        raise ValueError("The selected folder conflicts with existing settings. Use a different --settings file.")
    for name in ("port", "workbench_storage", "journal_storage"):
        chosen = getattr(arguments, name)
        if chosen is not None and chosen != getattr(values, name):
            raise ValueError("An option conflicts with existing settings. Edit the settings file before retrying.")
    return values, False


def write_settings(values: Settings) -> None:
    key = "project_root" if values.single_project else "projects_root"
    content = (
        "schema_version = 1\n\n"
        f"[shared_mcp]\n{key} = {json.dumps(str(values.folder), ensure_ascii=False)}\nhttp_port = {values.port}\n\n"
        f'[project_defaults]\nworkbench_storage = "{values.workbench_storage}"\n'
        f'journal_storage = "{values.journal_storage}"\n'
    )
    if len(content.encode()) > _MAX_SETTINGS_BYTES:
        raise ValueError("The settings path values exceed the size limit")
    values.path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=values.path.parent, delete=False) as stream:
        temporary = Path(stream.name)
        try:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
            os.link(temporary, values.path, follow_symlinks=False)
        finally:
            temporary.unlink()
