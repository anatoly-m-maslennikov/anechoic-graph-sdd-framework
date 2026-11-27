"""Own the optional warm Worker for the lifetime of a peer owner."""

from contextlib import contextmanager
import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
from tempfile import TemporaryDirectory
from time import monotonic, sleep

from pydantic import BaseModel, ConfigDict

from .jobs import ENGINE, operation_timeout


class _Health(BaseModel):
    model_config = ConfigDict(strict=True)

    ready: bool
    pid: int


def process_environment():
    environment = {
        key: value for key, value in os.environ.items() if key != "PYTHONHOME"
    }
    environment["PYTHONPATH"] = str(ENGINE)
    return environment


def stop_process(process):
    for signum in (signal.SIGTERM, signal.SIGKILL):
        try:
            os.killpg(process.pid, signum)
        except ProcessLookupError:
            pass
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            continue
        return
    process.wait()


def _healthy(path, pid, deadline):
    """Return None when the probe cannot complete and False for a bad reply."""
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
            client.settimeout(min(0.5, max(0.001, deadline - monotonic())))
            client.connect(str(path))
            client.sendall(b'{"kind":"health"}\n')
            response = b""
            while b"\n" not in response and len(response) <= 65536:
                remaining = deadline - monotonic()
                if remaining <= 0:
                    return None
                client.settimeout(min(0.5, remaining))
                chunk = client.recv(4096)
                if not chunk:
                    break
                response += chunk
        health = _Health.model_validate_json(response.split(b"\n", 1)[0])
        return health.ready and health.pid == pid
    except OSError:
        return None
    except ValueError:
        return False


def _ready(worker, path, started, stop):
    startup_limit = operation_timeout(15)
    while worker.poll() is None and (stop is None or not stop()):
        now = monotonic()
        deadline = (
            now + 0.5 if startup_limit is None else started + startup_limit
        )
        if now >= deadline:
            break
        health = _healthy(path, worker.pid, deadline)
        if health is True:
            return True
        if startup_limit is None and health is False:
            break
        sleep(0.05)
    return False


@contextmanager
def open_warm_worker(*, stop=None):
    """Yield the Worker's socket and load time, or None for cold fallback."""
    if stop is not None and stop():
        yield None
        return
    with TemporaryDirectory(prefix="anechoic-beta-worker-", dir="/tmp") as tmp:
        path = Path(tmp).resolve() / "worker.sock"
        worker, ready = None, False
        started = monotonic()
        try:
            try:
                worker = subprocess.Popen(
                    [
                        sys.executable,
                        "-B",
                        "-P",
                        "-m",
                        "WORKERS_beta_C69.warm_worker",
                        "--socket",
                        str(path),
                    ],
                    cwd=ENGINE,
                    env=process_environment(),
                    stdin=subprocess.DEVNULL,
                    stdout=sys.stderr,
                    start_new_session=True,
                )
                ready = _ready(worker, path, started, stop)
            except OSError:
                pass
            if not ready:
                if stop is None or not stop():
                    print(
                        "Beta warm worker unavailable; using cold worker startup",
                        file=sys.stderr,
                    )
                if worker is not None:
                    stop_process(worker)
                    worker = None
            yield (str(path), monotonic() - started) if ready else None
        finally:
            if worker is not None:
                stop_process(worker)
