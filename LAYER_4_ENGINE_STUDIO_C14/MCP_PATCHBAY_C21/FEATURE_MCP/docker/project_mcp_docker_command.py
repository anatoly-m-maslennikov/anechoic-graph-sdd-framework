"""Bounded Docker command execution for the Project MCP backend."""

import os
import selectors
import subprocess
import time
from typing import Mapping

_MAX_STDOUT = 64 * 1024


class BackendError(RuntimeError):
    """Safe lifecycle failure with command diagnostics discarded."""

    def __init__(self, code: str = "DOCKER_START_FAILED") -> None:
        self.code = code
        super().__init__(code)


def _cleanup(process, selector):
    selector.close()
    if process.stdout is not None:
        process.stdout.close()
    if process.poll() is None:
        try:
            process.kill()
            process.wait(timeout=1)
        except (OSError, subprocess.TimeoutExpired):
            pass


def _bounded_run(
    argv: list[str], *, timeout: float, env: Mapping[str, str] | None = None
) -> str:
    """Run a finite Docker command with bounded stdout and no stderr."""
    process = subprocess.Popen(
        argv, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL, env=dict(env) if env else None, shell=False,
    )
    selector = selectors.DefaultSelector()
    output = bytearray()
    deadline = time.monotonic() + timeout
    try:
        if process.stdout is None:
            raise BackendError()
        selector.register(process.stdout, selectors.EVENT_READ)
        while selector.get_map():
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise BackendError()
            for key, _ in selector.select(remaining):
                chunk = os.read(
                    key.fileobj.fileno(),
                    min(65536, _MAX_STDOUT + 1 - len(output)),
                )
                if not chunk:
                    selector.unregister(key.fileobj)
                    continue
                output.extend(chunk)
                if len(output) > _MAX_STDOUT:
                    raise BackendError()
        remaining = deadline - time.monotonic()
        if remaining <= 0 or process.wait(timeout=remaining) != 0:
            raise BackendError()
        return output.decode("utf-8")
    except (
        OSError, UnicodeError, subprocess.TimeoutExpired, ValueError
    ) as error:
        if isinstance(error, BackendError):
            raise
        raise BackendError() from None
    finally:
        _cleanup(process, selector)

