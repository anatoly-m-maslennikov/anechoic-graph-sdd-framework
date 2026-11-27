"""Bounded Docker CLI execution for runtime-image admission."""


from __future__ import annotations

import os
import selectors
import subprocess
import time


MAX_OUTPUT = 4 * 1024 * 1024
_DOCKER_ENVIRONMENT = frozenset(
    {
        "HOME",
        "PATH",
        "DOCKER_HOST",
        "DOCKER_CONTEXT",
        "DOCKER_CONFIG",
        "XDG_RUNTIME_DIR",
        "TMPDIR",
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "ALL_PROXY",
        "NO_PROXY",
        "http_proxy",
        "https_proxy",
        "all_proxy",
        "no_proxy",
    }
)


def docker_client_environment(*, buildx_config=None):
    environment = {
        name: value
        for name, value in os.environ.items()
        if name in _DOCKER_ENVIRONMENT
    }
    if buildx_config is not None:
        environment["BUILDX_CONFIG"] = str(buildx_config)
    return environment


def _read_stdout(selector, max_output, remaining):
    output = bytearray()
    while selector.get_map():
        for key, _events in selector.select(remaining()):
            chunk = os.read(
                key.fileobj.fileno(), min(65536, max_output + 1 - len(output))
            )
            if not chunk:
                selector.unregister(key.fileobj)
                continue
            output.extend(chunk)
            if len(output) > max_output:
                raise ValueError(
                    "Docker image stdout exceeded its bounded read"
                )
    return output


def bounded_run(argv, *, cwd, timeout, capture_stdout=True, max_output=MAX_OUTPUT,
                buildx_config=None, report_stderr=False):
    """Read a finite stdout prefix without retaining stderr or build logs."""
    deadline = None if timeout is None else time.monotonic() + timeout

    def remaining():
        if deadline is None:
            return None
        remaining_seconds = deadline - time.monotonic()
        if remaining_seconds <= 0:
            raise subprocess.TimeoutExpired(argv, timeout)
        return remaining_seconds

    environment = docker_client_environment(buildx_config=buildx_config)
    process = subprocess.Popen(
        argv,
        cwd=cwd,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE if capture_stdout else subprocess.DEVNULL,
        stderr=None if report_stderr else subprocess.DEVNULL,
        shell=False,
        env=environment,
    )
    selector = None
    output = bytearray()
    try:
        if capture_stdout:
            selector = selectors.DefaultSelector()
            selector.register(process.stdout, selectors.EVENT_READ)
            output = _read_stdout(selector, max_output, remaining)
        returncode = process.wait(timeout=remaining())
        return subprocess.CompletedProcess(
            argv, returncode, output.decode("utf-8"), ""
        )
    finally:
        if selector is not None:
            selector.close()
        if process.stdout is not None:
            process.stdout.close()
        if process.poll() is None:
            try:
                process.kill()
                process.wait(timeout=1)
            except OSError, subprocess.TimeoutExpired:
                pass
