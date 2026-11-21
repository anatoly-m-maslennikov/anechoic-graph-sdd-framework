"""Verify a candidate image against a disposable copy of the selected Project."""

from __future__ import annotations

import asyncio
from contextlib import contextmanager
from hashlib import sha256
import json
import os
import shutil
import stat
import re
import subprocess
import sys
import time
from pathlib import Path
from urllib.request import ProxyHandler, build_opener

class CanaryError(Exception):
    pass


def _copy_tree(source: Path, destination: Path) -> None:
    if source.is_symlink() or not source.is_dir() or destination.exists() or destination.is_symlink():
        raise CanaryError("canary-copy-unsafe")

    def fail(error):
        raise error

    for folder, directories, names in os.walk(source, followlinks=False, onerror=fail):
        base = Path(folder)
        directories[:] = [name for name in directories if not _ignored(name)]
        for name in directories + [name for name in names if not _ignored(name)]:
            entry = base / name
            mode = entry.lstat().st_mode
            if not (stat.S_ISDIR(mode) or stat.S_ISREG(mode)):
                raise CanaryError("canary-copy-unsafe")
    shutil.copytree(source, destination, ignore=lambda _, names: [n for n in names if _ignored(n)])


def _ignored(name: str) -> bool:
    return name == ".DS_Store" or name.startswith(".env") or name.endswith(".env")


def _workspace(root: Path, package: Path, run_id: str) -> Path:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", run_id or ""):
        raise CanaryError("canary-run-id-invalid")
    if not package.is_absolute():
        raise CanaryError("canary-package-invalid")
    staging = package.parent
    owner = root / ".anechoic_tmp" / "simple_local_release"
    if package.name != "package" or staging.parent != owner or not staging.name.startswith(run_id + "-"):
        raise CanaryError("canary-package-invalid")
    for path in (root, root / ".anechoic_tmp", owner, staging, package):
        mode = path.lstat().st_mode
        if not stat.S_ISDIR(mode) or path.is_symlink():
            raise CanaryError("canary-workspace-unsafe")
    info = staging.stat()
    if info.st_uid != os.getuid() or info.st_mode & 0o077:
        raise CanaryError("canary-workspace-unsafe")
    return staging

_HTTP = build_opener(ProxyHandler({}))


def _mcp_ready(port: int, timeout: float) -> bool:
    if timeout <= 0:
        return False

    async def initialize() -> None:
        from httpx2 import AsyncClient
        from mcp.client.session import ClientSession
        from mcp.client.streamable_http import streamable_http_client

        async with AsyncClient(trust_env=False, follow_redirects=False, timeout=timeout) as client:
            url = f"http://127.0.0.1:{port}/anechoic/mcp"
            async with streamable_http_client(url, http_client=client) as streams:
                async with ClientSession(*streams) as session:
                    await session.initialize()

    try:
        asyncio.run(asyncio.wait_for(initialize(), timeout))
    except Exception:
        return False
    return True


@contextmanager
def _candidate_tag(root: Path, staging: Path, image: str, run_id: str):
    if not isinstance(run_id, str) or re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", run_id) is None:
        raise CanaryError("local-release-canary-run-id-invalid")
    attempt = sha256(str(staging).encode()).hexdigest()[:16]
    tag = f"anechoic-runtime:candidate-{run_id[:96]}-{attempt}"
    try:
        subprocess.run(["docker", "image", "tag", image, tag], cwd=root, check=True,
                       capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError) as error:
        raise CanaryError("local-release-canary-image-tag-failed") from error
    try:
        yield
    finally:
        failure = sys.exception()
        try:
            subprocess.run(["docker", "image", "rm", tag], cwd=root, check=True,
                           capture_output=True, text=True, timeout=30)
        except (OSError, subprocess.SubprocessError) as error:
            if failure is None:
                raise CanaryError("local-release-canary-image-untag-failed") from error
            failure.add_note(f"Candidate tag {tag} cleanup failed.")


def verify_candidate_image(root: Path, package: Path, image: str, *, run_id: str) -> str:
    """Start the immutable image on a Docker-assigned port and verify MCP readiness."""
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", image):
        raise CanaryError("local-release-canary-image-invalid")
    staging = _workspace(root, package, run_id)
    source = Path(__file__).resolve().parents[3]
    engine = source / "LAYER_3_ENGINE_STUDIO_C14"
    sys.path[:0] = [
        str(source), str(engine / "FEATURE_PROGRAMMATIC"),
        str(engine / "FEATURE_PROGRAMMATIC/FEATURE_TOOLS"), str(engine / "IWE_CONSOLE_C43"),
    ]
    from LAYER_3_ENGINE_STUDIO_C14.MCP_PATCHBAY_C21.FEATURE_MCP.native_startup import select_runtime_project
    selection = select_runtime_project(root)
    with _candidate_tag(root, staging, image, run_id):
        return _verify_candidate_image(root, selection, package, staging, image)


def _verify_candidate_image(root: Path, selection, package: Path, staging: Path, image: str) -> str:
    project = staging / "canary-project"
    cidfile = staging / "canary-container-id"
    if "," in str(project):
        raise CanaryError("local-release-canary-path-invalid")
    try:
        _copy_tree(package, project)
        control = project / selection.control_relative
        _copy_tree(root / selection.control_relative, control)
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
            raise CanaryError("local-release-canary-container-invalid")
        publisher = subprocess.run(["docker", "port", container, "8092/tcp"], cwd=root, check=True,
                                   capture_output=True, text=True, timeout=30).stdout.strip()
        binding = re.fullmatch(r"127\.0\.0\.1:([1-9][0-9]{0,4})", publisher)
        if binding is None or int(binding[1]) > 65535:
            raise CanaryError("local-release-canary-port-invalid")
        port = int(binding[1])
        base = f"http://127.0.0.1:{port}"
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
                raise CanaryError("local-release-canary-container-exited")
            time.sleep(min(2, max(0, deadline - time.monotonic())))
        else:
            raise CanaryError("local-release-canary-health-timeout")
        if not _mcp_ready(port, deadline - time.monotonic()):
            raise CanaryError("local-release-canary-mcp-failed")
        return base + "/anechoic/mcp"
    except subprocess.SubprocessError as error:
        raise CanaryError("local-release-canary-command-failed") from error
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
                        raise CanaryError("local-release-canary-cleanup-failed") from error
                    failure.add_note(f"Canary container {container} cleanup failed.")
