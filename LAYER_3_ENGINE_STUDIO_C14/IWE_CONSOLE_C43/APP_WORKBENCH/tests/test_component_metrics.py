import subprocess
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.component_metrics import measure_components


class ComponentMetricsTest(unittest.TestCase):
    def test_direct_metrics_and_legacy_exclusions(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder).resolve()
            subprocess.run(['git', 'init', '--quiet', str(root)], check=True)
            def put(name, data):
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
            put('parent/code.py', b'x\r\ny\n')
            put('parent/child/code.py', 'é\n'.encode())
            put('parent/tests/old.py', b'legacy')
            put('parent/test_old.py', b'legacy')
            put('parent/parent__tests/test_a.py', b'test\n')
            put('parent/parent__tests/assets/fixture.py', b'\xff\x00')
            put('parent/parent__tests/assets/text.txt', b'a\r\nb')
            put('parent/parent__tests/notes.md', b'ordinary documentation')
            selection = SimpleNamespace(root=root, control_root=root, structure_snapshot=root/'s', project_prefix='CA')
            capture = SimpleNamespace(atoms=[
                {'id': 'CA-S-1', 'ref': 'CA-S-1', 'status_group': 'Current', '_source_bytes': 20, '_content_bytes': 'é\r\nx'.encode()},
                {'id': 'CA-S-2', 'ref': 'CA-S-2', 'status_group': 'Draft', '_source_bytes': 100, '_content_bytes': b'draft'},
            ], containment=[{'source_ref': 'CA-S-1', 'target_kind': 'Component', 'target_ref': 'C1'}])
            entries = {'C00': {'id': 'C00', 'kind': 'component'}, 'C1': {'id': 'C1', 'kind': 'component'}, 'C2': {'id': 'C2', 'kind': 'component'}}
            class Ownership:
                def __init__(self): self.entries = entries
                def owner(self, path):
                    return entries['C2' if 'child' in str(path) else 'C1']
            nodes = [('p', 'package', 'python', 'parent', None, None), ('t', 'package', 'python', 'parent/parent__tests', None, None)]
            source_names = ['parent/code.py', 'parent/child/code.py', 'parent/tests/old.py', 'parent/test_old.py', 'parent/parent__tests/test_a.py', 'parent/parent__tests/assets/fixture.py']
            with patch('APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.component_metrics.read_structure', return_value=SimpleNamespace(components={'C1': None, 'C2': None})), patch('APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.component_metrics.build_code_access_ownership', return_value=Ownership()):
                rows = dict((row[0], row[1:]) for row in measure_components(selection, capture, dict.fromkeys(source_names), nodes, [('t', 'p')]))
            self.assertEqual(rows['C1'], (20, 5, 2, 5, 2, 5, 1, 6, 2))
            self.assertEqual(rows['C2'], (0, 0, 0, 3, 1, 0, 0, 0, 0))
            self.assertEqual(rows['C00'], (0,) * 9)

    def test_no_structure(self):
        self.assertEqual(measure_components(SimpleNamespace(structure_snapshot=None), None, {}, [], []), [])


if __name__ == '__main__':
    unittest.main()
