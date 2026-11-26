"""Plan and archive explicit replacement targets under the promotion lock."""
from hashlib import sha256
import re

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    ARCHIVE_DIRECTORY, CUSTOM_MODEL_DIRECTORY, PROJECT_CONFIG_DIRECTORY, CEILINGS, ReadContext,
    frontmatter_bounds, native_carrier_path, native_header_view, parse_carrier,
)
from . import common, effects
from .native_draft_guards import _check_owner, _summary
from .native_draft_source import _revision_root, _state_bytes, _task_path
from .source import bind_query_reader


def _replacement_targets(row):
    relations = row['header_json'].get('relations', {})
    return relations.get('IS_REPLACEMENT_FOR', ()) if isinstance(relations, dict) else ()


def _check_replacement_activation(activating, rows, archived=()):
    activating_ids = {row['id'] for row in activating}
    active = [row for row in rows if row['status_group'] == 'Current' and row['status'] == 'active'
              and row['id'] not in activating_ids and row['id'] not in archived]
    active.extend(activating)
    active_ids = {row['id'] for row in active}
    for row in active:
        targets = _replacement_targets(row)
        if isinstance(targets, list):
            for target in targets:
                if (isinstance(target, str) and target != row['id'] and target in active_ids
                        and (row['id'] in activating_ids or target in activating_ids)):
                    raise common.InputError('targetStatus',
                                            f"Replacement-linked Atoms {row['id']} and {target} cannot both be Active.")


def _plan_replacements(selection, draft, current_rows, structure_snapshot, capture, previous=None):
    relations = draft['header_json'].get('relations', {})
    if not isinstance(relations, dict):
        raise common.InputError('target', 'Draft Relations are invalid.')
    targets = relations.get('IS_REPLACEMENT_FOR', [])
    if not isinstance(targets, list) or any(not isinstance(item, str) or not re.fullmatch(
            re.escape(selection.project_prefix) + r'-[STPC]-[0-9]+', item) for item in targets):
        raise common.InputError('target', 'Replacement targets must be base Atom IDs.')
    if draft['id'] in targets or len(targets) != len(set(targets)):
        raise common.InputError('target', 'Replacement targets must be unique and different from the Draft Atom ID.')
    adopted = () if previous is None else _replacement_targets(previous)
    if any(atom_id not in targets for atom_id in adopted):
        raise common.InputError('target', 'A successor revision must retain its adopted replacement links.')
    if not targets:
        return []
    if capture.errors or [row for row in capture.atoms if row.get('_exact_ref') == draft['_exact_ref']] != [draft]:
        raise common.SourceChanged('Draft or native capture changed.')
    draft_path = selection.root / draft['source_path']
    if draft_path.with_suffix('').exists() or draft_path.with_suffix('').is_symlink() or any(
            row.get('status_group') == 'Current' and native_header_view(row['header_json']).get('context', {}).get('container', {}).get('atom') == draft['id']
            for row in capture.atoms):
        raise common.InputError('target', 'A replacement Draft cannot be a container.')
    plans = []
    for atom_id in targets:
        plan = _plan_replacement(selection, draft, current_rows, structure_snapshot, capture, adopted, atom_id)
        if plan is not None:
            plans.append(plan)
    return plans


def _plan_replacement(selection, draft, current_rows, structure_snapshot, capture, adopted, atom_id):
    row = _replacement_row(atom_id, capture, current_rows, adopted)
    if row is None:
        return None
    path = selection.root / row['source_path']
    if path.with_suffix('').exists() or path.with_suffix('').is_symlink() or any(
            item.get('status_group') == 'Current' and native_header_view(item['header_json']).get('context', {}).get('container', {}).get('atom') == atom_id
            for item in capture.atoms):
        raise common.InputError('target', 'Replacement target is a container.')
    header = row['header_json']
    context = native_header_view(header)['context']
    custom = (header.get('atom_family') == 'PROJECT_CONFIG' and context.get('container') == {'component': 'C00'}
              and context.get('template') in {'model_manifest', 'manifest_node', 'manifest_property', 'manifest_relation'})
    root = selection.control_root / PROJECT_CONFIG_DIRECTORY / CUSTOM_MODEL_DIRECTORY if custom else _revision_root(selection, row, structure_snapshot, capture.atoms)
    reader = ReadContext(roots=[str(selection.root)], limits=dict(CEILINGS))
    try:
        raw = reader.read(path)
        bounds = frontmatter_bounds(raw)
        if (bounds is None or sha256(raw).hexdigest() != row.get('_source_sha256')
                or parse_carrier(raw, path).metadata != header or raw[bounds[2]:] != row.get('_content_bytes')
                or reader.currentness()['state'] != 'unchanged'):
            raise ValueError('Target changed')
        body = raw[bounds[2]:].decode('utf-8')
        if custom:
            projected = native_carrier_path(header, _summary(body), project_root=selection.control_root, owner_directory=None)
            if context.get('template') != 'model_manifest':
                config_root = selection.control_root / PROJECT_CONFIG_DIRECTORY
                projected = root / projected.relative_to(config_root)
            if path != projected:
                raise ValueError('Custom Model path disagrees')
        if '-T-' in atom_id and 'atom_family' in header:
            owner = _check_owner(selection, context.get('container'), capture.atoms, capture)
            archive_path = _task_path(selection, header, body, 'archived', row['version'], owner, root)
        else:
            archive_path = root / ARCHIVE_DIRECTORY / (f"{atom_id}@{row['version']}" + path.name[len(atom_id):])
        if archive_path.exists() or archive_path.is_symlink() or archive_path.parent.is_symlink() or (archive_path.parent.exists() and not archive_path.parent.is_dir()):
            raise common.InputError('target', 'A replacement archive destination already exists or is unsafe.')
        archived = _state_bytes(raw, bounds, path, row['version'], body, 'archived')
    except common.InputError:
        raise
    except (OSError, RuntimeError, TypeError, ValueError) as error:
        raise common.SourceChanged('Replacement target is unavailable or changed.') from error
    return (row, path, archive_path, archived)


def _replacement_row(atom_id, capture, current_rows, adopted):
    rows = [row for row in capture.atoms if row.get('id') == atom_id]
    selected = [row for row in current_rows if row.get('id') == atom_id and row.get('status_group') in {'Current', 'Archived'}]
    if [row for row in rows if row.get('status_group') in {'Current', 'Archived'}] != selected:
        raise common.SourceChanged('Replacement target changed after selection.')
    current = [row for row in rows if row.get('status_group') == 'Current']
    if len(current) > 1 or not current and not any(row.get('status_group') == 'Archived' for row in rows):
        raise common.SourceChanged('Replacement target is missing or ambiguous.')
    if not current and atom_id in adopted:
        return None
    if not current or current[0].get('status') not in {'ready', 'active'}:
        raise common.InputError('target', f'Replacement predecessor {atom_id} must be Current Ready or Active.')
    return current[0]


def _archive_replacements(selection, plans, draft):
    recorded = []
    with bind_query_reader(None):
        for row, path, archive_path, archived in plans:
            try:
                reader = ReadContext(roots=[str(selection.root)], limits=dict(CEILINGS))
                if (sha256(reader.read(selection.root / draft['source_path'])).hexdigest() != draft['_source_sha256']
                        or sha256(reader.read(selection.manifest_path)).hexdigest() != selection.manifest_sha256
                        or sha256(reader.read(path)).hexdigest() != row['_source_sha256']
                        or reader.currentness()['state'] != 'unchanged'):
                    raise ValueError('Source changed')
            except (OSError, RuntimeError, ValueError):
                return common.result(effects=recorded, errors=[{'code': 'source_changed', 'message': 'Draft, Manifest or replacement target changed.'}])
            written = common.write_destination(selection.root, archive_path, archived)
            recorded.extend(written.effects)
            if written.errors:
                return common.result(effects=recorded, errors=written.errors)
            removed = effects.remove(selection.root, path, row['_source_sha256'])
            recorded.extend(removed.effects)
            if removed.errors:
                return common.result(effects=recorded, errors=removed.errors)
    return common.result(effects=recorded)
