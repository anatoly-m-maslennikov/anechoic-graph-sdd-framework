"""Verify a candidate image against a disposable Project copy."""

from __future__ import annotations

from hashlib import sha256
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

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.header.header__shared \
    import ARCHIVE_DIRECTORY, project_goal_filename  # fmt: skip

from ._release_canary_command import (
    _container_command,
    _initialize_project,
    _inspect_canary,
    _published_port,
)
from ._release_canary_support import (
    CanaryError,
    _candidate_tag,
    _mcp_ready,
    _remove_late_finder_metadata,
    _report_canary_logs,
    _runtime_settings,
    _selection,
    _verify_manifest,
    _workspace,
)
from .release_image__shared import (
    image_timeout,
)

_RUNTIME_SETTINGS = Path(".anechoic_runtime/anechoic_runtime_settings.toml")
_RUNTIME_SETTINGS_LIMIT = 65536


def _copy_tree(
    source: Path, destination: Path, *, skip_archives: bool = False
) -> None:
    if (
        source.is_symlink()
        or not source.is_dir()
        or destination.exists()
        or destination.is_symlink()
    ):
        raise CanaryError("canary-copy-unsafe")

    def fail(error):
        raise error

    for folder, directories, names in os.walk(
        source, followlinks=False, onerror=fail
    ):
        base = Path(folder)
        directories[:] = [
            name for name in directories if not _ignored(name, skip_archives)
        ]
        for name in directories + [
            name for name in names if not _ignored(name)
        ]:
            entry = base / name
            mode = entry.lstat().st_mode
            if not (stat.S_ISDIR(mode) or stat.S_ISREG(mode)):
                raise CanaryError("canary-copy-unsafe")
    shutil.copytree(
        source,
        destination,
        ignore=lambda _, names: [
            n for n in names if _ignored(n, skip_archives)
        ],
    )


def _ignored(name: str, skip_archives: bool = False) -> bool:
    return (
        name == ".DS_Store"
        or name.startswith(".env")
        or name.endswith(".env")
        or (skip_archives and name == ARCHIVE_DIRECTORY)
    )


_HTTP = build_opener(ProxyHandler({}))


def _copy_runtime_settings(root: Path, project: Path, selection: dict) -> None:
    data = _runtime_settings(root)
    observed = sha256(data).hexdigest() if data is not None else None
    if (
        "runtime_settings_sha256" in selection
        and observed != selection["runtime_settings_sha256"]
    ):
        raise CanaryError("local-release-canary-runtime-settings-changed")
    destination = project / _RUNTIME_SETTINGS
    if (
        destination.parent.is_symlink()
        or destination.exists()
        or destination.is_symlink()
    ):
        raise CanaryError("local-release-canary-runtime-settings-unsafe")
    if data is not None:
        destination.parent.mkdir(exist_ok=True)
        with destination.open("xb") as stream:
            stream.write(data)


def verify_candidate_image(
    root: Path,
    package: Path,
    image: str,
    *,
    run_id: str,
    selection: dict,
    skip_archives=False,
) -> str:
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
            return _verify_candidate_image(
                root,
                selection,
                package,
                attempt,
                image,
                skip_archives=skip_archives,
            )
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


def _verify_candidate_image(
    root: Path,
    selection,
    package: Path,
    attempt: Path,
    image: str,
    *,
    skip_archives=False,
) -> str:
    project = attempt / "canary-project"
    cidfile = attempt / "canary-container-id"
    if "," in str(project):
        raise CanaryError("local-release-canary-path-invalid")
    try:
        _start_canary_container(
            root,
            selection,
            package,
            project,
            cidfile,
            image,
            skip_archives=skip_archives,
        )
        container = cidfile.read_text().strip()
        if not re.fullmatch(r"[0-9a-f]{64}", container):
            raise CanaryError("local-release-canary-container-invalid")
        port = _published_port(root, container, image_timeout(30))
        return _await_canary(
            root,
            container,
            port,
            query_enabled=selection["query_enabled"],
        )
    except subprocess.SubprocessError as error:
        raise CanaryError("local-release-canary-command-failed") from error
    finally:
        _remove_canary_container(root, cidfile, failure=sys.exception())


def _start_canary_container(
    root: Path,
    selection: dict,
    package: Path,
    project: Path,
    cidfile: Path,
    image: str,
    *,
    skip_archives=False,
) -> None:
    _copy_tree(package, project)
    control = project / selection["control_root"]
    _copy_tree(
        root / selection["control_root"], control, skip_archives=skip_archives
    )
    manifest = root / selection["manifest_path"]
    root_atoms = [manifest] if manifest.parent == root else []
    root_atoms.extend(
        path for path in root.iterdir() if project_goal_filename(path.name)
    )
    for source in root_atoms:
        destination = project / source.name
        if (
            source.is_symlink()
            or not source.is_file()
            or destination.exists()
            or destination.is_symlink()
        ):
            raise CanaryError("canary-copy-unsafe")
        shutil.copyfile(source, destination)
    _copy_runtime_settings(root, project, selection)
    _verify_manifest(project, selection)
    _initialize_project(root, project, image_timeout(30))
    command = _container_command(project, cidfile, image, selection)
    subprocess.run(
        command,
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
        timeout=image_timeout(30),
    )


def _await_canary(
    root: Path, container: str, port: int, *, query_enabled: bool
) -> str:
    base = f"http://127.0.0.1:{port}"
    startup_timeout = image_timeout(420)
    deadline = (
        float("inf")
        if startup_timeout is None
        else time.monotonic() + startup_timeout
    )
    while time.monotonic() < deadline:
        try:
            with _HTTP.open(
                base + "/anechoic/health",
                timeout=min(3, deadline - time.monotonic()),
            ) as response:
                if (state := json.load(response).get("state")) == "ready":
                    break
                if state == "degraded":
                    raise CanaryError("local-release-canary-health-degraded")
        except OSError, ValueError:
            pass
        inspect_timeout = (
            None
            if startup_timeout is None
            else max(0.01, min(30, deadline - time.monotonic()))
        )
        running = _inspect_canary(root, container, inspect_timeout)
        if running != "true":
            raise CanaryError("local-release-canary-container-exited")
        time.sleep(min(2, max(0, deadline - time.monotonic())))
    else:
        raise CanaryError("local-release-canary-health-timeout")
    query_timeout = (
        None if startup_timeout is None else deadline - time.monotonic()
    )
    if not _mcp_ready(port, query_timeout, query_enabled=query_enabled):
        raise CanaryError("local-release-canary-mcp-failed")
    return base + "/anechoic/mcp"


def _remove_canary_container(
    root: Path, cidfile: Path, *, failure: BaseException | None
) -> None:
    if cidfile.is_file():
        container = cidfile.read_text().strip()
        if re.fullmatch(r"[0-9a-f]{64}", container):
            if isinstance(failure, CanaryError):
                _report_canary_logs(root, container)
            try:
                subprocess.run(
                    ["docker", "rm", "-f", "-v", container],
                    cwd=root,
                    check=True,
                    capture_output=True,
                    text=True,
                    timeout=image_timeout(30),
                )
            except (OSError, subprocess.SubprocessError) as error:
                if failure is None:
                    raise CanaryError(
                        "local-release-canary-cleanup-failed"
                    ) from error
                failure.add_note(
                    f"Canary container {container} cleanup failed."
                )
