"""Transport adapter for the private shared Workbench Backend coordinator."""
from __future__ import annotations

import asyncio
from contextlib import nullcontext
import os
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from typing import Any

import httpx2
from mcp import types
from mcp.server.lowlevel import Server

from MCP_PATCHBAY_C21.FEATURE_MCP.backend_client import ToolProtocolError
from MCP_PATCHBAY_C21.FEATURE_MCP.caller_context import CallerContextError, take_caller_context
from MCP_PATCHBAY_C21.FEATURE_MCP.health_observations import HealthObservations
from MCP_PATCHBAY_C21.FEATURE_MCP.runtime_request_context import bind_request_context, current_request_context
from MCP_PATCHBAY_C21.FEATURE_MCP.runtime_stack import runtime_stack
from MCP_PATCHBAY_C21.FEATURE_MCP.shared_gateway_support import record_observation, refusal, result, tool_failure


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
        self.server = None
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
                self._directory = TemporaryDirectory(prefix="anechoic-shared-", dir="/tmp")
                socket = Path(self._directory.name).resolve() / "api.sock"
                engine = Path(__file__).resolve().parents[2]
                root = engine.parent
                environment = {**{k: v for k, v in os.environ.items() if k != "PYTHONHOME"}, "PYTHONPATH": str(engine)}
                module = (
                    "WORKBENCH_BACKEND_beta_C70.shared_runtime__pub" if runtime_stack() == "beta" else
                    "IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.shared_backend_process"
                )
                command = [sys.executable, "-B", "-P", "-m", module, "--socket", str(socket)]
                source = getattr(self.config, "source_path", self.config)
                if source is not None:
                    command += ["--host-settings", str(source)]
                self._process = await asyncio.create_subprocess_exec(
                    *command, cwd=root, env=environment, stdin=asyncio.subprocess.PIPE,
                    stdout=sys.stderr,
                )
                self._http = httpx2.AsyncClient(
                    transport=httpx2.AsyncHTTPTransport(uds=str(socket)),
                    base_url="http://anechoic-backend", trust_env=False, timeout=None,
                )
                async with asyncio.timeout(self.startup_timeout):
                    while True:
                        if self._process.returncode is not None:
                            raise RuntimeError("Shared Backend exited during startup")
                        try:
                            health = await self._request("GET", "/health", timeout=0.5)
                            if health.get("initialized") is True and health.get("pid") == self._process.pid:
                                break
                        except ToolProtocolError:
                            pass
                        await asyncio.sleep(0.05)
                    await self._load_catalog()
            except BaseException:
                await self.close()
                raise

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

    async def _tool(self, name: str, arguments: Any, public_base_url: str | None) -> dict[str, Any]:
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
            if (succeeded and isinstance(result, dict) and set(result) == {"value", "text"}
                    and isinstance(result["value"], dict)
                    and (result["text"] is None or isinstance(result["text"], str))):
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

    async def workbench_call(self, name: str, arguments: dict[str, Any], *, public_base_url=None) -> dict[str, Any]:
        return (await self._tool(name, arguments, public_base_url))["value"]

    async def call(self, context: Any, params: Any) -> types.CallToolResult:
        try:
            arguments, request_context = take_caller_context(getattr(params, "arguments", None))
        except CallerContextError as error:
            return refusal(str(error))
        try:
            with bind_request_context(request_context) if request_context else nullcontext():
                request = getattr(context, "request", None)
                base = getattr(request, "base_url", None)
                response = await self._tool(params.name, arguments, str(base) if base is not None else None)
            return result(response["value"], text=response["text"])
        except SharedGatewayRefusal as error:
            return refusal(error.code)
        except ToolProtocolError as error:
            return tool_failure(error)

    def build_server(self) -> Server:
        async def list_tools(_context: Any, _params: Any) -> types.ListToolsResult:
            return types.ListToolsResult(tools=self.tools if self.ready else [])
        self.server = Server("ANECHOIC", version="0.2.0", on_list_tools=list_tools, on_call_tool=self.call)
        return self.server
