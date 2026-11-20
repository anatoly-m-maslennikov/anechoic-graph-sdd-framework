"""Bounded updates for a selected Current native Ticket."""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re

import yaml

from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.native_source_rows import CURRENT_STATUSES, capture_native
from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.source_rows import frontmatter_bounds
from VALIDATE_ATOMS.validate_atoms_workers.parsing import parse_carrier
from VALIDATE_ATOMS.validate_atoms_workers.read_io import ReadContext
from VALIDATE_ATOMS.validate_atoms_workers.settings import CEILINGS

from . import effects
from .backend import _project_write_lock
from .common import InputError, SourceChanged, _create_parents, atom_summary, result, saved
from .source import bind_query_reader


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
    ticket_root = selection.control_root / '__TKT'
    path = selection.root / relative
    if (relative.is_absolute() or '..' in relative.parts or not path.is_relative_to(ticket_root)
            or path.suffix != '.md' or path == selection.manifest_path):
        raise SourceChanged('Current Ticket path is invalid.')

    return selected, digest, path


def _read_ticket(selection, target, selected, digest, path):
    try:
        capture = capture_native(selection)
        if capture.errors:
            raise SourceChanged('Native carrier capture is incomplete.')
        fresh = [row for row in capture.atoms if row.get('ref') == target['ref_id']
                 and row.get('status_group') == selected['status_group']]
        if len(fresh) != 1 or any(fresh[0].get(key) != selected.get(key) for key in (
                'source_path', 'id', 'ref', '_exact_ref', 'version', 'status', 'status_group',
                'header_json', '_content_bytes')):
            raise SourceChanged('Current Ticket source changed after selection.')
        if any(row.get('status_group') == 'Current' and row.get('id') != selected['id']
               and row.get('header_json', {}).get('context', {}).get('container') == {'atom': selected['id']}
               for row in capture.atoms):
            raise InputError('target', 'Direct updates of container Atoms are unsupported.')
        companion = path.with_suffix('')
        if companion.exists() or companion.is_symlink():
            raise InputError('target', 'Direct updates of container Atoms are unsupported.')
        reader = ReadContext(roots=[str(selection.control_root)], limits=dict(CEILINGS))
        raw = reader.read(path)
        bounds = frontmatter_bounds(raw)
        if bounds is None or sha256(raw).hexdigest() != digest or raw[bounds[2]:] != selected.get('_content_bytes'):
            raise SourceChanged('Current Ticket source changed after selection.')
        # Recheck the header after the independent guarded source read.
        if parse_carrier(raw, path).metadata != selected.get('header_json'):
            raise SourceChanged('Current Ticket header changed after selection.')
    except InputError:
        raise
    except SourceChanged:
        raise
    except (OSError, RuntimeError, TypeError, ValueError) as error:
        raise SourceChanged('Native source is unavailable or changed.') from error
    return raw, bounds


def direct_update(selection, params, *, current_rows):
    if not isinstance(params, dict) or set(params) != {'target', 'changes'}:
        raise InputError('target', 'Supply one target and body change.')
    target, changes = params['target'], params['changes']
    if not isinstance(changes, dict) or set(changes) != {'body'} or not isinstance(changes['body'], str):
        raise InputError('changes', 'Supply only a Markdown body change.')
    selected, digest, path = _select_ticket(selection, target, current_rows, allow_draft=True)
    branch = path.relative_to(selection.control_root / '__TKT').parts[0]
    template = selected['header_json']['context'].get('template')
    linked_asset = (branch in {'TASKS', 'ISSUES'} and isinstance(template, str)
                    and template.casefold().replace(' ', '_') in {'analysis_report', 'work_log'})
    if branch != 'ASSETS' and not linked_asset:
        raise InputError('target', 'Direct body updates are limited to Ticket Assets.')
    with _project_write_lock(selection.root):
        raw, bounds = _read_ticket(selection, target, selected, digest, path)
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


def _branch(selection, path, status):
    root = selection.control_root / '__TKT'
    parts = path.relative_to(root).parts
    old_folder = () if status == 'active' else (status,)
    if (len(parts) != 2 + len(old_folder) or parts[0] not in {'TASKS', 'ISSUES', 'ASSETS'}
            or parts[1:-1] != old_folder):
        raise InputError('target', 'Ticket path disagrees with its Current Status placement.')
    return root / parts[0]


def _move_ticket(selection, target, selected, digest, path, destination, status, check_definition):
    with _project_write_lock(selection.root):
        if destination.exists() or destination.is_symlink():
            return result(errors=[{'code': 'destination_exists', 'message': 'Ticket destination already exists.'}])
        raw, bounds = _read_ticket(selection, target, selected, digest, path)
        candidate = _status_bytes(raw, bounds, path, status)
        recorded, recorded_errors = [], []

        def check():
            try:
                check_definition()
                return True
            except Exception as error:
                recorded_errors.append({'code': 'definition_revalidation_required', 'message': str(error)})
                return False

        def source_intact():
            try:
                reader = ReadContext(roots=[str(selection.control_root)], limits=dict(CEILINGS))
                return sha256(reader.read(path)).hexdigest() == digest
            except (OSError, RuntimeError, ValueError):
                return False

        def rollback():
            if source_intact():
                undone = effects.remove(selection.root, destination, sha256(candidate).hexdigest())
                recorded.extend(undone.effects)
                recorded_errors.extend(undone.errors)

        if not destination.parent.exists():
            if not check():
                return result(effects=recorded, errors=recorded_errors)
            try:
                _create_parents(selection.root, destination.parent, recorded)
            except (OSError, ValueError):
                return result(effects=recorded, errors=[{'code': 'backend_failure',
                                                        'message': 'Cannot create the Ticket status directory.'}])
        if not check():
            return result(effects=recorded, errors=recorded_errors)
        if not source_intact():
            return result(effects=recorded, errors=[{'code': 'source_changed',
                                                     'message': 'Current Ticket source changed before publication.'}])
        with bind_query_reader(None):
            created = effects.create(selection.root, destination, candidate)
            recorded.extend(created.effects)
            if created.errors:
                return result(effects=recorded, errors=created.errors)
            if not check():
                rollback()
                return result(effects=recorded, errors=recorded_errors)
            removed = effects.remove(selection.root, path, digest)
            recorded.extend(removed.effects)
            recorded_errors.extend(removed.errors)
            if (removed.errors and not removed.effects
                    and not any(error.get('code') == 'effect_uncertain' for error in removed.errors)):
                rollback()
        ref = f"{selected['id']}@{target['version']}" if status == 'archived' else selected['id']
        data = {} if recorded_errors else {'artifact': saved(selection, destination, selected['id'], ref,
                                                               target['version'], status)}
        return result(effects=recorded, errors=recorded_errors, **data)


def change_ticket_status(selection, params, *, current_rows, check_definition):
    if not isinstance(params, dict) or set(params) != {'target', 'targetStatus'}:
        raise InputError('target', 'Supply one target and target Status.')
    status = params['targetStatus']
    if not isinstance(status, str) or status.casefold() not in CURRENT_STATUSES['T']:
        raise InputError('targetStatus', 'Supply a Current Ticket Status.', allowed_values=CURRENT_STATUSES['T'])
    status = status.casefold()
    target = params['target']
    selected, digest, path = _select_ticket(selection, target, current_rows)
    branch = _branch(selection, path, selected['status'])
    destination = branch / ('' if status == 'active' else status) / path.name
    if destination == path:
        with _project_write_lock(selection.root):
            _read_ticket(selection, target, selected, digest, path)
        return result(artifact=saved(selection, path, selected['id'], selected['id'],
                                     target['version'], selected['status']))
    return _move_ticket(selection, target, selected, digest, path, destination, status, check_definition)


def archive_ticket(selection, params, *, current_rows):
    if not isinstance(params, dict) or set(params) != {'target'}:
        raise InputError('target', 'Supply one Current Ticket target.')
    target = params['target']
    selected, digest, path = _select_ticket(selection, target, current_rows)
    branch = _branch(selection, path, selected['status'])
    name = f"{selected['id']}@{target['version']}" + path.name[len(selected['id']):]
    return _move_ticket(selection, target, selected, digest, path, branch / 'archived' / name,
                        'archived', lambda: None)
