"""Compare trace Contract obligations with a normalized workflow in Lean."""

from ..LAYER_1_DIAGNOSTICS_C90._package__shared import verdict
from ..LAYER_2_SPEC_READING_C83.SPECIFICATION_MODEL_C85._package__shared import (
    _HTTP_TRACE_BINDING,
    _IN_PROCESS_TRACE_BINDING,
    http_binding,
    outcome_cases,
)
from ..LAYER_3_LEAN_TRANSLATOR_C84._package__shared import (
    _effect,
    _effect_rules,
    _program,
    lean_string,
    run_lean_json,
)
from ..LAYER_3_MERMAID_RENDERER_C87._package__shared import render_solution
from .direct_comparison import report_comparison
from .http_spec import compare_http_workflow, manifest_http_binding
from .top_down__pub import compare_obligations

_UNRENDERED = object()


def compare_trace_workflow(contract, workflow, *, lean='lean'):
    """Compare a parsed trace Contract with a compiled workflow claim."""
    if {'cases', 'trace', 'invariant'} & contract.keys():
        return _compare_cases(_trace_cases(contract), workflow, lean)
    effects = contract.get('must_effect', [])
    forbidden = contract.get('forbid_effect', [])
    orders = contract.get('must_precede', [])
    count = 2 + len(effects) + len(forbidden) + len(orders)
    has_workflow = all(key in workflow for key in ('action', 'initial', 'states'))
    statuses = run_lean_json(_program(contract, workflow), lean) if has_workflow else ['unresolved'] * count
    if (not isinstance(statuses, list) or len(statuses) != count
            or any(status not in ('matched', 'conflicting', 'unresolved') for status in statuses)):
        raise ValueError('unexpected Lean trace comparison output')
    facts = [{'key': 'action', 'left': contract['action'], 'right': workflow.get('action'), 'status': statuses[0]}]
    facts.extend({'key': 'must_effect', 'left': effect, 'status': status}
                 for effect, status in zip(effects, statuses[1:1 + len(effects)]))
    facts.extend({'key': 'forbid_effect', 'left': target, 'status': status}
                 for target, status in zip(forbidden, statuses[1 + len(effects):1 + len(effects) + len(forbidden)]))
    facts.extend({'key': 'must_precede', 'left': order, 'status': status}
                 for order, status in zip(orders, statuses[1 + len(effects) + len(forbidden):-1]))
    facts.append({'key': 'terminal_output', 'status': statuses[-1]})
    facts.extend({'key': 'same_values', 'left': left, 'right': right, 'status': 'unresolved'}
                 for left, right in contract.get('same_values', []))
    facts.extend({'key': 'value_types', 'field': field, 'expected': kind, 'status': 'unresolved'}
                 for field, kind in contract.get('value_types', []))
    performance = _performance_facts(contract)
    return {'status': verdict([fact['status'] for fact in facts + performance]),
            'facts': facts + performance}


def _performance_facts(contract):
    performance = contract.get('performance', {})
    return [{'key': 'performance', 'name': name, 'left': value,
             'action': contract['action'], 'output': contract['output'],
             'resources': performance['resources'], 'status': 'unresolved'}
            for name, value in performance.get('measurements', {}).items()]


def _manifest_binding(manifest, contract):
    boundaries = manifest.get('boundaries')
    io = boundaries.get('io') if isinstance(boundaries, dict) else None
    servers = io.get('server') if isinstance(io, dict) else None
    if not isinstance(servers, dict):
        return {}
    server = servers.get(contract['interface'])
    if server is None:
        return {'interface': None}
    if not isinstance(server, dict):
        return {}
    transport = server.get('transport')
    if contract['transport'] == 'in_process':
        if 'entry' in contract and not isinstance(transport, str):
            return {}
        return {'interface': contract['interface'],
                **{key: value if isinstance(value := server[key], str) and value.strip() else None
                   for key in ('transport', 'entry') if key in server}}
    if not isinstance(transport, str):
        return {}
    if transport != 'http':
        return {'interface': contract['interface'], 'transport': transport}
    if 'routes' not in server:
        return {}
    return {'interface': contract['interface'], 'transport': transport,
            **manifest_http_binding(server['routes'], contract)}


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
    observed = detail
    if detail.get('transport') == 'http':
        try:
            observed = {**detail, **http_binding(detail)}
        except ValueError:
            observed = {'transport': 'http'}
    return {'interface': expect['target'],
            **{key: observed[key] for key in binding[1:]
               if isinstance(observed.get(key), str)}}


def _binding_directions(sources, claims, contract, workflow, lean):
    binding = (
        _IN_PROCESS_TRACE_BINDING
        if contract["transport"] == "in_process"
        else _HTTP_TRACE_BINDING
    )
    public_in_process = (
        contract["transport"] == "in_process" and "entry" not in contract
    )
    public_binding = binding[:2] if public_in_process else binding
    obligations = {'manifest': _manifest_binding(claims.get('manifest', {}), contract),
                   'contract': {key: contract[key] for key in public_binding},
                   'solution': _solution_binding(workflow, binding)}
    directions = compare_obligations(sources, obligations, lean=lean)['directions']
    if public_in_process:
        consistency = directions['manifest_contract']
        facts = [fact for fact in consistency['facts'] if fact['key'] != 'entry']
        consistency.update(facts=facts, status=verdict([fact['status'] for fact in facts]))
    return directions


def _trace_cases(contract):
    action = contract.get('action')
    trace = contract.get('trace', contract)
    legacy = {'action': action, **{key: value for key, value in trace.items() if key != 'invariant'}}
    cases = contract.get('cases', [legacy] if 'output' in trace else [])
    if 'invariant' in contract:
        return [*cases, {'action': action, **contract['invariant']}]
    return cases


def _compare_cases(cases, workflow, lean):
    facts, statuses = [], []
    for case in cases:
        result = compare_trace_workflow(case, workflow, lean=lean)
        context = ({'scope': 'action', 'action': case['action']} if 'output' not in case else
                   {'action': case['action'], 'output': case['output']})
        facts.extend({**fact, **context} for fact in result['facts'])
        statuses.append(result['status'])
    return {'status': verdict(statuses), 'facts': facts}


def _manifest_contract(cases, contract, lean):
    contracts = _trace_cases(contract)
    facts, expressions = [], []
    for case in cases:
        match = next((row for row in contracts if row.get('action') == case['action']
                      and row.get('output') == case['output']), None)
        for key in ('must_effect', 'forbid_effect'):
            for value in case.get(key, []):
                facts.append({'key': key, 'left': value, 'action': case['action'], 'output': case['output']})
                action_wide = contract.get('invariant', {}).get(key, ()) if case['action'] == contract.get('action') else ()
                if match is None and not action_wide:
                    expressions.append('"unresolved"')
                else:
                    modeled = (match or {}).get(key, ())
                    if key == 'must_effect':
                        candidates = ', '.join(_effect(item) for item in modeled)
                        condition = f'([{candidates}] : List Effect).any (fun actual => implies actual {_effect(value)})'
                    else:
                        candidates = ', '.join(lean_string(item) for item in (*modeled, *action_wide))
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
    directions = {'manifest_contract': {'status': 'unresolved', 'facts': []},
                  'manifest_solution': {'status': 'unresolved', 'facts': []},
                  'contract_solution': {'status': 'unresolved', 'facts': []}}
    if contract_claim.get('transport') in ('http', 'in_process'):
        directions = _binding_directions(sources, claims, contract_claim, workflow, lean)
    _add_manifest_outcomes(directions, claims.get('manifest', {}).get('boundaries'),
                           contract_claim, workflow, lean, action=action)
    comparison = _compare_cases(_trace_cases(contract_claim), workflow, lean)
    if comparison['facts']:
        _merge_direction(directions, 'contract_solution', comparison)
    if contract_claim.get('profile') == 'http':
        _merge_direction(directions, 'contract_solution',
                         compare_http_workflow(sources, contract_claim, workflow, lean))
    return directions


def _operation_claims(claim):
    if 'operations' in claim:
        return claim['operations']
    action = claim.get('action') or (claim['cases'][0]['action'] if 'cases' in claim else None)
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
        if profile.get('profile') == 'http':
            names.update(name for name, _, _ in profile['outcomes'])
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


def check_trace_spec(root, component_id, manifest, contract=None, solution=None, *, action=None, lean='lean'):
    """Check the trace Contracts and Solution workflows by declared action."""
    from ..LAYER_2_SPEC_READING_C83._package__shared import load_boundary_model
    from ..LAYER_2_SPEC_READING_C83.SPECIFICATION_MODEL_C85._package__shared import (
        select_formal_claims,
    )
    from ..LAYER_3_LEAN_TRANSLATOR_C84._package__shared import compile_lean

    model = select_formal_claims(load_boundary_model(root, component_id, manifest, contract, solution), action)
    compiled = compile_lean(model)
    return compare_trace_spec(model, compiled, action=action, lean=lean)


def _trace_claims(model, claims):
    contract, workflow = claims.get('contract', {}), claims.get('solution', {})
    has_trace = any(language == 'python trace' for language, _ in model['contract']['claims'])
    profiles = _operation_claims(contract)
    supported = {action: profile for action, profile in profiles.items()
                 if profile.get('profile') == 'http'
                 or (has_trace and profile.get('transport') != 'cli' and 'facts' not in profile)}
    if 'operations' not in contract:
        return next(iter(supported.values()), {}), workflow
    if 'operations' in workflow:
        specialized = profiles.keys() - supported.keys()
        remaining = {action: value for action, value in workflow['operations'].items() if action not in specialized}
        workflow = {'operations': remaining} if remaining else {}
    return {'operations': supported} if supported else {}, workflow


def compare_trace_spec(model, compiled, *, action=None, lean='lean', mermaid=_UNRENDERED):
    """Compare a loaded trace chain using its normalized declarations."""
    claims = compiled['claims']
    if mermaid is _UNRENDERED:
        mermaid = render_solution(model, claims.get('solution'), action=action)
    sources = {role: model[role]['source'] for role in ('manifest', 'contract', 'solution')}
    contract_claim, workflow = _trace_claims(model, claims)
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
    report = {'status': verdict(statuses), **({'operations': operations} if operations else {}),
              'sources': sources, 'directions': directions, 'issues': compiled['issues'],
              'unresolved': compiled['unresolved'], 'uncovered_outcomes': uncovered, 'mermaid': mermaid}
    return report_comparison(model, report, action=action)
