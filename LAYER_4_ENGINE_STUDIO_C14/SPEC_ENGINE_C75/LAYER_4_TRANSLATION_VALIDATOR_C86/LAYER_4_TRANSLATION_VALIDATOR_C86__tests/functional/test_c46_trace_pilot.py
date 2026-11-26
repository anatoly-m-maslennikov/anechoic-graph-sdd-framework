import os
from pathlib import Path
import unittest

from SPEC_ENGINE_C75.LAYER_1_SPEC_SOURCES_C83.boundary_model__pub import load_boundary_model
from SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C85.contract_model__pub import parse_trace_contract
from SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C85.workflow_model__pub import normalize_workflow, parse_workflow
from SPEC_ENGINE_C75.LAYER_3_LEAN_TRANSLATOR_C84.trace_lean__pub import _program
from SPEC_ENGINE_C75.LAYER_4_TRANSLATION_VALIDATOR_C86.LAYER_4_TRANSLATION_VALIDATOR_C86__tests.functional.trace_pilot import PINS, validate_c46_trace

ROOT = Path(__file__).resolve().parents[5]
LEAN = os.environ.get('ANECHOIC_TEST_LEAN', 'lean')
ACTION = 'workbench_frontend_check_view'


def artifact():
    model = load_boundary_model(ROOT, 'C46', *PINS)
    contracts = [parse_trace_contract(source) for _, source in model['contract']['claims']]
    workflows = [parse_workflow(source) for _, source in model['solution']['claims']]
    contract = next(c for c in contracts if c['action'] == ACTION and c['output'] == 'checked')
    workflow = next(w for w in workflows if w['action'] == ACTION)
    return _program(contract, {'action': ACTION, **normalize_workflow(workflow['machine'])})


class C46TracePilotTests(unittest.TestCase):
    def test_actual_trace_and_compiling_early_display_mutant(self):
        program = artifact()
        valid = validate_c46_trace(ROOT, program, lean=LEAN)
        self.assertEqual('matched', valid['status'])
        self.assertEqual('matched', valid['source_status'])
        self.assertEqual(['matched'], valid['lean_status'])
        self.assertEqual([('AN-S-3060', 10), ('AN-S-3306', 3), ('AN-S-3372', 3)],
                         [(source['atom_id'], source['version']) for source in valid['sources']])
        original = '⟨"idle", "waiting", "trigger"'
        mutant = '⟨"idle", "showing_verdict", "trigger"'
        self.assertEqual(1, program.count(original))
        result = validate_c46_trace(ROOT, program.replace(original, mutant, 1), lean=LEAN)
        self.assertEqual('conflicting', result['status'])
        self.assertEqual(['conflicting'], result['lean_status'])

    def test_wrong_lean_verdict_with_unchanged_edges_is_rejected(self):
        program = artifact()
        marker = 'def orderStatus (order : Effect × Effect) : String :='
        self.assertEqual(1, program.count(marker))
        before, after = program.split(marker)
        needle = 'then "conflicting" else "matched"'
        self.assertEqual(1, after.count(needle))
        mutant = before + marker + after.replace(needle, 'then "matched" else "conflicting"', 1)
        result = validate_c46_trace(ROOT, mutant, lean=LEAN)
        self.assertEqual('conflicting', result['status'])
        self.assertEqual('matched', result['source_status'])
        self.assertEqual(['conflicting'], result['lean_status'])


if __name__ == '__main__':
    unittest.main()
