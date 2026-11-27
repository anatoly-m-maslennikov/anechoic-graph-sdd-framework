"""MCP gateway for the Project-owned Workbench."""

import asyncio
from concurrent.futures import CancelledError as FutureCancelledError
from contextlib import ExitStack, contextmanager, redirect_stdout
import os
from pathlib import Path
import sys

from mcp import types
from mcp.server.stdio import stdio_server

from MCP_PATCHBAY_C21.FEATURE_MCP.caller_context import CallerContextError
from MCP_PATCHBAY_C21.FEATURE_MCP.backend_client import (
    ToolProtocolError,
    backend_client,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.health_observations import HealthObservations
from MCP_PATCHBAY_C21.FEATURE_MCP.native_startup import (
    ProjectBinding,
    select_runtime_project,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.project_tool_context import native_arguments
from MCP_PATCHBAY_C21.FEATURE_MCP.shared_gateway_support import (
    call_mcp,
    make_server,
    record_observation,
    result,
    tool_failure,
    unexpected_failure,
    valid_tool_response,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.shared_tool_contract import public_tool


def startup_selection(
    root, control_root=None, instance_id=None, host_root=None
):
    return select_runtime_project(
        root, control_root, instance_id=instance_id, host_root=host_root
    )


def native_project_gateway(
    root,
    *,
    selection,
    workbench_storage=None,
    journal_storage=None,
    backend_socket=None,
):
    if not isinstance(selection, ProjectBinding):
        raise ValueError("A native Project selection is required")
    return DirectGateway(
        root,
        selection=selection,
        workbench_storage=workbench_storage,
        journal_storage=journal_storage,
        backend_socket=backend_socket,
    )


@contextmanager
def native_runtime_gateway(selection, *, backend_socket=None):
    gateway = native_project_gateway(
        selection.root,
        selection=selection,
        workbench_storage=os.getenv("ANECHOIC_WORKBENCH_STORAGE"),
        journal_storage=os.getenv("ANECHOIC_JOURNAL_STORAGE"),
        backend_socket=backend_socket,
    )
    try:
        yield gateway
    finally:
        gateway._backend_resources.close()


class DirectGateway:
    "Keep native Workbench calls within their selected Project and request."

    def __init__(
        self,
        root,
        *,
        native_query=None,
        workbench=None,
        selection=None,
        workbench_storage=None,
        journal_storage=None,
        tool_client=None,
        backend_socket=None,
    ):
        self.root = Path(root).resolve(strict=True)
        if (native_query is None) != (workbench is None):
            raise ValueError(
                "An injected owner requires a Workbench interface"
            )
        selected = (
            native_query.selection if native_query is not None else selection
        )
        if selected is None or selected.root != self.root:
            raise ValueError(
                "Native query projection requires its own selected Project"
            )
        self._native_query = native_query
        self._backend_resources = ExitStack()
        self._uses_backend = native_query is None
        self._workbench_storage = workbench_storage
        self._journal_storage = journal_storage
        self._backend_socket = backend_socket
        self._tool_client = tool_client
        self.selection = selected
        self.tool_blacklist = frozenset()
        self.tools = ()
        self.registry = None
        self.ready = False
        self.health_observations = HealthObservations()
        self.workbench = workbench

    @property
    def ready(self):
        return self._ready and getattr(self._native_query, "available", True)

    @ready.setter
    def ready(self, value):
        self._ready = value

    def health_state(self):
        return (
            self._native_query.health_state() if self._ready else "unavailable"
        )

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
        if (
            not isinstance(catalog, dict)
            or set(catalog) != {"tools", "blacklist"}
            or not isinstance(catalog["tools"], list)
            or not isinstance(catalog["blacklist"], list)
            or any(not isinstance(item, str) for item in catalog["blacklist"])
        ):
            raise ToolProtocolError(
                "tool_runtime_failure", "Invalid Backend catalog"
            )
        self.tool_blacklist = frozenset(catalog["blacklist"])
        self.tools = tuple(
            types.Tool.model_validate(tool) for tool in catalog["tools"]
        )
        if len({tool.name for tool in self.tools}) != len(self.tools):
            raise ToolProtocolError(
                "tool_runtime_failure", "Invalid Backend catalog"
            )

    def _open_backend(self):
        self._native_query = self._backend_resources.enter_context(
            backend_client(
                self.selection,
                workbench_storage=self._workbench_storage,
                journal_storage=self._journal_storage,
                backend_socket=self._backend_socket,
            )
        )
        self.workbench = self._native_query

    async def close(self):
        self.ready = False
        if self._uses_backend:
            await asyncio.to_thread(self._backend_resources.close)
        else:
            await self.workbench.close()

    def status(self):
        runtime = (
            "api_backend"
            if getattr(self._native_query, "backend_pid", None) is not None
            else "single_process"
        )
        return {
            "runtime": runtime,
            "ready": self.ready,
            "advertised_tools": [tool.name for tool in self.tools],
        }

    async def call_tool(
        self,
        name,
        arguments,
        *,
        public_base_url=None,
        asserted_project_root=None,
    ):
        ("Call the admitted Backend with transport envelope fields "
         "already separated.")  # fmt: skip
        response = await self._tool_client.call_tool(
            name,
            arguments,
            public_base_url=public_base_url,
            asserted_project_root=asserted_project_root,
        )
        if not valid_tool_response(response):
            raise ToolProtocolError(
                "tool_runtime_failure", "Invalid Backend Tool response"
            )
        return response

    async def call(self, context, params, *, asserted_project_root=None):
        response = None
        error = None
        original = params.arguments
        try:
            root = asserted_project_root
            if root is None and isinstance(original, dict):
                root = original.get("project_root")
            arguments = native_arguments(original, self.selection, self.root)
            response = await call_mcp(
                self.call_tool,
                context,
                params.name,
                arguments,
                asserted_project_root=root,
            )
        except (asyncio.CancelledError, FutureCancelledError) as caught:
            error = caught
            raise
        except CallerContextError as caught:
            response = result(
                {"outcome": "rejected", "diagnostics": [str(caught)]}, True
            )
        except ToolProtocolError as caught:
            response = tool_failure(caught)
        except Exception as caught:
            error = caught
            response = unexpected_failure()
        finally:
            record_observation(
                self.health_observations,
                params.name,
                original,
                response,
                error,
            )
        return response

    def build_server(self):
        return make_server(
            lambda: [public_tool(tool, required=False) for tool in self.tools],
            self.call,
        )

    async def serve(self):
        async with stdio_server() as streams:
            with redirect_stdout(sys.stderr):
                try:
                    await self.initialize()
                    server = self.build_server()
                    await server.run(
                        *streams, server.create_initialization_options()
                    )
                finally:
                    await self.close()
