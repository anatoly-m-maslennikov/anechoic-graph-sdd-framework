"""Start and admit a Project's Kernel and Orchestrator processes."""

import asyncio
from contextlib import contextmanager
from hashlib import sha256
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
from time import sleep

import httpx2
from pydantic import BaseModel, ConfigDict

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.settings.project.project__shared import (
    console_state_path,
)

from ORCHESTRATOR_beta_C68.jobs import ENGINE
from ORCHESTRATOR_beta_C68.peers._project_peer_configuration import (
    ProjectBinding,
    _PeerHealth,
    _DatabaseHealth,
    _WorkerRun as _WorkerRun,
    _WorkerRuns,
    _database_args,
    _profile_values,
    _open_peer_processes,
    _worker_arguments,
)
from ORCHESTRATOR_beta_C68.peers.warm_worker_process import process_environment, stop_process


ORCHESTRATOR = "ORCHESTRATOR_beta_C68.ORCHESTRATOR_beta_C68__shared"
DATABASE = (
    "KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.DATABASE_SERVER_beta_C71__"
    "shared"
)
_PROFILES = {
    "dev-local": ("memory", "files", "skip"),
    "dev-preprod": ("disk", "duckdb", "load"),
    "test": ("memory", "files", "load"),
    "prod": ("disk", "duckdb", "load"),
}
_PROFILE_KEYS = (
    "ANECHOIC_WORKBENCH_STORAGE",
    "ANECHOIC_JOURNAL_STORAGE",
    "ANECHOIC_ARCHIVES",
)


def socket_path(value):
    path = Path(value)
    parent = path.parent
    info = parent.stat()
    if (
        not path.is_absolute()
        or str(path) != value
        or os.path.lexists(path)
        or parent.resolve(strict=True) != parent
        or parent.is_symlink()
        or not stat.S_ISDIR(info.st_mode)
        or info.st_uid != os.getuid()
        or stat.S_IMODE(info.st_mode) & 0o077
    ):
        raise ValueError("Socket directory is unavailable or unsafe")
    return path


def _resolve_profile(storage, journal_storage):
    return _profile_values(
        storage, journal_storage, os.environ, _PROFILES, _PROFILE_KEYS
    )


def database_path(
    root, storage, manifest_sha256, instance_id, *, local_archives=None
):
    if not isinstance(manifest_sha256, str) or not re.fullmatch(
        r"[0-9a-f]{64}", manifest_sha256
    ):
        raise ValueError("invalid_manifest_digest")
    if storage == "memory":
        return None
    if storage != "disk":
        raise ValueError("invalid_workbench_storage")
    if local_archives not in (None, "load", "skip"):
        raise ValueError("invalid_archive_mode")
    root = Path(root)
    if root.resolve(strict=True) != root:
        raise ValueError("project_declarations_stale")
    directory = root
    for name in (*console_state_path(root).relative_to(root).parts, "beta"):
        directory = directory / name
        directory.mkdir(mode=0o700, exist_ok=True)
        info = directory.lstat()
        if (
            not stat.S_ISDIR(info.st_mode)
            or info.st_uid != os.getuid()
            or directory.resolve(strict=True) != directory
        ):
            raise ValueError("invalid_workbench_storage_path")
    if directory.stat().st_mode & 0o077:
        raise ValueError("invalid_workbench_storage_path")
    identity = sha256(instance_id.encode()).hexdigest()
    suffix = f"-dev-local-{local_archives}" if local_archives else ""
    return (
        directory / f"projection-{identity}-{manifest_sha256}{suffix}.duckdb"
    )


def _wait_for_peer(client, process, instance_id, stop):
    while not stop.is_set() and process.poll() is None:
        try:
            response = client.get("/health", timeout=0.5)
        except httpx2.TransportError:
            sleep(0.05)
            continue
        response.raise_for_status()
        health = _PeerHealth.model_validate(response.json()["result"])
        if health.pid != process.pid or health.instance_id != instance_id:
            raise ValueError("Beta peer reported a different Project binding")
        return
    raise RuntimeError("Beta peer did not start")


@contextmanager
def _peer(module, path, instance_id, stop, *args):
    if stop.is_set():
        raise RuntimeError("Beta peer startup cancelled")
    if os.path.lexists(path):
        raise ValueError("Beta peer socket already exists")
    process = subprocess.Popen(
        [
            sys.executable,
            "-B",
            "-P",
            "-m",
            module,
            "--socket",
            str(path),
            "--instance-id",
            instance_id,
            *args,
        ],
        cwd=ENGINE,
        env=process_environment(),
        stdin=subprocess.DEVNULL,
        stdout=sys.stderr,
        start_new_session=True,
    )
    try:
        with httpx2.Client(
            transport=httpx2.HTTPTransport(uds=str(path)),
            base_url="http://private",
            timeout=125,
            trust_env=False,
        ) as client:
            _wait_for_peer(client, process, instance_id, stop)
            yield process
    finally:
        stop_process(process)
        path.unlink(missing_ok=True)


async def _read_peer(socket, route, **kwargs):
    async with httpx2.AsyncClient(
        transport=httpx2.AsyncHTTPTransport(uds=socket),
        base_url="http://private",
        timeout=2,
        trust_env=False,
    ) as client:
        response = await client.get(route, **kwargs)
        payload = response.json()
        if not isinstance(payload, dict) or set(payload) != {"result"}:
            raise ValueError("Invalid Beta peer response")
        return payload["result"]


class ProjectPeers(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=True)

    database_socket: str
    orchestrator_socket: str
    binding: ProjectBinding
    kernel: subprocess.Popen
    orchestrator: subprocess.Popen

    @property
    def kernel_pid(self):
        return self.kernel.pid

    @property
    def orchestrator_pid(self):
        return self.orchestrator.pid

    @property
    def alive(self):
        return self.kernel.poll() is None and self.orchestrator.poll() is None

    @property
    def worker_binding(self):
        return self.binding.model_dump()

    async def wait_ready(self, instance_id, *, stop=None):
        while self.alive and (stop is None or not stop.is_set()):
            try:
                health = _DatabaseHealth.model_validate(
                    await _read_peer(self.database_socket, "/health")
                )
                runs = _WorkerRuns.model_validate(
                    await _read_peer(
                        self.orchestrator_socket,
                        "/jobs/worker-runs",
                        params={"instance_id": instance_id},
                    )
                )
            except httpx2.TimeoutException:
                await asyncio.sleep(0.1)
                continue
            except httpx2.TransportError as error:
                raise RuntimeError(
                    "Beta peer unavailable during initial admission"
                ) from error
            latest = runs.latest
            if health.ready and latest and latest.state == "succeeded":
                return
            if (
                latest
                and runs.active is None
                and latest.state in ("failed", "aborted")
                and not latest.retrying
            ):
                message = str(
                    latest.message
                    if latest.message is not None
                    else latest.code
                )[:2048]
                raise RuntimeError("Initial Beta build failed: " + message)
            await asyncio.sleep(0.1)
        raise RuntimeError("Kernel did not admit an initial Beta generation")


def _database_launch_args(
    binding,
    storage,
    journal_storage,
    journal_relative,
    result_ttl_seconds,
    instance_id,
    archives,
):
    local_archives = (
        archives
        if os.environ.get("ANECHOIC_RUNTIME_PROFILE") == "dev-local"
        else None
    )
    db_path = database_path(
        binding.root,
        storage,
        binding.manifest_sha256,
        instance_id,
        local_archives=local_archives,
    )
    return _database_args(
        binding, db_path, journal_storage, journal_relative, result_ttl_seconds
    )


@contextmanager
def open_project_peers(
    path,
    instance_id,
    binding,
    stop,
    *,
    watch_code=False,
    storage="disk",
    journal_storage="files",
    journal_relative=None,
    result_ttl_seconds=None,
    warm_worker=None,
):
    """Start and check the selected Project peers, then reap both on exit."""
    binding = ProjectBinding.model_validate(binding)
    storage, journal_storage, archives = _resolve_profile(
        storage, journal_storage
    )
    database, orchestrator, binding_file = (
        path / name for name in ("db.sock", "jobs.sock", "binding.json")
    )
    db_args = _database_launch_args(
        binding,
        storage,
        journal_storage,
        journal_relative,
        result_ttl_seconds,
        instance_id,
        archives,
    )
    watch = ("--watch-code",) if watch_code else ()
    archive_args = ("--skip-archives",) if archives == "skip" else ()
    with _open_peer_processes(
        _peer,
        ProjectPeers,
        (DATABASE, ORCHESTRATOR),
        (database, orchestrator, binding_file),
        instance_id,
        binding,
        stop,
        db_args,
        watch + archive_args + _worker_arguments(warm_worker),
    ) as peers:
        yield peers
