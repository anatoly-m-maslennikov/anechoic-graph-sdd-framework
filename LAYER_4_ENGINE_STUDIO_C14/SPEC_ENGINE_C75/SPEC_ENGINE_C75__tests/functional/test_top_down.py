import os
import shutil
import unittest
from unittest.mock import patch

from SPEC_ENGINE_C75.LAYER_4_SPEC_COMPARISON_C88.top_down__pub import compare_obligations


class TopDownTests(unittest.TestCase):
    def test_lean_compares_all_directions_and_preserves_pins(self):
        lean = os.environ.get('ANECHOIC_TEST_LEAN') or shutil.which('lean')
        if lean is None:
            self.skipTest('Lean executable unavailable')
        sources = {role: {'atom_id': role, 'version': '1'}
                   for role in ('manifest', 'contract', 'solution')}
        obligations = {'manifest': {'equal': {'x': 1}, 'different': 1, 'missing': None},
                       'contract': {'equal': {'x': 1}, 'different': 2}, 'solution': {}}
        result = compare_obligations(sources, obligations, lean=lean)
        self.assertEqual(sources, result['sources'])
        direction = result['directions']['manifest_contract']
        self.assertEqual('conflicting', direction['status'])
        self.assertEqual({'different': 'conflicting', 'equal': 'matched', 'missing': 'unresolved'},
                         {fact['key']: fact['status'] for fact in direction['facts']})
        self.assertEqual('unresolved', result['directions']['contract_solution']['status'])
        empty = compare_obligations(sources, {role: {} for role in sources}, lean=lean)
        self.assertEqual('unresolved', empty['status'])
        self.assertTrue(all(direction['status'] == 'unresolved'
                            for direction in empty['directions'].values()))

    def test_lean_failure_is_explicit(self):
        roles = ('manifest', 'contract', 'solution')
        with patch('subprocess.run', side_effect=FileNotFoundError('missing Lean')):
            with self.assertRaisesRegex(ValueError, 'Lean comparison failed'):
                compare_obligations({role: {} for role in roles}, {role: {} for role in roles})
