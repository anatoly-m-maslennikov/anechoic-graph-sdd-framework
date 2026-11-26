import copy
import os
import shutil
import unittest
from pathlib import Path

from SPEC_ENGINE_C75.LAYER_1_SPEC_SOURCES_C83.boundary_model__pub import load_boundary_model
from SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C85.trace_manifest__pub import outcome_cases
from SPEC_ENGINE_C75.LAYER_3_LEAN_TRANSLATOR_C84.lean_spec__pub import compile_lean
from SPEC_ENGINE_C75.LAYER_4_SPEC_COMPARISON_C88.trace_spec__pub import compare_trace_workflow


class ComparisonDirectionTests(unittest.TestCase):
    def test_each_comparison_is_a_required_effect(self):
        lean = os.environ.get('ANECHOIC_TEST_LEAN') or shutil.which('lean')
        if not lean:
            self.skipTest('Lean unavailable')
        root = Path(__file__).resolve().parents[4]
        sources = root / '_anechoic_anechoic/LAYER_4_ENGINE_STUDIO_C14/SPEC_ENGINE_C75'
        pins = []
        for atom, component in (('AN-S-4935', 'C75'), ('AN-S-4962', 'C88'), ('AN-S-4963', 'C88')):
            path, = sources.rglob(atom + '@1-draft-*.md')
            pins.append({'path': str(path.relative_to(root)), 'atom_id': atom, 'version': 1,
                         'status': 'draft', 'container_component': component})
        compiled = compile_lean(load_boundary_model(root, 'C88', *pins))
        self.assertEqual(['manifest', 'contract', 'solution'], compiled['compiled_roles'])
        contract, workflow = compiled['claims']['contract'], compiled['claims']['solution']
        targets = ('C88.manifest_contract', 'C88.manifest_solution', 'C88.contract_solution')
        expected = {(target, 'compared') for target in targets}
        cases, _ = outcome_cases(compiled['claims']['manifest']['boundaries'])
        self.assertEqual(expected, set(cases[0]['must_effect']))
        self.assertEqual(expected, set(contract['must_effect']))
        self.assertEqual('matched', compare_trace_workflow(contract, workflow, lean=lean)['status'])
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
