"""Serve one pinned Project's Kernel through a private Unix socket."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
from copy import deepcopy
from dataclasses import replace
import logging
import inspect
import os
from pathlib import Path
import re
import stat
import sys
import threading

import anyio
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
import uvicorn

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__shared import rebind_native_selection, resolve_native_project
from KERNEL_MIXER_C59.MANIFEST_RUNTIME_C62.MANIFEST_RUNTIME_C62__shared import run_manifest_runtime
from KERNEL_MIXER_C59.MANIFEST_RUNTIME_C62.model_host_CS2.model_host_CS2__shared import reviewed_native_model
from KERNEL_MIXER_C59.ORCHESTRATOR_C66.ORCHESTRATOR_C66__shared import Orchestrator

from .errors import QueryExecutionError, WorkbenchUnavailableError
from .native_query_runtime import NativeQueryInputs
from .native_service_owner import NativeQueryOwner

_HEX = re.compile(r"[0-9a-f]{64}\Z")
_LOG = logging.getLogger(__name__)


def _selection(args, model):
    root = Path(args.project_root)
    control = Path(args.control_root)
    if (not root.is_absolute() or str(root) != args.project_root
            or root.resolve(strict=True) != root or root.is_symlink()
            or control.is_absolute() or len(control.parts) != 1
            or control.as_posix() != args.control_root
            or _HEX.fullmatch(args.instance_id) is None
            or _HEX.fullmatch(args.manifest_sha256) is None):
        raise ValueError("Invalid Project binding")
    selection = resolve_native_project(
        root, args.control_root, validate_manifest=model.validate_manifest,
        require_atom_state=model.requires_atom_state,
        require_atom_header=model.requires_atom_header,
        require_manifest_summary=model.declares_summary("Project Manifest"),
    )
    if selection.root != root or selection.control_relative != control:
        raise ValueError("Project binding changed")
    if selection.manifest_sha256 != args.manifest_sha256:
        raise ValueError("Project binding changed")
    return rebind_native_selection(selection, args.instance_id, host_root=args.host_project_root)



def _with_storage_defaults(selection, workbench, journal):
    if workbench is None and journal is None:
        return selection
    parameters = deepcopy(selection.parameters)
    runtime = parameters.setdefault("runtime", {})
    if isinstance(runtime, dict):
        for name, storage in (("workbench", workbench), ("journal", journal)):
            if storage is None:
                continue
            section = runtime.setdefault(name, {})
            if isinstance(section, dict):
                section.setdefault("storage", storage)
    return replace(selection, parameters=parameters)


def _inputs(model):
    extensions = os.environ.get("ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY")
    return NativeQueryInputs(
        model.validate_manifest, model.relation_types, model.inverses,
        extension_directory=Path(extensions) if extensions else None,
        require_atom_state=model.requires_atom_state,
        require_atom_header=model.requires_atom_header,
        ticket_labels=model.ticket_labels,
        validate_project_spec=model.validate_project_spec,
        require_manifest_summary=model.declares_summary("Project Manifest"),
    )


@contextmanager
def _owner(args, orchestrator):
    selected = _selection(args, reviewed_native_model())
    with run_manifest_runtime(selected, orchestrator=orchestrator) as (_, snapshot, model):
        current = _selection(args, model)
        if current != selected:
            raise ValueError("Project binding changed")
        current = _with_storage_defaults(current, args.default_workbench_storage, args.default_journal_storage)
        owner = NativeQueryOwner(replace(current, structure_snapshot=snapshot), _inputs(model))
        try:
            owner.start()
            yield owner
        finally:
            _close_owner(owner)


def _close_owner(owner):
    errors = []
    def close():
        try:
            owner.close()
        except BaseException as error:
            errors.append(error)
    worker = threading.Thread(target=close, daemon=True)
    worker.start()
    worker.join(timeout=10)
    if worker.is_alive():
        raise RuntimeError("Workbench shutdown timed out")
    if errors:
        raise errors[0]


def _socket_path(value):
    path = Path(value)
    parent = path.parent
    info = parent.stat()
    if (not path.is_absolute() or str(path) != value or path.exists() or path.is_symlink()
            or parent.resolve(strict=True) != parent or parent.is_symlink()
            or not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid()
            or stat.S_IMODE(info.st_mode) & 0o077):
        raise ValueError("Kernel socket directory is unavailable or unsafe")
    return path


def _error(code, message):
    return JSONResponse({"error": {"code": code, "message": message}})


def _operations(owner):
    names = ("status", "interface_call", "run", "check", "page", "schema", "save_view", "load",
             "saved_list", "rebuild", "lifecycle")
    return {name: getattr(owner, name) for name in names}


def _admit(value, instance_id, methods):
    if not isinstance(value, dict) or set(value) != {"operation", "args", "kwargs", "instance_id"}:
        raise ValueError("Invalid request envelope")
    operation, args, kwargs = value["operation"], value["args"], value["kwargs"]
    if (not isinstance(operation, str) or operation not in methods or value["instance_id"] != instance_id
            or not isinstance(args, list) or not isinstance(kwargs, dict)):
        raise ValueError("Invalid request envelope")
    method = methods[operation]
    try:
        inspect.signature(method).bind(*args, **kwargs)
    except TypeError as error:
        raise ValueError("Invalid request arguments") from error
    return method, args, kwargs


def _worker_runs_route(orchestrator, instance_id):
    async def worker_runs(request: Request):
        if request.query_params.getlist("instance_id") != [instance_id]:
            return _error("value_error", "Invalid Worker Run request binding")
        return JSONResponse({"result": orchestrator.worker_runs()})

    return Route("/jobs/worker-runs", worker_runs)


def create_app(owner, orchestrator):
    methods = _operations(owner)
    instance_id = owner.selection.instance_id

    async def health(_request):
        return JSONResponse({"ready": True, "instance_id": instance_id,
                             "manifest_sha256": owner.selection.manifest_sha256,
                             "pid": os.getpid()})

    async def database(request: Request):
        try:
            method, args, kwargs = _admit(await request.json(), instance_id, methods)
            def call():
                if method == methods["status"]:
                    return method(*args, **kwargs)
                with owner._interface_lock:
                    return method(*args, **kwargs)
            with anyio.CancelScope(shield=True):
                result = await anyio.to_thread.run_sync(call)
            return JSONResponse({"result": result})
        except ValueError as error:
            return _error("value_error", str(error))
        except QueryExecutionError as error:
            return _error("query_error", str(error))
        except WorkbenchUnavailableError:
            return _error("workbench_unavailable", "Workbench unavailable; restart required")
        except Exception:
            _LOG.exception("Kernel operation failed")
            return _error("internal", "Kernel operation failed")

    return Starlette(routes=[
        Route("/health", health),
        Route("/database", database, methods=["POST"]),
        _worker_runs_route(orchestrator, instance_id),
    ])


def _watch_parent(state, stopped, orchestrator):
    while os.read(sys.stdin.fileno(), 4096):
        pass
    stopped.set()
    orchestrator.stop()
    server = state.get("server")
    if server is not None:
        server.should_exit = True


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--socket", required=True)
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--control-root", required=True)
    parser.add_argument("--instance-id", required=True)
    parser.add_argument("--manifest-sha256", required=True)
    parser.add_argument("--host-project-root")
    parser.add_argument("--default-workbench-storage", choices=("disk", "memory"))
    parser.add_argument("--default-journal-storage", choices=("files", "duckdb"))
    args = parser.parse_args(argv)
    socket = _socket_path(args.socket)
    stopped = threading.Event()
    state = {}
    orchestrator = Orchestrator()
    watcher = threading.Thread(target=_watch_parent, args=(state, stopped, orchestrator), daemon=True)
    watcher.start()
    with _owner(args, orchestrator) as owner:
        server = uvicorn.Server(uvicorn.Config(create_app(owner, orchestrator), uds=str(socket), log_level="warning",
                                               timeout_graceful_shutdown=10))
        state["server"] = server
        if not stopped.is_set():
            server.run()


if __name__ == "__main__":
    main()
