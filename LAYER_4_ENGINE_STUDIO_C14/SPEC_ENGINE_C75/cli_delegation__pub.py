"""Check declared child CLI dispatch without inspecting implementation code."""

from .boundary_model import load_boundary_model, load_formal_claim
from .cli_spec__pub import _cli_profiles, _dispatch_facts, _initial_trigger, _manifest_endpoint, _workflow_facts
from .lean_spec__pub import _claim, compile_lean
from .top_down__pub import compare_delegation

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


def _caller_facts(workflow, command):
    if 'states' not in workflow:
        return {}, None
    trigger = _initial_trigger(workflow)
    if trigger is None:
        return {}, None
    expect = trigger['expect']
    interface = expect.get('target')
    targets = _dispatch_facts(workflow).get('subcommands', {})
    entry = _entry_facts(expect.get('detail', {}))
    if (command not in targets or not isinstance(interface, str) or not interface.strip()
            or entry.get('transport') != 'cli' or entry.keys() != {'transport', 'runner', 'entry_point'}):
        return {}, interface
    return {'command': command, 'component': targets[command], **entry}, interface


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


def _child_facts(claims, interface, command, component):
    contract, workflow = _cli_profiles(claims, interface)
    solution = _workflow_facts(workflow, component)
    bindings = {
        'manifest': _manifest_endpoint(claims.get('manifest', {}), interface),
        'contract': contract if contract.get('interface') == interface else None,
        'solution': solution if solution.get('interface') == interface else None,
    }
    return {role: _offered_facts(binding, command, component) for role, binding in bindings.items()}


def check_cli_child_dispatch(root, parent_solution, child_id, child_pins, *, interface, command, lean='lean'):
    """Check the selected command, first dispatch target and shared CLI entry point."""
    parent_id = parent_solution['container_component']
    _, caller, caller_issues = load_formal_claim(root, parent_id, 'solution', parent_solution)
    child = load_boundary_model(root, child_id, *child_pins)
    if child['manifest']['source']['container_component'] != parent_id or child_id == parent_id:
        raise ValueError(f'{child_id} is not a declared child of {parent_id}')
    workflow, _, caller_error = _claim('solution', caller, parent_id)
    compiled = compile_lean(child)
    sources = {'caller': caller['source'],
               **{role: child[role]['source'] for role in ('manifest', 'contract', 'solution')}}
    obligations = _child_facts(compiled['claims'], interface, command, child_id)
    obligations['caller'], caller_interface = _caller_facts(workflow or {}, command)
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
