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

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    console_state_path,
)

from .jobs import ENGINE
from .warm_worker_process import process_environment, stop_process


ORCHESTRATOR = "ORCHESTRATOR_beta_C68.ORCHESTRATOR_beta_C68__shared"
DATABASE = (
    'KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.DATABASE_SERVER_beta_C71__'
    'shared'
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


class ProjectBinding(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    root: str
    control_root: str
    manifest_path: str
    manifest_sha256: str
    project_prefix: str


class _PeerHealth(BaseModel):
    model_config = ConfigDict(strict=True)

    pid: int
    instance_id: str


class _DatabaseHealth(BaseModel):
    model_config = ConfigDict(strict=True)

    ready: bool


class _WorkerRun(BaseModel):
    model_config = ConfigDict(strict=True)

    state: str
    message: str | None = None
    code: str | None = None
    retrying: bool = False


class _WorkerRuns(BaseModel):
    model_config = ConfigDict(strict=True)

    latest: _WorkerRun | None
    active: _WorkerRun | None


def socket_path(value):
    path = Path(value)
    parent = path.parent
    info = parent.stat()
    if (not path.is_absolute() or str(path) != value or os.path.lexists(path)
            or parent.resolve(strict=True) != parent or parent.is_symlink()
            or not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid()
            or stat.S_IMODE(info.st_mode) & 0o077):
        raise ValueError("Socket directory is unavailable or unsafe")
    return path


def _resolve_profile(storage, journal_storage):
    if not any(
        key in os.environ
        for key in ("ANECHOIC_RUNTIME_PROFILE", *_PROFILE_KEYS)
    ):
        return storage, journal_storage, "load"
    profile = os.environ.get("ANECHOIC_RUNTIME_PROFILE", "dev-preprod")
    if profile not in _PROFILES:
        raise ValueError("Invalid ANECHOIC_RUNTIME_PROFILE")
    values = tuple(
        os.environ.get(key, default)
        for key, default in zip(_PROFILE_KEYS, _PROFILES[profile], strict=True)
    )
    choices = (("memory", "disk"), ("files", "duckdb"), ("load", "skip"))
    for key, value, allowed in zip(
        _PROFILE_KEYS, values, choices, strict=True
    ):
        if value not in allowed:
            raise ValueError(f"Invalid {key}")
    workbench, journal, archives = values
    if workbench == "disk" and archives == "skip" and profile != "dev-local":
        raise ValueError(
            (
                'Skipping archives with disk storage requires the dev-local '
                'profile'
            )
        )
    return workbench, journal, archives


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
        [sys.executable, "-B", "-P", "-m", module, "--socket", str(path), "--instance-id", instance_id, *args],
        cwd=ENGINE, env=process_environment(), stdin=subprocess.DEVNULL, stdout=sys.stderr, start_new_session=True,
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


def _database_args(
    binding, db_path, journal_storage, journal_relative, result_ttl_seconds
):
    if journal_storage not in ("files", "duckdb"):
        raise ValueError("Invalid Work Journal storage")
    args = (
        "--project-root",
        binding.root,
        "--journal-storage",
        journal_storage,
    )
    if journal_relative is None:
        journal_relative = binding.control_root + "/_journal"
    if not isinstance(journal_relative, str):
        raise ValueError("paths.journal_root must be a relative path")
    args += ("--journal-relative", journal_relative)
    if result_ttl_seconds is not None:
        if type(result_ttl_seconds) is not int or result_ttl_seconds <= 0:
            raise ValueError(
                "workbench.result_ttl_seconds must be a positive integer"
            )
        args += ("--result-ttl-seconds", str(result_ttl_seconds))
    if db_path is not None:
        args += ("--database-path", str(db_path))
    return args


@contextmanager
def open_project_peers(path, instance_id, binding, stop, *, watch_code=False, storage="disk",
                       journal_storage="files", journal_relative=None, result_ttl_seconds=None, warm_worker=None):
    """Start and check the selected Project peers, then reap both on exit."""
    binding = ProjectBinding.model_validate(binding)
    storage, journal_storage, archives = _resolve_profile(
        storage, journal_storage
    )
    database, orchestrator, binding_file = (
        path / name for name in ("db.sock", "jobs.sock", "binding.json")
    )
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
    db_args = _database_args(
        binding, db_path, journal_storage, journal_relative, result_ttl_seconds
    )
    watch = ("--watch-code",) if watch_code else ()
    archive_args = ("--skip-archives",) if archives == "skip" else ()
    worker_args = ("--worker-socket", warm_worker[0], "--worker-load-seconds", str(warm_worker[1])) if warm_worker else ()
    stream = binding_file.open("x", encoding="utf-8")
    try:
        with stream:
            stream.write(binding.model_dump_json())
        with _peer(DATABASE, database, instance_id, stop, "--manifest-sha256", binding.manifest_sha256, *db_args) as kernel:
            with _peer(ORCHESTRATOR, orchestrator, instance_id, stop, "--binding-file", str(binding_file),
                       "--database-socket", str(database), *watch, *archive_args, *worker_args) as jobs:
                binding_file.unlink()
                yield ProjectPeers(database_socket=str(database), orchestrator_socket=str(orchestrator),
                                   binding=binding, kernel=kernel, orchestrator=jobs)
    finally:
        binding_file.unlink(missing_ok=True)
