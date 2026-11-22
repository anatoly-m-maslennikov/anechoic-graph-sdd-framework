"""Call the Project's Workbench API in its own process."""

import asyncio
from contextlib import contextmanager
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
from time import monotonic, sleep

import httpx2

from MCP_PATCHBAY_C21.FEATURE_MCP.runtime_request_context import current_request_context
from MCP_PATCHBAY_C21.FEATURE_MCP.runtime_stack import runtime_stack


_MODULE = "IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.backend_process"


class ToolProtocolError(RuntimeError):
    def __init__(self, code, message, tool_result=None):
        self.code = code
        self.tool_result = tool_result
        super().__init__(message)

    @classmethod
    def from_fault(cls, fault):
        result = fault.get("tool_result") if isinstance(fault, dict) else None
        if (isinstance(result, dict) and set(result) == {"outcome", "diagnostics"}
                and result["outcome"] in ("rejected", "failed")
                and isinstance(result["diagnostics"], list)
                and all(isinstance(item, str) for item in result["diagnostics"])
                and isinstance(fault.get("code"), str) and isinstance(fault.get("message"), str)):
            return cls(fault["code"], fault["message"], result)
        return cls("tool_runtime_failure", "Invalid Backend response")


class BackendClient:
    def __init__(self, selection, process, http):
        self.selection = selection
        self.backend_pid = process.pid
        self._process = process
        self._http = http
        self._closed = False

    @property
    def available(self):
        return not self._closed and self._process.poll() is None

    def start(self):
        """Finish admission before the frontend advertises readiness."""
        expected = {"ready": True, "instance_id": self.selection.instance_id,
                    "manifest_sha256": self.selection.manifest_sha256, "pid": self.backend_pid}
        deadline = monotonic() + 90
        while self.available and monotonic() < deadline:
            try:
                response = self._http.get("/health", timeout=0.5)
            except httpx2.TransportError:
                sleep(0.05)
                continue
            observed = response.json()
            if (response.status_code != 200 or not isinstance(observed, dict)
                    or any(observed.get(key) != value for key, value in expected.items())):
                raise RuntimeError("Workbench Backend reported a different Project binding")
            return
        raise RuntimeError("Workbench Backend did not start")

    def _tool_response(self, response):
        try:
            envelope = response.json()
        except ValueError as error:
            raise ToolProtocolError("tool_runtime_failure", "Invalid Backend response") from error
        if response.is_success and isinstance(envelope, dict) and set(envelope) == {"result"}:
            if isinstance(envelope["result"], dict):
                return envelope["result"]
        raise ToolProtocolError.from_fault(envelope.get("error") if isinstance(envelope, dict) else None)

    def _catalog(self):
        try:
            return self._tool_response(self._http.get("/tools", params={"instance_id": self.selection.instance_id}))
        except httpx2.HTTPError as error:
            raise ToolProtocolError("tool_runtime_failure", "Backend unavailable") from error

    async def catalog(self):
        return await asyncio.to_thread(self._catalog)

    def _tool(self, name, arguments, public_base_url, asserted_project_root):
        context = current_request_context()
        try:
            response = self._http.post("/tools", json={
                "name": name, "arguments": arguments, "instance_id": self.selection.instance_id,
                "session_id": context.session_id if context else None, "public_base_url": public_base_url,
                "asserted_project_root": asserted_project_root,
            })
            return self._tool_response(response)
        except httpx2.HTTPError as error:
            raise ToolProtocolError("tool_runtime_failure", "Backend unavailable") from error

    async def call_tool(self, name, arguments, *, public_base_url=None, asserted_project_root=None):
        return await asyncio.to_thread(self._tool, name, arguments, public_base_url, asserted_project_root)

    def close(self):
        if self._closed:
            return
        self._closed = True
        try:
            self._http.close()
        finally:
            self._process.stdin.close()
            try:
                self._process.wait(timeout=15)
            except subprocess.TimeoutExpired:
                self._process.terminate()
                try:
                    self._process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self._process.kill()
                    self._process.wait()


def _beta_arguments(selection, socket):
    args = ["WORKBENCH_BACKEND_beta_C70.runtime__pub", "--socket", str(socket),
            "--project-root", str(selection.root), "--control-root", selection.control_relative.as_posix(),
            "--instance-id", selection.instance_id, "--manifest-sha256", selection.manifest_sha256,
            "--manifest-path", selection.manifest_path.relative_to(selection.control_root).as_posix(),
            "--project-prefix", selection.project_prefix]
    if selection.host_root is not None:
        args += ["--host-root", str(selection.host_root)]
    for name in selection.tool_blacklist:
        args += ["--blacklist", name]
    return args


def _current_arguments(selection, socket, workbench_storage, journal_storage):
    args = [_MODULE, "--socket", str(socket),
            "--project-root", str(selection.root), "--control-root", selection.control_relative.as_posix(),
            "--instance-id", selection.instance_id, "--manifest-sha256", selection.manifest_sha256]
    if selection.host_root is not None:
        args += ["--host-project-root", str(selection.host_root)]
    if workbench_storage is not None:
        args += ["--default-workbench-storage", workbench_storage]
    if journal_storage is not None:
        args += ["--default-journal-storage", journal_storage]
    return args


def _start(selection, socket, workbench_storage, journal_storage):
    engine = Path(__file__).resolve().parents[2]
    root = engine.parent
    environment = {**{k: v for k, v in os.environ.items() if k != "PYTHONHOME"}, "PYTHONPATH": str(engine)}
    if runtime_stack() == "beta":
        args = _beta_arguments(selection, socket)
    else:
        args = _current_arguments(selection, socket, workbench_storage, journal_storage)
    command = [sys.executable, "-B", "-P", "-m", *args]
    return subprocess.Popen(command, cwd=root, env=environment, stdin=subprocess.PIPE, stdout=2)


@contextmanager
def backend_client(selection, *, workbench_storage=None, journal_storage=None):
    with TemporaryDirectory(prefix="anechoic-api-", dir="/tmp") as directory:
        socket = Path(directory).resolve() / "api.sock"
        with httpx2.Client(transport=httpx2.HTTPTransport(uds=str(socket)),
                           base_url="http://anechoic-backend", trust_env=False, timeout=None) as http:
            process = _start(selection, socket, workbench_storage, journal_storage)
            client = BackendClient(selection, process, http)
            try:
                yield client
            finally:
                client.close()
