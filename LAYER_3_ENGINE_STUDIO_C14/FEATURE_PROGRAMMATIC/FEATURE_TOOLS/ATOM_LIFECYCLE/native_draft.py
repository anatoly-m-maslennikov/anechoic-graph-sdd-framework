"""Create and promote bounded same-ID native Draft revisions."""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
from types import SimpleNamespace
import re

import yaml

from native_carrier_header import canonical_native_header, native_header_view
from native_carrier_placement import native_carrier_path, native_ticket_label, spec_lens_directories

from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.native_source_rows import capture_native
from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.source_rows import frontmatter_bounds
from VALIDATE_ATOMS.validate_atoms_workers.parsing import parse_carrier
from VALIDATE_ATOMS.validate_atoms_workers.read_io import ReadContext
from VALIDATE_ATOMS.validate_atoms_workers.settings import CEILINGS

from . import common, effects
from .backend import _project_write_lock
from .placement import _slug
from .source import bind_query_reader


def _revision_root(selection, row, structure_snapshot=None, current_rows=None):
    """Validate a Current carrier and return its owning revision directory."""
    relative = row.get("source_path")
    if not isinstance(relative, str):
        raise common.SourceChanged("Current carrier path is invalid.")
    relative = Path(relative)
    path = selection.root / relative
    if (not selection.root.is_absolute() or not selection.control_root.is_relative_to(selection.root)
            or not selection.manifest_path.is_relative_to(selection.control_root)
            or relative.is_absolute() or ".." in relative.parts or not path.is_relative_to(selection.control_root)
            or path == selection.manifest_path):
        raise common.InputError("sourceCurrent", "Select an admitted Current carrier.")
    atom_id = row.get("id", "")
    header = native_header_view(row.get("header_json"))
    context = header.get("context") if isinstance(header, dict) else None
    if not isinstance(context, dict):
        raise common.InputError("sourceCurrent", "Current carrier context is invalid.")
    status = row.get("status")
    if "-T-" in atom_id:
        if current_rows is None:
            raise common.SourceChanged('Current owner capture is unavailable.')
        capture = SimpleNamespace(atoms=current_rows)
        owner_directory, _ = _check_owner(selection, context.get("container"), current_rows, capture)
        flat_root = selection.control_root / "__TKT" / "TASKS"
        root = owner_directory or flat_root
        if path.parent == flat_root / ("" if status == "active" else str(status)):
            root = flat_root
        directory = () if status == "active" else (status,)
        template = context.get("template")
        if (not isinstance(status, str) or status not in {"active", "backlog", "done", "canceled", "resolved"}
                or template not in {"task", "epic"} or not path.is_relative_to(root)
                or path.relative_to(root).parts[:-1] != directory
                or not re.fullmatch(re.escape(atom_id) + (r"-.+--.+\.md" if "atom_family" in row["header_json"]
                                                         else "-" + template.upper() + r"--.+\.md"), path.name)):
            raise common.InputError("sourceCurrent", "Select a native Task or Epic in its Current directory.")
        return root
    if status != "active" or not re.fullmatch(re.escape(atom_id) + r"-.+\.md", path.name):
        raise common.InputError("sourceCurrent", "Select an active native carrier.")
    if "-P-" in atom_id:
        root = selection.control_root / "_PMETA"
        if path.parent != root:
            raise common.InputError("sourceCurrent", "Select a direct PMETA carrier.")
        return root
    lens = context.get("lens")
    container = context.get("container")
    if not isinstance(lens, str) or not isinstance(container, dict) or set(container) != {"component"}:
        raise common.InputError("sourceCurrent", "Select a component-owned SPEC carrier.")
    from native_project_selection import _manifest_inputs
    try:
        reader = ReadContext(roots=[str(selection.control_root)], limits=dict(CEILINGS))
        raw = reader.read(selection.manifest_path)
        if sha256(raw).hexdigest() != selection.manifest_sha256:
            raise ValueError("Manifest changed")
        _, project_component = _manifest_inputs(selection.manifest_path, parse_carrier(raw, selection.manifest_path))
        root = path.parent
        for directory in reversed(spec_lens_directories(lens)):
            if root.name.upper() != directory:
                raise ValueError("Lens path disagrees")
            root = root.parent
        component = container["component"]
        if (not root.is_relative_to(selection.control_root) or
                (root == selection.control_root and component != project_component) or
                (root != selection.control_root and not root.name.endswith("_" + component))):
            raise ValueError("Component path disagrees")
        if any(part.startswith("_") or not re.search(r"_C[0-9]+$", part)
               for part in root.relative_to(selection.control_root).parts):
            raise ValueError("Nested carrier path")
        snapshot_path = getattr(selection, "structure_snapshot", None)
        if (structure_snapshot is not None or snapshot_path is not None) and root != selection.control_root:
            from LAYER_3_ENGINE_STUDIO_C14.KERNEL_MIXER_C59.MANIFEST_RUNTIME_C62.structure_host_pkg3.snapshot import (
                read_structure,
            )

            snapshot = structure_snapshot if structure_snapshot is not None else read_structure(snapshot_path)
            declaration = selection.control_root / snapshot.component(component).source_path
            if declaration.parent != root.parent:
                raise ValueError("Component parent contradicts the current Structure")
    except (OSError, RuntimeError, TypeError, ValueError, AttributeError, KeyError) as error:
        raise common.InputError("sourceCurrent", "SPEC carrier must be in its lens and component root.") from error
    return root


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


def _task_path(selection, header, body, status, version, owner, root=None):
    projected = {**header, 'state': {**header['state'], 'status': status, 'version': version}}
    try:
        owner_directory, owner_template = owner
        path = native_carrier_path(projected, _summary(body), project_root=selection.control_root,
                                   owner_directory=owner_directory, owner_template=owner_template)
        flat_root = selection.control_root / '__TKT' / 'TASKS'
        if root == flat_root and owner_directory is not None:
            directory = '000_draft' if status == 'draft' else '099_archived' if status == 'archived' else '' if status == 'active' else status
            return flat_root / directory / path.name
        return path
    except ValueError as error:
        raise common.InputError('summary', 'Task Header or Summary cannot be projected to a path.') from error


def create_draft(selection, params, *, current_rows, structure_snapshot=None):
    if isinstance(params, dict) and 'newAtom' in params:
        if set(params) != {'newAtom'}:
            raise common.InputError('newAtom', 'Supply only new Task properties.')
        return _create_task(selection, params['newAtom'], current_rows)
    if not isinstance(params, dict) or set(params) - {'sourceCurrent', 'changes'} or 'sourceCurrent' not in params:
        raise common.InputError('sourceCurrent', 'Supply one Current carrier and optional body change.')
    target = params['sourceCurrent']
    if (not isinstance(target, dict) or set(target) != {'ref_id', 'version'}
            or not isinstance(target['ref_id'], str)
            or not re.fullmatch(re.escape(selection.project_prefix) + r'-[STP]-[0-9]+', target['ref_id'])
            or type(target['version']) is not int or target['version'] < 1):
        raise common.InputError('sourceCurrent', 'Supply a Current carrier reference and positive Version.')
    changes = params.get('changes', {})
    if not isinstance(changes, dict) or set(changes) - {'body'} or ('body' in changes and not isinstance(changes['body'], str)):
        raise common.InputError('changes', 'Supply only a Markdown body change.')
    matches = [row for row in current_rows if row.get('id') == target['ref_id'] and row.get('status_group') == 'Current']
    if len(matches) != 1 or matches[0].get('version') != target['version']:
        raise common.SourceChanged('Current carrier selection is missing, ambiguous, or stale.')
    selected = matches[0]
    digest, relative = selected.get('_source_sha256'), selected.get('source_path')
    if (not isinstance(digest, str) or not re.fullmatch(r'[0-9a-f]{64}', digest)
            or not isinstance(relative, str)):
        raise common.SourceChanged('Current carrier capture lacks a valid path or source digest.')
    path = selection.root / relative
    root = _revision_root(selection, selected, structure_snapshot, current_rows)
    with _project_write_lock(selection.root):
        try:
            capture = capture_native(selection)
            fresh = [row for row in capture.atoms if row.get('id') == target['ref_id'] and row.get('status_group') == 'Current']
            if capture.errors or len(fresh) != 1 or any(fresh[0].get(key) != selected.get(key) for key in (
                    'source_path', 'id', 'ref', '_exact_ref', 'version', 'status', 'status_group',
                    'header_json', '_content_bytes', '_source_sha256')):
                raise common.SourceChanged('Current carrier source changed after selection.')
            raw = ReadContext(roots=[str(selection.control_root)], limits=dict(CEILINGS)).read(path)
            bounds = frontmatter_bounds(raw)
            if (bounds is None or sha256(raw).hexdigest() != digest
                    or raw[bounds[2]:] != selected.get('_content_bytes')
                    or parse_carrier(raw, path).metadata != selected.get('header_json')):
                raise common.SourceChanged('Current carrier source changed after selection.')
            old_body = raw[bounds[2]:].decode('utf-8')
            if '-T-' in target['ref_id']:
                owner = _check_owner(selection, native_header_view(selected['header_json'])['context'].get('container'), current_rows, capture)
        except common.SourceChanged:
            raise
        except (OSError, RuntimeError, TypeError, ValueError) as error:
            raise common.SourceChanged('Native source is unavailable or changed.') from error
        body = changes.get('body', old_body)
        if _summary(body) != _summary(old_body):
            raise common.InputError('summary', 'Changing a Summary is not supported.')
        version = max(row['version'] for row in capture.atoms if row.get('id') == target['ref_id']) + 1
        if '-T-' in target['ref_id'] and 'atom_family' in selected['header_json']:
            if _task_path(selection, selected['header_json'], old_body, selected['status'], target['version'], owner, root) != path:
                raise common.InputError('sourceCurrent', 'Task path disagrees with its authored Header and Summary.')
            destination = _task_path(selection, selected['header_json'], body, 'draft', version, owner, root)
        else:
            destination = root / '000_draft' / path.name.replace(target['ref_id'] + '-', f"{target['ref_id']}@{version}-draft-", 1)
        candidate = _state_bytes(raw, bounds, path, version, body, 'draft')
        with bind_query_reader(None):
            outcome = common.write_destination(selection.root, destination, candidate)
        data = {} if outcome.errors else {'savedDraft': common.saved(selection, destination, target['ref_id'],
                        f"{target['ref_id']}@{version}-draft", version, 'Draft')}
        return common.result(effects=outcome.effects, errors=outcome.errors, **data)


def _check_owner(selection, container, rows, capture, seen=None):
    if isinstance(container, dict) and set(container) == {'component'}:
        return None, None
    if (not isinstance(container, dict) or set(container) != {'atom'}
            or not isinstance(container['atom'], str)
            or not re.fullmatch(re.escape(selection.project_prefix) + r'-T-[0-9]+', container['atom'])):
        raise common.InputError('container', 'Supply C00 or a Current native Task or Epic in this Project.')
    owner_id = container['atom']
    seen = set() if seen is None else seen
    if owner_id in seen:
        raise common.InputError('container', 'Containing Atom cycle is invalid.')
    seen.add(owner_id)
    selected = [row for row in rows if row.get('id') == owner_id and row.get('status_group') == 'Current']
    fresh = [row for row in capture.atoms if row.get('id') == owner_id and row.get('status_group') == 'Current']
    if len(selected) != 1 or len(fresh) != 1 or any(selected[0].get(key) != fresh[0].get(key) for key in (
            'source_path', 'id', '_exact_ref', 'version', 'status', 'status_group', 'header_json', '_source_sha256')):
        raise common.SourceChanged('Containing Task or Epic is missing or changed.')
    row = fresh[0]
    header = native_header_view(row.get('header_json'))
    context = header.get('context') if isinstance(header, dict) else None
    template = context.get('template') if isinstance(context, dict) else None
    status = row.get('status')
    if template not in {'task', 'epic'} or status not in {'active', 'backlog', 'done', 'canceled', 'resolved'}:
        raise common.InputError('container', 'Containing Atom must be a Current Task or Epic.')
    relative = row.get('source_path')
    if not isinstance(relative, str):
        raise common.SourceChanged('Containing Atom path is invalid.')
    relative = Path(relative)
    parent_directory, _ = _check_owner(selection, context.get('container'), rows, capture, seen)
    root = parent_directory or selection.control_root / '__TKT' / 'TASKS'
    path = selection.root / relative
    flat_root = selection.control_root / '__TKT' / 'TASKS'
    if path.parent == flat_root / ('' if status == 'active' else status):
        root = flat_root
    directory = () if status == 'active' else (status,)
    if (relative.is_absolute() or '..' in relative.parts or not path.is_relative_to(root)
            or path.relative_to(root).parts[:-1] != directory
            or not re.fullmatch(re.escape(owner_id) + (r'-.+\.md' if 'atom_family' in row['header_json']
                                                          else '-' + template.upper() + r'--.+\.md'), path.name)):
        raise common.InputError('container', 'Containing Atom is outside its native Task branch.')
    try:
        reader = ReadContext(roots=[str(selection.control_root)], limits=dict(CEILINGS))
        raw = reader.read(path)
        if (sha256(raw).hexdigest() != row.get('_source_sha256')
                or parse_carrier(raw, path).metadata != row.get('header_json')
                or reader.currentness()['state'] != 'unchanged'):
            raise ValueError('Owner changed')
    except (OSError, RuntimeError, TypeError, ValueError) as error:
        raise common.SourceChanged('Containing Task or Epic source changed.') from error
    return path.with_suffix(''), template


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
            if (not isinstance(values['container'], dict) or
                    (values['container'] != {'component': 'C00'} and 'atom' not in values['container'])):
                raise common.InputError('container', 'Supply C00 or a Current native Task or Epic in this Project.')
            owner = _check_owner(selection, values['container'], current_rows, capture)
            _, owner_template = owner
            pattern = re.compile(re.escape(selection.project_prefix) + r'-T-([0-9]+)')
            numbers = [int(match[1]) for row in capture.atoms
                       if isinstance(row.get('id'), str) and (match := pattern.fullmatch(row['id']))]
            atom_id = f"{selection.project_prefix}-T-{max(numbers, default=0) + 1}"
            ref = f'{atom_id}@1-draft'
            context = {'container': values['container'], 'priority': 2, 'template': 'task'}
            label = native_ticket_label('task', owner_template)
            if label:
                context['label'] = label
            header = canonical_native_header(
                {'identity': {'atom_id': atom_id},
                 'context': context,
                 'state': {'status': 'draft', 'version': 1, 'updated_at': datetime.now(timezone.utc).isoformat()}})
            path = _task_path(selection, header, body, 'draft', 1, owner)
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
            or path.parent.name != '000_draft'
            or not re.fullmatch(re.escape(target['ref_id']) + r'-.+--.+\.md', path.name)):
        raise common.SourceChanged('Task Draft path is invalid.')
    root = root if path.parent == root / '000_draft' else None
    with _project_write_lock(selection.root):
        try:
            capture = capture_native(selection)
            rows = [row for row in capture.atoms if row.get('id') == atom_id]
            if (capture.errors or len(rows) != 1 or any(rows[0].get(key) != draft.get(key) for key in (
                    'source_path', 'id', 'ref', '_exact_ref', 'version', 'status', 'status_group',
                    'header_json', '_content_bytes', '_source_sha256'))):
                raise common.SourceChanged('Task Draft changed or its identity already has history.')
            header = draft.get('header_json')
            context = native_header_view(header).get('context')
            if not isinstance(context, dict) or context.get('template') != 'task':
                raise common.InputError('target', 'Select a native Task Draft.')
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
                        else root / '000_draft' / f"{target['ref_id']}-TASK--{slug}.md"):
                raise common.InputError('target', 'Task Draft filename disagrees with its Summary.')
            destination = (_task_path(selection, header, body, status, 1, owner, root) if 'atom_family' in header
                           else root / ('' if status == 'active' else status) / f'{atom_id}-TASK--{slug}.md')
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


def _publish_first_pinned_spec(selection, draft, structure_snapshot):
    atom_id, ref_id = draft['id'], draft['_exact_ref']
    relative, digest = draft.get('source_path'), draft.get('_source_sha256')
    if (not isinstance(relative, str) or not isinstance(digest, str)
            or not re.fullmatch(r'[0-9a-f]{64}', digest)):
        raise common.SourceChanged('Draft capture lacks a valid path or digest.')
    relative = Path(relative)
    path = selection.root / relative
    if (relative.is_absolute() or '..' in relative.parts or not path.is_relative_to(selection.control_root)
            or path.parent.name != '000_draft' or not re.fullmatch(re.escape(ref_id) + r'-.+\.md', path.name)):
        raise common.InputError('target', 'Select a Spec in its native Draft directory.')
    with _project_write_lock(selection.root):
        try:
            capture = capture_native(selection)
            history = [row for row in capture.atoms if row['id'] == atom_id]
            matching = [row for row in history if row['_exact_ref'] == ref_id]
            if capture.errors or matching != [draft] or any(row['status_group'] != 'Draft' for row in history):
                raise common.SourceChanged('Spec Draft changed or the identity has published revisions.')
            header = draft['header_json']
            context = native_header_view(header)['context']
            lens = context.get('lens')
            if context.get('template') is not None:
                raise common.InputError('target', 'Select a Spec Draft with a lens and without a structural template.')
            owner = path.parent.parent
            try:
                directory = owner.joinpath(*spec_lens_directories(lens))
            except ValueError as error:
                raise common.InputError('target', 'Select a Spec Draft with a valid Lens.') from error
            destination = directory / (atom_id + path.name[len(ref_id):])
            proposed = {**draft, 'source_path': destination.relative_to(selection.root).as_posix(), 'status': 'active'}
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
            _summary(body)
            version = max(row['version'] for row in history) + 1
            promoted = _state_bytes(raw, bounds, path, version, body, 'active')
        except (common.InputError, common.SourceChanged):
            raise
        except (OSError, RuntimeError, TypeError, ValueError) as error:
            raise common.SourceChanged('Native Spec source is unavailable or changed.') from error
        with bind_query_reader(None):
            written = common.write_destination(selection.root, destination, promoted)
        data = {} if written.errors else {'artifact': common.saved(selection, destination, atom_id, atom_id, version, 'active')}
        return common.result(effects=written.effects, errors=written.errors, **data)


def _cleanup_published_draft(selection, target, status, draft, current, structure_snapshot, current_rows):
    atom_id, version = target['ref_id'].split('@')[0], target['version']
    if current.get('status') != status:
        raise common.InputError('targetStatus', 'Published carrier Status differs from the requested Status.')
    root = _revision_root(selection, current, structure_snapshot, current_rows)
    paths = []
    for row, marker, directory in ((draft, target['ref_id'], root / '000_draft'),
                                   (current, atom_id, (selection.root / current['source_path']).parent)):
        relative, digest = row.get('source_path'), row.get('_source_sha256')
        if not isinstance(relative, str) or not isinstance(digest, str) or not re.fullmatch(r'[0-9a-f]{64}', digest):
            raise common.SourceChanged('Carrier capture lacks a valid path or digest.')
        relative = Path(relative)
        path = selection.root / relative
        if (relative.is_absolute() or '..' in relative.parts or path.parent != directory
                or not re.fullmatch(re.escape(marker) + r'-.+\.md', path.name)):
            raise common.SourceChanged('Carrier path is invalid.')
        paths.append(path)
    if paths[0].name[len(target['ref_id']):] != paths[1].name[len(atom_id):]:
        raise common.InputError('target', 'Published carrier filename differs from the Draft.')
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
                    raise common.SourceChanged('Draft or published carrier changed after selection.')
            reader = ReadContext(roots=[str(selection.control_root)], limits=dict(CEILINGS))
            for row, path in zip((draft, current), paths):
                raw = reader.read(path)
                bounds = frontmatter_bounds(raw)
                if (bounds is None or sha256(raw).hexdigest() != row['_source_sha256']
                        or raw[bounds[2]:] != row.get('_content_bytes')
                        or parse_carrier(raw, path).metadata != row.get('header_json')):
                    raise common.SourceChanged('Draft or published carrier changed after selection.')
            if reader.currentness()['state'] != 'unchanged':
                raise common.SourceChanged('Draft or published carrier changed after selection.')
            draft_header, current_header = draft['header_json'], current['header_json']
            if '-T-' in atom_id:
                owner = _check_owner(selection, native_header_view(current_header)['context'].get('container'), current_rows, capture)
            if '-T-' in atom_id and 'atom_family' in current_header:
                body = draft['_content_bytes'].decode('utf-8')
                if (paths[0] != _task_path(selection, draft_header, body, 'draft', version, owner, root)
                        or paths[1] != _task_path(selection, current_header, body, status, version, owner, root)):
                    raise common.InputError('target', 'Task paths disagree with their authored Headers and Summary.')
            if ({key: value for key, value in draft_header.items() if key != 'state'}
                    != {key: value for key, value in current_header.items() if key != 'state'}
                    or draft['_content_bytes'] != current['_content_bytes']):
                raise common.InputError('target', 'Published carrier differs from the Draft.')
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


def promote_draft(selection, params, *, current_rows, migration_refs, structure_snapshot=None):
    """Publish a native Draft and keep any exact reference required by migration."""
    if not isinstance(params, dict) or set(params) != {'target', 'targetStatus'}:
        raise common.InputError('target', 'Supply an exact Draft target and Current Status.')
    target, status = params['target'], params['targetStatus']
    if (not isinstance(target, dict) or set(target) != {'ref_id', 'version'}
            or not isinstance(target['ref_id'], str) or type(target['version']) is not int
            or target['version'] < 1):
        raise common.InputError('target', 'Supply an exact Draft reference and Version.')
    match = re.fullmatch(rf'({re.escape(selection.project_prefix)}-[STP]-[0-9]+)@([1-9][0-9]*)-draft', target['ref_id'])
    if match is None or int(match[2]) != target['version']:
        raise common.InputError('target', 'Supply an exact Draft reference and matching Version.')
    if (not isinstance(status, str) or status not in {'active', 'backlog', 'done', 'canceled', 'resolved'}
            or ('-T-' not in match[1] and status != 'active')):
        raise common.InputError('targetStatus', 'Supply an applicable Current Status.')
    try:
        refs = tuple(migration_refs)
        if any(not isinstance(item, (tuple, list)) or len(item) != 3 or not isinstance(item[2], str) for item in refs):
            raise ValueError('Invalid migration references')
    except (TypeError, ValueError) as error:
        raise common.SourceChanged('Migration references are unavailable or invalid.') from error
    atom_id, version = match[1], target['version']
    chosen = [row for row in current_rows if row.get('_exact_ref') == target['ref_id'] and row.get('status_group') == 'Draft']
    predecessors = [row for row in current_rows if row.get('id') == atom_id and row.get('status_group') == 'Current']
    if any(item[2] == target['ref_id'] for item in refs):
        if '-S-' in atom_id and len(chosen) == 1 and not predecessors:
            return _publish_first_pinned_spec(selection, chosen[0], structure_snapshot)
        raise common.InputError('target', 'A migration-pinned Draft cannot be promoted.')
    if len(chosen) != 1 or len(predecessors) > 1:
        raise common.SourceChanged('Draft or Current predecessor is missing or ambiguous.')
    if not predecessors:
        if version != 1 or '-T-' not in atom_id:
            raise common.SourceChanged('Current predecessor is missing.')
        return _promote_new(selection, target, status, chosen[0], current_rows)
    draft, previous = chosen[0], predecessors[0]
    if native_header_view(previous['header_json'])['context'].get('template') == 'epic' and status != previous['status']:
        raise common.InputError('targetStatus', 'Publish the Epic at its Current Status. Use Change Status for transitions.')
    if previous.get('version') == version:
        return _cleanup_published_draft(selection, target, status, draft, previous, structure_snapshot, current_rows)
    if type(previous.get('version')) is not int or previous['version'] >= version:
        raise common.InputError('target', 'Draft Version must be newer than its Current predecessor.')
    root = _revision_root(selection, previous, structure_snapshot, current_rows)
    paths = []
    for row, marker, directory in ((draft, target['ref_id'], root / '000_draft'),
                                   (previous, atom_id, (selection.root / previous['source_path']).parent)):
        relative, digest = row.get('source_path'), row.get('_source_sha256')
        if (not isinstance(relative, str) or not isinstance(digest, str)
                or not re.fullmatch(r'[0-9a-f]{64}', digest)):
            raise common.SourceChanged('Carrier capture lacks a valid path or source digest.')
        relative = Path(relative)
        path = selection.root / relative
        if (relative.is_absolute() or '..' in relative.parts or path.parent != directory
                or not re.fullmatch(re.escape(marker) + r'-.+\.md', path.name)):
            raise common.InputError('target', 'Select carriers in their native revision directories.')
        paths.append(path)
    draft_path, previous_path = paths
    suffix = draft_path.name[len(target['ref_id']):]
    if previous_path.name != atom_id + suffix:
        raise common.InputError('target', 'Draft and Current filename must agree.')
    archive_path = root / '099_archived' / f"{atom_id}@{previous['version']}{suffix}"
    destination = (root / ('' if status == 'active' else status) / (atom_id + suffix)
                   if '-T-' in atom_id else previous_path)

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
                    raise common.SourceChanged('Draft or Current predecessor changed after selection.')
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
                    raise common.SourceChanged('Draft or Current predecessor changed after selection.')
            draft_bounds, previous_bounds = frontmatter_bounds(raw_draft), frontmatter_bounds(raw_previous)
            draft_body, previous_body = raw_draft[draft_bounds[2]:].decode(), raw_previous[previous_bounds[2]:].decode()
            draft_header, previous_header = draft['header_json'], previous['header_json']
            if '-T-' in atom_id:
                owner = _check_owner(selection, native_header_view(previous_header)['context'].get('container'), current_rows, capture)
            if '-T-' in atom_id and 'atom_family' in previous_header:
                if (draft_path != _task_path(selection, draft_header, draft_body, 'draft', version, owner, root)
                        or previous_path != _task_path(selection, previous_header, previous_body, previous['status'], previous['version'], owner, root)):
                    raise common.InputError('target', 'Task paths disagree with their authored Headers and Summaries.')
                archive_path = _task_path(selection, previous_header, previous_body, 'archived', previous['version'], owner, root)
                destination = _task_path(selection, draft_header, draft_body, status, version, owner, root)
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
