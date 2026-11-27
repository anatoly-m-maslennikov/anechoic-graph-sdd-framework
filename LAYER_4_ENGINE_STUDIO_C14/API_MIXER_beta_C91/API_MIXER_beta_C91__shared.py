"""Attach the single-Project Beta API to its supervised peers."""

import argparse
import asyncio
import os
from pathlib import Path
import re
import socket
import stat
import sys
import threading

import uvicorn

from .admission import peer
from .api import create_app
from .models import KernelHealth, PeerHealth
from .owner_client import WorkerBinding


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


def private_artifact(path, kind):
    info = path.lstat()
    if (
        not kind(info.st_mode)
        or info.st_uid != os.getuid()
        or info.st_mode & 0o077
    ):
        raise ValueError("Invalid Beta peer owner artifact")
    return info


async def check_peers(instance, digest, database, jobs):
    kernel_data, jobs_data = await asyncio.gather(
        peer(database, "GET", "/health"), peer(jobs, "GET", "/health")
    )
    kernel = KernelHealth.model_validate(kernel_data["result"])
    orchestrator = PeerHealth.model_validate(jobs_data["result"])
    if (
        kernel.instance_id != instance
        or orchestrator.instance_id != instance
        or kernel.manifest_sha256 != digest
    ):
        raise ValueError("Beta peer reported a different Project binding")


def serve(path, app):
    level = os.environ.get("ANECHOIC_LOG_LEVEL", "INFO")
    if level not in ("DEBUG", "INFO", "WARNING", "ERROR"):
        raise ValueError("Invalid ANECHOIC_LOG_LEVEL")
    server = uvicorn.Server(
        uvicorn.Config(app, log_level=level.lower(), access_log=False)
    )

    def watch_parent():
        while os.read(sys.stdin.fileno(), 4096):
            pass
        server.should_exit = True

    threading.Thread(target=watch_parent, daemon=True).start()
    os.umask(0o077)
    bound = False
    try:
        with socket.socket(socket.AF_UNIX) as listener:
            listener.bind(str(path))
            bound = True
            listener.listen(128)
            server.run(sockets=[listener])
    finally:
        if bound:
            path.unlink(missing_ok=True)


def _parser():
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
    parser.add_argument("--role", choices=("api",), required=True)
    return parser


def main():
    parser = _parser()
    args = parser.parse_args()
    if not args.instance_id or not re.fullmatch(
        r"[0-9a-f]{64}", args.manifest_sha256
    ):
        parser.error("Invalid Project binding")
    if not Path(args.project_root).is_absolute():
        parser.error("Project root must be absolute")
    path = socket_path(args.socket)
    if private_artifact(path.parent / "peers.ready", stat.S_ISREG).st_size:
        raise ValueError("Invalid Beta peer readiness marker")
    database, jobs = (path.parent / name for name in ("db.sock", "jobs.sock"))
    for item in (database, jobs):
        private_artifact(item, stat.S_ISSOCK)
    asyncio.run(
        check_peers(args.instance_id, args.manifest_sha256, database, jobs)
    )
    binding = WorkerBinding(
        root=args.project_root,
        control_root=args.control_root,
        manifest_path=args.manifest_path,
        manifest_sha256=args.manifest_sha256,
        project_prefix=args.project_prefix,
    ).model_dump()
    app = create_app(
        args.instance_id,
        args.manifest_sha256,
        args.project_root,
        database,
        jobs,
        host_root=args.host_root,
        blacklist=args.blacklist,
        worker_binding=binding,
        project_name=args.project_name,
        workbench_public_url=args.workbench_public_url,
    )
    serve(path, app)


if __name__ == "__main__":
    main()
