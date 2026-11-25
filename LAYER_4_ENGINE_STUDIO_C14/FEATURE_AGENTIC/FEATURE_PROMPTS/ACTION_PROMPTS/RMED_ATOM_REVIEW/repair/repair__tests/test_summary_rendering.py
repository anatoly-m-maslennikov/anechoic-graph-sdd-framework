"""Lossless Summary rendering does not replace its identity-bearing value."""
import unittest

from FEATURE_AGENTIC.FEATURE_PROMPTS.ACTION_PROMPTS.RMED_ATOM_REVIEW.repair.repair__tests.test_repair_gate import SOURCE_TEXT, caller_preflight
from FEATURE_AGENTIC.FEATURE_PROMPTS.ACTION_PROMPTS.RMED_ATOM_REVIEW.repair.repair__tests.test_local_repair import local_inputs
from FEATURE_AGENTIC.FEATURE_PROMPTS.ACTION_PROMPTS.RMED_ATOM_REVIEW.repair.repair_gate__shared import admit_proposal


def admit_summary_change(before, after):
    context, evaluation, proposal, permission = local_inputs(
        original=SOURCE_TEXT.replace('Atom rule', before))
    proposal.update(before_summary=before, after_summary=after)
    output = proposal['outputs'][0]
    output['text'] = output['text'].replace('Atom rule', after)
    return admit_proposal(evaluation, proposal, context=context,
                          permission=permission, preflight=caller_preflight(proposal))


class SummaryRendering(unittest.TestCase):
    def test_plain_and_strong_text_keep_the_exact_same_value(self):
        for before, after in (
            ('Record provenance only when required', 'Record provenance **only** **when** required'),
            ('Terms in CORE_META_MODEL', 'Terms **in** CORE_META_MODEL'),
            ('Keep A', 'Keep **A**'),
            ('Keep **A**', 'Keep A'),
        ):
            with self.subTest(before=before, after=after):
                self.assertEqual(admit_summary_change(before, after)['result'], 'candidate')

    def test_actual_word_case_punctuation_and_space_changes_still_fail(self):
        for after in ('Other rule', '**atom** rule', 'Atom rule.', 'Atom  rule',
                      'Atom **new** rule', 'Atom **rule**\nextra'):
            with self.subTest(after=after), self.assertRaisesRegex(ValueError, 'Summary change requires replacement'):
                admit_summary_change('Atom rule', after)

    def test_unsupported_markup_is_not_losslessly_inferred(self):
        for after in ('Atom *rule*', 'Atom ***rule***', 'Atom ** rule **',
                      'Atom `rule`', 'Atom [rule](target)', 'Atom <b>rule</b>',
                      r'Atom \**rule**', 'Atom **rule', 'Atom rule**'):
            with self.subTest(after=after), self.assertRaisesRegex(ValueError, 'Summary change requires replacement'):
                admit_summary_change('Atom rule', after)

    def test_local_formatting_admission_preserves_identity_and_no_write_permission(self):
        result = admit_summary_change('Atom rule', 'Atom **rule**')
        self.assertEqual(result['result'], 'candidate')
        self.assertFalse(result['source_mutation_permitted'])

    def test_actual_summary_change_is_still_replacement_only(self):
        with self.assertRaisesRegex(ValueError, 'Summary change requires replacement'):
            admit_summary_change('Atom rule', 'Atom **new** rule')


if __name__ == '__main__':
    unittest.main()
