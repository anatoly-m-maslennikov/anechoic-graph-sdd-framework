import unittest

from SPEC_ENGINE_C75.LAYER_3_LEAN_TRANSLATOR_C84.lean_spec__pub import compile_lean
from SPEC_ENGINE_C75.LAYER_4_TRANSLATION_VALIDATOR_C86.translation_validation__pub import validate_translation
from SPEC_ENGINE_C75.LAYER_4_TRANSLATION_VALIDATOR_C86.LAYER_4_TRANSLATION_VALIDATOR_C86__tests.functional.test_translation_validation import (
    lean_path, model,
)


CONTRACT = 'declare_framing_contract(delimiter=[35], line_endings=[[10],[10,13]])'
SOLUTION = ('declare_framing_solution(opening_prefixes=[[35,10],[35,10,13]], '
            'closing_prefixes=[[10,35],[10,35,10]])')


def framing_model(solution=SOLUTION):
    source = model()
    source['contract']['claims'] = [('python framing', CONTRACT)]
    source['solution']['claims'] = [('python framing', solution)]
    return source


class FramingTranslationTests(unittest.TestCase):
    def setUp(self):
        self.lean = lean_path(self)

    def test_real_program_and_executable_only_mutation(self):
        source = framing_model()
        program = compile_lean(source)['lean']
        result = validate_translation(source, program, lean=self.lean)
        self.assertEqual('unresolved', result['status'])
        self.assertEqual([], result['issues'])
        self.assertTrue(all('byte witnesses' in gap['message'] for gap in result['unresolved']))

        target = 'some (start, close, stop)'
        self.assertEqual(1, program.count(target))
        changed = validate_translation(
            source, program.replace(target, 'some (start, close, stop + 1)', 1), lean=self.lean)
        self.assertEqual('conflicting', changed['status'])
        self.assertEqual({'atom_id': 'S'}, changed['issues'][0]['source'])

    def test_reports_oversized_witness_input_as_unverified(self):
        opening = [[i, 10] for i in range(9)]
        source = framing_model(f'declare_framing_solution(opening_prefixes={opening}, closing_prefixes=[[10,35]])')
        result = validate_translation(source, compile_lean(source)['lean'], lean=self.lean)
        self.assertEqual('unresolved', result['status'])
        self.assertIn({'source': {'atom_id': 'S'}, 'field': 'solution',
                       'message': 'framing witness budget exceeded'}, result['unresolved'])

    def test_rejects_reordering_overlapping_closing_patterns(self):
        source = framing_model()
        program = compile_lean(source)['lean']
        first = 'if raw.take 2 == [10, 35] then some 2'
        second = 'if raw.take 3 == [10, 35, 10] then some 3'
        order = first + '\n  else ' + second
        self.assertEqual(1, program.count(order))
        reordered = second + '\n  else ' + first
        result = validate_translation(source, program.replace(order, reordered, 1), lean=self.lean)
        self.assertEqual('conflicting', result['status'])
        self.assertIn('framing witness disagrees', result['issues'][0]['message'])
