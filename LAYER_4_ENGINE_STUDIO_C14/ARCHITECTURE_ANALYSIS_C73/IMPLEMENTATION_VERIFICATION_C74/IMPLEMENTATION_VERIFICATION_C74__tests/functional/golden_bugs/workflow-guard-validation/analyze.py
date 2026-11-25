"""Check supported workflow compiler behavior on a finite supplied graph."""
import argparse
import json
import re
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = 'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_IMPORT_GRAPH_C61/WORKFLOW_SPEC/WORKFLOW_SPEC__shared.mjs'
DETAILS = (
    'Overlapping output guards are accepted for the same event.',
    'A reachable closed cycle with no path to a final state is accepted.',
)
DEFAULT = {
    'id': 'pilot', 'initial': 'start', 'states': {
        'start': {'on': {'output': [
            {'target': 'stuck', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'output'}}},
            {'target': 'done', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'output', 'outcome': 'success'}}},
        ]}},
        'stuck': {'on': {'loop': {'target': 'stuck', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'output'}}}}},
        'done': {'type': 'final'},
    },
}


def validate_branch(branch, nodes):
    if (not isinstance(branch, dict) or set(branch) != {'target', 'guard'}
            or not safe(branch['target']) or branch['target'] not in nodes
            or not isinstance(branch['guard'], dict) or set(branch['guard']) != {'type', 'params'}
            or branch['guard']['type'] != 'matchesTrace' or not isinstance(branch['guard']['params'], dict)):
        raise ValueError('unsupported graph: invalid transition')
    guard = branch['guard']['params']
    if set(guard) - {'kind', 'target', 'outcome', 'detail'} or guard.get('kind') not in ('trigger', 'effect', 'output'):
        raise ValueError('unsupported graph: invalid guard')
    if any(k in guard and guard[k] is not None and (not isinstance(guard[k], str) or len(guard[k]) > 256) for k in ('target', 'outcome')):
        raise ValueError('unsupported graph: invalid guard constraint')
    detail = guard.get('detail', {})
    if (not isinstance(detail, dict) or any(not isinstance(k, str) for k in detail)
            or any(v is not None and (not isinstance(v, (str, bool, int)) or isinstance(v, int) and abs(v) > 2**53 - 1) for v in detail.values())):
        raise ValueError('unsupported graph: detail constraints must be scalar strings, safe integers, booleans, or null')
    return branch['guard']['params']


def safe(value):
    return (isinstance(value, str) and re.fullmatch(r'[A-Za-z_][A-Za-z0-9_-]{0,63}', value)
            and value not in ('__proto__', 'constructor', 'prototype'))


def validate_graph(config):
    if (not isinstance(config, dict) or set(config) != {'id', 'initial', 'states'}
            or not safe(config['id']) or not safe(config['initial']) or not isinstance(config['states'], dict)):
        raise ValueError('unsupported graph: invalid config')
    nodes = config['states']
    states, final, transitions = list(nodes), [], []
    if not 1 <= len(states) <= 100 or any(not safe(s) for s in states) or config['initial'] not in nodes:
        raise ValueError('unsupported graph: invalid states or initial')
    for name, node in nodes.items():
        if not isinstance(node, dict):
            raise ValueError('unsupported graph: invalid state')
        if node == {'type': 'final'}:
            final.append(name)
            continue
        if set(node) != {'on'} or not isinstance(node['on'], dict):
            raise ValueError('unsupported graph: invalid state')
        for event, branches in node['on'].items():
            if not safe(event):
                raise ValueError('unsupported graph: invalid event')
            branches = branches if isinstance(branches, list) else [branches]
            if not branches:
                raise ValueError('unsupported graph: empty transitions')
            for branch in branches:
                guard = validate_branch(branch, nodes)
                transitions.append({'source': name, 'event': event, 'target': branch['target'], 'guard': guard})
    if not final or len(transitions) > 1000:
        raise ValueError('unsupported graph: final state or transition count')
    reached = {config['initial']}
    while True:
        expanded = reached | {t['target'] for t in transitions if t['source'] in reached}
        if expanded == reached:
            break
        reached = expanded
    if len(reached) != len(states):
        raise ValueError('unsupported graph: unreachable states fail compiler admission')
    return {'initial': config['initial'], 'states': states, 'final': final, 'transitions': transitions}


def translate(path, graph):
    run = subprocess.run(
        ['node', str(HERE / 'extract.cts'), str(path)],
        capture_output=True, text=True, timeout=30, check=False,
    )
    if run.returncode:
        raise ValueError('unsupported JavaScript: ' + run.stderr.strip())
    facts = json.loads(run.stdout)
    states, transitions = graph['states'], graph['transitions']
    keys, values = {}, {}
    guards = []
    for t in transitions:
        items = [(k, v) for k, v in t['guard'].items() if k != 'detail']
        items += [('detail.' + k, v) for k, v in t['guard'].get('detail', {}).items()]
        encoded = []
        for key, value in items:
            value = json.dumps(value, ensure_ascii=True, separators=(',', ':'))
            keys.setdefault(key, len(keys))
            values.setdefault(value, len(values))
            encoded.append((keys[key], values[value]))
        guards.append(encoded)
    groups = {}
    for i, transition in enumerate(transitions):
        groups.setdefault((transition['source'], transition['event']), []).append(i)
    groups = [indices for indices in groups.values() if len(indices) > 1]
    def lean_list(items):
        return '[' + ', '.join(items) + ']'
    prefix = 'set_option maxRecDepth 10000\n' + ''.join(f'def {name}Check : Bool := {str(facts[key]).lower()}\n'
                     for name, key in [('overlap', 'overlap'), ('finish', 'finish')])
    prefix += 'def edges : List (Nat × Nat) := ' + lean_list(
        [f'({states.index(t["source"])}, {states.index(t["target"])})' for t in transitions]) + '\n'
    prefix += 'def finals : List Nat := ' + lean_list([str(states.index(s)) for s in graph['final']]) + '\n'
    prefix += 'def initial : Nat := ' + str(states.index(graph['initial'])) + '\n'
    prefix += 'def fuel : Nat := ' + str(len(states)) + '\n'
    for i, guard in enumerate(guards):
        prefix += f'def guard{i} : List (Nat × Nat) := ' + lean_list([f'({k}, {v})' for k, v in guard]) + '\n'
    code = prefix + (HERE / 'model.lean.txt').read_text()
    code += ''.join('\n#eval firstOverlap ' + lean_list([f'({i}, guard{i})' for i in group]) for group in groups)
    code += ''.join(f'\n#eval !finishCheck && reaches fuel initial {i} && !(finishes fuel {i})' for i in range(len(states)))
    return code + '\n', groups, facts


def analyze(checkout, lean, graph=DEFAULT):
    result = {'findings': [], 'unresolved': []}
    try:
        normalized = validate_graph(graph)
        code, groups, facts = translate(checkout / SOURCE, normalized)
        with tempfile.TemporaryDirectory() as tmp:
            proof = Path(tmp) / 'check.lean'
            proof.write_text(code)
            run = subprocess.run([lean, str(proof)], capture_output=True, text=True, timeout=45, check=False)
        outcomes = run.stdout.strip().splitlines()
        overlaps = outcomes[:len(groups)]
        dead = outcomes[len(groups):]
        matches = [re.fullmatch(r'some \((\d+), (\d+)\)', item) for item in overlaps]
        if (run.returncode or len(outcomes) != len(groups) + len(normalized['states'])
                or any(item != 'none' and not match for item, match in zip(overlaps, matches))
                or any(item not in ('true', 'false') for item in dead)):
            raise ValueError('Lean failed: ' + run.stderr + run.stdout)
        for match in matches:
            if match and not facts['overlap']:
                i, j = map(int, match.groups())
                a, b = normalized['transitions'][i], normalized['transitions'][j]
                witness = {**a['guard'], **b['guard']}
                if 'detail' in a['guard'] or 'detail' in b['guard']:
                    witness['detail'] = {**a['guard'].get('detail', {}), **b['guard'].get('detail', {})}
                result['findings'].append({'path': SOURCE, 'detail': DETAILS[0] if graph is DEFAULT else 'Overlapping guards are accepted for the same event.', 'witness': {
                    'state': a['source'], 'event': a['event'], 'transitions': [i, j], 'guard': witness}})
        if facts['overlap'] and any(matches):
            if graph is DEFAULT:
                alternate = json.loads(json.dumps(DEFAULT))
                alternate['states']['start']['on']['output'][0]['guard']['params']['outcome'] = 'failure'
                independent = analyze(checkout, lean, alternate)
                for finding in independent['findings']:
                    finding['detail'] = DETAILS[1]
                return independent
            return result
        for outcome, state in zip(dead, normalized['states']):
            if outcome == 'true':
                result['findings'].append({'path': SOURCE, 'detail': DETAILS[1] if graph is DEFAULT else 'A reachable state with no path to a final state is accepted.', 'witness': {'state': state}})
    except (OSError, ValueError, TypeError, subprocess.TimeoutExpired) as error:
        result['unresolved'].append({'path': SOURCE, 'detail': str(error)})
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('checkout', type=Path)
    parser.add_argument('--lean', required=True)
    parser.add_argument('--scenario', type=Path)
    args = parser.parse_args()
    try:
        graph = json.loads(args.scenario.read_text()) if args.scenario else DEFAULT
        print(json.dumps(analyze(args.checkout, args.lean, graph)))
    except (OSError, ValueError) as error:
        print(json.dumps({'findings': [], 'unresolved': [{'path': SOURCE, 'detail': str(error)}]}))


if __name__ == '__main__':
    main()
