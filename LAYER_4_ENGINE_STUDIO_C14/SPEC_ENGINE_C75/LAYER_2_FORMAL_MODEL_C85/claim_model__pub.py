"""Normalize and validate admitted Python formal declarations."""

from ..LAYER_1_DIAGNOSTICS_C90.diagnostics__pub import finding
from ..LAYER_1_SPEC_SOURCES_C83.boundary_model__pub import load_formal_claim, load_manifest
from .carrier_framing__pub import parse_framing
from .contract_model__pub import (
    _HTTP_TRACE_BINDING,
    _IN_PROCESS_TRACE_BINDING,
    parse_cli_contract,
    parse_contract,
    parse_trace_contract,
)
from .group_model__pub import parse_group
from .manifest_validation__pub import validate_manifest
from .shape_model__pub import parse_shape
from .workflow_model__pub import normalize_workflow, parse_workflow


def _lower_claim(role, language, source, component_id):
    if language == 'python group':
        return parse_group(source, role)
    if language == 'python shape':
        return parse_shape(source, role)
    if language == 'python framing':
        return parse_framing(source, role)
    if role == 'contract' and language == 'python contract':
        return parse_contract(source)
    if role == 'contract' and language == 'python cli':
        return parse_cli_contract(source)
    if role == 'contract' and language == 'python trace':
        return parse_trace_contract(source)
    if role == 'solution' and language == 'python':
        workflow = parse_workflow(source)
        if workflow['component'] != component_id:
            raise ValueError('workflow Component does not match its Solution')
        model = normalize_workflow(workflow['machine'])
        claim = {'action': workflow['action'], **model}
        if 'startup' in workflow:
            claim['startup'] = workflow['startup']
        return claim
    raise ValueError(f'unsupported {role} formal claim language {language!r}')


def _trace_profile(cases):
    if len(cases) == 1:
        return cases[0]
    if any('output' not in case for case in cases):
        raise ValueError('multiple claims for one action must be trace outcomes')
    if len({case['output'] for case in cases}) != len(cases):
        raise ValueError('trace claims must have unique outputs')
    fields = dict.fromkeys((*_HTTP_TRACE_BINDING, *_IN_PROCESS_TRACE_BINDING))
    binding, *others = [{key: case[key] for key in fields if key in case} for case in cases]
    if any(other != binding for other in others):
        raise ValueError('trace outcomes for one action must share one binding')
    return {**binding, 'cases': cases}


def _contract_operations(claims):
    parsers = {'python trace': parse_trace_contract, 'python cli': parse_cli_contract,
               'python contract': parse_contract}
    if any(language not in parsers for language, _ in claims):
        raise ValueError('multiple Contract claims must declare supported operations')
    by_action = {}
    for language, source in claims:
        case = parsers[language](source)
        name = case['operation'] if language == 'python contract' else case['action']
        by_action.setdefault(name, []).append(case)
    profiles = {action: _trace_profile(cases) for action, cases in by_action.items()}
    return next(iter(profiles.values())) if len(profiles) == 1 else {'operations': profiles}


def _workflow_operations(claims, component_id):
    if any(language != 'python' for language, _ in claims):
        raise ValueError('multiple Solution claims must all be Python workflows')
    operations = {}
    for language, source in claims:
        workflow = _lower_claim('solution', language, source, component_id)
        action = workflow['action']
        if action in operations:
            raise ValueError(f'duplicate Solution action {action!r}')
        operations[action] = workflow
    return {'operations': operations}


def normalize_claim(role, carrier, component_id):
    claims = carrier['claims']
    if not claims:
        return None, 'expected exactly one supported formal claim'
    try:
        if len(claims) == 1:
            model = _lower_claim(role, *claims[0], component_id)
        elif role == 'contract':
            model = _contract_operations(claims)
        else:
            model = _workflow_operations(claims, component_id)
    except (SyntaxError, TypeError, ValueError) as error:
        return None, str(error)
    return model, None


def validate_declaration(root, component_id, role, pin):
    """Validate one exact formal declaration independently of companion Specs."""
    if role == 'manifest':
        manifest = load_manifest(root, component_id, pin)
        return {'source': manifest['source'], **validate_manifest(manifest)}
    _, declaration, issues = load_formal_claim(root, component_id, role, pin)
    source = declaration['source']
    report = {'source': source, 'issues': [
        {'source': source, 'field': role, 'message': issue} for issue in issues
    ], 'unresolved': []}
    if not issues:
        _, error = normalize_claim(role, declaration, component_id)
        if error is not None:
            report['unresolved'].append({'source': source, 'field': role, 'message': error})
    return report


def normalize_spec(model):
    manifest = model['manifest']
    validation = validate_manifest(manifest)
    claims = {} if validation['issues'] else {'manifest': manifest['fields']}
    for role in ('contract', 'solution'):
        carrier = model[role]
        claim, error = normalize_claim(role, carrier, model['component_id'])
        if error is None:
            claims[role] = claim
        else:
            validation['unresolved'].append(finding(carrier['source'], role, error))
    return {**validation, 'claims': claims}
