import copy
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75._package__shared import compile_workflow
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_2_SPEC_READING_C83.SPECIFICATION_MODEL_C85._package__shared import parse_workflow

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


def correlation_machine():
    return {'id': 'reply', 'initial': 'idle', 'states': {
        'idle': {'on': {'start': {'to': 'waiting', 'expect': {
            'kind': 'trigger', 'bind': {'request': 'id', 'generation': 'generation'}}}}},
        'waiting': {'on': {
            'retry': {'to': 'waiting', 'expect': {'kind': 'effect', 'bind': {'request': 'id'}}},
            'finish': {'to': 'done', 'expect': {'kind': 'output', 'outcome': 'ok',
                'detail': {'sql': 'current'}, 'same_as': {'reply_id': 'request', 'generation': 'generation'}}}}},
        'done': {'type': 'final'}}}


class WorkflowCompilerTests(unittest.TestCase):
    def test_parse_shared_workflow(self):
        source = f"component_workflow(component='C61', action='run', machine={machine()!r})"
        self.assertEqual(compile_workflow(parse_workflow(source)['machine']), compile_workflow(machine()))
        with self.assertRaisesRegex(ValueError, 'unique string keys'):
            parse_workflow("component_workflow(component='C61', action='run', machine={'id': 1, 'id': 2})")

    def test_model_and_mermaid(self):
        result = compile_workflow(machine())
        states = result['model']['states']
        self.assertEqual(result['model']['initial'], 'start')
        self.assertEqual([t['target'] for t in states[0]['transitions']], ['done', 'start'])
        self.assertEqual(states[0]['transitions'][0]['expect'],
                         {'kind': 'output', 'outcome': 'success'})
        self.assertTrue(states[1]['final'])
        for text in ('stateDiagram', 'NEXT / output / outcome=#quot;success#quot;',
                     'NEXT / effect / outcome=#quot;retry#quot;',
                     'state "done" as S1', 'S1 --> [*]'):
            self.assertIn(text, result['mermaid'])

    def test_cli_selects_one_action_in_multi_action_solution(self):
        workflows = []
        for action in ('run', 'check'):
            config = machine()
            config['states']['start']['on']['NEXT'][0]['guard']['params']['outcome'] = action
            workflows.append(f"```python\ncomponent_workflow(component='C61', action={action!r}, machine={config!r})\n```")
        with TemporaryDirectory() as directory:
            path = Path(directory) / 'solution.md'
            path.write_text('## Claim\n\n### Formal Claim\n\n' + '\n\n'.join(workflows), encoding='utf-8')
            command = [sys.executable, '-B', '-m',
                       'IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IMPORT_GRAPH_C61.workflow_spec',
                       str(path), 'render']
            selected = subprocess.run([*command, '--action', 'check'], capture_output=True, text=True, check=False)
            self.assertEqual(0, selected.returncode, selected.stderr)
            self.assertIn('outcome=#quot;check#quot;', selected.stdout)
            for arguments, error in (([], 'Specify --action'), (['--action', 'missing'], 'Unknown Solution action')):
                with self.subTest(arguments=arguments):
                    rejected = subprocess.run([*command, *arguments], capture_output=True, text=True, check=False)
                    self.assertEqual(3, rejected.returncode)
                    self.assertIn(error, rejected.stderr)

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
            ({'kind': 'output', 'detail': {'a': {'at_most': 45}}}, {'kind': 'output', 'detail': {'a': 45}}, True),
            ({'kind': 'output', 'detail': {'a': 45.0}}, {'kind': 'output', 'detail': {'a': {'at_most': 45}}}, True),
            ({'kind': 'output', 'detail': {'a': {'at_most': 45}}}, {'kind': 'output', 'detail': {'a': 46}}, False),
            ({'kind': 'output', 'detail': {'a': {'at_most': 45}}}, {'kind': 'output', 'detail': {'a': True}}, False),
            ({'kind': 'output', 'detail': {'a': {'at_most': 45}}},
             {'kind': 'output', 'detail': {'a': {'at_most': 2}}}, True),
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

    def test_references_require_a_prior_binding_on_every_path(self):
        for gap in ('unknown', 'same_event', 'alternate_path'):
            config = correlation_machine()
            states = config['states']
            start = states['idle']['on']['start']['expect']
            finish = states['waiting']['on']['finish']['expect']
            if gap == 'unknown':
                finish['same_as']['reply_id'] = 'unknown'
            elif gap == 'same_event':
                start['same_as'] = {'id': 'request'}
            else:
                states['idle']['on']['skip'] = {'to': 'waiting', 'expect': {'kind': 'trigger'}}
            with self.subTest(gap=gap), self.assertRaisesRegex(ValueError, 'must be set on every path'):
                compile_workflow(config)

    def test_binding_guards_appear_in_the_diagram(self):
        mermaid = compile_workflow(correlation_machine())['mermaid']
        self.assertIn('bind={#quot;request#quot;:#quot;id#quot;', mermaid)
        self.assertIn('same_as={#quot;reply_id#quot;:#quot;request#quot;', mermaid)


@unittest.skipUnless(LEAN, 'Lean is required')
class WorkflowTraceTests(unittest.TestCase):
    def run_case(self, value):
        return subprocess.run([LEAN, '--run', SCRIPT], input=json.dumps(value),
                              text=True, capture_output=True, check=False)

    def result(self, value):
        run = self.run_case(value)
        self.assertEqual(run.returncode, 0, run.stderr)
        return json.loads(run.stdout)

    def test_solution_cli_checks_request_and_generation(self):
        config = correlation_machine()
        with TemporaryDirectory() as directory:
            path = Path(directory) / 'solution.md'
            path.write_text('## Claim\n\n### Formal Claim\n\n```python\n'
                            f"component_workflow(component='C61', action='run', machine={config!r})\n```\n",
                            encoding='utf-8')
            command = [sys.executable, '-B', '-m',
                       'IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IMPORT_GRAPH_C61.workflow_spec',
                       str(path), 'check', '-']
            columns = ['run_id', 'component', 'action', 'sequence', 'kind', 'name', 'target', 'outcome', 'detail']
            for generation, reply, retry, status, index in (
                (2, 'r1', 'r1', 'matched', None), (3, 'r1', 'r1', 'different', 2),
                (2, 'r2', 'r1', 'different', 2), (2, 'r2', 'r2', 'different', 1),
                (None, 'r1', 'r1', 'different', 2),
            ):
                details = {'reply_id': reply, 'sql': 'current'}
                if generation is not None:
                    details['generation'] = generation
                events = [('trigger', 'start', None, {'id': 'r1', 'generation': 2}),
                          ('effect', 'retry', None, {'id': retry}),
                          ('output', 'finish', 'ok', details)]
                rows = [['recorded', 'C61', 'run', seq, kind, name, None, outcome, detail]
                        for seq, (kind, name, outcome, detail) in enumerate(events)]
                with self.subTest(generation=generation, reply=reply, retry=retry):
                    run = subprocess.run(command, input=json.dumps({'columns': columns, 'rows': rows}),
                                         capture_output=True, text=True, timeout=120, check=False)
                    self.assertEqual(int(status == 'different'), run.returncode, run.stderr or run.stdout)
                    result = json.loads(run.stdout)
                    self.assertEqual(status, result['status'])
                    self.assertEqual(index, (result['firstDifference'] or {}).get('index'))

    def test_upper_bound_detail(self):
        case = sample()
        case['model']['states'][0]['transitions'][0]['expect']['detail'] = {
            'rows': {'at_most': 45}, 'serialized_bytes': {'at_most': 300}}
        for detail, expected in [({'rows': 45, 'serialized_bytes': 300}, 'matched'),
                                 ({'rows': {'at_most': 20}, 'serialized_bytes': 299}, 'matched'),
                                 ({'rows': 46, 'serialized_bytes': 300}, 'different'),
                                 ({'rows': True, 'serialized_bytes': 300}, 'different'),
                                 ({'rows': 45}, 'different'),
                                 ({'rows': {'at_most': 46}, 'serialized_bytes': 300}, 'different')]:
            case['events'][0]['detail'] = detail
            with self.subTest(detail=detail):
                self.assertEqual(self.result(case)['status'], expected)

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
