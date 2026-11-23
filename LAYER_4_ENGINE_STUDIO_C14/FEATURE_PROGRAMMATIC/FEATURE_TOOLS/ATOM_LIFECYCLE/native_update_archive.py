"""Ticket body updates and archive operations."""
from __future__ import annotations

from hashlib import sha256
from functools import partial
import re


from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import native_header_view
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import native_ticket_asset, ARCHIVE_DIRECTORY, TICKET_DIRECTORY

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import capture_native
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import parse_carrier
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import CEILINGS, ReadContext

from . import effects
from .effects import _project_write_lock
from .common import InputError, SourceChanged, atom_summary, result, saved
from .source import bind_query_reader


from .native_update_selection import _select_ticket, _branch


def direct_update(selection, params, *, current_rows):
    from .native_update import _read_ticket

    if not isinstance(params, dict) or set(params) != {'target', 'changes'}:
        raise InputError('target', 'Supply one target and body change.')
    target, changes = params['target'], params['changes']
    if not isinstance(changes, dict) or set(changes) != {'body'} or not isinstance(changes['body'], str):
        raise InputError('changes', 'Supply only a Markdown body change.')
    selected, digest, path = _select_ticket(selection, target, current_rows, allow_draft=True)
    branch = path.relative_to(next((selection.control_root / name for name in (TICKET_DIRECTORY, '001_TICKETS', '__TKT') if path.is_relative_to(selection.control_root / name)), selection.control_root / TICKET_DIRECTORY)).parts[0]
    template = native_header_view(selected['header_json']).get('context', {}).get('template')
    linked_asset = branch in {'TASKS', 'ISSUES'} and native_ticket_asset(template)
    if branch != 'ASSETS' and not linked_asset:
        raise InputError('target', 'Direct body updates are limited to Ticket Assets.')
    with _project_write_lock(selection.root):
        raw, bounds, _, _ = _read_ticket(selection, target, selected, digest, path)
        old_body = raw[bounds[2]:].decode('utf-8')
        old_summary = atom_summary(re.sub(r'(?m)^#(?= Summary[ \t]*\r?$)', '##', old_body)).group(1)
        new_summary = atom_summary(re.sub(r'(?m)^#(?= Summary[ \t]*\r?$)', '##', changes['body'])).group(1)
        if old_summary != new_summary:
            raise InputError('summary', 'Changing a published Summary requires a new Atom ID.')
        with bind_query_reader(None):
            outcome = effects.replace(selection.root, path, digest,
                                      raw[:bounds[2]] + changes['body'].encode('utf-8'))
        data = {} if outcome.errors else {'artifact': saved(selection, path, selected['id'],
                                                              target['ref_id'], target['version'], selected['status'])}
        return result(effects=outcome.effects, errors=outcome.errors, **data)


def _check_replacement(selection, selected, replacements):
    if not replacements:
        capture = capture_native(selection)
        if capture.errors:
            raise SourceChanged('Native carrier capture is incomplete.')
        replacements.extend(row for row in capture.atoms if row.get('status_group') == 'Current'
                    and row.get('id') != selected['id']
                    and isinstance(row.get('header_json', {}).get('relations', {}).get('IS_REPLACEMENT_FOR'), list)
                    and selected['id'] in row['header_json']['relations']['IS_REPLACEMENT_FOR'])
    if not replacements:
        raise InputError('target', 'A different Current Atom must declare IS_REPLACEMENT_FOR this Ticket.')
    reader = ReadContext(roots=[str(selection.control_root)], limits=dict(CEILINGS))
    for row in replacements:
        raw = reader.read(selection.root / row['source_path'])
        if (sha256(raw).hexdigest() != row.get('_source_sha256')
                or parse_carrier(raw, selection.root / row['source_path']).metadata != row['header_json']):
            raise SourceChanged('Replacement source changed.')
    if reader.currentness()['state'] != 'unchanged':
        raise SourceChanged('Replacement source changed.')


def archive_ticket(selection, params, *, current_rows):
    from .native_update import _move_ticket, _read_ticket

    if not isinstance(params, dict) or set(params) != {'target'}:
        raise InputError('target', 'Supply one Ticket target.')
    target = params['target']
    selected, digest, path = _select_ticket(selection, target, current_rows, allow_draft=True)
    if 'atom_family' not in selected['header_json']:
        if selected['status_group'] != 'Current':
            raise InputError('target', 'Legacy Ticket archive requires a Current carrier.')
        branch = _branch(selection, path, selected['status'], selected, current_rows)
        name = f"{selected['id']}@{target['version']}" + path.name[len(selected['id']):]
        return _move_ticket(selection, target, selected, digest, path, branch / ARCHIVE_DIRECTORY / name,
                            'archived', lambda: None)

    replacements = []

    check_replacement = partial(_check_replacement, selection, selected, replacements)

    with _project_write_lock(selection.root):
        branch = _branch(selection, path, selected['status'], selected, current_rows)
        if path.with_suffix('').exists() or path.with_suffix('').is_symlink():
            raise InputError('target', 'Ticket containers cannot be archived by this operation.')
        check_replacement()
        raw, bounds, tree, _ = _read_ticket(selection, target, selected, digest, path, placement=True)
        marker = target['ref_id'] if selected['status_group'] == 'Draft' else selected['id']
        if not path.name.startswith(marker + '-'):
            raise InputError('target', 'Ticket filename disagrees with its reference.')
        name = f"{selected['id']}@{target['version']}" + path.name[len(marker):]
        return _move_ticket(selection, target, selected, digest, path, branch / ARCHIVE_DIRECTORY / name,
                            'archived', check_replacement, locked=True, preflight=(raw, bounds, tree))
