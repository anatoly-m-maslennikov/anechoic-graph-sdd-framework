"""Create and validate Project-owned Axiom and Applicable Principle Drafts."""
from datetime import datetime, timezone

import yaml

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import canonical_native_header, native_header_view
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import native_carrier_path, spec_lens_directories
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import revalidate_native

from . import common
from .source import bind_query_reader

PROJECT_SPEC_TIERS = {'project_contract': (0,), 'axiom': (0,), 'applicable_principle': (1, 2)}


def project_spec_template(template, validate):
    model = getattr(validate, '__self__', None)
    if model is not None and hasattr(model, 'project_spec_template'):
        return model.project_spec_template(template)
    tiers = PROJECT_SPEC_TIERS.get(template)
    return (template, tiers[-1], True) if tiers else None


def validate_project_spec(header, validate, body=None):
    view = native_header_view(header)
    context = view['context']
    template = context.get('template')
    container = context.get('container')
    tiers = PROJECT_SPEC_TIERS.get(template)
    model = getattr(validate, '__self__', None)
    if (container != {'component': 'C00'} or type(context.get('tier')) is not int
            or (model is None and (tiers is None or context['tier'] not in tiers))):
        raise common.InputError('newAtom', 'Project SPEC requires its declared Tier and Project C00 container.')
    try:
        validate(template, header, 'C00', body)
    except (ValueError, TypeError, KeyError) as error:
        raise common.InputError('newAtom', f'Project SPEC does not satisfy the compiled Model: {error}') from error


def _project_spec_preflight(values, validate):
    if (not isinstance(values, dict) or set(values) - {'tier'} != {'template', 'container', 'lens', 'body'}
            or not isinstance(values.get('template'), str) or values.get('container') != {'component': 'C00'}
            or not isinstance(values.get('body'), str) or not isinstance(values.get('lens'), str)):
        raise common.InputError('newAtom', 'Supply a Project SPEC template, Project C00, Lens, and Markdown body.')
    try:
        declaration = project_spec_template(values['template'], validate)
    except ValueError as error:
        raise common.InputError('newAtom', str(error)) from error
    if declaration is None or not declaration[2]:
        raise common.InputError('newAtom', 'The compiled Model does not enable this Project SPEC Template for creation.')
    tiers = PROJECT_SPEC_TIERS.get(values['template'], (declaration[1],))
    tier = values.get('tier', declaration[1])
    model = getattr(validate, '__self__', None)
    if type(tier) is not int or (model is None and tier not in tiers):
        raise common.InputError('tier', 'Tier must match the selected Project SPEC template.')
    if model is None and values['template'] == 'axiom' and values['lens'] != 'SPEC':
        raise common.InputError('lens', 'Axiom requires the SPEC Lens.')
    try:
        spec_lens_directories(values['lens'])
    except ValueError as error:
        raise common.InputError('lens', 'Supply a valid Lens.') from error
    return tier


def create_project_spec(selection, values, validate, previous_capture=None):
    from .native_draft import _first_spec_write_lock, _summary
    tier = _project_spec_preflight(values, validate)
    summary = _summary(values['body'])
    if (not selection.root.is_absolute() or not selection.control_root.is_relative_to(selection.root)
            or selection.manifest_path.parent not in {selection.root, selection.control_root}):
        raise common.SourceChanged('Selected Project path is invalid.')
    with _first_spec_write_lock(selection.root):
        try:
            capture = revalidate_native(selection, previous_capture)
        except (OSError, RuntimeError, ValueError) as error:
            raise common.SourceChanged('Native carriers changed during Project SPEC selection.') from error
        if capture.errors:
            raise common.SourceChanged('Native carrier capture is incomplete.')
        atom_id = f'{selection.project_prefix}-S-{common.next_native_number(selection, capture, "S")}'
        header = canonical_native_header({'identity': {'atom_id': atom_id},
            'context': {'container': {'component': 'C00'}, 'tier': tier,
                        'template': values['template'], 'lens': values['lens']},
            'state': {'status': 'draft', 'version': 1, 'updated_at': datetime.now(timezone.utc).isoformat()}})
        validate_project_spec(header, validate, values['body'])
        try:
            path = native_carrier_path(header, summary, project_root=selection.control_root, owner_directory=selection.control_root)
            raw = b'---\n' + yaml.safe_dump(header, sort_keys=False).encode() + b'---\n' + values['body'].encode('utf-8')
        except (ValueError, UnicodeError) as error:
            raise common.InputError('summary', 'Summary cannot be used in a Project SPEC filename.') from error
        with bind_query_reader(None):
            outcome = common.write_destination(selection.root, path, raw)
        data = {} if outcome.errors else {'savedDraft': common.saved(selection, path, atom_id, f'{atom_id}@1-draft', 1, 'Draft')}
        if data:
            data['savedDraft']['updated_at'] = header['state']['updated_at']
        return common.result(effects=outcome.effects, errors=outcome.errors, **data)
