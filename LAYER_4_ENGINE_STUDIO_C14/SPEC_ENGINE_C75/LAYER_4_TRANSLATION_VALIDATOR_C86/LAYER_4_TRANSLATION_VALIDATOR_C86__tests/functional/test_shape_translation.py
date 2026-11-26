import unittest

from SPEC_ENGINE_C75.LAYER_3_LEAN_TRANSLATOR_C84.lean_spec__pub import compile_lean
from SPEC_ENGINE_C75.LAYER_4_TRANSLATION_VALIDATOR_C86.translation_validation__pub import validate_translation
from SPEC_ENGINE_C75.LAYER_4_TRANSLATION_VALIDATOR_C86.LAYER_4_TRANSLATION_VALIDATOR_C86__tests.functional.test_translation_validation import (
    lean_path, model,
)


CONTRACT = "declare_shape_contract(record='Atom', fields={'header':'Header','content':'Content'}, subtype='Plan')"
SOLUTION = 'class Atom:\n    header: Header\n    content: Content\n\nclass Plan(Atom):\n    pass\n'
TARGET = '''namespace Shape_contract
structure R_Atom (T_Content T_Header : Type) where
  f_header : T_Header
  f_content : T_Content
structure S_Plan (T_Content T_Header : Type) extends R_Atom T_Content T_Header where
end Shape_contract
'''


class ShapeTranslationTests(unittest.TestCase):
    def setUp(self):
        self.lean = lean_path(self)
        self.source = model()
        self.source['contract']['claims'] = [('python shape', CONTRACT)]
        self.source['solution']['claims'] = [('python shape', SOLUTION)]
        generated = compile_lean(self.source)['lean']
        declarations, _, tail = generated.partition('namespace Shape_contract')
        _, _, solution = tail.partition('end Shape_contract')
        self.program = declarations + TARGET + solution

    def test_independent_valid_shape(self):
        result = validate_translation(self.source, self.program, lean=self.lean)
        self.assertEqual('matched', result['status'])

    def test_well_typed_mutations_return_conflicts(self):
        variants = [
            TARGET.replace('S_Plan', 'S_Other'),
            TARGET.replace('  f_header : T_Header\n', ''),
            TARGET.replace('  f_header : T_Header\n', '  f_header : T_Header\n  f_extra : T_Header\n'),
            TARGET.replace('f_header : T_Header', 'f_header : T_Content'),
            TARGET.replace(' extends R_Atom T_Content T_Header', ''),
            TARGET.replace('extends R_Atom T_Content T_Header', 'extends R_Atom T_Header T_Content'),
            TARGET.replace('extends R_Atom T_Content T_Header where',
                           'extends R_Atom T_Content T_Header where\n  extra : T_Header'),
        ]
        for variant in variants:
            with self.subTest(variant=variant):
                result = validate_translation(self.source, self.program.replace(TARGET, variant, 1), lean=self.lean)
                self.assertEqual('conflicting', result['status'])
                self.assertTrue(all(issue['source'] == {'atom_id': 'C'} for issue in result['issues']))

    def test_projection_type_must_be_exact(self):
        for typ in ('T_Content', 'Subtype (fun _ : T_Header => False)'):
            with self.subTest(typ=typ):
                changed = self.program.replace('f_header : T_Header', f'f_header : {typ}', 1)
                result = validate_translation(self.source, changed, lean=self.lean)
                self.assertEqual('conflicting', result['status'])
                self.assertIn({'source': {'atom_id': 'C'}, 'field': 'contract.fields.header',
                               'message': 'Lean shape differs from the normalized source'}, result['issues'])

    def test_parameter_sorts_and_binder_modes_must_match(self):
        variants = [TARGET.replace(': Type)', f': {sort})') for sort in ('Prop', 'Type 1')]
        variants.append(TARGET.replace('T_Content T_Header : Type', 'T_Header T_Content : Type'))
        variants.append(TARGET.replace('(T_Content T_Header : Type)', '{T_Content T_Header : Type}')
                        .replace('extends R_Atom T_Content T_Header', 'extends @R_Atom T_Content T_Header'))
        variants.append(TARGET.replace('structure S_Plan (T_Content T_Header : Type)',
                                       'structure S_Plan {T_Content T_Header : Type}'))
        for variant in variants:
            with self.subTest(variant=variant):
                result = validate_translation(self.source, self.program.replace(TARGET, variant, 1), lean=self.lean)
                self.assertEqual('conflicting', result['status'])
                self.assertTrue(any(issue['field'].startswith('contract.') and issue['source'] == {'atom_id': 'C'}
                                    for issue in result['issues']))

    def test_result_universe_and_field_binder_mode_must_match(self):
        variants = [
            TARGET.replace('structure R_Atom (T_Content T_Header : Type) where',
                           'structure R_Atom (T_Content T_Header : Type) : Type 1 where'),
            TARGET.replace('  f_header : T_Header', '  {f_header : T_Header}'),
        ]
        for variant in variants:
            with self.subTest(variant=variant):
                result = validate_translation(self.source, self.program.replace(TARGET, variant, 1), lean=self.lean)
                self.assertEqual('conflicting', result['status'])
                self.assertIn('contract.shape', [issue['field'] for issue in result['issues']])

    def test_ill_typed_program_remains_an_error(self):
        with self.assertRaisesRegex(ValueError, 'Lean comparison failed'):
            validate_translation(self.source, self.program.replace('R_Atom', 'R_Other', 1), lean=self.lean)
        with self.assertRaisesRegex(ValueError, 'Lean comparison failed'):
            validate_translation(self.source, self.program, lean='/nonexistent/lean')

    def test_no_base(self):
        self.source['solution']['claims'] = [('python shape', SOLUTION.replace('Plan(Atom)', 'Plan'))]
        program = compile_lean(self.source)['lean']
        result = validate_translation(self.source, program, lean=self.lean)
        self.assertEqual('matched', result['status'])
        altered = program.replace(
            'structure «S_Plan» where',
            'structure «S_Plan» («T_Content» «T_Header» : Type) extends «R_Atom» «T_Content» «T_Header» where')
        result = validate_translation(self.source, altered, lean=self.lean)
        self.assertEqual('conflicting', result['status'])
        self.assertTrue(any(item['field'] == 'solution.shape' for item in result['issues']))
