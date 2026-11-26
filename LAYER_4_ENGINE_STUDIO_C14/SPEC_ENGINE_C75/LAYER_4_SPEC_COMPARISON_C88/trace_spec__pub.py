"""Compare trace Contract obligations with a normalized workflow in Lean."""

from ..LAYER_1_DIAGNOSTICS_C90.diagnostics__pub import verdict
from ..LAYER_2_FORMAL_MODEL_C85.contract_model__pub import _HTTP_TRACE_BINDING, _IN_PROCESS_TRACE_BINDING
from ..LAYER_2_FORMAL_MODEL_C85.trace_manifest__pub import outcome_cases
from ..LAYER_3_LEAN_TRANSLATOR_C84.lean_check__pub import run_lean_json
from ..LAYER_3_LEAN_TRANSLATOR_C84.lean_values__pub import lean_string
from ..LAYER_3_LEAN_TRANSLATOR_C84.trace_lean__pub import _effect, _effect_rules, _program
from ..LAYER_3_MERMAID_RENDERER_C87.solution_diagram__pub import render_solution
from .top_down__pub import compare_obligations

_UNRENDERED = object()


def compare_trace_workflow(contract, workflow, *, lean='lean'):
    """Compare a parsed trace Contract with a compiled workflow claim."""
    statuses = run_lean_json(_program(contract, workflow), lean)
    effects = contract.get('must_effect', [])
    forbidden = contract.get('forbid_effect', [])
    orders = contract.get('must_precede', [])
    if (not isinstance(statuses, list) or len(statuses) != 2 + len(effects) + len(forbidden) + len(orders)
            or any(status not in ('matched', 'conflicting', 'unresolved') for status in statuses)):
        raise ValueError('unexpected Lean trace comparison output')
    facts = [{'key': 'action', 'left': contract['action'], 'right': workflow['action'], 'status': statuses[0]}]
    facts.extend({'key': 'must_effect', 'left': effect, 'status': status}
                 for effect, status in zip(effects, statuses[1:1 + len(effects)]))
    facts.extend({'key': 'forbid_effect', 'left': target, 'status': status}
                 for target, status in zip(forbidden, statuses[1 + len(effects):1 + len(effects) + len(forbidden)]))
    facts.extend({'key': 'must_precede', 'left': order, 'status': status}
                 for order, status in zip(orders, statuses[1 + len(effects) + len(forbidden):-1]))
    facts.append({'key': 'terminal_output', 'status': statuses[-1]})
    return {'status': verdict(statuses), 'facts': facts}


def _manifest_binding(manifest, contract):
    boundaries = manifest.get('boundaries')
    io = boundaries.get('io') if isinstance(boundaries, dict) else None
    servers = io.get('server') if isinstance(io, dict) else None
    if not isinstance(servers, dict):
        return {}
    server = servers.get(contract['interface'])
    if server is None:
        return {'interface': None}
    if not isinstance(server, dict) or not isinstance(server.get('transport'), str):
        return {}
    if contract['transport'] == 'in_process':
        return {'interface': contract['interface'],
                **{key: server[key] for key in ('transport', 'entry') if isinstance(server.get(key), str)}}
    routes = server.get('routes')
    if isinstance(routes, list) and all(isinstance(route, str) for route in routes):
        return {'interface': contract['interface'], 'transport': server['transport'],
                'route': contract['route'] if contract['route'] in routes else None}
    if not isinstance(routes, dict):
        return {}
    operation = routes.get(contract['route'])
    if operation is not None and not isinstance(operation, str):
        return {}
    return {'interface': contract['interface'], 'route': contract['route'],
            'transport': server['transport'], 'operation': operation}


def _solution_binding(workflow, binding):
    states = workflow.get('states')
    if not isinstance(states, list):
        return {}
    initial = next((state for state in states if state['name'] == workflow.get('initial')), None)
    if initial is None:
        return {}
    transitions = initial['transitions']
    if len(transitions) != 1:
        return {'interface': None}
    expect = transitions[0]['expect']
    if expect.get('kind') != 'trigger':
        return {'interface': None}
    detail = expect.get('detail')
    if not isinstance(detail, dict):
        return {}
    if not isinstance(expect.get('target'), str):
        return {}
    return {'interface': expect['target'],
            **{key: detail[key] for key in binding[1:] if isinstance(detail.get(key), str)}}


def _binding_directions(sources, claims, contract, workflow, lean):
    binding = _IN_PROCESS_TRACE_BINDING if contract['transport'] == 'in_process' else _HTTP_TRACE_BINDING
    obligations = {'manifest': _manifest_binding(claims.get('manifest', {}), contract),
                   'contract': {key: contract[key] for key in binding},
                   'solution': _solution_binding(workflow, binding)}
    return compare_obligations(sources, obligations, lean=lean)['directions']


def _compare_cases(cases, workflow, lean):
    facts, statuses = [], []
    for case in cases:
        if all(key in workflow for key in ('action', 'initial', 'states')):
            result = compare_trace_workflow(case, workflow, lean=lean)
        else:
            result = {'status': 'unresolved', 'facts': [{'key': 'trace', 'status': 'unresolved'}]}
        facts.extend({**fact, 'action': case['action'], 'output': case['output']} for fact in result['facts'])
        statuses.append(result['status'])
    return {'status': verdict(statuses), 'facts': facts}


def _manifest_contract(cases, contract, lean):
    contracts = contract.get('cases', [contract])
    facts, expressions = [], []
    for case in cases:
        match = next((row for row in contracts if row.get('action') == case['action']
                      and row.get('output') == case['output']), None)
        for key in ('must_effect', 'forbid_effect'):
            for value in case.get(key, []):
                facts.append({'key': key, 'left': value, 'action': case['action'], 'output': case['output']})
                if match is None:
                    expressions.append('"unresolved"')
                else:
                    if key == 'must_effect':
                        candidates = ', '.join(_effect(item) for item in match.get(key, []))
                        condition = f'([{candidates}] : List Effect).any (fun actual => implies actual {_effect(value)})'
                    else:
                        candidates = ', '.join(lean_string(item) for item in match.get(key, []))
                        condition = f'([{candidates}] : List String).contains {lean_string(value)}'
                    expressions.append(f'if {condition} then "matched" else "conflicting"')
    program = 'import Lean\n' + _effect_rules() + '#eval IO.println (Lean.toJson [' + ', '.join(expressions) + ']).compress\n'
    statuses = run_lean_json(program, lean)
    if not isinstance(statuses, list) or len(statuses) != len(facts) or any(
            status not in ('matched', 'conflicting', 'unresolved') for status in statuses):
        raise ValueError('unexpected Lean manifest comparison output')
    for fact, status in zip(facts, statuses):
        fact['status'] = status
    return {'status': verdict(statuses), 'facts': facts}


def _merge_direction(directions, key, comparison):
    current = directions[key]
    if current['facts']:
        current['facts'].extend(comparison['facts'])
        current['status'] = verdict([current['status'], comparison['status']])
    else:
        directions[key] = comparison


def _add_manifest_outcomes(directions, boundaries, contract, workflow, lean, *, action=None):
    cases, _ = outcome_cases(boundaries)
    if action is not None:
        cases = [case for case in cases if case['action'] == action]
    if cases:
        _merge_direction(directions, 'manifest_contract', _manifest_contract(cases, contract, lean))
        _merge_direction(directions, 'manifest_solution', _compare_cases(cases, workflow, lean))


def _profile_directions(sources, claims, contract_claim, workflow, lean, *, action=None):
    if 'cases' in contract_claim:
        comparison = _compare_cases(contract_claim['cases'], workflow, lean)
    elif (all(key in contract_claim for key in ('action', 'output'))
            and bool({'must_effect', 'forbid_effect'} & contract_claim.keys())
            and all(key in workflow for key in ('action', 'initial', 'states'))):
        comparison = compare_trace_workflow(contract_claim, workflow, lean=lean)
    else:
        comparison = {'status': 'unresolved', 'facts': []}
    directions = {'manifest_contract': {'status': 'unresolved', 'facts': []},
                  'manifest_solution': {'status': 'unresolved', 'facts': []},
                  'contract_solution': comparison}
    if contract_claim.get('transport') in ('http', 'in_process'):
        directions = _binding_directions(sources, claims, contract_claim, workflow, lean)
        binding = directions['contract_solution']
        binding['facts'].extend(comparison['facts'])
        binding['status'] = verdict([binding['status'], comparison['status']])
    _add_manifest_outcomes(directions, claims.get('manifest', {}).get('boundaries'),
                           contract_claim, workflow, lean, action=action)
    return directions


def _operation_claims(claim):
    if 'operations' in claim:
        return claim['operations']
    action = claim['cases'][0]['action'] if 'cases' in claim else claim.get('action')
    return {action: claim} if isinstance(action, str) else {}


def _uncovered_outcomes(boundaries, contract, workflow, selected):
    cases, _ = outcome_cases(boundaries)
    declared = {}
    for case in cases:
        declared.setdefault(case['action'], set()).add(case['output'])
    for action, profile in _operation_claims(contract).items():
        names = declared.setdefault(action, set())
        outcomes = profile.get('cases', [profile, profile.get('trace', {})])
        names.update(case['output'] for case in outcomes if 'output' in case)
        if profile.get('transport') == 'cli':
            names.update(profile.get('outcomes', {}))
            names.update(profile.get('exit_codes', {}))
            names.update(key.removeprefix('stdout.') for key in profile if key.startswith('stdout.'))
    gaps = []
    for action, profile in _operation_claims(workflow).items():
        if not declared.get(action) or (selected is not None and action != selected):
            continue
        states = profile.get('states', ())
        finals = {state['name'] for state in states if state['final']}
        outputs = {edge['expect']['outcome'] for state in states for edge in state['transitions']
                   if edge['target'] in finals and edge['expect']['kind'] == 'output'
                   and (edge['expect'].get('outcome') or '').strip()}
        gaps.extend({'action': action, 'output': name} for name in sorted(outputs - declared[action]))
    return gaps


def _operation_directions(sources, claims, contract, workflow, lean):
    boundaries = claims.get('manifest', {}).get('boundaries')
    cases, _ = outcome_cases(boundaries)
    contracts, solutions = _operation_claims(contract), _operation_claims(workflow)
    actions = dict.fromkeys((*contracts, *solutions, *(case['action'] for case in cases)))
    operations = {
        action: _profile_directions(sources, claims, contracts.get(action, {}), solutions.get(action, {}),
                                    lean, action=action)
        for action in actions
    }
    keys = next(iter(operations.values()))
    directions = {}
    for key in keys:
        directions[key] = {
            'status': verdict([report[key]['status'] for report in operations.values()]),
            'facts': [{'action': action, **fact} for action, report in operations.items()
                      for fact in report[key]['facts']],
        }
    return operations, directions


def check_trace_spec(root, component_id, manifest, contract, solution, *, action=None, lean='lean'):
    """Check the trace Contracts and Solution workflows by declared action."""
    from ..LAYER_1_SPEC_SOURCES_C83.boundary_model__pub import load_boundary_model
    from ..LAYER_3_LEAN_TRANSLATOR_C84.lean_spec__pub import compile_lean

    model = load_boundary_model(root, component_id, manifest, contract, solution)
    compiled = compile_lean(model)
    return compare_trace_spec(model, compiled, action=action, lean=lean)


def compare_trace_spec(model, compiled, *, action=None, lean='lean', mermaid=_UNRENDERED):
    """Compare a loaded trace chain using its normalized declarations."""
    claims = compiled['claims']
    if mermaid is _UNRENDERED:
        mermaid = render_solution(model, claims.get('solution'))
    sources = {role: model[role]['source'] for role in ('manifest', 'contract', 'solution')}
    contract_claim, workflow = claims.get('contract', {}), claims.get('solution', {})
    has_trace = any(language == 'python trace' for language, _ in model['contract']['claims'])
    contract_claim = contract_claim if has_trace else {}
    operations = {}
    if action is not None:
        directions = _profile_directions(
            sources, claims, _operation_claims(contract_claim).get(action, {}),
            _operation_claims(workflow).get(action, {}), lean, action=action)
    elif 'operations' in contract_claim or 'operations' in workflow:
        operations, directions = _operation_directions(sources, claims, contract_claim, workflow, lean)
    else:
        directions = _profile_directions(sources, claims, contract_claim, workflow, lean)
    statuses = [direction['status'] for direction in directions.values()]
    boundaries = claims.get('manifest', {}).get('boundaries')
    uncovered = _uncovered_outcomes(boundaries, claims.get('contract', {}), workflow, action)
    if compiled['issues'] or compiled['unresolved'] or uncovered:
        statuses.append('unresolved')
    return {'status': verdict(statuses), **({'operations': operations} if operations else {}),
            'sources': sources, 'directions': directions, 'issues': compiled['issues'],
            'unresolved': compiled['unresolved'], 'uncovered_outcomes': uncovered, 'mermaid': mermaid}
