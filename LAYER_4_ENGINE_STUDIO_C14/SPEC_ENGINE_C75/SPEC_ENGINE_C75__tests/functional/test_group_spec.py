import unittest
from unittest.mock import patch

from SPEC_ENGINE_C75.boundary_sources import recognized_claim
from SPEC_ENGINE_C75.group_spec__pub import (
    check_group_spec,
    group_to_mermaid,
    parse_group,
)

LEAN = '/Users/am/.bb/thread-storage/thr_8zxi7bmrvv/pastalean-trial/lean-4.31.0-darwin_aarch64/bin/lean'
CONTRACT = "declare_group_contract(roles={'generation': 'C50', 'core': 'C52'}, entry_points=('api',))"
SOLUTION = "component_group(roles={'generation': 'C50', 'core': 'C52'}, entry_points=('api',))"


def model(contract=CONTRACT, solution=SOLUTION, server=None):
    boundaries = {'io': {'server': {'api': {}} if server is None else server}}
    return {'component_id': 'C51',
            'manifest': {'source': {'atom_id': 'M'}, 'fields': {'component_id': 'C51', 'name': 'Model',
                                                                  'boundaries': boundaries}, 'boundaries': boundaries},
            'contract': {'source': {'atom_id': 'C'}, 'claims': [('python group', contract)]},
            'solution': {'source': {'atom_id': 'S'}, 'claims': [('python group', solution)]}}


class GroupSpecTests(unittest.TestCase):
    def check(self, *, children=('C50', 'C52'), contract=CONTRACT, solution=SOLUTION, server=None,
              current_record_count=None):
        with patch('SPEC_ENGINE_C75.boundary_model.load_boundary_model', return_value=model(contract, solution, server)):
            return check_group_spec('.', 'C51', {}, {}, {}, structure_children=children,
                                    current_record_count=current_record_count, lean=LEAN)

    def test_structure_and_entrypoint_comparison(self):
        result = self.check()
        self.assertEqual('matched', result['directions']['manifest_contract']['status'])
        self.assertEqual('matched', result['directions']['contract_solution']['status'])
        self.assertEqual(['C50', 'C52'], result['structure_children'])
        self.assertIn('C51 -->|generation| C50', result['mermaid'])
        for children in (('C50',), ('C50', 'C53')):
            self.assertEqual('conflicting', self.check(children=children)['directions']['manifest_contract']['status'])
        result = self.check(server={'api': {}, 'extra': {}})
        self.assertEqual('conflicting', result['directions']['manifest_solution']['status'])
        result = self.check(solution=SOLUTION.replace("'generation': 'C50', 'core': 'C52'",
                                                      "'generation': 'C52', 'core': 'C50'"))
        self.assertEqual('conflicting', result['directions']['contract_solution']['status'])
        self.assertTrue(self.check(server='unsupported')['unresolved'])

    def test_omitted_entry_points_remain_unknown(self):
        contract = "declare_group_contract(roles={'generation': 'C50', 'core': 'C52'})"
        solution = "component_group(roles={'generation': 'C50', 'core': 'C52'})"
        self.assertEqual({'roles': {'generation': 'C50', 'core': 'C52'}}, parse_group(solution, 'solution'))
        result = self.check(contract=contract, solution=solution, server='unsupported')
        self.assertEqual('unresolved', result['status'])
        self.assertEqual('matched', result['directions']['contract_solution']['status'])
        self.assertEqual({'M', 'C', 'S'}, {gap['source']['atom_id'] for gap in result['unresolved']})
        result = self.check(contract=CONTRACT, solution=solution)
        self.assertEqual('unresolved', result['directions']['contract_solution']['status'])
        result = self.check(contract=contract, solution=solution.replace("'C52'", "'C53'"))
        self.assertEqual('conflicting', result['directions']['contract_solution']['status'])
        empty = solution[:-1] + ', entry_points=[])'
        result = self.check(contract=CONTRACT, solution=empty)
        self.assertEqual('conflicting', result['directions']['contract_solution']['status'])
        self.assertEqual([], parse_group(empty, 'solution')['entry_points'])

    def test_current_record_count(self):
        contract = CONTRACT[:-1] + ', current_record_count=500)'
        solution = SOLUTION[:-1] + ', current_record_count=500)'
        result = self.check(contract=contract, solution=solution, current_record_count=500)
        self.assertTrue(all(direction['status'] == 'matched' for direction in result['directions'].values()))
        self.assertEqual('conflicting', self.check(contract=contract, solution=solution,
                                                    current_record_count=499)['status'])
        result = self.check(contract=contract, solution=solution)
        self.assertEqual('unresolved', result['status'])
        self.assertEqual('unresolved', result['directions']['manifest_contract']['status'])
        self.assertIn('M', {gap['source']['atom_id'] for gap in result['unresolved']})
        result = self.check(contract=CONTRACT, solution=solution, current_record_count=500)
        self.assertEqual('unresolved', result['directions']['contract_solution']['status'])
        self.assertIn('C', {gap['source']['atom_id'] for gap in result['unresolved']})
        for invalid in ('-1', 'True', "'500'", '1.5'):
            with self.assertRaises(ValueError):
                parse_group(SOLUTION[:-1] + f', current_record_count={invalid})', 'solution')
        with self.assertRaises(ValueError):
            self.check(current_record_count=True)

    def test_safe_literals_and_empty_group(self):
        empty = 'component_group(roles={}, entry_points=())'
        self.assertTrue(recognized_claim('solution', 'python group', empty))
        self.assertEqual({'roles': {}, 'entry_points': []}, parse_group(empty, 'solution'))
        for bad in (empty.replace('{}', "{'x': run()}"),
                    empty.replace('{}', "{'x': 'C1', 'x': 'C2'}"), empty + '\nrun()'):
            with self.assertRaises((ValueError, TypeError)):
                parse_group(bad, 'solution')
        with self.assertRaises(ValueError):
            self.check(children=('C50', 'C50'))
        with self.assertRaises(ValueError):
            self.check(children=('C51',))
        with self.assertRaises(ValueError):
            group_to_mermaid({'roles': {}}, 'C51]; malicious')
        shared = parse_group("component_group(roles={'a': 'C50', 'b': 'C50'}, entry_points=())", 'solution')
        self.assertEqual({'a': 'C50', 'b': 'C50'}, shared['roles'])
