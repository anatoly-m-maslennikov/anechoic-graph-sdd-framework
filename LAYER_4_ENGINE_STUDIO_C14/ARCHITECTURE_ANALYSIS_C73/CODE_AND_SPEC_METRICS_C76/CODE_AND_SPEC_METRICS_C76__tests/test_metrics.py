import unittest

from ..metrics__shared import code_rows, spec_rows


class MetricsTests(unittest.TestCase):
    def test_code_attribution_and_unclassified(self):
        nodes = [
            ['p', 'package', 'python', 'a', None, None, None],
            ['t', 'package', 'python', 'a/a__tests', None, None, 'Test Package'],
            ['c', 'package', 'python', 'a/child', None, None, None],
            ['m', 'module', 'python', 'a/x.py', 'parsed', 'p', None],
            ['u', 'module', 'python', 'a/test_lonely.py', 'parsed', 'p', None],
            ['s', 'module', 'python', 'a/a__tests/test_x.py', 'parsed', 't', None],
            ['c1', 'module', 'python', 'a/child/x.py', 'read_error', 'c', None],
        ]
        sizes = {n[3]: (10, 1) for n in nodes if n[1] == 'module'}
        rows = code_rows(nodes, [('t', 'p'), ('t', 'C1')], {'.': 'C00', 'a': 'C1', 'a/child': 'C2'}, sizes, {'a/a__tests/assets/x': ('t', 4, None)})
        self.assertIn(['Component', 'C1', 'a/a__tests/test_x.py', 'test_code', 10, 1], rows)
        self.assertEqual(1, sum(r[:3] == ['Component', 'C1', 'a/a__tests/test_x.py'] for r in rows))
        self.assertIn(['Package', 'p', 'a/a__tests/assets/x', 'test_assets', 4, None], rows)
        self.assertIn(['Package', 'p', 'a/test_lonely.py', 'unclassified', 10, 1], rows)
        self.assertIn(['Component', 'C2', 'a/child/x.py', 'unclassified', 10, 1], rows)
        self.assertFalse(any(r[1] == 'C1' and r[2] == 'a/child/x.py' for r in rows))

    def test_cross_component_tests_and_unbound_paths(self):
        nodes = [
            ['p', 'package', 'python', 'a', None, None, None],
            ['t', 'package', 'python', 'b/b__tests', None, None, 'Test Package'],
            ['u', 'package', 'python', 'b/unbound__tests', None, None, 'Test Package'],
            ['m', 'module', 'python', 'b/b__tests/test_x.py', 'parsed', 't', None],
            ['n', 'module', 'python', 'b/unbound__tests/test_y.py', 'parsed', 'u', None],
        ]
        rows = code_rows(nodes, [('t', 'p')], {'.': 'C00', 'a': 'C1', 'b': 'C2'},
                                 {'b/b__tests/test_x.py': (10, 1), 'b/unbound__tests/test_y.py': (5, 1)},
                                 {'b/b__tests/assets/x': ('t', 4, None),
                                  'b/unbound__tests/assets/y': ('u', 2, None)})
        self.assertEqual({tuple(r) for r in rows if r[2].startswith('b/b__tests/')}, {
            ('Component', 'C1', 'b/b__tests/test_x.py', 'test_code', 10, 1),
            ('Package', 'p', 'b/b__tests/test_x.py', 'test_code', 10, 1),
            ('Component', 'C1', 'b/b__tests/assets/x', 'test_assets', 4, None),
            ('Package', 'p', 'b/b__tests/assets/x', 'test_assets', 4, None),
        })
        self.assertIn(['Component', 'C2', 'b/unbound__tests/test_y.py', 'unclassified', 5, 1], rows)
        self.assertIn(['Package', 'u', 'b/unbound__tests/assets/y', 'unclassified', 2, None], rows)

    def test_spec_carrier_measurements(self):
        atoms = [{'id': 'AN-S-1', 'ref': 'AN-S-1', '_exact_ref': 'AN-S-1@1',
                  'status_group': 'Current', '_source_bytes': 20, '_source_lines': 3,
                  '_content_bytes': b'a\nb\n'},
                 {'id': 'AN-S-2', 'status_group': 'Draft'},
                 {'id': 'AN-T-1', 'status_group': 'Current'}]
        self.assertEqual([['AN-S-1@1', 20, 3, 4, 2]], spec_rows(atoms))


if __name__ == '__main__':
    unittest.main()
