"""Validated Docker environment and inspect projection for Project MCP."""

from __future__ import annotations

import os
from pathlib import Path
import re
from typing import Any, Mapping

from MCP_PATCHBAY_C21.FEATURE_MCP.docker.project.backend.\
    project_mcp_docker_command import (
    BackendError,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.docker.shared_support.\
    shared_support__shared import (
    direct_log_level,
)

_DOCKER_CLIENT_ENV = (
    "HOME",
    "DOCKER_HOST",
    "DOCKER_CONTEXT",
    "DOCKER_CONFIG",
    "XDG_RUNTIME_DIR",
    "TMPDIR",
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "ALL_PROXY",
    "NO_PROXY",
    "http_proxy",
    "https_proxy",
    "all_proxy",
    "no_proxy",
)
_PROJECTED_INSPECT_KEYS = frozenset(
    {
        "Id",
        "Image",
        "Config",
        "State",
        "NetworkSettings",
        "Mounts",
    }
)


class BackendValidation:
    @staticmethod
    def _safe_instance(selection: object) -> str:
        value = getattr(selection, "instance_id", None)
        if not isinstance(value, str) or not re.fullmatch(
            r"[0-9a-f]{64}", value
        ):
            raise BackendError()
        return value

    @staticmethod
    def _root(selection: object) -> Path:
        try:
            root = Path(getattr(selection, "root"))
        except (TypeError, ValueError) as error:
            raise BackendError() from error
        if not root.is_absolute() or root.is_symlink() or not root.is_dir():
            raise BackendError()
        return root

    @staticmethod
    def _control(selection: object) -> str:
        value = getattr(selection, "control_relative", None)
        if (
            not isinstance(value, Path)
            or value.is_absolute()
            or len(value.parts) != 1
        ):
            raise BackendError()
        return value.as_posix()

    @staticmethod
    def _compose_project(selection: object) -> str:
        value = getattr(selection, "compose_project", None)
        if not isinstance(value, str) or not re.fullmatch(
            r"anechoic-mcp-[0-9a-f]{24}", value
        ):
            raise BackendError()
        return value

    @classmethod
    def _environment(
        cls, selection: object, image_id: str, fingerprint: str, port: int
    ) -> dict[str, str]:
        root = cls._root(selection)
        if not isinstance(image_id, str) or not re.fullmatch(
            r"sha256:[0-9a-f]{64}", image_id
        ):
            raise BackendError()
        if not isinstance(fingerprint, str) or not re.fullmatch(
            r"[0-9a-f]{64}", fingerprint
        ):
            raise BackendError()
        if (
            isinstance(port, bool)
            or not isinstance(port, int)
            or not 1 <= port <= 65535
        ):
            raise BackendError()
        environment = {
            "PATH": os.environ.get("PATH", ""),
            "ANECHOIC_IMAGE": image_id,
            "ANECHOIC_PROJECT_ROOT": str(root),
            "ANECHOIC_CONTROL_ROOT": cls._control(selection),
            "ANECHOIC_PROJECT_INSTANCE_ID": cls._safe_instance(selection),
            "ANECHOIC_RUNTIME_FINGERPRINT": fingerprint,
            "ANECHOIC_MCP_HTTP_PORT": str(port),
            "ANECHOIC_LOG_LEVEL": direct_log_level(),
        }
        for name in _DOCKER_CLIENT_ENV:
            if name in os.environ:
                environment[name] = os.environ[name]
        return environment

    @staticmethod
    def _docker_client_environment(context=None) -> dict[str, str]:
        """Pass Docker client context without ambient service credentials."""
        environment = {"PATH": os.environ.get("PATH", "")}
        for name in _DOCKER_CLIENT_ENV:
            if name in os.environ:
                environment[name] = os.environ[name]
        if context is not None:
            environment.pop("DOCKER_HOST", None)
            environment["DOCKER_CONTEXT"] = context
        return environment

    @classmethod
    def _projection_matches_selection(
        cls, row: Mapping[str, Any], selection: object
    ) -> bool:
        """Require the inspect projection to bind exactly one Project mount."""
        if set(row) != _PROJECTED_INSPECT_KEYS:
            return False
        config = row.get("Config")
        labels = config.get("Labels") if isinstance(config, Mapping) else None
        root = cls._root(selection)
        if not isinstance(labels, Mapping) or (
            labels.get("org.anechoic.project") != cls._safe_instance(selection)
            or labels.get("org.anechoic.service") != "mcp-http"
            or labels.get("org.anechoic.control_root")
            != cls._control(selection)
            or labels.get("org.anechoic.host_project_root") != str(root)
        ):
            return False
        mounts = row.get("Mounts")
        if (
            not isinstance(mounts, list)
            or len(mounts) != 2
            or not all(isinstance(m, Mapping) for m in mounts)
        ):
            return False
        volume = [
            m
            for m in mounts
            if m.get("Type") == "volume"
            and m.get("Name") == "anechoic-framework-db"
            and m.get("Destination") == "/var/lib/anechoic"
            and m.get("RW") is True
        ]
        if len(volume) != 1:
            return False
        mount = next(m for m in mounts if m is not volume[0])
        source = mount.get("Source")
        return (
            mount.get("Type") == "bind"
            and mount.get("Destination") == "/project"
            and isinstance(source, str)
            and Path(source) == root
        )
