"""Check declared child CLI dispatch without inspecting implementation code."""

from ...LAYER_2_SPEC_READING_C83._package__shared import (
    load_boundary_model,
    load_formal_claim,
)
from ...LAYER_2_SPEC_READING_C83.SPECIFICATION_MODEL_C85._package__shared import normalize_claim
from ...LAYER_3_LEAN_TRANSLATOR_C84._package__shared import compile_lean
from .._package__shared import (
    _cli_profiles,
    _dispatch_facts,
    _initial_trigger,
    _manifest_endpoint,
    _operation_claims,
    _workflow_facts,
    compare_delegation,
)
from .manifest_delegation import (
    CLI_INPUT_FIELDS,
    compare_manifest_call,
    load_manifest_call,
)


def _entry_facts(binding):
    facts = {key: value for key in ('transport', 'runner')
             if isinstance(value := binding.get(key), str) and value.strip()}
    entry = binding.keys() & {'path', 'module'}
    if len(entry) == 1:
        kind, = entry
        value = binding[kind]
        if isinstance(value, str) and value.strip():
            facts['entry_point'] = [kind, value]
    return facts


def _caller_facts(workflow, command, *, manifest=False):
    if 'states' not in workflow:
        return {}, None
    trigger = _initial_trigger(workflow)
    if trigger is None:
        return {}, None
    expect = trigger['expect']
    interface = expect.get('target')
    details = ('manifest', 'action', *CLI_INPUT_FIELDS) if manifest else ()
    targets = _dispatch_facts(workflow, detail_fields=details).get('subcommands', {})
    entry = _entry_facts(expect.get('detail', {}))
    if (command not in targets or not isinstance(interface, str) or not interface.strip()
            or entry.get('transport') != 'cli'
            or (not manifest and entry.keys() != {'transport', 'runner', 'entry_point'})):
        return {}, interface
    dispatch = targets[command]
    facts = dispatch if manifest and 'component' in dispatch else {'component': dispatch}
    return {'command': command, **facts, **entry}, interface


def _offered_facts(binding, command, component):
    if not isinstance(binding, dict):
        return {}
    facts = _entry_facts(binding)
    if 'command' in binding:
        facts.update(command=binding['command'], component=component)
    elif isinstance(subcommands := binding.get('subcommands'), dict):
        facts['command'] = command if command in subcommands else sorted(subcommands)
        if command in subcommands:
            facts['component'] = subcommands[command]
    return facts


def _child_facts(claims, interface, command, component, action):
    contract, workflow = _cli_profiles(claims, interface, action=action)
    solution = _workflow_facts(workflow, component)
    bindings = {
        'manifest': _manifest_endpoint(claims.get('manifest', {}), interface),
        'contract': contract if contract.get('interface') == interface else None,
        'solution': solution if solution.get('interface') == interface else None,
    }
    return {role: _offered_facts(binding, command, component) for role, binding in bindings.items()}


def _manifest_dispatch(child, contract, required, component, interface, command, action):
    selected = action if action is not None else required.get('action')
    profile = _operation_claims(contract).get(selected, {}) if isinstance(selected, str) else {}
    if profile.get('transport') != 'cli' or profile.get('interface') != interface:
        return {}
    declared = _offered_facts(_manifest_endpoint(child, interface), command, component)
    offered = _offered_facts(profile, command, component)
    binding = {**declared, **offered}
    binding.update({key: {'boundary': value, 'contract': offered[key]} for key, value in declared.items()
                    if key in offered and value != offered[key]})
    for key in ('action', *CLI_INPUT_FIELDS):
        if key in profile:
            binding[key] = profile[key]
    if required:
        for key in binding:
            required.setdefault(key, None)
    return binding


def _check_manifest_dispatch(root, parent_manifest, parent_solution, child_id, pin, *,
                             interface, command, caller_action, action, lean):
    caller, workflow, child, contract, issues, unresolved = load_manifest_call(
        root, parent_manifest, parent_solution, child_id, pin)
    if caller_action is not None:
        workflow = _operation_claims(workflow).get(caller_action, {})
    required, caller_interface = _caller_facts(workflow, command, manifest=True)
    offered = _manifest_dispatch(child, contract, required, child_id, interface, command, action) if not issues else {}
    report = compare_manifest_call(caller, child, required, offered, issues, unresolved, lean=lean)
    return {**report, 'caller_interface': caller_interface, 'interface': interface, 'command': command,
            'unmodeled': ['Exact call argument and return values', 'Child guarantees beyond the selected CLI binding']}


def check_cli_child_dispatch(root, parent_solution, child_id, child_pins, *, interface, command,
                             parent_manifest=None, caller_action=None, action=None, lean='lean'):
    """Check the selected command, first dispatch target and shared CLI entry point."""
    if parent_manifest is not None:
        return _check_manifest_dispatch(root, parent_manifest, parent_solution, child_id, child_pins,
                                        interface=interface, command=command, caller_action=caller_action,
                                        action=action, lean=lean)
    if isinstance(child_pins, dict):
        raise TypeError('A black-box child call requires the caller Manifest pin')
    parent_id = parent_solution['container_component']
    _, caller, caller_issues = load_formal_claim(root, parent_id, 'solution', parent_solution)
    child = load_boundary_model(root, child_id, *child_pins)
    if child['manifest']['source']['container_component'] != parent_id or child_id == parent_id:
        raise ValueError(f'{child_id} is not a declared child of {parent_id}')
    workflow, caller_error = normalize_claim('solution', caller, parent_id)
    workflow = workflow or {}
    if caller_action is not None:
        workflow = _operation_claims(workflow).get(caller_action, {})
        if not workflow and not caller_error:
            raise ValueError(f'Unknown caller Solution Action {caller_action!r}')
    compiled = compile_lean(child)
    sources = {'caller': caller['source'],
               **{role: child[role]['source'] for role in ('manifest', 'contract', 'solution')}}
    obligations = _child_facts(compiled['claims'], interface, command, child_id, action)
    obligations['caller'], caller_interface = _caller_facts(workflow, command)
    report = compare_delegation(sources, obligations, lean=lean)
    diagnostics = caller_issues or ([caller_error] if caller_error else [])
    if not obligations['caller'] and not diagnostics:
        diagnostics = ['The selected command has no complete caller entry and first-dispatch binding']
    return {**report, 'caller_interface': caller_interface, 'interface': interface,
            'command': command, 'issues': compiled['issues'],
            'unresolved': [*compiled['unresolved'], *(
                {'source': caller['source'], 'field': 'solution', 'message': message} for message in diagnostics)],
            'unmodeled': ['Arguments and results forwarded by the delegation',
                          'Child guarantees relied on beyond the selected CLI binding']}
