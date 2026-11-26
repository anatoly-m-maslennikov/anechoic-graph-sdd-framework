"""Verify a candidate image against a disposable copy of the selected Project."""

from __future__ import annotations

import asyncio
from contextlib import contextmanager, suppress
from errno import ENOTEMPTY
from hashlib import file_digest, sha256
import json
import os
import shutil
import stat
import re
import subprocess
import sys
from tempfile import mkdtemp
import time
from pathlib import Path
from urllib.request import ProxyHandler, build_opener

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import project_goal_filename

from .full_suite_docker import IMAGE_DEADLINES, image_deadline_mode, image_timeout

_RUNTIME_SETTINGS = Path(".anechoic_runtime/anechoic_runtime_settings.toml")
_RUNTIME_SETTINGS_LIMIT = 65536

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


def _mcp_ready(port: int, timeout: float | None, *, query_enabled: bool = True) -> bool:
    if timeout is not None and timeout <= 0:
        return False

    async def query() -> bool:
        from httpx2 import AsyncClient
        from mcp.client.session import ClientSession
        from mcp.client.streamable_http import streamable_http_client

        async with AsyncClient(trust_env=False, follow_redirects=False, timeout=timeout) as client:
            url = f"http://127.0.0.1:{port}/anechoic/mcp"
            async with streamable_http_client(url, http_client=client) as streams:
                async with ClientSession(*streams) as session:
                    await session.initialize()
                    if not query_enabled:
                        await session.send_ping()
                        return True
                    result = await session.call_tool("query_run", {
                        "sql": "SELECT 1 AS ready FROM framework.atoms LIMIT 1",
                        "result_delivery": "inline",
                        "result_format": "json_matrix",
                    })
                    data = result.structured_content
                    return not result.is_error and isinstance(data, dict) and data.get("rows") == [[1]]

    try:
        return asyncio.run(asyncio.wait_for(query(), timeout))
    except Exception:
        return False


@contextmanager
def _candidate_tag(root: Path, attempt: Path, image: str, run_id: str):
    if not isinstance(run_id, str) or re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", run_id) is None:
        raise CanaryError("local-release-canary-run-id-invalid")
    token = sha256(str(attempt).encode()).hexdigest()[:16]
    tag = f"anechoic-runtime:candidate-{run_id[:96]}-{token}"
    try:
        subprocess.run(["docker", "image", "tag", image, tag], cwd=root, check=True,
                       capture_output=True, text=True, timeout=image_timeout(30))
    except (OSError, subprocess.SubprocessError) as error:
        raise CanaryError("local-release-canary-image-tag-failed") from error
    try:
        yield
    finally:
        failure = sys.exception()
        try:
            subprocess.run(["docker", "image", "rm", tag], cwd=root, check=True,
                           capture_output=True, text=True, timeout=image_timeout(30))
        except (OSError, subprocess.SubprocessError) as error:
            if failure is None:
                raise CanaryError("local-release-canary-image-untag-failed") from error
            failure.add_note(f"Candidate tag {tag} cleanup failed.")


def _selection(value: object) -> dict:
    fields = {"control_root", "manifest_path", "manifest_ref", "manifest_sha256",
              "project_name", "project_prefix", "query_enabled"}
    if not isinstance(value, dict) or set(value) - {"runtime_settings_sha256"} != fields:
        raise CanaryError("local-release-canary-selection-invalid")
    runtime_digest = value.get("runtime_settings_sha256")
    if runtime_digest is not None and (
        not isinstance(runtime_digest, str) or re.fullmatch(r"[0-9a-f]{64}", runtime_digest) is None
    ):
        raise CanaryError("local-release-canary-selection-invalid")
    control, manifest = value["control_root"], value["manifest_path"]
    name, prefix, ref, digest = (value[key] for key in
                                 ("project_name", "project_prefix", "manifest_ref", "manifest_sha256"))
    if (not all(isinstance(item, str) for item in (control, manifest, name, prefix, ref, digest))
            or not name.strip() or re.fullmatch(r"[A-Z]+", prefix) is None
            or re.fullmatch(re.escape(prefix) + r"-S-[0-9]+@[1-9][0-9]*", ref) is None
            or re.fullmatch(r"[0-9a-f]{64}", digest) is None
            or type(value["query_enabled"]) is not bool
            or control not in {f".anechoic_{name.casefold()}", f"_anechoic_{name.casefold()}"}
            or len(Path(control).parts) != 1 or Path(control).as_posix() != control
            or Path(manifest).as_posix() != manifest
            or Path(manifest).parent not in {Path("."), Path(control)}
            or not Path(manifest).name.startswith(ref.split("@")[0] + "-")):
        raise CanaryError("local-release-canary-selection-invalid")
    return value


def _verify_manifest(root: Path, selection: dict) -> None:
    manifest = root / selection["manifest_path"]
    if manifest.parent.is_symlink() or manifest.is_symlink() or not manifest.is_file():
        raise CanaryError("local-release-canary-manifest-changed")
    with manifest.open("rb") as stream:
        if file_digest(stream, "sha256").hexdigest() != selection["manifest_sha256"]:
            raise CanaryError("local-release-canary-manifest-changed")


def _runtime_settings(root: Path) -> bytes | None:
    source = root / _RUNTIME_SETTINGS
    try:
        directory = os.open(source.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            fd = os.open(source.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory)
        finally:
            os.close(directory)
    except FileNotFoundError:
        return None
    except OSError as error:
        raise CanaryError("local-release-canary-runtime-settings-unsafe") from error
    with os.fdopen(fd, "rb") as stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise CanaryError("local-release-canary-runtime-settings-unsafe")
        data = stream.read(_RUNTIME_SETTINGS_LIMIT + 1)
    if len(data) > _RUNTIME_SETTINGS_LIMIT:
        raise CanaryError("local-release-canary-runtime-settings-too-large")
    return data


def _copy_runtime_settings(root: Path, project: Path, selection: dict) -> None:
    data = _runtime_settings(root)
    observed = sha256(data).hexdigest() if data is not None else None
    if "runtime_settings_sha256" in selection and observed != selection["runtime_settings_sha256"]:
        raise CanaryError("local-release-canary-runtime-settings-changed")
    destination = project / _RUNTIME_SETTINGS
    if destination.parent.is_symlink() or destination.exists() or destination.is_symlink():
        raise CanaryError("local-release-canary-runtime-settings-unsafe")
    if data is not None:
        destination.parent.mkdir(exist_ok=True)
        with destination.open("xb") as stream:
            stream.write(data)


def _remove_late_finder_metadata(function, path, error) -> None:
    if function is not os.rmdir or getattr(error, "errno", None) != ENOTEMPTY:
        raise error
    directory = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        name = ".DS_Store"
        if os.listdir(directory) != [name] or not stat.S_ISREG(os.stat(name, dir_fd=directory, follow_symlinks=False).st_mode):
            raise error
        os.unlink(name, dir_fd=directory)
    finally:
        os.close(directory)
    os.rmdir(path)


def verify_candidate_image(root: Path, package: Path, image: str, *, run_id: str, selection: dict) -> str:
    """Start the immutable image and verify that MCP serves a real query."""
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", image):
        raise CanaryError("local-release-canary-image-invalid")
    staging = _workspace(root, package, run_id)
    selection = _selection(selection)
    _verify_manifest(root, selection)
    attempt = Path(mkdtemp(prefix="canary-attempt-", dir=staging))
    failure = None
    try:
        with _candidate_tag(root, attempt, image, run_id):
            return _verify_candidate_image(root, selection, package, attempt, image)
    except BaseException as error:
        failure = error
        raise
    finally:
        try:
            shutil.rmtree(attempt, onexc=_remove_late_finder_metadata)
        except Exception as error:
            if failure is None:
                raise
            failure.add_note(f"Canary attempt cleanup failed: {error}")


def _verify_candidate_image(root: Path, selection, package: Path, attempt: Path, image: str) -> str:
    project = attempt / "canary-project"
    cidfile = attempt / "canary-container-id"
    if "," in str(project):
        raise CanaryError("local-release-canary-path-invalid")
    try:
        _start_canary_container(root, selection, package, project, cidfile, image)
        container = cidfile.read_text().strip()
        if not re.fullmatch(r"[0-9a-f]{64}", container):
            raise CanaryError("local-release-canary-container-invalid")
        publisher = subprocess.run(["docker", "port", container, "8092/tcp"], cwd=root, check=True,
                                   capture_output=True, text=True, timeout=image_timeout(30)).stdout.strip()
        binding = re.fullmatch(r"127\.0\.0\.1:([1-9][0-9]{0,4})", publisher)
        if binding is None or int(binding[1]) > 65535:
            raise CanaryError("local-release-canary-port-invalid")
        return _await_canary(root, container, int(binding[1]), query_enabled=selection["query_enabled"])
    except subprocess.SubprocessError as error:
        raise CanaryError("local-release-canary-command-failed") from error
    finally:
        _remove_canary_container(root, cidfile, failure=sys.exception())


def _start_canary_container(
    root: Path, selection: dict, package: Path, project: Path, cidfile: Path, image: str,
) -> None:
    _copy_tree(package, project)
    control = project / selection["control_root"]
    _copy_tree(root / selection["control_root"], control)
    manifest = root / selection["manifest_path"]
    root_atoms = [manifest] if manifest.parent == root else []
    root_atoms.extend(path for path in root.iterdir() if project_goal_filename(path.name))
    for source in root_atoms:
        destination = project / source.name
        if source.is_symlink() or not source.is_file() or destination.exists() or destination.is_symlink():
            raise CanaryError("canary-copy-unsafe")
        shutil.copyfile(source, destination)
    _copy_runtime_settings(root, project, selection)
    _verify_manifest(project, selection)
    subprocess.run(["git", "init", "--quiet", str(project)], cwd=root, check=True,
                   capture_output=True, text=True, timeout=image_timeout(30))
    instance_id = sha256(f"{project.resolve(strict=True)}\0{selection['control_root']}".encode("utf-8")).hexdigest()
    command = ["docker", "run", "-d", "--pull=never", "--cidfile", str(cidfile), "--init", "--read-only",
               "--cap-drop", "ALL", "--security-opt", "no-new-privileges:true",
               "--tmpfs", "/tmp:size=128m,mode=1777", "--pids-limit", "128",
               "--memory", "1536m", "--cpus", "1", "-p", "127.0.0.1::8092",
               "--mount", f"type=bind,src={project},dst=/project",
               "--mount", "type=volume,dst=/var/lib/anechoic",
               "-e", "ANECHOIC_FRAMEWORK_DB_ROOT=/var/lib/anechoic",
               "-e", "ANECHOIC_RUNTIME_NAMESPACE=docker",
               "-e", f"{IMAGE_DEADLINES}={image_deadline_mode(os.environ)}",
               "-e", f"ANECHOIC_CONTROL_ROOT={selection['control_root']}",
               "-e", f"ANECHOIC_PROJECT_INSTANCE_ID={instance_id}",
               "-e", f"ANECHOIC_HOST_PROJECT_ROOT={project}", image, "mcp-http"]
    subprocess.run(command, cwd=root, check=True, capture_output=True, text=True, timeout=image_timeout(30))

def _await_canary(root: Path, container: str, port: int, *, query_enabled: bool) -> str:
    base = f"http://127.0.0.1:{port}"
    startup_timeout = image_timeout(420)
    deadline = float("inf") if startup_timeout is None else time.monotonic() + startup_timeout
    while time.monotonic() < deadline:
        try:
            with _HTTP.open(base + "/anechoic/health", timeout=min(3, deadline - time.monotonic())) as response:
                if (state := json.load(response).get("state")) == "ready":
                    break
                if state == "degraded":
                    raise CanaryError("local-release-canary-health-degraded")
        except (OSError, ValueError):
            pass
        inspect_timeout = None if startup_timeout is None else max(0.01, min(30, deadline - time.monotonic()))
        running = subprocess.run(["docker", "container", "inspect", "--format", "{{.State.Running}}", container],
                                 cwd=root, check=True, capture_output=True, text=True, timeout=inspect_timeout).stdout.strip()
        if running != "true":
            raise CanaryError("local-release-canary-container-exited")
        time.sleep(min(2, max(0, deadline - time.monotonic())))
    else:
        raise CanaryError("local-release-canary-health-timeout")
    query_timeout = None if startup_timeout is None else deadline - time.monotonic()
    if not _mcp_ready(port, query_timeout, query_enabled=query_enabled):
        raise CanaryError("local-release-canary-mcp-failed")
    return base + "/anechoic/mcp"

def _remove_canary_container(root: Path, cidfile: Path, *, failure: BaseException | None) -> None:
    if cidfile.is_file():
        container = cidfile.read_text().strip()
        if re.fullmatch(r"[0-9a-f]{64}", container):
            if isinstance(failure, CanaryError):
                _report_canary_logs(root, container)
            try:
                subprocess.run(["docker", "rm", "-f", "-v", container], cwd=root, check=True,
                               capture_output=True, text=True, timeout=image_timeout(30))
            except (OSError, subprocess.SubprocessError) as error:
                if failure is None:
                    raise CanaryError("local-release-canary-cleanup-failed") from error
                failure.add_note(f"Canary container {container} cleanup failed.")


def _report_canary_logs(root: Path, container: str) -> None:
    with suppress(OSError, subprocess.SubprocessError, ValueError):
        logs = subprocess.run(["docker", "logs", "--tail", "60", container], cwd=root, check=True,
                              capture_output=True, encoding="utf-8", errors="replace", timeout=5)
        tail = "\n".join(part.rstrip() for part in (logs.stdout, logs.stderr) if part)[-8000:].strip()
        if tail:
            print(f"Canary container log tail:\n{tail}", file=sys.stderr, flush=True)
