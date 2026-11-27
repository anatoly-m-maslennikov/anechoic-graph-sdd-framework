
"""Read the machine-local shared MCP host configuration."""

from __future__ import annotations

from pydantic import ConfigDict
from pydantic.dataclasses import dataclass

import argparse
from copy import deepcopy
from dataclasses import replace
import hashlib
import json
import os
from pathlib import Path
import stat
import sys
import tomllib
from typing import Any


_MAX_CONFIG_BYTES = 4 * 1024
_MAX_LOADED_PROJECTS = 64
_READ_LIMITS = {
    "max_candidates": 1,
    "max_file_bytes": _MAX_CONFIG_BYTES,
    "max_total_read_bytes": 2 * _MAX_CONFIG_BYTES,
    "timeout_seconds": 5,
    "max_findings": 1,
}


class HostRuntimeConfigError(ValueError):
    """The shared host configuration cannot be trusted or resolved."""


class OutsideProjectRootError(HostRuntimeConfigError):
    """The selected Project is outside the configured host root."""


def _error(message: str) -> HostRuntimeConfigError:
    return HostRuntimeConfigError(message)


def _path(value: Path | str, *, absolute: bool = False) -> Path:
    if not isinstance(value, (Path, str)) or not str(value) or "\x00" in str(value):
        raise _error("Host runtime path is invalid")
    try:
        raw = Path(value).expanduser()
        if ".." in raw.parts or (absolute and not raw.is_absolute()):
            raise _error("Host runtime path is unsafe")
        return Path(os.path.abspath(raw))
    except HostRuntimeConfigError:
        raise
    except (OSError, RuntimeError, TypeError, ValueError) as error:
        raise _error("Host runtime path is unavailable or unsafe") from error


def _canonical_directory(value: Path | str, *, reject_filesystem_root: bool = False) -> Path:
    path = _path(value, absolute=True)
    try:
        if path.resolve(strict=True) != path:
            raise _error("Host runtime directory must be canonical")
        info = path.stat()
        if not stat.S_ISDIR(info.st_mode) or (reject_filesystem_root and path.parent == path):
            raise _error("Host runtime directory is invalid")
        return path
    except HostRuntimeConfigError:
        raise
    except (OSError, RuntimeError, ValueError) as error:
        raise _error("Host runtime directory is unavailable or unsafe") from error


def _canonical_config_path(value: Path | str) -> Path:
    path = _path(value)
    try:
        if path.resolve(strict=True) != path:
            raise _error("Host runtime configuration file must be canonical")
        info = path.lstat()
        if (
            path.is_symlink()
            or not stat.S_ISREG(info.st_mode)
            or stat.S_IMODE(info.st_mode) & 0o022
        ):
            raise _error("Host runtime configuration file is unsafe")
        return path
    except HostRuntimeConfigError:
        raise
    except (OSError, RuntimeError, ValueError) as error:
        raise _error("Host runtime configuration file is unavailable or unsafe") from error


def _read_config(path: Path) -> bytes:
    try:
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import ReadContext

        reader = ReadContext(roots=[str(path.parent)], limits=dict(_READ_LIMITS))
        raw = reader.read(path)
        if reader.currentness()["state"] != "unchanged":
            raise _error("Host runtime configuration changed during read")
        return raw
    except HostRuntimeConfigError:
        raise
    except (OSError, RuntimeError, UnicodeError, ValueError, KeyError) as error:
        raise _error("Host runtime configuration is unavailable or unsafe") from error


def _exact_int(value: Any, message: str, *, minimum: int, maximum: int) -> int:
    if type(value) is not int or not minimum <= value <= maximum:
        raise _error(message)
    return value


def _document(raw: bytes) -> tuple[Path, int, int, bool, str, str, str]:
    try:
        value = tomllib.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, tomllib.TOMLDecodeError, TypeError, ValueError) as error:
        raise _error("Host runtime configuration TOML is invalid") from error
    if (not isinstance(value, dict) or not {"schema_version", "shared_mcp"} <= set(value)
            or set(value) - {"schema_version", "shared_mcp", "project_defaults", "logging"}):
        raise _error("Host runtime configuration keys are invalid")
    if type(value["schema_version"]) is not int or value["schema_version"] != 1:
        raise _error("Host runtime configuration schema_version must be 1")
    shared = value["shared_mcp"]
    if (not isinstance(shared, dict) or "http_port" not in shared
            or len({"project_root", "projects_root"} & set(shared)) != 1):
        raise _error("Host runtime shared_mcp settings are incomplete")
    if set(shared) - {"project_root", "projects_root", "http_port", "max_loaded_projects"}:
        raise _error("Host runtime shared_mcp keys are invalid")
    single_project = "project_root" in shared
    root_value = shared["project_root" if single_project else "projects_root"]
    if not isinstance(root_value, str):
        raise _error("Host runtime root must be an absolute directory")
    root = _canonical_directory(root_value, reject_filesystem_root=True)
    port = _exact_int(
        shared["http_port"], "Host runtime http_port is invalid", minimum=1, maximum=65535
    )
    maximum = _exact_int(
        shared.get("max_loaded_projects", 2),
        "Host runtime max_loaded_projects is invalid",
        minimum=1,
        maximum=_MAX_LOADED_PROJECTS,
    )
    defaults = value.get("project_defaults", {})
    if not isinstance(defaults, dict) or set(defaults) - {"workbench_storage", "journal_storage"}:
        raise _error("Host runtime project_defaults keys are invalid")
    workbench = defaults.get("workbench_storage", "disk")
    journal = defaults.get("journal_storage", "files")
    if workbench not in ("disk", "memory") or journal not in ("files", "duckdb"):
        raise _error("Host runtime project_defaults storage is invalid")
    logging = value.get("logging", {})
    if not isinstance(logging, dict) or logging.keys() - {"level"}:
        raise _error("Host runtime logging keys are invalid")
    level = logging.get("level", "INFO")
    if level not in ("DEBUG", "INFO", "WARNING", "ERROR"):
        raise _error("Host runtime logging level is invalid")
    return root, port, maximum, single_project, workbench, journal, level


@dataclass(config=ConfigDict(strict=True, extra="forbid"), frozen=True)
class HostRuntimeConfig:
    """Immutable, provenance-carrying shared host settings."""

    source_path: Path
    projects_root: Path
    http_port: int
    raw_sha256: str
    max_loaded_projects: int = 2
    single_project: bool = False
    workbench_storage: str = "disk"
    journal_storage: str = "files"
    log_level: str = "INFO"

    @property
    def shared_runtime_id(self) -> str:
        value = f"{self.source_path}\0{self.projects_root}".encode("utf-8")
        return hashlib.sha256(value).hexdigest()

    def resolve_project(self, project_root: Path | str):
        return resolve_host_project(self, project_root)


def _default_path() -> Path:
    try:
        base = os.environ.get("XDG_CONFIG_HOME") or str(Path.home() / ".config")
        return Path(base) / "anechoic" / "runtime.toml"
    except (OSError, RuntimeError, TypeError, ValueError) as error:
        raise _error("Host runtime configuration default path is unavailable") from error


def load_host_runtime_config(path: Path | str | None = None) -> HostRuntimeConfig:
    """Load one canonical host config without writing or using a fallback."""
    source = _canonical_config_path(_default_path() if path is None else path)
    raw = _read_config(source)
    projects_root, http_port, maximum, single, workbench, journal, level = _document(raw)
    return HostRuntimeConfig(
        source, projects_root, http_port, hashlib.sha256(raw).hexdigest(), maximum,
        single, workbench, journal, level
    )


def resolve_host_project(config: HostRuntimeConfig, project_root: Path | str, *, selector=None):
    """Resolve one explicit Project admitted by the configured host root."""
    if not isinstance(config, HostRuntimeConfig):
        raise _error("Host runtime configuration is invalid")
    candidate = _canonical_directory(project_root)
    try:
        if (candidate != config.projects_root if config.single_project else
                candidate == config.projects_root or not candidate.is_relative_to(config.projects_root)):
            raise OutsideProjectRootError("Project root is outside the shared host root")
    except ValueError as error:
        raise OutsideProjectRootError("Project root is outside the shared host root") from error
    if selector is None:
        from .project_admission import select_runtime_project
        selector = select_runtime_project

    selection = selector(candidate)
    parameters = deepcopy(selection.parameters)
    runtime = parameters.setdefault("runtime", {})
    if isinstance(runtime, dict):
        console = "iwe_console" if "iwe_console" in runtime or "workbench" not in runtime else "workbench"
        for name, storage in ((console, config.workbench_storage),
                              ("journal", config.journal_storage)):
            section = runtime.setdefault(name, {})
            if isinstance(section, dict):
                section.setdefault("storage", storage)
    return replace(selection, parameters=parameters)



__all__ = [
    "HostRuntimeConfig",
    "HostRuntimeConfigError",
    "load_host_runtime_config",
    "resolve_host_project",
]


def main(argv=None) -> int:
    """Print validated settings for the shared host launcher."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host-settings", type=Path)
    args = parser.parse_args(argv)
    try:
        config = load_host_runtime_config(args.host_settings)
    except HostRuntimeConfigError:
        print("invalid_host_settings", file=sys.stderr)
        return 1
    print(json.dumps({
        "source_path": str(config.source_path),
        "projects_root": str(config.projects_root),
        "http_port": config.http_port,
        "max_loaded_projects": config.max_loaded_projects,
        "shared_runtime_id": config.shared_runtime_id,
        "single_project": config.single_project,
        "workbench_storage": config.workbench_storage,
        "journal_storage": config.journal_storage,
        "log_level": config.log_level,
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
