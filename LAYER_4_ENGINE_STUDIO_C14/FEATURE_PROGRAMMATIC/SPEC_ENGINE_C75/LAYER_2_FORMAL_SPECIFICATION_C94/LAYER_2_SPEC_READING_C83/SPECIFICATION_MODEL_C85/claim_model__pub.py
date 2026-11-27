"""Normalize and validate admitted Python formal declarations."""

from ...LAYER_1_DIAGNOSTICS_C90._package__shared import finding
from .._package__shared import SourceError, load_formal_claim, load_manifest
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


def _lower_claim(role, language, source, component_id, *, public=False):
    if language == 'python group':
        return parse_group(source, role)
    if language == 'python shape':
        return parse_shape(source, role)
    if language == 'python framing':
        return parse_framing(source, role)
    if role == 'contract' and language == 'python contract':
        return parse_contract(source)
    if role == 'contract' and language == 'python cli':
        return parse_cli_contract(source, public=public)
    if role == 'contract' and language == 'python trace':
        return parse_trace_contract(source, public=public)
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
    if any({'profile', 'cases', 'invariant'} & case.keys() for case in cases):
        raise ValueError('declare the action profile and its cases once')
    if any(case.get('transport') == 'cli' for case in cases):
        common = [{key: value for key, value in case.items() if key != 'trace'} for case in cases]
        if any(case != common[0] for case in common) or any('trace' not in case for case in cases):
            raise ValueError('CLI outcomes for one action must share one binding and common guarantees')
        traces = [{'action': case['action'], **case['trace']} for case in cases]
        return {**common[0], 'cases': _trace_profile(traces)['cases']}
    if any('output' not in case for case in cases):
        raise ValueError('multiple claims for one action must be trace outcomes')
    if len({case['output'] for case in cases}) != len(cases):
        raise ValueError('trace claims must have unique outputs')
    fields = dict.fromkeys((*_HTTP_TRACE_BINDING, *_IN_PROCESS_TRACE_BINDING))
    binding, *others = [{key: case[key] for key in fields if key in case} for case in cases]
    if any(other != binding for other in others):
        raise ValueError('trace outcomes for one action must share one binding')
    return {**binding, 'cases': cases}


def _contract_operations(claims, *, public=False):
    if any(language not in ('python trace', 'python cli', 'python contract') for language, _ in claims):
        raise ValueError('multiple Contract claims must declare supported operations')
    by_action = {}
    for language, source in claims:
        case = _lower_claim('contract', language, source, None, public=public)
        name = case.get('action', case.get('operation'))
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


def _framing_split(claims):
    framing = [claim for claim in claims if claim[0] == 'python framing']
    operations = [claim for claim in claims if claim[0] != 'python framing']
    return framing, operations


def _mixed_framing(role, framing, operations, component_id, *, public):
    if len(framing) != 1:
        raise ValueError(f'expected one {role} framing claim')
    if role == 'contract':
        modeled = _contract_operations(operations, public=public)
    else:
        modeled = _workflow_operations(operations, component_id)
    names = modeled.get('operations')
    if names is None:
        action = modeled.get('action') or modeled.get('operation')
        if action is None and 'cases' in modeled:
            action = modeled['cases'][0]['action']
        names = (action,)
    if 'framing' in names:
        raise ValueError("The Action name 'framing' is reserved for the framing profile")
    return {'framing': _lower_claim(role, *framing[0], component_id), **modeled}


def select_formal_claims(model, action):
    """Select framing or workflow claims from a mixed embedded Contract."""
    if not model.get('embedded_contract'):
        return model
    scopes = {role: _framing_split(model[role]['claims']) for role in ('contract', 'solution')}
    if not any(framing and operations for framing, operations in scopes.values()):
        return model
    if action is None:
        raise ValueError("Select 'framing' or a declared workflow Action for a mixed formal chain")
    selected = {}
    for role, (framing, operations) in scopes.items():
        carrier = model[role]
        if framing and operations:
            _, error = normalize_claim(role, carrier, model['component_id'])
            if error is not None:
                raise SourceError(role, carrier['source'], 'claim', error)
        selected[role] = {**carrier, 'claims': framing if action == 'framing' else operations}
    return {**model, **selected}


def normalize_claim(role, carrier, component_id):
    claims = carrier['claims']
    if not claims:
        return None, 'expected exactly one supported formal claim'
    try:
        public = carrier.get('public', False)
        framing, operations = _framing_split(claims)
        if len(claims) == 1:
            model = _lower_claim(role, *claims[0], component_id, public=public)
        elif framing and operations:
            model = _mixed_framing(role, framing, operations, component_id, public=public)
        elif role == 'contract':
            model = _contract_operations(claims, public=public)
        else:
            model = _workflow_operations(claims, component_id)
    except (SyntaxError, TypeError, ValueError) as error:
        return None, str(error)
    return model, None


def validate_declaration(root, component_id, role, pin):
    """Validate one exact formal declaration independently of companion Specs."""
    if role == 'manifest':
        manifest = load_manifest(root, component_id, pin)
        source = manifest['source']
        report = {'source': source, **validate_manifest(manifest)}
        if 'contract' in manifest:
            _, error = normalize_claim('contract', manifest['contract'], component_id)
            errors = manifest['contract_issues'] or ([error] if error else [])
            report['unresolved'].extend(finding(source, 'contract', issue) for issue in errors)
        return report
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
    claims = {}
    if not validation['issues']:
        claims['manifest'] = manifest['fields']
    for role in ('contract', 'solution'):
        carrier = model[role]
        claim, error = normalize_claim(role, carrier, model['component_id'])
        if error is None:
            claims[role] = claim
        else:
            validation['unresolved'].append(finding(carrier['source'], role, error))
    return {
        'issues': validation['issues'],
        'unresolved': validation['unresolved'],
        'claims': claims,
    }
