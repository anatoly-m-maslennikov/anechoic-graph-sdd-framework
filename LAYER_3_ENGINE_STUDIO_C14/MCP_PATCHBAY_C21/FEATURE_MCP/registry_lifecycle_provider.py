"""MCP adapter for native Atom Lifecycle operations."""

from __future__ import annotations

import anyio
from mcp import types


_TOOLS = {
    'atom_lifecycle_create_draft': (
        'Create a Draft from a Current Atom or create a new Task or Epic Draft.',
        {'sourceCurrent': {}, 'changes': {}, 'newAtom': {}},
    ),
    'atom_lifecycle_archive': ('Archive an exact Current Ticket.', {'target': {}}),
    'atom_lifecycle_change_status': (
        'Change the Status of an exact Current Ticket.', {'target': {}, 'targetStatus': {}},
    ),
    'atom_lifecycle_direct_update': (
        'Update the Markdown body of a Ticket Asset.', {'target': {}, 'changes': {}},
    ),
    'atom_lifecycle_promote_draft': (
        'Publish an exact Draft revision at the requested Current Status.', {'target': {}, 'targetStatus': {}},
    ),
    'atom_lifecycle_update': (
        'Create a Draft revision of a Current Atom.', {'sourceCurrent': {}, 'changes': {}},
    ),
}
LIFECYCLE_TOOL_NAMES = frozenset(_TOOLS)


def _result(value):
    if value.get('outcome') == 'completed' and not value.get('errors'):
        return {'status': 'completed'}
    errors = value.get('errors') or [
        {'code': 'invalid_input', 'field': field, 'message': detail.get('error')}
        for field, detail in value.get('requested_input', {}).items()
    ] or [{'code': 'backend_failure', 'message': 'Lifecycle operation failed.'}]
    return {
        'status': 'blocked' if value.get('outcome') == 'blocked' else 'failed',
        'effects': value.get('effects', []),
        'errors': errors,
        'warnings': value.get('warnings', []),
    }


class NativeLifecycleProvider:
    def __init__(self, owner):
        self.owner = owner

    async def call(self, name, arguments):
        with anyio.CancelScope(shield=True):
            value = await anyio.to_thread.run_sync(self.owner.lifecycle, name, arguments)
        response = _result(value)
        if response['status'] == 'completed':
            if 'savedDraft' in value:
                response['savedDraft'] = value['savedDraft']
                if name == 'atom_lifecycle_update':
                    response['status'] = 'draft_created'
            if name == 'atom_lifecycle_promote_draft' and 'artifact' in value:
                response['artifact'] = value['artifact']
        return response

    async def close(self):
        pass



def create_provider(_root, gateway):
    owner = gateway._native_query
    if owner is None:
        raise ValueError('Atom Lifecycle Tools require a native Project.')
    return NativeLifecycleProvider(owner)


def tool_descriptors():
    return tuple(types.Tool(
        name=name, description=description,
        input_schema={'type': 'object', 'properties': fields, 'additionalProperties': True},
    ) for name, (description, fields) in _TOOLS.items())
