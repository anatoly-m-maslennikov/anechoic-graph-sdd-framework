import unittest

from FEATURE_AGENTIC.FEATURE_PROMPTS.ACTION_PROMPTS.RMED_ATOM_REVIEW.RMED_ATOM_REVIEW__shared import ReviewContext, validate_part
from FEATURE_AGENTIC.FEATURE_PROMPTS.ACTION_PROMPTS.RMED_ATOM_REVIEW.RMED_ATOM_REVIEW__tests.test_local_review import (
    part6, prechecked_packet,
)

SUMMARY = '# Summary\nRecord Projection dependency provenance only when required'
SOURCE = f'''---
version: 1
---
{SUMMARY}
## Scope
provenance.
## Claim
the Atom **must not** lose provenance **when** required.
## Details
'''


def review_case(candidate, observations=()):
    packet = prechecked_packet(candidate_text=candidate)
    context = ReviewContext(packet)
    report = part6('cce')
    report.update(source=packet['candidate_bindings'][0], context_sha256=context.sha256)
    check = report['checks'][0]
    check['positive_observations'][0]['excerpt'] = 'lose provenance'
    check['operator_observations'] = [
        {'location': location, 'offset': offset, 'excerpt': excerpt,
         'disposition': 'literal_example', 'reason': 'Mock illustration'}
        for location, offset, excerpt in observations
    ]
    return context, report


SUMMARY_OPERATORS = tuple(('body:1:# Summary', SUMMARY.index(word), word) for word in ('only', 'when'))


class OperatorPrecheckTests(unittest.TestCase):
    def test_registry_requires_all_categories(self):
        packet = prechecked_packet(registry_text='1. modality: **must**')
        with self.assertRaisesRegex(ValueError, 'complete'):
            ReviewContext(packet)

    def test_indented_literals_and_list_continuations_need_classification(self):
        base = SOURCE.replace('only when', '**only** **when**')
        details = '## Details\n\n    must stay literal\n\n- prose\n    and a continuation\n'
        raw = base.removesuffix('## Details\n') + details
        observations = [('body:7:## Details', details.index(word), word) for word in ('must', 'and')]
        context, report = review_case(raw, observations)
        validate_part(report, context=context)
        report['checks'][0]['operator_observations'] = []
        with self.assertRaisesRegex(ValueError, 'coverage'):
            validate_part(report, context=context)

    def test_summary_is_included_and_intact_multiword_bold_is_excluded(self):
        context, report = review_case(SOURCE, SUMMARY_OPERATORS)
        validate_part(report, context=context)

    def test_code_headings_and_word_fragments_are_excluded(self):
        raw = SOURCE.replace('only when', '**only** **when**') + '''
### only when
`only when` remains literal.
```text
only when
```
inside ordinary rendering.
read-only and-code append-only facts.
'''
        context, report = review_case(raw)
        validate_part(report, context=context)

    def test_unquoted_prose_examples_need_review_not_automatic_failure(self):
        example = 'only in illustrative prose.'
        details = '## Details\n' + example
        observations = [*SUMMARY_OPERATORS]
        observations.extend(('body:7:## Details', details.index(word), word) for word in ('only', 'in'))
        context, report = review_case(SOURCE + example, observations)
        validate_part(report, context=context)

    def test_old_generic_pass_cannot_skip_summary_candidates(self):
        context, report = review_case(SOURCE)
        del report['checks'][0]['operator_observations']
        with self.assertRaisesRegex(ValueError, 'coverage'):
            validate_part(report, context=context)

    def test_repeated_occurrences_need_separate_dispositions(self):
        raw = SOURCE + '\nonly again.\n'
        context, report = review_case(raw, (*SUMMARY_OPERATORS, ('body:7:## Details', 12, 'only')))
        validate_part(report, context=context)
        report['checks'][0]['operator_observations'].pop()
        with self.assertRaisesRegex(ValueError, 'coverage'):
            validate_part(report, context=context)

    def test_incomplete_review_is_allowed_to_report_blocked(self):
        context, report = review_case(SOURCE)
        report['checks'][0]['status'] = report['result'] = 'blocked'
        report['coverage_gaps'] = [{'check_id': 'cce', 'kind': 'reviewer_incomplete',
                                    'reason': 'Operator classification incomplete.'}]
        validate_part(report, context=context)

    def test_empty_reason_or_shifted_offsets_do_not_establish_pass(self):
        for change in ({'reason': ''}, {'offset': 0}):
            context, report = review_case(SOURCE, SUMMARY_OPERATORS)
            observation = report['checks'][0]['operator_observations'][0]
            observation.update(disposition='non_operator_usage', **change)
            with self.subTest(change=change), self.assertRaisesRegex(ValueError, 'justified operator dispositions'):
                validate_part(report, context=context)
