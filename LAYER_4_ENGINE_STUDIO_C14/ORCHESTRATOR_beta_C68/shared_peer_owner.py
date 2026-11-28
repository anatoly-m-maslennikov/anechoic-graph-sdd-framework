"Own the shared Beta host's warm Project peers behind a private Unix socket."

import argparse
import asyncio
from contextlib import suppress
from copy import deepcopy
from dataclasses import asdict, replace
import json
import os
import re
import signal
import socket
import sys
from threading import Thread
from typing import Literal

from pydantic import BaseModel, ConfigDict, ValidationError

from ORCHESTRATOR_beta_C68.peers.project_admission import AdmissionClient, _selection
from ORCHESTRATOR_beta_C68.peers.shared_host_config import load
from ORCHESTRATOR_beta_C68.peers.shared_project_pool import SharedProjectPool
from ORCHESTRATOR_beta_C68.peers.warm_worker_process import open_warm_worker
from ORCHESTRATOR_beta_C68.peers.project_peers import socket_path

_LIMIT = 1024 * 1024
_RELEASE = b"R"


class _SelectRequest(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    operation: Literal["select"]
    project_root: str


class _LeaseRequest(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    operation: Literal["lease"]
    binding: object
    start: bool


def _encode(message):
    return json.dumps(message).encode() + b"\n"


async def _read(reader):
    line = await reader.readline()
    if not line.endswith(b"\n"):
        raise RuntimeError("Incomplete peer owner message")
    message = json.loads(line)
    if not isinstance(message, dict):
        raise RuntimeError("Invalid peer owner message")
    return message


async def _send(writer, message):
    writer.write(message)
    await writer.drain()


async def _close(writer):
    writer.close()
    with suppress(OSError):
        await writer.wait_closed()


def _wire_binding(selection):
    binding = asdict(selection)
    for key in (
        "root",
        "control_root",
        "control_relative",
        "manifest_path",
        "host_root",
    ):
        if binding[key] is not None:
            binding[key] = str(binding[key])
    return binding


def _check_current(config):
    try:
        current = load(config.source)
    except OSError, ValueError, TypeError:
        raise ValueError("host_configuration_invalid") from None
    if current != config:
        raise ValueError("host_configuration_stale")


def _check_paths(config, selection):
    root, control, manifest = (
        selection.root,
        selection.control_root,
        selection.manifest_path,
    )
    relative = selection.control_relative
    config.project(str(root))
    if (
        len(relative.parts) != 1
        or relative.is_absolute()
        or relative.name == ".."
        or control != root / relative
        or control.resolve(strict=True) != control
        or not control.is_dir()
        or manifest.parent not in (root, control)
        or manifest.resolve(strict=True) != manifest
        or not manifest.is_file()
        or selection.host_root is not None
    ):
        raise ValueError("Invalid peer owner Project paths")


def _configured(config, selected):
    parameters = deepcopy(selected.parameters)
    runtime = parameters.setdefault("runtime", {})
    name = (
        "iwe_console"
        if "iwe_console" in runtime or "workbench" not in runtime
        else "workbench"
    )
    runtime.setdefault(name, {}).setdefault(
        "storage", config.workbench_storage
    )
    runtime.setdefault("journal", {}).setdefault(
        "storage", config.journal_storage
    )
    return replace(selected, parameters=parameters)


def _select(config, admission, data):
    if set(data) == {"operation"}:
        raise ValueError("missing_project_root")
    try:
        request = _SelectRequest.model_validate(data)
    except ValidationError:
        raise ValueError("invalid_project_root") from None
    _check_current(config)
    try:
        path = config.project(request.project_root)
    except OSError:
        raise ValueError("invalid_project_root") from None
    try:
        selected = _configured(config, admission(path))
        if selected.root != path:
            raise ValueError("Project admission returned a different root")
        _check_paths(config, selected)
    except ValueError, OSError:
        raise ValueError("invalid_project_root") from None
    _check_current(config)
    return _wire_binding(selected)


def _binding(config, data):
    _check_current(config)
    selected = _selection({"result": data})
    try:
        _check_paths(config, selected)
    except ValueError, OSError, RuntimeError:
        raise ValueError("project_declarations_stale") from None
    if any(
        re.fullmatch(r"[0-9a-f]{64}", value) is None
        for value in (selected.instance_id, selected.manifest_sha256)
    ):
        raise ValueError("Invalid peer owner Project binding")
    return _configured(config, selected)


def _revalidate(config, admission, selected):
    _check_current(config)
    _check_paths(config, selected)
    if _configured(config, admission(selected.root)) != selected:
        raise ValueError("project_declarations_stale")
    _check_current(config)


async def _hold(pool, selection, start, writer):
    async with pool.lease(selection, start=start) as peers:
        result = (
            None
            if peers is None
            else {
                "database_socket": peers.database_socket,
                "orchestrator_socket": peers.orchestrator_socket,
                "worker_binding": peers.worker_binding,
            }
        )
        await _send(writer, _encode({"result": result}))
        await asyncio.Future()


async def _lease(pool, selection, start, reader, writer):
    stopped = asyncio.create_task(reader.read(1))
    lease = asyncio.create_task(_hold(pool, selection, start, writer))
    try:
        done, _ = await asyncio.wait(
            (stopped, lease), return_when=asyncio.FIRST_COMPLETED
        )
        if lease in done:
            lease.result()
    finally:
        stopped.cancel()
        lease.cancel()
        await asyncio.gather(stopped, lease, return_exceptions=True)
    if stopped.result() == _RELEASE:
        await _send(writer, _encode({"result": None}))


async def _dispatch(config, pool, admission, reader, writer):
    async with asyncio.timeout(2):
        request = await _read(reader)
    if request == {"operation": "status"}:
        await _send(writer, _encode({"result": pool.status()}))
        return
    if request.get("operation") == "select":
        selected = await asyncio.to_thread(_select, config, admission, request)
        await _send(writer, _encode({"result": selected}))
        return
    try:
        lease = _LeaseRequest.model_validate(request)
    except ValidationError:
        raise ValueError("Invalid peer owner request") from None
    await _lease(
        pool, _binding(config, lease.binding), lease.start, reader, writer
    )


async def _handle(config, pool, admission, reader, writer):
    try:
        with suppress(ConnectionError):
            try:
                await _dispatch(config, pool, admission, reader, writer)
            except (ValueError, RuntimeError) as error:
                kind = (
                    "ValueError"
                    if isinstance(error, ValueError)
                    else "RuntimeError"
                )
                await _send(
                    writer, _encode({"error": kind, "message": str(error)})
                )
            except OSError, TypeError:
                await _send(
                    writer,
                    _encode(
                        {
                            "error": "RuntimeError",
                            "message": "Peer owner request failed",
                        }
                    ),
                )
    finally:
        await _close(writer)


async def _serve(path, config, pool, admission, stopped):
    clients = set()

    def accept(reader, writer):
        task = asyncio.create_task(
            _handle(config, pool, admission, reader, writer)
        )
        clients.add(task)
        task.add_done_callback(clients.discard)

    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as listener:
        listener.bind(os.fspath(path))
        server = await asyncio.start_unix_server(
            accept, sock=listener, limit=_LIMIT
        )
        try:
            await stopped.wait()
        finally:
            server.close()
            server.close_clients()
            await server.wait_closed()
            await asyncio.to_thread(admission.close)
            await asyncio.gather(*clients, return_exceptions=True)


def _watch_parent(stop):
    with suppress(OSError):
        while os.read(sys.stdin.fileno(), 4096):
            pass
    stop()


async def _run(path, config):
    loop, stopped = asyncio.get_running_loop(), asyncio.Event()
    startup_stopped = False

    def stop():
        nonlocal startup_stopped
        startup_stopped = True
        with suppress(RuntimeError):
            loop.call_soon_threadsafe(stopped.set)

    Thread(target=_watch_parent, args=(stop,), daemon=True).start()
    pool = SharedProjectPool(config.maximum)
    admission = AdmissionClient()

    async def revalidate(selection):
        await asyncio.to_thread(_revalidate, config, admission, selection)

    signals = (signal.SIGINT, signal.SIGTERM)
    previous = {sig: signal.signal(sig, lambda *_: stop()) for sig in signals}
    try:
        with open_warm_worker(
            stop=lambda: startup_stopped
        ) as pool.warm_worker:
            if startup_stopped:
                return
            try:
                async with asyncio.TaskGroup() as tasks:
                    monitor = tasks.create_task(pool.monitor(revalidate))
                    try:
                        await _serve(path, config, pool, admission, stopped)
                    finally:
                        monitor.cancel()
            finally:
                await pool.close()
    finally:
        for sig, handler in previous.items():
            signal.signal(sig, handler)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--socket", required=True)
    parser.add_argument("--host-settings", required=True)
    args = parser.parse_args()
    os.umask(0o077)
    config = load(args.host_settings)
    level = os.environ.get("ANECHOIC_LOG_LEVEL", config.log_level)
    if level not in ("DEBUG", "INFO", "WARNING", "ERROR"):
        raise ValueError("Invalid ANECHOIC_LOG_LEVEL")
    os.environ.setdefault("ANECHOIC_LOG_LEVEL", level)
    asyncio.run(_run(socket_path(args.socket), config))


if __name__ == "__main__":
    main()
