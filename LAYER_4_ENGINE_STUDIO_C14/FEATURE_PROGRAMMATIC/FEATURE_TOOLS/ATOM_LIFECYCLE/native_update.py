"""Bounded updates for a selected Current native Ticket."""
from __future__ import annotations

from collections import defaultdict
from contextlib import nullcontext
from functools import partial
from hashlib import sha256


from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import native_header_view
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import native_ticket_asset, COMPLETE_DIRECTORY

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import CURRENT_STATUSES, capture_native, revalidate_native
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import frontmatter_bounds
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import parse_carrier
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import CEILINGS, ReadContext

from . import effects
from .effects import _project_write_lock
from .directory_effect import _read_tree, move_directory
from .common import InputError, SourceChanged, _create_parents, result, saved
from .native_update_selection import _select_ticket, _status_bytes, _branch, _descendants
from .native_update_publish import _publish_ticket


def _check_ticket_tree(selection, path, selected, capture, tree, close_tree, require_terminal):
    companion = path.with_suffix('')
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
    terminal = {'done', 'canceled', 'resolved', 'complete'}
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

def _read_ticket(selection, target, selected, digest, path, *, close_tree=False, placement=False, require_terminal=False, previous_capture=None):
    try:
        companion = path.with_suffix('')
        tree = _read_tree(selection.root, companion) if close_tree and companion.is_dir() else None
        capture = (capture_native(selection) if previous_capture is None
                   else revalidate_native(selection, previous_capture))
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
        _check_ticket_tree(selection, path, selected, capture, tree, close_tree, require_terminal)
        reader = ReadContext(roots=[str(selection.control_root)], limits=dict(CEILINGS))
        raw = reader.read(path)
        bounds = frontmatter_bounds(raw)
        if bounds is None or sha256(raw).hexdigest() != digest or raw[bounds[2]:] != selected.get('_content_bytes'):
            raise SourceChanged('Current Ticket source changed after selection.')
        if parse_carrier(raw, path).metadata != selected.get('header_json'):
            raise SourceChanged('Current Ticket header changed after selection.')
    except InputError:
        raise
    except SourceChanged:
        raise
    except (OSError, RuntimeError, TypeError, ValueError) as error:
        raise SourceChanged('Native source is unavailable or changed.') from error
    return raw, bounds, tree, capture


def _prepare_ticket_directory(selection, destination, recorded, recorded_errors, check):
    if not destination.parent.exists():
        if not check():
            return result(effects=recorded, errors=recorded_errors)
        try:
            _create_parents(selection.root, destination.parent, recorded)
        except (OSError, ValueError):
            return result(effects=recorded, errors=[{'code': 'backend_failure',
                                                    'message': 'Cannot create the Ticket status directory.'}])
    return None


def _ticket_source_intact(selection, path, digest, close_tree, tree, companion):
    try:
        reader = ReadContext(roots=[str(selection.control_root)], limits=dict(CEILINGS))
        return (sha256(reader.read(path)).hexdigest() == digest and not
                (close_tree and tree is None and (companion.exists() or companion.is_symlink())))
    except (OSError, RuntimeError, ValueError):
        return False


def _move_ticket(selection, target, selected, digest, path, destination, status, check_definition, *, close_tree=False, require_terminal=False, locked=False, preflight=None, previous_capture=None):
    with nullcontext() if locked else _project_write_lock(selection.root):
        companion = path.with_suffix('')
        target_companion = destination.with_suffix('')
        if (destination.exists() or destination.is_symlink() or
                (close_tree and (target_companion.exists() or target_companion.is_symlink()))):
            return result(errors=[{'code': 'destination_exists', 'message': 'Ticket destination already exists.'}])
        if preflight is None:
            raw, bounds, tree, _ = _read_ticket(selection, target, selected, digest, path, close_tree=close_tree, placement=True,
                                                require_terminal=require_terminal, previous_capture=previous_capture)
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

        source_intact = partial(_ticket_source_intact, selection, path, digest, close_tree, tree, companion)

        def rollback():
            if source_intact():
                undone = effects.remove(selection.root, destination, sha256(candidate).hexdigest())
                recorded.extend(undone.effects)
                recorded_errors.extend(undone.errors)

        failure = _prepare_ticket_directory(selection, destination, recorded, recorded_errors, check)
        if failure is not None:
            return failure
        if not check():
            return result(effects=recorded, errors=recorded_errors)
        if not source_intact():
            return result(effects=recorded, errors=[{'code': 'source_changed',
                                                     'message': 'Current Ticket source changed before publication.'}])
        outcome = _publish_ticket(selection, path, destination, digest, candidate, tree, companion,
                                  target_companion, recorded, recorded_errors, check, source_intact,
                                  rollback, move_directory)
        if outcome is not None:
            return outcome
        ref = f"{selected['id']}@{target['version']}" if status == 'archived' else selected['id']
        data = {} if recorded_errors else {'artifact': saved(selection, destination, selected['id'], ref,
                                                               target['version'], status)}
        return result(effects=recorded, errors=recorded_errors, **data)


def _check_ticket_transition(selected, template, status):
    if 'atom_family' in selected['header_json']:
        issue = template in {'problem', 'question', 'code_spec_mismatch', 'opportunity'}
        planning = template in {'task', 'epic'}
        if issue or planning:
            terminals = {'resolved', 'canceled'} if issue else {'done', 'canceled'}
            permitted = ((selected['status'] == 'backlog' and status == 'in_queue')
                         or (selected['status'] in {'in_queue', 'active'} and status in terminals)
                         or (selected['status'] == 'active' and status == 'in_queue'))
            if not permitted:
                raise InputError('targetStatus', 'Ticket Status transition is not supported for its Template.')


def _apply_status_actions(selection, actions, selected, status, current_rows, terminal,
                          check_definition, raw, bounds, tree, recorded):
    for row in actions:
        is_parent = row['id'] == selected['id']
        action_status = status if is_parent else 'canceled'
        action_target = {'ref_id': row['id'], 'version': row['version']}
        try:
            current, action_digest, action_path = _select_ticket(selection, action_target, current_rows)
            branch = _branch(selection, action_path, current['status'], current, current_rows)
            destination = branch / ('' if action_status in {'active', 'in_queue'} else COMPLETE_DIRECTORY if action_status == 'complete' else action_status) / action_path.name
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


def _ticket_template(selected, status):
    template = native_header_view(selected['header_json']).get('context', {}).get('template')
    context = native_header_view(selected['header_json']).get('context', {})
    detached_asset = native_ticket_asset(template) and 'component' in context.get('container', {})
    if status == 'complete' and not detached_asset:
        raise InputError('targetStatus', 'Only a standalone Ticket Asset can be completed.')
    if detached_asset and status == 'complete' and selected['status'] != 'in_queue':
        raise InputError('targetStatus', 'Only an In Queue Asset can be completed.')
    _check_ticket_transition(selected, template, status)
    return template

def change_ticket_status(selection, params, *, current_rows, check_definition, previous_capture=None):
    if not isinstance(params, dict) or set(params) != {'target', 'targetStatus'}:
        raise InputError('target', 'Supply one target and target Status.')
    status = params['targetStatus']
    if not isinstance(status, str) or status.casefold() not in CURRENT_STATUSES['T'] - {'active'}:
        raise InputError('targetStatus', 'Supply a Current Ticket Status.', allowed_values=CURRENT_STATUSES['T'] - {'active'})
    status = status.casefold()
    target = params['target']
    selected, digest, path = _select_ticket(selection, target, current_rows)
    template = _ticket_template(selected, status)
    move_tree = template in ('task', 'epic')
    terminal = move_tree and status in ('done', 'canceled')
    recorded = []
    with _project_write_lock(selection.root):
        branch = _branch(selection, path, selected['status'], selected, current_rows)
        destination = branch / ('' if status in {'active', 'in_queue'} else COMPLETE_DIRECTORY if status == 'complete' else status) / path.name
        if destination != path and (destination.exists() or destination.is_symlink() or
                (move_tree and (destination.with_suffix('').exists() or destination.with_suffix('').is_symlink()))):
            return result(errors=[{'code': 'destination_exists', 'message': 'Ticket destination already exists.'}])
        if move_tree and selected['status'] == 'backlog' and status == 'in_queue':
            try:
                capture = revalidate_native(selection, previous_capture)
            except (OSError, RuntimeError, ValueError) as error:
                raise SourceChanged('Native carrier capture changed.') from error
            if capture.errors:
                raise SourceChanged('Native carrier capture is incomplete.')
            return promote_ticket_tree(selection, selected, destination, status, current_rows,
                                       capture.atoms, check_definition)
        raw, bounds, tree, capture = _read_ticket(selection, target, selected, digest, path,
                                                   close_tree=move_tree, placement=True, previous_capture=previous_capture)
        planned = _descendants(current_rows, selected['id']) if move_tree else []
        fresh = _descendants(capture.atoms, selected['id']) if move_tree else []
        keys = ('id', 'version', 'status', 'source_path', '_source_sha256', 'header_json')
        if len(planned) != len(fresh) or any(
                any(before.get(key) != after.get(key) for key in keys)
                for before, after in zip(planned, fresh)):
            raise SourceChanged('Ticket descendants changed after selection.')
        if (move_tree and selected['status'] in ('done', 'canceled') and not terminal and status != 'in_queue'
                and any(row['status'] != status for row in planned)):
            raise InputError('target', 'Reopening requires changing contained Ticket statuses; this operation is unsupported.')
        actions = [row for row in planned if terminal and row['status'] not in ('done', 'canceled', 'resolved', 'complete')]
        actions.append(selected)
        return _apply_status_actions(selection, actions, selected, status, current_rows, terminal,
                                     check_definition, raw, bounds, tree, recorded)


from .native_update_promotion import promote_ticket_tree
from .native_update_archive import direct_update as direct_update, archive_ticket as archive_ticket
from .native_update_spec import change_spec_status as change_spec_status, archive_spec_draft as archive_spec_draft
