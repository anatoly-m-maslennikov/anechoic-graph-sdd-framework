"""Runtime coordination for the Project MCP launcher."""

from __future__ import annotations

from typing import Any
from importlib import import_module


def _launcher():
    return import_module(
        "MCP_PATCHBAY_C21.FEATURE_MCP.docker.project.project_mcp_launcher"
    )


class LauncherRuntime:
    def _complete_ready(
        self,
        backend,
        candidate,
        deadline,
        readiness_timeout,
        complete,
        selection,
        image_id,
        fingerprint,
        disposition,
        condition,
    ):
        if readiness_timeout is not None:
            deadline = min(
                deadline, _launcher().time.monotonic() + readiness_timeout
            )
        if not self._ready(backend, candidate, deadline):
            return complete(
                self._failure(
                    "READINESS_FAILED", selection, image_id, fingerprint
                )
            )
        return complete(
            self._result(
                disposition,
                condition,
                selection,
                image_id,
                fingerprint,
                candidate,
            )
        )

    def _start_backend(
        self,
        selection,
        backend,
        image_id,
        fingerprint,
        requested_port,
        deadline,
        complete,
    ):
        try:
            remaining = deadline - _launcher().time.monotonic()
            if remaining <= 0:
                return False, complete(
                    self._failure(
                        "DOCKER_START_FAILED", selection, image_id, fingerprint
                    )
                )
            backend.start(
                selection, image_id, fingerprint, remaining, requested_port
            )
        except _launcher().LaunchError as error:
            return False, complete(
                self._failure(error.code, selection, image_id, fingerprint)
            )
        except Exception as error:
            return False, complete(
                self._failure(
                    self._failure_code(error, "DOCKER_START_FAILED"),
                    selection,
                    image_id,
                    fingerprint,
                )
            )
        return True, None

    def _inspect_runtime(
        self,
        backend,
        selection,
        image_id,
        fingerprint,
        requested_port,
        complete,
    ):
        try:
            candidate = _launcher()._admit_runtime(
                backend.inspect(selection),
                selection,
                image_id,
                fingerprint,
                requested_port,
            )
        except Exception as error:
            return False, complete(
                self._failure(
                    self._failure_code(error, "DOCKER_PUBLICATION_FAILED"),
                    selection,
                    image_id,
                    fingerprint,
                )
            )
        return True, candidate

    def _started_candidate(
        self, candidate, selection, image_id, fingerprint, complete
    ):
        if isinstance(candidate, str):
            return complete(
                self._failure(
                    candidate
                    if candidate != "absent"
                    else "DOCKER_START_FAILED",
                    selection,
                    image_id,
                    fingerprint,
                )
            )
        return None

    def _start_runtime(
        self,
        selection,
        backend,
        image_id,
        fingerprint,
        requested_port,
        deadline,
        complete,
        readiness_timeout=None,
    ):
        started, result = self._start_backend(
            selection,
            backend,
            image_id,
            fingerprint,
            requested_port,
            deadline,
            complete,
        )
        if not started:
            return result
        admitted, candidate = self._inspect_runtime(
            backend, selection, image_id, fingerprint, requested_port, complete
        )
        if not admitted:
            return candidate
        if isinstance(candidate, str):
            return self._started_candidate(
                candidate, selection, image_id, fingerprint, complete
            )
        return self._complete_ready(
            backend,
            candidate,
            deadline,
            readiness_timeout,
            complete,
            selection,
            image_id,
            fingerprint,
            "started",
            "READY_STARTED",
        )

    def _launch_runtime_locked(
        self,
        selection,
        backend,
        image_id,
        fingerprint,
        startup_timeout,
        requested_port,
        readiness_timeout,
        complete,
    ):
        admitted, candidate = self._inspect_runtime(
            backend, selection, image_id, fingerprint, requested_port, complete
        )
        if not admitted:
            return candidate
        deadline = _launcher().time.monotonic() + startup_timeout
        if candidate == "absent":
            return self._start_runtime(
                selection,
                backend,
                image_id,
                fingerprint,
                requested_port,
                deadline,
                complete,
                readiness_timeout,
            )
        if isinstance(candidate, str):
            return complete(
                self._failure(candidate, selection, image_id, fingerprint)
            )
        return self._complete_ready(
            backend,
            candidate,
            deadline,
            readiness_timeout,
            complete,
            selection,
            image_id,
            fingerprint,
            "reused",
            "READY_REUSED",
        )

    def _launch_runtime(
        self,
        selection: object,
        backend: object,
        image_id: str,
        fingerprint: str,
        startup_timeout: float,
        requested_port: int,
        *,
        lock_held: bool = False,
        readiness_timeout=None,
    ) -> dict[str, Any]:
        "Inspect, start once, and health-check one already identified runtime."

        lock = (
            _launcher().nullcontext()
            if lock_held
            else _launcher()._project_lock(selection, startup_timeout)
        )
        with lock:

            def complete(result: dict[str, Any]) -> dict[str, Any]:
                _launcher()._record_safe_metadata(selection, result)
                return result

            return self._launch_runtime_locked(
                selection,
                backend,
                image_id,
                fingerprint,
                startup_timeout,
                requested_port,
                readiness_timeout,
                complete,
            )

    def _launch_locked(
        self,
        selection,
        backend,
        source,
        image,
        startup_timeout,
        configured_port,
        settings,
    ):
        with _launcher()._project_lock(selection, startup_timeout):
            try:
                image_id, fingerprint = self._image(
                    backend, source, image, selection
                )
            except _launcher().LaunchError as error:
                result = self._failure(error.code, selection)
                _launcher()._record_safe_metadata(selection, result)
                return result
            return self._launch_runtime(
                selection,
                backend,
                image_id,
                fingerprint,
                startup_timeout,
                configured_port,
                lock_held=True,
                readiness_timeout=(
                    settings.readiness_timeout_seconds
                    if settings is not None
                    else None
                ),
            )
