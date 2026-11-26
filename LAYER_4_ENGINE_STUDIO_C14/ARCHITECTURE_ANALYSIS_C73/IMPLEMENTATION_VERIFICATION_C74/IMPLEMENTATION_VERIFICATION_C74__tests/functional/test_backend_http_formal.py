"""Check that C45 formal comparison reports the target's unsupported claim."""
from pathlib import Path
import unittest

from ARCHITECTURE_ANALYSIS_C73.IMPLEMENTATION_VERIFICATION_C74.backend_http_formal import _carrier, _facts

ROOT = Path(__file__).resolve().parents[5]


class FormalHttpTests(unittest.TestCase):
    def test_target_contract_and_solution_are_distinct_revisions(self):
        _, contract = _carrier(ROOT, 'contract', 'AN-S-3185', 'C45')
        solution, _ = _carrier(ROOT, 'solution', 'AN-S-3371', 'C45')
        self.assertEqual(contract['version'], 12)
        self.assertIn('AN-S-3185@11', solution.metadata['relations']['IS_SOLUTION_FOR'])
        with self.assertRaisesRegex(ValueError, 'python contract formal claim'):
            _facts(ROOT)
