"""Return host commands for the Project release entry point."""
from __future__ import annotations

from pathlib import Path
import re
import shlex

from mcp import types


RELEASE_COMMAND_TOOLS = frozenset({'local_release_command', 'public_release_command'})


class ReleaseCommandProvider:
    def __init__(self, project_root, gateway):
        selection = getattr(gateway, 'selection', None)
        self.root = Path(getattr(selection, 'host_root', None) or project_root)
        if not self.root.is_absolute():
            raise ValueError('Release command requires an absolute Project root')

    async def call(self, name, arguments):
        if name not in RELEASE_COMMAND_TOOLS:
            raise ValueError('Unknown release command Tool')
        public = name == 'public_release_command'
        if set(arguments) - ({'run_id', 'base', 'head', 'content_draft'} if public else {'run_id'}):
            raise ValueError('Unexpected release command input')
        run_id = arguments.get('run_id')
        pattern = r'[A-Za-z0-9][A-Za-z0-9._:-]*' if public else r'[A-Za-z0-9][A-Za-z0-9._-]*'
        if not isinstance(run_id, str) or re.fullmatch(pattern, run_id) is None:
            raise ValueError('release-run-id-invalid')
        args = ['uv', 'run', '--project', str(self.root), '--locked', '--no-sync',
                '--python', '3.14', '--managed-python', '--no-env-file', '--all-groups',
                'python', '-B', str(self.root / 'LAYER_5_FRAMEWORK_DELIVERY/release.py'),
                'public' if public else 'local', '--project-root', str(self.root), '--run-id', run_id]
        for key in ('base', 'head', 'content_draft'):
            if key in arguments:
                value = arguments[key]
                if not isinstance(value, str) or not value or '\0' in value or value.startswith('-'):
                    raise ValueError(f'{key}-invalid')
                args.extend((f"--{key.replace('_', '-')}", value))
        env = shlex.quote(str(self.root / '.anechoic_runtime/launcher-venv'))
        return {'working_directory': str(self.root),
                'command': f'UV_PROJECT_ENVIRONMENT={env} {shlex.join(args)}'}

    async def close(self):
        return None


def create_provider(project_root, gateway):
    return ReleaseCommandProvider(project_root, gateway)


def tool_descriptors():
    run_id = {'type': 'string', 'description': 'Operator-selected release run ID.'}
    return tuple(types.Tool(
        name=name,
        description=f"Return the host uv command for {'Public Release' if name == 'public_release_command' else 'Local Release'}.",
        input_schema={'type': 'object', 'properties': {
            'run_id': run_id,
            **({'base': {'type': 'string', 'description': 'PR base Git ref. Defaults to origin/main.'},
                'head': {'type': 'string', 'description': 'PR head Git ref. Defaults to amm/dev.'},
                'content_draft': {'type': 'string', 'description': 'Host path to the reviewed changelog evidence JSON.'}}
               if name == 'public_release_command' else {}),
        }, 'required': ['run_id'], 'additionalProperties': False},
    ) for name in sorted(RELEASE_COMMAND_TOOLS))
