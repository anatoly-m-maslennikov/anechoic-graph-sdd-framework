"""Project peer binding models and startup configuration."""

from contextlib import contextmanager

from pydantic import BaseModel, ConfigDict


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


def _profile_values(storage, journal_storage, env, _PROFILES, _PROFILE_KEYS):
    if not any(
        key in env for key in ("ANECHOIC_RUNTIME_PROFILE", *_PROFILE_KEYS)
    ):
        return storage, journal_storage, "load"
    profile = env.get("ANECHOIC_RUNTIME_PROFILE", "dev-preprod")
    if profile not in _PROFILES:
        raise ValueError("Invalid ANECHOIC_RUNTIME_PROFILE")
    values = tuple(
        env.get(key, default)
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
                "Skipping archives with disk storage requires the dev-local "
                "profile"
            )
        )
    return workbench, journal, archives


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


def _worker_arguments(warm_worker):
    return (
        (
            "--worker-socket",
            warm_worker[0],
            "--worker-load-seconds",
            str(warm_worker[1]),
        )
        if warm_worker
        else ()
    )


def _peer_result(peers_type, database, orchestrator, binding, kernel, jobs):
    return peers_type(
        database_socket=str(database),
        orchestrator_socket=str(orchestrator),
        binding=binding,
        kernel=kernel,
        orchestrator=jobs,
    )


@contextmanager
def _open_peer_processes(
    peer,
    peers_type,
    modules,
    paths,
    instance_id,
    binding,
    stop,
    db_args,
    job_args,
):
    database_module, orchestrator_module = modules
    database, orchestrator, binding_file = paths
    stream = binding_file.open("x", encoding="utf-8")
    try:
        with stream:
            stream.write(binding.model_dump_json())
        with peer(
            database_module,
            database,
            instance_id,
            stop,
            "--manifest-sha256",
            binding.manifest_sha256,
            *db_args,
        ) as kernel:
            with peer(
                orchestrator_module,
                orchestrator,
                instance_id,
                stop,
                "--binding-file",
                str(binding_file),
                "--database-socket",
                str(database),
                *job_args,
            ) as jobs:
                binding_file.unlink()
                yield _peer_result(
                    peers_type, database, orchestrator, binding, kernel, jobs
                )
    finally:
        binding_file.unlink(missing_ok=True)
