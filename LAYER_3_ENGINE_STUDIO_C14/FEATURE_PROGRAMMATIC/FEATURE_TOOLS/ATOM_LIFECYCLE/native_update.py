"""Bounded updates for a selected Current native Ticket."""
from __future__ import annotations

from collections import defaultdict
from contextlib import nullcontext
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re

import yaml

from native_carrier_header import native_header_view

from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.native_source_rows import CURRENT_STATUSES, capture_native
from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.source_rows import frontmatter_bounds
from VALIDATE_ATOMS.validate_atoms_workers.parsing import parse_carrier
from VALIDATE_ATOMS.validate_atoms_workers.read_io import ReadContext
from VALIDATE_ATOMS.validate_atoms_workers.settings import CEILINGS

from . import effects
from .effects import _project_write_lock
from .directory_effect import _read_tree, move_directory
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


def _read_ticket(selection, target, selected, digest, path, *, close_tree=False, placement=False, require_terminal=False):
    try:
        companion = path.with_suffix('')
        tree = _read_tree(selection.root, companion) if close_tree and companion.is_dir() else None
        capture = capture_native(selection)
        if capture.errors:
            raise SourceChanged('Native carrier capture is incomplete.')
        fresh = [row for row in capture.atoms if row.get('ref') == target['ref_id']
                 and row.get('status_group') == selected['status_group']]
        if len(fresh) != 1 or any(fresh[0].get(key) != selected.get(key) for key in (
                'source_path', 'id', 'ref', '_exact_ref', 'version', 'status', 'status_group',
                'header_json', '_content_bytes')):
            raise SourceChanged('Current Ticket source changed after selection.')
        if placement:
            _branch(selection, path, selected['status'], selected, capture.atoms)
        children = defaultdict(list)
        for row in capture.atoms:
            if row['status_group'] == 'Current':
                owner = native_header_view(row['header_json']).get('context', {}).get('container', {}).get('atom')
                if owner is not None:
                    children[owner].append(row)
        pending = list(children.get(selected['id'], ()))
        if pending and (not close_tree or not companion.is_dir()):
            raise InputError('target', 'Ticket descendants require their companion directory.')
        visited = {selected['id']}
        terminal = {'done', 'canceled'}
        while pending:
            child = pending.pop()
            if child['id'] in visited:
                raise InputError('target', 'Ticket containment contains a cycle.')
            if require_terminal and child['status'] not in terminal:
                raise InputError('target', 'Current descendants must be terminal before this Status change.')
            visited.add(child['id'])
            pending.extend(children.get(child['id'], ()))
        companion = path.with_suffix('')
        if companion.exists() or companion.is_symlink():
            if not close_tree or companion.is_symlink() or not companion.is_dir():
                raise InputError('target', 'Direct updates of container Atoms are unsupported.')
            for child in capture.atoms:
                child_path = selection.root / child['source_path']
                if child['id'] in visited - {selected['id']} and not child_path.is_relative_to(companion):
                    raise InputError('target', 'Ticket descendants disagree with the companion directory.')
                if child_path.is_relative_to(companion):
                    owner = native_header_view(child['header_json']).get('context', {}).get('container', {}).get('atom')
                    if owner not in visited:
                        raise InputError('target', 'Ticket companion contains an unrelated Atom.')
                    _branch(selection, child_path, child['status'], child, capture.atoms, allow_flat=False)
            if _read_tree(selection.root, companion) != tree:
                raise SourceChanged('Ticket companion changed during validation.')
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
    return raw, bounds, tree, capture


def direct_update(selection, params, *, current_rows):
    if not isinstance(params, dict) or set(params) != {'target', 'changes'}:
        raise InputError('target', 'Supply one target and body change.')
    target, changes = params['target'], params['changes']
    if not isinstance(changes, dict) or set(changes) != {'body'} or not isinstance(changes['body'], str):
        raise InputError('changes', 'Supply only a Markdown body change.')
    selected, digest, path = _select_ticket(selection, target, current_rows, allow_draft=True)
    branch = path.relative_to(selection.control_root / '__TKT').parts[0]
    template = native_header_view(selected['header_json']).get('context', {}).get('template')
    linked_asset = (branch in {'TASKS', 'ISSUES'} and isinstance(template, str)
                    and template.casefold().replace(' ', '_') in {'analysis_report', 'work_log'})
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
    root = selection.control_root / '__TKT'
    parts = path.relative_to(root).parts
    folder = {'draft': '000_draft', 'archived': '099_archived'}.get(status, status)
    old_folder = () if status == 'active' else (folder,)
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
    if owner_template not in {'task', 'epic'} or (owner_template == 'epic' and template not in {'task', 'epic', 'work_report'}):
        raise InputError('target', 'Ticket container is invalid.')
    _branch(selection, owner_path, owner['status'], owner, rows, seen=seen)
    branch = owner_path.with_suffix('')
    if owner_template == 'epic' and template == 'work_report':
        branch /= 'ASSETS'
    if path.parent != branch.joinpath(*old_folder):
        raise InputError('target', 'Ticket path disagrees with its Current Status placement.')
    return branch


def _move_ticket(selection, target, selected, digest, path, destination, status, check_definition, *, close_tree=False, require_terminal=False, locked=False, preflight=None):
    with nullcontext() if locked else _project_write_lock(selection.root):
        companion = path.with_suffix('')
        target_companion = destination.with_suffix('')
        if (destination.exists() or destination.is_symlink() or
                (close_tree and (target_companion.exists() or target_companion.is_symlink()))):
            return result(errors=[{'code': 'destination_exists', 'message': 'Ticket destination already exists.'}])
        if preflight is None:
            raw, bounds, tree, _ = _read_ticket(selection, target, selected, digest, path, close_tree=close_tree, placement=True,
                                                require_terminal=require_terminal)
        else:
            raw, bounds, tree = preflight
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
                return (sha256(reader.read(path)).hexdigest() == digest and not
                        (close_tree and tree is None and (companion.exists() or companion.is_symlink())))
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
            if tree is not None:
                try:
                    if _read_tree(selection.root, companion) != tree:
                        raise ValueError('Ticket companion changed before publication.')
                except (OSError, RuntimeError, ValueError):
                    rollback()
                    return result(effects=recorded, errors=[{'code': 'source_changed', 'message': 'Ticket companion changed before publication.'}])
                moved = move_directory(selection.root, companion, target_companion)
                recorded.extend(moved.effects)
                recorded_errors.extend(moved.errors)
                if moved.errors:
                    if not moved.effects and not any(error.get('code') == 'effect_uncertain' for error in moved.errors):
                        try:
                            if _read_tree(selection.root, companion) == tree:
                                rollback()
                        except (OSError, RuntimeError, ValueError):
                            pass
                    return result(effects=recorded, errors=recorded_errors)
                if not check():
                    restored = move_directory(selection.root, target_companion, companion)
                    recorded.extend(restored.effects)
                    recorded_errors.extend(restored.errors)
                    if not restored.errors:
                        rollback()
                    return result(effects=recorded, errors=recorded_errors)
            removed = effects.remove(selection.root, path, digest)
            recorded.extend(removed.effects)
            recorded_errors.extend(removed.errors)
            if (removed.errors and not removed.effects
                    and not any(error.get('code') == 'effect_uncertain' for error in removed.errors)):
                if tree is not None and source_intact():
                    restored = move_directory(selection.root, target_companion, companion)
                    recorded.extend(restored.effects)
                    recorded_errors.extend(restored.errors)
                    if not restored.errors:
                        rollback()
                else:
                    rollback()
        ref = f"{selected['id']}@{target['version']}" if status == 'archived' else selected['id']
        data = {} if recorded_errors else {'artifact': saved(selection, destination, selected['id'], ref,
                                                               target['version'], status)}
        return result(effects=recorded, errors=recorded_errors, **data)


def _descendants(rows, atom_id):
    children = defaultdict(list)
    for row in rows:
        if row.get('status_group') == 'Current':
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


def change_ticket_status(selection, params, *, current_rows, check_definition):
    if not isinstance(params, dict) or set(params) != {'target', 'targetStatus'}:
        raise InputError('target', 'Supply one target and target Status.')
    status = params['targetStatus']
    if not isinstance(status, str) or status.casefold() not in CURRENT_STATUSES['T']:
        raise InputError('targetStatus', 'Supply a Current Ticket Status.', allowed_values=CURRENT_STATUSES['T'])
    status = status.casefold()
    target = params['target']
    selected, digest, path = _select_ticket(selection, target, current_rows)
    template = native_header_view(selected['header_json']).get('context', {}).get('template')
    move_tree = template in ('task', 'epic')
    terminal = move_tree and status in ('done', 'canceled')
    recorded = []
    with _project_write_lock(selection.root):
        branch = _branch(selection, path, selected['status'], selected, current_rows)
        destination = branch / ('' if status == 'active' else status) / path.name
        if destination != path and (destination.exists() or destination.is_symlink() or
                (move_tree and (destination.with_suffix('').exists() or destination.with_suffix('').is_symlink()))):
            return result(errors=[{'code': 'destination_exists', 'message': 'Ticket destination already exists.'}])
        raw, bounds, tree, capture = _read_ticket(selection, target, selected, digest, path,
                                                   close_tree=move_tree, placement=True)
        planned = _descendants(current_rows, selected['id']) if move_tree else []
        fresh = _descendants(capture.atoms, selected['id']) if move_tree else []
        keys = ('id', 'version', 'status', 'source_path', '_source_sha256', 'header_json')
        if len(planned) != len(fresh) or any(
                any(before.get(key) != after.get(key) for key in keys)
                for before, after in zip(planned, fresh)):
            raise SourceChanged('Ticket descendants changed after selection.')
        if (template == 'epic' and selected['status'] == 'backlog' and status == 'active' and any(
                native_header_view(row['header_json']).get('context', {}).get('template') == 'task'
                and row['status'] != 'active' for row in planned)):
            raise InputError('target', 'Epic activation requires activating its contained Tasks; this operation is unsupported.')
        reopen_epic = template == 'epic' and status == 'active'
        if (move_tree and selected['status'] in ('done', 'canceled') and not terminal and not reopen_epic
                and any(row['status'] != status for row in planned)):
            raise InputError('target', 'Reopening requires changing contained Ticket statuses; this operation is unsupported.')
        actions = [row for row in planned if terminal and row['status'] not in ('done', 'canceled')]
        actions.append(selected)
        for row in actions:
            is_parent = row['id'] == selected['id']
            action_status = status if is_parent else 'canceled'
            action_target = {'ref_id': row['id'], 'version': row['version']}
            try:
                current, action_digest, action_path = _select_ticket(selection, action_target, current_rows)
                branch = _branch(selection, action_path, current['status'], current, current_rows)
                destination = branch / ('' if action_status == 'active' else action_status) / action_path.name
                action_template = native_header_view(current['header_json']).get('context', {}).get('template')
                action_tree = action_template in ('task', 'epic')
                if destination == action_path:
                    if len(actions) > 1:
                        _read_ticket(selection, action_target, current, action_digest, action_path,
                                     close_tree=action_tree, placement=True, require_terminal=terminal)
                    outcome = result(artifact=saved(selection, action_path, current['id'], current['id'],
                                                    action_target['version'], current['status']))
                else:
                    outcome = _move_ticket(selection, action_target, current, action_digest, action_path,
                                           destination, action_status, check_definition, close_tree=action_tree,
                                           require_terminal=terminal, locked=True,
                                           preflight=(raw, bounds, tree) if len(actions) == 1 else None)
            except (InputError, SourceChanged, OSError, ValueError, RuntimeError, TypeError, KeyError) as error:
                if not recorded:
                    raise
                code = 'invalid_input' if isinstance(error, InputError) else 'source_changed'
                return result(effects=recorded, errors=[{'code': code, 'message': f"{row['id']}: {error}"}])
            recorded.extend(outcome.get('effects', ()))
            if outcome.get('errors'):
                return result(effects=recorded, errors=[{**error, 'target': row['id']}
                                                         for error in outcome['errors']])
        return result(effects=recorded, artifact=outcome['artifact'])


def archive_ticket(selection, params, *, current_rows):
    if not isinstance(params, dict) or set(params) != {'target'}:
        raise InputError('target', 'Supply one Current Ticket target.')
    target = params['target']
    selected, digest, path = _select_ticket(selection, target, current_rows)
    branch = _branch(selection, path, selected['status'], selected, current_rows)
    name = f"{selected['id']}@{target['version']}" + path.name[len(selected['id']):]
    return _move_ticket(selection, target, selected, digest, path, branch / '099_archived' / name,
                        'archived', lambda: None)
