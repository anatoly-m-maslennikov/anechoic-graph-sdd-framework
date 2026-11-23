"""Start and verify the selected Project's production container."""

from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess
import time

from .release_assets import LocalReleaseError


def _wait_healthy(docker, container, root: Path, image: str, labels, port: int) -> str:
    deadline = time.monotonic() + 420
    while True:
        try:
            row = json.loads(docker("container", "inspect", "--format", "{{json .}}", container))
            state, config = row["State"], row["Config"]
            bindings = row["NetworkSettings"]["Ports"]["8092/tcp"]
            mounts = row["Mounts"]
            if (row["Id"] != container or row["Image"] != image or
                    any(config["Labels"].get(key) != value for key, value in labels.items()) or
                    bindings != [{"HostIp": "127.0.0.1", "HostPort": str(port)}] or
                    not any(m.get("Type") == "volume" and m.get("Name") == "anechoic-framework-db"
                            and m.get("Destination") == "/var/lib/anechoic" and m.get("RW") is True for m in mounts) or
                    not any(m.get("Type") == "bind" and m.get("Source") == str(root)
                            and m.get("Destination") == "/project" and m.get("RW") is True for m in mounts)):
                raise LocalReleaseError("local-release-container-identity-mismatch")
            if state.get("Running") is not True:
                raise LocalReleaseError("local-release-container-exited")
            health = state.get("Health", {}).get("Status")
            if health == "healthy":
                return f"http://127.0.0.1:{port}/anechoic/mcp"
            if health not in ("starting", "unhealthy") or time.monotonic() >= deadline:
                raise LocalReleaseError("local-release-container-health-failed")
        except (KeyError, TypeError, ValueError) as error:
            raise LocalReleaseError("local-release-container-inspect-invalid") from error
        time.sleep(min(2, max(0, deadline - time.monotonic())))


def _container_command(root: Path, selection, image: str, port: int, control: str, labels):
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
                       "ANECHOIC_HOST_PROJECT_ROOT": str(root)}.items():
        command.extend(("-e", f"{key}={value}"))
    command.extend((image, "mcp-http"))
    return command


def start_container(root: Path, selection, image: str, fingerprint: str, port: int, runner=None, *, existing_container: str | None = None) -> str:
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
    labels = {
        "org.anechoic.project": selection.instance_id,
        "org.anechoic.runtime.fingerprint": fingerprint,
        "org.anechoic.service": "mcp-http",
        "org.anechoic.control_root": control,
        "org.anechoic.host_project_root": str(root),
    }

    def docker(*args):
        try:
            result = (runner(("docker", *args), root) if runner else subprocess.run(
                ("docker", *args), cwd=root, capture_output=True, text=True, timeout=30, check=False))
            if result.returncode or not isinstance(result.stdout, str) or len(result.stdout) > 1048576:
                raise LocalReleaseError("local-release-container-command-failed")
            return result.stdout.strip()
        except (OSError, subprocess.SubprocessError) as error:
            raise LocalReleaseError("local-release-container-command-failed") from error

    command = _container_command(root, selection, image, port, control, labels)
    if existing_container is not None and (not isinstance(existing_container, str)
                                           or not re.fullmatch(r"[0-9a-f]{64}", existing_container)):
        raise LocalReleaseError("local-release-container-id-invalid")
    container = existing_container if existing_container is not None else docker(*command)
    if not re.fullmatch(r"[0-9a-f]{64}", container):
        raise LocalReleaseError("local-release-container-id-invalid")
    try:
        return _wait_healthy(docker, container, root, image, labels, port)
    except BaseException as failure:
        if existing_container is None:
            try:
                docker("container", "rm", "-f", container)
            except LocalReleaseError:
                failure.add_note(f"Candidate container {container} cleanup failed.")
        raise
