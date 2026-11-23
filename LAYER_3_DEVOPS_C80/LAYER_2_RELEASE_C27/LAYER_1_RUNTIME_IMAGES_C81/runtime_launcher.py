"""Call the Engine shared MCP launcher in its production environment."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess


def launch_shared_image(*, image: str, host_settings: str | Path | None = None,
                        apply: bool = False, verify_mcp: bool = False,
                        startup_timeout: int = 420, readiness_timeout: int = 420) -> dict:
    root = Path(__file__).resolve().parents[3]
    engine = root / "LAYER_4_ENGINE_STUDIO_C14"
    env = os.environ.copy()
    env.pop("PYTHONHOME", None)
    env.pop("VIRTUAL_ENV", None)
    env["UV_PROJECT_ENVIRONMENT"] = str(engine / ".venv-prod")
    env["PYTHONPATH"] = str(engine)
    command = ["uv", "run", "--no-compile-bytecode", "--project",
               str(root / "LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine"),
               "--locked", "--python", "3.14", "--managed-python", "--no-env-file",
               "--no-default-groups", "--group", "runtime", "python", "-B", "-P",
               str(engine / "MCP_PATCHBAY_C21/FEATURE_MCP/docker/shared_mcp_launcher.py"),
               "--image", image, "--startup-timeout", str(startup_timeout),
               "--readiness-timeout", str(readiness_timeout)]
    if host_settings is not None:
        command += ["--host-settings", str(Path(host_settings).absolute())]
    if apply:
        command.append("--apply")
    if verify_mcp:
        command.append("--verify-mcp")
    result = subprocess.run(command, cwd=root, env=env, text=True, capture_output=True, check=False, timeout=1320)
    try:
        payload = json.loads(result.stdout)
    except (ValueError, TypeError) as error:
        raise RuntimeError(f"shared-mcp-launcher-failed: {result.stderr.strip()}") from error
    if not isinstance(payload, dict):
        raise RuntimeError("shared-mcp-launcher-invalid-result")
    return payload
