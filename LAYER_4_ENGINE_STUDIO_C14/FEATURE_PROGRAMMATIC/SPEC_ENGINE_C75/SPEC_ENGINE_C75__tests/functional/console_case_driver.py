"""Extract executable inputs and observations from pinned Console Draft claims."""
import json
import sys
from pathlib import Path

from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_2_SPEC_READING_C83._package__shared import load_boundary_model
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_3_LEAN_TRANSLATOR_C84._package__shared import compile_lean


def pinned_console_claims(root):
    base = '_anechoic_anechoic/LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/'
    manifest = {'path': base + '01_draft/AN-S-3060@12-draft-SPEC-COMPONENT_MANIFEST--declare-iwe-console-frontend.md',
                'atom_id': 'AN-S-3060', 'version': 12, 'status': 'draft', 'container_component': 'C43'}
    solution = {'path': base + 'FEATURE_IWE_CONSOLE_FRONTEND_C46/01_draft/AN-S-5037@1-draft-DES-SOLUTION--render-console-view.md',
                'atom_id': 'AN-S-5037', 'version': 1, 'status': 'draft', 'container_component': 'C46'}
    model = load_boundary_model(root, 'C46', manifest, solution=solution)
    compiled = compile_lean(model)
    if model['issues'] or compiled['issues']:
        raise ValueError(f"Invalid C46 claims: {model['issues'] + compiled['issues']}")
    return compiled['claims']


def pinned_patchbay_claims(root):
    base = '_anechoic_anechoic/LAYER_4_ENGINE_STUDIO_C14/'
    manifest = {'path': base + '01_draft/AN-S-3044@68-draft-SPEC-COMPONENT_MANIFEST--declare-mcp.md',
                'atom_id': 'AN-S-3044', 'version': 68, 'status': 'draft', 'container_component': 'C14'}
    solution = {'path': base + 'MCP_PATCHBAY_C21/01_draft/AN-S-5044@1-draft-DES-SOLUTION--forward-a-console-document.md',
                'atom_id': 'AN-S-5044', 'version': 1, 'status': 'draft', 'container_component': 'C21'}
    model = load_boundary_model(root, 'C21', manifest, solution=solution)
    compiled = compile_lean(model)
    if model['issues'] or compiled['issues']:
        raise ValueError(f"Invalid C21 claims: {model['issues'] + compiled['issues']}")
    return compiled['claims']


def _outputs_after(states, start):
    pending = [start]
    visited = set()
    outputs = set()
    while pending:
        name = pending.pop()
        if name in visited:
            continue
        visited.add(name)
        for edge in states[name]:
            if edge['expect']['kind'] == 'output':
                outputs.add(edge['expect']['outcome'])
            else:
                pending.append(edge['target'])
    return outputs


def _case_inputs(action, states, initial, selecting):
    inputs = {}
    for edge in states[initial]:
        if not selecting and edge['expect']['kind'] != 'trigger':
            continue
        for name in _outputs_after(states, edge['target']):
            if selecting and edge['event'] != name:
                raise ValueError(f"{action}: binding {edge['event']} leads to {name}")
            if name in inputs:
                raise ValueError(f'{action}: ambiguous input for {name}')
            inputs[name] = edge['expect'].get('detail', {})
    return inputs


def observable_cases(claims, action, selecting=False):
    contract = claims['contract'] if selecting else claims['contract']['operations'][action]
    workflow = claims['solution'] if selecting else claims['solution']['operations'][action]
    cases = contract['cases']
    if selecting and (contract['action'] != action or workflow['action'] != action):
        raise ValueError(f'{action}: claim actions differ')
    states = {state['name']: state['transitions'] for state in workflow['states']}
    initial = workflow['initial']
    binding = None
    if selecting:
        if len(states[initial]) != 1 or states[initial][0]['target'] != 'selecting':
            raise ValueError(f'{action}: expected one trigger to selecting')
        trigger = states[initial][0]
        if trigger['expect']['kind'] != 'trigger' or trigger['expect']['target'] != 'workbench_http':
            raise ValueError(f'{action}: expected workbench_http trigger')
        binding = trigger['expect']['detail']
        if any(binding[key] != contract[key] for key in ('endpoint', 'route_name', 'transport')):
            raise ValueError(f'{action}: contract and trigger bindings differ')
        initial = 'selecting'
    inputs = _case_inputs(action, states, initial, selecting)
    outputs = {edge['expect']['outcome'] for transitions in states.values() for edge in transitions
               if edge['expect']['kind'] == 'output'}
    if outputs != {case['output'] for case in cases}:
        raise ValueError(f'{action}: contract and workflow outputs differ')
    for case in cases:
        name = case['output']
        if name not in inputs:
            raise ValueError(f'{action}: no input reaches {name}')
        obligations = {key: case.get(key, []) for key in ('must_effect', 'forbid_effect', 'must_precede', 'same_values')}
        required = obligations['must_effect']
        result = {'name': name, 'input': inputs[name], 'effect': required[-1] if required else None, **obligations}
        if binding is not None:
            result['binding'] = binding
        yield result


def main():
    root = Path(__file__).resolve().parents[5]
    actions = sys.argv[1:]
    output = {}
    if any(action != 'forward_console_document' for action in actions):
        claims = pinned_console_claims(root)
        output.update({action: list(observable_cases(claims, action)) for action in actions
                       if action != 'forward_console_document'})
    if 'forward_console_document' in actions:
        claims = pinned_patchbay_claims(root)
        output['forward_console_document'] = list(observable_cases(claims, 'forward_console_document', True))
    print(json.dumps(output))


if __name__ == '__main__':
    main()
