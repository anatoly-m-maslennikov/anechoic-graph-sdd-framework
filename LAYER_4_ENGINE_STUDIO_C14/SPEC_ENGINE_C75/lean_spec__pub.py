"""Lower a pinned, formal specification chain to Lean declarations."""

import json

from .boundary_model import load_formal_claim, load_manifest
from .carrier_framing__pub import framing_to_lean, framing_to_mermaid, parse_framing
from .contract_model__pub import (
    _HTTP_TRACE_BINDING,
    _IN_PROCESS_TRACE_BINDING,
    lean_string,
    parse_cli_contract,
    parse_contract,
    parse_trace_contract,
)
from .group_spec__pub import group_to_mermaid, parse_group
from .manifest_validation import validate_manifest
from .shape_spec__pub import parse_shape, shape_to_lean, shape_to_mermaid
from .workflow_model__pub import compile_workflow, parse_workflow, render_operation_diagram


def _lower_claim(role, language, source, component_id):
    if language == 'python group':
        claim = parse_group(source, role)
        return claim, group_to_mermaid(claim, component_id) if role == 'solution' else None
    if language == 'python shape':
        claim = parse_shape(source, role)
        return claim, shape_to_mermaid(claim) if role == 'solution' else None
    if language == 'python framing':
        claim = parse_framing(source, role)
        return claim, framing_to_mermaid(claim) if role == 'solution' else None
    if role == 'contract' and language == 'python contract':
        return parse_contract(source), None
    if role == 'contract' and language == 'python cli':
        return parse_cli_contract(source), None
    if role == 'contract' and language == 'python trace':
        return parse_trace_contract(source), None
    if role == 'solution' and language == 'python':
        workflow = parse_workflow(source)
        if workflow['component'] != component_id:
            raise ValueError('workflow Component does not match its Solution')
        compiled = compile_workflow(workflow['machine'])
        claim = {'action': workflow['action'], **compiled['model']}
        if 'startup' in workflow:
            claim['startup'] = workflow['startup']
        return claim, compiled['mermaid']
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
        workflow, _ = _lower_claim('solution', language, source, component_id)
        action = workflow['action']
        if action in operations:
            raise ValueError(f'duplicate Solution action {action!r}')
        operations[action] = workflow
    return {'operations': operations}, render_operation_diagram(operations)


def _claim(role, carrier, component_id):
    claims = carrier['claims']
    if not claims:
        return None, None, 'expected exactly one supported formal claim'
    try:
        if len(claims) == 1:
            model, mermaid = _lower_claim(role, *claims[0], component_id)
        elif role == 'contract':
            model, mermaid = _contract_operations(claims), None
        else:
            model, mermaid = _workflow_operations(claims, component_id)
    except (SyntaxError, TypeError, ValueError) as error:
        return None, None, str(error)
    return model, mermaid, None


def _lean_declaration(role, source, payload):
    encoded = json.dumps({'source': source, 'claim': payload}, allow_nan=False, ensure_ascii=False)
    return f'def {role} : Except String Lean.Json := Lean.Json.parse {lean_string(encoded)}'


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
        _, _, error = _claim(role, declaration, component_id)
        if error is not None:
            report['unresolved'].append({'source': source, 'field': role, 'message': error})
    return report


def compile_lean(model):
    """Return Lean source, source-linked gaps and the modeled Solution diagram."""
    manifest = model['manifest']
    validation = validate_manifest(manifest)
    declarations = {}
    claims = {}
    framing_models = []
    unresolved = list(validation['unresolved'])
    if not validation['issues']:
        claims['manifest'] = manifest['fields']
        declarations['manifest'] = _lean_declaration('manifest', manifest['source'], manifest['fields'])
    mermaid = None
    for role in ('contract', 'solution'):
        carrier = model[role]
        claim, diagram, error = _claim(role, carrier, model['component_id'])
        if error is not None:
            unresolved.append({'source': carrier['source'], 'field': role, 'message': error})
        else:
            claims[role] = claim
            declarations[role] = _lean_declaration(role, carrier['source'], claim)
            if carrier['claims'][0][0] == 'python shape':
                framing_models.append(shape_to_lean(claim, role))
            if carrier['claims'][0][0] == 'python framing':
                framing_models.append(framing_to_lean(claim, role))
            if role == 'solution':
                mermaid = diagram
    lines = ['import Lean', '', 'namespace AnechoicSpec', *declarations.values(), 'end AnechoicSpec',
             '', *framing_models, '']
    return {'lean': '\n'.join(lines), 'mermaid': mermaid, 'issues': validation['issues'],
            'unresolved': unresolved, 'compiled_roles': list(declarations), 'claims': claims}
