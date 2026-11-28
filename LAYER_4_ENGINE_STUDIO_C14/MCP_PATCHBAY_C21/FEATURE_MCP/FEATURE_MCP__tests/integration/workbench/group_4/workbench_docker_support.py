"""Shared requests and liveness checks for disposable test images."""

from contextlib import AsyncExitStack, asynccontextmanager
import atexit
import json
import os
import signal
import subprocess
import tempfile
from time import monotonic, sleep
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import httpx2
from mcp.client.streamable_http import streamable_http_client

IMAGE_DEADLINES = "ANECHOIC_TEST_IMAGE_DEADLINES"


def image_deadline_mode(environment) -> str:
    return "0" if environment.get(IMAGE_DEADLINES, "0") == "0" else "1"


def image_timeout(seconds: float) -> float | None:
    return seconds if image_deadline_mode(os.environ) == "1" else None


def docker_deadline_env() -> str:
    return f"{IMAGE_DEADLINES}={image_deadline_mode(os.environ)}"


def defer_container_cleanup(register, container: str) -> None:
    def remove():
        result = subprocess.run(
            ["docker", "container", "rm", "-f", container],
            capture_output=True,
            text=True,
            timeout=image_timeout(30),
        )
        if "No such container:" not in result.stderr:
            result.check_returncode()

    def cleanup():
        atexit.unregister(remove)
        remove()

    atexit.register(remove)
    register(cleanup)


def assert_container_running(container: str) -> None:
    running = subprocess.check_output(
        ["docker", "inspect", "--format", "{{.State.Running}}", container],
        text=True,
        timeout=image_timeout(10),
    ).strip()
    if running != "true":
        raise RuntimeError(f"Test container exited: {container} ({running})")


def observing(container: str, deadline: float) -> bool:
    if image_deadline_mode(os.environ) == "1":
        return monotonic() < deadline
    assert_container_running(container)
    return True


@asynccontextmanager
async def image_mcp_transport(endpoint: str):
    async with AsyncExitStack() as stack:
        http = None
        if image_deadline_mode(os.environ) == "0":
            http = await stack.enter_async_context(
                httpx2.AsyncClient(timeout=None)
            )
        yield await stack.enter_async_context(
            streamable_http_client(endpoint, http_client=http)
        )


def run_browser(container, command, *, cwd, env, bounded_timeout=120):
    if image_deadline_mode(env) == "1":
        return subprocess.run(
            command,
            cwd=cwd,
            env=env,
            capture_output=True,
            text=True,
            timeout=bounded_timeout,
        )
    with (
        tempfile.TemporaryFile(mode="w+t") as stdout,
        tempfile.TemporaryFile(mode="w+t") as stderr,
    ):
        with subprocess.Popen(
            command, cwd=cwd, env=env, stdout=stdout, stderr=stderr
        ) as process:
            try:
                while process.poll() is None:
                    assert_container_running(container)
                    sleep(0.5)
            except BaseException:
                process.send_signal(signal.SIGINT)
                try:
                    process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
                raise
            stdout.seek(0)
            stderr.seek(0)
            return subprocess.CompletedProcess(
                command, process.returncode, stdout.read(), stderr.read()
            )


def request(
    url: str, *, method: str = "GET", payload: dict | None = None
) -> tuple[int, dict | str]:
    body = None if payload is None else json.dumps(payload).encode()
    target = Request(
        url,
        data=body,
        method=method,
        headers={"content-type": "application/json"},
    )
    try:
        with urlopen(target, timeout=image_timeout(60)) as response:  # noqa: S310 -- loopback test server
            data = response.read().decode()
            return (
                response.status,
                json.loads(data)
                if response.headers.get_content_type() == "application/json"
                else data,
            )
    except HTTPError as error:
        with error:
            data = error.read().decode()
        return error.code, json.loads(data) if data else {}
