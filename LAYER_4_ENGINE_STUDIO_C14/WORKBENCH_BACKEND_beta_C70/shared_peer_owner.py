"""Own the shared Beta host's warm Project peers behind a private Unix socket."""

import argparse
import asyncio
from contextlib import asynccontextmanager, suppress
from copy import deepcopy
from dataclasses import asdict, dataclass, replace
import json
import os
import re
import signal
import socket
import sys
from threading import Thread

from .project_admission import AdmissionClient, _selection
from .shared_host_config import load
from .shared_project_pool import SharedProjectPool
from .warm_worker import open_warm_worker
from .WORKBENCH_BACKEND_beta_C70__shared import socket_path

_LIMIT = 1024 * 1024
_RELEASE = b"R"


@dataclass(frozen=True)
class _PeerSockets:
    database_socket: str
    orchestrator_socket: str
    worker_binding: dict


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


async def _exchange(reader, writer, request):
    try:
        await _send(writer, request)
        response = await _read(reader)
    except (OSError, ValueError) as error:
        raise RuntimeError("Peer owner exchange failed") from error
    if set(response) == {"result"}:
        return response["result"]
    if set(response) == {"error", "message"} and isinstance(response["message"], str):
        error_types = {"ValueError": ValueError, "RuntimeError": RuntimeError}
        if isinstance(response["error"], str) and response["error"] in error_types:
            raise error_types[response["error"]](response["message"])
    raise RuntimeError("Invalid peer owner response")


async def _close(writer):
    writer.close()
    with suppress(OSError):
        await writer.wait_closed()


class PeerOwnerClient:
    def __init__(self, path):
        self.path = path

    @asynccontextmanager
    async def _connect(self):
        try:
            reader, writer = await asyncio.open_unix_connection(self.path, limit=_LIMIT)
        except OSError as error:
            raise RuntimeError("Peer owner unavailable") from error
        try:
            yield reader, writer
        finally:
            await _close(writer)

    async def status(self):
        async with asyncio.timeout(2), self._connect() as (reader, writer):
            return await _exchange(reader, writer, _encode({"operation": "status"}))

    @asynccontextmanager
    async def lease(self, selection, *, start=True):
        binding = asdict(selection)
        for key in ("root", "control_root", "control_relative", "manifest_path", "host_root"):
            if binding[key] is not None:
                binding[key] = str(binding[key])
        request = _encode({"operation": "lease", "binding": binding, "start": start})
        async with self._connect() as (reader, writer):
            result = await _exchange(reader, writer, request)
            yield None if result is None else _PeerSockets(**result)
            async with asyncio.timeout(2):
                await _exchange(reader, writer, _RELEASE)


def _check_current(config):
    try:
        current = load(config.source)
    except (OSError, ValueError, TypeError):
        raise ValueError("host_configuration_invalid") from None
    if current != config:
        raise ValueError("host_configuration_stale")


def _check_paths(config, selection):
    root, control, manifest = selection.root, selection.control_root, selection.manifest_path
    relative = selection.control_relative
    config.project(str(root))
    if (len(relative.parts) != 1 or relative.is_absolute() or relative.name == ".."
            or control != root / relative or control.resolve(strict=True) != control or not control.is_dir()
            or manifest.parent not in (root, control) or manifest.resolve(strict=True) != manifest
            or not manifest.is_file() or selection.host_root is not None):
        raise ValueError("Invalid peer owner Project paths")


def _configured(config, selected):
    parameters = deepcopy(selected.parameters)
    runtime = parameters.setdefault("runtime", {})
    runtime.setdefault("workbench", {}).setdefault("storage", config.workbench_storage)
    runtime.setdefault("journal", {}).setdefault("storage", config.journal_storage)
    return replace(selected, parameters=parameters)


def _binding(config, data):
    _check_current(config)
    selected = _selection({"result": data})
    try:
        _check_paths(config, selected)
    except (ValueError, OSError, RuntimeError):
        raise ValueError("project_declarations_stale") from None
    if any(re.fullmatch(r"[0-9a-f]{64}", value) is None
           for value in (selected.instance_id, selected.manifest_sha256)):
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
        result = None if peers is None else {
            "database_socket": peers.database_socket, "orchestrator_socket": peers.orchestrator_socket,
            "worker_binding": peers.worker_binding,
        }
        await _send(writer, _encode({"result": result}))
        await asyncio.Future()


async def _lease(pool, selection, start, reader, writer):
    # Watch the socket while startup and readiness checks hold the pool lease.
    stopped = asyncio.create_task(reader.read(1))
    lease = asyncio.create_task(_hold(pool, selection, start, writer))
    try:
        done, _ = await asyncio.wait((stopped, lease), return_when=asyncio.FIRST_COMPLETED)
        if lease in done:
            lease.result()
    finally:
        stopped.cancel()
        lease.cancel()
        await asyncio.gather(stopped, lease, return_exceptions=True)
    if stopped.result() == _RELEASE:
        await _send(writer, _encode({"result": None}))


async def _dispatch(config, pool, reader, writer):
    async with asyncio.timeout(2):
        request = await _read(reader)
    if request == {"operation": "status"}:
        await _send(writer, _encode({"result": pool.status()}))
        return
    if (set(request) != {"operation", "binding", "start"} or request["operation"] != "lease"
            or type(request["start"]) is not bool):
        raise ValueError("Invalid peer owner request")
    await _lease(pool, _binding(config, request["binding"]), request["start"], reader, writer)


async def _handle(config, pool, reader, writer):
    try:
        with suppress(ConnectionError):
            try:
                await _dispatch(config, pool, reader, writer)
            except (ValueError, RuntimeError) as error:
                kind = "ValueError" if isinstance(error, ValueError) else "RuntimeError"
                await _send(writer, _encode({"error": kind, "message": str(error)}))
            except (OSError, TypeError):
                await _send(writer, _encode({"error": "RuntimeError", "message": "Peer owner request failed"}))
    finally:
        await _close(writer)


async def _serve(path, config, pool, stopped):
    clients = set()

    def accept(reader, writer):
        task = asyncio.create_task(_handle(config, pool, reader, writer))
        clients.add(task)
        task.add_done_callback(clients.discard)

    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as listener:
        listener.bind(os.fspath(path))
        server = await asyncio.start_unix_server(accept, sock=listener, limit=_LIMIT)
        try:
            await stopped.wait()
        finally:
            server.close()
            server.close_clients()
            await server.wait_closed()
            await asyncio.gather(*clients, return_exceptions=True)


def _watch_parent(loop, stopped):
    with suppress(OSError):
        while os.read(sys.stdin.fileno(), 4096):
            pass
    with suppress(RuntimeError):
        loop.call_soon_threadsafe(stopped.set)


async def _run(path, config):
    loop, stopped = asyncio.get_running_loop(), asyncio.Event()
    Thread(target=_watch_parent, args=(loop, stopped), daemon=True).start()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stopped.set)
    pool = SharedProjectPool(config.maximum)
    admission = AdmissionClient()

    async def revalidate(selection):
        await asyncio.to_thread(_revalidate, config, admission, selection)

    with open_warm_worker() as pool.warm_worker:
        try:
            async with asyncio.TaskGroup() as tasks:
                monitor = tasks.create_task(pool.monitor(revalidate))
                try:
                    await _serve(path, config, pool, stopped)
                finally:
                    monitor.cancel()
                    await asyncio.to_thread(admission.close)
        finally:
            await pool.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--socket", required=True)
    parser.add_argument("--host-settings", required=True)
    args = parser.parse_args()
    os.umask(0o077)
    asyncio.run(_run(socket_path(args.socket), load(args.host_settings)))


if __name__ == "__main__":
    main()
