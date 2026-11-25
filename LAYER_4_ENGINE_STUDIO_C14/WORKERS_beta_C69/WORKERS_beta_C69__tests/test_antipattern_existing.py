"""Exercise existing access findings through a captured Beta graph."""

import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

ENGINE = Path(__file__).resolve().parents[2]


class ExistingAccessFindingsTest(unittest.TestCase):
    def test_cross_package_access_and_declared_exception(self):
        with TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            (root / '_control/_SPEC').mkdir(parents=True)
            (root / '_control/Widget_C9').mkdir()
            (root / 'Widget/lib').mkdir(parents=True)
            (root / 'Widget/client').mkdir()
            (root / 'Widget/lib/parse.py').write_text('def run(): return 1\n')
            (root / 'Widget/lib/__init__.py').write_text('from .parse import run\n')
            (root / 'Widget/client/run.py').write_text(
                'from Widget.lib.parse import run\nfrom Widget.lib.parse import *\n'
                'from Widget.lib import run\n')
            code = {'imports': ['lib.parse.run', 'lib.run']}
            structure = {'model_sha256': 'model', 'project': {'ref': 'AN-S-1', 'sha256': 'hash'},
                         'components': {'C9': {'parent': 'C00', 'ref': 'AN-S-2', 'sha256': 'hash',
                                                'fields': {'name': 'Widget', 'boundaries': {'code': code}},
                                                'source_path': '_SPEC/spec.md'}}, 'packages': {}}
            def findings():
                request = {'root': str(root), 'config': {'python_roots': ['.']},
                           'structure': structure, 'control_root': '_control'}
                result = subprocess.run([sys.executable, '-B', '-P', '-m', 'WORKERS_beta_C69.realization_graph'],
                    input=json.dumps(request), text=True, capture_output=True, timeout=60,
                    env=os.environ | {'PYTHONPATH': str(ENGINE)})
                self.assertEqual(0, result.returncode, result.stderr)
                return [row for row in json.loads(result.stdout)['code_access_findings']
                        if row[1] == 'Widget/client/run.py']
            rows = findings()
            self.assertEqual([(row[4], row[5], row[6]) for row in rows], [
                ('from Widget.lib.parse import run', 'declared_bypass', 'exact import declaration'),
                ('from Widget.lib.parse import *', 'uncertain', 'wildcard import'),
                ('from Widget.lib import run', 'denied', 'code access rule')])
            code['imports'].remove('lib.parse.run')
            self.assertEqual('denied', findings()[0][5])
            code['imports'].append('lib.parse.run')
            self.assertEqual('declared_bypass', findings()[0][5])

    def test_reversed_sibling_layer_is_denied(self):
        with TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            (root / '_control/_SPEC').mkdir(parents=True)
            for name in ('Low_C1', 'High_C2'):
                (root / '_control' / name).mkdir()
            (root / 'Low').mkdir()
            (root / 'High').mkdir()
            (root / 'Low/main.py').write_text('from High.api import run\n')
            (root / 'High/api.py').write_text('def run(): return 1\n')
            def component(name, layer, code=None):
                fields = {'name': name, 'layer': layer}
                if code is not None:
                    fields['boundaries'] = {'code': code}
                return {'parent': 'C00', 'ref': 'AN-S-2', 'sha256': 'hash',
                        'fields': fields, 'source_path': '_SPEC/spec.md'}
            structure = {'model_sha256': 'model', 'project': {'ref': 'AN-S-1', 'sha256': 'hash'},
                         'components': {'C1': component('Low', 1, {'imports': ['High.api.run']}),
                                        'C2': component('High', 2)},
                         'packages': {}}
            request = {'root': str(root), 'config': {'python_roots': ['.']},
                       'structure': structure, 'control_root': '_control'}
            result = subprocess.run([sys.executable, '-B', '-P', '-m', 'WORKERS_beta_C69.realization_graph'],
                input=json.dumps(request), text=True, capture_output=True, timeout=60,
                env=os.environ | {'PYTHONPATH': str(ENGINE)})
            self.assertEqual(0, result.returncode, result.stderr)
            rows = [row for row in json.loads(result.stdout)['code_access_findings'] if row[1] == 'Low/main.py']
            self.assertEqual([('denied', 'sibling layer order')], [(row[5], row[6]) for row in rows])


if __name__ == '__main__':
    unittest.main()
