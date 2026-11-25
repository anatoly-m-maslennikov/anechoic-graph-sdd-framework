import os
import shutil
import unittest
from unittest.mock import patch

from SPEC_ENGINE_C75.formal_chain__pub import verify_formal_chain
from SPEC_ENGINE_C75.LAYER_3_LEAN_TRANSLATOR_C84.lean_spec__pub import compile_lean
from SPEC_ENGINE_C75.LAYER_4_TRANSLATION_VALIDATOR_C86.translation_validation__pub import validate_translation


CONTRACT = r'''declare_trace_contract(action='invoke', output='done', must_effect=(
    ('store', 'saved', {'flag': False, 'zero': 0, 'nothing': None, 'text': 'λ"\\\n\t'}),))'''
SOLUTION = '''component_workflow(component='C52', action='invoke', machine={
    'id': 'invoke', 'initial': 'start', 'states': {
        'start': {'on': {'finish': {'target': 'done', 'guard': {
            'type': 'matchesTrace', 'params': {'kind': 'output', 'outcome': 'done',
                                              'detail': {'fraction': 1.0}}}}}},
        'done': {'type': 'final'}}})'''


def model():
    boundaries = {'state': {'reads': [], 'writes': []}}
    return {'component_id': 'C52',
            'manifest': {'source': {'atom_id': 'M'},
                         'fields': {'component_id': 'C52', 'name': 'Core', 'boundaries': boundaries},
                         'boundaries': boundaries},
            'contract': {'source': {'atom_id': 'C'}, 'claims': [('python trace', CONTRACT)]},
            'solution': {'source': {'atom_id': 'S'}, 'claims': [('python', SOLUTION)]}}


def lean_path(test):
    lean = os.environ.get('ANECHOIC_TEST_LEAN') or os.environ.get('LEAN_BIN') or shutil.which('lean')
    test.assertTrue(lean, 'Set ANECHOIC_TEST_LEAN or LEAN_BIN, or put lean on PATH')
    return lean


def mutate(program):
    target = r'flag\": false'
    if program.count(target) != 1:
        raise AssertionError('Expected the contract flag in the emitted Lean program')
    return program.replace(target, r'flag\": true ', 1)


class TranslationValidationTests(unittest.TestCase):
    def test_comparison_failure_leaves_chain_incomplete(self):
        with patch('SPEC_ENGINE_C75.formal_chain__pub.load_boundary_model', return_value=model()), \
             patch('SPEC_ENGINE_C75.formal_chain__pub.validate_translation',
                   return_value={'status': 'matched', 'claims': {}}), \
             patch('SPEC_ENGINE_C75.formal_chain__pub.compare_trace_spec',
                   side_effect=ValueError('Lean comparison timed out')):
            result = verify_formal_chain('.', 'C52', {}, {}, {})
        self.assertEqual({'outcome': 'incomplete', 'diagnostics': ['Lean comparison timed out']}, result)

    def test_json_values_and_unchanged_source_target_mutation(self):
        lean = lean_path(self)
        source = model()
        program = compile_lean(source)['lean']
        valid = validate_translation(source, program, lean=lean)
        target = r'fraction\": 1.0'
        self.assertEqual(1, program.count(target))
        changed = validate_translation(source, program.replace(
            target, r'fraction\": 1.00000000000000000001', 1), lean=lean)
        self.assertEqual('matched', valid['status'])
        self.assertEqual([], valid['issues'])
        self.assertEqual('conflicting', changed['status'])
        self.assertTrue(any(issue['field'] == 'solution' and issue['source'] == {'atom_id': 'S'}
                            for issue in changed['issues']))
        self.assertEqual(SOLUTION, source['solution']['claims'][0][1])

    def test_chain_compares_only_after_translation_matches(self):
        lean = lean_path(self)
        source = model()
        with patch('SPEC_ENGINE_C75.formal_chain__pub.load_boundary_model', return_value=source), \
             patch('SPEC_ENGINE_C75.formal_chain__pub.compare_trace_spec',
                   return_value={'status': 'matched'}) as compare:
            compiled = compile_lean(source)
            expected = compiled['claims']
            compiled['claims'] = {}
            with patch('SPEC_ENGINE_C75.formal_chain__pub.compile_lean', return_value=compiled):
                valid = verify_formal_chain('.', 'C52', {}, {}, {}, lean=lean)
            self.assertEqual('compared', valid['outcome'])
            self.assertEqual('matched', valid['translation']['status'])
            compare.assert_called_once()
            self.assertEqual(expected, compare.call_args.args[1]['claims'])
            compare.reset_mock()
            compiled['lean'] = mutate(compiled['lean'])
            with patch('SPEC_ENGINE_C75.formal_chain__pub.compile_lean', return_value=compiled):
                rejected = verify_formal_chain('.', 'C52', {}, {}, {}, lean=lean)
            self.assertEqual('incomplete', rejected['outcome'])
            self.assertEqual('conflicting', rejected['translation']['status'])
            compare.assert_not_called()

    def test_framing_witnesses_report_their_bound(self):
        lean = lean_path(self)
        source = model()
        source['contract']['claims'] = [('python framing',
            'declare_framing_contract(delimiter=[45,45,45], line_endings=[[10]])')]
        source['solution']['claims'] = [('python framing',
            'declare_framing_solution(opening_prefixes=[[45,45,45,10]], '
            'closing_prefixes=[[10,45,45,45,10]])')]
        program = compile_lean(source)['lean']
        result = validate_translation(source, program, lean=lean)
        self.assertEqual('unresolved', result['status'])
        self.assertEqual({'contract', 'solution'}, {item['field'] for item in result['unresolved']})
        self.assertTrue(all('byte witnesses' in item['message'] for item in result['unresolved']))
        changed = validate_translation(source, program.replace(
            '.body (raw.drop stop)', '.body (raw.drop (stop + 1))', 1), lean=lean)
        self.assertEqual('conflicting', changed['status'])
        self.assertEqual({'atom_id': 'C'}, changed['issues'][0]['source'])
        self.assertIn('framing witness disagrees', changed['issues'][0]['message'])

    def test_shape_chain_compares_validated_declarations(self):
        lean = lean_path(self)
        source = model()
        source['contract']['claims'] = [('python shape',
            "declare_shape_contract(record='Atom', fields={'header':'Header'}, subtype='Plan')")]
        source['solution']['claims'] = [('python shape',
            'class Atom:\n    header: Header\n\nclass Plan(Atom):\n    pass\n')]
        with patch('SPEC_ENGINE_C75.formal_chain__pub.load_boundary_model', return_value=source):
            result = verify_formal_chain('.', 'C52', {}, {}, {}, lean=lean)
        self.assertEqual('compared', result['outcome'], result)
        self.assertEqual('matched', result['translation']['status'])
        self.assertEqual('matched', result['directions']['contract_solution']['status'])
        mutated = result['lean'].replace('«f_header» : «T_Header»',
                                         '«f_other» : «T_Header»', 1)
        result = validate_translation(source, mutated, lean=lean)
        self.assertEqual('conflicting', result['status'])
        self.assertTrue(any(item['field'] == 'contract.shape' for item in result['issues']))

    def test_unmodeled_boundaries_block_comparison(self):
        lean = lean_path(self)
        source = model()
        source['manifest']['fields'].pop('boundaries')
        source['manifest']['boundaries'] = None
        with patch('SPEC_ENGINE_C75.formal_chain__pub.load_boundary_model', return_value=source), \
             patch('SPEC_ENGINE_C75.formal_chain__pub.compare_trace_spec') as compare:
            rejected = verify_formal_chain('.', 'C52', {}, {}, {}, lean=lean)
        self.assertEqual('incomplete', rejected['outcome'])
        self.assertEqual('unresolved', rejected['translation']['status'])
        self.assertEqual('boundaries', rejected['translation']['unresolved'][0]['field'])
        compare.assert_not_called()
