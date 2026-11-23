"""Keep packaged Beta Project peers independent of the transport processes."""

from contextlib import ExitStack
import signal
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Event


def _stop(process):
    if process.stdin is not None:
        process.stdin.close()
    elif process.poll() is None:
        process.terminate()
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()


class Child:
    def __init__(self, command, environment, *, parent_pipe=False, socket=None):
        self.command = command
        self.environment = environment
        self.parent_pipe = parent_pipe
        self.socket = socket
        self.process = None

    def ensure(self):
        if self.process is not None and self.process.poll() is None:
            return
        self.stop()
        self.process = subprocess.Popen(self.command, env=self.environment,
                                        stdin=subprocess.PIPE if self.parent_pipe else subprocess.DEVNULL)

    def stop(self):
        if self.process is not None:
            _stop(self.process)
            self.process = None
            if self.socket is not None:
                self.socket.unlink(missing_ok=True)


def _service(name, path, settings):
    return [sys.executable, "-B", "-P", "-m", "WORKBENCH_BACKEND_beta_C70." + name,
            "--socket", str(path), "--host-settings", settings]


def _run_services(owner, backend, mcp, ready, stopping, *, restart_owner):
    admitted = serving = False
    owner.ensure()
    while not stopping.is_set():
        owner_exited = owner.process.poll() is not None
        if not owner_exited and ready():
            backend.ensure()
            mcp.ensure()
            admitted = serving = True
        elif restart_owner and serving:
            mcp.stop()
            backend.stop()
            serving = False
        if owner_exited:
            if not restart_owner or not admitted:
                return owner.process.returncode or 1
            if stopping.wait(0.5):
                break
            owner.ensure()
        stopping.wait(0.25)
    return 0


def _supervise(command, environment, configure, *, restart_owner=False):
    stopping = Event()
    signals = (signal.SIGINT, signal.SIGTERM)
    previous = {sig: signal.signal(sig, lambda *_: stopping.set()) for sig in signals}
    try:
        with ExitStack() as stack:
            directory = Path(stack.enter_context(TemporaryDirectory(prefix="ane-beta-host-", dir="/tmp"))).resolve()
            owner, backend, ready = configure(directory)
            if stopping.is_set():
                return 0
            mcp = Child(command, {**environment, "ANECHOIC_BETA_BACKEND_SOCKET": str(backend.socket)})
            for service in (owner, backend, mcp):
                stack.callback(service.stop)
            return _run_services(owner, backend, mcp, ready, stopping, restart_owner=restart_owner)
    finally:
        for sig, handler in previous.items():
            signal.signal(sig, handler)


def supervise(command, environment, settings):
    def configure(directory):
        owner_socket, backend_socket = directory / "owner.sock", directory / "api.sock"
        owner = Child(_service("shared_peer_owner", owner_socket, settings), environment, parent_pipe=True)
        backend = Child(_service("shared_runtime", backend_socket, settings)
                        + ["--peer-owner-socket", str(owner_socket)], environment,
                        parent_pipe=True, socket=backend_socket)
        return owner, backend, owner_socket.is_socket

    return _supervise(command, environment, configure)


def supervise_project(command, environment, project_root):
    from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import beta_runtime_arguments, select_runtime_project

    def configure(directory):
        selection = select_runtime_project(project_root, environment.get("ANECHOIC_CONTROL_ROOT"),
                                           instance_id=environment.get("ANECHOIC_PROJECT_INSTANCE_ID"),
                                           host_root=environment.get("ANECHOIC_HOST_PROJECT_ROOT"))
        socket = directory / "api.sock"
        arguments = [sys.executable, "-B", "-P", "-m", *beta_runtime_arguments(selection, socket)]
        owner = Child(arguments + ["--role", "peer-owner"], environment, parent_pipe=True)
        backend = Child(arguments + ["--role", "api"], environment, parent_pipe=True, socket=socket)
        return owner, backend, (directory / "peers.ready").is_file

    return _supervise(command, environment, configure, restart_owner=True)
