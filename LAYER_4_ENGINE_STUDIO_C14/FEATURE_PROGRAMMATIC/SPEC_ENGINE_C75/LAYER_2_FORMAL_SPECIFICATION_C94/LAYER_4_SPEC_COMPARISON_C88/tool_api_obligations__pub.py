"""Project the declared HTTP Tool API behavior onto comparable obligations."""

from ..LAYER_2_SPEC_READING_C83.SPECIFICATION_MODEL_C85._package__shared import (
    http_routes,
)


def manifest_tool_api(api):
    """Return modeled invocation fields and the remaining Tool API declarations."""
    observed = {}
    routes = http_routes(api['routes']) if 'routes' in api else {}
    invoke = next((route for route, name in routes.items() if name == 'invoke'), None)
    if invoke is not None:
        observed['operation'] = [invoke]
    if isinstance(api.get('transport'), str):
        observed['interface.protocol'] = [api['transport']]
    if isinstance(api.get('socket'), str):
        observed['interface.transport'] = [
            'unix_socket' if api['socket'] == 'private Unix socket' else api['socket']]
    for key, name in (('input_format.fields', 'request_fields'),
                      ('error_handling.error_fields', 'failure_fields')):
        value = api.get(name)
        if isinstance(value, list) and all(isinstance(item, str) for item in value):
            if len(value) != len(set(value)):
                raise ValueError('duplicate Manifest ' + name)
            observed[key] = sorted(value)
    extra = {key: value for key, value in api.items()
             if key not in {'transport', 'socket', 'routes', 'request_fields', 'failure_fields'}}
    extra.update({'routes.' + (name or route): route for route, name in routes.items() if name != 'invoke'})
    return observed, extra


def contract_tool_api(claim):
    """Project the Contract operation, named public facts and response outcomes."""
    return {'operation': [claim['operation']], **dict(claim['facts']),
            **{f'outcomes.{name}': [code, envelope] for name, code, envelope in claim['outcomes']}}


def _record(facts, key, value):
    previous = facts.get(key)
    if isinstance(previous, dict) and 'conflicting_values' in previous:
        if value not in previous['conflicting_values']:
            previous['conflicting_values'].append(value)
    elif key in facts and previous != value:
        facts[key] = {'conflicting_values': [previous, value]}
    else:
        facts[key] = value


def _request_facts(detail):
    facts = {}
    for key, field in (('operation', 'operation'), ('interface.protocol', 'protocol'),
                       ('interface.transport', 'transport'), ('interface.request_format', 'request_format')):
        if isinstance(value := detail.get(field), str):
            facts[key] = [value]
    if (isinstance(fields := detail.get('request_fields'), list)
            and all(isinstance(field, str) for field in fields)):
        facts['input_format.fields'] = sorted(fields)
    return facts


def _branch_coverage(facts, branches, expected):
    observed = {}
    for branch in branches:
        for key, value in branch.items():
            observed.setdefault(key, []).append(value)
    for key, rows in observed.items():
        distinct = []
        for value in rows:
            if value not in distinct:
                distinct.append(value)
        value = rows[0]
        mismatch = expected is not None and key in expected and value != expected[key]
        if len(distinct) > 1:
            facts[key] = {'conflicting_values': distinct}
        elif mismatch or len(rows) == len(branches):
            facts[key] = value


def _derived(facts, key, detail, expected, result):
    if all(name in detail and type(detail[name]) is type(value) for name, value in expected.items()):
        observed = {name: detail[name] for name in expected}
        _record(facts, key, [result if observed == expected else observed])


def _effect_facts(detail):
    facts = {}
    types = detail.get('input_types')
    if isinstance(types, dict):
        for name in ('name', 'arguments'):
            if isinstance(types.get(name), str):
                _record(facts, 'input_format.' + name, [types[name]])
        nullable = types.get('nullable_strings')
        if isinstance(nullable, list) and all(isinstance(item, str) for item in nullable):
            _record(facts, 'input_format.nullable_strings', sorted(nullable))
    _derived(facts, 'preconditions.project_binding', detail,
             {'matches_admitted_instance': True}, 'matching_instance')
    _derived(facts, 'preconditions.tool', detail,
             {'tool_enabled': True, 'tool_in_registry': True}, 'enabled_and_in_registry')
    return facts


def _query_facts(claim):
    expected = {'statement_count': 1, 'read_only': True, 'cursor_metadata_only': True,
                'uses_full_submitted_sql': True, 'uses_selected_project': True}
    states = {state['name']: state for state in claim['states']}
    pending, visited, successes = [(claim['initial'], False, True, ())], set(), []
    while pending:
        state = pending.pop()
        if state in visited:
            continue
        visited.add(state)
        name, observed, complete, conflict = state
        for transition in states[name]['transitions']:
            expect = transition['expect']
            detail = expect.get('detail', {})
            observation = ()
            query = (expect['kind'] == 'effect' and expect.get('target') == 'C59'
                     and expect.get('outcome') == 'succeeded')
            if query and isinstance(sql := detail.get('sql'), dict):
                observation = tuple((key, sql[key]) for key, value in expected.items()
                                    if key in sql and type(sql[key]) is type(value))
            mismatch = observation and any(value != expected[key] for key, value in observation)
            next_conflict = conflict or (observation if mismatch else ())
            next_observed = observed or query
            next_complete = complete and (not query or (
                detail.get('operation') == 'run' and dict(observation) == expected))
            target = transition['target']
            if states[target]['final'] and expect['kind'] == 'output' and expect.get('outcome') == 'succeeded':
                successes.append((next_observed and next_complete, next_conflict))
            pending.append((target, next_observed, next_complete, next_conflict))
    conflict = next((value for _, value in successes if value), ())
    if conflict:
        return {'guarantees.query': [dict(conflict)]}
    if successes and all(covered for covered, _ in successes):
        return {'guarantees.query': ['one_complete_read_only_statement']}
    return {}


def _delivery_facts(facts, detail):
    types = detail.get('result_types')
    if isinstance(types, dict):
        for name in ('text', 'value'):
            if isinstance(types.get(name), str):
                _record(facts, 'output_format.' + name, [types[name]])
    delivery = {'delivery_mode': 'requested', 'include_submitted_sql': False}
    observed = {key: detail[key] for key, value in delivery.items()
                if key in detail and type(detail[key]) is type(value)}
    if len(observed) < len(delivery) and any(observed[key] != delivery[key] for key in observed):
        _record(facts, 'guarantees.query_output', [observed])
    _derived(facts, 'guarantees.query_output', detail,
             delivery,
             'requested_delivery_without_submitted_sql')
    _derived(facts, 'effects.query_result', detail, {'retain_result_by': 'query_id'}, 'retained')
    _derived(facts, 'effects.bookmark', detail, {'bookmark_requires_save': True}, 'explicit_save_only')


def _dispatched_states(claim):
    states = {state['name']: state for state in claim['states']}
    pending, visited = [(claim['initial'], False)], set()
    while pending:
        name, dispatched = pending.pop()
        if (name, dispatched) in visited:
            continue
        visited.add((name, dispatched))
        for transition in states[name]['transitions']:
            expect = transition['expect']
            is_dispatch = expect['kind'] == 'effect' and expect.get('target') == 'C59'
            pending.append((transition['target'], dispatched or is_dispatch))
    return {name for name, _ in visited}, {name for name, dispatched in visited if dispatched}


def _unclassified_failure(detail, outcome, errors, outcomes):
    if outcome == 'failed':
        for name in ('invalid_input', 'internal_error'):
            outcomes.setdefault(name, []).append([None, None])
        fields = detail.get('response_fields')
        if isinstance(fields, list) and all(isinstance(field, str) for field in fields):
            _record(errors, 'unclassified', sorted(fields))


def _response_facts(facts, detail, outcome, errors, outcomes):
    name = detail.get('http_outcome')
    if isinstance(value := detail.get('response_format'), str):
        _record(facts, 'interface.response_format', [value])
    if name not in ('success', 'invalid_input', 'internal_error'):
        if outcome == 'succeeded':
            name = 'success'
            outcomes.setdefault(name, []).append([None, None])
        else:
            _unclassified_failure(detail, outcome, errors, outcomes)
            return
    if outcome != ('succeeded' if name == 'success' else 'failed'):
        raise ValueError(f'Solution output classification disagrees with {name}')
    code, envelope = detail.get('status_code'), detail.get('envelope')
    outcomes.setdefault(name, []).append([code if type(code) is int else None,
                                         envelope if isinstance(envelope, str) else None])
    if name == 'internal_error' and isinstance(message := detail.get('message'), str):
        _record(facts, 'error_handling.internal_message', [message])
    fields = detail.get('response_fields')
    if not isinstance(fields, list) or not all(isinstance(field, str) for field in fields):
        return
    if name == 'success':
        _record(facts, 'output_format.result_fields', sorted(fields))
    else:
        _record(errors, name, sorted(fields))


def _terminal_facts(facts, errors, outcomes, detail, outcome, dispatched):
    if (outcome not in ('succeeded', 'failed') or
            detail.get('http_outcome') not in ('success', 'invalid_input', 'internal_error')):
        facts['_unclassified_terminal'] = True
    _response_facts(facts, detail, outcome, errors, outcomes)
    if outcome == 'succeeded':
        _delivery_facts(facts, detail)
    if detail.get('http_outcome') == 'invalid_input':
        if detail.get('provider_dispatched') is False and dispatched:
            raise ValueError('Solution invalid input follows provider dispatch')
        if dispatched:
            detail = {**detail, 'provider_dispatched': True}
        _derived(facts, 'effects.invalid_input_dispatch', detail,
                 {'provider_dispatched': False}, 'none')
    return detail


def _error_facts(facts, errors, expected):
    observed = {}
    for value in errors.values():
        for fields in value.get('conflicting_values', []) if isinstance(value, dict) else [value]:
            _record(observed, 'error_handling.error_fields', fields)
    value = observed.get('error_handling.error_fields')
    if (isinstance(value, dict) or {'invalid_input', 'internal_error'} <= errors.keys()
            or (expected and value is not None and value != expected.get('error_handling.error_fields'))):
        facts.update(observed)


def _response_coverage(facts, responses, expected):
    for key, field, applicable in (
            ('interface.response_format', 'response_format', lambda outcome: True),
            ('output_format.result_fields', 'response_fields', lambda outcome: outcome == 'succeeded'),
            ('error_handling.error_fields', 'response_fields', lambda outcome: outcome == 'failed')):
        details = [detail for detail, outcome in responses if applicable(outcome)]
        missing = any(not isinstance(detail.get(field), str if field == 'response_format' else list)
                      or (field == 'response_fields' and not all(
                          isinstance(item, str) for item in detail[field])) for detail in details)
        value = facts.get(key)
        if missing and not isinstance(value, dict) and (expected is None or value == expected.get(key)):
            facts.pop(key, None)
    dispatch = 'effects.invalid_input_dispatch'
    value = facts.get(dispatch)
    if value == ['none'] and (expected is None or value == expected.get(dispatch, value)) and any(
        detail.get('http_outcome') == 'invalid_input' and detail.get('provider_dispatched') is not False
        for detail, _ in responses
    ):
        del facts[dispatch]


def _delivery_coverage(facts, responses, expected):
    specs = (
        ('output_format.text', ('result_types', 'text'), str, ['string_or_null']),
        ('output_format.value', ('result_types', 'value'), str, ['object']),
        ('guarantees.query_output', ('delivery_mode', 'include_submitted_sql'), (str, bool),
         ['requested_delivery_without_submitted_sql']),
        ('effects.query_result', ('retain_result_by',), (str,), ['retained']),
        ('effects.bookmark', ('bookmark_requires_save',), (bool,), ['explicit_save_only']),
        ('error_handling.internal_message', ('message',), (str,), None))
    for key, fields, types, default in specs:
        details = [detail for detail, outcome in responses
                   if (outcome == 'succeeded' if default is not None else
                       outcome == 'failed' and detail.get('http_outcome') != 'invalid_input')]
        if isinstance(types, type):
            missing = any(not isinstance(detail.get(fields[0]), dict) or
                          not isinstance(detail[fields[0]].get(fields[1]), types) for detail in details)
        else:
            missing = any(any(type(detail.get(field)) is not kind for field, kind in zip(fields, types))
                          for detail in details)
        if default is None and any(detail.get('http_outcome') != 'internal_error' for detail in details):
            missing = True
        value = facts.get(key)
        target = (expected or {}).get(key, default)
        if missing and not isinstance(value, dict) and (value is None or value == target):
            facts.pop(key, None)


def _outcome_facts(facts, outcomes, expected):
    for name, values in outcomes.items():
        conflicts = any(a is not None and b is not None and a != b
                        for i, left in enumerate(values) for right in values[i + 1:]
                        for a, b in zip(left, right))
        if conflicts:
            facts[f'outcomes.{name}'] = {'conflicting_values': values}
        elif all(None not in value for value in values):
            facts[f'outcomes.{name}'] = values[0]
        elif (target := (expected or {}).get(f'outcomes.{name}')) is not None:
            mismatch = next((value for value in values if any(
                actual is not None and actual != wanted for actual, wanted in zip(value, target))), None)
            if mismatch is not None:
                facts[f'outcomes.{name}'] = mismatch


def solution_tool_api(claim, expected=None):
    """Read explicit HTTP observations on a validated Solution workflow."""
    facts, errors, outcomes = _query_facts(claim), {}, {}
    requests, effects, responses = [], [], []
    startup = claim.get('startup', {})
    required = startup.get('required_arguments') if isinstance(startup, dict) else None
    if isinstance(required, list) and all(isinstance(item, str) for item in required):
        _record(facts, 'interface.cli_required', sorted(required))
    reachable, dispatched_states = _dispatched_states(claim)
    finals = {state['name'] for state in claim['states'] if state['final']}
    for state in claim['states']:
        if state['name'] not in reachable:
            continue
        for transition in state['transitions']:
            expect = transition['expect']
            detail = expect.get('detail', {})
            if state['name'] == claim['initial']:
                requests.append(_request_facts(detail) if expect['kind'] == 'trigger' else {})
            if (expect['kind'] == 'effect' and expect.get('target') == 'C59'
                    and expect.get('outcome') == 'succeeded'):
                effects.append(_effect_facts(detail))
            if transition['target'] not in finals:
                continue
            if expect['kind'] == 'output':
                detail = _terminal_facts(facts, errors, outcomes, detail, expect.get('outcome'),
                                         state['name'] in dispatched_states)
                if expect.get('outcome') in ('succeeded', 'failed'):
                    responses.append((detail, expect['outcome']))
            else:
                facts['_unclassified_terminal'] = True
    _branch_coverage(facts, requests, expected)
    _branch_coverage(facts, effects, expected)
    _outcome_facts(facts, outcomes, expected)
    _error_facts(facts, errors, expected)
    _response_coverage(facts, responses, expected)
    _delivery_coverage(facts, responses, expected)
    return facts
