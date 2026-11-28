"""Start and verify the selected Project's production container."""

from __future__ import annotations

from pathlib import Path
import re
import time

from ..release_assets import LocalReleaseError
from ._release_container_diagnostics import (
    _DIAGNOSTIC_TIMEOUT,
    _inspect_container,
    _note_failed_start,
    _run_label,
)
from ._release_container_runtime import _container_command, _docker

_STOPPED = {"created", "exited", "dead"}


def _wait_healthy(
    docker, container, root: Path, image: str, labels, port: int, evidence=None
) -> str:
    deadline = time.monotonic() + 900
    while True:
        try:
            state = _inspect_container(
                docker, container, root, image, labels, port
            )
            if state.get("Running") is not True:
                raise LocalReleaseError("local-release-container-exited")
            health = state.get("Health", {}).get("Status")
            if health == "healthy":
                endpoint = f"http://127.0.0.1:{port}/anechoic/mcp"
                if evidence is not None:
                    evidence.update(
                        container_id=container,
                        image_id=image,
                        project_root=str(root),
                        port=port,
                        fingerprint=labels["org.anechoic.runtime.fingerprint"],
                        project_instance=labels["org.anechoic.project"],
                        control_root=labels["org.anechoic.control_root"],
                        endpoint=endpoint,
                        readiness=health,
                    )
                return endpoint
            if (
                health not in ("starting", "unhealthy")
                or time.monotonic() >= deadline
            ):
                raise LocalReleaseError(
                    "local-release-container-health-failed"
                )
        except (KeyError, TypeError, ValueError) as error:
            raise LocalReleaseError(
                "local-release-container-inspect-invalid"
            ) from error
        time.sleep(min(2, max(0, deadline - time.monotonic())))


def _labels(root, selection, fingerprint, run_id):
    result = {
        "org.anechoic.project": selection.instance_id,
        "org.anechoic.runtime.fingerprint": fingerprint,
        "org.anechoic.service": "mcp-http",
        "org.anechoic.control_root": selection.control_relative.as_posix(),
        "org.anechoic.host_project_root": str(root),
    }
    if run_id is not None:
        result["org.anechoic.local_release_run"] = _run_label(run_id)
    return result


def _find_release_container(docker, selection, run_id, *, timeout=30):
    output = docker(
        "container",
        "ls",
        "--all",
        "--no-trunc",
        "--quiet",
        "--filter",
        f"label=org.anechoic.project={selection.instance_id}",
        "--filter",
        f"label=org.anechoic.local_release_run={_run_label(run_id)}",
        timeout=timeout,
    )
    if not output:
        return None
    if not re.fullmatch(r"[0-9a-f]{64}", output):
        raise LocalReleaseError("local-release-resume-container-ambiguous")
    return output


def find_release_container(root, selection, run_id, runner=None):
    return _find_release_container(_docker(root, runner), selection, run_id)


def _discard_failed_start(
    docker, failure, container, root, selection, image, labels, port, run_id
):
    force = container is not None
    if container is None and run_id is not None:
        try:
            container = _find_release_container(
                docker, selection, run_id, timeout=_DIAGNOSTIC_TIMEOUT
            )
        except LocalReleaseError:
            failure.add_note(
                "Candidate container discovery unavailable or ambiguous."
            )
    if not _note_failed_start(failure, docker, container, labels, port):
        return
    try:
        state = _inspect_container(
            docker,
            container,
            root,
            image,
            labels,
            port,
            timeout=_DIAGNOSTIC_TIMEOUT,
        )
    except LocalReleaseError, AttributeError, KeyError, TypeError, ValueError:
        failure.add_note(
            f"Candidate container {container} retained: "
            "exact delivery identity unverified."
        )
        return
    if not force and (
        state.get("Running") is not False
        or state.get("Status") not in _STOPPED
    ):
        failure.add_note(
            f"Candidate container {container} retained: "
            "verified stopped state required."
        )
        return
    try:
        docker("container", "rm", *(("-f",) if force else ()), container)
    except LocalReleaseError:
        failure.add_note(f"Candidate container {container} cleanup failed.")


def reconcile_release_container(
    root,
    selection,
    image,
    fingerprint,
    port,
    container,
    runner=None,
    *,
    run_id,
):
    """Keep a running candidate or remove its verified stopped instance."""
    if not isinstance(container, str) or not re.fullmatch(
        r"[0-9a-f]{64}", container
    ):
        raise LocalReleaseError("local-release-container-id-invalid")
    docker = _docker(root, runner)
    labels = _labels(root, selection, fingerprint, run_id)
    try:
        try:
            state = _inspect_container(
                docker, container, root, image, labels, port
            )
        except (AttributeError, KeyError, TypeError, ValueError) as error:
            raise LocalReleaseError(
                "local-release-container-inspect-invalid"
            ) from error
        if state.get("Running") is True:
            return container
        if (
            state.get("Running") is not False
            or state.get("Status") not in _STOPPED
        ):
            raise LocalReleaseError(
                "local-release-resume-container-unverified"
            )
        docker("container", "rm", container)
        return None
    except LocalReleaseError as failure:
        _note_failed_start(failure, docker, container, labels, port)
        raise


def verify_release_container(
    root,
    selection,
    image,
    fingerprint,
    port,
    container,
    runner=None,
    *,
    run_id=None,
    evidence=None,
):
    if not isinstance(container, str) or not re.fullmatch(
        r"[0-9a-f]{64}", container
    ):
        raise LocalReleaseError("local-release-container-id-invalid")
    docker = _docker(root, runner)
    labels = _labels(root, selection, fingerprint, run_id)
    try:
        return _wait_healthy(
            docker, container, root, image, labels, port, evidence
        )
    except BaseException as failure:
        _note_failed_start(failure, docker, container, labels, port)
        raise


def _validated_container_input(root, selection, image, fingerprint, port):
    if (
        not re.fullmatch(r"sha256:[0-9a-f]{64}", image)
        or not re.fullmatch(r"[0-9a-f]{64}", fingerprint)
        or not re.fullmatch(r"[0-9a-f]{64}", selection.instance_id)
        or type(port) is not int
        or not 1 <= port <= 65535
        or selection.root != root
        or not root.is_absolute()
        or "," in str(root)
    ):
        raise LocalReleaseError("local-release-container-input-invalid")
    control = selection.control_relative.as_posix()
    if (
        not control
        or control.startswith("/")
        or ".." in selection.control_relative.parts
    ):
        raise LocalReleaseError("local-release-container-input-invalid")
    return control


def _handle_start_failure(
    existing_container,
    docker,
    failure,
    container,
    root,
    selection,
    image,
    labels,
    port,
    run_id,
):
    if existing_container is None:
        _discard_failed_start(
            docker,
            failure,
            container,
            root,
            selection,
            image,
            labels,
            port,
            run_id,
        )
    else:
        _note_failed_start(failure, docker, container, labels, port)


def _start_command(
    root, selection, image, port, control, labels, existing_container
):
    if existing_container is not None and (
        not isinstance(existing_container, str)
        or not re.fullmatch(r"[0-9a-f]{64}", existing_container)
    ):
        raise LocalReleaseError("local-release-container-id-invalid")
    command = (
        _container_command(root, selection, image, port, control, labels)
        if existing_container is None
        else None
    )
    return command


def start_container(
    root: Path,
    selection,
    image: str,
    fingerprint: str,
    port: int,
    runner=None,
    *,
    existing_container: str | None = None,
    run_id: str | None = None,
    evidence: dict | None = None,
) -> str:
    """Start the image and return its health-checked loopback endpoint."""
    control = _validated_container_input(
        root, selection, image, fingerprint, port
    )
    labels = _labels(root, selection, fingerprint, run_id)
    docker = _docker(root, runner)
    container = existing_container
    command = _start_command(
        root, selection, image, port, control, labels, existing_container
    )
    try:
        if container is None:
            identifier = docker(*command)
            if not re.fullmatch(r"[0-9a-f]{64}", identifier):
                raise LocalReleaseError("local-release-container-id-invalid")
            container = identifier
        return _wait_healthy(
            docker, container, root, image, labels, port, evidence
        )
    except BaseException as failure:
        _handle_start_failure(
            existing_container,
            docker,
            failure,
            container,
            root,
            selection,
            image,
            labels,
            port,
            run_id,
        )
        raise
