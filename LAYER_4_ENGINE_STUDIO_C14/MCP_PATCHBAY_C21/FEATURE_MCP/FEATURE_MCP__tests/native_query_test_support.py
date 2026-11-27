"""In-process Workbench fixtures for transport and behavior tests."""

import asyncio
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import NonCallableMock

from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import (
    NativeQueryInputs,
    NativeQueryOwner,
)
from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import (
    QueryExecutionError,
    WorkbenchUnavailableError,
)
from IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IWE_CONSOLE_BACKEND.\
    FEATURE_IWE_CONSOLE_BACKEND__shared \
    import (
        load_active_registry,
        ToolInputValidationError,
        ToolOutputValidationError,
        ToolRegistryRuntimeError,
        ToolRegistryStaleError,
    )  # fmt: skip
from IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IWE_CONSOLE_BACKEND.\
    backend_tool_api \
    import tool_failure_result  # fmt: skip

MCP = Path(__file__).resolve().parents[1]
STUDIO = MCP.parents[1]

from IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IWE_CONSOLE_BACKEND.workbench_operations import (  # noqa: E402
    WorkbenchOperations,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__shared import (  # noqa: E402
    ExplicitBlockingRuntimeFailure,
    resolve_native_project,
)


def _tool_fault(code, message, *, emit=False):
    from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import (
        ToolProtocolError,
    )

    return ToolProtocolError(
        code, message, tool_failure_result(code, message, emit=emit)
    )


class FixtureToolClient:
    def __init__(self, gateway):
        self.gateway = gateway
        self.registry = None

    async def catalog(self):
        from IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IWE_CONSOLE_BACKEND.\
            project_admission \
            import project_tool_policy  # fmt: skip
        from IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IWE_CONSOLE_BACKEND.\
            registry_release_command_provider \
            import RELEASE_COMMAND_TOOLS  # fmt: skip

        if self.registry is None:
            try:
                self.registry = load_active_registry(
                    STUDIO
                    / "IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_BACKEND",
                    self.gateway.root,
                    self.gateway,
                )
            except ToolRegistryRuntimeError as error:
                raise _tool_fault(
                    "tool_runtime_failure", str(error)
                ) from error
            self.gateway.registry = self.registry
        try:
            self.registry.ensure_current()
        except ToolRegistryStaleError as error:
            raise _tool_fault("tool_registry_stale", str(error)) from error
        blacklist, releases = project_tool_policy(
            self.gateway.selection.parameters
        )
        blocked = set(blacklist) | set(self.registry.global_blacklist)
        if not releases:
            blocked.update(RELEASE_COMMAND_TOOLS & self.registry.routes.keys())
        if "query_run" in blocked:
            blocked.add("query_template")
        return {
            "tools": [
                tool.model_dump(by_alias=True)
                for tool in self.registry.tools
                if tool.name not in blocked
            ],
            "blacklist": sorted(blocked),
        }

    async def call_tool(
        self,
        name,
        arguments,
        *,
        public_base_url=None,
        asserted_project_root=None,
    ):
        context = NonCallableMock(
            spec_set=["request", "params"],
            request=NonCallableMock(
                spec_set=["base_url"], base_url=public_base_url
            )
            if public_base_url
            else None,
            params=SimpleNamespace(
                arguments={"project_root": asserted_project_root}
            ),
        )
        try:
            if name in self.gateway.tool_blacklist:
                raise _tool_fault("tool_unavailable", "Unknown Tool")
            value = await self.registry.call(name, arguments, context=context)
            text = (
                value.get("csv")
                if name in {"query_run", "query_template", "query_page"}
                else None
            )
            if name in {"local_release_command", "public_release_command"}:
                text = value.get("command")
            return {"value": value, "text": text}
        except ExplicitBlockingRuntimeFailure as error:
            raise _tool_fault(error.code, str(error), emit=True) from error
        except ToolInputValidationError as error:
            raise _tool_fault("tool_input_invalid", str(error)) from error
        except ToolRegistryStaleError as error:
            raise _tool_fault("tool_registry_stale", str(error)) from error
        except ToolOutputValidationError as error:
            raise _tool_fault("tool_output_invalid", str(error)) from error
        except ToolRegistryRuntimeError as error:
            raise _tool_fault("tool_unavailable", str(error)) from error

    async def close(self):
        if self.registry is not None:
            await self.registry.close()


class WorkbenchTools:
    def __init__(self, *, query_owner):
        self._query_owner = query_owner
        self._operations = WorkbenchOperations(query_owner=query_owner)

    async def call(self, name, arguments):
        try:
            return await asyncio.to_thread(
                self._operations.call, name, arguments
            )
        except WorkbenchUnavailableError as error:
            raise ExplicitBlockingRuntimeFailure(
                "workbench_unavailable",
                "Workbench unavailable; restart required",
            ) from error
        except (ValueError, QueryExecutionError) as error:
            raise ExplicitBlockingRuntimeFailure(
                "query_error", str(error)
            ) from error

    async def call_tool(self, name, arguments, **kwargs):
        return await self.tool_client.call_tool(name, arguments, **kwargs)

    async def release_command(self, name, arguments):
        from IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IWE_CONSOLE_BACKEND.\
            backend_process \
            import _release_command  # fmt: skip

        return await asyncio.to_thread(
            _release_command, self._query_owner.selection, name, arguments
        )

    async def close(self):
        if hasattr(self, "tool_client"):
            await self.tool_client.close()
        await asyncio.to_thread(self._operations.close)


def local_gateway(root, *, native_query):
    from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import DirectGateway

    gateway = DirectGateway(
        root,
        native_query=native_query,
        workbench=WorkbenchTools(query_owner=native_query),
    )
    gateway._tool_client = FixtureToolClient(gateway)
    gateway.workbench.tool_client = gateway._tool_client
    return gateway


def create_native_gateway(root, control_root, inputs):
    selection = resolve_native_project(
        root,
        control_root,
        validate_manifest=inputs.validate_manifest,
        require_atom_state=inputs.require_atom_state,
        require_atom_header=inputs.require_atom_header,
    )
    return local_gateway(
        selection.root, native_query=NativeQueryOwner(selection, inputs)
    )


def load_native_inputs(selection, *, model=None):
    if model is None:
        from KERNEL_MIXER_C59.MANIFEST_RUNTIME_C62.model_host_CS2.\
            model_host_CS2__shared \
            import reviewed_native_model  # fmt: skip

        model = reviewed_native_model()
    return NativeQueryInputs(
        model.validate_manifest,
        model.relation_types,
        model.inverses,
        require_atom_state=model.requires_atom_state,
        require_atom_header=model.requires_atom_header,
        ticket_labels=model.ticket_labels,
        validate_project_spec=model.validate_project_spec,
    )
