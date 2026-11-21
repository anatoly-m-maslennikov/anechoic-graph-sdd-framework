
"""In-process MCP gateway for the Project-owned Workbench."""

import asyncio
from concurrent.futures import CancelledError as FutureCancelledError
from contextlib import contextmanager, nullcontext, redirect_stdout
from dataclasses import replace
import json
from pathlib import Path
import sys
from typing import TYPE_CHECKING

from mcp import types
from mcp.server.lowlevel import Server
from mcp.server.stdio import stdio_server

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "FEATURE_PROGRAMMATIC"))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "FEATURE_PROGRAMMATIC" / "FEATURE_TOOLS"))
from caller_context import CallerContextError, take_caller_context  # noqa: E402
from health_observations import HealthObservations  # noqa: E402
from operation_error_boundary import (  # noqa: E402
    FailureRecord, operation_error_boundary,
)
from project_settings_schema import mcp_tool_blacklist  # noqa: E402
from project_tool_context import native_arguments  # noqa: E402
from query_templates import QUERY_TEMPLATE  # noqa: E402
from registry_release_command_provider import RELEASE_COMMAND_TOOLS  # noqa: E402
from runtime_failure_diagnostics import report_failure  # noqa: E402
from runtime_request_context import bind_request_context  # noqa: E402
from shared_tool_contract import public_tool  # noqa: E402
from tool_registry_runtime import (  # noqa: E402
    ToolInputValidationError, ToolOutputValidationError, ToolRegistryRuntimeError,
    ToolRegistryStaleError,
    load_active_registry,
)
from workbench_tools import PAGE, RUN, WorkbenchTools  # noqa: E402

if TYPE_CHECKING:
    from native_query import NativeQueryOwner


def startup_selection(root, control_root=None, instance_id=None, host_root=None):
    from native_project_selection import rebind_native_selection
    from native_startup import select_runtime_project

    selection = select_runtime_project(root, control_root)
    if host_root is not None and instance_id is None:
        raise ValueError("Host Project binding requires an explicit instance identity")
    if instance_id is None:
        return selection
    return rebind_native_selection(selection, instance_id, host_root=host_root)


def native_project_gateway(root, *, selection):
    from native_project_selection import NativeProjectSelection
    from native_query import NativeQueryOwner
    from native_startup import load_native_inputs

    if not isinstance(selection, NativeProjectSelection):
        raise ValueError("A native Project selection is required")
    return DirectGateway(root, native_query=NativeQueryOwner(selection, load_native_inputs(selection)))


@contextmanager
def native_runtime_gateway(selection):
    from LAYER_3_ENGINE_STUDIO_C14.KERNEL_MIXER_C59.MANIFEST_RUNTIME_C62.manifest_compiler_pkg1.compiler import (
        load_generation_model,
    )
    from LAYER_3_ENGINE_STUDIO_C14.KERNEL_MIXER_C59.MANIFEST_RUNTIME_C62.runtime import run_manifest_runtime
    from native_query import NativeQueryOwner
    from native_startup import load_native_inputs

    with run_manifest_runtime(selection) as (generation, snapshot):
        sys.path.insert(0, str(generation))
        try:
            selected = replace(selection, structure_snapshot=snapshot)
            inputs = load_native_inputs(selected, model=load_generation_model(generation))
            yield DirectGateway(selected.root, native_query=NativeQueryOwner(selected, inputs))
        finally:
            sys.path.remove(str(generation))


def result(value, error=False, *, text=None):
    return types.CallToolResult(
        content=[types.TextContent(type="text", text=json.dumps(value) if text is None else text)],
        structured_content=value, is_error=error,
    )


class DirectGateway:
    """Keep native Workbench calls within their selected Project and request."""

    def __init__(self, root, *, native_query: "NativeQueryOwner"):
        self.root = Path(root).resolve(strict=True)
        if native_query.selection.root != self.root:
            raise ValueError("Native query projection requires its own selected Project")
        self._native_query = native_query
        self._diagnostic_root = None
        self.selection = native_query.selection
        self.tool_blacklist = frozenset()
        self.tools = ()
        self.registry = None
        self.ready = False
        self.server = None
        self.health_observations = HealthObservations()
        self.workbench = WorkbenchTools(query_owner=native_query)

    async def initialize(self):
        if self.ready:
            return
        project_blacklist = mcp_tool_blacklist(self.selection.parameters)
        try:
            self.registry = load_active_registry(Path(__file__).parent, self.root, self)
        except ToolRegistryRuntimeError as error:
            report_failure(
                self._diagnostic_root,
                FailureRecord("ERROR", "tool_registry_unavailable", "MCP tool registry is unavailable"),
                component="MCP_GATEWAY", operation="initialize",
            )
            raise error
        self.tool_blacklist = self.registry.global_blacklist | project_blacklist
        try:
            self._native_query.start()
            if self.selection.parameters.get("project_mcp", {}).get("release_workflows_enabled") is not True:
                self.tool_blacklist |= RELEASE_COMMAND_TOOLS & self.registry.routes.keys()
            if RUN in self.tool_blacklist:
                self.tool_blacklist |= {QUERY_TEMPLATE}
            self.tools = tuple(
                tool for tool in self.registry.tools if tool.name not in self.tool_blacklist
            )
        except Exception:
            await self.close()
            raise
        self.ready = True

    async def close(self):
        self.ready = False
        if self.registry is not None:
            await self.registry.close()
            self.registry = None
        await self.workbench.close()

    def status(self):
        return {"runtime": "single_process", "ready": self.ready,
                "advertised_tools": [tool.name for tool in self.tools]}

    def _failure(self, error, operation):
        failure, secondary = report_failure(
            self._diagnostic_root, error, component="MCP_GATEWAY", operation=operation,
        )
        diagnostics = [f"{failure.code}: {failure.message}"]
        if secondary:
            diagnostics.append("technical diagnostic unavailable")
        return result({"outcome": "failed", "diagnostics": diagnostics}, True)

    def _input_rejection(self, operation):
        report_failure(
            self._diagnostic_root,
            FailureRecord("WARNING", "tool_input_invalid", "Tool input does not match its schema"),
            component="MCP_GATEWAY", operation=operation,
        )
        return result({"outcome": "rejected", "diagnostics": ["tool_input_invalid"]}, True)

    def _runtime_failure(self, code, message, operation):
        return self._failure(FailureRecord("ERROR", code, message), operation)

    def _registry_failure(self, error, operation):
        if isinstance(error, ToolRegistryStaleError):
            return result({"outcome": "rejected", "diagnostics": ["tool_registry_stale"]}, True)
        return self._runtime_failure(
            "tool_runtime_failure", "MCP tool runtime is unavailable", operation
        )

    async def _invoke_bound(self, context, params, arguments):
        try:
            arguments, request_context = take_caller_context(arguments)
        except CallerContextError as error:
            return result({"outcome": "rejected", "diagnostics": [str(error)]}, True)
        if self.registry is None or params.name in self.tool_blacklist or not self.registry.permits(params.name):
            return result({"outcome": "rejected", "diagnostics": ["Unknown Tool"]}, True)
        with bind_request_context(request_context) if request_context else nullcontext():
            try:
                return await self._call(context, params.name, arguments)
            except ToolInputValidationError:
                return self._input_rejection(params.name)
            except ToolOutputValidationError:
                return self._runtime_failure(
                    "tool_output_invalid", "Tool output does not match its schema", params.name,
                )
            except ToolRegistryRuntimeError as error:
                return self._registry_failure(error, params.name)

    async def call(self, context, params):
        response = None
        error = None

        def on_error(caught):
            nonlocal error
            error = caught
            return self._failure(caught, params.name)

        @operation_error_boundary(on_error=on_error)
        async def guarded_call():
            arguments = native_arguments(params.arguments, self.selection, self.root)
            return await self._invoke_bound(context, params, arguments)

        try:
            response = await guarded_call()
            return response
        except (asyncio.CancelledError, FutureCancelledError) as caught:
            error = caught
            raise
        finally:
            try:
                self.health_observations.record(
                    params.name, getattr(params, "arguments", None), response, error=error,
                )
            except FutureCancelledError:
                raise
            except Exception:
                report_failure(
                    self._diagnostic_root,
                    FailureRecord("WARNING", "health_observation_failed", "health observations unavailable"),
                    component="MCP_GATEWAY", operation="health_observations",
                )

    async def _call(self, context, name, arguments):
        if self.registry is None:
            raise ToolRegistryRuntimeError("tool-registry-unavailable")
        value = await self.registry.call(name, arguments, context=context)
        return result(value, text=value.get("csv") if name in {QUERY_TEMPLATE, RUN, PAGE} else None)

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
