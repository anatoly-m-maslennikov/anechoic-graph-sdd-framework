"""Start or reuse one selected Project-local HTTP MCP service safely."""

from __future__ import annotations

from contextlib import nullcontext
from pathlib import Path
import time
from typing import Any, Mapping

from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import (
    select_runtime_project as resolve_project,
)

from MCP_PATCHBAY_C21.FEATURE_MCP.docker.runtime_images_common import (
    ImageError,
)


from MCP_PATCHBAY_C21.FEATURE_MCP.docker.project_mcp_launcher_common import (
    LaunchError, _CONDITIONS, _DISPOSITIONS, _FINGERPRINT, _IMAGE,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.docker.project_mcp_launcher_state import (
    _project_lock, _record_safe_metadata,
    open_legacy_process_fence as open_legacy_process_fence,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.docker.project_mcp_launcher_admission import _admit_runtime, _attribution

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


def _configured_port(selection: object, requested_port: int | None, settings=None) -> int:
    """Read the sole Project-owned HTTP port and check an optional assertion."""
    parameters = selection.parameters
    project_mcp = (
        parameters.get("project_mcp") if isinstance(parameters, Mapping) else None
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


def _launch_options(selection, timeout, build_timeout, build_if_missing, settings=None):
    startup_timeout = _positive_timeout(
        timeout,
        ceiling=_DEFAULT_STARTUP_TIMEOUT,
        default=_DEFAULT_STARTUP_TIMEOUT,
    )
    bounded_build_timeout = _positive_timeout(
        build_timeout,
        ceiling=_DEFAULT_BUILD_TIMEOUT,
        default=_DEFAULT_BUILD_TIMEOUT,
    )
    if type(build_if_missing) is not bool:
        raise LaunchError("IMAGE_REFUSED")
    if settings is not None:
        return (min(startup_timeout, settings.startup_timeout_seconds),
                min(bounded_build_timeout, settings.build_timeout_seconds),
                build_if_missing and settings.build_if_missing)
    runtime = selection.parameters.get("runtime", {})
    mcp_options = (
        runtime.get("project_mcp", {})
        if isinstance(runtime, Mapping)
        else None
    )
    if (
        not isinstance(mcp_options, Mapping)
        or type(mcp_options.get("build_if_missing", True)) is not bool
    ):
        raise LaunchError("PROJECT_SELECTION_REFUSED")
    startup_timeout = min(startup_timeout, _positive_timeout(
        mcp_options.get("startup_timeout_seconds", _DEFAULT_STARTUP_TIMEOUT),
        ceiling=_DEFAULT_STARTUP_TIMEOUT, default=_DEFAULT_STARTUP_TIMEOUT,
    ))
    bounded_build_timeout = min(bounded_build_timeout, _positive_timeout(
        mcp_options.get("build_timeout_seconds", _DEFAULT_BUILD_TIMEOUT),
        ceiling=_DEFAULT_BUILD_TIMEOUT, default=_DEFAULT_BUILD_TIMEOUT,
    ))
    build_if_missing = build_if_missing and mcp_options.get(
        "build_if_missing", True
    )
    return startup_timeout, bounded_build_timeout, build_if_missing


class Launcher:
    """Bounded Project MCP start-or-reuse coordinator with an injectable backend."""

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
    def _backend(backend, *, build_if_missing: bool, build_timeout: float, settings=None):
        if backend is not None:
            return backend
        from MCP_PATCHBAY_C21.FEATURE_MCP.docker.project_mcp_backend import (
            ProjectMcpBackend,
        )

        return ProjectMcpBackend(
            build_if_missing=build_if_missing, build_timeout=build_timeout,
            settings=settings
        )

    @staticmethod
    def _image(backend, source_root, image, selection):
        from MCP_PATCHBAY_C21.FEATURE_MCP.docker.project_mcp_backend import (
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

    def _start_runtime(self, selection, backend, image_id, fingerprint,
                       requested_port, deadline, complete, readiness_timeout=None):
        try:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return complete(
                    self._failure(
                        "DOCKER_START_FAILED", selection, image_id, fingerprint
                    )
                )
            backend.start(
                selection, image_id, fingerprint, remaining, requested_port
            )
        except LaunchError as error:
            return complete(
                self._failure(error.code, selection, image_id, fingerprint)
            )
        except Exception as error:
            return complete(
                self._failure(
                    self._failure_code(error, "DOCKER_START_FAILED"),
                    selection,
                    image_id,
                    fingerprint,
                )
            )
        try:
            candidate = _admit_runtime(backend.inspect(selection), selection, image_id,
                                       fingerprint, requested_port)
        except Exception as error:
            return complete(self._failure(self._failure_code(
                error, "DOCKER_PUBLICATION_FAILED"), selection, image_id, fingerprint))
        if isinstance(candidate, str):
            return complete(self._failure(candidate if candidate != "absent"
                                          else "DOCKER_START_FAILED", selection,
                                          image_id, fingerprint))
        if readiness_timeout is not None:
            deadline = min(deadline, time.monotonic() + readiness_timeout)
        if not self._ready(backend, candidate, deadline):
            return complete(self._failure("READINESS_FAILED", selection,
                                          image_id, fingerprint))
        return complete(self._result("started", "READY_STARTED", selection, image_id,
                                     fingerprint, candidate))

    def _launch_runtime(self, selection: object, backend: object, image_id: str, fingerprint: str,
                        startup_timeout: float, requested_port: int,
                        *, lock_held: bool = False, readiness_timeout=None) -> dict[str, Any]:
        """Inspect, start once, and health-check one already identified runtime."""

        lock = (
            nullcontext()
            if lock_held
            else _project_lock(selection, startup_timeout)
        )
        with lock:
            def complete(result: dict[str, Any]) -> dict[str, Any]:
                _record_safe_metadata(selection, result)
                return result

            try:
                candidate = _admit_runtime(backend.inspect(selection), selection, image_id,
                                           fingerprint, requested_port)
            except Exception as error:
                return complete(self._failure(self._failure_code(
                    error, "DOCKER_PUBLICATION_FAILED"), selection, image_id, fingerprint))
            deadline = time.monotonic() + startup_timeout
            if candidate == "absent":
                return self._start_runtime(selection, backend, image_id, fingerprint,
                                           requested_port, deadline, complete, readiness_timeout)
            if isinstance(candidate, str):
                return complete(
                    self._failure(candidate, selection, image_id, fingerprint)
                )
            if readiness_timeout is not None:
                deadline = min(deadline, time.monotonic() + readiness_timeout)
            if not self._ready(backend, candidate, deadline):
                return complete(self._failure("READINESS_FAILED", selection, image_id, fingerprint))
            return complete(self._result("reused", "READY_REUSED", selection, image_id,
                                         fingerprint, candidate))

    def launch(self, project_root, token=None, control_root=None, image=None, source_root=None,
               timeout=420, *, port=None, build_if_missing=True, build_timeout=600):
        """Return one safe result; never stop, replace, or retry a live runtime."""
        try:
            requested_port = _requested_port(port)
        except LaunchError as error:
            return self._failure(error.code)
        try:
            from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.container_settings__pub import (
                read_container_settings,
            )
            settings = read_container_settings(project_root)
            if settings is not None:
                if settings.mode != "project":
                    raise ValueError("Project MCP requires project mode")
                if control_root is not None and settings.control_root is not None and str(control_root) != settings.control_root:
                    raise ValueError("control root does not match settings")
                control_root = control_root or settings.control_root
            selection = resolve_project(project_root, control_root)
        except Exception:
            return self._failure("PROJECT_SELECTION_REFUSED")
        try:
            startup_timeout, bounded_build_timeout, build_if_missing = _launch_options(
                selection, timeout, build_timeout, build_if_missing, settings,
            )
            configured_port = _configured_port(selection, requested_port, settings)
            if source_root is None:
                return self._failure("IMAGE_INPUT_UNAVAILABLE", selection)
            source = Path(source_root)
            if image is None and settings is not None:
                image = settings.image
            backend = self._backend(self.backend, build_if_missing=build_if_missing,
                                    build_timeout=bounded_build_timeout, settings=settings)
            with _project_lock(selection, startup_timeout):
                try:
                    image_id, fingerprint = self._image(
                        backend, source, image, selection
                    )
                except LaunchError as error:
                    result = self._failure(error.code, selection)
                    _record_safe_metadata(selection, result)
                    return result
                return self._launch_runtime(selection, backend, image_id, fingerprint, startup_timeout,
                                            configured_port, lock_held=True,
                                            readiness_timeout=(settings.readiness_timeout_seconds
                                                               if settings is not None else None))
        except LaunchError as error:
            return self._failure(error.code, selection)

__all__ = ["ImageError", "LaunchError", "Launcher"]
