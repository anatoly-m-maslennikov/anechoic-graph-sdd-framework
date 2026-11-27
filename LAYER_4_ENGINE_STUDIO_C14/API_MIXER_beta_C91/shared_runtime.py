"""Serve shared-host query Tools using the supervised Project peer owner."""

import argparse
import os
from pathlib import Path

import httpx2
from pydantic import ValidationError
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from ._shared_runtime_support import (
    TOOL_REST_PATH,
    Invocation,
    SelectionRequest,
    fault,
    owner_fault,
    public_tool,
    tool_unavailable,
)
from .API_MIXER_beta_C91__shared import serve, socket_path
from . import atom_document, lifecycle, projection, saved_sql
from .admission import failure, peer
from .api import (
    LIFECYCLE_TOOLS,
    PROJECTION_TOOLS,
    body,
    descriptors,
    execute_core,
)
from .models import JobsHealth, KernelHealth
from .owner_client import Owner
from .schema import read_schema


def bound_binding(binding, lease):
    worker = lease.worker_binding
    if (
        worker.root != binding.root
        or worker.control_root != binding.control_relative
        or worker.manifest_path
        != str(Path(binding.manifest_path).relative_to(binding.root))
        or worker.manifest_sha256 != binding.manifest_sha256
        or worker.project_prefix != binding.project_prefix
    ):
        raise ValueError("project_declarations_stale")


async def bound_health(binding, lease):
    bound_binding(binding, lease)
    kernel = KernelHealth.model_validate(
        (await peer(lease.database_socket, "GET", "/health"))["result"]
    )
    jobs = JobsHealth.model_validate(
        (await peer(lease.orchestrator_socket, "GET", "/health"))["result"]
    )
    if (
        kernel.instance_id != binding.instance_id
        or kernel.manifest_sha256 != binding.manifest_sha256
        or jobs.instance_id != binding.instance_id
    ):
        raise ValueError("project_declarations_stale")
    if (
        not kernel.ready
        or not kernel.generation
        or jobs.startup_replay_pending
        or not jobs.watcher_active
    ):
        return failure(
            "project_build_unavailable",
            "The Project projection is unavailable",
        )
    return None


class Coordinator:
    def __init__(self, owner):
        self.owner = Owner(owner)
        self.tools = descriptors()
        self.known = {}

    async def health(self, _request):
        try:
            status = (await self.owner.status()).model_dump()
        except OSError, RuntimeError, ValueError, TimeoutError:
            return fault("shared_gateway_failure", status=503)
        return JSONResponse(
            {
                "result": {
                    "pid": os.getpid(),
                    "initialized": True,
                    "shared_runtime_id": os.environ.get(
                        "ANECHOIC_SHARED_RUNTIME_ID"
                    ),
                    "advertised_tools": list(self.tools),
                    "known_project_contexts": list(self.known.values()),
                    "warnings": [],
                    **status,
                }
            }
        )

    async def catalog(self, _request):
        return JSONResponse(
            {
                "result": {
                    "tools": [
                        public_tool(tool) for tool in self.tools.values()
                    ]
                }
            }
        )

    async def selection(self, request):
        try:
            data = SelectionRequest.model_validate_json(await body(request))
        except ValidationError, ValueError, TypeError:
            return fault("invalid_project_root")
        try:
            selected = await self.owner.select(data.project_root)
            return JSONResponse(
                {
                    "result": {
                        "project_name": selected.project_name,
                        "project_prefix": selected.project_prefix,
                        "instance_id": selected.instance_id,
                    }
                }
            )
        except (ValueError, OSError, RuntimeError, TimeoutError) as error:
            return owner_fault(error)

    async def invoke(self, request):
        project = None
        try:
            try:
                data = Invocation.model_validate_json(await body(request))
            except ValidationError, ValueError, TypeError:
                return fault("invalid_tool_request")
            arguments = (data.arguments or {}).copy()
            if "project_root" not in arguments:
                return fault("missing_project_root")
            root = arguments.pop("project_root", None)
            if not isinstance(root, str) or not root.strip():
                return fault("invalid_project_root")
            selected = await self.owner.select(root)
            expected = request.headers.get("X-Anechoic-Project-Instance")
            if expected is not None and expected != selected.instance_id:
                return fault("project_declarations_stale")
            if tool_unavailable(data.name, selected, self.tools):
                return fault("tool_unavailable")
            project = {
                "prefix": selected.project_prefix,
                "instance_id": selected.instance_id,
            }
            self.known[selected.instance_id] = project
            if len(self.known) > 32:
                self.known.pop(next(iter(self.known)))
            return await self.invoke_selected(
                data, arguments, root, selected, project
            )
        except (
            OSError,
            RuntimeError,
            ValueError,
            TypeError,
            KeyError,
            TimeoutError,
            httpx2.HTTPError,
        ) as error:
            return owner_fault(error, project=project)

    async def invoke_selected(self, data, arguments, root, selected, project):
        async with self.owner.lease(
            selected,
            start=data.name
            not in {
                "iwe_console_status",
                "iwe_console_abort",
                "workbench_status",
                "workbench_abort",
            },
        ) as lease:
            result = await self.execute(
                selected,
                lease,
                data.name,
                arguments,
                data.public_base_url,
                root,
                data.session_id,
            )
            await self.revalidate(selected)
        if "error" in result:
            error = result["error"]
            return fault(
                error["code"],
                scope="tool",
                project=project,
                message=error["message"],
                tool_result=error["tool_result"],
                status=503
                if error["code"] == "workbench_unavailable"
                else 200,
            )
        return JSONResponse({"result": result["result"], "project": project})

    async def execute(
        self, selected, lease, name, arguments, base, root, session
    ):
        if name in PROJECTION_TOOLS:
            if lease is not None:
                bound_binding(selected, lease)
            return await projection.invoke(
                name,
                arguments,
                lease.database_socket if lease else None,
                lease.orchestrator_socket if lease else None,
                lease.worker_binding.model_dump() if lease else None,
                selected.instance_id,
            )
        if lease is None:
            return failure(
                "project_build_unavailable",
                "The Project projection is unavailable",
            )
        if name in LIFECYCLE_TOOLS:
            bound_binding(selected, lease)
            return await lifecycle.invoke(
                name,
                arguments,
                lease.orchestrator_socket,
                lease.worker_binding.model_dump(),
                selected.instance_id,
            )
        unavailable = await bound_health(selected, lease)
        if unavailable:
            return unavailable
        if name == atom_document.NAME:
            return await atom_document.invoke(
                arguments,
                lease.orchestrator_socket,
                lease.worker_binding.model_dump(),
                selected.instance_id,
            )
        if name == "query_schema":
            return await read_schema(
                lease.database_socket, selected.instance_id, arguments
            )
        return await self.execute_query(
            selected, lease, name, arguments, base, root, session
        )

    async def execute_query(
        self, selected, lease, name, arguments, base, root, session
    ):
        runtime = selected.parameters.get("runtime", {})
        configured = runtime.get(
            "iwe_console", runtime.get("workbench", {})
        ).get("public_url")
        if not isinstance(configured, str):
            configured = None
        context = saved_sql.LinkContext(
            project_name=selected.project_name,
            base=base,
            root=root,
            configured_url=configured,
        )
        return await execute_core(
            lease.database_socket,
            selected.instance_id,
            name,
            arguments,
            context,
            session,
        )

    async def revalidate(self, selected):
        try:
            current = await self.owner.select(selected.root)
        except ValueError as error:
            if str(error) in {
                "host_configuration_stale",
                "host_configuration_invalid",
            }:
                raise
            raise ValueError("project_declarations_stale") from error
        if current != selected:
            raise ValueError("project_declarations_stale")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--socket", required=True)
    parser.add_argument("--host-settings")
    parser.add_argument("--peer-owner-socket", required=True)
    args = parser.parse_args()
    coordinator = Coordinator(args.peer_owner_socket)
    app = Starlette(
        routes=[
            Route("/health", coordinator.health),
            Route(TOOL_REST_PATH, coordinator.catalog),
            Route("/selection", coordinator.selection, methods=["POST"]),
            Route(TOOL_REST_PATH, coordinator.invoke, methods=["POST"]),
        ]
    )
    serve(socket_path(args.socket), app)


if __name__ == "__main__":
    main()
