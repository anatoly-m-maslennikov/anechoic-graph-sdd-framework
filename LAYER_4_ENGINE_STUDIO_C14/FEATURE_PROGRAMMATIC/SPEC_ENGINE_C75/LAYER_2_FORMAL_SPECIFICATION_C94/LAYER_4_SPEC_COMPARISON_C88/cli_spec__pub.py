"""Compare a pinned CLI declaration, public Contract and Solution workflow."""

from itertools import pairwise

from ..LAYER_1_DIAGNOSTICS_C90._package__shared import verdict
from ..LAYER_2_SPEC_READING_C83._package__shared import load_boundary_model
from ..LAYER_2_SPEC_READING_C83.SPECIFICATION_MODEL_C85._package__shared import (
    exit_code,
    exit_status_class,
    select_formal_claims,
)
from ..LAYER_3_LEAN_TRANSLATOR_C84._package__shared import compile_lean
from ..LAYER_3_MERMAID_RENDERER_C87._package__shared import render_solution
from .cli_reachability import feasible_terminals
from .cli_selection import _cli_profiles, _initial_trigger, _manifest_endpoint
from .direct_comparison import report_comparison
from .top_down__pub import compare_obligations
from .trace_spec__pub import (
    _add_manifest_outcomes,
    _compare_cases,
    _trace_cases,
    _uncovered_outcomes,
)

_BINDING_FIELDS = ('transport', 'runner', 'path', 'module', 'command', 'arguments', 'input_fields',
                   'optional_paired_inputs', 'stdin')
_UNRENDERED = object()


def _solution_binding(claim, terminals):
    trigger = _initial_trigger(claim)
    if trigger is None or not terminals:
        return {}
    bypass = _reachable_without(claim, trigger)
    if any(name in bypass for name, _ in terminals):
        return {}
    expected = trigger['expect']
    detail = expected.get('detail', {})
    return {'interface': expected.get('target'),
            **{key: detail[key] for key in _BINDING_FIELDS if key in detail}}


def _status_values(outcomes):
    return {name: next(iter(values)) if len(values) == 1 else sorted(values)
            for name, values in outcomes.items()}


def _solution_outcomes(claim, contract):
    feasible = feasible_terminals(claim)
    if feasible is None:
        return {}
    states = {state['name']: state for state in claim['states']}
    outcomes, complete = {}, not states[claim['initial']]['final']
    modeled_key = None
    for name, index in sorted(feasible):
        expected = states[name]['transitions'][index]['expect']
        outcome = expected.get('outcome')
        detail = expected.get('detail', {})
        fields = detail.keys() & {'exit_code', 'exit_status_class'}
        if expected['kind'] != 'output' or not outcome or not fields:
            complete = False
            continue
        if len(fields) != 1 or (modeled_key is not None and modeled_key not in fields):
            raise ValueError('Solution mixes exit codes and exit status classes')
        modeled_key, = fields
        validate = exit_code if modeled_key == 'exit_code' else exit_status_class
        outcomes.setdefault(outcome, set()).add(validate(detail[modeled_key]))
    facts = {'outcomes': _status_values(outcomes)}
    if modeled_key == 'exit_code':
        classes = {name: {'zero' if code == 0 else 'nonzero' for code in codes}
                   for name, codes in outcomes.items()}
        facts = {'exit_codes': facts['outcomes'], 'outcomes': _status_values(classes)}
    if complete:
        return facts
    return {key: observed for key, observed in facts.items() if key in contract
            and any(value != contract[key].get(name) for name, value in observed.items())}


def _common_checks(details, names):
    facts = {}
    for field, key, expected_type in names:
        values = [detail.get(field) for detail in details]
        if not values or any(type(value) is not expected_type for value in values):
            continue
        if expected_type is list:
            if any(any(not isinstance(item, str) for item in value) for value in values):
                continue
            values = [sorted(value) for value in values]
        else:
            values = [[value] for value in values]
        facts[key] = values[0] if all(value == values[0] for value in values) else values
    return facts


def _reachable_without(claim, blocked):
    states = {state['name']: state['transitions'] for state in claim['states']}
    reached = {claim['initial']}
    queue = [claim['initial']]
    for name in queue:
        for transition in states[name]:
            target = transition['target']
            if transition is not blocked and target not in reached:
                reached.add(target)
                queue.append(target)
    return reached


def _success_outputs(terminals):
    return [(name, transition['expect'].get('detail', {})) for name, transition in terminals
            if transition['expect']['kind'] == 'output'
            and transition['expect'].get('outcome') == 'succeeded']


def _query_checks(claim, edges, successes, component_id):
    effects = [transition for _, transition in edges if transition['expect']['kind'] == 'effect']
    if len(effects) != 1 or not successes:
        return {}
    effect = effects[0]
    expect = effect['expect']
    if expect.get('target') != component_id or expect.get('outcome') != 'succeeded':
        return {}
    bypass = _reachable_without(claim, effect)
    if any(name in bypass for name, _ in successes):
        return {}
    detail = expect.get('detail', {})
    checks = _common_checks([detail], (
        ('match_fields', 'guarantees.match_fields', list),
        ('rank_first', 'guarantees.priority', str),
        ('read_source', 'effects.query_scope', str),
    ))
    for key, observation, obligation in (
        ('guarantees.priority', 'exact_name_match', 'exact_name_first'),
        ('effects.query_scope', 'context_argument', 'supplied_frozen_context'),
    ):
        if key in checks:
            checks[key] = [obligation] if checks[key] == [observation] else {'observed': checks[key]}
    return checks


def _stage_bypasses(claim, stages, order):
    if any(len(stages.get(name, ())) != 1 for name in order):
        return None
    return [after for before, after in pairwise(order)
            if stages[after][0][0] in _reachable_without(claim, stages[before][0][1])]


def _release_checks(claim, edges):
    stages = {}
    for source, edge in edges:
        expect = edge['expect']
        stage = expect.get('detail', {}).get('release_stage')
        if (expect['kind'] == 'effect' and expect.get('outcome') in ('passed', 'succeeded')
                and isinstance(stage, str)):
            stages.setdefault(stage, []).append((source, edge))
    checks = {f'guarantees.{stage}_owner': [owner] for stage, rows in stages.items()
              if len(rows) == 1 and (owner := rows[0][1]['expect'].get('target'))}
    host = _stage_bypasses(claim, stages, ('static', 'functional', 'build'))
    if host is not None:
        checks['guarantees.host_checks_before_build'] = {'bypassed_before': host} if host else [
            'static_then_functional']
    image = _stage_bypasses(claim, stages, ('build', 'verify_image', 'install'))
    if image is not None:
        install = stages['install'][0][1]
        finals = {state['name'] for state in claim['states'] if state['final']}
        reachable = _reachable_without(claim, None)
        successes = [source for source, edge in edges if source in reachable and edge['target'] in finals
                     and edge['expect']['kind'] == 'output'
                     and edge['expect'].get('outcome') in ('completed', 'completed_with_cleanup_pending')]
        bypass = _reachable_without(claim, install)
        possible = [source for source, edge in edges if edge['target'] in finals
                    and edge['expect']['kind'] == 'output'
                    and edge['expect'].get('outcome') is None]
        refs = [stages[stage][0][1]['expect']['detail'].get('image_ref')
                for stage in ('build', 'verify_image', 'install')]
        if image or any(source in bypass for source in successes + possible):
            checks['guarantees.image_checks_before_install'] = {'bypassed_before': image or ['completion']}
        elif all(isinstance(ref, str) and ref.strip() for ref in refs):
            if len(set(refs)) != 1:
                checks['guarantees.image_checks_before_install'] = {'image_refs': refs}
            elif successes:
                checks['guarantees.image_checks_before_install'] = ['exact_candidate']
    return checks


def _first_dispatch(states, starts, detail_fields):
    reached = set(starts)
    queue = list(starts)
    targets = set()
    details = []
    bypassed = False
    for name in queue:
        state = states[name]
        bypassed |= state['final']
        for edge in state['transitions']:
            expect = edge['expect']
            if expect['kind'] == 'effect':
                targets.add(expect.get('target'))
                if detail_fields:
                    details.append(expect.get('detail', {}))
            elif edge['target'] not in reached:
                reached.add(edge['target'])
                queue.append(edge['target'])
    if len(targets) == 1 and None not in targets and not bypassed:
        target, = targets
        if not detail_fields:
            return target
        return {'component': target, **{key: details[0][key] for key in detail_fields
                                       if key in details[0] and all(
                                           key in detail and detail[key] == details[0][key] for detail in details)}}
    return {'targets': sorted(target for target in targets if target is not None),
            'unbound_effect': None in targets, 'terminal_without_dispatch': bypassed}


def _dispatch_facts(workflow, *, detail_fields=()):
    trigger = _initial_trigger(workflow)
    if trigger is None:
        return {}
    states = {state['name']: state for state in workflow['states']}
    routes, generic = {}, []
    for edge in states[trigger['target']]['transitions']:
        expect = edge['expect']
        if expect['kind'] != 'trigger':
            return {}
        detail = expect.get('detail', {})
        command = detail.get('command')
        if isinstance(command, str):
            routes.setdefault(command, []).append(edge['target'])
        elif 'command' not in detail:
            generic.append(edge['target'])
    if not routes:
        return {}
    return {'subcommands': {command: _first_dispatch(states, starts + generic, detail_fields)
                            for command, starts in routes.items()}}


def _outcome_stdout(terminals):
    expected = [edge['expect'] for _, edge in terminals]
    outcomes = {event.get('outcome') for event in expected if event['kind'] == 'output'
                and isinstance(event.get('outcome'), str) and event['outcome'].strip()}
    facts = {}
    for outcome in outcomes:
        events = [event for event in expected if event['kind'] != 'output'
                  or event.get('outcome') in (outcome, None)]
        values = [event.get('detail', {}).get('stdout') for event in events]
        if (all(event['kind'] == 'output' and event.get('outcome') == outcome for event in events)
                and all(isinstance(value, str) and value.strip() for value in values)):
            facts[f'stdout.{outcome}'] = values[0] if len(set(values)) == 1 else values
    return facts


def _workflow_facts(workflow, component_id, *, contract=None):
    if 'states' not in workflow:
        return {}
    edges = [(state['name'], transition) for state in workflow['states']
             for transition in state['transitions']]
    finals = {state['name'] for state in workflow['states'] if state['final']}
    terminals = [row for row in edges if row[1]['target'] in finals]
    successes = _success_outputs(terminals)
    output = _common_checks([detail for _, detail in successes], (
        ('encoding', 'output_format.encoding', str),
        ('output_fields', 'output_fields', list),
        ('record_properties', 'output_format.record_properties', list),
        ('record_role', 'output_format.record_role', str),
    ))
    terminal_details = [edge['expect'].get('detail', {}) if edge['expect']['kind'] == 'output' else {}
                        for _, edge in terminals]
    values = [detail.get('stdout') for detail in terminal_details]
    stdout = ({'stdout': values[0] if all(value == values[0] for value in values) else values}
              if values and all(isinstance(value, str) and value.strip() for value in values) else {})
    return {'action': workflow['action'], **_solution_binding(workflow, terminals), **stdout,
            **_solution_outcomes(workflow, contract or {}), **_outcome_stdout(terminals), **output,
            **_query_checks(workflow, edges, successes, component_id),
            **_release_checks(workflow, edges), **_dispatch_facts(workflow)}


def _add_trace(report, contract, workflow, lean):
    direction = report['directions']['contract_solution']
    comparison = _compare_cases(_trace_cases(contract), workflow, lean)
    direction['facts'].extend(fact for fact in comparison['facts'] if fact['key'] != 'action')
    direction['status'] = verdict([fact['status'] for fact in direction['facts']])


def check_cli_spec(root, component_id, manifest, contract=None, solution=None, *, interface, action=None, lean='lean'):
    """Check the selected CLI binding and supported workflow obligations."""
    model = select_formal_claims(load_boundary_model(root, component_id, manifest, contract, solution), action)
    return compare_cli_spec(model, compile_lean(model), interface=interface, action=action, lean=lean)


def compare_cli_spec(model, compiled, *, interface, action=None, lean='lean', mermaid=_UNRENDERED):
    claims = compiled['claims']
    sources = {role: model[role]['source'] for role in ('manifest', 'contract', 'solution')}
    endpoint = _manifest_endpoint(claims.get('manifest', {}), interface)
    declared = ({'interface': interface,
                 **{key: endpoint[key] for key in (*_BINDING_FIELDS, 'subcommands') if key in endpoint}}
                if isinstance(endpoint, dict) else {})
    if (isinstance(endpoint, dict) and isinstance(fields := endpoint.get('output_fields'), list)
            and all(isinstance(field, str) for field in fields)):
        declared['output_fields'] = sorted(fields)
    if isinstance(endpoint, dict):
        declared.update({key: endpoint[source] for key, source in (('stdin', 'input'), ('stdout', 'output'))
                         if isinstance(endpoint.get(source), str) and endpoint[source].strip()})
    if isinstance(endpoint, dict) and isinstance(endpoint.get('output'), dict):
        output = endpoint['output']
        if output and all(isinstance(k, str) and k.strip() and isinstance(v, str) and v.strip()
                          for k, v in output.items()):
            declared.update({f'stdout.{key}': value for key, value in output.items()})
    contract_claim, workflow = _cli_profiles(claims, interface, action=action)
    contract_facts = {key: value for key, value in contract_claim.items() if key not in ('trace', 'cases', 'invariant')}
    if mermaid is _UNRENDERED:
        mermaid = render_solution(model, claims.get('solution'), action=contract_claim.get('action'))
    solution_facts = _workflow_facts(workflow, model['component_id'], contract=contract_facts)
    report = compare_obligations(sources, {'manifest': declared, 'contract': contract_facts,
                                           'solution': solution_facts}, lean=lean)
    _add_trace(report, contract_claim, workflow, lean)
    _add_manifest_outcomes(report['directions'], {'io': {'server': {interface: endpoint}}},
                           contract_claim, workflow, lean)
    report['status'] = verdict([item['status'] for item in report['directions'].values()])
    uncovered = _uncovered_outcomes(claims.get('manifest', {}).get('boundaries'),
                                    contract_claim, workflow, contract_claim.get('action'))
    report.update(issues=compiled['issues'], unresolved=compiled['unresolved'],
                  uncovered_outcomes=uncovered, mermaid=mermaid)
    if report['status'] == 'matched' and (report['issues'] or report['unresolved'] or uncovered):
        report['status'] = 'unresolved'
    return report_comparison(model, report, action=action)
