"""Serve one pinned Project's Workbench through a private Unix socket."""

from __future__ import annotations

import argparse
from contextlib import asynccontextmanager
import logging
import os
from pathlib import Path
import re
import shlex
import stat
import sys
import threading
from functools import partial

import anyio
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
import uvicorn

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.\
    ATOM_LIFECYCLE.NATIVE_LIFECYCLE.\
    NATIVE_LIFECYCLE__shared import (
    declared_release_entrypoint,
)
from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import (
    QueryExecutionError,
    WorkbenchUnavailableError,
)

from ....kernel_client import kernel_client
from ....backend_tool_api import BackendToolAPI
from ....workbench_operations import WorkbenchOperations

_LOG = logging.getLogger(__name__)


def _socket_path(value):
    path = Path(value)
    parent = path.parent
    info = parent.stat()
    if (
        not path.is_absolute()
        or str(path) != value
        or path.exists()
        or path.is_symlink()
        or parent.resolve(strict=True) != parent
        or parent.is_symlink()
        or not stat.S_ISDIR(info.st_mode)
        or info.st_uid != os.getuid()
        or stat.S_IMODE(info.st_mode) & 0o077
    ):
        raise ValueError("Backend socket directory is unavailable or unsafe")
    return path


def _error(code, message):
    return JSONResponse({"error": {"code": code, "message": message}})


def _operations(owner):
    workbench = WorkbenchOperations(
        query_owner=owner, lock=owner._interface_lock
    )
    return {
        "workbench": workbench.call,
        "lifecycle": owner.lifecycle,
        "release_command": partial(_pinned_release_command, owner.selection),
    }


def _release_request(selection, name, arguments):
    from ....project_admission import project_tool_policy

    if name not in ("local_release_command", "public_release_command"):
        raise ValueError("Unknown release command Tool")
    if not project_tool_policy(selection.parameters)[1]:
        raise ValueError("Release workflows are not enabled")
    root = Path(selection.host_root or selection.root)
    if not root.is_absolute():
        raise ValueError("Release command requires an absolute Project root")
    public = name == "public_release_command"
    if not isinstance(arguments, dict) or set(arguments) - (
        {"run_id", "base", "head", "content_draft"} if public else {"run_id"}
    ):
        raise ValueError("Unexpected release command input")
    run_id = arguments.get("run_id")
    pattern = (
        r"[A-Za-z0-9][A-Za-z0-9._:-]*"
        if public
        else r"[A-Za-z0-9][A-Za-z0-9._-]*"
    )
    if not isinstance(run_id, str) or re.fullmatch(pattern, run_id) is None:
        raise ValueError("release-run-id-invalid")
    operation = "public" if public else "local"
    return root, operation, run_id


def _release_command(selection, name, arguments):
    root, operation, run_id = _release_request(selection, name, arguments)
    entrypoint = declared_release_entrypoint(selection, operation)
    args = [
        "uv",
        "run",
        "--project",
        str(root / "LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/release"),
        "--locked",
        "--python",
        "3.14",
        "--managed-python",
        "--no-env-file",
        "python",
        "-B",
        "-E",
        str(root / entrypoint),
        operation,
        "--project-root",
        str(root),
        "--run-id",
        run_id,
    ]
    for key in ("base", "head", "content_draft"):
        if key in arguments:
            value = arguments[key]
            if (
                not isinstance(value, str)
                or not value
                or "\0" in value
                or value.startswith("-")
            ):
                raise ValueError(f"{key}-invalid")
            args.extend((f"--{key.replace('_', '-')}", value))
    env = shlex.quote(
        str(root / "LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/.venv-release")
    )
    return {
        "working_directory": str(root),
        "command": f"UV_PROJECT_ENVIRONMENT={env} {shlex.join(args)}",
    }


def _pinned_release_command(binding, name, arguments):
    from ....project_admission import pinned_project

    return _release_command(pinned_project(binding), name, arguments)


def _admit(value, instance_id, methods):
    if not isinstance(value, dict) or set(value) != {
        "operation",
        "name",
        "arguments",
        "instance_id",
        "session_id",
    }:
        raise ValueError("Invalid request envelope")
    operation, name = value["operation"], value["name"]
    session = value["session_id"]
    if (
        not isinstance(operation, str)
        or operation not in methods
        or not isinstance(name, str)
        or value["instance_id"] != instance_id
        or (
            session is not None
            and (not isinstance(session, str) or not session.strip())
        )
    ):
        raise ValueError("Invalid request envelope")
    return methods[operation], name, value["arguments"]


def _worker_runs_route(owner, instance_id):
    async def worker_runs(request: Request):
        if request.query_params.getlist("instance_id") != [instance_id]:
            return _error("value_error", "Invalid Worker Run request binding")
        try:
            result = await anyio.to_thread.run_sync(owner.worker_runs)
        except WorkbenchUnavailableError:
            return _error(
                "workbench_unavailable", "Kernel unavailable; restart required"
            )
        except ValueError, RuntimeError:
            _LOG.exception("Worker Run status request failed")
            return _error("internal", "Worker Run status request failed")
        return JSONResponse({"result": result})

    return Route("/jobs/worker-runs", worker_runs)


def _health_route(owner, instance_id):
    async def health(_request):
        ready = owner.available
        return JSONResponse(
            {
                "ready": ready,
                "instance_id": instance_id,
                "manifest_sha256": owner.selection.manifest_sha256,
                "pid": os.getpid(),
                "kernel_pid": owner.pid,
            },
            status_code=200 if ready else 503,
        )

    return Route("/health", health)


def _workbench_route(methods, instance_id):
    async def workbench(request: Request):
        try:
            method, name, arguments = _admit(
                await request.json(), instance_id, methods
            )
            with anyio.CancelScope(shield=True):
                result = await anyio.to_thread.run_sync(
                    method, name, arguments
                )
            return JSONResponse({"result": result})
        except ValueError as error:
            return _error("value_error", str(error))
        except QueryExecutionError as error:
            return _error("query_error", str(error))
        except WorkbenchUnavailableError:
            return _error(
                "workbench_unavailable",
                "Workbench unavailable; restart required",
            )
        except Exception:
            _LOG.exception("Backend operation failed")
            return _error("internal", "Backend operation failed")

    return Route("/workbench", workbench, methods=["POST"])


def create_app(owner):
    methods = _operations(owner)
    tools = BackendToolAPI(owner, methods)
    instance_id = owner.selection.instance_id

    @asynccontextmanager
    async def lifespan(_app):
        try:
            yield
        finally:
            await tools.close()

    return Starlette(
        lifespan=lifespan,
        routes=[
            _health_route(owner, instance_id),
            _workbench_route(methods, instance_id),
            _worker_runs_route(owner, instance_id),
            Route("/", tools.catalog),
            Route("/", tools.invoke, methods=["POST"]),
        ],
    )


def _watch_parent(state, stopped):
    while os.read(sys.stdin.fileno(), 4096):
        pass
    stopped.set()
    server = state.get("server")
    if server is not None:
        server.should_exit = True


def _watch_kernel(owner, server):
    owner.wait()
    server.should_exit = True


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--socket", required=True)
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--control-root", required=True)
    parser.add_argument("--instance-id", required=True)
    parser.add_argument("--manifest-sha256", required=True)
    parser.add_argument("--host-project-root")
    parser.add_argument(
        "--default-workbench-storage", choices=("disk", "memory")
    )
    parser.add_argument(
        "--default-journal-storage", choices=("files", "duckdb")
    )
    args = parser.parse_args(argv)
    socket = _socket_path(args.socket)
    stopped = threading.Event()
    state = {}
    watcher = threading.Thread(
        target=_watch_parent, args=(state, stopped), daemon=True
    )
    watcher.start()
    with kernel_client(args) as owner:
        server = uvicorn.Server(
            uvicorn.Config(
                create_app(owner),
                uds=str(socket),
                log_level="warning",
                timeout_graceful_shutdown=10,
            )
        )
        state["server"] = server
        threading.Thread(
            target=_watch_kernel, args=(owner, server), daemon=True
        ).start()
        if not stopped.is_set() and owner.available:
            server.run()


if __name__ == "__main__":
    main()
