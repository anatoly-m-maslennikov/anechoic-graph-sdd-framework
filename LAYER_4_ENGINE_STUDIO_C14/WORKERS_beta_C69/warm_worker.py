"""Serve Ticket delta captures and indexed lifecycle writes in isolated children."""
import argparse
import json
import math
import os
import select
import signal
import socket
import stat
import time
from pathlib import Path

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    capture_ticket_delta,
)

from .native_refresh import _ticket_delta, valid_reuse
from .lifecycle_worker import run as lifecycle_run


def _admit_lifecycle(request):
    if set(request) != {"kind", "start_by", "request"}:
        return False
    job = request["request"]
    return (isinstance(job, dict)
            and set(job) == {"binding", "name", "arguments", "base_generation", "structure_sha256", "indexed_task"}
            and job["name"] == "atom_lifecycle_create_draft" and isinstance(job["indexed_task"], dict))


def _admit(request):
    if (not isinstance(request, dict) or isinstance(request.get("start_by"), bool)
            or not isinstance(request.get("start_by"), (int, float)) or not math.isfinite(request["start_by"])
            or request["start_by"] <= time.monotonic()):
        return False
    if request.get("kind") == "indexed_lifecycle":
        return _admit_lifecycle(request) and request["start_by"] > time.monotonic()
    if (set(request) != {"kind", "start_by", "binding", "reuse", "paths"}
            or request["kind"] != "ticket_delta" or not valid_reuse(request["reuse"])):
        return False
    binding, paths = request["binding"], request["paths"]
    if (not isinstance(binding, dict)
            or set(binding) != {"root", "control_root", "manifest_path", "manifest_sha256", "project_prefix"}
            or any(not isinstance(value, str) or not value for value in binding.values())
            or not isinstance(paths, list) or not 0 < len(paths) <= 32
            or any(not isinstance(path, str) or not path for path in paths)):
        return False
    return request["start_by"] > time.monotonic()


def _capture(connection, request, read_fd, write_fd, indexed_draft):
    try:
        os.setpgid(0, 0)
        signal.set_wakeup_fd(-1)
        signal.signal(signal.SIGTERM, signal.SIG_DFL)
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        connection.close()
        os.close(read_fd)
        if request["kind"] == "indexed_lifecycle":
            result = lifecycle_run(request["request"], indexed_draft=indexed_draft)
        else:
            result = _ticket_delta(request["binding"], request["reuse"], request["paths"], capture_ticket_delta)
        with os.fdopen(write_fd, "w") as out:
            json.dump(result, out, ensure_ascii=False, separators=(",", ":"))
    finally:
        os._exit(0)


def _collect(connection, read_fd, stop):
    chunks = []
    while True:
        ready, _, _ = select.select([connection, read_fd, stop], [], [])
        # Closing the client's write side abandons just this capture.
        if stop in ready or connection in ready:
            return None
        chunk = os.read(read_fd, 65536)
        if not chunk:
            return b"".join(chunks)
        chunks.append(chunk)


def _job(connection, request, stop, indexed_draft):
    read_fd, write_fd = os.pipe()
    pid = None
    try:
        pid = os.fork()
        if pid == 0:
            _capture(connection, request, read_fd, write_fd, indexed_draft)
        os.setpgid(pid, pid)
        os.close(write_fd)
        write_fd = None
        _send(connection, {"accepted": True, "pid": pid})
        data = _collect(connection, read_fd, stop)
        if data is None:
            return None
        _, status = os.waitpid(pid, 0)
        pid = None
        return json.loads(data) if status == 0 else None
    finally:
        os.close(read_fd)
        if write_fd is not None:
            os.close(write_fd)
        if pid is not None:
            try:
                os.killpg(pid, signal.SIGKILL)
            except ProcessLookupError:
                os.kill(pid, signal.SIGKILL)
            os.waitpid(pid, 0)


def _send(connection, value):
    connection.sendall(json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode() + b"\n")


def _serve(connection, stop, indexed_draft):
    connection.settimeout(5)
    try:
        with connection.makefile("rb") as source:
            line = source.readline(1024 * 1024 + 1)
        if len(line) > 1024 * 1024 or not line.endswith(b"\n"):
            raise ValueError("Invalid request")
        request = json.loads(line)
        if request == {"kind": "health"}:
            _send(connection, {"ready": True, "pid": os.getpid()})
        elif _admit(request):
            try:
                result = _job(connection, request, stop, indexed_draft)
            except (OSError, RuntimeError, TypeError, ValueError):
                result = None
            _send(connection, {"result": result})
        else:
            _send(connection, {"accepted": False})
    except (OSError, ValueError, UnicodeError):
        pass


def _wake_on_signal(_signal, _frame):
    pass


def main():
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__shared import indexed_draft_runner

    indexed_draft = indexed_draft_runner()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--socket", required=True)
    args = parser.parse_args()
    path = Path(args.socket)
    parent = path.parent.stat()
    if (not path.is_absolute() or not stat.S_ISDIR(parent.st_mode) or parent.st_uid != os.getuid()
            or parent.st_mode & 0o077 or path.parent.resolve() != path.parent):
        raise ValueError("Socket must be in a private canonical runtime directory")
    stop, wake = socket.socketpair()
    with stop, wake, socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as server:
        server.bind(str(path))
        try:
            wake.setblocking(False)
            signal.set_wakeup_fd(wake.fileno())
            signal.signal(signal.SIGTERM, _wake_on_signal)
            signal.signal(signal.SIGINT, _wake_on_signal)
            os.chmod(path, 0o600)
            server.listen()
            while stop not in select.select([stop, server], [], [])[0]:
                connection, _ = server.accept()
                with connection:
                    _serve(connection, stop, indexed_draft)
        finally:
            signal.set_wakeup_fd(-1)
            path.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
