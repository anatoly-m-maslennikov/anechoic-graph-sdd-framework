"""Call the reviewed Project admission CLI over a bounded process."""

from dataclasses import dataclass
import json
import os
from pathlib import Path
import subprocess
import socket
from threading import Lock
import sys

_ENGINE = Path(__file__).resolve().parents[1]
_MODULE = "FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_MODEL_VALIDATION.project_admission__pub"


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
    parameters: dict
    host_root: Path | None
    tool_blacklist: tuple
    release_workflows_enabled: bool


def _selection(response):
    if isinstance(response, dict) and set(response) == {"error"}:
        error = response["error"]
        if (isinstance(error, dict) and set(error) == {"code", "message"}
                and error["code"] == "project_selection_error" and isinstance(error["message"], str)):
            raise ValueError(error["message"])
    if not isinstance(response, dict) or set(response) != {"result"} or not isinstance(response["result"], dict):
        raise RuntimeError("Invalid Project admission response")
    data = response["result"]
    paths = ("root", "control_root", "control_relative", "manifest_path")
    texts = ("instance_id", "project_name", "project_prefix", "manifest_ref", "manifest_sha256")
    if (set(data) != set(paths + texts + ("parameters", "host_root", "tool_blacklist", "release_workflows_enabled"))
            or any(not isinstance(data[key], str) for key in paths + texts)
            or not isinstance(data["parameters"], dict) or not isinstance(data["tool_blacklist"], list)
            or any(not isinstance(item, str) for item in data["tool_blacklist"])
            or type(data["release_workflows_enabled"]) is not bool
            or (data["host_root"] is not None and not isinstance(data["host_root"], str))):
        raise RuntimeError("Invalid Project admission response")
    for key in paths:
        data[key] = Path(data[key])
    if data["host_root"] is not None:
        data["host_root"] = Path(data["host_root"])
    data["tool_blacklist"] = tuple(data["tool_blacklist"])
    return ProjectBinding(**data)


class AdmissionClient:
    """Serialize requests through one private, bounded admission process."""

    def __init__(self):
        self._lock = Lock()
        self._connection = None
        self._responses = None
        self._process = None
        self._closed = False

    def _start(self):
        parent, child = socket.socketpair()
        try:
            parent.settimeout(90)
            env = {**{k: v for k, v in os.environ.items() if k != "PYTHONHOME"}, "PYTHONPATH": str(_ENGINE)}
            process = subprocess.Popen([sys.executable, "-B", "-P", "-m", _MODULE], cwd=_ENGINE.parent, env=env,
                                       stdin=child, stdout=child)
        except BaseException:
            parent.close()
            raise
        finally:
            child.close()
        self._connection, self._responses, self._process = parent, parent.makefile("rb"), process

    def __call__(self, project_root, control_root=None, *, instance_id=None, host_root=None):
        request = {"project_root": str(project_root), "control_root": str(control_root) if control_root is not None else None,
                   "instance_id": instance_id, "host_root": str(host_root) if host_root is not None else None}
        with self._lock:
            if self._closed:
                raise RuntimeError("Project admission service closed")
            if self._connection is None:
                self._start()
            if self._closed:
                self._stop()
                raise RuntimeError("Project admission service closed")
            try:
                self._connection.sendall(json.dumps(request).encode("utf-8") + b"\n")
                response = json.loads(self._responses.readline())
            except (OSError, UnicodeError, json.JSONDecodeError) as error:
                self._stop()
                raise RuntimeError("Project admission service unavailable") from error
            return _selection(response)

    def _stop(self):
        if self._responses is not None:
            self._responses.close()
            self._connection.close()
            self._responses = self._connection = None
        if self._process is not None:
            try:
                self._process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._process.terminate()
                try:
                    self._process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self._process.kill()
                    self._process.wait()
            self._process = None

    def close(self):
        self._closed = True
        connection = self._connection
        if connection is not None:
            try:
                connection.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
        with self._lock:
            self._stop()
