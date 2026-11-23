"""Start the single-Project Beta Backend with independent Kernel and Orchestrator peers."""

import argparse
import asyncio
from contextlib import contextmanager, suppress
from dataclasses import dataclass
from hashlib import sha256
import json
import os
import re
from pathlib import Path
import signal
import stat
import subprocess
import sys
from threading import Event, Thread
from time import sleep

import httpx2

from .WORKBENCH_BACKEND_beta_C70__shared import create_app, serve, socket_path
from .peer_transport import upstream
from .warm_worker import ENGINE, _stop, open_warm_worker

ORCHESTRATOR = "ORCHESTRATOR_beta_C68.ORCHESTRATOR_beta_C68__shared"
DATABASE = "KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.DATABASE_SERVER_beta_C71__shared"


def _wait_for_peer(client, peer, instance_id, stop):
    while not stop.is_set() and peer.poll() is None:
        try:
            response = client.get("/health", timeout=0.5)
        except httpx2.TransportError:
            sleep(0.05)
            continue
        response.raise_for_status()
        result = response.json()["result"]
        if result.get("pid") != peer.pid or result.get("instance_id") != instance_id:
            raise ValueError("Beta peer reported a different Project binding")
        return
    raise RuntimeError("Beta peer did not start")


@contextmanager
def _peer(module, path, instance_id, stop, *args):
    if stop.is_set():
        raise RuntimeError("Beta peer startup cancelled")
    if os.path.lexists(path):
        raise ValueError("Beta peer socket already exists")
    environment = {key: value for key, value in os.environ.items() if key != "PYTHONHOME"}
    environment["PYTHONPATH"] = str(ENGINE)
    peer = subprocess.Popen(
        [sys.executable, "-B", "-P", "-m", module, "--socket", str(path), "--instance-id", instance_id, *args],
        cwd=ENGINE, env=environment, stdin=subprocess.DEVNULL, stdout=sys.stderr, start_new_session=True,
    )
    try:
        with httpx2.Client(transport=httpx2.HTTPTransport(uds=str(path)),
                           base_url="http://private", timeout=125, trust_env=False) as client:
            _wait_for_peer(client, peer, instance_id, stop)
        yield peer
    finally:
        _stop(peer)
        # The peer may die before it can remove its socket.
        path.unlink(missing_ok=True)


@dataclass(frozen=True)
class ProjectPeers:
    database_socket: str
    orchestrator_socket: str
    worker_binding: dict
    _kernel: subprocess.Popen
    _orchestrator: subprocess.Popen

    @property
    def kernel_pid(self):
        return self._kernel.pid

    @property
    def orchestrator_pid(self):
        return self._orchestrator.pid

    @property
    def alive(self):
        return self._kernel.poll() is None and self._orchestrator.poll() is None

    async def wait_ready(self, instance_id, *, stop=None):
        while self.alive and (stop is None or not stop.is_set()):
            try:
                health = await upstream(self.database_socket, "GET", "/health", timeout=2)
                runs = await upstream(self.orchestrator_socket, "GET", "/jobs/worker-runs", timeout=2,
                                      params={"instance_id": instance_id})
            except httpx2.TimeoutException:
                await asyncio.sleep(0.1)
                continue
            except httpx2.TransportError as error:
                raise RuntimeError("Beta peer unavailable during initial admission") from error
            state = runs["result"]
            latest = state["latest"]
            if health["result"]["ready"] and latest and latest["state"] == "succeeded":
                return
            if latest and state.get("active") is None and latest["state"] in ("failed", "aborted"):
                message = str(latest.get("message", latest.get("code")))[:2048]
                raise RuntimeError("Initial Beta build failed: " + message)
            await asyncio.sleep(0.1)
        raise RuntimeError("Kernel did not admit an initial Beta generation")


def database_path(root, storage, manifest_sha256, instance_id):
    """Return a private Beta database location, or use an in-memory database."""
    if not isinstance(manifest_sha256, str) or not re.fullmatch(r"[0-9a-f]{64}", manifest_sha256):
        raise ValueError("invalid_manifest_digest")
    if storage == "memory":
        return None
    if storage != "disk":
        raise ValueError("invalid_workbench_storage")
    root = Path(root)
    if root.resolve(strict=True) != root:
        raise ValueError("project_declarations_stale")
    directory = root
    for name in (".anechoic_runtime", "workbench", "beta"):
        directory = directory / name
        directory.mkdir(mode=0o700, exist_ok=True)
        info = directory.lstat()
        if (not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid()
                or directory.resolve(strict=True) != directory):
            raise ValueError("invalid_workbench_storage_path")
    if directory.stat().st_mode & 0o077:
        raise ValueError("invalid_workbench_storage_path")
    identity = sha256(instance_id.encode()).hexdigest()
    return directory / f"projection-{identity}-{manifest_sha256}.duckdb"


@contextmanager
def open_project_peers(path, instance_id, binding, stop, *, watch_code=False, storage="disk",
                       journal_storage="files", journal_relative=None, result_ttl_seconds=None,
                       warm_worker=None):
    """Start and validate a Project's peers; stop both when the context exits."""
    database, orchestrator, binding_file = (path / name for name in (
        "db.sock", "jobs.sock", "binding.json"))
    db_path = database_path(binding["root"], storage, binding["manifest_sha256"], instance_id)
    if journal_storage not in ("files", "duckdb"):
        raise ValueError("Invalid Work Journal storage")
    db_args = ("--project-root", binding["root"], "--journal-storage", journal_storage)
    journal_relative = journal_relative if journal_relative is not None else binding["control_root"] + "/_journal"
    if not isinstance(journal_relative, str):
        raise ValueError("paths.journal_root must be a relative path")
    db_args += ("--journal-relative", journal_relative)
    if result_ttl_seconds is not None:
        if type(result_ttl_seconds) is not int or result_ttl_seconds <= 0:
            raise ValueError("workbench.result_ttl_seconds must be a positive integer")
        db_args += ("--result-ttl-seconds", str(result_ttl_seconds))
    if db_path is not None:
        db_args += ("--database-path", str(db_path))
    watch = ("--watch-code",) if watch_code else ()
    worker_args = ("--worker-socket", warm_worker[0], "--worker-load-seconds", str(warm_worker[1])) if warm_worker else ()
    with binding_file.open("x", encoding="utf-8") as stream:
        json.dump(binding, stream)
    try:
        with _peer(DATABASE, database, instance_id, stop, "--manifest-sha256", binding["manifest_sha256"], *db_args) as kernel:
            with _peer(ORCHESTRATOR, orchestrator, instance_id, stop, "--binding-file", str(binding_file),
                       "--database-socket", str(database), *watch, *worker_args) as jobs:
                binding_file.unlink()
                yield ProjectPeers(str(database), str(orchestrator), binding, kernel, jobs)
    finally:
        binding_file.unlink(missing_ok=True)


def _open_bound_peers(path, args, binding, stop, warm_worker):
    return open_project_peers(path.parent, args.instance_id, binding, stop, watch_code=args.watch_code,
                              storage=args.workbench_storage, journal_storage=args.journal_storage,
                              journal_relative=args.journal_relative, result_ttl_seconds=args.result_ttl_seconds,
                              warm_worker=warm_worker)


def _serve_api(path, args, binding, database, orchestrator):
    app = create_app(args.instance_id, args.manifest_sha256, args.project_root, database, orchestrator,
                     host_root=args.host_root, blacklist=args.blacklist, project_name=args.project_name,
                     worker_binding=binding, workbench_public_url=args.workbench_public_url)
    serve(path, app)


def _serve_project(path, args, binding, warm_worker=None):
    with _open_bound_peers(path, args, binding, Event(), warm_worker) as peers:
        asyncio.run(peers.wait_ready(args.instance_id))
        _serve_api(path, args, binding, peers.database_socket, peers.orchestrator_socket)


def _watch_parent(stop):
    with suppress(OSError):
        while os.read(sys.stdin.fileno(), 4096):
            pass
    stop.set()


def _publish_ready(path, peers, stop):
    if not peers.alive:
        raise RuntimeError("A bound Beta peer exited")
    path.touch(mode=0o600, exist_ok=False)
    try:
        while not stop.is_set():
            if not peers.alive:
                raise RuntimeError("A bound Beta peer exited")
            sleep(0.1)
    finally:
        path.unlink(missing_ok=True)


def _own_project(path, args, binding):
    stop = Event()
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, lambda *_: stop.set())
    Thread(target=_watch_parent, args=(stop,), daemon=True).start()
    try:
        with open_warm_worker() as worker, _open_bound_peers(path, args, binding, stop, worker) as peers:
            asyncio.run(peers.wait_ready(args.instance_id, stop=stop))
            if not stop.is_set():
                _publish_ready(path.parent / "peers.ready", peers, stop)
    except RuntimeError:
        if not stop.is_set():
            raise


def _private_artifact(path, kind):
    try:
        info = path.lstat()
    except FileNotFoundError:
        raise ValueError("Beta peer owner is not ready") from None
    if not kind(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077:
        raise ValueError("Invalid Beta peer owner artifact")
    return info


async def _check_peer_binding(args, database, orchestrator):
    kernel, jobs = await asyncio.gather(upstream(database, "GET", "/health", timeout=2),
                                        upstream(orchestrator, "GET", "/health", timeout=2))
    reports = [reply.get("result") for reply in (kernel, jobs)]
    if any(not isinstance(report, dict) or report.get("instance_id") != args.instance_id
           or type(report.get("pid")) is not int or report["pid"] <= 1 for report in reports):
        raise ValueError("Beta peer reported a different Project binding")
    health = reports[0]
    if health.get("manifest_sha256") != args.manifest_sha256 or health.get("ready") is not True:
        raise ValueError("Kernel did not admit the selected Beta Project")


def _attach_project(path, args, binding):
    marker = path.parent / "peers.ready"
    if _private_artifact(marker, stat.S_ISREG).st_size:
        raise ValueError("Invalid Beta peer readiness marker")
    database, orchestrator = (path.parent / name for name in ("db.sock", "jobs.sock"))
    for peer_socket in (database, orchestrator):
        _private_artifact(peer_socket, stat.S_ISSOCK)
    asyncio.run(_check_peer_binding(args, str(database), str(orchestrator)))
    _serve_api(path, args, binding, str(database), str(orchestrator))


def _terminate(_signum, _frame):
    raise SystemExit(1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("socket", "instance-id", "project-root", "control-root", "manifest-path",
                 "manifest-sha256", "project-prefix"):
        parser.add_argument("--" + name, required=True)
    parser.add_argument("--host-root")
    parser.add_argument("--project-name")
    parser.add_argument("--workbench-public-url")
    parser.add_argument("--blacklist", action="append", default=[])
    parser.add_argument("--watch-code", action="store_true")
    parser.add_argument("--workbench-storage", choices=("disk", "memory"), default="disk")
    parser.add_argument("--journal-storage", choices=("files", "duckdb"), default="files")
    parser.add_argument("--journal-relative")
    parser.add_argument("--result-ttl-seconds", type=int)
    parser.add_argument("--role", choices=("combined", "peer-owner", "api"), default="combined")
    args = parser.parse_args()
    path = socket_path(args.socket)
    binding = {"root": args.project_root, "control_root": args.control_root, "manifest_path": args.manifest_path,
               "manifest_sha256": args.manifest_sha256, "project_prefix": args.project_prefix}
    if args.role == "peer-owner":
        _own_project(path, args, binding)
        return
    signal.signal(signal.SIGTERM, _terminate)
    if args.role == "api":
        _attach_project(path, args, binding)
        return
    with open_warm_worker() as worker:
        _serve_project(path, args, binding, worker)


if __name__ == "__main__":
    main()
