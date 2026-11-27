from unittest.mock import NonCallableMock
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import duckdb

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    NativeCapture,
)

from KERNEL_MIXER_C59.component_metrics import (
    measure_components,
    refresh_spec_sizes,
)
from KERNEL_MIXER_C59.native_projection import replace_component_metrics


class ComponentMetricsTest(unittest.TestCase):
    def test_direct_metrics_and_legacy_exclusions(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder).resolve()
            subprocess.run(['git', 'init', '--quiet', str(root)], check=True)
            self._write_metric_sources(root)
            selection = NonCallableMock(
                spec_set=[
                    'root', 'control_root', 'structure_snapshot',
                    'project_prefix'
                ],
                root=root, control_root=root, structure_snapshot=root/'s',
                project_prefix='CA',
            )
            capture = NativeCapture(atoms=[
                {'id': 'CA-S-1', 'ref': 'CA-S-1', 'status_group': 'Current', '_source_bytes': 20, '_content_bytes': 'é\r\nx'.encode()},
                {'id': 'CA-S-2', 'ref': 'CA-S-2', 'status_group': 'Draft', '_source_bytes': 100, '_content_bytes': b'draft'},
            ], containment=[{'source_ref': 'CA-S-1', 'target_kind': 'Component',
                             'target_ref': 'C1'}], errors={})
            component_paths = {'.': 'C00', 'parent': 'C1', 'parent/child': 'C2'}
            snapshot = NonCallableMock(
                spec_set=[
                    'components'
                ],
                components={'C1': None, 'C2': None})
            package_paths = {'p': 'parent', 't': 'parent/parent__tests',
                             'cp': 'parent/child', 'ct': 'parent/child/child__tests'}
            nodes = [(key, 'package', 'python', path, None, None) for key, path in package_paths.items()]
            source_names = ['parent/code.py', 'parent/child/code.py', 'parent/tests/old.py',
                            'parent/test_old.py', 'parent/parent__tests/test_a.py',
                            'parent/parent__tests/assets/fixture.py', 'parent/child/child__tests/test_child.py']
            module = 'KERNEL_MIXER_C59.component_metrics'
            with (patch(f'{module}.read_structure', return_value=snapshot),
                  patch(f'{module}._component_paths', return_value=component_paths)):
                rows = {row[0]: row[1:] for row in measure_components(
                    selection, capture, dict.fromkeys(source_names), nodes, [('t', 'p'), ('ct', 'cp')])}
            self.assertEqual(rows['C1'], (20, 5, 2, 5, 2, 5, 1, 11, 3))
            self.assertEqual(rows['C2'], (0, 0, 0, 3, 1, 6, 1, 0, 0))
            self.assertEqual(rows['C00'], (0,) * 9)

    def _write_metric_sources(self, root):
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
        put('parent/parent__tests/assets/project/.anechoic_anechoic/fixture.md', b'atom\n')
        put('parent/child/child__tests/test_child.py', b'child\n')
        put('parent/parent__tests/notes.md', b'ordinary documentation')

    def test_no_structure(self):
        self.assertEqual(measure_components(NonCallableMock(
            spec_set=[
                'structure_snapshot'
            ],
            structure_snapshot=None), None, {}, [], []), [])

    def test_spec_refresh_keeps_realization_measurements(self):
        capture = NativeCapture(
            atoms=[
                {
                    "id": "CA-S-1",
                    "ref": "CA-S-1",
                    "status_group": "Current",
                    "_source_bytes": 25,
                    "_content_bytes": b"first\nsecond\n",
                }
            ],
            containment=[
                {
                    "source_ref": "CA-S-1",
                    "target_kind": "Component",
                    "target_ref": "C1",
                }
            ],
            errors={},
        )
        with duckdb.connect() as connection:
            replace_component_metrics(
                connection, [("C1", 20, 6, 1, 5, 2, 5, 1, 11, 3)]
            )
            self.assertEqual(
                [("C1", 25, 13, 2, 5, 2, 5, 1, 11, 3)],
                refresh_spec_sizes(connection, capture, "CA"),
            )


if __name__ == '__main__':
    unittest.main()
