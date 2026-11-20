"""Create a same-ID Draft from one pinned Current native Task."""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re

import yaml

from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.native_source_rows import capture_native
from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.source_rows import frontmatter_bounds
from VALIDATE_ATOMS.validate_atoms_workers.parsing import parse_carrier
from VALIDATE_ATOMS.validate_atoms_workers.read_io import ReadContext
from VALIDATE_ATOMS.validate_atoms_workers.settings import CEILINGS

from . import common, effects
from .backend import _project_write_lock
from .placement import _slug
from .source import bind_query_reader


_SUMMARY = re.compile(r'(?m)^#{1,2} Summary[ \t]*\r?\n(?:[ \t]*\r?\n)*([^\r\n]+)[ \t]*(?=\r?$)')


def _summary(body):
    matches = list(_SUMMARY.finditer(body))
    if len(matches) != 1 or not matches[0].group(1).strip():
        raise common.InputError('summary', 'Exactly one nonempty Summary is required.')
    return matches[0].group(1)


def _native_slug(body):
    summary = _summary(body)
    if not summary.isprintable():
        raise common.InputError('summary', 'Summary must contain printable characters.')
    return _slug(''.join(char if char.isascii() else '-' for char in summary))


def _state_bytes(raw, bounds, path, version, body, status):
    header = raw[bounds[0]:bounds[1]].decode('utf-8')
    try:
        node = yaml.compose(header, Loader=yaml.SafeLoader)
        states = [value for key, value in node.value if key.value == 'state']
        if len(states) != 1 or not isinstance(states[0], yaml.MappingNode):
            raise ValueError('Invalid state')
        fields = states[0].value
        values = {'status': status, 'version': version}
        if any(key.value == 'updated_at' for key, _ in fields):
            values['updated_at'] = datetime.now(timezone.utc).isoformat()
        edits = []
        for name, value in values.items():
            found = [item for key, item in fields if key.value == name]
            if len(found) != 1 or not isinstance(found[0], yaml.ScalarNode):
                raise ValueError('Invalid state field')
            edits.append((found[0].start_mark.index, found[0].end_mark.index, json.dumps(value)))
        for start, end, value in sorted(edits, reverse=True):
            header = header[:start] + value + header[end:]
        candidate = raw[:bounds[0]] + header.encode('utf-8') + raw[bounds[1]:bounds[2]] + body.encode('utf-8')
        before = parse_carrier(raw, path).metadata
        after = parse_carrier(candidate, path).metadata
        expected = dict(before)
        expected['state'] = {**before['state'], **values}
        if after != expected:
            raise ValueError('Unexpected header change')
        return candidate
    except (AttributeError, KeyError, TypeError, ValueError, yaml.YAMLError) as error:
        raise common.InputError('sourceCurrent', 'Task needs valid scalar state fields.') from error


def create_draft(selection, params, *, current_rows):
    if isinstance(params, dict) and 'newAtom' in params:
        if set(params) != {'newAtom'}:
            raise common.InputError('newAtom', 'Supply only new Task properties.')
        return _create_task(selection, params['newAtom'], current_rows)
    if not isinstance(params, dict) or set(params) - {'sourceCurrent', 'changes'} or 'sourceCurrent' not in params:
        raise common.InputError('sourceCurrent', 'Supply one Current Task and optional body change.')
    target = params['sourceCurrent']
    if (not isinstance(target, dict) or set(target) != {'ref_id', 'version'}
            or not isinstance(target['ref_id'], str)
            or not re.fullmatch(re.escape(selection.project_prefix) + r'-T-[0-9]+', target['ref_id'])
            or type(target['version']) is not int or target['version'] < 1):
        raise common.InputError('sourceCurrent', 'Supply a Current Task reference and positive Version.')
    changes = params.get('changes', {})
    if not isinstance(changes, dict) or set(changes) - {'body'} or ('body' in changes and not isinstance(changes['body'], str)):
        raise common.InputError('changes', 'Supply only a Markdown body change.')
    matches = [row for row in current_rows if row.get('id') == target['ref_id'] and row.get('status_group') == 'Current']
    if len(matches) != 1 or matches[0].get('version') != target['version']:
        raise common.SourceChanged('Current Task selection is missing, ambiguous, or stale.')
    selected = matches[0]
    digest, relative = selected.get('_source_sha256'), selected.get('source_path')
    if (not isinstance(digest, str) or not re.fullmatch(r'[0-9a-f]{64}', digest)
            or not isinstance(relative, str)):
        raise common.SourceChanged('Current Task capture lacks a valid path or source digest.')
    relative = Path(relative)
    root = selection.control_root / '__TKT' / 'TASKS'
    path = selection.root / relative
    if (not selection.root.is_absolute() or not selection.control_root.is_relative_to(selection.root)
            or not selection.manifest_path.is_relative_to(selection.control_root)
            or relative.is_absolute() or '..' in relative.parts or not path.is_relative_to(root)):
        raise common.SourceChanged('Current Task path is invalid.')
    parts = path.relative_to(root).parts
    status = selected.get('status')
    status_dir = () if status == 'active' else (status,)
    header = selected.get('header_json')
    context = header.get('context') if isinstance(header, dict) else None
    if (not isinstance(status, str) or status not in {'active', 'backlog', 'done', 'canceled', 'resolved'}
            or len(parts) != len(status_dir) + 1 or parts[:-1] != status_dir
            or not re.fullmatch(re.escape(target['ref_id']) + r'-TASK--.+\.md', path.name)
            or not isinstance(context, dict) or context.get('template') != 'task'):
        raise common.InputError('sourceCurrent', 'Select a native Task in its Current status directory.')
    with _project_write_lock(selection.root):
        try:
            capture = capture_native(selection)
            fresh = [row for row in capture.atoms if row.get('id') == target['ref_id'] and row.get('status_group') == 'Current']
            if capture.errors or len(fresh) != 1 or any(fresh[0].get(key) != selected.get(key) for key in (
                    'source_path', 'id', 'ref', '_exact_ref', 'version', 'status', 'status_group',
                    'header_json', '_content_bytes', '_source_sha256')):
                raise common.SourceChanged('Current Task source changed after selection.')
            raw = ReadContext(roots=[str(selection.control_root)], limits=dict(CEILINGS)).read(path)
            bounds = frontmatter_bounds(raw)
            if (bounds is None or sha256(raw).hexdigest() != digest
                    or raw[bounds[2]:] != selected.get('_content_bytes')
                    or parse_carrier(raw, path).metadata != selected.get('header_json')):
                raise common.SourceChanged('Current Task source changed after selection.')
            old_body = raw[bounds[2]:].decode('utf-8')
        except common.SourceChanged:
            raise
        except (OSError, RuntimeError, TypeError, ValueError) as error:
            raise common.SourceChanged('Native source is unavailable or changed.') from error
        body = changes.get('body', old_body)
        if _summary(body) != _summary(old_body):
            raise common.InputError('summary', 'Changing a Task Summary is not supported.')
        version = max(row['version'] for row in capture.atoms if row.get('id') == target['ref_id']) + 1
        destination = root / 'draft' / path.name.replace(target['ref_id'] + '-', f"{target['ref_id']}@{version}-draft-", 1)
        candidate = _state_bytes(raw, bounds, path, version, body, 'draft')
        with bind_query_reader(None):
            outcome = common.write_destination(selection.root, destination, candidate)
        data = {} if outcome.errors else {'savedDraft': common.saved(selection, destination, target['ref_id'],
                        f"{target['ref_id']}@{version}-draft", version, 'Draft')}
        return common.result(effects=outcome.effects, errors=outcome.errors, **data)


def _check_owner(selection, container, rows, capture):
    if container == {'component': 'C00'}:
        return
    if (not isinstance(container, dict) or set(container) != {'atom'}
            or not isinstance(container['atom'], str)
            or not re.fullmatch(re.escape(selection.project_prefix) + r'-T-[0-9]+', container['atom'])):
        raise common.InputError('container', 'Supply C00 or a Current native Task or Epic in this Project.')
    owner_id = container['atom']
    selected = [row for row in rows if row.get('id') == owner_id and row.get('status_group') == 'Current']
    fresh = [row for row in capture.atoms if row.get('id') == owner_id and row.get('status_group') == 'Current']
    if len(selected) != 1 or len(fresh) != 1 or any(selected[0].get(key) != fresh[0].get(key) for key in (
            'source_path', 'id', '_exact_ref', 'version', 'status', 'status_group', 'header_json', '_source_sha256')):
        raise common.SourceChanged('Containing Task or Epic is missing or changed.')
    row = fresh[0]
    header = row.get('header_json')
    context = header.get('context') if isinstance(header, dict) else None
    template = context.get('template') if isinstance(context, dict) else None
    status = row.get('status')
    if template not in {'task', 'epic'} or status not in {'active', 'backlog', 'done', 'canceled', 'resolved'}:
        raise common.InputError('container', 'Containing Atom must be a Current Task or Epic.')
    relative = row.get('source_path')
    if not isinstance(relative, str):
        raise common.SourceChanged('Containing Atom path is invalid.')
    relative = Path(relative)
    root = selection.control_root / '__TKT' / 'TASKS'
    path = selection.root / relative
    directory = () if status == 'active' else (status,)
    if (relative.is_absolute() or '..' in relative.parts or not path.is_relative_to(root)
            or path.relative_to(root).parts[:-1] != directory
            or not re.fullmatch(re.escape(owner_id) + '-' + template.upper() + r'--.+\.md', path.name)):
        raise common.InputError('container', 'Containing Atom is outside its native Task branch.')


def _create_task(selection, values, current_rows):
    if (not isinstance(values, dict) or set(values) != {'template', 'container', 'body'}
            or values['template'] != 'task' or not isinstance(values['body'], str)):
        raise common.InputError('newAtom', 'Supply a Task template, container, and Markdown body.')
    body = values['body']
    try:
        slug = _native_slug(body)
        body_bytes = body.encode('utf-8')
    except (ValueError, UnicodeError) as error:
        if isinstance(error, common.InputError):
            raise
        raise common.InputError('summary', 'Summary cannot be used in a Task filename.') from error
    if (not selection.root.is_absolute() or not selection.control_root.is_relative_to(selection.root)
            or not selection.manifest_path.is_relative_to(selection.control_root)):
        raise common.SourceChanged('Selected Project path is invalid.')
    with _project_write_lock(selection.root):
        try:
            capture = capture_native(selection)
            if capture.errors:
                raise common.SourceChanged('Native carrier capture is incomplete.')
            _check_owner(selection, values['container'], current_rows, capture)
            pattern = re.compile(re.escape(selection.project_prefix) + r'-T-([0-9]+)')
            numbers = [int(match[1]) for row in capture.atoms
                       if isinstance(row.get('id'), str) and (match := pattern.fullmatch(row['id']))]
            atom_id = f"{selection.project_prefix}-T-{max(numbers, default=0) + 1}"
            ref = f'{atom_id}@1-draft'
            path = selection.control_root / '__TKT' / 'TASKS' / 'draft' / f'{ref}-TASK--{slug}.md'
            header = {'identity': {'atom_id': atom_id},
                      'context': {'container': values['container'], 'template': 'task'},
                      'state': {'status': 'draft', 'version': 1, 'updated_at': datetime.now(timezone.utc).isoformat()}}
            raw = b'---\n' + yaml.safe_dump(header, sort_keys=False).encode() + b'---\n' + body_bytes
        except (common.InputError, common.SourceChanged):
            raise
        except (OSError, RuntimeError, TypeError, ValueError) as error:
            raise common.SourceChanged('Native Project source is unavailable or changed.') from error
        with bind_query_reader(None):
            outcome = common.write_destination(selection.root, path, raw)
        data = {} if outcome.errors else {'savedDraft': common.saved(selection, path, atom_id, ref, 1, 'Draft')}
        return common.result(effects=outcome.effects, errors=outcome.errors, **data)


def _promote_new(selection, target, status, draft, current_rows):
    atom_id = target['ref_id'].split('@')[0]
    relative, digest = draft.get('source_path'), draft.get('_source_sha256')
    if (not isinstance(relative, str) or not isinstance(digest, str)
            or not re.fullmatch(r'[0-9a-f]{64}', digest)):
        raise common.SourceChanged('Draft capture lacks a valid path or digest.')
    relative = Path(relative)
    root = selection.control_root / '__TKT' / 'TASKS'
    path = selection.root / relative
    if (not selection.root.is_absolute() or not selection.control_root.is_relative_to(selection.root)
            or not selection.manifest_path.is_relative_to(selection.control_root)
            or relative.is_absolute() or '..' in relative.parts or not path.is_relative_to(root)
            or path.parent != root / 'draft'
            or not re.fullmatch(re.escape(target['ref_id']) + r'-TASK--.+\.md', path.name)):
        raise common.SourceChanged('Task Draft path is invalid.')
    with _project_write_lock(selection.root):
        try:
            capture = capture_native(selection)
            rows = [row for row in capture.atoms if row.get('id') == atom_id]
            if (capture.errors or len(rows) != 1 or any(rows[0].get(key) != draft.get(key) for key in (
                    'source_path', 'id', 'ref', '_exact_ref', 'version', 'status', 'status_group',
                    'header_json', '_content_bytes', '_source_sha256'))):
                raise common.SourceChanged('Task Draft changed or its identity already has history.')
            header = draft.get('header_json')
            context = header.get('context') if isinstance(header, dict) else None
            if not isinstance(context, dict) or context.get('template') != 'task':
                raise common.InputError('target', 'Select a native Task Draft.')
            _check_owner(selection, context.get('container'), current_rows, capture)
            reader = ReadContext(roots=[str(selection.control_root)], limits=dict(CEILINGS))
            raw = reader.read(path)
            bounds = frontmatter_bounds(raw)
            if (bounds is None or sha256(raw).hexdigest() != digest or raw[bounds[2]:] != draft.get('_content_bytes')
                    or parse_carrier(raw, path).metadata != header or reader.currentness()['state'] != 'unchanged'):
                raise common.SourceChanged('Task Draft source changed after selection.')
            body = raw[bounds[2]:].decode('utf-8')
            slug = _native_slug(body)
            if path.name != f"{target['ref_id']}-TASK--{slug}.md":
                raise common.InputError('target', 'Task Draft filename disagrees with its Summary.')
            destination = root / ('' if status == 'active' else status) / f'{atom_id}-TASK--{slug}.md'
            if destination.exists() or destination.is_symlink():
                raise common.InputError('target', 'The promotion destination already exists.')
            if destination.parent.is_symlink() or (destination.parent.exists() and not destination.parent.is_dir()):
                raise common.InputError('target', 'The promotion destination directory is unsafe.')
            promoted = _state_bytes(raw, bounds, path, 1, body, status)
        except (common.InputError, common.SourceChanged):
            raise
        except (OSError, RuntimeError, TypeError, ValueError) as error:
            raise common.SourceChanged('Native source is unavailable or changed.') from error
        with bind_query_reader(None):
            written = common.write_destination(selection.root, destination, promoted)
            recorded = list(written.effects)
            if written.errors:
                return common.result(effects=recorded, errors=written.errors)
            removed = effects.remove(selection.root, path, digest)
            recorded.extend(removed.effects)
        data = {} if removed.errors else {'artifact': common.saved(selection, destination, atom_id, atom_id, 1, status)}
        return common.result(effects=recorded, errors=removed.errors, **data)


def _cleanup_published_draft(selection, target, status, draft, current):
    atom_id, version = target['ref_id'].split('@')[0], target['version']
    if current.get('status') != status:
        raise common.InputError('targetStatus', 'Published Task Status differs from the requested Status.')
    root = selection.control_root / '__TKT' / 'TASKS'
    paths = []
    for row, marker, directory in ((draft, target['ref_id'], ('draft',)),
                                   (current, atom_id, () if status == 'active' else (status,))):
        relative, digest = row.get('source_path'), row.get('_source_sha256')
        if not isinstance(relative, str) or not isinstance(digest, str) or not re.fullmatch(r'[0-9a-f]{64}', digest):
            raise common.SourceChanged('Task capture lacks a valid path or digest.')
        relative = Path(relative)
        path = selection.root / relative
        if (not selection.root.is_absolute() or not selection.control_root.is_relative_to(selection.root)
                or not selection.manifest_path.is_relative_to(selection.control_root)
                or relative.is_absolute() or '..' in relative.parts or not path.is_relative_to(root)
                or path.relative_to(root).parts[:-1] != directory
                or not re.fullmatch(re.escape(marker) + r'-TASK--.+\.md', path.name)):
            raise common.SourceChanged('Task path is invalid.')
        paths.append(path)
    if paths[0].name[len(target['ref_id']):] != paths[1].name[len(atom_id):]:
        raise common.InputError('target', 'Published Task filename differs from the Draft.')
    with _project_write_lock(selection.root):
        try:
            capture = capture_native(selection)
            if capture.errors:
                raise common.SourceChanged('Native carrier capture is incomplete.')
            for row in (draft, current):
                fresh = [item for item in capture.atoms if item.get('_exact_ref') == row.get('_exact_ref')]
                if len(fresh) != 1 or any(fresh[0].get(key) != row.get(key) for key in (
                        'source_path', 'id', 'ref', '_exact_ref', 'version', 'status', 'status_group',
                        'header_json', '_content_bytes', '_source_sha256')):
                    raise common.SourceChanged('Draft or published Task changed after selection.')
            reader = ReadContext(roots=[str(selection.control_root)], limits=dict(CEILINGS))
            for row, path in zip((draft, current), paths):
                raw = reader.read(path)
                bounds = frontmatter_bounds(raw)
                if (bounds is None or sha256(raw).hexdigest() != row['_source_sha256']
                        or raw[bounds[2]:] != row.get('_content_bytes')
                        or parse_carrier(raw, path).metadata != row.get('header_json')):
                    raise common.SourceChanged('Draft or published Task changed after selection.')
            if reader.currentness()['state'] != 'unchanged':
                raise common.SourceChanged('Draft or published Task changed after selection.')
            draft_header, current_header = draft['header_json'], current['header_json']
            if (draft_header.get('context', {}).get('template') != 'task'
                    or {key: value for key, value in draft_header.items() if key != 'state'}
                    != {key: value for key, value in current_header.items() if key != 'state'}
                    or draft['_content_bytes'] != current['_content_bytes']):
                raise common.InputError('target', 'Published Task differs from the Draft.')
        except (common.InputError, common.SourceChanged):
            raise
        except (OSError, RuntimeError, TypeError, ValueError) as error:
            raise common.SourceChanged('Native source is unavailable or changed.') from error
        with bind_query_reader(None):
            removed = effects.remove(selection.root, paths[0], draft['_source_sha256'])
        data = {} if removed.errors else {'artifact': common.saved(selection, paths[1], atom_id, atom_id, version, status)}
        return common.result(effects=removed.effects, errors=removed.errors, **data)


def _rollback_promotion(selection, previous_path, previous_digest, created, recorded, errors):
    errors = list(errors)
    for path, raw in reversed(created):
        try:
            reader = ReadContext(roots=[str(selection.control_root)], limits=dict(CEILINGS))
            if sha256(reader.read(previous_path)).hexdigest() != previous_digest:
                raise ValueError('Current changed')
            if reader.currentness()['state'] != 'unchanged':
                raise ValueError('Current changed')
        except (OSError, RuntimeError, ValueError):
            errors.append({'code': 'rollback_unconfirmed', 'message': 'Current is no longer pinned; generated carriers were retained.'})
            break
        removed = effects.remove(selection.root, path, sha256(raw).hexdigest())
        recorded.extend(removed.effects)
        if removed.errors:
            errors.extend(removed.errors)
            errors.append({'code': 'rollback_unconfirmed', 'message': 'A generated carrier could not be safely removed.'})
    return common.result(effects=recorded, errors=errors)


def promote_draft(selection, params, *, current_rows, migration_refs):
    """Archive the pinned predecessor and publish one unpinned Task Draft."""
    if not isinstance(params, dict) or set(params) != {'target', 'targetStatus'}:
        raise common.InputError('target', 'Supply an exact Draft target and Current Status.')
    target, status = params['target'], params['targetStatus']
    if (not isinstance(target, dict) or set(target) != {'ref_id', 'version'}
            or not isinstance(target['ref_id'], str) or type(target['version']) is not int
            or target['version'] < 1):
        raise common.InputError('target', 'Supply an exact Task Draft reference and Version.')
    match = re.fullmatch(rf'({re.escape(selection.project_prefix)}-T-[0-9]+)@([1-9][0-9]*)-draft', target['ref_id'])
    if match is None or int(match[2]) != target['version']:
        raise common.InputError('target', 'Supply an exact Task Draft reference and matching Version.')
    if not isinstance(status, str) or status not in {'active', 'backlog', 'done', 'canceled', 'resolved'}:
        raise common.InputError('targetStatus', 'Supply a Current Ticket Status.')
    try:
        refs = tuple(migration_refs)
        if any(not isinstance(item, (tuple, list)) or len(item) != 3 or not isinstance(item[2], str) for item in refs):
            raise ValueError('Invalid migration references')
    except (TypeError, ValueError) as error:
        raise common.SourceChanged('Migration references are unavailable or invalid.') from error
    if any(item[2] == target['ref_id'] for item in refs):
        raise common.InputError('target', 'A migration-pinned Draft cannot be promoted.')

    atom_id, version = match[1], target['version']
    chosen = [row for row in current_rows if row.get('_exact_ref') == target['ref_id'] and row.get('status_group') == 'Draft']
    predecessors = [row for row in current_rows if row.get('id') == atom_id and row.get('status_group') == 'Current']
    if len(chosen) != 1 or len(predecessors) > 1:
        raise common.SourceChanged('Draft or Current predecessor is missing or ambiguous.')
    if not predecessors:
        if version != 1:
            raise common.SourceChanged('Current predecessor is missing.')
        return _promote_new(selection, target, status, chosen[0], current_rows)
    draft, previous = chosen[0], predecessors[0]
    if previous.get('version') == version:
        return _cleanup_published_draft(selection, target, status, draft, previous)
    if type(previous.get('version')) is not int or previous['version'] >= version:
        raise common.InputError('target', 'Draft Version must be newer than its Current predecessor.')
    root = selection.control_root / '__TKT' / 'TASKS'
    paths = []
    for row, marker, group in ((draft, target['ref_id'], 'draft'), (previous, atom_id, previous.get('status'))):
        relative, digest = row.get('source_path'), row.get('_source_sha256')
        if (not isinstance(relative, str) or not isinstance(digest, str)
                or not re.fullmatch(r'[0-9a-f]{64}', digest)):
            raise common.SourceChanged('Task capture lacks a valid path or source digest.')
        relative = Path(relative)
        path = selection.root / relative
        if (not selection.root.is_absolute() or not selection.control_root.is_relative_to(selection.root)
                or not selection.manifest_path.is_relative_to(selection.control_root)
                or relative.is_absolute() or '..' in relative.parts or not path.is_relative_to(root)):
            raise common.SourceChanged('Task path is invalid.')
        directory = () if group == 'active' else (group,)
        header = row.get('header_json')
        context = header.get('context') if isinstance(header, dict) else None
        if (not isinstance(group, str) or group not in {'draft', 'active', 'backlog', 'done', 'canceled', 'resolved'}
                or path.relative_to(root).parts[:-1] != directory
                or not re.fullmatch(re.escape(marker) + r'-TASK--.+\.md', path.name)
                or not isinstance(context, dict) or context.get('template') != 'task'):
            raise common.InputError('target', 'Select Task carriers in their native status directories.')
        paths.append(path)
    draft_path, previous_path = paths
    suffix = draft_path.name[len(target['ref_id']):]
    if previous_path.name != atom_id + suffix:
        raise common.InputError('target', 'Task Draft and Current filename must agree.')
    archive_path = root / 'archived' / f"{atom_id}@{previous['version']}{suffix}"
    destination = root / ('' if status == 'active' else status) / (atom_id + suffix)

    with _project_write_lock(selection.root):
        try:
            capture = capture_native(selection)
            if capture.errors:
                raise common.SourceChanged('Native carrier capture is incomplete.')
            for row in (draft, previous):
                fresh = [item for item in capture.atoms if item.get('_exact_ref') == row.get('_exact_ref')]
                if len(fresh) != 1 or any(fresh[0].get(key) != row.get(key) for key in (
                        'source_path', 'id', 'ref', '_exact_ref', 'version', 'status', 'status_group',
                        'header_json', '_content_bytes', '_source_sha256')):
                    raise common.SourceChanged('Task Draft or Current predecessor changed after selection.')
            if any(row.get('id') == atom_id and row.get('version') == version
                   and row.get('status_group') != 'Draft' for row in capture.atoms):
                raise common.InputError('target', 'The Draft Version already has a non-Draft revision.')
            reader = ReadContext(roots=[str(selection.control_root)], limits=dict(CEILINGS))
            raw_draft, raw_previous = (reader.read(path) for path in paths)
            for row, path, raw in zip((draft, previous), paths, (raw_draft, raw_previous)):
                bounds = frontmatter_bounds(raw)
                if (bounds is None or sha256(raw).hexdigest() != row['_source_sha256']
                        or raw[bounds[2]:] != row.get('_content_bytes')
                        or parse_carrier(raw, path).metadata != row.get('header_json')):
                    raise common.SourceChanged('Task Draft or Current predecessor changed after selection.')
            draft_bounds, previous_bounds = frontmatter_bounds(raw_draft), frontmatter_bounds(raw_previous)
            draft_body, previous_body = raw_draft[draft_bounds[2]:].decode(), raw_previous[previous_bounds[2]:].decode()
            draft_header, previous_header = draft['header_json'], previous['header_json']
            if ({key: value for key, value in draft_header.items() if key != 'state'}
                    != {key: value for key, value in previous_header.items() if key != 'state'}
                    or _summary(draft_body) != _summary(previous_body)):
                raise common.InputError('target', 'Only a body revision with unchanged Summary is supported.')
            if archive_path.exists() or archive_path.is_symlink() or (destination != previous_path and
                    (destination.exists() or destination.is_symlink())):
                raise common.InputError('target', 'A promotion destination already exists.')
            if destination != previous_path and (previous_path.with_suffix('').exists() or previous_path.with_suffix('').is_symlink()):
                raise common.InputError('target', 'A Task with a companion directory cannot change status here.')
            for parent in (archive_path.parent, destination.parent):
                if parent.is_symlink() or (parent.exists() and not parent.is_dir()):
                    raise common.InputError('target', 'A promotion destination directory is unsafe.')
            archive = _state_bytes(raw_previous, previous_bounds, previous_path, previous['version'], previous_body, 'archived')
            promoted = _state_bytes(raw_draft, draft_bounds, draft_path, version, draft_body, status)
        except (common.InputError, common.SourceChanged):
            raise
        except (OSError, RuntimeError, TypeError, ValueError) as error:
            raise common.SourceChanged('Native sources are unavailable or changed.') from error

        recorded, created = [], []
        with bind_query_reader(None):
            written = common.write_destination(selection.root, archive_path, archive)
            recorded.extend(written.effects)
            if any(item.get('operation') == 'create' and item.get('target') == archive_path.relative_to(selection.root).as_posix()
                   for item in written.effects):
                created.append((archive_path, archive))
            if written.errors:
                return _rollback_promotion(selection, previous_path, previous['_source_sha256'], created, recorded, written.errors)
            try:
                reader = ReadContext(roots=[str(selection.control_root)], limits=dict(CEILINGS))
                if (sha256(reader.read(draft_path)).hexdigest() != draft['_source_sha256']
                        or sha256(reader.read(selection.manifest_path)).hexdigest() != selection.manifest_sha256
                        or reader.currentness()['state'] != 'unchanged'):
                    raise ValueError('Source changed')
            except (OSError, RuntimeError, ValueError):
                return _rollback_promotion(selection, previous_path, previous['_source_sha256'], created, recorded,
                    [{'code': 'source_changed', 'message': 'Draft or Manifest changed after archival.'}])
            if destination == previous_path:
                published = effects.replace(selection.root, previous_path, previous['_source_sha256'], promoted)
                recorded.extend(published.effects)
                if published.errors:
                    return _rollback_promotion(selection, previous_path, previous['_source_sha256'], created, recorded, published.errors)
            else:
                published = common.write_destination(selection.root, destination, promoted)
                recorded.extend(published.effects)
                if any(item.get('operation') == 'create' and item.get('target') == destination.relative_to(selection.root).as_posix()
                       for item in published.effects):
                    created.append((destination, promoted))
                if published.errors:
                    return _rollback_promotion(selection, previous_path, previous['_source_sha256'], created, recorded, published.errors)
                removed = effects.remove(selection.root, previous_path, previous['_source_sha256'])
                recorded.extend(removed.effects)
                if removed.errors:
                    return _rollback_promotion(selection, previous_path, previous['_source_sha256'], created, recorded, removed.errors)
            removed = effects.remove(selection.root, draft_path, draft['_source_sha256'])
            recorded.extend(removed.effects)
        data = {} if removed.errors else {'artifact': common.saved(selection, destination, atom_id, atom_id, version, status)}
        return common.result(effects=recorded, errors=removed.errors, **data)
