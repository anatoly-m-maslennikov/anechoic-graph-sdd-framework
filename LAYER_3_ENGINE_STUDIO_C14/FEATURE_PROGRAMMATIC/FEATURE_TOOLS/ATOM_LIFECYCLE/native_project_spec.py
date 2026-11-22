"""Create and validate Project-owned Axiom and Applicable Principle Drafts."""
from datetime import datetime, timezone
import re

import yaml

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.native_carrier_header__pub import canonical_native_header, native_header_view
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.native_carrier_placement__pub import native_carrier_path, spec_lens_directories
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.native_source_rows__pub import capture_native

from . import common
from .source import bind_query_reader

PROJECT_SPEC_TIERS = {'project_contract': (0,), 'axiom': (-1,), 'applicable_principle': (1, 2)}


def validate_project_spec(header, validate, body=None):
    view = native_header_view(header)
    context = view['context']
    template = context.get('template')
    tiers = PROJECT_SPEC_TIERS.get(template)
    container = context.get('container')
    if (tiers is None or container != {'component': 'C00'} or
            type(context.get('tier')) is not int or context['tier'] not in tiers):
        raise common.InputError('newAtom', 'Project SPEC requires its declared Tier and Project C00 container.')
    try:
        if template == 'project_contract':
            validate(template, header, 'C00', body)
        else:
            validate(template, header, 'C00')
    except (ValueError, TypeError, KeyError) as error:
        raise common.InputError('newAtom', f'Project SPEC does not satisfy the compiled Model: {error}') from error


def create_project_spec(selection, values, validate):
    from .native_draft import _first_spec_write_lock, _summary
    if (not isinstance(values, dict) or set(values) - {'tier'} != {'template', 'container', 'lens', 'body'}
            or values.get('template') not in PROJECT_SPEC_TIERS or values.get('container') != {'component': 'C00'}
            or not isinstance(values.get('body'), str) or not isinstance(values.get('lens'), str)):
        raise common.InputError('newAtom', 'Supply a Project SPEC template, Project C00, Lens, and Markdown body.')
    tiers = PROJECT_SPEC_TIERS[values['template']]
    tier = values.get('tier', tiers[-1])
    if type(tier) is not int or tier not in tiers:
        raise common.InputError('tier', 'Tier must match the selected Project SPEC template.')
    if values['template'] == 'axiom' and values['lens'] != 'SPEC':
        raise common.InputError('lens', 'Axiom requires the SPEC Lens.')
    try:
        spec_lens_directories(values['lens'])
    except ValueError as error:
        raise common.InputError('lens', 'Supply a valid Lens.') from error
    summary = _summary(values['body'])
    if (not selection.root.is_absolute() or not selection.control_root.is_relative_to(selection.root)
            or not selection.manifest_path.is_relative_to(selection.control_root)):
        raise common.SourceChanged('Selected Project path is invalid.')
    with _first_spec_write_lock(selection.root):
        try:
            capture = capture_native(selection)
        except (OSError, RuntimeError, ValueError) as error:
            raise common.SourceChanged('Native carriers changed during Project SPEC selection.') from error
        if capture.errors:
            raise common.SourceChanged('Native carrier capture is incomplete.')
        pattern = re.compile(re.escape(selection.project_prefix) + r'-S-([0-9]+)')
        numbers = [int(match[1]) for row in capture.atoms if isinstance(row.get('id'), str)
                   and (match := pattern.fullmatch(row['id']))]
        atom_id = f'{selection.project_prefix}-S-{max(numbers, default=0) + 1}'
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
        return common.result(effects=outcome.effects, errors=outcome.errors, **data)
