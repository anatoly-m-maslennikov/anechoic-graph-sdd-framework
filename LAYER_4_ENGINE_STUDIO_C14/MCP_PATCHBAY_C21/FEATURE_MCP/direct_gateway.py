
"""MCP gateway for the Project-owned Workbench."""

import asyncio
from concurrent.futures import CancelledError as FutureCancelledError
from contextlib import ExitStack, contextmanager, nullcontext, redirect_stdout
from pathlib import Path
import sys

from mcp import types
from mcp.server.lowlevel import Server
from mcp.server.stdio import stdio_server

from MCP_PATCHBAY_C21.FEATURE_MCP.caller_context import CallerContextError, take_caller_context
from MCP_PATCHBAY_C21.FEATURE_MCP.backend_client import ToolProtocolError, backend_client
from MCP_PATCHBAY_C21.FEATURE_MCP.health_observations import HealthObservations
from MCP_PATCHBAY_C21.FEATURE_MCP.native_startup import ProjectBinding, select_runtime_project
from MCP_PATCHBAY_C21.FEATURE_MCP.project_tool_context import native_arguments
from MCP_PATCHBAY_C21.FEATURE_MCP.runtime_request_context import bind_request_context
from MCP_PATCHBAY_C21.FEATURE_MCP.shared_gateway_support import record_observation, result, tool_failure, unexpected_failure
from MCP_PATCHBAY_C21.FEATURE_MCP.shared_tool_contract import public_tool


def startup_selection(root, control_root=None, instance_id=None, host_root=None):
    return select_runtime_project(root, control_root, instance_id=instance_id, host_root=host_root)


def native_project_gateway(root, *, selection, workbench_storage=None, journal_storage=None):
    if not isinstance(selection, ProjectBinding):
        raise ValueError("A native Project selection is required")
    return DirectGateway(root, selection=selection, workbench_storage=workbench_storage,
                         journal_storage=journal_storage)


@contextmanager
def native_runtime_gateway(selection):
    gateway = native_project_gateway(selection.root, selection=selection)
    try:
        yield gateway
    finally:
        gateway._backend_resources.close()


class DirectGateway:
    """Keep native Workbench calls within their selected Project and request."""

    def __init__(self, root, *, native_query=None, workbench=None, selection=None,
                 workbench_storage=None, journal_storage=None, tool_policy=None, tool_client=None):
        self.root = Path(root).resolve(strict=True)
        if (native_query is None) != (workbench is None):
            raise ValueError("An injected owner requires a Workbench interface")
        selected = native_query.selection if native_query is not None else selection
        if selected is None or selected.root != self.root:
            raise ValueError("Native query projection requires its own selected Project")
        self._native_query = native_query
        self._backend_resources = ExitStack()
        self._uses_backend = native_query is None
        self._workbench_storage = workbench_storage
        self._journal_storage = journal_storage
        self._tool_client = tool_client
        self.selection = selected
        self.tool_blacklist = frozenset()
        self.tools = ()
        self.registry = None
        self.ready = False
        self.server = None
        self.health_observations = HealthObservations()
        self.workbench = workbench

    @property
    def ready(self):
        return self._ready and getattr(self._native_query, "available", True)

    @ready.setter
    def ready(self, value):
        self._ready = value

    async def initialize(self):
        if self._ready:
            return
        try:
            if self._uses_backend:
                self._open_backend()
                await asyncio.to_thread(self._native_query.start)
            else:
                self._native_query.start()
            self._tool_client = self._tool_client or self._native_query
            await self._load_catalog()
        except BaseException:
            await self.close()
            raise
        self.ready = True

    async def _load_catalog(self):
        catalog = await self._tool_client.catalog()
        if (not isinstance(catalog, dict) or set(catalog) != {"tools", "blacklist"}
                or not isinstance(catalog["tools"], list) or not isinstance(catalog["blacklist"], list)
                or any(not isinstance(item, str) for item in catalog["blacklist"])):
            raise ToolProtocolError("tool_runtime_failure", "Invalid Backend catalog")
        self.tool_blacklist = frozenset(catalog["blacklist"])
        self.tools = tuple(types.Tool.model_validate(tool) for tool in catalog["tools"])
        if len({tool.name for tool in self.tools}) != len(self.tools):
            raise ToolProtocolError("tool_runtime_failure", "Invalid Backend catalog")

    def _open_backend(self):
        self._native_query = self._backend_resources.enter_context(backend_client(
            self.selection, workbench_storage=self._workbench_storage, journal_storage=self._journal_storage,
        ))
        self.workbench = self._native_query

    async def close(self):
        self.ready = False
        if self._uses_backend:
            await asyncio.to_thread(self._backend_resources.close)
        else:
            await self.workbench.close()

    def status(self):
        runtime = "api_backend" if getattr(self._native_query, "backend_pid", None) is not None else "single_process"
        return {"runtime": runtime, "ready": self.ready,
                "advertised_tools": [tool.name for tool in self.tools]}

    async def _invoke_bound(self, context, params, arguments, asserted_project_root):
        try:
            arguments, request_context = take_caller_context(arguments)
        except CallerContextError as error:
            return result({"outcome": "rejected", "diagnostics": [str(error)]}, True)
        with bind_request_context(request_context) if request_context else nullcontext():
            request = getattr(context, "request", None)
            base = getattr(request, "base_url", None)
            response = await self._tool_client.call_tool(
                params.name, arguments, public_base_url=str(base) if base is not None else None,
                asserted_project_root=asserted_project_root,
            )
        if (not isinstance(response, dict) or set(response) != {"value", "text"}
                or not isinstance(response["value"], dict)
                or (response["text"] is not None and not isinstance(response["text"], str))):
            raise ToolProtocolError("tool_runtime_failure", "Invalid Backend Tool response")
        return result(response["value"], text=response["text"])

    async def call(self, context, params, *, asserted_project_root=None):
        response = None
        error = None
        original = params.arguments
        try:
            root = asserted_project_root
            if root is None and isinstance(original, dict):
                root = original.get("project_root")
            arguments = native_arguments(original, self.selection, self.root)
            response = await self._invoke_bound(context, params, arguments, root)
        except (asyncio.CancelledError, FutureCancelledError) as caught:
            error = caught
            raise
        except ToolProtocolError as caught:
            response = tool_failure(caught)
        except Exception as caught:
            error = caught
            response = unexpected_failure()
        finally:
            record_observation(self.health_observations, params.name, original, response, error)
        return response

    def build_server(self):
        async def list_tools(context, params):
            return types.ListToolsResult(tools=[public_tool(tool, required=False) for tool in self.tools])

        self.server = Server(
            "ANECHOIC", version="0.2.0", on_list_tools=list_tools, on_call_tool=self.call,
        )
        return self.server

    async def serve(self):
        async with stdio_server() as streams:
            with redirect_stdout(sys.stderr):
                try:
                    await self.initialize()
                    await self.build_server().run(*streams, self.server.create_initialization_options())
                finally:
                    await self.close()
