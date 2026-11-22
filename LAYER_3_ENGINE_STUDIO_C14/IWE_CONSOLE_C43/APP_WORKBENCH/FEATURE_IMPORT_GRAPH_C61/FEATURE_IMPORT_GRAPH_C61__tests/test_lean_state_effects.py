"""Verify the Lean effect rules and one explicitly instrumented Autoform fixture."""

import ast
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch


KERNEL = Path(__file__).resolve().parents[1] / 'ActionEffects.lean'
CONTEXT = '''
open Autoform.Core Autoform.SpecsGen Autoform.Generated.AnechoicEffects
set_option maxRecDepth 20000
set_option maxHeartbeats 0
private def gp : Heap × Ref := initGlobals program 300 moduleInits
private def h0 : Heap := gp.1
private def base : Nat := h0.length
private def ctx : Ctx :=
  { dialect := program.dialect, table := program.table, globals := gp.2,
    builtinBases := program.builtinBases, properties := program.properties,
    excClasses := program.excClasses, classDecls := program.classDecls }
'''
SOURCE = '''
def action(kind, state, sink, trace):
    if kind == 0:
        alias = state
        alias[0] = 1
    elif kind == 1:
        sink.append(7)
    elif kind == 2:
        old = state[0]
        state[0] = 1
        state[0] = old
    elif kind == 3:
        pass
    else:
        raise ValueError('unsupported fixture input')
'''


def _event(kind, target='', name='', line=1):
    return {'kind': kind, 'target': target, 'name': name, 'line': line}


def _case(events, **changes):
    return {
        'sourcePath': 'action.py', 'line': 2, 'input': None,
        'reachable': True, 'complete': True, 'declaredNoOp': False,
        'policy': {'kind': 'local', 'owner': 'caller', 'grants': []},
        'events': events,
    } | changes


def _kernel(cases):
    result = subprocess.run(
        ['lean', '--run', KERNEL], input=json.dumps(cases), text=True,
        stdout=subprocess.PIPE, check=True, timeout=60,
    )
    return json.loads(result.stdout)


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class FixtureTrace(ast.NodeTransformer):
    """Record operations in the fixed fixture's selected state and output."""

    def visit_Assign(self, node):
        marker = None
        if isinstance(node.targets[0], ast.Subscript):
            marker = 1
        elif isinstance(node.value, ast.Subscript):
            marker = 0
        return node if marker is None else [node, self.record(node, marker)]

    def visit_Expr(self, node):
        return [node, self.record(node, 2)] if isinstance(node.value, ast.Call) else node

    @staticmethod
    def record(node, marker):
        return ast.parse(f'trace.append({10 * node.lineno + marker})').body[0]


def _run(args, cwd):
    subprocess.run(args, cwd=cwd, check=True, timeout=480)


def _observations(folder, source, differential):
    module = _load(source, 'lean_action_effects_fixture')
    identities = differential.class_identity_index(
        json.loads((folder / 'ast.json').read_text()), source.parent,
    ) or {}
    records, events = [], []
    markers = [_event('read', 'ambient', 'REQUEST_CTX'),
               _event('write', 'ambient', 'REQUEST_CTX'), _event('output')]
    for kind in range(4):
        state, sink, trace = [0], [], []
        encoder = differential.GraphEncoder(identities)
        args = [encoder.enc(value) for value in (kind, state, sink, trace)]
        encoder.freeze()
        value = module.action(kind, state, sink, trace)
        assert (state, sink) == [([1], []), ([0], [7]), ([0], []), ([0], [])][kind]
        record = {'name': 'instrumented.py:<module>.action', 'self': None,
                  'args': args, 'outcome': ('val', encoder.enc_result(value))}
        observation = differential.finish_record(encoder, record)
        assert 'post_heap' in observation
        records.append(observation)
        events.append([markers[marker % 10] | {'line': marker // 10} for marker in trace])
        if kind == 2:
            trace.clear()
            tampered = differential.finish_record(encoder, dict(record))
    return records, events, tampered


def _prove(folder, checkout, source):
    differential = _load(checkout / 'scripts/differential.py', 'ane_effect_diff')
    synth = _load(checkout / 'scripts/synth_specs.py', 'ane_effect_synth')
    records, events, tampered = _observations(folder, source, differential)
    model = (folder / 'Model.lean').read_text().replace(
        'import Autoform.Lang.Core.Semantics', 'import Autoform.SpecsGen.Basis',
    )
    proof = [model, CONTEXT]
    fn = synth.lean_ident('instrumented.py:<module>.action')
    for index, record in enumerate(records):
        proof.extend([f'private def obs{index} : Obs := {synth.obs_lit(record)}',
                      f'example : lawConform ctx 160 {fn} obs{index} = true := by decide +kernel'])
    proof.extend([f'private def tampered : Obs := {synth.obs_lit(tampered)}',
                  f'example : lawConform ctx 160 {fn} tampered = false := by decide +kernel'])
    path = folder / 'Proof.lean'
    path.write_text('\n'.join(proof) + '\n')
    _run(['lake', 'env', 'lean', path], checkout)
    return events


@unittest.skipUnless(shutil.which('lean'), 'Lean 4 is required for the effect checks')
class LeanStateEffectsTests(unittest.TestCase):
    def test_dead_end_and_grants(self):
        read = _event('read', 'ambient', 'REQUEST_CTX')
        write = _event('write', 'ambient', 'REQUEST_CTX')
        policy = {'kind': 'local', 'owner': 'caller',
                  'grants': [{'channel': 'REQUEST_CTX', 'mode': 'r'}]}
        cases = [_case([]), _case([], declaredNoOp=True), _case([], complete=False),
                 _case([_event('output')]), _case([read, write, write], policy=policy),
                 _case([_event('write', 'local', 'other')]),
                 _case([write], policy={'kind': 'pure', 'owner': '', 'grants': []})]
        results = _kernel(cases)
        self.assertEqual([result['status'] for result in results],
                         ['deadEnd', 'declaredNoOp', 'unresolved', 'hasEffects',
                          'hasEffects', 'hasEffects', 'hasEffects'])
        self.assertEqual([i for i, row in enumerate(results) if row['deadEnd']], [0])
        self.assertEqual([[v['index'] for v in result['violations']] for result in results],
                         [[], [], [], [], [1, 2], [0], [0]])

    def test_invalid_trace_fails_on_stderr(self):
        result = subprocess.run(['lean', '--run', KERNEL], input='{}', text=True,
                                capture_output=True, timeout=60, check=False)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, '')
        self.assertTrue(result.stderr)

    @unittest.skipUnless(os.environ.get('AUTOFORM_CHECKOUT'), 'Set AUTOFORM_CHECKOUT for the Autoform canary')
    def test_autoform_agrees_with_python_on_ordered_effects(self):
        checkout = Path(os.environ['AUTOFORM_CHECKOUT']).resolve(strict=True)
        joern = Path(os.environ['JOERN_HOME']).resolve(strict=True)
        with TemporaryDirectory(prefix='anechoic-state-effects-') as tmp, \
                patch.dict(os.environ, {'AUTOFORM_NO_REEXEC': '1'}), \
                patch.object(sys, 'path', [str(checkout / 'scripts'), *sys.path]):
            folder = Path(tmp)
            source = folder / 'source' / 'instrumented.py'
            source.parent.mkdir()
            tree = FixtureTrace().visit(ast.parse(SOURCE))
            source.write_text(ast.unparse(ast.fix_missing_locations(tree)) + '\n')
            _run([joern / 'joern-parse', source.parent, '--language', 'PYTHONSRC',
                  '--output', 'cpg.bin'], folder)
            _run([joern / 'joern', '--script', checkout / 'cartographer/export_ast.sc',
                  '--param', 'cpgPath=cpg.bin', '--param', 'out=ast.json'], folder)
            _run([sys.executable, checkout / 'cartographer/render_lean.py',
                  folder / 'ast.json', folder / 'Model.lean', 'AnechoicEffects'], folder)
            _run(['lake', 'build', 'Autoform.SpecsGen.Basis'], checkout)
            events = _prove(folder, checkout, source)
        self.assertEqual([[event['kind'] for event in path] for path in events],
                         [['write'], ['output'], ['read', 'write', 'write'], []])
        policy = {'kind': 'local', 'owner': 'caller',
                  'grants': [{'channel': 'REQUEST_CTX', 'mode': 'r'}]}
        results = _kernel([_case(path, policy=policy, input=index)
                           for index, path in enumerate(events)])
        self.assertEqual([row['status'] for row in results], ['hasEffects'] * 3 + ['deadEnd'])
        self.assertEqual([[v['index'] for v in row['violations']] for row in results], [[0], [], [1, 2], []])
        self.assertEqual([v['line'] for v in results[2]['violations']], [10, 11])
        self.assertEqual((results[3]['sourcePath'], results[3]['input']), ('action.py', 3))


if __name__ == '__main__':
    unittest.main()
