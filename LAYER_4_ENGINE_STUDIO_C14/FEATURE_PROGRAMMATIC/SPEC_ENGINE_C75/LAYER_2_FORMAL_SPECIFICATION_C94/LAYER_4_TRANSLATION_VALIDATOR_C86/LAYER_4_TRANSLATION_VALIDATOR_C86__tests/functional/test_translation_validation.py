import os
import shutil
import unittest
from unittest.mock import patch

from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75._package__shared import verify_formal_chain
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_3_LEAN_TRANSLATOR_C84._package__shared import compile_lean
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_4_TRANSLATION_VALIDATOR_C86._package__shared import validate_translation


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
    def test_exact_code_rules_translate_without_resolving_the_import_graph(self):
        source = model()
        source['manifest']['boundaries']['code'] = {
            'imports': ['C30'], 'exports': {'api.run': 'public'},
        }
        lean = lean_path(self)
        program = compile_lean(source)
        self.assertEqual({'boundaries.code.imports', 'boundaries.code.exports'},
                         {issue['field'] for issue in program['unresolved']})
        receipt = validate_translation(source, program['lean'], lean=lean)
        self.assertEqual('matched', receipt['status'])
        self.assertEqual(source['manifest']['fields'], receipt['claims']['manifest'])
        incorrect = program['lean'].replace('C30', 'C31', 1)
        self.assertEqual('conflicting', validate_translation(source, incorrect, lean=lean)['status'])

    def test_comparison_failure_leaves_chain_incomplete(self):
        with patch('FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.formal_chain__pub.load_boundary_model', return_value=model()), \
             patch('FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.formal_chain__pub.validate_translation',
                   return_value={'status': 'matched', 'claims': {}}), \
             patch('FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.formal_chain__pub.compare_trace_spec',
                   side_effect=ValueError('Lean comparison timed out')):
            result = verify_formal_chain('.', 'C52', {}, {}, {})
        self.assertEqual({'outcome': 'incomplete', 'diagnostics': [
            {'source': {'atom_id': 'M'}, 'field': 'comparison', 'message': 'Lean comparison timed out'}]}, result)

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
        with patch('FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.formal_chain__pub.load_boundary_model', return_value=source), \
             patch('FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.formal_chain__pub.compare_trace_spec',
                   return_value={'status': 'matched'}) as compare:
            compiled = compile_lean(source)
            expected = compiled['claims']
            compiled['claims'] = {}
            with patch('FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.formal_chain__pub.compile_lean', return_value=compiled):
                valid = verify_formal_chain('.', 'C52', {}, {}, {}, lean=lean)
            self.assertEqual('compared', valid['outcome'])
            self.assertEqual('matched', valid['translation']['status'])
            compare.assert_called_once()
            self.assertEqual(expected, compare.call_args.args[1]['claims'])
            compare.reset_mock()
            compiled['lean'] = mutate(compiled['lean'])
            with patch('FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.formal_chain__pub.compile_lean', return_value=compiled):
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

    def test_mixed_framing_projects_both_fences_in_either_order(self):
        lean = lean_path(self)
        declarations = {
            'contract': ('declare_framing_contract(delimiter=[45], line_endings=[[10]])'),
            'solution': ('declare_framing_solution(opening_prefixes=[[45,10]], '
                         'closing_prefixes=[[10,45,10]])'),
        }
        for first in (True, False):
            with self.subTest(framing_first=first):
                source = model()
                for role in declarations:
                    framing = ('python framing', declarations[role])
                    source[role]['claims'] = ([framing] + source[role]['claims'] if first
                                              else source[role]['claims'] + [framing])
                program = compile_lean(source)
                self.assertEqual([], program['unresolved'])
                for role in declarations:
                    self.assertIn('framing', program['claims'][role])
                    self.assertIn('namespace CarrierBody' + role.title(), program['lean'])
                result = validate_translation(source, program['lean'], lean=lean)
                self.assertEqual('unresolved', result['status'])
                self.assertEqual({'contract', 'solution'}, {item['field'] for item in result['unresolved']})
                changed = program['lean'].replace('.body (raw.drop stop)', '.body (raw.drop (stop + 1))', 1)
                result = validate_translation(source, changed, lean=lean)
                self.assertEqual('conflicting', result['status'])
                self.assertEqual({'atom_id': 'C'}, result['issues'][0]['source'])

    def test_shape_chain_compares_validated_declarations(self):
        lean = lean_path(self)
        source = model()
        source['contract']['claims'] = [('python shape',
            "declare_shape_contract(record='Atom', fields={'header':'Header'}, subtype='Plan')")]
        source['solution']['claims'] = [('python shape',
            'class Atom:\n    header: Header\n\nclass Plan(Atom):\n    pass\n')]
        with patch('FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.formal_chain__pub.load_boundary_model', return_value=source):
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
        with patch('FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.formal_chain__pub.load_boundary_model', return_value=source), \
             patch('FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.formal_chain__pub.compare_trace_spec') as compare:
            rejected = verify_formal_chain('.', 'C52', {}, {}, {}, lean=lean)
        self.assertEqual('incomplete', rejected['outcome'])
        self.assertEqual('unresolved', rejected['translation']['status'])
        self.assertEqual('boundaries', rejected['translation']['unresolved'][0]['field'])
        compare.assert_not_called()
