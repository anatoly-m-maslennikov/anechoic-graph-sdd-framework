"""Read and validate mounted-folder container startup settings."""

from dataclasses import fields
import os
from pathlib import Path
import re
import stat
from typing import Any

from pydantic import ConfigDict
from pydantic.dataclasses import dataclass

from ..ADAPTERS_C30__pub import CEILINGS, ReadContext, open_regular
from ..settings.settings_carrier__pub import read_settings_carrier

CONTAINER_SETTINGS_FILENAME = ".anechoic_runtime_config.toml"


@dataclass(
    frozen=True,
    config=ConfigDict(strict=True, extra="forbid", hide_input_in_errors=True),
)
class ContainerStartupSettings:
    http_port: int
    mode: str = "project"
    image: str | None = None
    docker_context: str | None = None
    control_root: str | None = None
    build_if_missing: bool = True
    build_timeout_seconds: int = 600
    startup_timeout_seconds: int = 420
    readiness_timeout_seconds: int = 420
    max_loaded_projects: int = 2
    workbench_storage: str = "disk"
    journal_storage: str = "files"
    log_level: str = "INFO"


def parse_container_settings(
    document: dict[str, Any],
) -> ContainerStartupSettings:
    settings = ContainerStartupSettings(**_container_fields(document))
    for name, maximum in (
        ("http_port", 65535),
        ("build_timeout_seconds", 600),
        ("startup_timeout_seconds", 420),
        ("readiness_timeout_seconds", 900),
        ("max_loaded_projects", 64),
    ):
        value = getattr(settings, name)
        if type(value) is not int or not 1 <= value <= maximum:
            raise ValueError(f"invalid container.{name}")
    for name, options in (
        ("mode", ("project", "projects")),
        ("workbench_storage", ("disk", "memory")),
        ("journal_storage", ("files", "duckdb")),
        ("log_level", ("INFO", "DEBUG", "WARNING", "ERROR")),
    ):
        if getattr(settings, name) not in options:
            raise ValueError(f"invalid container.{name}")
    if settings.image is not None and not re.fullmatch(
        r"sha256:[0-9a-f]{64}", settings.image
    ):
        raise ValueError("invalid container.image")
    if settings.docker_context is not None and not re.fullmatch(
        r"[A-Za-z0-9][A-Za-z0-9_.-]*", settings.docker_context
    ):
        raise ValueError("invalid container.docker_context")
    if settings.control_root is not None and (
        settings.control_root in ("", ".", "..")
        or "/" in settings.control_root
        or "\\" in settings.control_root
    ):
        raise ValueError("invalid container.control_root")
    return settings


def _container_fields(document):
    if not isinstance(document, dict) or set(document) - {
        "schema_version",
        "container",
    }:
        raise ValueError("invalid container settings document")
    version = document.get("schema_version", 1)
    if type(version) is not int or version != 1:
        raise ValueError("invalid container settings schema_version")
    values = document.get("container")
    names = {field.name for field in fields(ContainerStartupSettings)}
    if not isinstance(values, dict) or set(values) - names:
        raise ValueError("invalid container settings fields")
    if "http_port" not in values:
        raise ValueError("container.http_port is required")
    return values


def read_container_settings(
    mounted_folder: str | Path,
) -> ContainerStartupSettings | None:
    root = Path(os.path.abspath(mounted_folder))
    root_fd = open_regular(root, directory=True)
    try:
        path = root / CONTAINER_SETTINGS_FILENAME
        try:
            fd = os.open(
                path.name,
                os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK,
                dir_fd=root_fd,
            )
        except FileNotFoundError:
            return None
        try:
            info = os.fstat(fd)
            if not stat.S_ISREG(info.st_mode) or info.st_mode & 0o022:
                raise ValueError(
                    "container settings must be writable only by its owner"
                )
        finally:
            os.close(fd)
        reader = ReadContext(
            roots=[str(root)], limits={**CEILINGS, "max_file_bytes": 4096}
        )
        document = read_settings_carrier(path, read_bytes=reader.read)
        if (
            reader.versions[str(path)] != reader.version(info)
            or reader.currentness()["state"] != "unchanged"
        ):
            raise ValueError("container settings changed during read")
        return parse_container_settings(document)
    finally:
        os.close(root_fd)
