"""Read the machine-local settings for the shared MCP launcher."""

from hashlib import sha256
import os
from pathlib import Path
import stat
import tomllib
from typing import Literal, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from .runtime_log_level import LOG_LEVELS


_MAX_BYTES = 4 * 1024


class _Settings(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)


class _SharedMcp(_Settings):
    project_root: str | None = None
    projects_root: str | None = None
    http_port: int = Field(ge=1, le=65535)
    max_loaded_projects: int = Field(default=2, ge=1, le=64)

    @model_validator(mode="after")
    def check_root(self) -> Self:
        if (self.project_root is None) == (self.projects_root is None):
            raise ValueError("Exactly one shared host root is required")
        return self


class _ProjectDefaults(_Settings):
    workbench_storage: Literal["disk", "memory"] = "disk"
    journal_storage: Literal["files", "duckdb"] = "files"


class _Logging(_Settings):
    level: str = "INFO"

    @field_validator("level")
    @classmethod
    def check_level(cls, value: str) -> str:
        if value not in LOG_LEVELS:
            raise ValueError("Invalid shared host logging level")
        return value


class _Document(_Settings):
    schema_version: int = Field(ge=1, le=1)
    shared_mcp: _SharedMcp
    project_defaults: _ProjectDefaults = Field(
        default_factory=_ProjectDefaults
    )
    logging: _Logging = Field(default_factory=_Logging)


class HostRuntimeSettings(_Settings):
    source_path: Path
    projects_root: Path
    http_port: int
    max_loaded_projects: int
    single_project: bool
    workbench_storage: str
    journal_storage: str
    log_level: str

    @property
    def shared_runtime_id(self) -> str:
        return sha256(
            f"{self.source_path}\0{self.projects_root}".encode("utf-8")
        ).hexdigest()


def _canonical_path(value: Path | str, base: Path | None = None) -> Path:
    if (
        not isinstance(value, (Path, str))
        or not str(value)
        or "\0" in str(value)
    ):
        raise ValueError("Invalid shared host path")
    path = Path(value).expanduser()
    if ".." in path.parts or (base is None and not path.is_absolute()):
        raise ValueError("Unsafe shared host path")
    if base is not None:
        path = base / path
    if path.resolve(strict=True) != path:
        raise ValueError("Shared host path must be canonical")
    return path


def _version(info: os.stat_result) -> tuple[int, ...]:
    return (
        info.st_dev,
        info.st_ino,
        info.st_mode,
        info.st_size,
        info.st_mtime_ns,
        info.st_ctime_ns,
    )


def _read(source: Path) -> bytes:
    before = source.lstat()
    if (
        not stat.S_ISREG(before.st_mode)
        or before.st_mode & 0o022
        or before.st_size > _MAX_BYTES
    ):
        raise ValueError("Unsafe shared host settings file")
    with os.fdopen(
        os.open(source, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK), "rb"
    ) as stream:
        version = _version(before)
        if _version(os.fstat(stream.fileno())) != version:
            raise ValueError("Shared host settings changed before read")
        raw = stream.read(_MAX_BYTES + 1)
        if (
            len(raw) != before.st_size
            or source.resolve(strict=True) != source
            or _version(os.fstat(stream.fileno())) != version
            or _version(source.lstat()) != version
        ):
            raise ValueError("Shared host settings changed during read")
    return raw


def load_host_runtime_settings(
    path: Path | str | None, *, base: Path
) -> HostRuntimeSettings:
    if path is None:
        config_home = Path(
            os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config"
        )
        path = config_home / "anechoic/runtime.toml"
    source = _canonical_path(path, base)
    document = _Document.model_validate(
        tomllib.loads(_read(source).decode("utf-8"))
    )
    shared = document.shared_mcp
    single = shared.project_root is not None
    root = _canonical_path(
        shared.project_root if single else shared.projects_root
    )
    if root.parent == root or not root.is_dir():
        raise ValueError("Shared host root must be a canonical directory")
    return HostRuntimeSettings(
        source_path=source,
        projects_root=root,
        http_port=shared.http_port,
        max_loaded_projects=shared.max_loaded_projects,
        single_project=single,
        workbench_storage=document.project_defaults.workbench_storage,
        journal_storage=document.project_defaults.journal_storage,
        log_level=document.logging.level,
    )
