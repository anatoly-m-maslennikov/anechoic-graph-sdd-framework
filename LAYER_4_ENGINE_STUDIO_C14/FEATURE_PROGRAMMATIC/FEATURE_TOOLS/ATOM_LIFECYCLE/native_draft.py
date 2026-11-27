"""Create and promote bounded same-ID native Draft revisions."""
from __future__ import annotations

from contextlib import ExitStack, contextmanager
from hashlib import sha256
import re

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import DRAFT_DIRECTORY, native_header_view

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import revalidate_native
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import frontmatter_bounds
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import parse_carrier
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import CEILINGS, ReadContext

from . import common
from .native_draft_guards import _check_owner, _reject_component_contract, _summary
from .native_draft_source import _revision_root, _state_bytes, _task_path
from .native_draft_task import _create_task
from .native_draft_promotion import promote_draft as promote_draft
from .effects import _project_write_lock
from .native_project_spec import PROJECT_SPEC_TIERS, create_project_spec, project_spec_template, validate_project_spec
from .source import bind_query_reader


@contextmanager
def _first_spec_write_lock(root):
    with ExitStack() as stack:
        try:
            stack.enter_context(_project_write_lock(root))
        except BlockingIOError as error:
            raise common.SourceChanged('A native Atom write is in progress.') from error
        yield


def _validate_project_template(header, validate, body=None):
    template = native_header_view(header)['context'].get('template')
    _reject_component_contract(template, 'target')
    if isinstance(template, str) and (template in PROJECT_SPEC_TIERS or
            (validate is not None and project_spec_template(template, validate) is not None)):
        if validate is None:
            raise common.InputError('target', 'The compiled Model does not admit this Project SPEC Template.')
        validate_project_spec(header, validate, body)


def create_draft(selection, params, *, current_rows, structure_snapshot=None, ticket_labels=(),
                 validate_project_spec_model=None, previous_capture=None, indexed_task=None):
    if indexed_task is not None and (not isinstance(params, dict) or set(params) != {'newAtom'}
            or not isinstance(params['newAtom'], dict) or params['newAtom'].get('template') not in ('task', 'epic')
            or not isinstance(params['newAtom'].get('container'), dict)
            or set(params['newAtom']['container']) != {'component'}):
        raise common.InputError('newAtom', 'Indexed creation requires a Component Task or Epic.')
    if isinstance(params, dict) and 'newAtom' in params:
        if set(params) != {'newAtom'}:
            raise common.InputError('newAtom', 'Supply only new Task or Epic properties.')
        values = params['newAtom']
        template = values.get('template') if isinstance(values, dict) else None
        _reject_component_contract(template, 'newAtom')
        if isinstance(template, str) and template not in ('task', 'epic') and (
                template in PROJECT_SPEC_TIERS or isinstance(values, dict) and 'lens' in values):
            if validate_project_spec_model is None:
                raise common.InputError('newAtom', 'The compiled Model does not admit this Project SPEC Template.')
            return create_project_spec(selection, values, validate_project_spec_model, previous_capture)
        return _create_task(selection, params['newAtom'], current_rows, structure_snapshot, ticket_labels, previous_capture, indexed_task)
    return _create_revision(selection, params, current_rows, structure_snapshot, previous_capture)


def _create_revision(selection, params, current_rows, structure_snapshot, previous_capture):
    target, changes, selected, digest, relative = _revision_input(selection, params, current_rows)
    _reject_component_contract(native_header_view(selected['header_json'])['context'].get('template'), 'sourceCurrent')
    path = selection.root / relative
    root = _revision_root(selection, selected, structure_snapshot, current_rows)
    with _project_write_lock(selection.root):
        try:
            capture = revalidate_native(selection, previous_capture)
            fresh = [row for row in capture.atoms if row.get('id') == target['ref_id'] and row.get('status_group') == 'Current']
            if capture.errors or len(fresh) != 1 or any(fresh[0].get(key) != selected.get(key) for key in (
                    'source_path', 'id', 'ref', '_exact_ref', 'version', 'status', 'status_group',
                    'header_json', '_content_bytes', '_source_sha256')):
                raise common.SourceChanged('Current carrier source changed after selection.')
            raw = ReadContext(roots=[str(selection.root)], limits=dict(CEILINGS)).read(path)
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
        return _write_revision(selection, target, selected, path, root, raw, bounds, body, old_body,
                               capture, previous_capture, digest, owner if '-T-' in target['ref_id'] else None)


def _write_revision(selection, target, selected, path, root, raw, bounds, body, old_body,
                    capture, previous_capture, digest, owner):
    version = max(getattr(capture, 'max_archived_version', 0),
                  max(row['version'] for row in capture.atoms if row.get('id') == target['ref_id'])) + 1
    if '-T-' in target['ref_id'] and 'atom_family' in selected['header_json']:
        if _task_path(selection, selected['header_json'], old_body, selected['status'], target['version'], owner, root) != path:
            raise common.InputError('sourceCurrent', 'Task path disagrees with its authored Header and Summary.')
    while version <= 2**63 - 1:
        if '-T-' in target['ref_id'] and 'atom_family' in selected['header_json']:
            destination = _task_path(selection, selected['header_json'], body, 'draft', version, owner, root)
        else:
            destination = root / DRAFT_DIRECTORY / path.name.replace(target['ref_id'] + '-', f"{target['ref_id']}@{version}-draft-", 1)
        candidate = _state_bytes(raw, bounds, path, version, body, 'draft', update_timestamp=True)
        with bind_query_reader(None):
            outcome = common.write_destination(selection.root, destination, candidate)
        if not common.destination_collision({"effects": outcome.effects, "errors": outcome.errors}):
            break
        try:
            fresh_raw = ReadContext(roots=[str(selection.root)], limits=dict(CEILINGS)).read(path)
            if sha256(fresh_raw).hexdigest() != digest:
                raise common.SourceChanged('Current carrier source changed after selection.')
            refreshed = revalidate_native(selection, previous_capture)
            if refreshed.errors:
                raise common.SourceChanged('Native carrier capture is incomplete.')
            reader = ReadContext(roots=[str(selection.root)], limits=dict(CEILINGS))
            if sha256(reader.read(selection.manifest_path)).hexdigest() != selection.manifest_sha256 or reader.currentness()['state'] != 'unchanged':
                raise common.SourceChanged('Project Manifest changed after selection.')
        except (OSError, RuntimeError, ValueError) as error:
            raise common.SourceChanged('Current carrier source changed after selection.') from error
        version += 1
    else:
        raise common.SourceChanged('No representable revision Version remains.')
    data = {} if outcome.errors else {'savedDraft': common.saved(selection, destination, target['ref_id'],
                    f"{target['ref_id']}@{version}-draft", version, 'Draft')}
    if data:
        timestamp = parse_carrier(candidate, destination).metadata.get('state', {}).get('updated_at')
        if timestamp is not None:
            data['savedDraft']['updated_at'] = str(timestamp)
    return common.result(effects=outcome.effects, errors=outcome.errors, **data)




def _revision_input(selection, params, current_rows):
    if not isinstance(params, dict) or set(params) - {'sourceCurrent', 'changes'} or 'sourceCurrent' not in params:
        raise common.InputError('sourceCurrent', 'Supply one Current carrier and optional body change.')
    target = params['sourceCurrent']
    if (not isinstance(target, dict) or set(target) != {'ref_id', 'version'}
            or not isinstance(target['ref_id'], str)
            or not re.fullmatch(re.escape(selection.project_prefix) + r'-[STPC]-[0-9]+', target['ref_id'])
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
    return target, changes, selected, digest, relative
