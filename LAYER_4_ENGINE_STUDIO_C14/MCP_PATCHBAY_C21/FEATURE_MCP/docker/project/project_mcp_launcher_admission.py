"""Validate and attribute the selected Project's Docker runtime."""

from pathlib import Path
from typing import Any, Mapping

from MCP_PATCHBAY_C21.FEATURE_MCP.docker.shared_support.\
    shared_support__shared import MCP_PATH
from MCP_PATCHBAY_C21.FEATURE_MCP.docker.project.\
    project_mcp_launcher_common import (
    LaunchError,
    _FINGERPRINT,
    _IMAGE,
    _selection_root,
)


def _labels(row: Mapping[str, Any]) -> Mapping[str, Any] | None:
    config = row.get("Config")
    labels = config.get("Labels") if isinstance(config, Mapping) else None
    return labels if isinstance(labels, Mapping) else None


def _project_mount_is_exact(row: Mapping[str, Any], selection: object) -> bool:
    """Validate a raw inspect mount when Docker supplied one.

    The injected contract fake omits `Mounts`; real `docker inspect` rows
    carry it and are consequently checked here.
    """
    if "Mounts" not in row:
        return True
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
    root = _selection_root(selection)
    return (
        mount.get("Type") == "bind"
        and mount.get("Destination") == "/project"
        and isinstance(source, str)
        and Path(source) == root
    )


def _project_labels_are_exact(
    labels: Mapping[str, Any], row: Mapping[str, Any], selection: object
) -> bool:
    """Bind real Docker inspect rows to exactly the selected Project.

    The frozen backend seam intentionally supplies the small common subset of
    inspect fields and has no ``Mounts`` member.  Docker's actual inspect
    schema always includes that member, so once it is present require the
    compose labels that bind the selected direct control root and host root.
    Together with the sole ``/project`` bind this excludes sibling, ancestor,
    and Docker-socket binds.
    """
    if "Mounts" not in row:
        return True
    control = getattr(selection, "control_relative", None)
    if not isinstance(control, Path) or control.is_absolute():
        return False
    return labels.get(
        "org.anechoic.control_root"
    ) == control.as_posix() and labels.get(
        "org.anechoic.host_project_root"
    ) == str(_selection_root(selection))


def _publisher(row: Mapping[str, Any]) -> tuple[str, int] | None:
    network = row.get("NetworkSettings")
    ports = network.get("Ports") if isinstance(network, Mapping) else None
    if not isinstance(ports, Mapping) or set(ports) != {"8092/tcp"}:
        return None
    rows = ports.get("8092/tcp")
    if (
        not isinstance(rows, list)
        or len(rows) != 1
        or not isinstance(rows[0], Mapping)
    ):
        return None
    publisher = rows[0]
    value = publisher.get("HostPort")
    if (
        publisher.get("HostIp") != "127.0.0.1"
        or not isinstance(value, str)
        or not value.isdecimal()
    ):
        return None
    port = int(value)
    return (
        ("http://127.0.0.1:" + value + MCP_PATH, port)
        if 1 <= port <= 65535
        else None
    )


def _attribution(
    selection: object | None,
    image_id: str | None = None,
    fingerprint: str | None = None,
) -> dict[str, Any]:
    """Return only fields that remain safe if a launch stops early."""
    root = control = project_id = None
    if selection is not None:
        try:
            root = str(_selection_root(selection))
            control_value = getattr(selection, "control_root", None)
            if isinstance(control_value, Path) and control_value.is_absolute():
                control = str(control_value)
            value = getattr(selection, "instance_id", None)
            if isinstance(value, str) and _FINGERPRINT.fullmatch(value):
                project_id = value
        except LaunchError:
            pass
    return {
        "project_root": root,
        "control_root": control,
        "project_id": project_id,
        "image_id": image_id
        if isinstance(image_id, str) and _IMAGE.fullmatch(image_id)
        else None,
        "fingerprint": (
            fingerprint
            if isinstance(fingerprint, str)
            and _FINGERPRINT.fullmatch(fingerprint)
            else None
        ),
        "container_id": None,
        "service": "mcp-http",
        "port": None,
        "readiness": False,
    }


def _healthy(row):
    state = row.get("State")
    health = state.get("Health") if isinstance(state, Mapping) else None
    return (
        isinstance(state, Mapping)
        and state.get("Status") == "running"
        and isinstance(health, Mapping)
        and health.get("Status") == "healthy"
    )


def _admit_runtime(
    rows: object,
    selection: object,
    image_id: str,
    fingerprint: str,
    requested_port: int,
):
    """Return absent, a ready candidate, or its terminal safe condition."""
    if not isinstance(rows, list):
        return "DOCKER_PUBLICATION_FAILED"
    if not rows:
        return "absent"
    if len(rows) != 1 or not isinstance(rows[0], Mapping):
        return "DOCKER_PUBLICATION_FAILED"
    row = rows[0]
    labels = _labels(row)
    instance = getattr(selection, "instance_id", None)
    if (
        labels is None
        or labels.get("org.anechoic.project") != instance
        or labels.get("org.anechoic.service") != "mcp-http"
        or labels.get("org.anechoic.runtime.fingerprint") != fingerprint
        or row.get("Image") != image_id
        or not _project_labels_are_exact(labels, row, selection)
        or not _project_mount_is_exact(row, selection)
    ):
        return "RUNTIME_MISMATCH"
    if not _healthy(row):
        return "RUNTIME_UNHEALTHY"
    publisher = _publisher(row)
    if publisher is None:
        return "DOCKER_PUBLICATION_FAILED"
    if publisher[1] != requested_port:
        return "RUNTIME_MISMATCH"
    container = row.get("Id")
    if not isinstance(container, str) or not container:
        return "DOCKER_PUBLICATION_FAILED"
    return {
        "row": row,
        "container_id": container,
        "url": publisher[0],
        "port": publisher[1],
    }
