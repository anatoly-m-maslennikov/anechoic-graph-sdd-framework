import json
import os
import shutil
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ANALYZER = Path(__file__).with_name('analyze.py')
LEAN = os.environ.get('LEAN_BIN') or shutil.which('lean') or 'lean'


class ResultContractTest(unittest.TestCase):
    def check_case(self, statements, details=(), unresolved=False):
        source = 'def release(arguments, root):\n    if arguments.operation == "local":\n'
        source += ''.join('        ' + line + '\n' for line in statements)
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, 'independent.py').write_text(source)
            run = subprocess.run([sys.executable, '-B', str(ANALYZER), tmp,
                                  '--file', 'independent.py', '--lean', LEAN],
                                 capture_output=True, text=True, check=True, timeout=40)
        report = json.loads(run.stdout)
        self.assertEqual(bool(report['unresolved']), unresolved, report)
        actual = ' '.join(item['detail'] for item in report['findings'])
        for detail in details:
            self.assertIn(detail, actual)
        self.assertEqual(bool(actual), bool(details), report)

    def test_spread_clean(self):
        self.check_case(['output = run_local_release(root)',
                         'return {**output, "run_id": arguments.run_id, "project_root": str(root)}'])

    def test_wrong_and_missing(self):
        self.check_case(['output = run_local_release(root)',
                         'return {**output, "run_id": "wrong"}'],
                        ['run_id is incorrect', 'project_root is missing'])

    def test_replacement_discards_diagnostics(self):
        self.check_case(['output = run_local_release(root)',
                         'return {"run_id": arguments.run_id, "project_root": str(root)}'],
                        ['Runner diagnostics are discarded'])

    def test_spread_overrides_earlier_field(self):
        self.check_case(['output = run_local_release(root)',
                         'output.update(run_id="wrong", project_root=str(root))',
                         'return {"run_id": arguments.run_id, **output}'],
                        ['run_id is incorrect'])

    def test_same_dict_wrong_value(self):
        self.check_case(['output = run_local_release(root)',
                         'output.update(run_id=arguments.run_id, project_root="wrong")',
                         'return output'], ['project_root is incorrect'])

    def test_diagnostic_overwrite_is_unsupported(self):
        self.check_case(['output = run_local_release(root)',
                         'return {**output, "errors": []}'], unresolved=True)

    def test_unsupported_mutation(self):
        self.check_case(['output = run_local_release(root)', 'output.clear()',
                         'return output'], unresolved=True)


if __name__ == '__main__':
    unittest.main()
