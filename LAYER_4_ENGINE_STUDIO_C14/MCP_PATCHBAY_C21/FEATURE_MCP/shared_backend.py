"""Transport adapter for the private shared Workbench Backend coordinator."""
from __future__ import annotations

import asyncio
import os
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from typing import Any

import httpx2
from mcp import types

from MCP_PATCHBAY_C21.FEATURE_MCP.backend_client import ToolProtocolError
from MCP_PATCHBAY_C21.FEATURE_MCP.caller_context import CallerContextError
from MCP_PATCHBAY_C21.FEATURE_MCP.health_observations import HealthObservations
from MCP_PATCHBAY_C21.FEATURE_MCP.runtime_request_context import current_request_context
from MCP_PATCHBAY_C21.FEATURE_MCP.runtime_stack import runtime_stack
from MCP_PATCHBAY_C21.FEATURE_MCP.shared_gateway_support import call_mcp, make_server, record_observation, refusal, tool_failure, valid_tool_response


class SharedGatewayRefusal(ValueError):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def _raise_fault(envelope):
    fault = envelope.get("error")
    if (isinstance(fault, dict) and isinstance(fault.get("code"), str)
            and isinstance(fault.get("message"), str)):
        if fault.get("scope") == "project":
            raise SharedGatewayRefusal(fault["code"])
        if fault.get("scope") == "tool":
            raise ToolProtocolError.from_fault(fault)
    raise ToolProtocolError("tool_runtime_failure", "Invalid Shared Backend response")


class SharedBackendGateway:
    def __init__(self, config: Any, *, startup_timeout: float = 420) -> None:
        self.config = config
        self.startup_timeout = startup_timeout
        self.tools: list[types.Tool] = []
        self.ready = False
        self.health_observations = HealthObservations()
        self._directory = None
        self._process = None
        self._http = None
        self._lock = asyncio.Lock()

    async def initialize(self) -> None:
        async with self._lock:
            if self.ready:
                return
            try:
                socket = os.environ.get("ANECHOIC_BETA_BACKEND_SOCKET") if runtime_stack() == "beta" else None
                if socket is None:
                    socket = await self._start_backend()
                self._http = httpx2.AsyncClient(
                    transport=httpx2.AsyncHTTPTransport(uds=str(socket)),
                    base_url="http://anechoic-backend", trust_env=False, timeout=None,
                )
                async with asyncio.timeout(self.startup_timeout):
                    while True:
                        process = self._process
                        if process is not None and process.returncode is not None:
                            raise RuntimeError("Shared Backend exited during startup")
                        try:
                            health = await self._request("GET", "/health", timeout=0.5)
                            pid = health.get("pid")
                            if health.get("initialized") is True and type(pid) is int and (process is None or pid == process.pid):
                                break
                        except ToolProtocolError:
                            pass
                        await asyncio.sleep(0.05)
                    await self._load_catalog()
            except BaseException:
                await self.close()
                raise

    async def _start_backend(self):
        self._directory = TemporaryDirectory(prefix="anechoic-shared-", dir="/tmp")
        socket = Path(self._directory.name).resolve() / "api.sock"
        engine = Path(__file__).resolve().parents[2]
        environment = {**{k: v for k, v in os.environ.items() if k != "PYTHONHOME"}, "PYTHONPATH": str(engine)}
        module = (
            "WORKBENCH_BACKEND_beta_C70.shared_runtime" if runtime_stack() == "beta" else
            "IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.shared_backend_process"
        )
        command = [sys.executable, "-B", "-P", "-m", module, "--socket", str(socket)]
        source = getattr(self.config, "source_path", self.config)
        if source is not None:
            command += ["--host-settings", str(source)]
        self._process = await asyncio.create_subprocess_exec(
            *command, cwd=engine.parent, env=environment, stdin=asyncio.subprocess.PIPE, stdout=sys.stderr,
        )
        return socket

    async def _load_catalog(self):
        catalog = await self._request("GET", "/tools", timeout=45)
        raw_tools = catalog.get("tools")
        if not isinstance(raw_tools, list):
            raise RuntimeError("Invalid Shared Backend catalog")
        self.tools = [types.Tool.model_validate(item) for item in raw_tools]
        self.ready = True

    async def close(self) -> None:
        self.ready = False
        http, self._http = self._http, None
        process, self._process = self._process, None
        directory, self._directory = self._directory, None
        try:
            if http is not None:
                await http.aclose()
            if process is not None:
                if process.stdin is not None:
                    process.stdin.close()
                try:
                    await asyncio.wait_for(process.wait(), 15)
                except TimeoutError:
                    process.terminate()
                    try:
                        await asyncio.wait_for(process.wait(), 5)
                    except TimeoutError:
                        process.kill()
                        await process.wait()
        finally:
            if directory is not None:
                directory.cleanup()

    async def _exchange(self, method, path, **kwargs):
        if self._http is None:
            raise ToolProtocolError("tool_runtime_failure", "Shared Backend unavailable")
        try:
            response = await self._http.request(method, path, **kwargs)
        except httpx2.HTTPError as error:
            raise ToolProtocolError("tool_runtime_failure", "Shared Backend unavailable") from error
        try:
            envelope = response.json()
        except ValueError as error:
            raise ToolProtocolError("tool_runtime_failure", "Invalid Shared Backend response") from error
        if not isinstance(envelope, dict):
            raise ToolProtocolError("tool_runtime_failure", "Invalid Shared Backend response")
        return response.is_success, envelope

    async def _request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        succeeded, envelope = await self._exchange(method, path, **kwargs)
        if succeeded and isinstance(envelope.get("result"), dict):
            return envelope["result"]
        _raise_fault(envelope)

    async def status(self) -> dict[str, Any]:
        status = await self._request("GET", "/health", timeout=45)
        return {**status, **self.health_observations.snapshot()}

    async def select_project(self, value: object) -> dict[str, Any]:
        return await self._request("POST", "/selection", json={"project_root": value}, timeout=45)

    async def call_tool(self, name: str, arguments: Any, *, public_base_url: str | None = None) -> dict[str, Any]:
        context = current_request_context()
        response = None
        error = None
        project = None
        try:
            succeeded, envelope = await self._exchange("POST", "/tools", json={
                "name": name, "arguments": arguments,
                "session_id": context.session_id if context else None,
                "public_base_url": public_base_url,
            })
            project = envelope.get("project")
            result = envelope.get("result")
            if succeeded and valid_tool_response(result):
                response = result["value"]
                return result
            try:
                _raise_fault(envelope)
            except ToolProtocolError as caught:
                if caught.tool_result is not None:
                    response = {**caught.tool_result, "is_error": True}
                raise
        except BaseException as caught:
            if response is None:
                error = caught
            raise
        finally:
            project = project if isinstance(project, dict) else {}
            record_observation(self.health_observations, name, arguments, response, error,
                               project_prefix=project.get("prefix"),
                               project_instance_id=project.get("instance_id"))

    async def call(self, context: Any, params: Any) -> types.CallToolResult:
        try:
            return await call_mcp(self.call_tool, context, params.name, getattr(params, "arguments", None))
        except CallerContextError as error:
            return refusal(str(error))
        except SharedGatewayRefusal as error:
            return refusal(error.code)
        except ToolProtocolError as error:
            return tool_failure(error)

    def build_server(self):
        return make_server(lambda: self.tools if self.ready else [], self.call)
