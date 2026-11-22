"""Start the single-Project Beta Backend with independent Kernel and Orchestrator peers."""

import argparse
from contextlib import contextmanager
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
from threading import Event
from time import monotonic, sleep

import httpx2

from .WORKBENCH_BACKEND_beta_C70__shared import create_app, serve, socket_path

ENGINE = Path(__file__).resolve().parents[1]
ORCHESTRATOR = "ORCHESTRATOR_beta_C68.ORCHESTRATOR_beta_C68__shared"
DATABASE = "KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.DATABASE_SERVER_beta_C71__shared"


def _stop(peer):
    for sig in (signal.SIGTERM, signal.SIGKILL):
        try:
            os.killpg(peer.pid, sig)
        except ProcessLookupError:
            pass
        try:
            peer.wait(timeout=5)
        except subprocess.TimeoutExpired:
            continue
        break
    else:
        peer.wait()


def _wait_for_peer(client, peer, instance_id, stop):
    deadline = monotonic() + 15
    while not stop.is_set() and peer.poll() is None and monotonic() < deadline:
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
            yield client, peer
    finally:
        _stop(peer)


def _wait_for_generation(kernel, jobs, instance_id, stop):
    deadline = monotonic() + 75
    while not stop.is_set() and monotonic() < deadline:
        health = kernel.get("/health", timeout=2)
        health.raise_for_status()
        runs = jobs.get("/jobs/worker-runs", params={"instance_id": instance_id}, timeout=2)
        runs.raise_for_status()
        latest = runs.json()["result"]["latest"]
        if health.json()["result"]["ready"] and latest and latest["state"] in ("succeeded", "failed"):
            return
        if latest and latest["state"] == "failed":
            raise RuntimeError("Initial Beta build failed: " + str(latest.get("message", latest.get("code")))[:2048])
        sleep(0.1)
    raise RuntimeError("Kernel did not admit an initial Beta generation")


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
                       journal_storage="files", journal_relative=None, result_ttl_seconds=None):
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
    with binding_file.open("x", encoding="utf-8") as stream:
        json.dump(binding, stream)
    try:
        with _peer(DATABASE, database, instance_id, stop, "--manifest-sha256", binding["manifest_sha256"], *db_args) as (kernel, kernel_process):
            with _peer(ORCHESTRATOR, orchestrator, instance_id, stop, "--binding-file", str(binding_file),
                       "--database-socket", str(database), *watch) as (jobs, jobs_process):
                _wait_for_generation(kernel, jobs, instance_id, stop)
                binding_file.unlink()
                yield ProjectPeers(str(database), str(orchestrator), binding, kernel_process, jobs_process)
    finally:
        binding_file.unlink(missing_ok=True)


def _serve_project(path, args, binding):
    with open_project_peers(path.parent, args.instance_id, binding, Event(), watch_code=args.watch_code,
                            storage=args.workbench_storage, journal_storage=args.journal_storage,
                            journal_relative=args.journal_relative, result_ttl_seconds=args.result_ttl_seconds) as peers:
        app = create_app(args.instance_id, args.manifest_sha256, args.project_root, peers.database_socket,
                         peers.orchestrator_socket, host_root=args.host_root, blacklist=args.blacklist,
                         project_name=args.project_name, worker_binding=peers.worker_binding)
        serve(path, app)


def _terminate(_signum, _frame):
    raise SystemExit(1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("socket", "instance-id", "project-root", "control-root", "manifest-path",
                 "manifest-sha256", "project-prefix"):
        parser.add_argument("--" + name, required=True)
    parser.add_argument("--host-root")
    parser.add_argument("--project-name")
    parser.add_argument("--blacklist", action="append", default=[])
    parser.add_argument("--watch-code", action="store_true")
    parser.add_argument("--workbench-storage", choices=("disk", "memory"), default="disk")
    parser.add_argument("--journal-storage", choices=("files", "duckdb"), default="files")
    parser.add_argument("--journal-relative")
    parser.add_argument("--result-ttl-seconds", type=int)
    args = parser.parse_args()
    path = socket_path(args.socket)
    signal.signal(signal.SIGTERM, _terminate)
    binding = {"root": args.project_root, "control_root": args.control_root, "manifest_path": args.manifest_path,
               "manifest_sha256": args.manifest_sha256, "project_prefix": args.project_prefix}
    _serve_project(path, args, binding)


if __name__ == "__main__":
    main()
