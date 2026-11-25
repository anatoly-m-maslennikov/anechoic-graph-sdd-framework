"""Bind the caller's Atom-ID presentation policy to review context."""
import unittest

from FEATURE_AGENTIC.FEATURE_PROMPTS.ACTION_PROMPTS.RMED_ATOM_REVIEW.RMED_ATOM_REVIEW__shared import ReviewContext
from FEATURE_AGENTIC.FEATURE_PROMPTS.ACTION_PROMPTS.RMED_ATOM_REVIEW.RMED_ATOM_REVIEW__tests.test_split_evaluation import source, RULE_TEXT


class RelationOrderingTests(unittest.TestCase):
    def policy(self):
        return {'key': 'atom_id', 'direction': 'ascending', 'source': 'operator_input',
                'instruction': 'just atom ID', 'provenance': 'Operator reply, 2026-09-27'}

    def test_missing_policy_is_not_an_implicit_default(self):
        packet = {'confidence_threshold': .99, 'relation_ordering': None,
                  'sources': [source('rule.md', 'MOCK-R-002', RULE_TEXT)]}
        self.assertIsNone(ReviewContext(packet).relation_ordering)
        packet['relation_ordering'] = self.policy()
        self.assertEqual(ReviewContext(packet).relation_ordering, self.policy())

    def test_only_explicit_caller_atom_id_policy(self):
        for delta in [{'key': 'filename'}, {'direction': 'descending'}, {'source': 'reviewer'},
                      {'instruction': ''}, {'provenance': ''}, {'tie_breaker': 'version'}]:
            packet = {'confidence_threshold': .99, 'relation_ordering': self.policy() | delta,
                      'sources': [source('rule.md', 'MOCK-R-002', RULE_TEXT)]}
            with self.subTest(delta=delta), self.assertRaises(ValueError):
                ReviewContext(packet)

    def test_review_context_binds_explicit_policy_in_hash(self):
        packet = {'confidence_threshold': .99,
                  'sources': [source('rule.md', 'MOCK-R-002', RULE_TEXT)]}
        unselected = ReviewContext(packet)
        self.assertIsNone(unselected.relation_ordering)
        packet['relation_ordering'] = self.policy()
        selected = ReviewContext(packet)
        self.assertEqual(selected.relation_ordering, self.policy())
        self.assertNotEqual(selected.sha256, unselected.sha256)
        packet['relation_ordering']['key'] = 'filename'
        self.assertEqual(selected.relation_ordering['key'], 'atom_id')
        with self.assertRaises(ValueError):
            ReviewContext(packet)


if __name__ == '__main__':
    unittest.main()
