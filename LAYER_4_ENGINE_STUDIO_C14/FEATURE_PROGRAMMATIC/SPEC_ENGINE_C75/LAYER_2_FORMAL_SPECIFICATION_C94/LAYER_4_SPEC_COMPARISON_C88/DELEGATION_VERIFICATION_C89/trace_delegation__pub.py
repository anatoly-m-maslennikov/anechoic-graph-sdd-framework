"""Compare a delegated outcome with the provider's pinned Specs."""

from ...LAYER_2_SPEC_READING_C83._package__shared import (
    load_boundary_model,
    load_formal_claim,
)
from ...LAYER_2_SPEC_READING_C83.SPECIFICATION_MODEL_C85._package__shared import (
    HTTP_BINDING_INPUTS,
    http_binding,
    json_equal,
    normalize_claim,
    outcome_cases,
    select_formal_claims,
)
from ...LAYER_3_LEAN_TRANSLATOR_C84._package__shared import compile_lean
from .._package__shared import (
    _manifest_binding,
    _manifest_contract,
    _operation_claims,
    compare_delegation,
    compare_trace_workflow,
)
from .manifest_delegation import (
    CLI_INPUT_FIELDS,
    compare_manifest_call,
    load_manifest_call,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.atom_reference__pub import derive_atom_ref
from .sibling_delegation__pub import _load_sibling_caller, _offered_bindings, _require_sibling

_TRACE_BINDING = {'interface', 'transport', 'entry', 'route', 'operation'}
_CLI_BINDING = {'command', *CLI_INPUT_FIELDS}
_CALL_BINDING = _TRACE_BINDING | _CLI_BINDING | HTTP_BINDING_INPUTS


def _call_detail(expect, manifest):
    detail = expect.get('detail', {})
    if not manifest or detail.get('transport') != 'http':
        return detail
    try:
        binding = http_binding(detail)
    except ValueError:
        return {}
    return {**{key: detail[key] for key in detail.keys() - HTTP_BINDING_INPUTS}, **binding}


def _binding_fields(transport, manifest, manifest_pin):
    fields = (_TRACE_BINDING | HTTP_BINDING_INPUTS
              if transport == 'http' else _TRACE_BINDING)
    if manifest or manifest_pin:
        fields = fields | {'manifest'}
        if manifest and transport == 'cli':
            fields |= _CLI_BINDING
        elif manifest and transport == 'http':
            fields.add('request_fields')
    return fields


def _requirement(workflow, event, interface=None, *, caller_action=None, manifest=False, manifest_pin=False, sibling=False):
    if caller_action is None:
        operations = workflow.get('operations', {'': workflow}).values()
    else:
        operations = (_operation_claims(workflow).get(caller_action, {}),)
    selected = [row['expect'] for model in operations for state in model.get('states', [])
                for row in state['transitions'] if row['event'] == event]
    if interface is not None and any(
        expect.get("detail", {}).get("interface") != interface
        for expect in selected
    ):
        raise ValueError(
            f"The selected event does not use interface {interface}"
        )
    if (
        not selected
        or selected[0]["kind"] != "effect"
        or any(not json_equal(expect, selected[0]) for expect in selected[1:])
    ):
        return {}
    expect = selected[0]
    detail = _call_detail(expect, manifest or sibling)
    names = {key: detail.get(key) for key in ('component', 'action', 'output')}
    effect = (expect.get('target'), expect.get('outcome'))
    if not all(isinstance(value, str) and value.strip() for value in (*effect, *names.values())):
        return {}
    transport = detail.get('transport')
    if sibling and transport is None and 'entry' in detail:
        detail = {**detail, 'transport': 'in_process'}
        transport = 'in_process'
    fields = _binding_fields(transport, manifest, manifest_pin)
    qualifiers = {key: value for key, value in detail.items() if key not in fields and key not in names}
    if qualifiers:
        effect = (*effect, qualifiers)
    metadata = {key: detail[key] for key in fields & detail.keys()} if manifest else (
        {'manifest': detail['manifest']} if manifest_pin and 'manifest' in detail else {})
    request_fields = metadata.get('request_fields')
    if isinstance(request_fields, list) and all(isinstance(field, str) for field in request_fields):
        metadata['request_fields'] = sorted(request_fields)
    metadata.update({key: detail[key] for key in ('interface', 'transport', 'entry', 'endpoint', 'route_name')
                     if sibling and transport is not None and key in detail})
    return {**names, 'effect': effect, **metadata}


def _declared_outcome(cases, required, lean='lean'):
    for case in cases:
        if case.get('action') != required['action'] or case.get('output') != required['output']:
            continue
        facts = {'action': case['action'], 'output': case['output']}
        if any(tuple(effect[:2]) == tuple(required['effect'][:2]) for effect in case.get('must_effect', ())):
            if len(required['effect']) == 2 or _manifest_contract(
                    [{**facts, 'must_effect': [required['effect']]}], case, lean)['status'] == 'matched':
                facts['effect'] = required['effect']
            else:
                facts['effect'] = None
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
    bound = declared == interface
    initial = next((state for state in workflow.get('states', ())
                    if state['name'] == workflow.get('initial')), None)
    for row in initial.get('transitions', ()) if initial else ():
        expect = row['expect']
        detail = expect.get('detail', {})
        if (expect.get('kind') == 'trigger' and isinstance(expect.get('target'), str)
                and (declared is not None or detail.get('transport') in ('in_process', 'http', 'cli'))):
            if expect['target'] != interface:
                raise ValueError(f'The provider Solution does not use interface {interface}')
            bound = True
    return bound


def _offerings(compiled, child, required, lean, interface=None):
    if not required:
        return dict.fromkeys(('manifest', 'contract', 'solution'))
    claims = compiled['claims']
    cases, _ = outcome_cases(claims.get('manifest', {}).get('boundaries'))
    contract, workflow = (claims.get(role, {}) for role in ('contract', 'solution'))
    if 'operations' in contract:
        contract = contract['operations'].get(required['action'], {})
    if 'operations' in workflow:
        workflow = workflow['operations'].get(required['action'], {})
    if interface is not None:
        bound = _require_provider_interface(contract, workflow, interface)
        if required['action'] != interface and not bound:
            return dict.fromkeys(('manifest', 'contract', 'solution'), {})
    if (contract.get('transport') != 'cli' and contract.get('profile') != 'http'
            and not any(language == 'python trace' for language, _ in child['contract']['claims'])):
        contract = {}
    trace = {'action': contract.get('action'), **contract['trace']} if 'trace' in contract else contract
    offered = _declared_outcome(contract.get('cases', [trace]), required, lean)
    if (contract.get('action') == required['action']
            and required['effect'][0] in contract.get('invariant', {}).get('forbid_effect', ())):
        offered.update(action=required['action'], effect='forbidden')
    manifest = _declared_outcome(cases, required, lean)
    if not cases and child.get('embedded_contract'):
        manifest = offered
    return {'manifest': manifest,
            'contract': offered,
            'solution': _modeled_outcome(workflow, required, lean)}


def _add_outcome_binding(provider, compiled, required, obligations):
    if 'transport' not in required:
        return False
    fields = tuple(key for key in ('interface', 'transport', 'entry', 'endpoint', 'route_name') if key in required)
    binding = _offered_bindings(compiled['claims'], required, fields, required['action'])
    for role, facts in binding.items():
        obligations[role].update(
            {key: facts[key] for key in fields if key in facts}
        )
    private_fields = (
        {key for key in fields if key not in binding["contract"]}
        if provider.get("embedded_contract")
        else set()
    )
    obligations["contract"].update(
        {key: required[key] for key in private_fields}
    )
    return private_fields


def _check_outcome(caller, caller_id, caller_issues, provider, *, event, lean, interface=None, caller_action=None):
    workflow, error = normalize_claim('solution', caller, caller_id)
    required = _requirement(workflow or {}, event, interface, caller_action=caller_action, manifest_pin=True,
                            sibling=interface is not None)
    selected_provider = select_formal_claims(provider, required['action']) if required.get('action') else provider
    compiled = compile_lean(selected_provider)
    sources = {
        "caller": caller["source"],
        **{
            role: provider[role]["source"]
            for role in ("manifest", "contract", "solution")
        },
    }
    obligations = {
        role: {"component": provider["component_id"], **(facts or {})}
        for role, facts in _offerings(
            compiled, provider, required, lean, interface
        ).items()
    }
    if "manifest" in required:
        source = provider["manifest"]["source"]
        ref = derive_atom_ref(
            source["atom_id"], source["version"], source["status"]
        )
        for facts in obligations.values():
            facts['manifest'] = ref
    private_fields = interface is not None and _add_outcome_binding(provider, compiled, required, obligations)
    obligations['caller'] = required
    diagnostics = caller_issues or ([error] if error else [])
    if not required and not diagnostics:
        diagnostics = ['The selected effect has no complete provider action and output binding']
    report = compare_delegation(sources, obligations, lean=lean)
    if private_fields:
        facts = report['directions']['caller_contract']['facts']
        report['directions']['caller_contract']['facts'] = [fact for fact in facts if fact['key'] not in private_fields]
    return {**report, 'event': event, 'issues': compiled['issues'],
            'unresolved': [*compiled['unresolved'], *(
                {'source': caller['source'], 'field': 'solution', 'message': issue} for issue in diagnostics)],
            'unmodeled': ['Call arguments and exact returned values']}


def _manifest_outcome(child, contract, required, lean):
    offered = {'component': child['fields']['component_id']}
    if not required:
        return offered
    profile = _operation_claims(contract).get(required['action'], {})
    trace = {'action': required['action'], **profile['trace']} if 'trace' in profile else profile
    offered.update(_declared_outcome(profile.get('cases', [trace]), required, lean))
    if required['effect'][0] in profile.get('invariant', {}).get('forbid_effect', ()):
        offered['effect'] = 'forbidden'
    binding = {key: profile[key] for key in _CALL_BINDING & profile.keys()}
    request_fields = dict(profile.get('facts', ())).get('input_format.fields')
    if request_fields is not None:
        binding['request_fields'] = request_fields
    if profile.get('transport') in ('http', 'in_process'):
        for key, value in _manifest_binding(child, profile).items():
            if key in binding and value != binding[key]:
                binding[key] = {'boundary': value, 'contract': binding[key]}
    for key in binding:
        required.setdefault(key, None)
    return {**offered, **binding}


def _check_manifest_outcome(root, parent_manifest, parent_solution, child_id, pin, *, event, caller_action, lean):
    caller, workflow, child, contract, issues, unresolved = load_manifest_call(
        root, parent_manifest, parent_solution, child_id, pin
    )
    required = _requirement(
        workflow, event, caller_action=caller_action, manifest=True
    )
    offered = (
        _manifest_outcome(child, contract, required, lean)
        if not issues
        else {}
    )
    report = compare_manifest_call(
        caller, child, required, offered, issues, unresolved, lean=lean
    )
    return {
        **report,
        "event": event,
        "unmodeled": ["Exact call argument and return values"],
    }


def check_child_outcome(root, parent_solution, child_id, child_pins, *, event, parent_manifest=None,
                        caller_action=None, lean='lean'):
    """Check that the selected child outcome guarantees the effect the parent relies on."""
    if parent_manifest is not None:
        return _check_manifest_outcome(root, parent_manifest, parent_solution, child_id, child_pins,
                                       event=event, caller_action=caller_action, lean=lean)
    if isinstance(child_pins, dict):
        raise TypeError('A black-box child call requires the caller Manifest pin')
    parent_id = parent_solution['container_component']
    _, caller, caller_issues = load_formal_claim(root, parent_id, 'solution', parent_solution)
    child = load_boundary_model(root, child_id, *child_pins)
    if child['manifest']['source']['container_component'] != parent_id or child_id == parent_id:
        raise ValueError(f'{child_id} is not a declared child of {parent_id}')
    return _check_outcome(caller, parent_id, caller_issues, child, event=event, lean=lean,
                          caller_action=caller_action)


def check_sibling_outcome(root, caller_pins, provider_id, provider_pins, *, event, interface, caller_action=None,
                          lean='lean'):
    """Check the required outcome of a declared sibling client."""
    caller = _load_sibling_caller(root, caller_pins)
    caller_id = caller['component_id']
    provider = load_boundary_model(root, provider_id, *provider_pins)
    workflow, _ = normalize_claim("solution", caller["solution"], caller_id)
    required = _requirement(
        workflow or {}, event, caller_action=caller_action, sibling=True
    )
    route = {
        key: required[key]
        for key in ("endpoint", "route_name")
        if key in required
    } or None
    _require_sibling(
        caller, provider, interface, route, transport=required.get("transport")
    )
    boundaries = provider["manifest"]["boundaries"]
    io = boundaries.get("io") if isinstance(boundaries, dict) else None
    servers = io.get("server") if isinstance(io, dict) else None
    if not isinstance(servers, dict) or interface not in servers:
        raise ValueError(f'{provider_id} does not declare server {interface}')
    issues = [issue for issue in caller['issues'] if issue.startswith('solution:')]
    report = _check_outcome(caller['solution'], caller_id, issues, provider, event=event, lean=lean,
                            interface=interface, caller_action=caller_action)
    return {**report, 'declared_client': caller['manifest']['source']}
