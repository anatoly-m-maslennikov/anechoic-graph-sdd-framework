import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from SPEC_ENGINE_C75.boundary_sources import recognized_claim
from SPEC_ENGINE_C75.shape_spec__pub import check_shape_spec, parse_shape

LEAN = '/Users/am/.bb/thread-storage/thr_8zxi7bmrvv/pastalean-trial/lean-4.31.0-darwin_aarch64/bin/lean'
CONTRACT = "declare_shape_contract(record='Atom', fields={'header':'Header','content':'Content'}, subtype='Plan')"
SOLUTION = 'class Atom:\n    header: Header\n    content: Content\n\nclass Plan(Atom):\n    pass\n'


def model(solution=SOLUTION):
    return {'component_id': 'C52',
            'manifest': {'source': {'atom_id': 'M'}, 'fields': {'component_id': 'C52', 'name': 'Core'}, 'boundaries': None},
            'contract': {'source': {'atom_id': 'C'}, 'claims': [('python shape', CONTRACT)]},
            'solution': {'source': {'atom_id': 'S'}, 'claims': [('python shape', solution)]}}


class ShapeSpecTests(unittest.TestCase):
    def check(self, solution):
        with patch('SPEC_ENGINE_C75.boundary_model.load_boundary_model', return_value=model(solution)):
            return check_shape_spec('.', 'C52', {}, {}, {}, lean=LEAN)

    def test_real_lean_and_observed_conflicts(self):
        result = self.check(SOLUTION)
        self.assertEqual('unresolved', result['status'])
        self.assertEqual('matched', result['directions']['contract_solution']['status'])
        self.assertIn('Atom <|-- Plan', result['mermaid'])
        self.assertIn('«header» : «Header»', result['lean'])
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'Shape.lean'
            path.write_text(result['lean'])
            checked = subprocess.run([LEAN, str(path)], capture_output=True, text=True, timeout=45, check=False)
            self.assertEqual(0, checked.returncode, checked.stdout + checked.stderr)
        for changed in (SOLUTION.replace('    header: Header\n', ''),
                        SOLUTION.replace('header: Header', 'header: Other'),
                        SOLUTION.replace('Plan(Atom)', 'Plan')):
            with self.subTest(changed=changed):
                self.assertEqual('conflicting', self.check(changed)['directions']['contract_solution']['status'])

    def test_rejects_executable_and_duplicate_syntax(self):
        self.assertTrue(recognized_claim('solution', 'python shape', SOLUTION))
        for role, source in (('solution', SOLUTION.replace('Plan(Atom)', 'Plan(Unknown)')),
                             ('solution', SOLUTION.replace('    pass', '    print(1)')),
                             ('solution', SOLUTION.replace('    content: Content', '    header: Content')),
                             ('solution', SOLUTION + '\nprint(1)'),
                             ('contract', CONTRACT.replace("'content':'Content'", "'header':'Content'"))):
            with self.subTest(source=source), self.assertRaises(ValueError):
                parse_shape(source, role)
