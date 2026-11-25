"""Start and verify the selected Project's production container."""

from __future__ import annotations

from hashlib import sha256
import json
import os
from pathlib import Path
import re
import subprocess
import time

from .release_assets import LocalReleaseError

_DIAGNOSTIC_STATE = (
    '{"id":{{json .Id}},"labels":{{json .Config.Labels}},'
    '"status":{{json .State.Status}},"running":{{json .State.Running}},'
    '"exit_code":{{json .State.ExitCode}},"oom_killed":{{json .State.OOMKilled}},'
    '"health":{{if .State.Health}}{{json .State.Health.Status}}{{else}}null{{end}},'
    '"memory_limit_bytes":{{json .HostConfig.Memory}},"nano_cpus":{{json .HostConfig.NanoCpus}}}'
)
_LOG_FIELDS = ("severity", "event", "component", "operation", "outcome", "code", "exception_class")
_DIAGNOSTIC_TIMEOUT = 5
_STOPPED = {"created", "exited", "dead"}


def _inspect_container(docker, container, root, image, labels, port, *, timeout=30):
    row = json.loads(docker("container", "inspect", "--format", "{{json .}}", container, timeout=timeout))
    state, config = row["State"], row["Config"]
    if state.get("Running") is True:
        ports = row["NetworkSettings"]["Ports"]
    else:
        ports = row["HostConfig"]["PortBindings"]
    mounts = row["Mounts"]
    if (row["Id"] != container or row["Image"] != image
            or any(config["Labels"].get(key) != value for key, value in labels.items())
            or ports["8092/tcp"] != [{"HostIp": "127.0.0.1", "HostPort": str(port)}]
            or not any(m.get("Type") == "volume" and m.get("Name") == "anechoic-framework-db"
                       and m.get("Destination") == "/var/lib/anechoic" and m.get("RW") is True for m in mounts)
            or not any(m.get("Type") == "bind" and m.get("Source") == str(root)
                       and m.get("Destination") == "/project" and m.get("RW") is True for m in mounts)):
        raise LocalReleaseError("local-release-container-identity-mismatch")
    return state


def _wait_healthy(docker, container, root: Path, image: str, labels, port: int, evidence=None) -> str:
    deadline = time.monotonic() + 900
    while True:
        try:
            state = _inspect_container(docker, container, root, image, labels, port)
            if state.get("Running") is not True:
                raise LocalReleaseError("local-release-container-exited")
            health = state.get("Health", {}).get("Status")
            if health == "healthy":
                endpoint = f"http://127.0.0.1:{port}/anechoic/mcp"
                if evidence is not None:
                    evidence.update(
                        container_id=container, image_id=image, project_root=str(root), port=port,
                        fingerprint=labels["org.anechoic.runtime.fingerprint"],
                        project_instance=labels["org.anechoic.project"],
                        control_root=labels["org.anechoic.control_root"],
                        endpoint=endpoint, readiness=health,
                    )
                return endpoint
            if health not in ("starting", "unhealthy") or time.monotonic() >= deadline:
                raise LocalReleaseError("local-release-container-health-failed")
        except (KeyError, TypeError, ValueError) as error:
            raise LocalReleaseError("local-release-container-inspect-invalid") from error
        time.sleep(min(2, max(0, deadline - time.monotonic())))


def _safe_log_fields(line):
    if len(line) > 4096:
        return None
    try:
        row = json.loads(line)
    except (ValueError, RecursionError):
        return None
    if not isinstance(row, dict) or row.get("severity") not in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
        return None
    return {
        key: value for key in _LOG_FIELDS
        if isinstance(value := row.get(key), str) and re.fullmatch("[A-Za-z][A-Za-z0-9_.-]{0,47}", value)
    }


def _diagnostic_state(docker, container, labels):
    row = json.loads(docker("container", "inspect", "--format", _DIAGNOSTIC_STATE, container,
                            timeout=_DIAGNOSTIC_TIMEOUT))
    if row["id"] != container or any(row["labels"].get(key) != value for key, value in labels.items()):
        return None
    state = {key: row[key] for key in ("running", "oom_killed") if type(row.get(key)) is bool}
    state.update({key: row[key] for key in ("exit_code", "memory_limit_bytes", "nano_cpus")
                  if type(row.get(key)) is int and 0 <= row[key] < 2**64})
    if row.get("health") in ("starting", "healthy", "unhealthy"):
        state["health"] = row["health"]
    if row.get("status") in ("created", "running", "paused", "restarting", "removing", "exited", "dead"):
        state["status"] = row["status"]
    return state


def _note_failed_start(failure, docker, container, labels, port):
    details = {"loopback_port": port}
    if isinstance(failure, LocalReleaseError) and re.fullmatch(r"[a-z][a-z0-9-]{0,79}", str(failure)):
        details["failure"] = str(failure)
    if container is not None:
        details["container_id"] = container
        try:
            state = _diagnostic_state(docker, container, labels)
            if state is not None:
                details["state"] = state
                logs = docker("logs", "--tail", "20", container, timeout=_DIAGNOSTIC_TIMEOUT, include_stderr=True)
                details["recent_events"] = [event for line in logs.splitlines()[-20:]
                                            if (event := _safe_log_fields(line))][-10:]
            else:
                details["diagnostics"] = "container ownership unverified"
        except (LocalReleaseError, AttributeError, KeyError, TypeError, ValueError, RecursionError):
            details["diagnostics"] = "Docker inspection or logs unavailable"
    failure.add_note("Local Release startup diagnostics: " + json.dumps(details, sort_keys=True, separators=(",", ":")))
    return "state" in details


def _container_command(root: Path, selection, image: str, port: int, control: str, labels):
    log_level = os.environ.get("ANECHOIC_LOG_LEVEL", "INFO")
    if log_level not in ("DEBUG", "INFO", "WARNING", "ERROR"):
        raise LocalReleaseError("invalid_log_level")
    command = ["run", "-d", "--pull=never", "--init", "--read-only", "--cap-drop", "ALL",
               "--security-opt", "no-new-privileges:true", "--tmpfs", "/tmp:size=128m,mode=1777",
               "--pids-limit", "128", "--memory", "1536m", "--cpus", "1",
               "--log-driver", "local", "--log-opt", "max-size=10m", "--log-opt", "max-file=3",
               "--log-opt", "mode=non-blocking", "--log-opt", "max-buffer-size=1m",
               "-p", f"127.0.0.1:{port}:8092",
               "--mount", f"type=bind,src={root},dst=/project",
               "--mount", "type=volume,src=anechoic-framework-db,dst=/var/lib/anechoic"]
    for key, value in labels.items():
        command.extend(("--label", f"{key}={value}"))
    for key, value in {"ANECHOIC_FRAMEWORK_DB_ROOT": "/var/lib/anechoic", "ANECHOIC_RUNTIME_NAMESPACE": "docker", "ANECHOIC_CONTROL_ROOT": control,
                       "ANECHOIC_PROJECT_INSTANCE_ID": selection.instance_id,
                       "ANECHOIC_MCP_HTTP_HEALTHCHECK": "1",
                       "ANECHOIC_LOG_LEVEL": log_level,
                       "ANECHOIC_HOST_PROJECT_ROOT": str(root)}.items():
        command.extend(("-e", f"{key}={value}"))
    command.extend((image, "mcp-http"))
    return command


def _run_label(run_id):
    return sha256(run_id.encode()).hexdigest()


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


def _docker_failure(stderr):
    error = LocalReleaseError("local-release-container-command-failed")
    tail = stderr[-8192:].lower() if isinstance(stderr, str) else ""
    for patterns, cause in (
        (("address already in use", "port is already allocated", "ports are not available",
          "failed to bind host port"), "Docker could not bind the requested port."),
        (("no space left on device",), "Docker reported no space left on device."),
        (("cannot allocate memory", "not enough memory"), "Docker reported insufficient memory."),
        (("cannot connect to the docker daemon",), "Docker daemon is unavailable."),
    ):
        if any(pattern in tail for pattern in patterns):
            error.add_note(cause)
            break
    return error


def _docker(root, runner):
    def run(*args, timeout=30, include_stderr=False):
        try:
            result = (runner(("docker", *args), root) if runner else subprocess.run(
                ("docker", *args), cwd=root, stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT if include_stderr else subprocess.PIPE, encoding="utf-8", errors="replace",
                timeout=timeout, check=False))
            if result.returncode:
                raise _docker_failure(getattr(result, "stderr", None))
            output = result.stdout
            if include_stderr and isinstance(output, str) and isinstance(result.stderr, str):
                output += "\n" + result.stderr
            if not isinstance(output, str) or len(output) > 1048576:
                raise LocalReleaseError("local-release-container-command-failed")
            return output.strip()
        except (OSError, subprocess.SubprocessError) as error:
            raise LocalReleaseError("local-release-container-command-failed") from error
    return run


def _find_release_container(docker, selection, run_id, *, timeout=30):
    output = docker(
        "container", "ls", "--all", "--no-trunc", "--quiet",
        "--filter", f"label=org.anechoic.project={selection.instance_id}",
        "--filter", f"label=org.anechoic.local_release_run={_run_label(run_id)}",
        timeout=timeout,
    )
    if not output:
        return None
    if not re.fullmatch(r"[0-9a-f]{64}", output):
        raise LocalReleaseError("local-release-resume-container-ambiguous")
    return output


def find_release_container(root, selection, run_id, runner=None):
    return _find_release_container(_docker(root, runner), selection, run_id)


def _discard_failed_start(docker, failure, container, root, selection, image, labels, port, run_id):
    force = container is not None
    if container is None and run_id is not None:
        try:
            container = _find_release_container(docker, selection, run_id, timeout=_DIAGNOSTIC_TIMEOUT)
        except LocalReleaseError:
            failure.add_note("Candidate container discovery unavailable or ambiguous.")
    if not _note_failed_start(failure, docker, container, labels, port):
        return
    try:
        state = _inspect_container(docker, container, root, image, labels, port, timeout=_DIAGNOSTIC_TIMEOUT)
    except (LocalReleaseError, AttributeError, KeyError, TypeError, ValueError):
        failure.add_note(f"Candidate container {container} retained: exact delivery identity unverified.")
        return
    if not force and (state.get("Running") is not False or state.get("Status") not in _STOPPED):
        failure.add_note(f"Candidate container {container} retained: verified stopped state required.")
        return
    try:
        docker("container", "rm", *(("-f",) if force else ()), container)
    except LocalReleaseError:
        failure.add_note(f"Candidate container {container} cleanup failed.")


def reconcile_release_container(root, selection, image, fingerprint, port, container, runner=None, *, run_id):
    """Keep an exact running candidate or remove its verified stopped instance."""
    if not isinstance(container, str) or not re.fullmatch(r"[0-9a-f]{64}", container):
        raise LocalReleaseError("local-release-container-id-invalid")
    docker = _docker(root, runner)
    labels = _labels(root, selection, fingerprint, run_id)
    try:
        try:
            state = _inspect_container(docker, container, root, image, labels, port)
        except (AttributeError, KeyError, TypeError, ValueError) as error:
            raise LocalReleaseError("local-release-container-inspect-invalid") from error
        if state.get("Running") is True:
            return container
        if state.get("Running") is not False or state.get("Status") not in _STOPPED:
            raise LocalReleaseError("local-release-resume-container-unverified")
        docker("container", "rm", container)
        return None
    except LocalReleaseError as failure:
        _note_failed_start(failure, docker, container, labels, port)
        raise


def verify_release_container(root, selection, image, fingerprint, port, container, runner=None, *, run_id=None,
                             evidence=None):
    if not isinstance(container, str) or not re.fullmatch(r"[0-9a-f]{64}", container):
        raise LocalReleaseError("local-release-container-id-invalid")
    docker = _docker(root, runner)
    labels = _labels(root, selection, fingerprint, run_id)
    try:
        return _wait_healthy(docker, container, root, image, labels, port, evidence)
    except BaseException as failure:
        _note_failed_start(failure, docker, container, labels, port)
        raise


def start_container(root: Path, selection, image: str, fingerprint: str, port: int, runner=None, *,
                    existing_container: str | None = None, run_id: str | None = None,
                    evidence: dict | None = None) -> str:
    """Start the immutable image and return its health-checked loopback endpoint."""
    if (not re.fullmatch(r"sha256:[0-9a-f]{64}", image)
            or not re.fullmatch(r"[0-9a-f]{64}", fingerprint)
            or not re.fullmatch(r"[0-9a-f]{64}", selection.instance_id)
            or type(port) is not int or not 1 <= port <= 65535
            or selection.root != root or not root.is_absolute() or "," in str(root)):
        raise LocalReleaseError("local-release-container-input-invalid")
    control = selection.control_relative.as_posix()
    if not control or control.startswith("/") or ".." in selection.control_relative.parts:
        raise LocalReleaseError("local-release-container-input-invalid")
    labels = _labels(root, selection, fingerprint, run_id)
    docker = _docker(root, runner)
    if existing_container is not None and (not isinstance(existing_container, str)
                                           or not re.fullmatch(r"[0-9a-f]{64}", existing_container)):
        raise LocalReleaseError("local-release-container-id-invalid")
    container = existing_container
    command = _container_command(root, selection, image, port, control, labels) if container is None else None
    try:
        if container is None:
            identifier = docker(*command)
            if not re.fullmatch(r"[0-9a-f]{64}", identifier):
                raise LocalReleaseError("local-release-container-id-invalid")
            container = identifier
        return _wait_healthy(docker, container, root, image, labels, port, evidence)
    except BaseException as failure:
        if existing_container is None:
            _discard_failed_start(docker, failure, container, root, selection, image, labels, port, run_id)
        else:
            _note_failed_start(failure, docker, container, labels, port)
        raise
