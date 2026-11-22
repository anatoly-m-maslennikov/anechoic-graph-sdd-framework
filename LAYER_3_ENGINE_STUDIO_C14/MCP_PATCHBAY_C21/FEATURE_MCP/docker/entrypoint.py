"""Foreground services with immutable code and explicit runtime-only state."""


from concurrent.futures import CancelledError
import json
import os
from pathlib import Path
import sys

MCP = Path(__file__).resolve().parents[1]
PROJECT_ROOT = Path("/project")
ENGINE = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ENGINE))

from MCP_PATCHBAY_C21.FEATURE_MCP.mcp_startup_boundary import ExplicitStartupFailure  # noqa: E402

RUNTIME_MODES = frozenset({"mcp", "mcp-http", "shared-mcp"})


def _process_failure(mode, error):
    if mode not in RUNTIME_MODES:
        code, severity = "invalid_runtime_mode", "WARNING"
    elif isinstance(error, ExplicitStartupFailure):
        code, severity = error.code, "ERROR"
    else:
        code, severity = "internal_failure", "WARNING"
    try:
        print(json.dumps({"error": code, "severity": severity}, separators=(",", ":")), file=sys.stderr)
    except Exception:
        pass
    return 1


def _shared_mcp_command():
    settings = os.environ.get("ANECHOIC_HOST_SETTINGS")
    if not settings:
        raise ExplicitStartupFailure("shared_host_settings_unavailable")
    return [
        sys.executable,
        "-B", "-P", "-m", "MCP_PATCHBAY_C21.FEATURE_MCP.shared_http_server",
        "--host-settings",
        settings,
    ]


def _exec_service(mode):
    if mode == "shared-mcp":
        command = _shared_mcp_command()
    else:
        paths = {
            "mcp": MCP / "server.py",
            "mcp-http": MCP / "server.py",
        }
        if mode not in paths:
            raise ValueError("unsupported runtime mode")
        command = [sys.executable, "-B", "-P", "-m", "MCP_PATCHBAY_C21.FEATURE_MCP.server", "--project-root", str(PROJECT_ROOT)]
        if mode == "mcp-http":
            command += ["--transport", "streamable-http"]
        if mode in {"mcp", "mcp-http"}:
            for flag, key in (
                ("--control-root", "ANECHOIC_CONTROL_ROOT"),
                ("--instance-id", "ANECHOIC_PROJECT_INSTANCE_ID"),
                ("--host-project-root", "ANECHOIC_HOST_PROJECT_ROOT"),
            ):
                if key in os.environ:
                    command += [flag, os.environ[key]]
    try:
        os.execve(sys.executable, command, {**{k: v for k, v in os.environ.items() if k != "PYTHONHOME"}, "PYTHONPATH": str(ENGINE)})
    except OSError as error:
        raise ExplicitStartupFailure("service_start_failed") from error


def _dispatch(mode):
    _exec_service(mode)


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else ""

    try:
        _dispatch(mode)
    except CancelledError:
        raise
    except Exception as error:
        return _process_failure(mode, error)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
