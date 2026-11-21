"""MCP adapter for native Atom Lifecycle operations."""

from __future__ import annotations

import re

import anyio
from mcp import types


_TOOLS = {
    'atom_lifecycle_create_draft': (
        'Create a Draft from a Current Atom or create a Task, Component Contract, Axiom, or Applicable Principle Draft. '
        'Use newAtom.label for Task navigation, such as Epic or Version.',
        {'sourceCurrent': {}, 'changes': {}, 'newAtom': {}},
    ),
    'atom_lifecycle_archive': (
        'Archive a replaced Ticket, retire an Active SPEC Atom, or archive a SPEC Draft. '
        'For multiple SPEC Drafts, pass query_run rows of [exact_ref, version] as targets.',
        {'target': {}, 'targets': {'type': 'array', 'items': {'type': 'array', 'minItems': 2, 'maxItems': 2}}},
    ),
    'atom_lifecycle_create_asset': (
        'Create a Ticket Asset. Supply newAtom.template, newAtom.body and an optional Task or Epic container.',
        {'newAtom': {}},
    ),
    'atom_lifecycle_change_status': (
        'Change a Current Ticket Status or start implementation of a Ready SPEC Atom.',
        {'target': {}, 'targetStatus': {}},
    ),
    'atom_lifecycle_direct_update': (
        'Update the Markdown body of a Ticket Asset.', {'target': {}, 'changes': {}},
    ),
    'atom_lifecycle_promote_draft': (
        'Publish an exact Draft revision. Finalize a SPEC Draft with targetStatus ready.',
        {'target': {}, 'targetStatus': {}},
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
            if name == 'atom_lifecycle_archive' and 'targets' in arguments:
                return await anyio.to_thread.run_sync(self._archive_targets, arguments)
            value = await anyio.to_thread.run_sync(self.owner.lifecycle, name, arguments)
        response = _result(value)
        if response['status'] == 'completed':
            if 'savedDraft' in value:
                response['savedDraft'] = value['savedDraft']
                if name == 'atom_lifecycle_update':
                    response['status'] = 'draft_created'
            if 'artifact' in value and name != 'atom_lifecycle_direct_update':
                response['artifact'] = value['artifact']
            if 'sourceRef' in value:
                response['sourceRef'] = value['sourceRef']
        return response

    def _archive_targets(self, arguments):
        rows = arguments['targets']
        if (set(arguments) != {'targets'} or not isinstance(rows, list) or not rows or any(
                not isinstance(row, list) or len(row) != 2 or not isinstance(row[0], str)
                or type(row[1]) is not int or row[1] < 1
                or not re.fullmatch(r'[A-Z]+-S-[0-9]+@' + str(row[1]) + r'-draft', row[0])
                for row in rows) or len({row[0] for row in rows}) != len(rows)):
            return {'status': 'failed', 'errors': [{'code': 'invalid_input', 'field': 'targets',
                    'message': 'Supply distinct exact SPEC Draft references and matching Versions.'}]}
        outcomes = []
        for ref, version in rows:
            value = self.owner.lifecycle('atom_lifecycle_archive', {'target': {'ref_id': ref, 'version': version}})
            report = _result(value)
            if 'artifact' in value and report['status'] == 'completed':
                report['artifact'] = value['artifact']
            outcomes.append({'sourceRef': ref, **report})
        return {'status': 'completed' if all(item['status'] == 'completed' for item in outcomes) else 'failed',
                'results': outcomes}

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
