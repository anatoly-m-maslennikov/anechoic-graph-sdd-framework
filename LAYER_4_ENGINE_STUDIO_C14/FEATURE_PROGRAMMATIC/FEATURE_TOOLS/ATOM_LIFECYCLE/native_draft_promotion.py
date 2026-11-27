"""Publish native Drafts with source checks and rollback."""
from hashlib import sha256
from pathlib import Path
import re

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import native_header_view
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (spec_lens_directories,
    DRAFT_DIRECTORY, READY_DIRECTORY, TICKET_DIRECTORY)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import revalidate_native
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import frontmatter_bounds
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import parse_carrier
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import CEILINGS, ReadContext

from . import common, effects
from .effects import _project_write_lock
from .native_draft_guards import (
    _check_owner, _native_slug, _reject_component_contract,
    _check_first_spec, is_c9_typed_manifest,
)
from .native_draft_source import _revision_header, _revision_root, _state_bytes, _task_path
from .native_draft_revision import _promote_revision
from .native_replacement_promotion import _plan_replacements, _archive_replacements
from .native_draft_custom_replacement import _publish_custom_replacement
from .native_project_spec import PROJECT_SPEC_TIERS, project_spec_template
from .source import bind_query_reader


def _promote_new(selection, target, status, draft, current_rows, previous_capture):
    atom_id = target['ref_id'].split('@')[0]
    relative, digest = draft.get('source_path'), draft.get('_source_sha256')
    if (not isinstance(relative, str) or not isinstance(digest, str)
            or not re.fullmatch(r'[0-9a-f]{64}', digest)):
        raise common.SourceChanged('Draft capture lacks a valid path or digest.')
    relative = Path(relative)
    path = selection.root / relative
    root = next((selection.control_root / name for name in (TICKET_DIRECTORY, '001_TICKETS', '__TKT') if path.is_relative_to(selection.control_root / name)), selection.control_root / TICKET_DIRECTORY) / 'TASKS'
    if (not selection.root.is_absolute() or not selection.control_root.is_relative_to(selection.root)
            or selection.manifest_path.parent not in {selection.root, selection.control_root}
            or relative.is_absolute() or '..' in relative.parts or not path.is_relative_to(root)
            or path.parent.name not in {DRAFT_DIRECTORY, '000_draft'}
            or not re.fullmatch(re.escape(target['ref_id']) + r'-.+--.+\.md', path.name)):
        raise common.SourceChanged('Task Draft path is invalid.')
    root = root if path.parent in {root / DRAFT_DIRECTORY, root / '000_draft'} else None
    with _project_write_lock(selection.root):
        capture, destination, promoted = _preflight_new(
            selection, target, status, draft, current_rows, previous_capture, path, root, digest, atom_id)
        if status in ('active', 'in_queue', 'backlog'):
            from .native_update_promotion import promote_ticket_tree
            return promote_ticket_tree(selection, draft, destination, status, current_rows, capture, lambda: None)
        plans = _plan_replacements(selection, draft, current_rows, None, capture)
        if path.with_suffix('').exists() or path.with_suffix('').is_symlink():
            raise common.InputError('targetStatus', 'Draft trees can only be published to Backlog or In Queue.')
        archived = _archive_replacements(selection, plans, draft)
        if archived['outcome'] != 'completed':
            return archived
        with bind_query_reader(None):
            written = common.write_destination(selection.root, destination, promoted)
            recorded = archived['effects'] + list(written.effects)
            if written.errors:
                return common.result(effects=recorded, errors=written.errors)
            removed = effects.remove(selection.root, path, digest)
            recorded.extend(removed.effects)
        data = {} if removed.errors else {'artifact': common.saved(selection, destination, atom_id, atom_id, 1, status)}
        return common.result(effects=recorded, errors=removed.errors, **data)



def _preflight_new(selection, target, status, draft, current_rows, previous_capture, path, root, digest, atom_id):
    try:
        capture = revalidate_native(selection, previous_capture)
        rows = [row for row in capture.atoms if row.get('id') == atom_id]
        if (capture.errors or len(rows) != 1 or any(rows[0].get(key) != draft.get(key) for key in (
                'source_path', 'id', 'ref', '_exact_ref', 'version', 'status', 'status_group',
                'header_json', '_content_bytes', '_source_sha256'))):
            raise common.SourceChanged('Task Draft changed or its identity already has history.')
        header = draft.get('header_json')
        context = native_header_view(header).get('context')
        if not isinstance(context, dict) or context.get('template') not in ('task', 'epic'):
            raise common.InputError('target', 'Select a native Task or Epic Draft.')
        owner = _check_owner(selection, context.get('container'), current_rows, capture)
        reader = ReadContext(roots=[str(selection.control_root)], limits=dict(CEILINGS))
        raw = reader.read(path)
        bounds = frontmatter_bounds(raw)
        if (bounds is None or sha256(raw).hexdigest() != digest or raw[bounds[2]:] != draft.get('_content_bytes')
                or parse_carrier(raw, path).metadata != header or reader.currentness()['state'] != 'unchanged'):
            raise common.SourceChanged('Task Draft source changed after selection.')
        body = raw[bounds[2]:].decode('utf-8')
        slug = _native_slug(body)
        if path != (_task_path(selection, header, body, 'draft', 1, owner, root) if 'atom_family' in header
                    else root / DRAFT_DIRECTORY / f"{target['ref_id']}-TASK--{slug}.md"):
            raise common.InputError('target', 'Task Draft filename disagrees with its Summary.')
        destination = (_task_path(selection, header, body, status, 1, owner, root) if 'atom_family' in header
                       else root / ('' if status in {'active', 'in_queue'} else status) / f'{atom_id}-TASK--{slug}.md')
        if destination.exists() or destination.is_symlink():
            raise common.InputError('target', 'The promotion destination already exists.')
        if destination.parent.is_symlink() or (destination.parent.exists() and not destination.parent.is_dir()):
            raise common.InputError('target', 'The promotion destination directory is unsafe.')
        promoted = _state_bytes(raw, bounds, path, 1, body, status)
    except (common.InputError, common.SourceChanged):
        raise
    except (OSError, RuntimeError, TypeError, ValueError) as error:
        raise common.SourceChanged('Native source is unavailable or changed.') from error
    return capture, destination, promoted


def _publish_first_spec(selection, draft, current_rows, structure_snapshot, previous_capture, validate_project_spec_model):
    from .native_draft import _first_spec_write_lock

    atom_id, ref_id = draft['id'], draft['_exact_ref']
    relative, digest = draft.get('source_path'), draft.get('_source_sha256')
    if (not isinstance(relative, str) or not isinstance(digest, str)
            or not re.fullmatch(r'[0-9a-f]{64}', digest)):
        raise common.SourceChanged('Draft capture lacks a valid path or digest.')
    relative = Path(relative)
    path = selection.root / relative
    if (relative.is_absolute() or '..' in relative.parts or not path.is_relative_to(selection.control_root)
            or path.parent.name not in {DRAFT_DIRECTORY, '000_draft'} or not re.fullmatch(re.escape(ref_id) + r'-.+\.md', path.name)):
        raise common.InputError('target', 'Select a Spec in its native Draft directory.')
    with _first_spec_write_lock(selection.root):
        destination, promoted, version, capture = _preflight_first_spec(
            selection, draft, structure_snapshot, previous_capture, validate_project_spec_model,
            atom_id, ref_id, path, digest)
        plans = _plan_replacements(selection, draft, current_rows, structure_snapshot, capture)
        archived = _archive_replacements(selection, plans, draft)
        if archived['outcome'] != 'completed':
            return archived
        with bind_query_reader(None):
            written = common.write_destination(selection.root, destination, promoted)
            recorded = archived['effects'] + list(written.effects)
            errors = list(written.errors)
            if not errors:
                removed = effects.remove(selection.root, path, digest)
                recorded.extend(removed.effects)
                errors.extend(removed.errors)
        data = {} if errors else {'artifact': common.saved(selection, destination, atom_id, atom_id, version, 'ready')}
        return common.result(effects=recorded, errors=errors, **data)



def _preflight_first_spec(selection, draft, structure_snapshot, previous_capture, validate_project_spec_model,
                          atom_id, ref_id, path, digest):
    from .native_draft import _validate_project_template

    try:
        capture = revalidate_native(selection, previous_capture)
        history = [row for row in capture.atoms if row['id'] == atom_id]
        matching = [row for row in history if row['_exact_ref'] == ref_id]
        if capture.errors or matching != [draft] or any(row['status_group'] != 'Draft' for row in history):
            raise common.SourceChanged('Spec Draft changed or the identity has published revisions.')
        header = draft['header_json']
        context = native_header_view(header)['context']
        lens = context.get('lens')
        if (context.get('template') not in (None, *PROJECT_SPEC_TIERS)
                and not (validate_project_spec_model and project_spec_template(context.get('template'), validate_project_spec_model))
                and not is_c9_typed_manifest(header)
                or re.search(r'-(?:PROJECT|COMPONENT)_MANIFEST(?:--|\.md$)', path.name, re.I)):
            raise common.InputError('target', 'Select a Spec Draft with a lens and without a structural template.')
        owner = path.parent.parent
        try:
            spec_lens_directories(lens)
            directory = owner / READY_DIRECTORY
        except ValueError as error:
            raise common.InputError('target', 'Select a Spec Draft with a valid Lens.') from error
        destination = directory / (atom_id + path.name[len(ref_id):])
        proposed = {**draft, 'source_path': destination.relative_to(selection.root).as_posix(), 'status': 'ready'}
        if _revision_root(selection, proposed, structure_snapshot) != owner:
            raise common.InputError('target', 'Spec Draft and Current carrier must belong to the same Component.')
        if destination.exists() or destination.is_symlink():
            raise common.InputError('target', 'The promotion destination already exists.')
        reader = ReadContext(roots=[str(selection.control_root)], limits=dict(CEILINGS))
        raw = reader.read(path)
        bounds = frontmatter_bounds(raw)
        if (bounds is None or sha256(raw).hexdigest() != digest or raw[bounds[2]:] != draft['_content_bytes']
                or parse_carrier(raw, path).metadata != header or reader.currentness()['state'] != 'unchanged'):
            raise common.SourceChanged('Spec Draft source changed after selection.')
        body = raw[bounds[2]:].decode('utf-8')
        _check_first_spec(selection, header, body, path, owner)
        version = draft['version']
        promoted = _state_bytes(raw, bounds, path, version, body, 'ready')
        _validate_project_template(parse_carrier(promoted, destination).metadata, validate_project_spec_model, body)
    except (common.InputError, common.SourceChanged):
        raise
    except (OSError, RuntimeError, TypeError, ValueError) as error:
        raise common.SourceChanged('Native Spec source is unavailable or changed.') from error
    return destination, promoted, version, capture



def _cleanup_published_draft(selection, target, status, draft, current, structure_snapshot, current_rows,
                             previous_capture):
    atom_id, version = target['ref_id'].split('@')[0], target['version']
    if current.get('status') != status:
        raise common.InputError('targetStatus', 'Published carrier Status differs from the requested Status.')
    root = _revision_root(selection, current, structure_snapshot, current_rows)
    paths = []
    for row, marker, directory in ((draft, target['ref_id'], (selection.root / draft['source_path']).parent),
                                   (current, atom_id, (selection.root / current['source_path']).parent)):
        relative, digest = row.get('source_path'), row.get('_source_sha256')
        if not isinstance(relative, str) or not isinstance(digest, str) or not re.fullmatch(r'[0-9a-f]{64}', digest):
            raise common.SourceChanged('Carrier capture lacks a valid path or digest.')
        relative = Path(relative)
        path = selection.root / relative
        if (relative.is_absolute() or '..' in relative.parts or path.parent != directory
                or (row is draft and path.parent not in {root / DRAFT_DIRECTORY, root / '000_draft'})
                or not re.fullmatch(re.escape(marker) + r'-.+\.md', path.name)):
            raise common.SourceChanged('Carrier path is invalid.')
        paths.append(path)
    if paths[0].name[len(target['ref_id']):] != paths[1].name[len(atom_id):]:
        raise common.InputError('target', 'Published carrier filename differs from the Draft.')
    with _project_write_lock(selection.root):
        companion = paths[0].with_suffix('')
        if '-T-' in atom_id and (companion.exists() or companion.is_symlink()):
            raise common.InputError('target', 'Recover the interrupted Draft companion before removing its carrier.')
        _preflight_cleanup(selection, target, status, draft, current, current_rows,
                           previous_capture, atom_id, version, root, paths)
        with bind_query_reader(None):
            removed = effects.remove(selection.root, paths[0], draft['_source_sha256'])
        data = {} if removed.errors else {'artifact': common.saved(selection, paths[1], atom_id, atom_id, version, status)}
        return common.result(effects=removed.effects, errors=removed.errors, **data)



def _preflight_cleanup(selection, target, status, draft, current, current_rows,
                       previous_capture, atom_id, version, root, paths):
    try:
        capture = revalidate_native(selection, previous_capture)
        if capture.errors:
            raise common.SourceChanged('Native carrier capture is incomplete.')
        for row in (draft, current):
            fresh = [item for item in capture.atoms if item.get('_exact_ref') == row.get('_exact_ref')]
            if len(fresh) != 1 or any(fresh[0].get(key) != row.get(key) for key in (
                    'source_path', 'id', 'ref', '_exact_ref', 'version', 'status', 'status_group',
                    'header_json', '_content_bytes', '_source_sha256')):
                raise common.SourceChanged('Draft or published carrier changed after selection.')
        reader = ReadContext(roots=[str(selection.control_root)], limits=dict(CEILINGS))
        for row, path in zip((draft, current), paths, strict=False):
            raw = reader.read(path)
            bounds = frontmatter_bounds(raw)
            if (bounds is None or sha256(raw).hexdigest() != row['_source_sha256']
                    or raw[bounds[2]:] != row.get('_content_bytes')
                    or parse_carrier(raw, path).metadata != row.get('header_json')):
                raise common.SourceChanged('Draft or published carrier changed after selection.')
        if reader.currentness()['state'] != 'unchanged':
            raise common.SourceChanged(
                'Draft or published carrier changed after selection.'
            )
        draft_header, current_header = draft['header_json'], current['header_json']
        if '-T-' in atom_id:
            owner = _check_owner(selection, native_header_view(current_header)['context'].get('container'), current_rows, capture)
        if '-T-' in atom_id and 'atom_family' in current_header:
            body = draft['_content_bytes'].decode('utf-8')
            if (paths[0] != _task_path(selection, draft_header, body, 'draft', version, owner, root)
                    or paths[1] != _task_path(selection, current_header, body, status, version, owner, root)):
                raise common.InputError('target', 'Task paths disagree with their authored Headers and Summary.')
        if (_revision_header(draft_header) != _revision_header(current_header)
                or draft['_content_bytes'] != current['_content_bytes']):
            raise common.InputError('target', 'Published carrier differs from the Draft.')
    except (common.InputError, common.SourceChanged):
        raise
    except (OSError, RuntimeError, TypeError, ValueError) as error:
        raise common.SourceChanged('Native source is unavailable or changed.') from error

def promote_draft(selection, params, *, current_rows, structure_snapshot=None, previous_capture=None,
                  validate_project_spec_model=None):
    """Publish a native Draft."""
    if not isinstance(params, dict) or set(params) != {'target', 'targetStatus'}:
        raise common.InputError('target', 'Supply an exact Draft target and Current Status.')
    target, status = params['target'], params['targetStatus']
    if (not isinstance(target, dict) or set(target) != {'ref_id', 'version'}
            or not isinstance(target['ref_id'], str) or type(target['version']) is not int
            or target['version'] < 1):
        raise common.InputError('target', 'Supply an exact Draft reference and Version.')
    match = re.fullmatch(rf'({re.escape(selection.project_prefix)}-[STPC]-[0-9]+)@([1-9][0-9]*)-draft', target['ref_id'])
    if match is None or int(match[2]) != target['version']:
        raise common.InputError('target', 'Supply an exact Draft reference and matching Version.')
    if (not isinstance(status, str) or status not in {'active', 'ready', 'in_queue', 'backlog', 'done', 'canceled', 'resolved'}
            or ('-S-' in match[1] and status != 'ready')
            or (('-P-' in match[1] or '-C-' in match[1]) and status != 'active')
            or ('-T-' in match[1] and status in {'ready', 'in_queue'})):
        raise common.InputError('targetStatus', 'Supply an applicable Current Status.')
    atom_id, version = match[1], target['version']
    chosen = [row for row in current_rows if row.get('_exact_ref') == target['ref_id'] and row.get('status_group') == 'Draft']
    predecessors = [row for row in current_rows if row.get('id') == atom_id and row.get('status_group') == 'Current']
    if len(chosen) != 1 or len(predecessors) > 1:
        raise common.SourceChanged('Draft or Current predecessor is missing or ambiguous.')
    _reject_component_contract(native_header_view(chosen[0]['header_json'])['context'].get('template'), 'target')
    if '-T-' in atom_id and status != 'backlog' and 'atom_family' in chosen[0]['header_json']:
        raise common.InputError('targetStatus', 'A native Ticket Draft must be published to Backlog.')
    if not predecessors:
        if version == 1 and _is_custom_replacement(chosen[0]['header_json']):
            return _publish_custom_replacement(selection, chosen[0], current_rows, previous_capture)
        if '-S-' in atom_id:
            return _publish_first_spec(selection, chosen[0], current_rows, structure_snapshot, previous_capture,
                                       validate_project_spec_model)
        if version == 1 and '-T-' in atom_id:
            return _promote_new(selection, target, status, chosen[0], current_rows, previous_capture)
        raise common.SourceChanged('Current predecessor is missing.')
    draft, previous = chosen[0], predecessors[0]
    if previous.get('version') == version:
        return _cleanup_published_draft(selection, target, status, draft, previous, structure_snapshot, current_rows,
                                        previous_capture)
    if type(previous.get('version')) is not int or previous['version'] >= version:
        raise common.InputError('target', 'Draft Version must be newer than its Current predecessor.')
    return _promote_revision(selection, target, status, draft, previous, current_rows,
                             structure_snapshot, previous_capture, validate_project_spec_model)


def _is_custom_replacement(header):
    context = native_header_view(header).get('context', {})
    return (header.get('atom_family') == 'PROJECT_CONFIG'
            and context.get('container') == {'component': 'C00'}
            and context.get('template') == 'manifest_node'
            and header.get('relations', {}).get('IS_REPLACEMENT_FOR'))
