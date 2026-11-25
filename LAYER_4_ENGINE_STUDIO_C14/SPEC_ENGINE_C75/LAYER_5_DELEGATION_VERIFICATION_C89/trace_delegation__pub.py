"""Compare a delegated outcome with the provider's pinned Specs."""

from ..LAYER_1_SPEC_SOURCES_C83.boundary_model__pub import load_boundary_model, load_formal_claim
from ..LAYER_3_LEAN_TRANSLATOR_C84.lean_spec__pub import compile_lean
from ..LAYER_2_FORMAL_MODEL_C85.claim_model__pub import normalize_claim
from .sibling_delegation__pub import _require_sibling
from ..LAYER_4_SPEC_COMPARISON_C88.top_down__pub import compare_delegation
from ..LAYER_2_FORMAL_MODEL_C85.trace_manifest__pub import outcome_cases
from ..LAYER_4_SPEC_COMPARISON_C88.trace_spec__pub import compare_trace_workflow


def _requirement(workflow, event, interface=None):
    operations = workflow.get('operations', {'': workflow})
    selected = [row['expect'] for model in operations.values() for state in model.get('states', [])
                for row in state['transitions'] if row['event'] == event]
    if (not selected or selected[0]['kind'] != 'effect'
            or any(expect != selected[0] for expect in selected[1:])):
        return {}
    expect = selected[0]
    detail = expect.get('detail', {})
    if interface is not None and detail.get('interface') != interface:
        raise ValueError(f'The selected event does not use interface {interface}')
    names = {key: detail.get(key) for key in ('component', 'action', 'output')}
    effect = (expect.get('target'), expect.get('outcome'))
    if not all(isinstance(value, str) and value.strip() for value in (*effect, *names.values())):
        return {}
    return {**names, 'effect': effect}


def _declared_outcome(cases, required):
    for case in cases:
        if case.get('action') != required['action'] or case.get('output') != required['output']:
            continue
        facts = {'action': case['action'], 'output': case['output']}
        if any(tuple(effect[:2]) == required['effect'] for effect in case.get('must_effect', ())):
            facts['effect'] = required['effect']
        elif required['effect'][0] in case.get('forbid_effect', ()):
            facts['effect'] = 'forbidden'
        return facts
    return {}


def _modeled_outcome(workflow, required, lean):
    if 'states' not in workflow:
        return {}
    trace = {'action': required['action'], 'output': required['output'], 'must_effect': [required['effect']]}
    proof = compare_trace_workflow(trace, workflow, lean=lean)
    effect, = (fact for fact in proof['facts'] if fact['key'] == 'must_effect')
    facts = {'action': workflow['action']}
    if effect['status'] != 'unresolved':
        facts.update(output=required['output'], effect=required['effect'] if effect['status'] == 'matched' else None)
    return facts


def _require_provider_interface(contract, workflow, interface):
    declared = contract.get('interface')
    if declared is not None and declared != interface:
        raise ValueError(f'The provider Contract does not use interface {interface}')
    initial = next((state for state in workflow.get('states', ())
                    if state['name'] == workflow.get('initial')), None)
    for row in initial.get('transitions', ()) if initial else ():
        expect = row['expect']
        detail = expect.get('detail', {})
        if (expect.get('kind') == 'trigger' and isinstance(expect.get('target'), str)
                and (declared is not None or detail.get('transport') in ('in_process', 'http', 'cli'))
                and expect['target'] != interface):
            raise ValueError(f'The provider Solution does not use interface {interface}')


def _offerings(compiled, child, required, lean, interface=None):
    if not required:
        return dict.fromkeys(('manifest', 'contract', 'solution'))
    claims = compiled['claims']
    cases, _ = outcome_cases(claims.get('manifest', {}).get('boundaries'))
    if interface is not None:
        cases = [case for case in cases if case['action'] == interface]
    contract, workflow = (claims.get(role, {}) for role in ('contract', 'solution'))
    if 'operations' in contract:
        contract = contract['operations'].get(required['action'], {})
    if 'operations' in workflow:
        workflow = workflow['operations'].get(required['action'], {})
    if interface is not None:
        _require_provider_interface(contract, workflow, interface)
    if contract.get('transport') == 'cli':
        contract = {'action': contract.get('action'), **contract.get('trace', {})}
    elif not any(language == 'python trace' for language, _ in child['contract']['claims']):
        contract = {}
    return {'manifest': _declared_outcome(cases, required),
            'contract': _declared_outcome(contract.get('cases', [contract]), required),
            'solution': _modeled_outcome(workflow, required, lean)}


def _check_outcome(caller, caller_id, caller_issues, provider, *, event, lean, interface=None):
    workflow, error = normalize_claim('solution', caller, caller_id)
    required = _requirement(workflow or {}, event, interface)
    compiled = compile_lean(provider)
    sources = {'caller': caller['source'],
               **{role: provider[role]['source'] for role in ('manifest', 'contract', 'solution')}}
    obligations = {role: {'component': provider['component_id'], **(facts or {})}
                   for role, facts in _offerings(compiled, provider, required, lean, interface).items()}
    obligations['caller'] = required
    diagnostics = caller_issues or ([error] if error else [])
    if not required and not diagnostics:
        diagnostics = ['The selected effect has no complete provider action and output binding']
    report = compare_delegation(sources, obligations, lean=lean)
    return {**report, 'event': event, 'issues': compiled['issues'],
            'unresolved': [*compiled['unresolved'], *(
                {'source': caller['source'], 'field': 'solution', 'message': issue} for issue in diagnostics)],
            'unmodeled': ['Call arguments and exact returned values']}


def check_child_outcome(root, parent_solution, child_id, child_pins, *, event, lean='lean'):
    """Check that the selected child outcome guarantees the effect the parent relies on."""
    parent_id = parent_solution['container_component']
    _, caller, caller_issues = load_formal_claim(root, parent_id, 'solution', parent_solution)
    child = load_boundary_model(root, child_id, *child_pins)
    if child['manifest']['source']['container_component'] != parent_id or child_id == parent_id:
        raise ValueError(f'{child_id} is not a declared child of {parent_id}')
    return _check_outcome(caller, parent_id, caller_issues, child, event=event, lean=lean)


def check_sibling_outcome(root, caller_pins, provider_id, provider_pins, *, event, interface, lean='lean'):
    """Check the required outcome of a declared sibling client."""
    caller_id = caller_pins[2]['container_component']
    caller = load_boundary_model(root, caller_id, *caller_pins)
    provider = load_boundary_model(root, provider_id, *provider_pins)
    _require_sibling(caller, provider, interface, None)
    boundaries = provider['manifest']['boundaries']
    io = boundaries.get('io') if isinstance(boundaries, dict) else None
    servers = io.get('server') if isinstance(io, dict) else None
    if not isinstance(servers, dict) or interface not in servers:
        raise ValueError(f'{provider_id} does not declare server {interface}')
    issues = [issue for issue in caller['issues'] if issue.startswith('solution:')]
    report = _check_outcome(caller['solution'], caller_id, issues, provider, event=event, lean=lean,
                            interface=interface)
    return {**report, 'declared_client': caller['manifest']['source']}
