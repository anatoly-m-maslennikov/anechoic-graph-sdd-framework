"""Validation, project staging, and probes for release canaries."""

import asyncio
from contextlib import contextmanager, suppress
from errno import ENOTEMPTY
from hashlib import file_digest, sha256
import os
from pathlib import Path
import re
import stat
import subprocess
import sys

from .release_image__shared import image_timeout

_RUNTIME_SETTINGS = Path(".anechoic_runtime/anechoic_runtime_settings.toml")
_RUNTIME_SETTINGS_LIMIT = 65536


class CanaryError(Exception):
    pass


def _workspace(root: Path, package: Path, run_id: str) -> Path:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", run_id or ""):
        raise CanaryError("canary-run-id-invalid")
    if not package.is_absolute():
        raise CanaryError("canary-package-invalid")
    staging = package.parent
    owner = root / ".anechoic_tmp" / "simple_local_release"
    if (
        package.name != "package"
        or staging.parent != owner
        or not staging.name.startswith(run_id + "-")
    ):
        raise CanaryError("canary-package-invalid")
    for path in (root, root / ".anechoic_tmp", owner, staging, package):
        mode = path.lstat().st_mode
        if not stat.S_ISDIR(mode) or path.is_symlink():
            raise CanaryError("canary-workspace-unsafe")
    info = staging.stat()
    if info.st_uid != os.getuid() or info.st_mode & 0o077:
        raise CanaryError("canary-workspace-unsafe")
    return staging


def _mcp_ready(
    port: int, timeout: float | None, *, query_enabled: bool = True
) -> bool:
    if timeout is not None and timeout <= 0:
        return False

    async def query() -> bool:
        from httpx2 import AsyncClient
        from mcp.client.session import ClientSession
        from mcp.client.streamable_http import streamable_http_client

        async with AsyncClient(
            trust_env=False, follow_redirects=False, timeout=timeout
        ) as client:
            url = f"http://127.0.0.1:{port}/anechoic/mcp"
            async with streamable_http_client(
                url, http_client=client
            ) as streams:
                async with ClientSession(*streams) as session:
                    await session.initialize()
                    if not query_enabled:
                        await session.send_ping()
                        return True
                    result = await session.call_tool(
                        "query_run",
                        {
                            "sql": (
                                "SELECT 1 AS ready "
                                "FROM framework.atoms LIMIT 1"
                            ),
                            "result_delivery": "inline",
                            "result_format": "json_matrix",
                        },
                    )
                    data = result.structured_content
                    return (
                        not result.is_error
                        and isinstance(data, dict)
                        and data.get("rows") == [[1]]
                    )

    try:
        return asyncio.run(asyncio.wait_for(query(), timeout))
    except Exception:
        return False


@contextmanager
def _candidate_tag(root: Path, attempt: Path, image: str, run_id: str):
    if (
        not isinstance(run_id, str)
        or re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", run_id) is None
    ):
        raise CanaryError("local-release-canary-run-id-invalid")
    token = sha256(str(attempt).encode()).hexdigest()[:16]
    tag = f"anechoic-runtime:candidate-{run_id[:96]}-{token}"
    try:
        subprocess.run(
            ["docker", "image", "tag", image, tag],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
            timeout=image_timeout(30),
        )
    except (OSError, subprocess.SubprocessError) as error:
        raise CanaryError("local-release-canary-image-tag-failed") from error
    try:
        yield
    finally:
        failure = sys.exception()
        try:
            subprocess.run(
                ["docker", "image", "rm", tag],
                cwd=root,
                check=True,
                capture_output=True,
                text=True,
                timeout=image_timeout(30),
            )
        except (OSError, subprocess.SubprocessError) as error:
            if failure is None:
                raise CanaryError(
                    "local-release-canary-image-untag-failed"
                ) from error
            failure.add_note(f"Candidate tag {tag} cleanup failed.")


def _validate_selection_header(value: object) -> None:
    fields = {
        "control_root",
        "manifest_path",
        "manifest_ref",
        "manifest_sha256",
        "project_name",
        "project_prefix",
        "query_enabled",
    }
    if (
        not isinstance(value, dict)
        or set(value) - {"runtime_settings_sha256"} != fields
    ):
        raise CanaryError("local-release-canary-selection-invalid")
    runtime_digest = value.get("runtime_settings_sha256")
    if runtime_digest is not None and (
        not isinstance(runtime_digest, str)
        or re.fullmatch(r"[0-9a-f]{64}", runtime_digest) is None
    ):
        raise CanaryError("local-release-canary-selection-invalid")


def _selection(value: object) -> dict:
    _validate_selection_header(value)
    control, manifest = value["control_root"], value["manifest_path"]
    name, prefix, ref, digest = (
        value[key]
        for key in (
            "project_name",
            "project_prefix",
            "manifest_ref",
            "manifest_sha256",
        )
    )
    if (
        not all(
            isinstance(item, str)
            for item in (control, manifest, name, prefix, ref, digest)
        )
        or not name.strip()
        or re.fullmatch(r"[A-Z]+", prefix) is None
        or re.fullmatch(re.escape(prefix) + r"-S-[0-9]+@[1-9][0-9]*", ref)
        is None
        or re.fullmatch(r"[0-9a-f]{64}", digest) is None
        or type(value["query_enabled"]) is not bool
        or control
        not in {f".anechoic_{name.casefold()}", f"_anechoic_{name.casefold()}"}
        or len(Path(control).parts) != 1
        or Path(control).as_posix() != control
        or Path(manifest).as_posix() != manifest
        or Path(manifest).parent not in {Path("."), Path(control)}
        or not Path(manifest).name.startswith(ref.split("@")[0] + "-")
    ):
        raise CanaryError("local-release-canary-selection-invalid")
    return value


def _verify_manifest(root: Path, selection: dict) -> None:
    manifest = root / selection["manifest_path"]
    if (
        manifest.parent.is_symlink()
        or manifest.is_symlink()
        or not manifest.is_file()
    ):
        raise CanaryError("local-release-canary-manifest-changed")
    with manifest.open("rb") as stream:
        if (
            file_digest(stream, "sha256").hexdigest()
            != selection["manifest_sha256"]
        ):
            raise CanaryError("local-release-canary-manifest-changed")


def _runtime_settings(root: Path) -> bytes | None:
    source = root / _RUNTIME_SETTINGS
    try:
        directory = os.open(
            source.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
        )
        try:
            fd = os.open(
                source.name,
                os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK,
                dir_fd=directory,
            )
        finally:
            os.close(directory)
    except FileNotFoundError:
        return None
    except OSError as error:
        raise CanaryError(
            "local-release-canary-runtime-settings-unsafe"
        ) from error
    with os.fdopen(fd, "rb") as stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise CanaryError("local-release-canary-runtime-settings-unsafe")
        data = stream.read(_RUNTIME_SETTINGS_LIMIT + 1)
    if len(data) > _RUNTIME_SETTINGS_LIMIT:
        raise CanaryError("local-release-canary-runtime-settings-too-large")
    return data


def _remove_late_finder_metadata(function, path, error) -> None:
    if function is not os.rmdir or getattr(error, "errno", None) != ENOTEMPTY:
        raise error
    directory = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        name = ".DS_Store"
        if os.listdir(directory) != [name] or not stat.S_ISREG(
            os.stat(name, dir_fd=directory, follow_symlinks=False).st_mode
        ):
            raise error
        os.unlink(name, dir_fd=directory)
    finally:
        os.close(directory)
    os.rmdir(path)


def _report_canary_logs(root: Path, container: str) -> None:
    with suppress(OSError, subprocess.SubprocessError, ValueError):
        logs = subprocess.run(
            ["docker", "logs", "--tail", "60", container],
            cwd=root,
            check=True,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            timeout=5,
        )
        tail = "\n".join(
            part.rstrip() for part in (logs.stdout, logs.stderr) if part
        )[-8000:].strip()
        if tail:
            print(
                f"Canary container log tail:\n{tail}",
                file=sys.stderr,
                flush=True,
            )
