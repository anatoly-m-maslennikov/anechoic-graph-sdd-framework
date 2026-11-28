"""Start or reuse one selected Project-local HTTP MCP service safely."""

from __future__ import annotations

from contextlib import nullcontext as nullcontext
from pathlib import Path
import time
from typing import Any, Mapping

from ._project_mcp_launcher_options import _launch_options
from ._project_mcp_launcher_runtime import LauncherRuntime

from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import (
    select_runtime_project as resolve_project,
)

from MCP_PATCHBAY_C21.FEATURE_MCP.docker.image_runtime.\
    image_runtime__shared import (
    ImageError,
)


from MCP_PATCHBAY_C21.FEATURE_MCP.docker.project.\
    project_mcp_launcher_common import (
    LaunchError,
    _CONDITIONS,
    _DISPOSITIONS,
    _FINGERPRINT,
    _IMAGE,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.docker.project.\
    project_mcp_launcher_state import (
    _project_lock as _project_lock,
    _record_safe_metadata as _record_safe_metadata,
    open_legacy_process_fence as open_legacy_process_fence,
)
from .project_mcp_launcher_admission import (
    _admit_runtime as _admit_runtime,
    _attribution,
)

_DEFAULT_STARTUP_TIMEOUT = 420.0
_DEFAULT_BUILD_TIMEOUT = 600.0


def _positive_timeout(
    value: object, *, ceiling: float, default: float
) -> float:
    if value is None:
        return default
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not 0 < value <= ceiling
    ):
        raise LaunchError("READINESS_FAILED")
    return float(value)


def _requested_port(value: object) -> int | None:
    """Admit an optional caller assertion of the selected host port."""
    if value is None:
        return None
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or not 1 <= value <= 65535
    ):
        raise LaunchError("DOCKER_START_FAILED")
    return value


def _configured_port(
    selection: object, requested_port: int | None, settings=None
) -> int:
    "Read the sole Project-owned HTTP port and check an optional assertion."
    parameters = selection.parameters
    project_mcp = (
        parameters.get("project_mcp")
        if isinstance(parameters, Mapping)
        else None
    )
    port = (
        project_mcp.get("http_port")
        if isinstance(project_mcp, Mapping)
        else None
    )
    if settings is not None:
        port = settings.http_port
    if type(port) is not int or not 1 <= port <= 65535:
        raise LaunchError("PROJECT_SELECTION_REFUSED")
    if requested_port is not None and requested_port != port:
        raise LaunchError("PROJECT_SELECTION_REFUSED")
    return port


class Launcher(LauncherRuntime):
    "Bounded Project MCP start-or-reuse coordinator."

    def __init__(self, backend=None) -> None:
        self.backend = backend

    @staticmethod
    def _failure(
        code: str,
        selection: object | None = None,
        image_id: str | None = None,
        fingerprint: str | None = None,
    ) -> dict[str, Any]:
        condition = code if code in _CONDITIONS else "DOCKER_START_FAILED"
        return {
            "disposition": _DISPOSITIONS[condition],
            "condition": condition,
            **_attribution(selection, image_id, fingerprint),
        }

    @staticmethod
    def _backend(
        backend, *, build_if_missing: bool, build_timeout: float, settings=None
    ):
        if backend is not None:
            return backend
        from MCP_PATCHBAY_C21.FEATURE_MCP.docker.project.backend.\
            backend__shared import (
            ProjectMcpBackend,
        )

        return ProjectMcpBackend(
            build_if_missing=build_if_missing,
            build_timeout=build_timeout,
            settings=settings,
        )

    @staticmethod
    def _image(backend, source_root, image, selection):
        from MCP_PATCHBAY_C21.FEATURE_MCP.docker.project.backend.\
            backend__shared import (
            ProjectMcpBackend,
        )

        options = (
            {"selection": selection}
            if isinstance(backend, ProjectMcpBackend)
            else {}
        )
        try:
            image_id, fingerprint = backend.resolve_image(
                source_root, image, project_root=selection.root, **options
            )
        except ImageError as error:
            raise LaunchError(
                getattr(error, "code", "IMAGE_REFUSED")
            ) from None
        except LaunchError:
            raise
        except Exception:
            raise LaunchError("IMAGE_REFUSED") from None
        if not isinstance(image_id, str) or _IMAGE.fullmatch(image_id) is None:
            raise LaunchError("IMAGE_REFUSED")
        if (
            not isinstance(fingerprint, str)
            or _FINGERPRINT.fullmatch(fingerprint) is None
        ):
            raise LaunchError("IMAGE_REFUSED")
        return image_id, fingerprint

    @staticmethod
    def _ready(backend, candidate: Mapping[str, Any], deadline: float) -> bool:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return False
        try:
            return backend.health(candidate["url"], remaining) is True
        except Exception:
            return False

    @staticmethod
    def _result(
        disposition: str,
        condition: str,
        selection: object,
        image_id: str,
        fingerprint: str,
        candidate: Mapping[str, Any],
    ) -> dict[str, Any]:
        result = {
            "disposition": disposition,
            "condition": condition,
            "readiness": True,
            "url": candidate["url"],
        }
        result.update(_attribution(selection, image_id, fingerprint))
        result.update(
            {
                "container_id": candidate["container_id"],
                "port": candidate["port"],
                "readiness": True,
            }
        )
        return result

    @staticmethod
    def _failure_code(error: Exception, fallback: str) -> str:
        code = getattr(error, "code", None)
        return (
            code if isinstance(code, str) and code in _CONDITIONS else fallback
        )

    @staticmethod
    def _select_project(project_root, control_root):
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.settings.\
            container_settings__pub import (
            read_container_settings,
        )

        settings = read_container_settings(project_root)
        if settings is not None:
            if settings.mode != "project":
                raise ValueError("Project MCP requires project mode")
            if (
                control_root is not None
                and settings.control_root is not None
                and str(control_root) != settings.control_root
            ):
                raise ValueError("control root does not match settings")
            control_root = control_root or settings.control_root
        return resolve_project(project_root, control_root), settings

    def _launch_selection(
        self,
        selection,
        settings,
        timeout,
        build_timeout,
        build_if_missing,
        requested_port,
        source_root,
        image,
    ):
        try:
            startup_timeout, bounded_build_timeout, build_if_missing = (
                _launch_options(
                    selection,
                    timeout,
                    build_timeout,
                    build_if_missing,
                    settings,
                )
            )
            port = _configured_port(selection, requested_port, settings)
            if source_root is None:
                return self._failure("IMAGE_INPUT_UNAVAILABLE", selection)
            source = Path(source_root)
            if image is None and settings is not None:
                image = settings.image
            backend = self._backend(
                self.backend,
                build_if_missing=build_if_missing,
                build_timeout=bounded_build_timeout,
                settings=settings,
            )
            return self._launch_locked(
                selection,
                backend,
                source,
                image,
                startup_timeout,
                port,
                settings,
            )
        except LaunchError as error:
            return self._failure(error.code, selection)

    def launch(
        self,
        project_root,
        token=None,
        control_root=None,
        image=None,
        source_root=None,
        timeout=420,
        *,
        port=None,
        build_if_missing=True,
        build_timeout=600,
    ):
        "Return one safe result; never stop, replace, or retry a live runtime."
        try:
            requested_port = _requested_port(port)
        except LaunchError as error:
            return self._failure(error.code)
        try:
            selection, settings = self._select_project(
                project_root, control_root
            )
        except Exception:
            return self._failure("PROJECT_SELECTION_REFUSED")
        return self._launch_selection(
            selection,
            settings,
            timeout,
            build_timeout,
            build_if_missing,
            requested_port,
            source_root,
            image,
        )


__all__ = ["ImageError", "LaunchError", "Launcher"]
