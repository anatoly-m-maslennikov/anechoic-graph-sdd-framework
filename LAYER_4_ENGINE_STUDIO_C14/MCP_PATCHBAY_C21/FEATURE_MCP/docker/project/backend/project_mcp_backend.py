"""Docker and loopback-MCP backend for the bounded Project MCP launcher."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
import re
import time
from typing import Mapping
from urllib.parse import urlsplit

from MCP_PATCHBAY_C21.FEATURE_MCP.docker.project.backend.\
    _project_mcp_backend_image import (
    BackendImage,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.docker.shared_support.\
    shared_support__shared import HEALTH_PATH, MCP_PATH
from ._project_mcp_backend_validation import (
    BackendValidation,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.docker.project.backend.\
    project_mcp_docker_command import (
    BackendError,
    _bounded_run,
)


_DIRECTORY = Path(__file__).resolve().parents[2]
_COMPOSE = _DIRECTORY / "project-mcp.compose.yaml"
_CONTAINER_ID = re.compile(r"[0-9a-f]{12,64}\Z")
_INSPECT_FORMAT = (
    '{"Id":{{json .Id}},"Image":{{json .Image}},'
    '"Config":{"Labels":{{json .Config.Labels}}},'
    '"State":{{json .State}},'
    '"NetworkSettings":{"Ports":{{json .NetworkSettings.Ports}}},'
    '"Mounts":{{json .Mounts}}}'
)


def _unique_object(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("duplicate Docker inspect member")
        value[key] = item
    return value


class ProjectMcpBackend(BackendValidation, BackendImage):
    """Build, inspect and start one HTTP MCP service, never a worker."""

    def __init__(
        self,
        *,
        build_if_missing: bool = True,
        build_timeout: float = 600.0,
        settings=None,
    ) -> None:
        self.build_if_missing = build_if_missing
        self.build_timeout = build_timeout
        self.settings = settings

    def inspect(self, selection, *, timeout: float = 30.0):
        """Read the selected Project's Docker namespace within one deadline."""
        self._check_native_selection(selection)
        if (
            isinstance(timeout, bool)
            or not isinstance(timeout, (int, float))
            or not 0 < timeout <= 30.0
        ):
            raise BackendError("DOCKER_PUBLICATION_FAILED")
        deadline = time.monotonic() + float(timeout)

        def remaining() -> float:
            value = deadline - time.monotonic()
            if value <= 0:
                raise BackendError("DOCKER_PUBLICATION_FAILED")
            return value

        instance = self._safe_instance(selection)
        listing = _bounded_run(
            [
                "docker",
                "ps",
                "--all",
                "--filter",
                f"label=org.anechoic.project={instance}",
                "--filter",
                "label=org.anechoic.service=mcp-http",
                "--format",
                "{{.ID}}",
            ],
            timeout=remaining(),
            env=self._docker_client_environment(
                self.settings.docker_context
                if self.settings is not None
                else None
            ),
        )
        identifiers = list(filter(None, map(str.strip, listing.splitlines())))
        if len(identifiers) > 1 or any(
            _CONTAINER_ID.fullmatch(value) is None for value in identifiers
        ):
            raise BackendError("DOCKER_PUBLICATION_FAILED")
        return [
            self._inspect_row(value, selection, remaining)
            for value in identifiers
        ]

    def _inspect_row(self, identifier, selection, remaining):
        raw = _bounded_run(
            [
                "docker",
                "container",
                "inspect",
                "--format",
                _INSPECT_FORMAT,
                identifier,
            ],
            timeout=remaining(),
            env=self._docker_client_environment(
                self.settings.docker_context
                if self.settings is not None
                else None
            ),
        )
        try:
            value = json.loads(raw, object_pairs_hook=_unique_object)
            if not isinstance(
                value, dict
            ) or not self._projection_matches_selection(value, selection):
                raise ValueError()
            return value
        except (TypeError, ValueError, json.JSONDecodeError) as error:
            raise BackendError("RUNTIME_MISMATCH") from error

    def collect_legacy_processes(
        self, admission: object, deadline: float
    ) -> Mapping[str, object]:
        """Query the actual Docker namespace without acting on any container.

        The generic migration collector validates a complete sealed process
        identity before it can classify a non-empty roster as ``observed``.
        Docker's existing inspect projection does not carry that identity, so
        a live row is deliberately returned as raw provider evidence and the
        caller will block rather than guess that it belongs to the predecessor.
        """
        selection = getattr(admission, "selection", None)
        root = getattr(admission, "project_root", None)
        instance = getattr(admission, "project_instance_id", None)
        if (
            selection is None
            or getattr(selection, "root", None) != root
            or getattr(selection, "instance_id", None) != instance
        ):
            return {"outcome": "unavailable", "records": []}
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return {"outcome": "unavailable", "records": []}
        rows = self.inspect(selection, timeout=min(30.0, remaining))
        records: list[dict[str, object]] = []
        for row in rows:
            if not isinstance(row, Mapping):
                return {"outcome": "unavailable", "records": []}
            config = row.get("Config")
            labels = (
                config.get("Labels") if isinstance(config, Mapping) else None
            )
            records.append(
                {
                    "container_id": row.get("Id"),
                    "labels": dict(labels)
                    if isinstance(labels, Mapping)
                    else None,
                }
            )
        return {"outcome": "complete", "records": records}

    @staticmethod
    def _compose_file(value: Path | str) -> Path:
        """Admit a regular, absolute Compose carrier before invoking Docker."""
        try:
            compose = Path(value)
            if (
                not compose.is_absolute()
                or compose.is_symlink()
                or not compose.is_file()
            ):
                raise BackendError()
            return compose
        except BackendError:
            raise
        except (OSError, TypeError, ValueError) as error:
            raise BackendError() from error

    def _start(
        self,
        selection,
        image_id,
        fingerprint,
        compose_file: Path | str,
        timeout,
        port,
    ):
        if (
            not isinstance(timeout, (int, float))
            or isinstance(timeout, bool)
            or timeout <= 0
        ):
            raise BackendError()
        compose = self._compose_file(compose_file)
        command = [
            "docker",
            "compose",
            "--env-file",
            "/dev/null",
            "--project-name",
            self._compose_project(selection),
            "-f",
            str(compose),
            "up",
            "-d",
            "--wait",
            "--wait-timeout",
            str(max(1, int(timeout))),
            "--no-recreate",
            "--no-deps",
            "mcp-http",
        ]
        environment = self._environment(selection, image_id, fingerprint, port)
        self._apply_settings(environment)
        _bounded_run(command, timeout=float(timeout), env=environment)

    def _apply_settings(self, environment):
        if self.settings is not None:
            if self.settings.docker_context is not None:
                environment.pop("DOCKER_HOST", None)
                environment["DOCKER_CONTEXT"] = self.settings.docker_context
            environment["ANECHOIC_LOG_LEVEL"] = self.settings.log_level
            environment["ANECHOIC_WORKBENCH_STORAGE"] = (
                self.settings.workbench_storage
            )
            environment["ANECHOIC_JOURNAL_STORAGE"] = (
                self.settings.journal_storage
            )

    def start(self, selection, image_id, fingerprint, timeout, port):
        """Start development mode from its checked-in Compose carrier."""
        self._check_native_selection(selection)
        try:
            manager, identity, resolved_id, packaged = self._image_evidence
        except AttributeError, TypeError:
            raise BackendError("IMAGE_INPUT_UNAVAILABLE") from None
        if (image_id, fingerprint) != (resolved_id, identity.fingerprint):
            raise BackendError("IMAGE_INPUT_UNAVAILABLE")
        manager._current(identity, use_packaged_assets=packaged)
        self._start(selection, image_id, fingerprint, _COMPOSE, timeout, port)

    @staticmethod
    async def _initialize(url: str, timeout: float) -> None:
        import httpx2
        from mcp.client.session import ClientSession
        from mcp.client.streamable_http import streamable_http_client

        async with httpx2.AsyncClient(
            trust_env=False, follow_redirects=False, timeout=timeout
        ) as client:
            response = await client.get(
                url.removesuffix(MCP_PATH) + HEALTH_PATH
            )
            if (
                response.status_code != 200
                or response.json().get("state") != "ready"
            ):
                raise ValueError("Project is not ready")
            async with (
                streamable_http_client(url, http_client=client) as streams,
                ClientSession(*streams) as session,
            ):
                await session.initialize()

    def health(self, full_mcp_url, timeout):
        try:
            address = urlsplit(full_mcp_url)
            valid = (
                address.scheme == "http"
                and address.hostname == "127.0.0.1"
                and address.port is not None
                and 1 <= address.port <= 65535
                and address.path == MCP_PATH
                and not address.query
                and not address.fragment
                and address.username is None
                and address.password is None
                and address.netloc == f"127.0.0.1:{address.port}"
            )
        except TypeError, ValueError:
            valid = False
        if (
            not valid
            or isinstance(timeout, bool)
            or not isinstance(timeout, (int, float))
            or timeout <= 0
        ):
            return False
        try:
            asyncio.run(
                asyncio.wait_for(
                    self._initialize(full_mcp_url, float(timeout)),
                    timeout=float(timeout),
                )
            )
        except Exception:
            return False
        return True


def collect_legacy_processes(
    admission: object, deadline: float
) -> Mapping[str, object]:
    """Provider hook used only by retained-migration read-only collection."""
    return ProjectMcpBackend(build_if_missing=False).collect_legacy_processes(
        admission, deadline
    )


__all__ = ["BackendError", "ProjectMcpBackend", "collect_legacy_processes"]
