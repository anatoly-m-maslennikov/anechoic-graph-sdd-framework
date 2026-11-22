"""Coordinate Tool calls across admitted Projects over a private Unix socket."""

from __future__ import annotations

import argparse
import asyncio
from contextlib import asynccontextmanager
from functools import partial
import logging
import os
import threading

from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
import uvicorn

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import ProjectSelectionError

from .backend_process import _socket_path, _watch_parent
from .backend_tool_api import tool_failure_result
from .host_runtime_config import (
    HostRuntimeConfigError, OutsideProjectRootError, _canonical_directory,
    load_host_runtime_config, resolve_host_project,
)
from .project_tool_session import ProjectToolSession, ToolProtocolError
from .shared_project_catalog import contract_digest, discover_frontier, native_tools
from .shared_project_pool import ProjectCapacityError, SharedProjectPool


_LOG = logging.getLogger(__name__)
_FIELDS = {"name", "arguments", "session_id", "public_base_url"}


class SharedProjectRefusal(ValueError):
    pass


def _fault(code, *, message=None, scope="project", project=None, tool_result=None):
    error = {"code": code, "message": message or code, "scope": scope}
    if scope == "tool":
        error["tool_result"] = tool_result if tool_result is not None else tool_failure_result(code, message or code)
    return JSONResponse({
        "error": error,
        "project": project,
    })


def _envelope(value):
    if (not isinstance(value, dict) or set(value) != _FIELDS
            or not isinstance(value["name"], str) or not value["name"]
            or any(value[key] is not None and (
                not isinstance(value[key], str) or not value[key].strip()
            ) for key in ("session_id", "public_base_url"))):
        raise SharedProjectRefusal("invalid_tool_request")
    if not isinstance(value["arguments"], dict) or "project_root" not in value["arguments"]:
        raise SharedProjectRefusal("missing_project_root")
    return value


class SharedBackend:
    def __init__(self, config, gateway_factory=None):
        self.config = config
        factory = gateway_factory or partial(
            ProjectToolSession, workbench_storage=config.workbench_storage,
            journal_storage=config.journal_storage,
        )
        self.pool = SharedProjectPool(config.max_loaded_projects, factory)
        self.frontier = None
        self._known_projects = {}

    async def initialize(self):
        self.frontier = await discover_frontier(self.config, self.pool.gateway_factory)

    async def close(self):
        self.frontier = None
        await self.pool.close()

    def status(self):
        frontier = self.frontier
        return {
            "pid": os.getpid(),
            "shared_runtime_id": self.config.shared_runtime_id,
            "initialized": frontier is not None,
            "advertised_tools": sorted(frontier.tools) if frontier is not None else [],
            "warnings": list(frontier.warnings) if frontier is not None else [],
            "known_project_contexts": list(self._known_projects.values()),
            **self.pool.status(),
        }

    def _current_config(self):
        try:
            current = load_host_runtime_config(self.config.source_path)
        except HostRuntimeConfigError as error:
            raise SharedProjectRefusal("host_configuration_invalid") from error
        if current != self.config:
            raise SharedProjectRefusal("host_configuration_stale")

    def select(self, value):
        if not isinstance(value, str):
            raise SharedProjectRefusal("invalid_project_root")
        try:
            return resolve_host_project(self.config, value)
        except OutsideProjectRootError as error:
            raise SharedProjectRefusal("outside_project_root") from error
        except (HostRuntimeConfigError, ProjectSelectionError) as error:
            raise SharedProjectRefusal("invalid_project_root") from error

    async def select_project(self, request):
        try:
            value = await request.json()
            if not isinstance(value, dict) or set(value) != {"project_root"}:
                raise SharedProjectRefusal("invalid_project_root")
            self._current_config()
            binding = await asyncio.to_thread(self.select, value["project_root"])
            return JSONResponse({"result": {
                "project_name": binding.project_name,
                "project_prefix": binding.project_prefix,
                "instance_id": binding.instance_id,
            }})
        except SharedProjectRefusal as error:
            return _fault(str(error))
        except (OSError, RuntimeError, TypeError, ValueError):
            return _fault("invalid_project_root")

    def _cached_root(self, value):
        if not isinstance(value, str):
            raise SharedProjectRefusal("invalid_project_root")
        try:
            root = _canonical_directory(value)
        except HostRuntimeConfigError as error:
            raise SharedProjectRefusal("invalid_project_root") from error
        if (root != self.config.projects_root if self.config.single_project else
                root == self.config.projects_root or not root.is_relative_to(self.config.projects_root)):
            raise SharedProjectRefusal("outside_project_root")
        return root

    async def _lease(self, value, name):
        self._current_config()
        if name.startswith("atom_lifecycle_"):
            cached = await self.pool.acquire_cached(self._cached_root(value))
            if cached is not None:
                return cached, cached.selection
        selected = await asyncio.to_thread(self.select, value)
        return await self.pool.acquire(selected), selected

    async def _current_tool(self, entry, selection, name):
        if entry.selection != selection:
            raise SharedProjectRefusal("project_declarations_stale")
        try:
            await entry.gateway.ensure_current()
        except ToolProtocolError as error:
            if error.code == "tool_registry_stale":
                raise SharedProjectRefusal(error.code) from error
            raise
        advertised = self.frontier.tools.get(name)
        if advertised is None:
            raise SharedProjectRefusal("tool_unavailable")
        native = next((tool for tool in native_tools(entry.gateway) if tool["name"] == name), None)
        if native is None or contract_digest(native) != advertised.digest:
            raise SharedProjectRefusal("project_tool_frontier_stale")

    def _remember(self, selection):
        prefix, identity = selection.project_prefix, selection.instance_id
        project = {"prefix": prefix, "instance_id": identity}
        self._known_projects.pop(identity, None)
        self._known_projects[identity] = project
        if len(self._known_projects) > 32:
            self._known_projects.pop(next(iter(self._known_projects)))
        return project

    async def dispatch(self, envelope):
        entry = project = None
        try:
            if self.frontier is None:
                raise SharedProjectRefusal("shared_gateway_unavailable")
            name, arguments = envelope["name"], envelope["arguments"]
            source = arguments["project_root"]
            entry, selected = await self._lease(source, name)
            if not name.startswith("atom_lifecycle_"):
                selected = await asyncio.to_thread(self.select, str(selected.root))
            self._current_config()
            await self._current_tool(entry, selected, name)
            project = self._remember(selected)
            native = {key: value for key, value in arguments.items() if key != "project_root"}
            result = await entry.gateway.call_tool(
                name, native, session_id=envelope["session_id"], public_base_url=envelope["public_base_url"],
                asserted_project_root=source,
            )
            return JSONResponse({"result": result, "project": project})
        except SharedProjectRefusal as error:
            return _fault(str(error), project=project)
        except ProjectCapacityError:
            return _fault("project_gateway_busy", project=project)
        except ToolProtocolError as error:
            return _fault(error.code, message=str(error), scope="tool", project=project, tool_result=error.tool_result)
        except (OSError, RuntimeError, TypeError, ValueError) as error:
            _LOG.warning("Shared Backend request failed: %s", type(error).__name__)
            return _fault("shared_gateway_failure", project=project)
        finally:
            if entry is not None:
                await self.pool.release(entry)


def create_app(config, gateway_factory=None):
    backend = SharedBackend(config, gateway_factory)

    @asynccontextmanager
    async def lifespan(_app):
        try:
            await backend.initialize()
            yield
        finally:
            await backend.close()

    async def health(_request):
        return JSONResponse({"result": backend.status()})

    async def catalog(_request):
        tools = [entry.tool for entry in backend.frontier.tools.values()]
        return JSONResponse({"result": {"tools": tools}})

    async def invoke(request):
        try:
            envelope = _envelope(await request.json())
        except SharedProjectRefusal as error:
            return _fault(str(error))
        except (TypeError, ValueError):
            return _fault("invalid_tool_request")
        return await backend.dispatch(envelope)

    return Starlette(lifespan=lifespan, routes=[
        Route("/health", health), Route("/tools", catalog),
        Route("/selection", backend.select_project, methods=["POST"]),
        Route("/tools", invoke, methods=["POST"]),
    ])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--socket", required=True)
    parser.add_argument("--host-settings")
    args = parser.parse_args()
    config = load_host_runtime_config(args.host_settings)
    socket = _socket_path(args.socket)
    stopped = threading.Event()
    server = uvicorn.Server(uvicorn.Config(
        create_app(config), uds=str(socket), log_level="warning", timeout_graceful_shutdown=20,
    ))
    threading.Thread(target=_watch_parent, args=({"server": server}, stopped), daemon=True).start()
    if not stopped.is_set():
        server.run()


if __name__ == "__main__":
    main()
