"""Compare trace Contract obligations with a normalized workflow in Lean."""

import json

from .contract_model__pub import _HTTP_TRACE_BINDING, _IN_PROCESS_TRACE_BINDING, lean_string
from .top_down__pub import _run, _status, compare_obligations
from .trace_manifest import outcome_cases


def _edges(states):
    final = {state['name'] for state in states if state['final']}
    edges = []
    for state in states:
        for transition in state['transitions']:
            expect = transition['expect']
            values = (state['name'], transition['target'], expect['kind'],
                      expect.get('target') or '', expect.get('outcome') or '')
            flags = (expect.get('outcome') is None, transition['target'] in final, expect.get('target') is None)
            fields = [*(lean_string(value) for value in values), *(str(flag).lower() for flag in flags)]
            edges.append('⟨' + ', '.join(fields) + '⟩')
    return ', '.join(edges)


def _rules(count):
    return f'''def selected (e : Edge) : Bool := e.kind == "output" && e.final && (e.wildcard || e.outcome == output)
def reachable (start : String) (removed : Option (String × String)) : List String :=
  (List.range {count}).foldl (fun reached _ =>
    edges.foldl (fun seen e =>
      if seen.contains e.source && !(removed.any (fun r => e.kind == "effect" && e.observed == r.1 && e.outcome == r.2))
      then if seen.contains e.target then seen else e.target :: seen else seen) reached) [start]
def effectStatus (effect : String × String) : String :=
  let reached := reachable initial (some effect)
  if !(edges.any (fun e => selected e && !e.wildcard)) then "unresolved"
  else if edges.any (fun e => selected e && reached.contains e.source)
       then "conflicting" else "matched"
def forbiddenStatus (target : String) : String :=
  let reached := reachable initial none
  if !(edges.any (fun e => selected e && !e.wildcard)) then "unresolved"
  else if edges.any (fun e =>
       let after := reachable e.target none
       e.kind == "effect" && (e.targetWildcard || e.observed == target) && reached.contains e.source &&
       edges.any (fun terminal => selected terminal && after.contains terminal.source))
       then "conflicting" else "matched"
def orderStatus (order : (String × String) × (String × String)) : String :=
  let reached := reachable initial (some order.1)
  if !(edges.any (fun e => selected e && !e.wildcard)) then "unresolved"
  else if edges.any (fun e =>
       let after := reachable e.target none
       e.kind == "effect" && (e.targetWildcard || e.observed == order.2.1) &&
       (e.wildcard || e.outcome == order.2.2) && reached.contains e.source &&
       edges.any (fun terminal => selected terminal && after.contains terminal.source))
       then "conflicting" else "matched"
'''


def _program(contract, workflow):
    states = workflow['states']
    effects = ', '.join(f'({lean_string(target)}, {lean_string(outcome)})'
                        for target, outcome in contract.get('must_effect', []))
    forbidden = ', '.join(lean_string(target) for target in contract.get('forbid_effect', []))
    orders = ', '.join(f'(({lean_string(a)}, {lean_string(b)}), ({lean_string(c)}, {lean_string(d)}))'
                       for (a, b), (c, d) in contract.get('must_precede', []))
    return f'''import Lean
structure Edge where
  source : String
  target : String
  kind : String
  observed : String
  outcome : String
  wildcard : Bool
  final : Bool
  targetWildcard : Bool

def edges : List Edge := [{_edges(states)}]
def initial : String := {lean_string(workflow['initial'])}
def output : String := {lean_string(contract['output'])}
def effects : List (String × String) := [{effects}]
def forbidden : List String := [{forbidden}]
def orders : List ((String × String) × (String × String)) := [{orders}]
{_rules(len(states))}def actionStatus : String :=
  if {lean_string(contract['action'])} == {lean_string(workflow['action'])} then "matched" else "conflicting"
#eval IO.println (Lean.toJson (actionStatus :: effects.map effectStatus ++ forbidden.map forbiddenStatus ++ orders.map orderStatus)).compress
'''


def compare_trace_workflow(contract, workflow, *, lean='lean'):
    """Compare a parsed trace Contract with a compiled workflow claim."""
    statuses = _run(_program(contract, workflow), lean)
    effects = contract.get('must_effect', [])
    forbidden = contract.get('forbid_effect', [])
    orders = contract.get('must_precede', [])
    if (not isinstance(statuses, list) or len(statuses) != 1 + len(effects) + len(forbidden) + len(orders)
            or any(status not in ('matched', 'conflicting', 'unresolved') for status in statuses)):
        raise ValueError('unexpected Lean trace comparison output')
    facts = [{'key': 'action', 'left': contract['action'], 'right': workflow['action'], 'status': statuses[0]}]
    facts.extend({'key': 'must_effect', 'left': effect, 'status': status}
                 for effect, status in zip(effects, statuses[1:1 + len(effects)]))
    facts.extend({'key': 'forbid_effect', 'left': target, 'status': status}
                 for target, status in zip(forbidden, statuses[1 + len(effects):1 + len(effects) + len(forbidden)]))
    facts.extend({'key': 'must_precede', 'left': order, 'status': status}
                 for order, status in zip(orders, statuses[1 + len(effects) + len(forbidden):]))
    return {'status': _status(statuses), 'facts': facts}


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
    return {'status': _status(statuses), 'facts': facts}


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
                    literal = lean_string(json.dumps(value, ensure_ascii=False))
                    candidates = ', '.join(lean_string(json.dumps(item, ensure_ascii=False))
                                           for item in match.get(key, []))
                    expressions.append(f'if ([{candidates}] : List String).contains {literal} '
                                       'then "matched" else "conflicting"')
    program = 'import Lean\n#eval IO.println (Lean.toJson [' + ', '.join(expressions) + ']).compress\n'
    statuses = _run(program, lean)
    if not isinstance(statuses, list) or len(statuses) != len(facts) or any(
            status not in ('matched', 'conflicting', 'unresolved') for status in statuses):
        raise ValueError('unexpected Lean manifest comparison output')
    for fact, status in zip(facts, statuses):
        fact['status'] = status
    return {'status': _status(statuses), 'facts': facts}


def _merge_direction(directions, key, comparison):
    current = directions[key]
    if current['facts']:
        current['facts'].extend(comparison['facts'])
        current['status'] = _status([current['status'], comparison['status']])
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
        binding['status'] = _status([binding['status'], comparison['status']])
    _add_manifest_outcomes(directions, claims.get('manifest', {}).get('boundaries'),
                           contract_claim, workflow, lean, action=action)
    return directions


def _operation_claims(claim):
    if 'operations' in claim:
        return claim['operations']
    action = claim['cases'][0]['action'] if 'cases' in claim else claim.get('action')
    return {action: claim} if isinstance(action, str) else {}


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
            'status': _status([report[key]['status'] for report in operations.values()]),
            'facts': [{'action': action, **fact} for action, report in operations.items()
                      for fact in report[key]['facts']],
        }
    return operations, directions


def check_trace_spec(root, component_id, manifest, contract, solution, *, action=None, lean='lean'):
    """Check the trace Contracts and Solution workflows by declared action."""
    from .boundary_model import load_boundary_model
    from .lean_spec__pub import compile_lean

    model = load_boundary_model(root, component_id, manifest, contract, solution)
    compiled = compile_lean(model)
    claims = compiled['claims']
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
    if compiled['issues'] or compiled['unresolved']:
        statuses.append('unresolved')
    return {'status': _status(statuses), **({'operations': operations} if operations else {}),
            'sources': sources, 'directions': directions, 'issues': compiled['issues'],
            'unresolved': compiled['unresolved'], 'mermaid': compiled['mermaid']}
