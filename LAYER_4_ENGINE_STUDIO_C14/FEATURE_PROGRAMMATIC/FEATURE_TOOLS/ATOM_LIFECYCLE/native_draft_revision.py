"""Preflight and commit a promotion over a Current revision."""
from hashlib import sha256
from pathlib import Path
import re

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import native_header_view
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (native_carrier_path, DRAFT_DIRECTORY,
    ARCHIVE_DIRECTORY, READY_DIRECTORY)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import revalidate_native
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import frontmatter_bounds
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import parse_carrier
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import CEILINGS, ReadContext

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.continuant_concern__pub import CONTINUANT_LENS

from . import common, effects
from .effects import _project_write_lock
from .native_draft_guards import _check_owner, _summary, is_c9_typed_manifest, _validate_c9_typed_manifest, _has_formal_declaration
from .native_draft_source import _revision_header, _revision_root, _state_bytes, _task_path
from .source import bind_query_reader
from .native_replacement_promotion import _plan_replacements, _archive_replacements, _check_replacement_activation


def _promote_revision(selection, target, status, draft, previous, current_rows,
                      structure_snapshot, previous_capture, validate_project_spec_model):
    atom_id, version = target['ref_id'].split('@')[0], target['version']
    root = _revision_root(selection, previous, structure_snapshot, current_rows)
    paths = []
    for row, marker, directory in ((draft, target['ref_id'], (selection.root / draft['source_path']).parent),
                                   (previous, atom_id, (selection.root / previous['source_path']).parent)):
        relative, digest = row.get('source_path'), row.get('_source_sha256')
        if (not isinstance(relative, str) or not isinstance(digest, str)
                or not re.fullmatch(r'[0-9a-f]{64}', digest)):
            raise common.SourceChanged('Carrier capture lacks a valid path or source digest.')
        relative = Path(relative)
        path = selection.root / relative
        if (relative.is_absolute() or '..' in relative.parts or path.parent != directory
                or (row is draft and path.parent not in {root / DRAFT_DIRECTORY, root / '000_draft'})
                or not re.fullmatch(re.escape(marker) + r'-.+\.md', path.name)):
            raise common.InputError('target', 'Select carriers in their native revision directories.')
        paths.append(path)
    draft_path, previous_path = paths
    suffix = draft_path.name[len(target['ref_id']):]
    typed = is_c9_typed_manifest(draft['header_json'])
    if not typed and previous_path.name != atom_id + suffix:
        raise common.InputError('target', 'Draft and Current filename must agree.')
    previous_suffix = previous_path.name[len(atom_id):]
    archive_path = root / ARCHIVE_DIRECTORY / f"{atom_id}@{previous['version']}{previous_suffix if typed else suffix}"
    destination = (root / ('' if status in {'active', 'in_queue'} else status) / (atom_id + suffix)
                   if '-T-' in atom_id else root / READY_DIRECTORY / (atom_id + suffix) if '-S-' in atom_id else previous_path)

    with _project_write_lock(selection.root):
        archive_path, destination, archive, promoted, capture = _preflight_revision(
            selection, status, draft, previous, current_rows, previous_capture,
            validate_project_spec_model, root, paths, archive_path, destination, atom_id, version)
        plans = _plan_replacements(selection, draft, current_rows, structure_snapshot, capture, previous=previous)
        if status == 'active':
            _check_replacement_activation([draft], capture.atoms, {row['id'] for row, *_ in plans})
        archived = _archive_replacements(selection, plans, draft)
        if archived['outcome'] != 'completed':
            return archived
        result = _commit_revision(selection, status, draft, previous, paths, archive_path,
                                  destination, archive, promoted, atom_id, version)
        result['effects'] = archived['effects'] + result['effects']
        return result


def _preflight_revision(selection, status, draft, previous, current_rows,
                        previous_capture, validate_project_spec_model, root, paths,
                        archive_path, destination, atom_id, version):
    from .native_draft import _validate_project_template
    draft_path, previous_path = paths
    try:
        capture, raw_draft, raw_previous, draft_bounds, previous_bounds, draft_body, previous_body = (
            _read_revision_sources(selection, draft, previous, previous_capture, paths, atom_id, version))
        draft_header, previous_header = draft['header_json'], previous['header_json']
        typed = is_c9_typed_manifest(draft_header)
        if typed:
            _validate_c9_typed_manifest(draft_header, draft_body)
            parameters = getattr(selection, 'parameters', None)
            if draft_path != native_carrier_path(draft_header, _summary(draft_body), project_root=selection.control_root, owner_directory=root, parameters=parameters):
                raise common.InputError('target', 'Draft path disagrees with its Header and Summary.')
        if '-T-' in atom_id:
            owner = _check_owner(selection, native_header_view(previous_header)['context'].get('container'), current_rows, capture)
        if '-T-' in atom_id and 'atom_family' in previous_header:
            if (draft_path != _task_path(selection, draft_header, draft_body, 'draft', version, owner, root)
                    or previous_path != _task_path(selection, previous_header, previous_body, previous['status'], previous['version'], owner, root)):
                raise common.InputError('target', 'Task paths disagree with their authored Headers and Summaries.')
            archive_path = _task_path(selection, previous_header, previous_body, 'archived', previous['version'], owner, root)
            destination = _task_path(selection, draft_header, draft_body, status, version, owner, root)
        _check_revision_headers(draft_header, previous_header, draft_body, previous_body, typed)
        _check_promotion_destinations(archive_path, destination, previous_path, capture, previous['id'])
        archive = _state_bytes(raw_previous, previous_bounds, previous_path, previous['version'], previous_body, 'archived')
        promoted = _state_bytes(raw_draft, draft_bounds, draft_path, version, draft_body, status)
        if '-S-' in atom_id:
            _validate_project_template(parse_carrier(promoted, destination).metadata, validate_project_spec_model, draft_body)
    except (common.InputError, common.SourceChanged):
        raise
    except (OSError, RuntimeError, TypeError, ValueError) as error:
        raise common.SourceChanged('Native sources are unavailable or changed.') from error

    return archive_path, destination, archive, promoted, capture




def _check_revision_headers(draft_header, previous_header, draft_body, previous_body, typed):
    draft_revision, previous_revision = _revision_header(draft_header), _revision_header(previous_header)
    if (typed and previous_header.get('atom_family') == 'SPEC'
            and (previous_revision.get('context', {}).get('template') == draft_revision['context']['template']
                 or (previous_revision.get('context', {}).get('template') is None and _has_formal_declaration(previous_body)))):
        draft_revision = {**draft_revision, 'context': {k: v for k, v in draft_revision['context'].items() if k != 'template'}}
        previous_revision = {**previous_revision, 'context': {k: v for k, v in previous_revision['context'].items() if k != 'template'}}
        if (draft_revision['context'].get('lens') == CONTINUANT_LENS
                and previous_revision['context'].get('lens') in {'SPEC', 'DES'}):
            draft_revision['context'].pop('lens')
            previous_revision['context'].pop('lens')
            draft_revision.pop('concern', None)
            previous_revision.pop('concern', None)
    if any('IS_REPLACEMENT_FOR' in header.get('relations', {}) for header in (draft_header, previous_header)):
        for revision in (draft_revision, previous_revision):
            if isinstance(revision.get('relations'), dict):
                revision['relations'] = {k: v for k, v in revision['relations'].items() if k != 'IS_REPLACEMENT_FOR'}
                if not revision['relations']:
                    revision.pop('relations')
    draft_relations = draft_revision.pop('relations', {})
    previous_relations = previous_revision.pop('relations', {})
    if (not isinstance(draft_relations, dict) or not isinstance(previous_relations, dict)
            or any(not isinstance(values, list) or not isinstance(previous_relations.get(key), list)
                   or any(values.count(value) > previous_relations[key].count(value) for value in values)
                   for key, values in draft_relations.items())):
        raise common.InputError('target', 'A Draft may only remove existing authored relations.')
    if (draft_revision != previous_revision
            or _summary(draft_body) != _summary(previous_body)):
        raise common.InputError('target', 'Only a body revision with unchanged Summary is supported.')


def _check_promotion_destinations(archive_path, destination, previous_path, capture, atom_id):
    if archive_path.exists() or archive_path.is_symlink() or (destination != previous_path and
            (destination.exists() or destination.is_symlink())):
        raise common.InputError('target', 'A promotion destination already exists.')
    if destination != previous_path and (previous_path.with_suffix('').exists() or
            previous_path.with_suffix('').is_symlink() or any(
                row.get('status_group') == 'Current' and
                native_header_view(row['header_json']).get('context', {}).get('container', {}).get('atom') == atom_id
                for row in capture.atoms)):
        raise common.InputError('target', 'A container cannot change status during promotion.')
    for parent in (archive_path.parent, destination.parent):
        if parent.is_symlink() or (parent.exists() and not parent.is_dir()):
            raise common.InputError('target', 'A promotion destination directory is unsafe.')

def _read_revision_sources(selection, draft, previous, previous_capture, paths, atom_id, version):
    capture = revalidate_native(selection, previous_capture)
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
    reader = ReadContext(roots=[str(selection.root)], limits=dict(CEILINGS))
    raw_draft, raw_previous = (reader.read(path) for path in paths)
    for row, path, raw in zip((draft, previous), paths, (raw_draft, raw_previous), strict=False):
        bounds = frontmatter_bounds(raw)
        if (bounds is None or sha256(raw).hexdigest() != row['_source_sha256']
                or raw[bounds[2]:] != row.get('_content_bytes')
                or parse_carrier(raw, path).metadata != row.get('header_json')):
            raise common.SourceChanged('Draft or Current predecessor changed after selection.')
    draft_bounds, previous_bounds = frontmatter_bounds(raw_draft), frontmatter_bounds(raw_previous)
    draft_body, previous_body = raw_draft[draft_bounds[2]:].decode(), raw_previous[previous_bounds[2]:].decode()
    return capture, raw_draft, raw_previous, draft_bounds, previous_bounds, draft_body, previous_body


def _rollback_promotion(selection, previous_path, previous_digest, created, recorded, errors):
    errors = list(errors)
    for path, raw in reversed(created):
        try:
            reader = ReadContext(roots=[str(selection.root)], limits=dict(CEILINGS))
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


def _commit_revision(selection, status, draft, previous, paths, archive_path, destination,
                     archive, promoted, atom_id, version):
    draft_path, previous_path = paths
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
            reader = ReadContext(roots=[str(selection.root)], limits=dict(CEILINGS))
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
