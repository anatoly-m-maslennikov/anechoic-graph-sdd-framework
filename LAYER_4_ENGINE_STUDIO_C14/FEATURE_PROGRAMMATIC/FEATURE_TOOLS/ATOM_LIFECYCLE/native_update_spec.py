"""SPEC status and Draft archive operations."""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import re


from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import native_header_view
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import DRAFT_DIRECTORY

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import revalidate_native
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import frontmatter_bounds
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import parse_carrier
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import CEILINGS, ReadContext

from . import effects
from .effects import _project_write_lock
from .common import InputError, SourceChanged, result, saved
from .source import bind_query_reader




def change_spec_status(selection, params, *, current_rows, structure_snapshot=None, validate_project_spec_model=None, previous_capture=None):
    """Start implementation of a Ready SPEC or retire an Active SPEC."""
    from .native_draft import _revision_root

    if not isinstance(params, dict) or set(params) != {'target', 'targetStatus'}:
        raise InputError('target', 'Supply one Current SPEC target and Status.')
    target, status = params['target'], params['targetStatus']
    if (not isinstance(target, dict) or set(target) != {'ref_id', 'version'}
            or not isinstance(target['ref_id'], str)
            or not re.fullmatch(re.escape(selection.project_prefix) + r'-S-[0-9]+', target['ref_id'])
            or type(target['version']) is not int or target['version'] < 1
            or status not in {'active', 'archived'}):
        raise InputError('target', 'Supply a SPEC reference, Version and applicable Status.')
    matches = [row for row in current_rows if row.get('ref') == target['ref_id']
               and row.get('status_group') == 'Current' and row.get('version') == target['version']]
    if len(matches) != 1:
        raise SourceChanged('Current SPEC selection is missing, ambiguous, or stale.')
    selected = matches[0]
    if (selected.get('status'), status) not in {('ready', 'active'), ('active', 'archived')}:
        raise InputError('targetStatus', 'Only Ready to Active and Active to Archived are supported.')
    root = _revision_root(selection, selected, structure_snapshot, current_rows)
    path = selection.root / selected['source_path']
    digest = selected.get('_source_sha256')
    if not isinstance(digest, str) or not re.fullmatch(r'[0-9a-f]{64}', digest):
        raise SourceChanged('Current SPEC capture lacks a source digest.')
    return _change_spec_selected(selection, target, selected, path, digest, root, status,
                                 validate_project_spec_model, previous_capture)


def _selected_spec_bytes(selection, selected, path, digest):
    reader = ReadContext(roots=[str(selection.root)], limits=dict(CEILINGS))
    raw = reader.read(path)
    bounds = frontmatter_bounds(raw)
    if (bounds is None or sha256(raw).hexdigest() != digest or raw[bounds[2]:] != selected['_content_bytes']
            or parse_carrier(raw, path).metadata != selected['header_json']
            or sha256(reader.read(selection.manifest_path)).hexdigest() != selection.manifest_sha256
            or reader.currentness()['state'] != 'unchanged'):
        raise SourceChanged('Current SPEC source changed after selection.')
    return raw, bounds


def _change_spec_selected(selection, target, selected, path, digest, root, status, validate_project_spec_model, previous_capture):
    from .native_update import _move_ticket
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import native_carrier_path
    from .native_draft import _summary, _validate_project_template

    with _project_write_lock(selection.root):
        try:
            capture = revalidate_native(selection, previous_capture)
        except (OSError, RuntimeError, ValueError) as error:
            raise SourceChanged('Native carrier capture changed.') from error
        fresh = [row for row in capture.atoms if row.get('_exact_ref') == selected.get('_exact_ref')]
        if capture.errors or len(fresh) != 1 or any(fresh[0].get(k) != selected.get(k) for k in (
                'source_path', 'id', 'ref', '_exact_ref', 'version', 'status', 'status_group',
                'header_json', '_content_bytes', '_source_sha256')):
            raise SourceChanged('Current SPEC changed after selection.')
        if path.with_suffix('').exists() or path.with_suffix('').is_symlink() or any(
                native_header_view(row['header_json']).get('context', {}).get('container', {}).get('atom') == selected['id']
                for row in capture.atoms):
            raise InputError('target', 'SPEC containers cannot change Status.')
        try:
            raw, bounds = _selected_spec_bytes(selection, selected, path, digest)
            header = selected['header_json']
            body = raw[bounds[2]:].decode('utf-8')
            if status == 'active':
                _validate_project_template(header, validate_project_spec_model, body)
            parameters = getattr(selection, 'parameters', None)
            expected = native_carrier_path(header, _summary(body), project_root=selection.control_root,
                                           owner_directory=root, parameters=parameters)
            if path != expected and not (
                    expected.parent == selection.root and path == selection.control_root / expected.name):
                raise InputError('target', 'SPEC path disagrees with its Header and Summary.')
            projected = {**header, 'state': {**header['state'], 'status': status}}
            destination = native_carrier_path(projected, _summary(body), project_root=selection.control_root,
                                              owner_directory=root, parameters=parameters)
        except (InputError, SourceChanged):
            raise
        except (OSError, RuntimeError, ValueError, KeyError, TypeError) as error:
            raise SourceChanged('Current SPEC source is unavailable or changed.') from error
        return _move_ticket(selection, target, selected, digest, path, destination, status, lambda: None,
                            locked=True, preflight=(raw, bounds, None))

def archive_spec_draft(selection, params, *, current_rows, structure_snapshot=None, previous_capture=None):
    """Archive an exact SPEC Draft without replacing an existing revision."""
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import READY_DIRECTORY
    from .native_draft import _revision_root

    if not isinstance(params, dict) or set(params) != {'target'}:
        raise InputError('target', 'Supply one exact SPEC Draft target.')
    target = params['target']
    if (not isinstance(target, dict) or set(target) != {'ref_id', 'version'}
            or not isinstance(target['ref_id'], str) or type(target['version']) is not int
            or target['version'] < 1):
        raise InputError('target', 'Supply an exact SPEC Draft reference and Version.')
    match = re.fullmatch(re.escape(selection.project_prefix) + r'-S-[0-9]+@([1-9][0-9]*)-draft', target['ref_id'])
    if match is None or int(match[1]) != target['version']:
        raise InputError('target', 'Supply an exact SPEC Draft reference and matching Version.')
    rows = [row for row in current_rows if row.get('_exact_ref') == target['ref_id'] and row.get('status_group') == 'Draft']
    if len(rows) != 1:
        raise SourceChanged('SPEC Draft selection is missing or ambiguous.')
    draft = rows[0]
    relative, digest = draft.get('source_path'), draft.get('_source_sha256')
    if not isinstance(relative, str) or not isinstance(digest, str) or not re.fullmatch(r'[0-9a-f]{64}', digest):
        raise SourceChanged('SPEC Draft capture lacks a path or digest.')
    relative = Path(relative)
    path = selection.root / relative
    if (relative.is_absolute() or '..' in relative.parts or not path.is_relative_to(selection.control_root)
            or path.parent.name != DRAFT_DIRECTORY):
        raise InputError('target', 'Select a SPEC in its native Draft directory.')
    owner = path.parent.parent
    proposed = {**draft, 'status': 'ready', 'source_path': (owner / READY_DIRECTORY / (draft['id'] + path.name[len(target['ref_id']):])).relative_to(selection.root).as_posix()}
    if _revision_root(selection, proposed, structure_snapshot, current_rows) != owner:
        raise InputError('target', 'SPEC Draft owner is invalid.')
    return _archive_spec_selected(selection, target, draft, path, digest, owner, previous_capture)


def _archive_spec_selected(selection, target, draft, path, digest, owner, previous_capture):
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import native_carrier_path
    from .native_draft import _state_bytes, _summary

    with _project_write_lock(selection.root):
        try:
            capture = revalidate_native(selection, previous_capture)
        except (OSError, RuntimeError, ValueError) as error:
            raise SourceChanged('Native carrier capture changed.') from error
        fresh = [row for row in capture.atoms if row.get('_exact_ref') == target['ref_id']]
        if capture.errors or len(fresh) != 1 or any(fresh[0].get(k) != draft.get(k) for k in (
                'source_path', 'id', 'ref', '_exact_ref', 'version', 'status', 'status_group',
                'header_json', '_content_bytes', '_source_sha256')):
            raise SourceChanged('SPEC Draft changed after selection.')
        reader = ReadContext(roots=[str(selection.root)], limits=dict(CEILINGS))
        try:
            raw = reader.read(path)
            bounds = frontmatter_bounds(raw)
            if (bounds is None or sha256(raw).hexdigest() != digest or raw[bounds[2]:] != draft['_content_bytes']
                    or parse_carrier(raw, path).metadata != draft['header_json']
                    or sha256(reader.read(selection.manifest_path)).hexdigest() != selection.manifest_sha256
                    or reader.currentness()['state'] != 'unchanged'):
                raise SourceChanged('SPEC Draft changed after selection.')
            body = raw[bounds[2]:].decode('utf-8')
            header = draft['header_json']
            if path != native_carrier_path(header, _summary(body), project_root=selection.control_root, owner_directory=owner):
                raise InputError('target', 'SPEC Draft path disagrees with its Header and Summary.')
            used = {row['version'] for row in capture.atoms if row['id'] == draft['id'] and row is not fresh[0]}
            version = max(target['version'], getattr(capture, 'max_archived_version', 0) + 1)
        except (OSError, RuntimeError, ValueError, KeyError, TypeError) as error:
            raise SourceChanged('SPEC Draft source is unavailable or changed.') from error
        return _allocate_archived_spec(selection, target, draft, path, digest, owner, previous_capture,
                                       raw, bounds, body, header, used, version)


def _allocate_archived_spec(selection, target, draft, path, digest, owner, previous_capture,
                            raw, bounds, body, header, used, version):
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import native_carrier_path
    from .native_draft import _state_bytes, _summary
    from . import common
    while version <= 2**63 - 1:
        if version in used:
            version += 1
            continue
        projected = {**header, 'state': {**header['state'], 'status': 'archived', 'version': version}}
        destination = native_carrier_path(projected, _summary(body), project_root=selection.control_root, owner_directory=owner)
        archived = _state_bytes(raw, bounds, path, version, body, 'archived',
                                update_timestamp=version != target['version'])
        outcome = _write_archived_spec(selection, target, draft, path, digest, destination, archived, version)
        if not common.destination_collision(outcome):
            return outcome
        try:
            _selected_spec_bytes(selection, draft, path, digest)
            refreshed = revalidate_native(selection, previous_capture)
            if refreshed.errors:
                raise SourceChanged('Native carrier capture is incomplete.')
        except (OSError, RuntimeError, ValueError) as error:
            raise SourceChanged('SPEC Draft changed after selection.') from error
        version += 1
    raise SourceChanged('No representable revision Version remains.')




def _write_archived_spec(selection, target, draft, path, digest, destination, archived, version):
    from . import common

    with bind_query_reader(None):
        written = common.write_destination(selection.root, destination, archived)
        recorded = list(written.effects)
        if written.errors:
            return result(effects=recorded, errors=written.errors)
        removed = effects.remove(selection.root, path, digest)
        recorded.extend(removed.effects)
        if removed.errors:
            errors = list(removed.errors)
            if not removed.effects and not any(error.get('code') == 'effect_uncertain' for error in errors):
                try:
                    if sha256(ReadContext(roots=[str(selection.root)], limits=dict(CEILINGS)).read(path)).hexdigest() == digest:
                        rollback = effects.remove(selection.root, destination, sha256(archived).hexdigest())
                        recorded.extend(rollback.effects)
                        errors.extend(rollback.errors)
                except (OSError, RuntimeError, ValueError):
                    pass
            return result(effects=recorded, errors=errors)
    artifact = saved(selection, destination, draft['id'], f"{draft['id']}@{version}", version, 'archived')
    return result(effects=recorded, artifact=artifact, sourceRef=target['ref_id'])
