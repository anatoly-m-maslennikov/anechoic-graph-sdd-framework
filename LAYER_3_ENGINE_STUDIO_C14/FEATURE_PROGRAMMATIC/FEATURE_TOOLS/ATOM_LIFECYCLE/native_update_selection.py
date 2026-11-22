"""Ticket selection, placement, and status helpers."""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timezone
import json
from pathlib import Path
import re

import yaml

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.native_carrier_header__pub import native_header_view
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.native_carrier_placement__pub import native_ticket_asset, DRAFT_DIRECTORY, ARCHIVE_DIRECTORY, COMPLETE_DIRECTORY, TICKET_DIRECTORY

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carrier_read__pub import parse_carrier

from .common import InputError, SourceChanged




def _select_ticket(selection, target, current_rows, *, allow_draft=False):
    if (not isinstance(target, dict) or set(target) != {'ref_id', 'version'}
            or not isinstance(target['ref_id'], str)
            or not re.fullmatch(re.escape(selection.project_prefix) + r'-T-[0-9]+(?:@[1-9][0-9]*-draft)?', target['ref_id'])
            or type(target['version']) is not int or target['version'] < 1):
        raise InputError('target', 'Supply a Current Ticket reference and positive Version.')
    draft = target['ref_id'].endswith('-draft')
    if draft and (not allow_draft or not target['ref_id'].endswith(f"@{target['version']}-draft")):
        raise InputError('target', 'Supply an admitted Ticket reference and matching Version.')
    group = 'Draft' if draft else 'Current'
    matches = [row for row in current_rows if row.get('ref') == target['ref_id']
               and row.get('status_group') == group]
    if len(matches) != 1 or matches[0].get('version') != target['version']:
        raise SourceChanged('Current Ticket selection is missing, ambiguous, or stale.')
    selected = matches[0]
    digest = selected.get('_source_sha256')
    if not isinstance(digest, str) or not re.fullmatch(r'[0-9a-f]{64}', digest):
        raise SourceChanged('Current Ticket capture lacks a full source digest.')
    relative = selected.get('source_path')
    if not isinstance(relative, str):
        raise SourceChanged('Current Ticket path is invalid.')
    relative = Path(relative)
    ticket_root = selection.control_root / ('__TKT' if '__TKT' in relative.parts else TICKET_DIRECTORY)
    path = selection.root / relative
    if (relative.is_absolute() or '..' in relative.parts or not path.is_relative_to(ticket_root)
            or path.suffix != '.md' or path == selection.manifest_path):
        raise SourceChanged('Current Ticket path is invalid.')

    return selected, digest, path

def _status_bytes(raw, bounds, path, status):
    header = raw[bounds[0]:bounds[1]].decode('utf-8')
    node = yaml.compose(header, Loader=yaml.SafeLoader)
    try:
        state = next(value for key, value in node.value if key.value == 'state')
        fields = {key.value: value for key, value in state.value}
        values = {'status': status, 'updated_at': datetime.now(timezone.utc).isoformat()}
        edits = [(fields[key].start_mark.index, fields[key].end_mark.index, json.dumps(value))
                 for key, value in values.items() if isinstance(fields[key], yaml.ScalarNode)]
        if len(edits) != 2:
            raise ValueError('Invalid state fields')
        for start, end, value in sorted(edits, reverse=True):
            header = header[:start] + value + header[end:]
        candidate = raw[:bounds[0]] + header.encode('utf-8') + raw[bounds[1]:]
        before = parse_carrier(raw, path).metadata
        after = parse_carrier(candidate, path).metadata
        expected = dict(before)
        expected['state'] = {**before['state'], **values}
        if after != expected:
            raise ValueError('Unintended header change')
        return candidate
    except (AttributeError, KeyError, StopIteration, TypeError, ValueError) as error:
        raise InputError('target', 'Ticket needs scalar state status and updated_at fields.') from error

def _branch(selection, path, status, selected, rows, *, allow_flat=True, seen=None):
    root = selection.control_root / ('__TKT' if '__TKT' in path.parts else TICKET_DIRECTORY)
    parts = path.relative_to(root).parts
    folder = {'draft': DRAFT_DIRECTORY, 'archived': ARCHIVE_DIRECTORY, 'complete': COMPLETE_DIRECTORY}.get(status, status)
    old_folder = () if status in {'active', 'in_queue'} else (('000_draft' if status == 'draft' and path.parent.name == '000_draft' else folder),)
    if parts[0] not in {'TASKS', 'ISSUES', 'ASSETS'}:
        raise InputError('target', 'Ticket path disagrees with its Current Status placement.')
    flat = root / parts[0]
    if allow_flat and path.parent == flat.joinpath(*old_folder):
        return flat
    context = native_header_view(selected['header_json']).get('context', {})
    owner_id = context.get('container', {}).get('atom')
    seen = set() if seen is None else seen
    if not owner_id or owner_id in seen:
        raise InputError('target', 'Ticket path disagrees with its Current Status placement.')
    seen.add(owner_id)
    owners = [row for row in rows if row.get('id') == owner_id and row.get('status_group') == 'Current']
    if len(owners) != 1:
        raise SourceChanged('Containing Ticket is missing or ambiguous.')
    owner = owners[0]
    owner_path = selection.root / owner['source_path']
    if not owner_path.is_relative_to(root) or '..' in owner_path.parts:
        raise SourceChanged('Containing Ticket path is invalid.')
    owner_template = native_header_view(owner['header_json']).get('context', {}).get('template')
    template = context.get('template')
    if owner_template not in {'task', 'epic'}:
        raise InputError('target', 'Ticket container is invalid.')
    _branch(selection, owner_path, owner['status'], owner, rows, seen=seen)
    branch = owner_path.with_suffix('')
    if native_ticket_asset(template) and path.parent == (branch / 'ASSETS').joinpath(*old_folder):
        branch /= 'ASSETS'
    if path.parent != branch.joinpath(*old_folder):
        raise InputError('target', 'Ticket path disagrees with its Current Status placement.')
    return branch

def _descendants(rows, atom_id, *, include_drafts=False):
    children = defaultdict(list)
    history = Counter(row['id'] for row in rows) if include_drafts else {}
    for row in rows:
        first_draft = (include_drafts and row.get('status_group') == 'Draft'
                       and row.get('version') == 1 and history[row['id']] == 1)
        if row.get('status_group') == 'Current' or first_draft:
            owner = native_header_view(row['header_json']).get('context', {}).get('container', {}).get('atom')
            if owner is not None:
                children[owner].append(row)
    ordered, seen = [], {atom_id}
    stack = [(row, False) for row in reversed(sorted(children.get(atom_id, ()), key=lambda r: r['id']))]
    while stack:
        row, visited = stack.pop()
        if visited:
            ordered.append(row)
            continue
        if row['id'] in seen:
            raise InputError('target', 'Ticket containment is cyclic or ambiguous.')
        seen.add(row['id'])
        stack.append((row, True))
        stack.extend((child, False) for child in reversed(sorted(children.get(row['id'], ()), key=lambda r: r['id'])))
    return ordered
