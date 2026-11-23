"""Create and promote bounded same-ID native Draft revisions."""
from __future__ import annotations

from contextlib import ExitStack, contextmanager
from datetime import datetime, timezone
from hashlib import sha256
import re

import yaml

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import canonical_native_header, native_header_view
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (native_carrier_path, spec_lens_directories,
                                      DRAFT_DIRECTORY)

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import revalidate_native
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import frontmatter_bounds
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import parse_carrier
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import CEILINGS, ReadContext

from . import common
from .native_draft_guards import _check_owner, _summary, _validate_contract
from .native_draft_source import _revision_root, _state_bytes, _task_path
from .native_draft_task import _create_task
from .native_draft_promotion import promote_draft as promote_draft
from .effects import _project_write_lock
from .native_project_spec import PROJECT_SPEC_TIERS, create_project_spec, validate_project_spec
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
    if isinstance(template, str) and template in PROJECT_SPEC_TIERS:
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
        if isinstance(template, str) and template in PROJECT_SPEC_TIERS:
            if validate_project_spec_model is None:
                raise common.InputError('newAtom', 'The compiled Model does not admit this Project SPEC Template.')
            return create_project_spec(selection, values, validate_project_spec_model, previous_capture)
        if template == 'component_contract':
            return _create_component_contract(selection, params['newAtom'], structure_snapshot, previous_capture)
        return _create_task(selection, params['newAtom'], current_rows, structure_snapshot, ticket_labels, previous_capture, indexed_task)
    return _create_revision(selection, params, current_rows, structure_snapshot, previous_capture)


def _create_revision(selection, params, current_rows, structure_snapshot, previous_capture):
    target, changes, selected, digest, relative = _revision_input(selection, params, current_rows)
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
        version = max(row['version'] for row in capture.atoms if row.get('id') == target['ref_id']) + 1
        if '-T-' in target['ref_id'] and 'atom_family' in selected['header_json']:
            if _task_path(selection, selected['header_json'], old_body, selected['status'], target['version'], owner, root) != path:
                raise common.InputError('sourceCurrent', 'Task path disagrees with its authored Header and Summary.')
            destination = _task_path(selection, selected['header_json'], body, 'draft', version, owner, root)
        else:
            destination = root / DRAFT_DIRECTORY / path.name.replace(target['ref_id'] + '-', f"{target['ref_id']}@{version}-draft-", 1)
        candidate = _state_bytes(raw, bounds, path, version, body, 'draft')
        with bind_query_reader(None):
            outcome = common.write_destination(selection.root, destination, candidate)
        data = {} if outcome.errors else {'savedDraft': common.saved(selection, destination, target['ref_id'],
                        f"{target['ref_id']}@{version}-draft", version, 'Draft')}
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


def _create_component_contract(selection, values, structure_snapshot, previous_capture):
    if (set(values) != {'template', 'container', 'lens', 'body'} or not isinstance(values['body'], str)
            or not isinstance(values['lens'], str) or not values['lens'].strip()
            or not isinstance(values['container'], dict) or set(values['container']) != {'component'}
            or not isinstance(values['container']['component'], str)
            or not re.fullmatch(r'C[0-9]+', values['container']['component'])):
        raise common.InputError('newAtom', 'Supply a Component Contract template, Component, Lens, and Markdown body.')
    try:
        spec_lens_directories(values['lens'])
    except ValueError as error:
        raise common.InputError('lens', 'Supply a valid Lens.') from error
    if (not selection.root.is_absolute() or not selection.control_root.is_relative_to(selection.root)
            or selection.manifest_path.parent not in {selection.root, selection.control_root}):
        raise common.SourceChanged('Selected Project path is invalid.')
    with _first_spec_write_lock(selection.root):
        try:
            capture = revalidate_native(selection, previous_capture)
        except (OSError, RuntimeError, ValueError) as error:
            raise common.SourceChanged('Native carriers changed during Contract selection.') from error
        if capture.errors:
            raise common.SourceChanged('Native carrier capture is incomplete.')
        atom_id = f'{selection.project_prefix}-S-{common.next_native_number(selection, capture, "S")}'
        header = canonical_native_header({'identity': {'atom_id': atom_id},
            'context': {'container': values['container'], 'tier': 0, 'template': 'component_contract', 'lens': values['lens']},
            'state': {'status': 'draft', 'version': 1, 'updated_at': datetime.now(timezone.utc).isoformat()}})
        body = values['body']
        owner = _validate_contract(selection, header, body, selection.control_root, structure_snapshot, capture)
        try:
            path = native_carrier_path(header, _summary(body), project_root=selection.control_root, owner_directory=owner)
            raw = b'---\n' + yaml.safe_dump(header, sort_keys=False).encode() + b'---\n' + body.encode('utf-8')
        except (ValueError, UnicodeError) as error:
            raise common.InputError('summary', 'Summary cannot be used in a Contract filename.') from error
        with bind_query_reader(None):
            outcome = common.write_destination(selection.root, path, raw)
        data = {} if outcome.errors else {'savedDraft': common.saved(selection, path, atom_id, f'{atom_id}@1-draft', 1, 'Draft')}
        return common.result(effects=outcome.effects, errors=outcome.errors, **data)
