import copy
import os
import shutil
import unittest
from pathlib import Path

from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_2_SPEC_READING_C83._package__shared import load_boundary_model
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_2_SPEC_READING_C83.SPECIFICATION_MODEL_C85._package__shared import outcome_cases
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_3_LEAN_TRANSLATOR_C84._package__shared import compile_lean
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_4_SPEC_COMPARISON_C88._package__shared import (
    compare_obligations,
    compare_trace_workflow,
)


_C94_SPECS = Path(
    '_anechoic_anechoic/LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC_C15/'
    'SPEC_ENGINE_C75/LAYER_2_FORMAL_SPECIFICATION_C94'
)
_SOURCES = (
    ('01_TIER_1_ARCHITECTURE/AN-S-4935-SPEC-COMPONENT_MANIFEST--declare-spec-comparison.md',
     'AN-S-4935', 'C94', '929c914afb640966de04ce2f96420b484a3eaaab991066c2eaf3203d10b2d9cd'),
    ('LAYER_4_SPEC_COMPARISON_C88/AN-S-5030-DES-SOLUTION--compare-formal-spec-obligations.md',
     'AN-S-5030', 'C88', 'ad6af299477be8d524d398f808d99acd79b9ebc96361d7bb44a413dfe0d1822d'),
)


class ComparisonDirectionTests(unittest.TestCase):
    def test_each_comparison_is_a_required_effect(self):
        lean = os.environ.get('ANECHOIC_TEST_LEAN') or shutil.which('lean')
        if not lean:
            self.skipTest('Lean unavailable')
        root = Path(__file__).resolve().parents[5]
        pins = []
        for relative, atom, component, digest in _SOURCES:
            path = _C94_SPECS / relative
            pins.append({'path': path.as_posix(), 'atom_id': atom, 'version': 1,
                         'status': 'active', 'container_component': component, 'sha256': digest})
        compiled = compile_lean(load_boundary_model(root, 'C88', *pins))
        self.assertEqual(['manifest', 'contract', 'solution'], compiled['compiled_roles'])
        contract, workflow = compiled['claims']['contract'], compiled['claims']['solution']
        targets = ('C88.manifest_contract', 'C88.manifest_solution', 'C88.contract_solution')
        expected = {(target, 'compared') for target in targets}
        cases, _ = outcome_cases(compiled['claims']['manifest']['boundaries'])
        self.assertEqual(expected, set(cases[0]['must_effect']))
        self.assertEqual(expected, set(contract['must_effect']))
        self.assertEqual('matched', compare_trace_workflow(contract, workflow, lean=lean)['status'])
        self._assert_public_comparison(pins, contract, lean)
        for target in targets:
            with self.subTest(target=target):
                mutant = copy.deepcopy(workflow)
                for state in mutant['states']:
                    for transition in state['transitions']:
                        if transition['expect'].get('target') == target:
                            transition['expect']['target'] = 'missing'
                report = compare_trace_workflow(contract, mutant, lean=lean)
                self.assertEqual('conflicting', report['status'])
                self.assertTrue(any(f['key'] == 'must_effect' and f['left'][0] == target
                                    and f['status'] == 'conflicting' for f in report['facts']))

    def _assert_public_comparison(self, pins, contract, lean):
        sources = {'manifest': pins[0], 'contract': pins[0], 'solution': pins[1]}
        obligations = {'manifest': {'spec_value': 1}, 'contract': {'contract_value': 1},
                       'solution': {'spec_value': 1, 'contract_value': 2}}
        report = compare_obligations(sources, obligations, lean=lean)
        directions = [target.removeprefix('C88.') for target, _ in contract['must_effect']]
        self.assertEqual(directions, list(report['directions']))
        facts = {
            'manifest_contract': {'key': 'spec_value', 'left': 1, 'right': None, 'status': 'unresolved'},
            'manifest_solution': {'key': 'spec_value', 'left': 1, 'right': 1, 'status': 'matched'},
            'contract_solution': {'key': 'contract_value', 'left': 1, 'right': 2, 'status': 'conflicting'},
        }
        self.assertEqual({'sources': sources, 'status': 'conflicting', 'directions': {
            name: {'status': fact['status'], 'facts': [fact]} for name, fact in facts.items()
        }}, report)
