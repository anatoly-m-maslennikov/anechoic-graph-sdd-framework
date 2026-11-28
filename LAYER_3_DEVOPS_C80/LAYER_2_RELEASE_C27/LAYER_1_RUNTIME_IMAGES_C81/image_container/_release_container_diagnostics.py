"""Inspect container identity and record safe startup diagnostics."""

from hashlib import sha256
import json
import re

from ..release_assets import LocalReleaseError


_DIAGNOSTIC_STATE = (
    '{"id":{{json .Id}},"labels":{{json .Config.Labels}},'
    '"status":{{json .State.Status}},"running":{{json .State.Running}},'
    '"exit_code":{{json .State.ExitCode}},'
    '"oom_killed":{{json .State.OOMKilled}},'
    '"health":{{if .State.Health}}'
    "{{json .State.Health.Status}}{{else}}null{{end}},"
    '"memory_limit_bytes":{{json .HostConfig.Memory}},'
    '"nano_cpus":{{json .HostConfig.NanoCpus}}}'
)

_LOG_FIELDS = (
    "severity",
    "event",
    "component",
    "operation",
    "outcome",
    "code",
    "exception_class",
)

_DIAGNOSTIC_TIMEOUT = 5


def _inspect_container(
    docker, container, root, image, labels, port, *, timeout=30
):
    row = json.loads(
        docker(
            "container",
            "inspect",
            "--format",
            "{{json .}}",
            container,
            timeout=timeout,
        )
    )
    state, config = row["State"], row["Config"]
    if state.get("Running") is True:
        ports = row["NetworkSettings"]["Ports"]
    else:
        ports = row["HostConfig"]["PortBindings"]
    mounts = row["Mounts"]
    if (
        row["Id"] != container
        or row["Image"] != image
        or any(
            config["Labels"].get(key) != value for key, value in labels.items()
        )
        or ports["8092/tcp"]
        != [{"HostIp": "127.0.0.1", "HostPort": str(port)}]
        or not any(
            m.get("Type") == "volume"
            and m.get("Name") == "anechoic-framework-db"
            and m.get("Destination") == "/var/lib/anechoic"
            and m.get("RW") is True
            for m in mounts
        )
        or not any(
            m.get("Type") == "bind"
            and m.get("Source") == str(root)
            and m.get("Destination") == "/project"
            and m.get("RW") is True
            for m in mounts
        )
    ):
        raise LocalReleaseError("local-release-container-identity-mismatch")
    return state


def _safe_log_fields(line):
    if len(line) > 4096:
        return None
    try:
        row = json.loads(line)
    except ValueError, RecursionError:
        return None
    if not isinstance(row, dict) or row.get("severity") not in (
        "DEBUG",
        "INFO",
        "WARNING",
        "ERROR",
        "CRITICAL",
    ):
        return None
    return {
        key: value
        for key in _LOG_FIELDS
        if isinstance(value := row.get(key), str)
        and re.fullmatch("[A-Za-z][A-Za-z0-9_.-]{0,47}", value)
    }


def _diagnostic_state(docker, container, labels):
    row = json.loads(
        docker(
            "container",
            "inspect",
            "--format",
            _DIAGNOSTIC_STATE,
            container,
            timeout=_DIAGNOSTIC_TIMEOUT,
        )
    )
    if row["id"] != container or any(
        row["labels"].get(key) != value for key, value in labels.items()
    ):
        return None
    state = {
        key: row[key]
        for key in ("running", "oom_killed")
        if type(row.get(key)) is bool
    }
    state.update(
        {
            key: row[key]
            for key in ("exit_code", "memory_limit_bytes", "nano_cpus")
            if type(row.get(key)) is int and 0 <= row[key] < 2**64
        }
    )
    if row.get("health") in ("starting", "healthy", "unhealthy"):
        state["health"] = row["health"]
    if row.get("status") in (
        "created",
        "running",
        "paused",
        "restarting",
        "removing",
        "exited",
        "dead",
    ):
        state["status"] = row["status"]
    return state


def _note_failed_start(failure, docker, container, labels, port):
    details = {"loopback_port": port}
    if isinstance(failure, LocalReleaseError) and re.fullmatch(
        r"[a-z][a-z0-9-]{0,79}", str(failure)
    ):
        details["failure"] = str(failure)
    if container is not None:
        details["container_id"] = container
        try:
            state = _diagnostic_state(docker, container, labels)
            if state is not None:
                details["state"] = state
                logs = docker(
                    "logs",
                    "--tail",
                    "20",
                    container,
                    timeout=_DIAGNOSTIC_TIMEOUT,
                    include_stderr=True,
                )
                details["recent_events"] = [
                    event
                    for line in logs.splitlines()[-20:]
                    if (event := _safe_log_fields(line))
                ][-10:]
            else:
                details["diagnostics"] = "container ownership unverified"
        except (
            LocalReleaseError,
            AttributeError,
            KeyError,
            TypeError,
            ValueError,
            RecursionError,
        ):
            details["diagnostics"] = "Docker inspection or logs unavailable"
    failure.add_note(
        "Local Release startup diagnostics: "
        + json.dumps(details, sort_keys=True, separators=(",", ":"))
    )
    return "state" in details


def _run_label(run_id):
    return sha256(run_id.encode()).hexdigest()
