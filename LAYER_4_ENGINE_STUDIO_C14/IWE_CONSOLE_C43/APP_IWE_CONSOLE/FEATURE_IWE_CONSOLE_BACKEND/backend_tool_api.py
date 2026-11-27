"""Serve the Project's Tool catalog and dispatch from the same registry."""

import asyncio
import logging
from concurrent.futures import CancelledError as FutureCancelledError
from pathlib import Path
from types import SimpleNamespace

import anyio
from starlette.responses import JSONResponse

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__shared import ExplicitBlockingRuntimeFailure, FailureRecord, report_failure
from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import QueryExecutionError, WorkbenchUnavailableError

from .project_admission import pinned_project, project_tool_policy
from .tool_registry_runtime import (
    ToolInputValidationError, ToolOutputValidationError, ToolRegistryRuntimeError,
    ToolRegistryStaleError, load_active_registry,
)


_RELEASE = frozenset({"local_release_command", "public_release_command"})
_CSV = frozenset({"query_template", "query_run", "query_page"})
_FIELDS = {"name", "arguments", "instance_id", "session_id", "public_base_url", "asserted_project_root"}
_LOG = logging.getLogger(__name__)
_ERRORS = (
    (ToolRegistryStaleError, "tool_registry_stale"),
    (ToolInputValidationError, "tool_input_invalid"),
    (ToolOutputValidationError, "tool_output_invalid"),
    (ToolRegistryRuntimeError, "tool_runtime_failure"),
    (QueryExecutionError, "query_error"),
    (WorkbenchUnavailableError, "workbench_unavailable"),
    (ValueError, "value_error"),
)


def tool_failure_result(code, message, *, emit=False):
    rejected = code in {"tool_input_invalid", "tool_registry_stale", "tool_unavailable"}
    diagnostic_code = "query_error" if code == "value_error" else code
    if rejected:
        diagnostic = "Unknown Tool" if code == "tool_unavailable" else code
    else:
        if code == "tool_output_invalid":
            message = "Tool output does not match its schema"
        diagnostic = f"{diagnostic_code}: {message}"
    diagnostics = [diagnostic]
    if emit:
        _, secondary = report_failure(
            None, FailureRecord("WARNING" if rejected else "ERROR", diagnostic_code, "Backend Tool request failed"),
            component="WORKBENCH_BACKEND", operation="tool_api",
        )
        if secondary is not None and not rejected:
            diagnostics.append("technical diagnostic unavailable")
    return {"outcome": "rejected" if rejected else "failed", "diagnostics": diagnostics}


def _failure(code, message, *, emit=False, status_code=200):
    value = tool_failure_result(code, message, emit=emit)
    return JSONResponse({"error": {"code": code, "message": message, "tool_result": value}},
                        status_code=status_code)


def _context(value, selection):
    base, root = value["public_base_url"], value["asserted_project_root"]
    if root is not None and root not in {
        str(path) for path in (selection.root, selection.host_root) if path is not None
    }:
        raise ValueError("project_root does not match the bound Project")
    request = SimpleNamespace(base_url=base) if base is not None else None
    return SimpleNamespace(  # pragma: anechoic-model-adapter - tool context
        request=request, params={"arguments": {"project_root": root}},
    )


class BackendToolAPI:
    def __init__(self, owner, methods):
        self._owner = owner
        self._methods = methods
        self._lock = asyncio.Lock()
        self._registry = None

    def _load(self):
        try:
            selection = pinned_project(self._owner.selection)
        except ValueError as error:
            raise ToolRegistryStaleError("Project binding changed") from error
        workbench = SimpleNamespace(  # pragma: anechoic-model-adapter - workbench interface
            call=self._workbench, release_command=self._release,
        )
        provider_context = SimpleNamespace(  # pragma: anechoic-model-adapter - registry interface
            selection=selection, workbench=workbench, _native_query=self._owner,
        )
        registry = load_active_registry(Path(__file__).parent, selection.root, provider_context)
        exclusions, release_enabled = project_tool_policy(selection.parameters)
        blacklist = registry.global_blacklist | frozenset(exclusions)
        if not release_enabled:
            blacklist |= _RELEASE
        if blacklist & {"workbench_status", "iwe_console_status"}:
            blacklist |= {"workbench_status", "iwe_console_status"}
        if "query_run" in blacklist:
            blacklist |= {"query_template"}
        return registry, selection, blacklist

    async def _active(self):
        async with self._lock:
            if self._registry is None:
                self._registry, self._selection, self._blacklist = await anyio.to_thread.run_sync(self._load)
        return self._registry

    async def _workbench(self, name, arguments):
        return await anyio.to_thread.run_sync(self._methods["workbench"], name, arguments)

    async def _release(self, name, arguments):
        return await anyio.to_thread.run_sync(self._methods["release_command"], name, arguments)

    async def catalog(self, request):
        if request.query_params.getlist("instance_id") != [self._owner.selection.instance_id]:
            return _failure("value_error", "Invalid Tool request binding")
        try:
            registry = await self._active()
            registry.ensure_current()
            tools = [tool.model_dump(by_alias=True, mode="json")
                     for tool in registry.tools if tool.name not in self._blacklist]
            return JSONResponse({"result": {"tools": tools, "blacklist": sorted(self._blacklist)}})
        except ToolRegistryStaleError:
            return _failure("tool_registry_stale", "Tool registry changed")
        except (ToolRegistryRuntimeError, ValueError) as error:
            _LOG.error("Backend Tool catalog unavailable: %s", type(error).__name__)
            return _failure("tool_runtime_failure", "Backend Tool registry is unavailable")

    def _admit(self, value):
        if (not isinstance(value, dict) or set(value) != _FIELDS
                or value["instance_id"] != self._owner.selection.instance_id
                or not isinstance(value["name"], str)
                or not isinstance(value["arguments"], dict)
                or any(value[key] is not None and (
                    not isinstance(value[key], str) or not value[key].strip()
                ) for key in ("session_id", "public_base_url", "asserted_project_root"))):
            raise ValueError("Invalid Tool request envelope")
        return value

    async def invoke(self, request):
        try:
            envelope = self._admit(await request.json())
            registry = await self._active()
            registry.ensure_current()
            name = envelope["name"]
            if name in self._blacklist or not registry.permits(name):
                return _failure("tool_unavailable", "Unknown Tool")
            with anyio.CancelScope(shield=True):
                value = await registry.call(name, envelope["arguments"], context=_context(envelope, self._selection))
            text = value.get("command") if name in _RELEASE else value.get("csv") if name in _CSV else None
            return JSONResponse({"result": {"value": value, "text": text}})
        except FutureCancelledError:
            raise
        except ExplicitBlockingRuntimeFailure as error:
            return _failure(error.code, str(error), emit=True)
        except Exception as error:
            for kind, code in _ERRORS:
                if isinstance(error, kind):
                    status = 400 if code in {"tool_input_invalid", "value_error"} else 200
                    return _failure(code, str(error), emit=True, status_code=status)
            return _failure("internal", "Backend Tool operation failed", emit=True, status_code=500)

    async def close(self):
        if self._registry is not None:
            await self._registry.close()
