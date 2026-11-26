"""Keep packaged Beta Project peers independent of the transport processes."""

from contextlib import ExitStack
from fcntl import LOCK_EX, flock
from hashlib import file_digest
import json
import os
import signal
import stat
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Event
from time import monotonic, sleep

from pydantic import BaseModel, ConfigDict


def _stop(process, *, graceful=False):
    if process.stdin is not None:
        process.stdin.close()
    elif process.poll() is None:
        process.terminate()
    try:
        process.wait(timeout=None if graceful else 10)
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

    def stop(self, *, graceful=False):
        if self.process is not None:
            _stop(self.process, graceful=graceful)
            self.process = None
            if self.socket is not None:
                self.socket.unlink(missing_ok=True)


def _service(module, path, settings):
    return [sys.executable, "-B", "-P", "-m", module,
            "--socket", str(path), "--host-settings", settings]


def _manifest_version(path):
    try:
        return _file_version(path.lstat())
    except OSError:
        return None


def _file_version(info):
    return info.st_dev, info.st_ino, info.st_mode, info.st_size, info.st_mtime_ns, info.st_ctime_ns


def _sealed_version(selection):
    path = selection.manifest_path
    version = _manifest_version(path)
    if version is None or not stat.S_ISREG(version[2]):
        raise ValueError("The selected Project Manifest is unavailable")
    flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK
    with os.fdopen(os.open(path, flags), "rb") as stream:
        if _file_version(os.fstat(stream.fileno())) != version:
            raise ValueError("The Project Manifest changed during admission")
        digest = file_digest(stream, "sha256").hexdigest()
    if digest != selection.manifest_sha256 or version != _manifest_version(path):
        raise ValueError("The Project Manifest changed during admission")
    return version



class _LifecycleHealth(BaseModel):
    model_config = ConfigDict(strict=True, extra="ignore")

    instance_id: str
    lifecycle_active: bool

def _lifecycle_idle(owner, jobs_socket, instance_id):
    if owner.process is None or owner.process.poll() is not None:
        return True
    import httpx2

    try:
        with httpx2.Client(transport=httpx2.HTTPTransport(uds=str(jobs_socket)),
                           base_url="http://private", timeout=0.5, trust_env=False) as client:
            response = client.get("/health")
            if response.status_code != 200:
                return False
            value = _LifecycleHealth.model_validate(response.json()["result"])
            return value.instance_id == instance_id and value.lifecycle_active is False
    except (httpx2.HTTPError, ValueError, KeyError, TypeError):
        return False


class ManifestReload:
    def __init__(self, select, arguments, directory):
        self.select = select
        self.arguments = arguments
        self.directory = directory
        self.gate = directory / "api.draining"
        self.transport = self.gate.with_suffix(".transport")
        self.transport.touch(mode=0o600, exist_ok=False)
        self.selection = self.version = None
        self.retry_at = 0
        self.rejected = ()

    def admit_initial(self, owner, backend):
        try:
            selected = self.select()
            version = _sealed_version(selected)
            commands = self.arguments(selected, backend.socket)
        except (AttributeError, OSError, TypeError, ValueError):
            if not self.gate.exists():
                self.gate.write_text("project_manifest_invalid", encoding="ascii")
                print("WARNING: Project Manifest is missing or invalid", file=sys.stderr, flush=True)
            self.retry_at = monotonic() + 1
            return False
        self.configure(selected, version, owner, backend, commands)
        self.gate.unlink(missing_ok=True)
        return True

    def configure(self, selected, version, owner, backend, commands):
        owner.command, backend.command = commands
        backend.environment = {**backend.environment, "ANECHOIC_BETA_DIRECT_MANIFEST": json.dumps({
            "path": str(selected.manifest_path), "version": version, "gate": str(self.gate),
        })}
        self.selection, self.version = selected, version

    def children(self, environment):
        socket = self.directory / "api.sock"
        owner = Child([], environment, parent_pipe=True)
        backend = Child([], environment, parent_pipe=True, socket=socket)
        self.admit_initial(owner, backend)
        return owner, backend

    def refresh(self, owner, backend, mcp, stopping):
        if self.selection is None:
            if monotonic() < self.retry_at or not self.admit_initial(owner, backend):
                return False
            if not stopping.is_set():
                owner.ensure()
            return True
        version = _manifest_version(self.selection.manifest_path)
        if version == self.version and not self.gate.exists():
            return True
        if version == self.rejected:
            return False
        self.gate.write_text("project_manifest_reloading", encoding="ascii")
        try:
            selected = self.select()
            if (selected.manifest_path, selected.instance_id) != (self.selection.manifest_path,
                                                                  self.selection.instance_id):
                raise ValueError("The selected Project Manifest binding changed")
            sealed = _sealed_version(selected)
            commands = self.arguments(selected, backend.socket)
        except (AttributeError, OSError, RuntimeError, TypeError, ValueError) as error:
            self.rejected = version
            self.gate.write_text("project_manifest_invalid", encoding="ascii")
            print(f"Project Manifest reload refused: {error}", file=sys.stderr, flush=True)
            return False
        with self.transport.open("rb") as lock:
            flock(lock, LOCK_EX)
            backend.stop(graceful=True)
            mcp.stop(graceful=True)
        self.wait_for_lifecycle(owner)
        owner.stop(graceful=True)
        if stopping.is_set() or sealed != _manifest_version(selected.manifest_path):
            return False
        self.configure(selected, sealed, owner, backend, commands)
        self.rejected = ()
        self.gate.unlink()
        owner.ensure()
        return True

    def wait_for_lifecycle(self, owner):
        if not _lifecycle_idle(owner, self.directory / "jobs.sock", self.selection.instance_id):
            print("Waiting for the Project lifecycle before Manifest reload", file=sys.stderr, flush=True)
            while not _lifecycle_idle(owner, self.directory / "jobs.sock", self.selection.instance_id):
                sleep(0.25)


def _run_services(owner, backend, mcp, ready, stopping, *, restart_owner, reload=None, diagnostics=None):
    admitted = serving = False
    if owner.command:
        owner.ensure()
    while not stopping.is_set():
        if reload is not None and not reload.refresh(owner, backend, mcp, stopping):
            if diagnostics is not None and (mcp.process is None or mcp.process.poll() is not None):
                diagnostics.ensure()
            stopping.wait(0.25)
            continue
        if stopping.is_set():
            break
        owner_exited = owner.process.poll() is not None
        if not owner_exited and ready():
            backend.ensure()
            if diagnostics is not None and diagnostics.process is not None:
                if not backend.socket.is_socket():
                    stopping.wait(0.25)
                    continue
                diagnostics.stop()
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
            owner, backend, ready, reload = configure(directory)
            if stopping.is_set():
                return 0
            mcp_environment = {**environment, "ANECHOIC_BETA_BACKEND_SOCKET": str(backend.socket)}
            diagnostics = None
            if reload is not None:
                mcp_environment["ANECHOIC_BETA_DIRECT_TRANSPORT_GATE"] = str(reload.gate)
                diagnostics = Child(command, {**mcp_environment, "ANECHOIC_BETA_DIRECT_DIAGNOSTICS": "1"})
                stack.callback(diagnostics.stop)
            mcp = Child(command, mcp_environment)
            for service in (owner, backend, mcp):
                stack.callback(service.stop)
            return _run_services(owner, backend, mcp, ready, stopping, restart_owner=restart_owner,
                                 reload=reload, diagnostics=diagnostics)
    finally:
        for sig, handler in previous.items():
            signal.signal(sig, handler)


def supervise(command, environment, settings):
    def configure(directory):
        owner_socket, backend_socket = directory / "owner.sock", directory / "api.sock"
        owner_module = "ORCHESTRATOR_beta_C68.shared_peer_owner"
        owner = Child(_service(owner_module, owner_socket, settings),
                      environment, parent_pipe=True)
        module = "API_MIXER_beta_C91.shared_runtime"
        backend = Child(_service(module, backend_socket, settings)
                        + ["--peer-owner-socket", str(owner_socket)], environment,
                        parent_pipe=True, socket=backend_socket)
        return owner, backend, owner_socket.is_socket, None

    return _supervise(command, environment, configure)


def _direct_arguments(selection, socket):
    from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import beta_runtime_arguments

    module, *args = beta_runtime_arguments(selection, socket)
    owner = ["ORCHESTRATOR_beta_C68.project_peer_owner", *args]
    prefix = [sys.executable, "-B", "-P", "-m"]
    return [*prefix, *owner], [*prefix, module, *args, "--role", "api"]


def supervise_project(command, environment, project_root):
    from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import select_runtime_project

    def select():
        return select_runtime_project(project_root, environment.get("ANECHOIC_CONTROL_ROOT"),
                                      instance_id=environment.get("ANECHOIC_PROJECT_INSTANCE_ID"),
                                      host_root=environment.get("ANECHOIC_HOST_PROJECT_ROOT"))

    def configure(directory):
        reload = ManifestReload(select, _direct_arguments, directory)
        owner, backend = reload.children(environment)
        return owner, backend, (directory / "peers.ready").is_file, reload

    return _supervise(command, environment, configure, restart_owner=True)
