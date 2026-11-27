"""Compare typed HTTP responses and registered checks with workflow observations."""

from ..LAYER_2_SPEC_READING_C83.SPECIFICATION_MODEL_C85._package__shared import (
    HTTP_CHECKS,
    http_routes,
)
from .top_down__pub import compare_obligations


def manifest_http_binding(routes, required):
    routes = http_routes(routes)
    endpoint, name = required.get('endpoint'), required.get('route_name')
    if endpoint in routes:
        observed = {'endpoint': endpoint}
        if routes[endpoint] is not None:
            observed['route_name'] = routes[endpoint]
        return observed
    if name is not None:
        for actual_endpoint, actual_name in routes.items():
            if actual_name == name:
                return {'endpoint': actual_endpoint, 'route_name': name}
        if name in routes:
            return {'route_name': name}
    return {'endpoint' if endpoint is not None else 'route_name': None}


def _observed(values, expected):
    mismatches = [value for value in values if value is not None and value != expected]
    if mismatches:
        return mismatches[0] if all(value == mismatches[0] for value in mismatches) else {
            'conflicting_values': mismatches}
    return values[0] if values and None not in values else None


def _response(detail, expected):
    status, envelope = detail.get('status_code'), detail.get('envelope')
    known_status = isinstance(status, int) and not isinstance(status, bool)
    known_envelope = isinstance(envelope, str)
    if ((known_status and (known_envelope or status != expected[0]))
            or (known_envelope and envelope != expected[1])):
        return [status if known_status else None, envelope if known_envelope else None]
    return None


def _check(detail, name, kind):
    value = detail.get(name)
    if kind is str:
        return [value] if isinstance(value, str) and value.strip() else None
    if isinstance(value, list) and all(isinstance(field, str) and field.strip() for field in value):
        return sorted(value)
    return None


def _workflow_http(workflow, expected, outcomes):
    states = workflow.get('states')
    if not states:
        return {}
    finals = {state['name'] for state in states if state['final']}
    initial = next(state for state in states if state['name'] == workflow['initial'])
    entries = [edge['expect'] for edge in initial['transitions']]
    exits = [edge['expect'] for state in states for edge in state['transitions'] if edge['target'] in finals]
    guards = [edge['expect'] for state in states for edge in state['transitions']]
    if any(guard.get('bind') or guard.get('same_as') for guard in guards):
        return {}
    request = [event.get('detail', {}) if event['kind'] == 'trigger' else {} for event in entries]
    response = [event.get('detail', {}) if event['kind'] == 'output' else {} for event in exits]
    observations = {'request': request, 'response': response}
    facts = {key: _observed([_check(detail, field, kind) for detail in observations[phase]], expected[key])
             for key, (phase, field, kind) in HTTP_CHECKS.items() if key in expected}
    facts['action'] = workflow.get('action')
    for name, _, _ in outcomes:
        key = f'outcomes.{name}'
        possible = [event for event in exits if event['kind'] != 'output'
                    or event.get('outcome') == name or not (event.get('outcome') or '').strip()]
        facts[key] = _observed([
            _response(event.get('detail', {}), expected[key])
            if event['kind'] == 'output' and event.get('outcome') == name else None
            for event in possible
        ], expected[key])
    return {key: value for key, value in facts.items() if value is not None}


def compare_http_workflow(sources, contract, workflow, lean):
    outcomes = contract['outcomes']
    expected = {'action': contract['action'], **dict(contract['facts'])}
    expected.update({f'outcomes.{name}': [status, envelope] for name, status, envelope in outcomes})
    if 'request_schema' in contract:
        expected['request_schema'] = contract['request_schema']
        expected.update({f'response_schemas.{name}': schema for name, schema in contract['response_schemas'].items()})
    return compare_obligations(sources, {'manifest': {}, 'contract': expected,
                                         'solution': _workflow_http(workflow, expected, outcomes)},
                               lean=lean)['directions']['contract_solution']
