"""Call the Backend's Project admission service over a private pipe."""

from contextlib import contextmanager
from dataclasses import dataclass, field
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import threading

from MCP_PATCHBAY_C21.FEATURE_MCP.runtime_stack import runtime_stack

class ProjectAdmissionError(ValueError):
    """The Backend refused a Project binding."""


@dataclass(frozen=True)
class ProjectBinding:
    root: Path
    control_root: Path
    control_relative: Path
    instance_id: str
    project_name: str
    project_prefix: str
    manifest_path: Path
    manifest_ref: str
    manifest_sha256: str
    parameters: dict[str, object] = field(default_factory=dict)
    host_root: Path | None = None
    tool_blacklist: tuple[str, ...] = ()
    release_workflows_enabled: bool = False

    @property
    def launcher_state(self) -> Path:
        return self.root / ".anechoic_runtime/runtime/project_mcp" / self.instance_id

    @property
    def compose_project(self) -> str:
        return "anechoic-mcp-" + self.instance_id[:24]

_MODULE = "IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.project_admission"
_BETA_MODULE = "FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_MODEL_VALIDATION.project_admission__pub"
_PATH_FIELDS = ("root", "control_root", "control_relative", "manifest_path")
_TEXT_FIELDS = ("instance_id", "project_name", "project_prefix", "manifest_ref", "manifest_sha256")


def _selection(value):
    keys = set(_PATH_FIELDS + _TEXT_FIELDS + ("host_root", "parameters", "tool_blacklist", "release_workflows_enabled"))
    if (not isinstance(value, dict) or set(value) != keys
            or any(not isinstance(value[key], str) for key in _PATH_FIELDS + _TEXT_FIELDS)
            or not isinstance(value["parameters"], dict)
            or not isinstance(value["tool_blacklist"], list)
            or any(not isinstance(item, str) for item in value["tool_blacklist"])
            or type(value["release_workflows_enabled"]) is not bool
            or (value["host_root"] is not None and not isinstance(value["host_root"], str))):
        raise RuntimeError("Invalid Project admission response")
    data = dict(value)
    for key in _PATH_FIELDS:
        data[key] = Path(data[key])
    if data["host_root"] is not None:
        data["host_root"] = Path(data["host_root"])
    data["tool_blacklist"] = tuple(data["tool_blacklist"])
    return ProjectBinding(**data)


class _AdmissionClient:
    def __init__(self, connection, responses):
        self._connection = connection
        self._responses = responses
        self._lock = threading.Lock()

    def interrupt(self):
        try:
            self._connection.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass

    def __call__(self, project_root, control_root=None, *, instance_id=None, host_root=None):
        request = {"project_root": str(project_root), "control_root": str(control_root) if control_root is not None else None,
                   "instance_id": instance_id, "host_root": str(host_root) if host_root is not None else None}
        with self._lock:
            try:
                self._connection.sendall(json.dumps(request).encode("utf-8") + b"\n")
                response = json.loads(self._responses.readline())
            except (OSError, UnicodeError, json.JSONDecodeError) as error:
                self._responses.close()
                self._connection.close()
                raise RuntimeError("Project admission service unavailable") from error
        if isinstance(response, dict) and set(response) == {"result"}:
            return _selection(response["result"])
        if isinstance(response, dict) and set(response) == {"error"}:
            error = response["error"]
            if (isinstance(error, dict) and set(error) == {"code", "message"}
                    and error["code"] == "project_selection_error" and isinstance(error["message"], str)):
                raise ProjectAdmissionError(error["message"])
        raise RuntimeError("Invalid Project admission response")

def _start(connection):
    engine = Path(__file__).resolve().parents[2]
    root = engine.parent
    environment = {**{k: v for k, v in os.environ.items() if k != "PYTHONHOME"}, "PYTHONPATH": str(engine)}
    module = _BETA_MODULE if runtime_stack() == "beta" else _MODULE
    return subprocess.Popen([sys.executable, "-B", "-P", "-m", module], cwd=root, env=environment,
                            stdin=connection, stdout=connection)


def _close(process):
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()


@contextmanager
def project_admission():
    parent, child = socket.socketpair()
    try:
        if os.getenv("ANECHOIC_TEST_IMAGE_DEADLINES") != "0":
            parent.settimeout(90)
        process = _start(child)
        child.close()
        try:
            with parent.makefile("rb") as responses:
                yield _AdmissionClient(parent, responses)
        finally:
            parent.close()
            _close(process)
    finally:
        parent.close()
        child.close()


def select_runtime_project(project_root, control_root=None, *, instance_id=None, host_root=None):
    """Return one native Project with an active Project Manifest."""
    with project_admission() as select:
        return select(project_root, control_root, instance_id=instance_id, host_root=host_root)
