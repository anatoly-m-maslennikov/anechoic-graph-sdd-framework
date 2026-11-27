"""Foreground services with immutable code and explicit runtime-only state."""

from concurrent.futures import CancelledError
import json
import os
from pathlib import Path
import sys

PROJECT_ROOT = Path("/project")
ENGINE = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ENGINE))

from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import (  # noqa: E402
    ExplicitStartupFailure,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.docker.\
    runtime_log_level import (  # noqa: E402
    direct_log_level,
)  # fmt: skip

RUNTIME_MODES = frozenset({"mcp", "mcp-http", "shared-mcp"})


def _process_failure(mode, error):
    if mode not in RUNTIME_MODES:
        code, severity = "invalid_runtime_mode", "WARNING"
    elif isinstance(error, ExplicitStartupFailure):
        code, severity = error.code, "ERROR"
    else:
        code, severity = "internal_failure", "WARNING"
    try:
        print(
            json.dumps(
                {"error": code, "severity": severity}, separators=(",", ":")
            ),
            file=sys.stderr,
        )
    except Exception:
        pass
    return 1


def _shared_mcp_command():
    settings = os.environ.get("ANECHOIC_HOST_SETTINGS")
    if not settings:
        raise ExplicitStartupFailure("shared_host_settings_unavailable")
    return [
        sys.executable,
        "-B",
        "-P",
        "-m",
        "MCP_PATCHBAY_C21.FEATURE_MCP.shared_http_server",
        "--host-settings",
        settings,
    ]


def _project_mcp_command(mode):
    command = [
        sys.executable,
        "-B",
        "-P",
        "-m",
        "MCP_PATCHBAY_C21.FEATURE_MCP.server",
        "--project-root",
        str(PROJECT_ROOT),
    ]
    if mode == "mcp-http":
        command += ["--transport", "streamable-http"]
    for flag, key in (
        ("--control-root", "ANECHOIC_CONTROL_ROOT"),
        ("--instance-id", "ANECHOIC_PROJECT_INSTANCE_ID"),
        ("--host-project-root", "ANECHOIC_HOST_PROJECT_ROOT"),
    ):
        if key in os.environ:
            command += [flag, os.environ[key]]
    return command


def _exec_service(mode):
    if mode not in RUNTIME_MODES:
        raise ValueError("unsupported runtime mode")
    stack = os.environ.get("ANECHOIC_RUNTIME_STACK")
    command = (
        _shared_mcp_command()
        if mode == "shared-mcp"
        else _project_mcp_command(mode)
    )
    environment = {
        **{k: v for k, v in os.environ.items() if k != "PYTHONHOME"},
        "PYTHONPATH": str(ENGINE),
    }
    try:
        environment["ANECHOIC_LOG_LEVEL"] = direct_log_level()
    except ValueError as error:
        raise ExplicitStartupFailure("invalid_log_level") from error
    if mode == "shared-mcp" and stack == "beta_next":
        from MCP_PATCHBAY_C21.FEATURE_MCP.docker.shared_supervisor import (
            supervise,
        )

        return supervise(
            command, environment, environment["ANECHOIC_HOST_SETTINGS"]
        )
    if mode == "mcp-http" and stack == "beta_next":
        from MCP_PATCHBAY_C21.FEATURE_MCP.docker.shared_supervisor import (
            supervise_project,
        )

        return supervise_project(command, environment, PROJECT_ROOT)
    try:
        os.execve(sys.executable, command, environment)
    except OSError as error:
        raise ExplicitStartupFailure("service_start_failed") from error


def _dispatch(mode):
    return _exec_service(mode)


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else ""

    try:
        return _dispatch(mode) or 0
    except CancelledError:
        raise
    except Exception as error:
        return _process_failure(mode, error)


if __name__ == "__main__":
    raise SystemExit(main())
