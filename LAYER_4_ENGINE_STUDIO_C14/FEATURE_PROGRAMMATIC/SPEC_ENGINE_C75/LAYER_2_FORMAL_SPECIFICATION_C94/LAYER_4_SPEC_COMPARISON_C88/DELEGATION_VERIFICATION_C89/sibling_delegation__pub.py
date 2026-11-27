"""Compare declared sibling calls with their pinned provider Specs."""

from ...LAYER_1_DIAGNOSTICS_C90._package__shared import verdict
from ....LAYER_1_SOURCE_ADAPTERS_C95._package__shared import (
    SourceError,
    read_source,
)
from ...LAYER_2_SPEC_READING_C83._package__shared import load_boundary_model
from ...LAYER_2_SPEC_READING_C83.SPECIFICATION_MODEL_C85._package__shared import (
    _IN_PROCESS_TRACE_BINDING,
    http_binding,
    http_routes,
    is_http_route,
    select_formal_claims,
)
from ...LAYER_3_LEAN_TRANSLATOR_C84._package__shared import compile_lean
from .._package__shared import compare_delegation
from .._package__shared import (
    _manifest_binding,
    _operation_claims,
    _solution_binding,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.atom_reference__pub import (
    derive_atom_ref,
)


def _call_binding(
    workflow, event, fields, *, caller_action=None, manifest_pin=False
):
    if caller_action is None:
        profiles = workflow.get('operations', {'': workflow}).values()
    else:
        profiles = (_operation_claims(workflow).get(caller_action, {}),)
    transitions = [
        row["expect"]
        for profile in profiles
        for state in profile.get("states", [])
        for row in state["transitions"]
        if row["event"] == event
    ]
    if len(transitions) != 1 or transitions[0]["kind"] != "effect":
        return {}
    expect = transitions[0]
    detail = expect.get('detail', {})
    if detail.get('transport') == 'http':
        try:
            detail = {**detail, **http_binding(detail)}
        except ValueError:
            return {}
    if not isinstance(expect.get("target"), str) or any(
        not isinstance(detail.get(key), str) or not detail[key].strip()
        for key in fields
    ):
        return {}
    result = {
        "component": expect["target"],
        **{key: detail[key] for key in fields},
    }
    if manifest_pin and "manifest" in detail:
        result["manifest"] = detail["manifest"]
    return result


def _matches_route(routes, route):
    if isinstance(route, dict):
        endpoint, name = route.get('endpoint'), route.get('route_name')
        if endpoint and name:
            return routes.get(endpoint) == name
        return (endpoint and endpoint in routes) or (
            name and name in routes.values()
        )
    return route in routes or route in routes.values()


def _declares_client(
    clients, provider_id, interface, route, *, transport=None
):
    if isinstance(clients, dict):
        declarations = clients.items()
    elif isinstance(clients, list):
        declarations = [(None, client) for client in clients]
    else:
        return False
    for name, client in declarations:
        if (
            not isinstance(client, dict)
            or client.get("component") != provider_id
            or client.get("interface", name) != interface
        ):
            continue
        if route is None:
            declared = client.get("transport")
            if (
                transport is None
                or declared == transport
                or (transport == "in_process" and declared is None)
            ):
                return True
            continue
        if client.get('transport') == 'http' and 'routes' in client:
            routes = http_routes(client['routes'])
            if _matches_route(routes, route):
                return True
    return False


def _require_sibling(caller, provider, interface, route, *, transport=None):
    caller_parent = caller["manifest"]["source"]["container_component"]
    provider_parent = provider["manifest"]["source"]["container_component"]
    provider_id = provider["component_id"]
    if (
        caller_parent is None
        or caller_parent != provider_parent
        or caller["component_id"] == provider_id
    ):
        raise ValueError(
            f"{provider_id} is not a declared sibling of {caller['component_id']}"
        )
    boundaries = caller["manifest"]["boundaries"]
    io = boundaries.get("io") if isinstance(boundaries, dict) else None
    clients = io.get("client", []) if isinstance(io, dict) else []
    if not _declares_client(
        clients, provider_id, interface, route, transport=transport
    ):
        raise ValueError(
            f"{caller['component_id']} does not declare client {provider_id}.{interface}"
        )


def _offered_bindings(claims, binding, fields, action):
    contract, solution = (
        claims.get(role, {}) for role in ("contract", "solution")
    )
    if action is not None:
        contract = _operation_claims(contract).get(action, {})
        solution = _operation_claims(solution).get(action, {})
    return {
        'manifest': _manifest_binding(claims.get('manifest', {}), binding),
        'contract': {key: contract[key] for key in fields if key in contract},
        'solution': _solution_binding(solution, fields),
    }


def _load_sibling_caller(root, pins):
    if not isinstance(pins, (tuple, list)) or len(pins) not in (2, 3):
        raise SourceError(
            "solution",
            pins,
            "source_pin",
            "expected Manifest and Solution pins",
        )
    _, source = read_source(root, pins[-1], "solution")
    return load_boundary_model(root, source["container_component"], *pins)


def check_sibling_binding(root, caller_pins, provider_id, provider_pins, *, event,
                          interface, route=None, action=None, caller_action=None, lean='lean'):
    """Compare a selected sibling call on an in-process entry or HTTP route."""
    caller = _load_sibling_caller(root, caller_pins)
    provider = load_boundary_model(root, provider_id, *provider_pins)
    transport = 'in_process' if route is None else 'http'
    _require_sibling(caller, provider, interface, route, transport=transport)
    binding = {'interface': interface, 'transport': transport}
    fields = _IN_PROCESS_TRACE_BINDING
    if route is not None:
        field = 'endpoint' if is_http_route(route) else 'route_name'
        binding[field] = route
        fields = ('interface', 'transport', field)
    caller_compiled = compile_lean(select_formal_claims(caller, caller_action) if caller_action else caller)
    offered = compile_lean(select_formal_claims(provider, action) if action else provider)
    sources = {'caller': caller['solution']['source'],
               **{role: provider[role]['source'] for role in ('manifest', 'contract', 'solution')}}
    offerings = _offered_bindings(offered['claims'], binding, fields, action)
    obligations = {role: {'component': provider_id, **facts} for role, facts in offerings.items()}
    call_fields = fields if action is None else (*fields, 'action')
    selected = _call_binding(caller_compiled['claims'].get('solution', {}), event, call_fields,
                             caller_action=caller_action, manifest_pin=bool(provider.get('embedded_contract')))
    if action is not None and selected.pop('action', None) != action:
        selected = {}
    if "manifest" in selected:
        source = provider["manifest"]["source"]
        ref = derive_atom_ref(
            source["atom_id"], source["version"], source["status"]
        )
        for facts in obligations.values():
            facts['manifest'] = ref
    obligations['caller'] = selected
    report = compare_delegation(sources, obligations, lean=lean)
    if provider.get('embedded_contract') and 'entry' in selected and 'entry' not in offerings['contract']:
        public = {key: value for key, value in selected.items() if key != 'entry'}
        contract_report = compare_delegation(sources, {**obligations, 'caller': public}, lean=lean)
        report['directions']['caller_contract'] = contract_report['directions']['caller_contract']
        report['status'] = verdict([row['status'] for row in report['directions'].values()])
    return {**report, 'event': event, 'declared_client': caller['manifest']['source'],
            'issues': [*caller_compiled['issues'], *offered['issues']],
            'unresolved': [*caller_compiled['unresolved'], *offered['unresolved']],
            'unmodeled': ['Call arguments and response values', 'Provider outcome relied on by the caller']}
