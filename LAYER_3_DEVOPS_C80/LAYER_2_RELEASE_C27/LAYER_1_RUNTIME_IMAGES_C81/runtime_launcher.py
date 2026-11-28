"""Call the Engine shared MCP launcher in its production environment."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess


def _base_command(root: Path, engine: Path) -> list[str]:
    return [
        "uv",
        "run",
        "--no-compile-bytecode",
        "--project",
        str(root / "LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine"),
        "--locked",
        "--python",
        "3.14",
        "--managed-python",
        "--no-env-file",
        "--no-default-groups",
        "--group",
        "runtime",
        "python",
        "-B",
        "-P",
        str(
            engine
            / "MCP_PATCHBAY_C21/FEATURE_MCP/docker/shared_mcp_launcher.py"
        ),
    ]


def _launcher_command(
    root: Path,
    engine: Path,
    image: str | None,
    host_settings: str | Path | None,
    apply: bool,
    verify_mcp: bool,
    startup_timeout: int | None,
    readiness_timeout: int | None,
    mounted_folder: str | Path | None,
) -> list[str]:
    command = _base_command(root, engine)
    if image is not None:
        command += ["--image", image]
    if startup_timeout is not None:
        command += ["--startup-timeout", str(startup_timeout)]
    if readiness_timeout is not None:
        command += ["--readiness-timeout", str(readiness_timeout)]
    if mounted_folder is not None:
        command += ["--mounted-folder", str(Path(mounted_folder).absolute())]
    elif host_settings is not None:
        command += ["--host-settings", str(Path(host_settings).absolute())]
    if apply:
        command.append("--apply")
    if verify_mcp:
        command.append("--verify-mcp")
    return command


def launch_shared_image(
    *,
    image: str | None = None,
    host_settings: str | Path | None = None,
    mounted_folder: str | Path | None = None,
    apply: bool = False,
    verify_mcp: bool = False,
    startup_timeout: int | None = None,
    readiness_timeout: int | None = None,
) -> dict:
    root = Path(__file__).resolve().parents[3]
    engine = root / "LAYER_4_ENGINE_STUDIO_C14"
    env = os.environ.copy()
    env.pop("PYTHONHOME", None)
    env.pop("VIRTUAL_ENV", None)
    env.pop("UV_COMPILE_BYTECODE", None)
    env["UV_PROJECT_ENVIRONMENT"] = str(engine / ".venv-prod")
    env["PYTHONPATH"] = str(engine)
    command = _launcher_command(
        root,
        engine,
        image,
        host_settings,
        apply,
        verify_mcp,
        startup_timeout,
        readiness_timeout,
        mounted_folder,
    )
    result = subprocess.run(
        command,
        cwd=root,
        env=env,
        text=True,
        capture_output=True,
        check=False,
        timeout=(startup_timeout or 420) + (readiness_timeout or 900) + 480,
    )
    return _launcher_payload(result)


def _launcher_payload(result: subprocess.CompletedProcess[str]) -> dict:
    try:
        payload = json.loads(result.stdout)
    except (ValueError, TypeError) as error:
        raise RuntimeError(
            f"shared-mcp-launcher-failed: {result.stderr.strip()}"
        ) from error
    if not isinstance(payload, dict):
        raise RuntimeError("shared-mcp-launcher-invalid-result")
    return payload
