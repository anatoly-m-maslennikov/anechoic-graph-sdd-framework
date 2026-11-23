"""Coordinate stateless Beta Project requests over a private Unix socket."""
import argparse
import asyncio
import os
from contextlib import asynccontextmanager, nullcontext
from copy import deepcopy
from dataclasses import replace

from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from .project_admission import AdmissionClient
from .peer_transport import tool_failure
from .shared_host_config import load
from .shared_peer_owner import PeerOwnerClient
from .shared_project_pool import SharedProjectPool
from .warm_worker import open_warm_worker
from .WORKBENCH_BACKEND_beta_C70__shared import (
    TOOLS,
    execute_tool,
    read_tool_request,
    serve,
    socket_path,
)


def fault(code, *, scope='project', project=None, tool_result=None, message=None):
    error = {'code': code, 'message': message or code, 'scope': scope}
    if scope == 'tool':
        error['tool_result'] = tool_result
    return JSONResponse({'error': error, 'project': project})


def public_tool(native):
    tool = deepcopy(native)
    schema = tool['inputSchema']
    schema['properties']['project_root'] = {'type': 'string', 'minLength': 1}
    schema['properties']['caller_context'] = {'type': 'object', 'properties': {
        'session_id': {'type': 'string', 'minLength': 1, 'pattern': '\\S'}},
        'required': ['session_id'], 'additionalProperties': False}
    schema.setdefault('required', []).append('project_root')
    return tool


def _validate_invocation(data):
    if (not isinstance(data, dict) or set(data) != {'name', 'arguments', 'session_id', 'public_base_url'}
            or not isinstance(data['name'], str) or not data['name']
            or any(data[k] is not None and (not isinstance(data[k], str) or not data[k].strip())
                   for k in ('session_id', 'public_base_url'))):
        raise ValueError('invalid_tool_request')
    if not isinstance(data['arguments'], dict) or 'project_root' not in data['arguments']:
        raise ValueError('missing_project_root')


class Coordinator:
    def __init__(self, config, peer_owner=None):
        self.config = config
        self.pool = PeerOwnerClient(peer_owner) if peer_owner else SharedProjectPool(config.maximum)
        self.admission = AdmissionClient()
        self.known = {}

    def current(self):
        try:
            current = load(self.config.source)
        except (OSError, ValueError, TypeError):
            raise ValueError('host_configuration_invalid') from None
        if current != self.config:
            raise ValueError('host_configuration_stale')

    def select(self, root):
        self.current()
        try:
            path = self.config.project(root)
            selected = self.admission(path)
            parameters = deepcopy(selected.parameters)
            runtime = parameters.setdefault("runtime", {})
            runtime.setdefault("workbench", {}).setdefault("storage", self.config.workbench_storage)
            runtime.setdefault("journal", {}).setdefault("storage", self.config.journal_storage)
            return replace(selected, parameters=parameters)
        except ValueError as error:
            if str(error) in ('outside_project_root', 'invalid_project_root'):
                raise
            raise ValueError('invalid_project_root') from error
        except (OSError, RuntimeError, TypeError):
            raise ValueError('invalid_project_root') from None

    async def health(self, _request):
        pool_status = await self.pool.status() if isinstance(self.pool, PeerOwnerClient) else self.pool.status()
        return JSONResponse({'result': {'pid': os.getpid(), 'initialized': True,
            'shared_runtime_id': self.config.runtime_id, 'advertised_tools': list(TOOLS),
            'known_project_contexts': list(self.known.values()), 'warnings': [],
            **pool_status}})

    async def catalog(self, _request):
        return JSONResponse({'result': {'tools': [public_tool(tool) for tool in TOOLS.values()]}})

    async def selection(self, request):
        try:
            data = await request.json()
            if not isinstance(data, dict) or set(data) != {'project_root'}:
                raise ValueError('invalid_project_root')
            selected = await asyncio.to_thread(self.select, data['project_root'])
            return JSONResponse({'result': {'project_name': selected.project_name,
                'project_prefix': selected.project_prefix, 'instance_id': selected.instance_id}})
        except (ValueError, TypeError) as error:
            return fault(str(error) if str(error) in ('outside_project_root', 'host_configuration_stale', 'host_configuration_invalid') else 'invalid_project_root')

    async def invoke(self, request):
        project = None
        try:
            data = await read_tool_request(request)
            _validate_invocation(data)
            selected = await asyncio.to_thread(self.select, data['arguments']['project_root'])
            if data['name'] not in TOOLS or data['name'] in selected.tool_blacklist:
                raise ValueError('tool_unavailable')
            project = {'prefix': selected.project_prefix, 'instance_id': selected.instance_id}
            self.known[selected.instance_id] = project
            if len(self.known) > 32:
                self.known.pop(next(iter(self.known)))
            result = await self._call(selected, data)
            if 'error' in result:
                error = result['error']
                return fault(error.get('code', 'internal'), scope='tool', project=project,
                             message=error.get('message'), tool_result=error.get('tool_result'))
            return JSONResponse({'result': result['result'], 'project': project})
        except ValueError as error:
            code = str(error)
            allowed = {'invalid_tool_request', 'missing_project_root', 'invalid_project_root', 'outside_project_root',
                       'host_configuration_stale', 'host_configuration_invalid', 'tool_unavailable',
                       'project_gateway_busy', 'project_declarations_stale'}
            return fault(code if code in allowed else 'shared_gateway_failure', project=project)
        except (OSError, RuntimeError, TypeError, TimeoutError):
            return fault('shared_gateway_failure', project=project)

    async def _call(self, selected, data):
        name = data["name"]
        native = {k: v for k, v in data["arguments"].items() if k != "project_root"}
        async with self.pool.lease(selected, start=name not in {"workbench_status", "workbench_abort"}) as peers:
            if peers is None:
                if name == "workbench_abort":
                    return await execute_tool(None, selected.instance_id, name, native)
                if native:
                    return tool_failure("tool_input_invalid", "The status request has no arguments")
                return {"result": {"value": {"mode": "unavailable", "syncing": False, "last_synced_at": None}, "text": None}}
            result = await execute_tool(peers.database_socket, selected.instance_id, name, native,
                                        session_id=data["session_id"], project_name=selected.project_name,
                                        public_base_url=data["public_base_url"], project_root=data["arguments"]["project_root"],
                                        orchestrator_socket=peers.orchestrator_socket, worker_binding=peers.worker_binding,
                                        workbench_public_url=selected.parameters["runtime"]["workbench"].get("public_url"))
            if await asyncio.to_thread(self.select, str(selected.root)) != selected:
                raise ValueError("project_declarations_stale")
            return result


def create_app(config, peer_owner=None):
    coordinator = Coordinator(config, peer_owner)

    @asynccontextmanager
    async def lifespan(_app):
        stop = getattr(_app.state, "shutdown_requested", None)
        with (nullcontext() if peer_owner else open_warm_worker(stop=stop)) as worker:
            if not peer_owner:
                coordinator.pool.warm_worker = worker
            try:
                yield
            finally:
                try:
                    if not peer_owner:
                        await coordinator.pool.close()
                finally:
                    await asyncio.to_thread(coordinator.admission.close)

    return Starlette(lifespan=lifespan, routes=[
        Route('/health', coordinator.health), Route('/tools', coordinator.catalog),
        Route('/selection', coordinator.selection, methods=['POST']), Route('/tools', coordinator.invoke, methods=['POST']),
    ])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--socket', required=True)
    parser.add_argument('--host-settings')
    parser.add_argument('--peer-owner-socket')
    args = parser.parse_args()
    serve(socket_path(args.socket), create_app(load(args.host_settings), args.peer_owner_socket), shutdown_timeout=3)


if __name__ == '__main__':
    main()
