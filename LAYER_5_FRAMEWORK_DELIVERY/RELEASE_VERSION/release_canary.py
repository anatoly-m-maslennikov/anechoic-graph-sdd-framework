"""Verify a candidate image against a disposable copy of the selected Project."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import time
from pathlib import Path
from urllib.request import ProxyHandler, build_opener

from release_support import LocalReleaseError, _copy_tree

_DOCKER = Path(__file__).resolve().parents[2] / "LAYER_3_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/docker"
if str(_DOCKER) not in sys.path:
    sys.path.insert(0, str(_DOCKER))
from project_mcp_backend import ProjectMcpBackend  # noqa: E402

_HTTP = build_opener(ProxyHandler({}))

def verify_candidate_image(root: Path, selection, package: Path, staging: Path, image: str) -> str:
    """Start the immutable image on a Docker-assigned port and verify MCP readiness."""
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", image):
        raise LocalReleaseError("local-release-canary-image-invalid")
    project = staging / "canary-project"
    cidfile = staging / "canary-container-id"
    if "," in str(project):
        raise LocalReleaseError("local-release-canary-path-invalid")
    try:
        project.mkdir()
        _copy_tree(package, project, preserve=frozenset())
        control = project / selection.control_relative
        control.mkdir()
        _copy_tree(root / selection.control_relative, control, preserve=frozenset())
        subprocess.run(["git", "init", "--quiet", str(project)], cwd=root, check=True,
                       capture_output=True, text=True, timeout=30)
        from LAYER_3_ENGINE_STUDIO_C14.MCP_PATCHBAY_C21.FEATURE_MCP.native_startup import select_runtime_project

        copied = select_runtime_project(project, selection.control_relative)
        command = ["docker", "run", "-d", "--pull=never", "--cidfile", str(cidfile), "--init", "--read-only",
                   "--cap-drop", "ALL", "--security-opt", "no-new-privileges:true",
                   "--tmpfs", "/tmp:size=128m,mode=1777", "--pids-limit", "128",
                   "--memory", "1536m", "--cpus", "1", "-p", "127.0.0.1::8092",
                   "--mount", f"type=bind,src={project},dst=/project",
                   "-e", "ANECHOIC_RUNTIME_NAMESPACE=docker",
                   "-e", f"ANECHOIC_CONTROL_ROOT={copied.control_relative.as_posix()}",
                   "-e", f"ANECHOIC_PROJECT_INSTANCE_ID={copied.instance_id}",
                   "-e", f"ANECHOIC_HOST_PROJECT_ROOT={project}", image, "mcp-http"]
        subprocess.run(command, cwd=root, check=True, capture_output=True, text=True, timeout=30)
        container = cidfile.read_text().strip()
        if not re.fullmatch(r"[0-9a-f]{64}", container):
            raise LocalReleaseError("local-release-canary-container-invalid")
        port = subprocess.run(["docker", "port", container, "8092/tcp"], cwd=root, check=True,
                              capture_output=True, text=True, timeout=30).stdout.strip()
        if not re.fullmatch(r"127\.0\.0\.1:([0-9]{1,5})", port) or not 1 <= int(port.rsplit(":", 1)[1]) <= 65535:
            raise LocalReleaseError("local-release-canary-port-invalid")
        base = f"http://{port}"
        deadline = time.monotonic() + 420
        while time.monotonic() < deadline:
            try:
                with _HTTP.open(base + "/anechoic/health", timeout=min(3, deadline - time.monotonic())) as response:
                    if json.load(response).get("ready") is True:
                        break
            except (OSError, ValueError):
                pass
            running = subprocess.run(["docker", "container", "inspect", "--format", "{{.State.Running}}", container],
                                     cwd=root, check=True, capture_output=True, text=True,
                                     timeout=max(0.01, min(30, deadline - time.monotonic()))).stdout.strip()
            if running != "true":
                raise LocalReleaseError("local-release-canary-container-exited")
            time.sleep(min(2, max(0, deadline - time.monotonic())))
        else:
            raise LocalReleaseError("local-release-canary-health-timeout")
        remaining = deadline - time.monotonic()
        if remaining <= 0 or not ProjectMcpBackend(build_if_missing=False).health(base + "/anechoic/mcp", remaining):
            raise LocalReleaseError("local-release-canary-mcp-failed")
        return base + "/anechoic/mcp"
    except subprocess.SubprocessError as error:
        raise LocalReleaseError("local-release-canary-command-failed") from error
    finally:
        failure = sys.exception()
        if cidfile.is_file():
            container = cidfile.read_text().strip()
            if re.fullmatch(r"[0-9a-f]{64}", container):
                try:
                    subprocess.run(["docker", "rm", "-f", container], cwd=root, check=True,
                                   capture_output=True, text=True, timeout=30)
                except (OSError, subprocess.SubprocessError) as error:
                    if failure is None:
                        raise LocalReleaseError("local-release-canary-cleanup-failed") from error
                    failure.add_note(f"Canary container {container} cleanup failed.")
