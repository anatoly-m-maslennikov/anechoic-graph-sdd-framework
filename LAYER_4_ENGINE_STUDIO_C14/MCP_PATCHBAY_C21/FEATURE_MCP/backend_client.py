"""Call the Project's Workbench API in its own process."""

import asyncio
from contextlib import ExitStack, contextmanager
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
from time import monotonic, sleep

import httpx2

from MCP_PATCHBAY_C21.FEATURE_MCP.transport_support.paths.\
    paths__shared import (
    TOOL_REST_PATH,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.runtime_request_context import (
    current_request_context,
)


_MODULE = (
    "IWE_CONSOLE_C43.APP_IWE_CONSOLE."
    "FEATURE_IWE_CONSOLE_BACKEND.backend_process"
)
_STARTUP_SECONDS = 180
_DEV_LOCAL_STARTUP_SECONDS = 420


def _validate_kernel_readiness(observed):
    kernel = observed.get("kernel_pid")
    generation = observed.get("generation")
    if (
        type(kernel) is not int
        or kernel <= 1
        or not isinstance(generation, str)
        or not generation
    ):
        raise RuntimeError("Invalid managed Kernel readiness")


class ToolProtocolError(RuntimeError):
    def __init__(self, code, message, tool_result=None, *, status_code=200):
        self.code = code
        self.tool_result = tool_result
        self.status_code = status_code
        super().__init__(message)

    @classmethod
    def from_fault(cls, fault, *, status_code=200):
        result = fault.get("tool_result") if isinstance(fault, dict) else None
        if (
            isinstance(result, dict)
            and set(result) == {"outcome", "diagnostics"}
            and result["outcome"] in ("rejected", "failed")
            and isinstance(result["diagnostics"], list)
            and all(isinstance(item, str) for item in result["diagnostics"])
            and isinstance(fault.get("code"), str)
            and isinstance(fault.get("message"), str)
        ):
            return cls(
                fault["code"],
                fault["message"],
                result,
                status_code=status_code,
            )
        return cls("tool_runtime_failure", "Invalid Backend response")


class BackendClient:
    def __init__(self, selection, process, http):
        self.selection = selection
        self.backend_pid = process.pid if process is not None else None
        self._process = process
        self._http = http
        self._closed = False

    @property
    def available(self):
        if self._closed:
            return False
        if self._process is not None:
            return self._process.poll() is None
        return self.health_state() == "ready"

    def health_state(self):
        if self._closed:
            return "unavailable"
        try:
            return self._probe_state()
        except httpx2.HTTPError, ValueError, RuntimeError:
            return "unavailable"

    def _managed_state(self, response, observed):
        pid = observed.get("pid")
        if type(pid) is not int or pid <= 1:
            raise RuntimeError("Invalid managed Backend identity")
        if response.status_code == 200 and observed.get("state") in (
            "pending",
            "degraded",
        ):
            self.backend_pid = pid
            return observed["state"]
        if response.status_code == 503:
            return "unavailable"
        _validate_kernel_readiness(observed)
        return None

    def _probe_state(self):
        response = self._http.get("/health", timeout=0.5)
        observed = response.json()
        if (
            not isinstance(observed, dict)
            or observed.get("instance_id") != self.selection.instance_id
            or observed.get("manifest_sha256")
            != self.selection.manifest_sha256
        ):
            raise RuntimeError(
                "Workbench Backend reported a different Project binding"
            )
        pid = observed.get("pid")
        state = observed.get("state")
        if self._process is None:
            managed_state = self._managed_state(response, observed)
            if managed_state is not None:
                return managed_state
        elif pid != self.backend_pid:
            raise RuntimeError(
                "Workbench Backend reported a different Project binding"
            )
        elif state is None and observed.get("ready") is True:
            state = "ready"
        if response.status_code != 200 or state != "ready":
            raise RuntimeError(
                "Workbench Backend reported a different Project binding"
            )
        self.backend_pid = pid
        return "ready"

    def start(self):
        """Attach to the admitted Project transport."""
        dev_local = (
            self._process is not None
            and os.getenv("ANECHOIC_RUNTIME_PROFILE") == "dev-local"
        )
        budget = _DEV_LOCAL_STARTUP_SECONDS if dev_local else _STARTUP_SECONDS
        deadline = monotonic() + budget
        bounded = os.getenv("ANECHOIC_TEST_IMAGE_DEADLINES") != "0"
        while not self._closed and (not bounded or monotonic() < deadline):
            if self._process is not None and self._process.poll() is not None:
                break
            try:
                state = self._probe_state()
                if state == "ready" or (
                    self._process is None and state in {"pending", "degraded"}
                ):
                    return
            except httpx2.TransportError:
                pass
            sleep(0.05)
        raise RuntimeError("Workbench Backend did not start")

    def _tool_response(self, response):
        try:
            envelope = response.json()
        except ValueError as error:
            raise ToolProtocolError(
                "tool_runtime_failure", "Invalid Backend response"
            ) from error
        if (
            response.is_success
            and isinstance(envelope, dict)
            and set(envelope) == {"result"}
        ):
            if isinstance(envelope["result"], dict):
                return envelope["result"]
        raise ToolProtocolError.from_fault(
            envelope.get("error") if isinstance(envelope, dict) else None,
            status_code=response.status_code,
        )

    def _catalog(self):
        try:
            return self._tool_response(
                self._http.get(
                    TOOL_REST_PATH,
                    params={"instance_id": self.selection.instance_id},
                )
            )
        except httpx2.HTTPError as error:
            raise ToolProtocolError(
                "tool_runtime_failure", "Backend unavailable"
            ) from error

    async def catalog(self):
        return await asyncio.to_thread(self._catalog)

    def _tool(self, name, arguments, public_base_url, asserted_project_root):
        context = current_request_context()
        try:
            response = self._http.post(
                TOOL_REST_PATH,
                json={
                    "name": name,
                    "arguments": arguments,
                    "instance_id": self.selection.instance_id,
                    "session_id": context.session_id if context else None,
                    "public_base_url": public_base_url,
                    "asserted_project_root": asserted_project_root,
                },
            )
            return self._tool_response(response)
        except httpx2.HTTPError as error:
            raise ToolProtocolError(
                "tool_runtime_failure", "Backend unavailable"
            ) from error

    async def call_tool(
        self,
        name,
        arguments,
        *,
        public_base_url=None,
        asserted_project_root=None,
    ):
        return await asyncio.to_thread(
            self._tool, name, arguments, public_base_url, asserted_project_root
        )

    def close(self):
        if self._closed:
            return
        self._closed = True
        try:
            self._http.close()
        finally:
            if self._process is not None:
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


def _current_arguments(selection, socket, workbench_storage, journal_storage):
    args = [
        _MODULE,
        "--socket",
        str(socket),
        "--project-root",
        str(selection.root),
        "--control-root",
        selection.control_relative.as_posix(),
        "--instance-id",
        selection.instance_id,
        "--manifest-sha256",
        selection.manifest_sha256,
    ]
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
    environment = {
        **{k: v for k, v in os.environ.items() if k != "PYTHONHOME"},
        "PYTHONPATH": str(engine),
    }
    args = _current_arguments(
        selection, socket, workbench_storage, journal_storage
    )
    command = [sys.executable, "-B", "-P", "-m", *args]
    return subprocess.Popen(
        command, cwd=root, env=environment, stdin=subprocess.PIPE, stdout=2
    )


@contextmanager
def backend_client(
    selection,
    *,
    workbench_storage=None,
    journal_storage=None,
    backend_socket=None,
):
    with ExitStack() as stack:
        if backend_socket is None:
            directory = stack.enter_context(
                TemporaryDirectory(prefix="anechoic-api-", dir="/tmp")
            )
            socket = Path(directory).resolve() / "api.sock"
            transport = httpx2.HTTPTransport(uds=str(socket))
        else:
            socket = backend_socket
            limits = httpx2.Limits(
                max_connections=100, max_keepalive_connections=0
            )
            transport = httpx2.HTTPTransport(uds=str(socket), limits=limits)
        http = stack.enter_context(
            httpx2.Client(
                transport=transport,
                base_url="http://anechoic-backend",
                trust_env=False,
                timeout=None,
            )
        )
        process = (
            _start(selection, socket, workbench_storage, journal_storage)
            if backend_socket is None
            else None
        )
        client = BackendClient(selection, process, http)
        try:
            yield client
        finally:
            client.close()
