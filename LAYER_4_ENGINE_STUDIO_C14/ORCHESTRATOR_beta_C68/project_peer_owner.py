"""Keep one Project's peer pair independent of its API and MCP processes."""

import argparse
from contextlib import suppress
import os
import signal
import sys
from threading import Event, Thread

from pydantic import BaseModel, ConfigDict

from ORCHESTRATOR_beta_C68.peers.project_peers import ProjectBinding, open_project_peers, socket_path
from ORCHESTRATOR_beta_C68.peers.warm_worker_process import open_warm_worker


class _Options(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True)

    socket: str
    instance_id: str
    project_root: str
    control_root: str
    manifest_path: str
    manifest_sha256: str
    project_prefix: str
    watch_code: bool
    workbench_storage: str
    journal_storage: str
    journal_relative: str | None
    result_ttl_seconds: int | None


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
        while not stop.wait(0.1):
            if not peers.alive:
                raise RuntimeError("A bound Beta peer exited")
    finally:
        path.unlink(missing_ok=True)


def _own_project(path, args, binding):
    stop = Event()
    for signum in (signal.SIGINT, signal.SIGTERM):
        signal.signal(signum, lambda *_: stop.set())
    Thread(target=_watch_parent, args=(stop,), daemon=True).start()
    try:
        with open_warm_worker(stop=stop.is_set) as worker:
            with open_project_peers(
                path.parent,
                args.instance_id,
                binding,
                stop,
                watch_code=args.watch_code,
                storage=args.workbench_storage,
                journal_storage=args.journal_storage,
                journal_relative=args.journal_relative,
                result_ttl_seconds=args.result_ttl_seconds,
                warm_worker=worker,
            ) as peers:
                if not stop.is_set():
                    _publish_ready(path.parent / "peers.ready", peers, stop)
    except RuntimeError:
        if not stop.is_set():
            raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in (
        "socket",
        "instance-id",
        "project-root",
        "control-root",
        "manifest-path",
        "manifest-sha256",
        "project-prefix",
    ):
        parser.add_argument("--" + name, required=True)
    for name in (
        "host-root",
        "project-name",
        "workbench-public-url",
        "journal-relative",
    ):
        parser.add_argument("--" + name)
    parser.add_argument("--blacklist", action="append", default=[])
    parser.add_argument("--watch-code", action="store_true")
    parser.add_argument(
        "--workbench-storage", choices=("disk", "memory"), default="disk"
    )
    parser.add_argument(
        "--journal-storage", choices=("files", "duckdb"), default="files"
    )
    parser.add_argument("--result-ttl-seconds", type=int)
    args = _Options.model_validate(vars(parser.parse_args()))
    path = socket_path(args.socket)
    binding = ProjectBinding(
        root=args.project_root,
        control_root=args.control_root,
        manifest_path=args.manifest_path,
        manifest_sha256=args.manifest_sha256,
        project_prefix=args.project_prefix,
    )
    os.umask(0o077)
    _own_project(path, args, binding)


if __name__ == "__main__":
    main()
