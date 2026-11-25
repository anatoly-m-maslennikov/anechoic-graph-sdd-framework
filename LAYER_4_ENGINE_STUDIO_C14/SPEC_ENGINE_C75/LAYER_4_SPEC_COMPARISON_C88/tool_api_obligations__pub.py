"""Project the declared HTTP Tool API behavior onto comparable obligations."""


def manifest_tool_api(api):
    """Return modeled invocation fields and the remaining Tool API declarations."""
    observed = {}
    routes = api.get('routes')
    if isinstance(routes, dict) and isinstance(routes.get('invoke'), str):
        observed['operation'] = [routes['invoke']]
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
    if isinstance(routes, dict):
        extra.update({'routes.' + key: value for key, value in routes.items() if key != 'invoke'})
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


def _request_facts(facts, detail):
    for key, field in (('operation', 'operation'), ('interface.protocol', 'protocol'),
                       ('interface.transport', 'transport'), ('interface.request_format', 'request_format')):
        if isinstance(value := detail.get(field), str):
            _record(facts, key, [value])
    if (isinstance(fields := detail.get('request_fields'), list)
            and all(isinstance(field, str) for field in fields)):
        _record(facts, 'input_format.fields', sorted(fields))


def _derived(facts, key, detail, expected, result):
    if all(name in detail and type(detail[name]) is type(value) for name, value in expected.items()):
        observed = {name: detail[name] for name in expected}
        _record(facts, key, [result if observed == expected else observed])


def _effect_facts(facts, detail):
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


def _query_facts(claim):
    expected = {'statement_count': 1, 'read_only': True, 'cursor_metadata_only': True}
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
            sql = detail.get('sql')
            observation = ()
            query = (expect['kind'] == 'effect' and expect.get('target') == 'C59'
                     and expect.get('outcome') == 'succeeded')
            if query and isinstance(sql, dict):
                observation = tuple((key, sql[key]) for key, value in expected.items()
                                    if key in sql and type(sql[key]) is type(value))
            mismatch = observation and any(value != expected[key] for key, value in observation)
            next_conflict = conflict or (observation if mismatch else ())
            next_observed = observed or query
            next_complete = complete and (not query or dict(observation) == expected)
            target = transition['target']
            if (states[target]['final'] and expect['kind'] == 'output'
                    and expect.get('outcome') == 'succeeded'):
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
    _derived(facts, 'guarantees.query_output', detail,
             {'delivery_mode': 'requested', 'include_submitted_sql': False},
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
    return {name for name, dispatched in visited if dispatched}


def _response_facts(facts, detail, outcome, errors):
    name = detail.get('http_outcome')
    if name not in ('success', 'invalid_input', 'internal_error'):
        return
    if outcome != ('succeeded' if name == 'success' else 'failed'):
        raise ValueError(f'Solution output classification disagrees with {name}')
    code, envelope = detail.get('status_code'), detail.get('envelope')
    if type(code) is int and isinstance(envelope, str):
        _record(facts, f'outcomes.{name}', [code, envelope])
    if isinstance(value := detail.get('response_format'), str):
        _record(facts, 'interface.response_format', [value])
    if name == 'internal_error' and isinstance(message := detail.get('message'), str):
        _record(facts, 'error_handling.internal_message', [message])
    fields = detail.get('response_fields')
    if not isinstance(fields, list) or not all(isinstance(field, str) for field in fields):
        return
    if name == 'success':
        _record(facts, 'output_format.result_fields', sorted(fields))
    else:
        _record(errors, name, sorted(fields))


def _terminal_facts(facts, errors, detail, outcome, dispatched):
    _response_facts(facts, detail, outcome, errors)
    if detail.get('http_outcome') == 'success':
        _delivery_facts(facts, detail)
    if detail.get('http_outcome') == 'invalid_input':
        if detail.get('provider_dispatched') is False and dispatched:
            raise ValueError('Solution invalid input follows provider dispatch')
        _derived(facts, 'effects.invalid_input_dispatch', detail,
                 {'provider_dispatched': False}, 'none')


def solution_tool_api(claim):
    """Read explicit HTTP observations on a validated Solution workflow."""
    facts, errors = _query_facts(claim), {}
    startup = claim.get('startup', {})
    required = startup.get('required_arguments') if isinstance(startup, dict) else None
    if isinstance(required, list) and all(isinstance(item, str) for item in required):
        _record(facts, 'interface.cli_required', sorted(required))
    dispatched_states = _dispatched_states(claim)
    finals = {state['name'] for state in claim['states'] if state['final']}
    for state in claim['states']:
        for transition in state['transitions']:
            expect = transition['expect']
            detail = expect.get('detail', {})
            if expect['kind'] == 'trigger' and state['name'] == claim['initial']:
                _request_facts(facts, detail)
            if (expect['kind'] == 'effect' and expect.get('target') == 'C59'
                    and expect.get('outcome') == 'succeeded'):
                _effect_facts(facts, detail)
            if expect['kind'] == 'output' and transition['target'] in finals:
                _terminal_facts(facts, errors, detail, expect.get('outcome'), state['name'] in dispatched_states)
    if {'invalid_input', 'internal_error'} <= errors.keys() or any(
            isinstance(value, dict) for value in errors.values()):
        for value in errors.values():
            for fields in value.get('conflicting_values', []) if isinstance(value, dict) else [value]:
                _record(facts, 'error_handling.error_fields', fields)
    return facts
