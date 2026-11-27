"""Read or create machine-local Runtime Setup settings."""

from __future__ import annotations

import argparse
from dataclasses import asdict
import json
import os
from pathlib import Path
import stat
import sys

from pydantic import ConfigDict, ValidationError
from pydantic.dataclasses import dataclass

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1] / "LAYER_4_ENGINE_STUDIO_C14")
)

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.container_settings__pub import (
    CONTAINER_SETTINGS_FILENAME,
    ContainerStartupSettings,
    parse_container_settings,
    read_container_settings,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.settings_carrier__pub import (
    parse_settings_carrier,
    write_settings_carrier,
)

_MAX_SETTINGS_BYTES = 4096


@dataclass(frozen=True, config=ConfigDict(strict=True))
class Settings:
    path: Path
    folder: Path
    single_project: bool
    port: int
    workbench_storage: str
    journal_storage: str
    log_level: str = "INFO"
    container: ContainerStartupSettings | None = None


def _settings(*values: object) -> Settings:
    try:
        return Settings(*values)
    except ValidationError as error:
        raise ValueError("Invalid runtime settings values") from error


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
            raise ValueError(
                "Settings must be a regular file writable only by its owner"
            )
        raw = stream.read(_MAX_SETTINGS_BYTES + 1)
    if len(raw) > _MAX_SETTINGS_BYTES:
        raise ValueError("Runtime settings exceed the size limit")
    return parse_settings_carrier(raw)


def _folder(value: Path | str) -> Path:
    path = Path(value).expanduser()
    if path.is_symlink():
        raise ValueError("Use the repository folder itself")
    folder = path.resolve(strict=True)
    if (
        not folder.is_dir()
        or folder == Path(folder.anchor)
        or any(ord(ch) < 32 for ch in str(folder))
    ):
        raise ValueError(
            "Select an existing repository or repositories directory"
        )
    return folder


def _validate(values: Settings) -> Settings:
    if type(values.port) is not int or not 1 <= values.port <= 65535:
        raise ValueError("The HTTP port must be between 1 and 65535")
    if values.workbench_storage not in (
        "disk",
        "memory",
    ) or values.journal_storage not in ("files", "duckdb"):
        raise ValueError("Invalid Project storage defaults")
    if values.log_level not in ("DEBUG", "INFO", "WARNING", "ERROR"):
        raise ValueError("Invalid runtime logging level")
    return values


def _sections(document: dict) -> tuple[dict, dict, dict]:
    if (
        type(document.get("schema_version")) is not int
        or document["schema_version"] != 1
    ):
        raise ValueError("Runtime settings require schema_version = 1")
    shared = document.get("shared_mcp")
    defaults = document.get("project_defaults", {})
    logging = document.get("logging", {})
    if (
        not isinstance(shared, dict)
        or not isinstance(defaults, dict)
        or not isinstance(logging, dict)
    ):
        raise ValueError("Invalid runtime settings sections")
    if (
        document.keys()
        - {"schema_version", "shared_mcp", "project_defaults", "logging"}
        or shared.keys()
        - {"project_root", "projects_root", "http_port", "max_loaded_projects"}
        or defaults.keys() - {"workbench_storage", "journal_storage"}
        or logging.keys() - {"level"}
    ):
        raise ValueError("Unrecognized runtime settings keys")
    return shared, defaults, logging


def _existing(path: Path, document: dict) -> Settings:
    shared, defaults, logging = _sections(document)
    maximum = shared.get("max_loaded_projects", 2)
    if type(maximum) is not int or not 1 <= maximum <= 64:
        raise ValueError("max_loaded_projects must be between 1 and 64")
    modes = set(shared) & {"project_root", "projects_root"}
    if len(modes) != 1:
        raise ValueError(
            "Set either project_root or projects_root in [shared_mcp]"
        )
    key = next(iter(modes))
    value = shared[key]
    if not isinstance(value, str) or not Path(value).is_absolute():
        raise ValueError(
            "The configured repository directory must be an absolute path"
        )
    return _validate(
        _settings(
            path,
            _folder(value),
            key == "project_root",
            shared.get("http_port"),
            defaults.get("workbench_storage", "disk"),
            defaults.get("journal_storage", "files"),
            logging.get("level", "INFO"),
        )
    )


def docker_context(engine: str) -> str:
    if engine == "orbstack":
        return "orbstack"
    return "desktop-linux" if sys.platform == "darwin" else "default"


def _mounted_values(path: Path, config: ContainerStartupSettings) -> Settings:
    return _settings(
        path,
        _folder(path.parent),
        config.mode == "project",
        config.http_port,
        config.workbench_storage,
        config.journal_storage,
        config.log_level,
        config,
    )


def _existing_settings(path: Path) -> Settings | None:
    if path.name == CONTAINER_SETTINGS_FILENAME:
        config = read_container_settings(path.parent)
        return _mounted_values(path, config) if config is not None else None
    document = _read(path)
    if document is None:
        return None
    legacy = _existing(path, document)
    mounted = read_container_settings(legacy.folder)
    if mounted is not None:
        return _mounted_values(legacy.folder / CONTAINER_SETTINGS_FILENAME, mounted)
    return legacy


def _new_settings(path, selected, arguments) -> Settings:
    if selected is None:
        raise ValueError(
            "Choose --project or --projects-root for the first installation"
        )
    single = arguments.project is not None
    port = arguments.port if arguments.port is not None else 8092
    storage = arguments.workbench_storage or "disk"
    journal = arguments.journal_storage or "files"
    if path.name != CONTAINER_SETTINGS_FILENAME:
        return _validate(_settings(path, selected, single, port, storage, journal))
    if path.parent != selected:
        raise ValueError("Container settings must be in the selected mounted folder")
    log_level = "INFO"
    if arguments.settings is None:
        legacy_path = _path(None)
        document = _read(legacy_path)
        if document is not None:
            previous = _existing(legacy_path, document)
            if previous.folder == selected and previous.single_project == single:
                port = previous.port if arguments.port is None else port
                storage = arguments.workbench_storage or previous.workbench_storage
                journal = arguments.journal_storage or previous.journal_storage
                log_level = previous.log_level
    return _mounted_values(
        path,
        ContainerStartupSettings(
            mode="project" if single else "projects",
            http_port=port,
            docker_context=docker_context(arguments.engine),
            workbench_storage=storage,
            journal_storage=journal,
            log_level=log_level,
        ),
    )


def select_settings(arguments: argparse.Namespace) -> tuple[Settings, bool]:
    directory = arguments.project or arguments.projects_root
    selected = _folder(directory) if directory is not None else None
    path = (
        selected / CONTAINER_SETTINGS_FILENAME
        if arguments.settings is None and selected is not None
        else _path(arguments.settings)
    )
    values = _existing_settings(path)
    if values is None:
        return _new_settings(path, selected, arguments), True
    if selected is not None and (
        selected != values.folder
        or (arguments.project is not None) != values.single_project
    ):
        raise ValueError(
            "The selected folder conflicts with existing settings. "
            "Use a different --settings file."
        )
    for name in ("port", "workbench_storage", "journal_storage"):
        chosen = getattr(arguments, name)
        if chosen is not None and chosen != getattr(values, name):
            raise ValueError(
                "An option conflicts with existing settings. Edit the "
                "settings file before retrying."
            )
    return values, False


def write_settings(values: Settings) -> None:
    _validate(values)
    if values.container is not None:
        content = "schema_version = 1\n\n[container]\n" + "".join(
            f"{key} = {json.dumps(value, ensure_ascii=False)}\n"
            for key, value in asdict(values.container).items()
            if value is not None
        )
        write_settings_carrier(
            values.path, content, validate=parse_container_settings,
            replace_existing=False,
        )
        return
    key = "project_root" if values.single_project else "projects_root"
    content = (
        "schema_version = 1\n\n"
        f"[shared_mcp]\n{key} = "
        f"{json.dumps(str(values.folder), ensure_ascii=False)}\n"
        f"http_port = {values.port}\n\n"
        f"[project_defaults]\nworkbench_storage = "
        f'"{values.workbench_storage}"\n'
        f'journal_storage = "{values.journal_storage}"\n'
        f'\n[logging]\nlevel = "{values.log_level}"\n'
    )
    if len(content.encode()) > _MAX_SETTINGS_BYTES:
        raise ValueError("The settings path values exceed the size limit")
    values.path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    write_settings_carrier(
        values.path, content,
        validate=lambda document: _existing(values.path, document),
        replace_existing=False,
    )
