"""Run the historical pair and finite graph controls."""
import os
import sys
import tempfile
from pathlib import Path

if not __package__:
    directory = Path(__file__).resolve().parent
    engine = next(parent for parent in directory.parents if parent.name == "LAYER_4_ENGINE_STUDIO_C14")
    sys.path.insert(0, str(engine))
    __package__ = ".".join(directory.relative_to(engine).parts)

from . import analyze


def branch(target, outcome=None):
    params = {'kind': 'output'}
    if outcome is not None:
        params['outcome'] = outcome
    return {'target': target, 'guard': {'type': 'matchesTrace', 'params': params}}


def main():
    lean = os.environ.get('LEAN_BIN', 'lean')
    scenario = {'id': 'heldout', 'initial': 'start', 'states': {
        'start': {'on': {'go': [branch('a', 'yes'), branch('done', 'no')]}},
        'a': {'on': {'go': branch('b')}},
        'b': {'on': {'go': branch('a')}},
        'done': {'type': 'final'},
    }}
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        source = root / analyze.SOURCE
        source.parent.mkdir(parents=True)
        for fixture in ('before', 'fixed'):
            source.write_bytes((analyze.HERE / (fixture + '.mjs.txt')).read_bytes())
            default = analyze.analyze(root, lean)
            held = analyze.analyze(root, lean, scenario)
            assert not default['unresolved'] and not held['unresolved']
            assert len(default['findings']) == (2 if fixture == 'before' else 0)
            assert [f['witness']['state'] for f in held['findings']] == (['a', 'b'] if fixture == 'before' else [])
        fixed = (analyze.HERE / 'fixed.mjs.txt').read_text()
        source.write_text(fixed + '\nfunction unrelatedHelper() { return true; }\n')
        assert analyze.analyze(root, lean) == {'findings': [], 'unresolved': []}
        for name, replacement in (('guardsOverlap', 'return false;'), ('requirePathToFinal', 'return;')):
            start = fixed.index('{', fixed.index('function ' + name))
            end = fixed.index('\n}', start)
            disabled = fixed[:start + 1] + '\n/*' + fixed[start + 1:end] + '\n*/\n' + replacement + fixed[end:]
            source.write_text(disabled)
            rejected = analyze.analyze(root, lean)
            assert not rejected['findings'] and 'unsupported executable AST:' in rejected['unresolved'][0]['detail']
            assert name in rejected['unresolved'][0]['detail']
        source.write_text((analyze.HERE / 'fixed.mjs.txt').read_text().replace('  requirePathToFinal(states);\n', ''))
        partial = analyze.analyze(root, lean)
        assert not partial['unresolved'] and len(partial['findings']) == 1
        assert partial['findings'][0]['witness']['state'] == 'stuck'
        source.write_bytes((analyze.HERE / 'before.mjs.txt').read_bytes())
        scenario['states']['b']['on']['go'] = [branch('a', 'yes'), branch('done', 'no')]
        assert analyze.analyze(root, lean, scenario) == {'findings': [], 'unresolved': []}
        scenario['states']['b']['on']['go'][1]['guard']['params']['outcome'] = 'yes'
        overlap = analyze.analyze(root, lean, scenario)
        assert not overlap['unresolved'] and len(overlap['findings']) == 1
        assert overlap['findings'][0]['witness']['guard'] == {'kind': 'output', 'outcome': 'yes'}
        scenario['states']['orphan'] = {'on': {}}
        assert analyze.analyze(root, lean, scenario)['unresolved']
    print('historical pair and graph controls passed')


if __name__ == '__main__':
    main()
