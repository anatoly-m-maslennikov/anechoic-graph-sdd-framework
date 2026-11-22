"""Coordinate stateless Beta Project requests over a private Unix socket."""
import argparse
import asyncio
from copy import deepcopy
import os

from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__pub import mcp_tool_blacklist
from .project_admission__pub import select_runtime_project
from .shared_host_config import load
from .shared_host_process import run
from .WORKBENCH_BACKEND_beta_C70__pub import _TOOL, serve, socket_path


def fault(code, *, scope='project', project=None, tool_result=None, message=None):
    error = {'code': code, 'message': message or code, 'scope': scope}
    if scope == 'tool':
        error['tool_result'] = tool_result
    return JSONResponse({'error': error, 'project': project})


def public_tool():
    tool = deepcopy(_TOOL)
    schema = tool['inputSchema']
    schema['properties']['project_root'] = {'type': 'string', 'minLength': 1}
    schema['properties']['caller_context'] = {'type': 'object', 'properties': {
        'session_id': {'type': 'string', 'minLength': 1, 'pattern': '\\S'}},
        'required': ['session_id'], 'additionalProperties': False}
    schema['required'].append('project_root')
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
    def __init__(self, config):
        self.config = config
        self.lock = asyncio.Lock()
        self.active = 0
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
            return select_runtime_project(path)
        except ValueError as error:
            if str(error) in ('outside_project_root', 'invalid_project_root'):
                raise
            raise ValueError('invalid_project_root') from error
        except (OSError, RuntimeError, TypeError):
            raise ValueError('invalid_project_root') from None

    async def health(self, _request):
        return JSONResponse({'result': {'pid': os.getpid(), 'initialized': True,
            'shared_runtime_id': self.config.runtime_id, 'advertised_tools': ['query_run'],
            'known_project_contexts': list(self.known.values()), 'warnings': [],
            'max_loaded_projects': self.config.maximum, 'loaded_project_count': self.active}})

    async def catalog(self, _request):
        return JSONResponse({'result': {'tools': [public_tool()]}})

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
        acquired = False
        try:
            data = await request.json()
            _validate_invocation(data)
            selected = await asyncio.to_thread(self.select, data['arguments']['project_root'])
            if data['name'] != 'query_run' or data['name'] in mcp_tool_blacklist(selected.parameters):
                raise ValueError('tool_unavailable')
            async with self.lock:
                if self.active >= self.config.maximum:
                    raise ValueError('project_gateway_busy')
                self.active += 1
                acquired = True
            project = {'prefix': selected.project_prefix, 'instance_id': selected.instance_id}
            self.known[selected.instance_id] = project
            if len(self.known) > 32:
                self.known.pop(next(iter(self.known)))
            native = {k: v for k, v in data['arguments'].items() if k != 'project_root'}
            wire = {'name': data['name'], 'arguments': native, 'instance_id': selected.instance_id,
                    'session_id': data['session_id'], 'public_base_url': data['public_base_url'],
                    'asserted_project_root': str(selected.root)}
            result = await run(selected, wire)
            again = await asyncio.to_thread(self.select, str(selected.root))
            if again != selected:
                raise ValueError('project_declarations_stale')
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
        finally:
            if acquired:
                async with self.lock:
                    self.active -= 1


def create_app(config):
    coordinator = Coordinator(config)
    return Starlette(routes=[Route('/health', coordinator.health), Route('/tools', coordinator.catalog),
        Route('/selection', coordinator.selection, methods=['POST']), Route('/tools', coordinator.invoke, methods=['POST'])])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--socket', required=True)
    parser.add_argument('--host-settings')
    args = parser.parse_args()
    serve(socket_path(args.socket), create_app(load(args.host_settings)))


if __name__ == '__main__':
    main()
