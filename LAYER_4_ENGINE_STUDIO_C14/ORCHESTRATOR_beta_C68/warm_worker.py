"""Private client for the optional warm Worker broker."""
import json
import os
import socket
import time

from .generation import parse_worker_result

MAX_REPLY_BYTES = 16 * 1024 * 1024


class WarmCapture:
    def __init__(self, socket, pid):
        self.socket = socket
        self.pid = pid

    def alive(self):
        try:
            return os.getpgid(self.pid) == self.pid
        except ProcessLookupError:
            return False

    def cancel(self):
        self.socket.shutdown(socket.SHUT_WR)


def _line(sock, limit, *, deadline=None):
    data = bytearray()
    while len(data) <= limit:
        if deadline is not None:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError("Worker start deadline exceeded")
            sock.settimeout(remaining)
        chunk = sock.recv(1 if deadline is not None else min(65536, limit + 1 - len(data)))
        if not chunk:
            raise ValueError("Worker closed the connection")
        data.extend(chunk)
        if b"\n" in data:
            line, extra = data.split(b"\n", 1)
            if extra or len(line) > limit:
                raise ValueError("Invalid worker reply")
            return json.loads(line)
    raise ValueError("Worker reply too large")


def request(socket_path, load_seconds, binding, reuse, paths, register):
    """Return the worker payload, or None when the broker cannot serve it."""
    try:
        start_by = time.monotonic() + load_seconds
        payload = {"kind": "ticket_delta", "start_by": start_by,
                   "binding": binding, "reuse": reuse, "paths": paths}
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
            sock.settimeout(max(0.0, start_by - time.monotonic()))
            sock.connect(socket_path)
            sock.sendall(json.dumps(payload, allow_nan=False).encode() + b"\n")
            ack = _line(sock, 1024, deadline=start_by)
            if not isinstance(ack, dict) or set(ack) != {"accepted", "pid"}:
                return None
            pid = ack["pid"]
            if ack["accepted"] is not True or type(pid) is not int or not 0 < pid < 2**31:
                return None
            sock.settimeout(None)
            if not register(WarmCapture(sock, pid)):
                return None
            reply = _line(sock, MAX_REPLY_BYTES)
            if not isinstance(reply, dict) or set(reply) != {"result"}:
                return None
            return reply["result"]
    except (OSError, ValueError, TypeError, OverflowError):
        return None


def validated_result(socket_path, load_seconds, binding, reuse, paths, register):
    result = request(socket_path, load_seconds, binding, reuse, paths, register)
    if result is None:
        return None
    try:
        result = parse_worker_result(json.dumps(result), reuse, paths)
        return result if "base_generation" in result else None
    except (ValueError, TypeError, KeyError):
        return None
