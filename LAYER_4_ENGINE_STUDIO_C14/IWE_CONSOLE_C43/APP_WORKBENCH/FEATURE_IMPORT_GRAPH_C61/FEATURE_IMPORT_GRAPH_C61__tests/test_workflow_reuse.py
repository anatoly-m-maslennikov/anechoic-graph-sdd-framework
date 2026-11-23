from hashlib import sha256
import json
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_IMPORT_GRAPH_C61.workflow_reuse import check_reuse


LEAN = shutil.which('lean')
SOURCE = '''\
def update(store, value):
    store["key"] = value
    return value

def caller(target, amount):
    setup = 0
    target["key"] = amount
    result = amount
    return result

def literal(target):
    target["key"] = 42
    result = 42
    return result

def extra(target, amount):
    target["key"] = amount
    target["other"] = amount
    result = amount
    return result

def unsupported(target, amount):
    if amount:
        target["key"] = amount
    result = amount
    return result
'''


@unittest.skipUnless(LEAN, 'Lean is required')
class WorkflowReuseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        temp = TemporaryDirectory()
        cls.addClassCleanup(temp.cleanup)
        cls.root = Path(temp.name).resolve()
        (cls.root / '_anechoic_demo').mkdir()
        (cls.root / 'flows.py').write_text(SOURCE, encoding='utf-8')
        request = {'root': str(cls.root), 'config': {'python_roots': ['.']},
                   'structure': cls.structure(), 'control_root': '_anechoic_demo'}
        capture = subprocess.run(
            [sys.executable, '-B', '-P', '-m', 'WORKERS_beta_C69.realization_graph'],
            input=json.dumps(request), text=True, capture_output=True, timeout=60,
        )
        if capture.returncode:
            raise RuntimeError(capture.stderr)
        cls.graph = json.loads(capture.stdout)
        cls.keys = {row[3]: row[0] for row in cls.graph['code_units']}

    @staticmethod
    def structure(state='local'):
        return {'model_sha256': 'model', 'project': {
            'ref': 'AN-S-1', 'sha256': 'hash', 'boundaries': {'state': state}},
            'components': {}}

    def setUp(self):
        (self.root / 'flows.py').write_text(SOURCE, encoding='utf-8')

    def check(self, caller, first=None, last=None, *, state='local'):
        return check_reuse(self.root, self.graph, self.structure(state), self.keys[caller],
                           self.keys['update'], first, last, control_root='_anechoic_demo')

    def test_matches_renamed_and_literal_arguments_without_execution(self):
        for caller, first, last, arguments in [
            ('caller', 7, 8, {'store': {'parameter': 'target'}, 'value': {'parameter': 'amount'}}),
            ('literal', 12, 13, {'store': {'parameter': 'target'}, 'value': {'literal': 42}}),
        ]:
            with self.subTest(caller=caller):
                result = self.check(caller) if caller == 'caller' else self.check(caller, first, last)
                self.assertEqual(result['status'], 'matched', result)
                self.assertEqual(result['arguments'], arguments)
                self.assertEqual(result['result_binding'], 'result')
                self.assertEqual(result['source']['path'], 'flows.py')
                self.assertEqual(result['source']['sha256'], sha256(SOURCE.encode()).hexdigest())
                self.assertEqual(result['source']['first'], first)
                self.assertEqual(result['source']['last'], last)

    def test_adjacent_extra_write_is_different_and_keeps_range(self):
        result = self.check('extra')
        self.assertEqual(result['status'], 'different', result)
        self.assertIsNotNone(result['firstDifference'])
        self.assertEqual(result['source']['first'], 17)
        self.assertEqual(result['source']['last'], 19)

    def test_source_is_never_evaluated(self):
        marker = self.root / 'executed'
        source = SOURCE + f"\nopen({str(marker)!r}, 'w').close()\n"
        (self.root / 'flows.py').write_text(source, encoding='utf-8')
        self.assertEqual(self.check('caller', 7, 8)['status'], 'unresolved')
        self.assertFalse(marker.exists())

    def test_unsupported_region_and_ownership_are_unresolved(self):
        self.assertEqual(self.check('unsupported', 23, 25)['status'], 'unresolved')
        self.assertEqual(self.check('caller', 7, 8, state='pure')['status'], 'unresolved')


if __name__ == '__main__':
    unittest.main()
