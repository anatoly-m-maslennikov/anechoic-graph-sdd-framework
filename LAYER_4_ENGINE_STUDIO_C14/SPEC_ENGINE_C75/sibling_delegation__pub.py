"""Compare declared sibling calls with their pinned provider Specs."""

from .boundary_model import load_boundary_model
from .contract_model__pub import _IN_PROCESS_TRACE_BINDING
from .lean_spec__pub import compile_lean
from .top_down__pub import compare_delegation
from .trace_spec__pub import _manifest_binding, _operation_claims, _solution_binding


def _call_binding(workflow, event, fields):
    profiles = workflow.get('operations', {'': workflow})
    transitions = [row['expect'] for profile in profiles.values() for state in profile.get('states', [])
                   for row in state['transitions'] if row['event'] == event]
    if len(transitions) != 1 or transitions[0]['kind'] != 'effect':
        return {}
    expect = transitions[0]
    detail = expect.get('detail', {})
    if (not isinstance(expect.get('target'), str)
            or any(not isinstance(detail.get(key), str) or not detail[key].strip()
                   for key in fields)):
        return {}
    return {'component': expect['target'], **{key: detail[key] for key in fields}}


def _declares_client(clients, provider_id, interface, route):
    if isinstance(clients, dict):
        clients = [{'interface': name, **client} for name, client in clients.items() if isinstance(client, dict)]
    if not isinstance(clients, list):
        return False
    for client in clients:
        if (not isinstance(client, dict) or client.get('component') != provider_id
                or client.get('interface') != interface):
            continue
        if route is None:
            return True
        routes = client.get('routes')
        if client.get('transport') == 'http' and isinstance(routes, (list, dict)) and route in routes:
            return True
    return False


def _require_sibling(caller, provider, interface, route):
    caller_parent = caller['manifest']['source']['container_component']
    provider_parent = provider['manifest']['source']['container_component']
    provider_id = provider['component_id']
    if caller_parent is None or caller_parent != provider_parent or caller['component_id'] == provider_id:
        raise ValueError(f'{provider_id} is not a declared sibling of {caller["component_id"]}')
    boundaries = caller['manifest']['boundaries']
    io = boundaries.get('io') if isinstance(boundaries, dict) else None
    clients = io.get('client', []) if isinstance(io, dict) else []
    if not _declares_client(clients, provider_id, interface, route):
        raise ValueError(f'{caller["component_id"]} does not declare client {provider_id}.{interface}')


def _offered_bindings(claims, binding, fields, action):
    contract, solution = (claims.get(role, {}) for role in ('contract', 'solution'))
    if action is not None:
        contract = _operation_claims(contract).get(action, {})
        solution = _operation_claims(solution).get(action, {})
    return {
        'manifest': _manifest_binding(claims.get('manifest', {}), binding),
        'contract': {key: contract[key] for key in fields if key in contract},
        'solution': _solution_binding(solution, fields),
    }


def check_sibling_binding(root, caller_pins, provider_id, provider_pins, *, event,
                          interface, route=None, action=None, lean='lean'):
    """Compare a selected sibling call on an in-process entry or HTTP route."""
    caller_id = caller_pins[2]['container_component']
    caller = load_boundary_model(root, caller_id, *caller_pins)
    provider = load_boundary_model(root, provider_id, *provider_pins)
    _require_sibling(caller, provider, interface, route)
    binding = {'interface': interface, 'transport': 'in_process' if route is None else 'http'}
    if route is not None:
        binding['route'] = route
    fields = _IN_PROCESS_TRACE_BINDING if route is None else ('interface', 'transport', 'route')
    caller_compiled, offered = compile_lean(caller), compile_lean(provider)
    sources = {'caller': caller['solution']['source'],
               **{role: provider[role]['source'] for role in ('manifest', 'contract', 'solution')}}
    offerings = _offered_bindings(offered['claims'], binding, fields, action)
    obligations = {role: {'component': provider_id, **facts} for role, facts in offerings.items()}
    call_fields = fields if action is None else (*fields, 'action')
    selected = _call_binding(caller_compiled['claims'].get('solution', {}), event, call_fields)
    if action is not None and selected.pop('action', None) != action:
        selected = {}
    obligations['caller'] = selected
    report = compare_delegation(sources, obligations, lean=lean)
    return {**report, 'event': event, 'declared_client': caller['manifest']['source'],
            'issues': [*caller_compiled['issues'], *offered['issues']],
            'unresolved': [*caller_compiled['unresolved'], *offered['unresolved']],
            'unmodeled': ['Call arguments and response values', 'Provider outcome relied on by the caller']}
