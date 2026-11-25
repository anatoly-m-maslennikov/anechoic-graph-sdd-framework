import copy
import json
import os
from pathlib import Path
import shutil
import subprocess
import unittest

from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_IMPORT_GRAPH_C61.import_graph__shared import compile_workflow

LEAN = os.environ.get('LEAN_BIN') or shutil.which('lean')
SCRIPT = Path(__file__).resolve().parents[1] / 'WorkflowTrace.lean'


def sample():
    return {'complete': True, 'model': {'initial': 'idle', 'states': [
        {'name': 'idle', 'final': False, 'transitions': [
            {'event': 'save', 'target': 'done', 'expect': {
                'kind': 'effect', 'target': None, 'outcome': 'ok', 'detail': {'id': 1}}}]},
        {'name': 'done', 'final': True, 'transitions': []}]},
        'events': [{'kind': 'effect', 'name': 'save', 'target': None,
                    'outcome': 'ok', 'detail': {'id': 1, 'extra': True}}]}


def machine():
    def branch(target, **params):
        return {'target': target, 'guard': {'type': 'matchesTrace', 'params': params}}
    return {'id': 'flow', 'initial': 'start', 'states': {
        'start': {'on': {'NEXT': [branch('done', kind='output', outcome='success'),
                                  branch('start', kind='effect', outcome='retry')]}},
        'done': {'type': 'final'}}}


class WorkflowCompilerTests(unittest.TestCase):
    def test_model_and_mermaid(self):
        result = compile_workflow(machine())
        states = result['model']['states']
        self.assertEqual(result['model']['initial'], 'start')
        self.assertEqual([t['target'] for t in states[0]['transitions']], ['done', 'start'])
        self.assertEqual(states[0]['transitions'][0]['expect'],
                         {'kind': 'output', 'outcome': 'success'})
        self.assertTrue(states[1]['final'])
        for text in ('stateDiagram', 'NEXT / output / success',
                     'NEXT / effect / retry', 'done --> [*]'):
            self.assertIn(text, result['mermaid'])

    def test_invalid_graphs(self):
        cases = []
        c = machine()
        c['states']['start']['entry'] = 'action'
        cases.append(c)
        c = machine()
        c['states']['start']['on']['NEXT'][0]['target'] = 'missing'
        cases.append(c)
        c = machine()
        c['states']['extra'] = {'type': 'final'}
        cases.append(c)
        c = machine()
        c['states']['start']['on']['NEXT'][0]['guard']['type'] = 'arbitrary'
        cases.append(c)
        c = machine()
        c['states']['start']['on']['NEXT'][0]['guard']['params']['kind'] = []
        cases.append(c)
        c = machine()
        c['states']['done'] = {'on': {}}
        cases.append(c)
        for on in ({}, {'LOOP': {'target': 'stuck', 'guard': {
                'type': 'matchesTrace', 'params': {'kind': 'effect'}}}}):
            c = machine()
            c['states']['start']['on']['NEXT'][1]['target'] = 'stuck'
            c['states']['stuck'] = {'on': on}
            cases.append(c)
        for case in cases:
            with self.subTest(case=case), self.assertRaises(ValueError):
                compile_workflow(case)

    def test_guard_overlap_and_disjointness(self):
        pairs = [
            ({'kind': 'output'}, {'kind': 'output', 'outcome': 'success'}, True),
            ({'kind': 'output', 'target': None}, {'kind': 'output'}, True),
            ({'kind': 'output', 'detail': {'a': 1}},
             {'kind': 'output', 'detail': {'a': 1, 'b': 2}}, True),
            ({'kind': 'output', 'detail': {'a': {'x': 1, 'y': 2}}},
             {'kind': 'output', 'detail': {'a': {'y': 2, 'x': 1}}}, True),
            ({'kind': 'output', 'target': None}, {'kind': 'output', 'target': 'x'}, False),
            ({'kind': 'output', 'detail': {'a': 1}}, {'kind': 'output', 'detail': {'a': 2}}, False),
            ({'kind': 'output', 'detail': {'a': {'x': 1}}},
             {'kind': 'output', 'detail': {'a': {'x': 1, 'y': 2}}}, False),
            ({'kind': 'output', 'detail': {'a': True}}, {'kind': 'output', 'detail': {'a': 1}}, False),
        ]
        for a, b, overlap in pairs:
            c = machine()
            c['states']['start']['on']['NEXT'] = [
                {'target': target, 'guard': {'type': 'matchesTrace', 'params': params}}
                for target, params in [('done', a), ('start', b)]]
            with self.subTest(a=a, b=b):
                if overlap:
                    with self.assertRaisesRegex(ValueError, 'overlapping guards'):
                        compile_workflow(c)
                else:
                    self.assertEqual(len(compile_workflow(c)['model']['states'][0]['transitions']), 2)


@unittest.skipUnless(LEAN, 'Lean is required')
class WorkflowTraceTests(unittest.TestCase):
    def run_case(self, value):
        return subprocess.run([LEAN, '--run', SCRIPT], input=json.dumps(value),
                              text=True, capture_output=True, check=False)

    def result(self, value):
        run = self.run_case(value)
        self.assertEqual(run.returncode, 0, run.stderr)
        return json.loads(run.stdout)

    def test_match_and_mismatches(self):
        self.assertEqual(self.result(sample())['status'], 'matched')
        for field, value in [('kind', 'output'), ('target', 'other'),
                             ('outcome', None), ('detail', {'id': 2})]:
            case = sample()
            case['events'][0][field] = value
            result = self.result(case)
            self.assertEqual(result['status'], 'different')
            self.assertEqual(result['firstDifference']['state'], 'idle')
            self.assertEqual(result['firstDifference']['index'], 0)
        case = sample()
        case['events'] = []
        self.assertEqual(self.result(case)['firstDifference']['index'], 0)
        case = sample()
        case['events'].append(copy.deepcopy(case['events'][0]))
        self.assertEqual(self.result(case)['firstDifference']['state'], 'done')
        self.assertEqual(self.result(case)['firstDifference']['index'], 1)

    def test_unresolved_and_invalid(self):
        case = sample()
        case['complete'] = False
        self.assertEqual(self.result(case)['status'], 'unresolved')
        case = sample()
        case['model']['states'][0]['transitions'].append(
            copy.deepcopy(case['model']['states'][0]['transitions'][0]))
        self.assertEqual(self.result(case)['status'], 'unresolved')
        case = sample()
        case['model']['states'][0]['transitions'][0]['target'] = 'missing'
        run = self.run_case(case)
        self.assertNotEqual(run.returncode, 0)
        self.assertTrue(run.stderr)

if __name__ == '__main__':
    unittest.main()
