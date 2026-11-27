"""Compose and execute container runtime commands."""

import os
from pathlib import Path
import subprocess

from .release_assets import LocalReleaseError


def _append_container_environment(
    command, root, selection, control, log_level
):
    for key, value in {
        "ANECHOIC_FRAMEWORK_DB_ROOT": "/var/lib/anechoic",
        "ANECHOIC_RUNTIME_NAMESPACE": "docker",
        "ANECHOIC_CONTROL_ROOT": control,
        "ANECHOIC_PROJECT_INSTANCE_ID": selection.instance_id,
        "ANECHOIC_MCP_HTTP_HEALTHCHECK": "1",
        "ANECHOIC_LOG_LEVEL": log_level,
        "ANECHOIC_HOST_PROJECT_ROOT": str(root),
    }.items():
        command.extend(("-e", f"{key}={value}"))


def _container_log_level():
    log_level = os.environ.get("ANECHOIC_LOG_LEVEL", "INFO")
    if log_level not in ("DEBUG", "INFO", "WARNING", "ERROR"):
        raise LocalReleaseError("invalid_log_level")
    return log_level


def _container_command(
    root: Path, selection, image: str, port: int, control: str, labels
):
    log_level = _container_log_level()
    command = [
        "run",
        "-d",
        "--pull=never",
        "--init",
        "--read-only",
        "--cap-drop",
        "ALL",
        "--security-opt",
        "no-new-privileges:true",
        "--tmpfs",
        "/tmp:size=128m,mode=1777",
        "--pids-limit",
        "128",
        "--memory",
        "1536m",
        "--cpus",
        "1",
        "--log-driver",
        "local",
        "--log-opt",
        "max-size=10m",
        "--log-opt",
        "max-file=3",
        "--log-opt",
        "mode=non-blocking",
        "--log-opt",
        "max-buffer-size=1m",
        "-p",
        f"127.0.0.1:{port}:8092",
        "--mount",
        f"type=bind,src={root},dst=/project",
        "--mount",
        "type=volume,src=anechoic-framework-db,dst=/var/lib/anechoic",
    ]
    for key, value in labels.items():
        command.extend(("--label", f"{key}={value}"))
    _append_container_environment(command, root, selection, control, log_level)
    command.extend((image, "mcp-http"))
    return command


def _docker_failure(stderr):
    error = LocalReleaseError("local-release-container-command-failed")
    tail = stderr[-8192:].lower() if isinstance(stderr, str) else ""
    for patterns, cause in (
        (
            (
                "address already in use",
                "port is already allocated",
                "ports are not available",
                "failed to bind host port",
            ),
            "Docker could not bind the requested port.",
        ),
        (
            ("no space left on device",),
            "Docker reported no space left on device.",
        ),
        (
            ("cannot allocate memory", "not enough memory"),
            "Docker reported insufficient memory.",
        ),
        (
            ("cannot connect to the docker daemon",),
            "Docker daemon is unavailable.",
        ),
    ):
        if any(pattern in tail for pattern in patterns):
            error.add_note(cause)
            break
    return error


def _docker(root, runner):
    def run(*args, timeout=30, include_stderr=False):
        try:
            result = (
                runner(("docker", *args), root)
                if runner
                else subprocess.run(
                    ("docker", *args),
                    cwd=root,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT
                    if include_stderr
                    else subprocess.PIPE,
                    encoding="utf-8",
                    errors="replace",
                    timeout=timeout,
                    check=False,
                )
            )
            if result.returncode:
                raise _docker_failure(getattr(result, "stderr", None))
            output = result.stdout
            if (
                include_stderr
                and isinstance(output, str)
                and isinstance(result.stderr, str)
            ):
                output += "\n" + result.stderr
            if not isinstance(output, str) or len(output) > 1048576:
                raise LocalReleaseError(
                    "local-release-container-command-failed"
                )
            return output.strip()
        except (OSError, subprocess.SubprocessError) as error:
            raise LocalReleaseError(
                "local-release-container-command-failed"
            ) from error

    return run
