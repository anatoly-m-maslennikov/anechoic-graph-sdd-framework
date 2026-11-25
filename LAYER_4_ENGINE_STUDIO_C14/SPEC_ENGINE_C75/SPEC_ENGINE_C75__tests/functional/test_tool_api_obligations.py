import copy
import unittest

from SPEC_ENGINE_C75.tool_api_obligations__pub import solution_tool_api


class ToolApiObligationTests(unittest.TestCase):
    def test_explicit_facts_and_missing_or_contradictory_evidence(self):
        effect = {'kind': 'effect', 'target': 'C59', 'outcome': 'succeeded', 'detail': {
            'input_types': {'name': 'string', 'arguments': 'object', 'nullable_strings': ['session_id']},
            'matches_admitted_instance': True, 'tool_enabled': True, 'tool_in_registry': True,
            'sql': {'statement_count': 1, 'read_only': True, 'cursor_metadata_only': True}}}
        success = {'kind': 'output', 'outcome': 'succeeded', 'detail': {
            'http_outcome': 'success', 'result_types': {'text': 'string_or_null', 'value': 'object'},
            'delivery_mode': 'requested', 'include_submitted_sql': False,
            'retain_result_by': 'query_id', 'bookmark_requires_save': True}}
        invalid = {'kind': 'output', 'outcome': 'failed', 'detail': {
            'http_outcome': 'invalid_input', 'provider_dispatched': False}}
        claim = {'initial': 'validating', 'startup': {'required_arguments': ['--socket']}, 'states': [
            {'name': 'validating', 'final': False, 'transitions': [
                {'target': 'executing', 'expect': effect}, {'target': 'failed', 'expect': invalid}]},
            {'name': 'executing', 'final': False, 'transitions': [{'target': 'done', 'expect': success}]},
            {'name': 'done', 'final': True, 'transitions': []},
            {'name': 'failed', 'final': True, 'transitions': []}]}
        facts = solution_tool_api(claim)
        self.assertEqual(['matching_instance'], facts['preconditions.project_binding'])
        self.assertEqual(['one_complete_read_only_statement'], facts['guarantees.query'])
        self.assertEqual(['none'], facts['effects.invalid_input_dispatch'])
        self.assertEqual(['--socket'], facts['interface.cli_required'])
        self.assertEqual(['explicit_save_only'], facts['effects.bookmark'])
        changed = copy.deepcopy(claim)
        detail = changed['states'][0]['transitions'][0]['expect']['detail']
        detail['sql']['read_only'] = False
        del detail['tool_in_registry']
        changed['states'][1]['transitions'][0]['expect']['detail']['provider_dispatched'] = False
        del changed['states'][0]['transitions'][1]['expect']['detail']['provider_dispatched']
        facts = solution_tool_api(changed)
        self.assertNotEqual(['one_complete_read_only_statement'], facts['guarantees.query'])
        self.assertNotIn('preconditions.tool', facts)
        self.assertNotIn('effects.invalid_input_dispatch', facts)
        changed['states'][1]['transitions'].append({'target': 'failed', 'expect': invalid})
        with self.assertRaisesRegex(ValueError, 'follows provider dispatch'):
            solution_tool_api(changed)
