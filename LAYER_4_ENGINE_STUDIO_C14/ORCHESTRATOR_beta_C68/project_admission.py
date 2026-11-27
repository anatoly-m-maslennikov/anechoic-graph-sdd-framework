"""Call the reviewed Project admission CLI over a bounded process."""

from pydantic import BaseModel, ConfigDict, ValidationError
from pydantic.dataclasses import dataclass
import json
import os
from pathlib import Path
import subprocess
import socket
from threading import Lock
import sys
from typing import Literal

from .jobs import ENGINE as _ENGINE
_MODULE = "FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51.FEATURE_MODEL_VALIDATION.project_admission__pub"


@dataclass(frozen=True, config=ConfigDict(strict=True, extra="forbid"))
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


class _WireBinding(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    root: str
    control_root: str
    control_relative: str
    instance_id: str
    project_name: str
    project_prefix: str
    manifest_path: str
    manifest_ref: str
    manifest_sha256: str
    parameters: dict
    host_root: str | None
    tool_blacklist: list[str]
    release_workflows_enabled: bool

    def binding(self):
        data = self.model_dump()
        for key in ("root", "control_root", "control_relative", "manifest_path", "host_root"):
            if data[key] is not None:
                data[key] = Path(data[key])
        data["tool_blacklist"] = tuple(data["tool_blacklist"])
        return ProjectBinding(**data)


class _AdmissionResult(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    result: _WireBinding


class _AdmissionFailure(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    code: Literal["project_selection_error"]
    message: str


class _AdmissionError(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    error: _AdmissionFailure


def _selection(response):
    if isinstance(response, dict) and set(response) == {"error"}:
        try:
            failure = _AdmissionError.model_validate(response)
        except ValidationError:
            pass
        else:
            raise ValueError(failure.error.message)
    try:
        return _AdmissionResult.model_validate(response).result.binding()
    except ValidationError:
        raise RuntimeError("Invalid Project admission response") from None


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
            if os.getenv("ANECHOIC_TEST_IMAGE_DEADLINES") != "0":
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
