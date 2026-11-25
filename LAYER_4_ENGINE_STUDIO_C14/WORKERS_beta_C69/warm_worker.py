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
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, ValidationError

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    capture_ticket_delta,
)

from .native_refresh import _ReuseHint, _ticket_delta
from .lifecycle_worker import _validate_indexed, run as lifecycle_run
from .lifecycle_request import _Binding


class _Envelope(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    start_by: Any


class _TicketDelta(_Envelope):
    kind: Literal["ticket_delta"]
    binding: _Binding
    reuse: _ReuseHint
    paths: list[Annotated[str, Field(min_length=1)]] = Field(min_length=1, max_length=32)


class _IndexedLifecycle(_Envelope):
    kind: Literal["indexed_lifecycle"]
    request: Any


_REQUEST = TypeAdapter(Annotated[_TicketDelta | _IndexedLifecycle, Field(discriminator="kind")])


def _within_start_window(start_by):
    if start_by is None:
        return os.getenv("ANECHOIC_TEST_IMAGE_DEADLINES") == "0"
    return (type(start_by) in (int, float) and math.isfinite(start_by)
            and start_by > time.monotonic())


def _admit(request):
    if (not isinstance(request, dict)
            or not _within_start_window(request.get("start_by"))):
        return None
    try:
        admitted = _REQUEST.validate_python(request)
        if isinstance(admitted, _IndexedLifecycle):
            admitted.request = _validate_indexed(admitted.request)
    except (ValidationError, TypeError, ValueError, KeyError):
        return None
    return admitted if _within_start_window(admitted.start_by) else None


def _capture(connection, request, read_fd, write_fd, indexed_draft):
    try:
        os.setpgid(0, 0)
        signal.set_wakeup_fd(-1)
        signal.signal(signal.SIGTERM, signal.SIG_DFL)
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        connection.close()
        os.close(read_fd)
        if isinstance(request, _IndexedLifecycle):
            result = lifecycle_run(request.request, indexed_draft=indexed_draft)
        else:
            result = _ticket_delta(request.binding.model_dump(), request.reuse, request.paths, capture_ticket_delta)
        with os.fdopen(write_fd, "w") as out:
            json.dump(result, out, ensure_ascii=False, separators=(",", ":"))
    finally:
        os._exit(0)


def _collect(connection, read_fd, stop):
    chunks = []
    while True:
        ready, _, _ = select.select([connection, read_fd, stop], [], [])
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
        elif (admitted := _admit(request)) is not None:
            try:
                result = _job(connection, admitted, stop, indexed_draft)
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
