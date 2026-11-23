import copy
import json
import os
from pathlib import Path
import shutil
import subprocess
import unittest

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
