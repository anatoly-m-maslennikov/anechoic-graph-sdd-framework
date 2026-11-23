"""Own one optional, private C69 worker for the lifetime of a C70 runtime."""

from contextlib import contextmanager
import json
import os
from pathlib import Path
import socket
import signal
import subprocess
import sys
from tempfile import TemporaryDirectory
from time import monotonic, sleep

ENGINE = Path(__file__).resolve().parents[1]


def _stop(peer):
    for sig in (signal.SIGTERM, signal.SIGKILL):
        try:
            os.killpg(peer.pid, sig)
        except ProcessLookupError:
            pass
        try:
            peer.wait(timeout=5)
        except subprocess.TimeoutExpired:
            continue
        break
    else:
        peer.wait()


def _healthy(path, pid, deadline):
    """Return None when the readiness probe could not complete."""
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
        health = json.loads(response.split(b"\n", 1)[0])
        return health.get("ready") is True and health.get("pid") == pid
    except OSError:
        return None
    except (ValueError, TypeError, AttributeError):
        return False


@contextmanager
def open_warm_worker(*, stop=None):
    """Yield (socket, load seconds), or None when the optional worker fails."""
    if stop is not None and stop():
        yield None
        return
    with TemporaryDirectory(prefix="anechoic-beta-worker-", dir="/tmp") as tmp:
        path = Path(tmp).resolve() / "worker.sock"
        environment = {key: value for key, value in os.environ.items() if key != "PYTHONHOME"}
        environment["PYTHONPATH"] = str(ENGINE)
        worker = None
        started = monotonic()
        try:
            ready = False
            try:
                worker = subprocess.Popen(
                    [sys.executable, "-B", "-P", "-m", "WORKERS_beta_C69.warm_worker", "--socket", str(path)],
                    cwd=ENGINE, env=environment, stdin=subprocess.DEVNULL, stdout=sys.stderr, start_new_session=True,
                )
                deadline = started + 15
                bounded = os.getenv("ANECHOIC_TEST_IMAGE_DEADLINES") != "0"
                while worker.poll() is None and (stop is None or not stop()):
                    now = monotonic()
                    if bounded and now >= deadline:
                        break
                    health = _healthy(path, worker.pid,
                                      deadline if bounded else now + 0.5)
                    ready = health is True
                    if ready or (not bounded and health is False):
                        break
                    sleep(0.05)
            except OSError:
                pass
            if not ready:
                if stop is None or not stop():
                    print("Beta warm worker unavailable; using cold worker startup", file=sys.stderr)
                if worker is not None:
                    _stop(worker)
                    worker = None
            yield (str(path), monotonic() - started) if ready else None
        finally:
            if worker is not None:
                _stop(worker)
