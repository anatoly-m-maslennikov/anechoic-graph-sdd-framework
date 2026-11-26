import copy
import unittest
from unittest.mock import patch

from SPEC_ENGINE_C75.LAYER_4_SPEC_COMPARISON_C88.tool_api_obligations__pub import solution_tool_api
from SPEC_ENGINE_C75.LAYER_4_SPEC_COMPARISON_C88.tool_api_spec__pub import check_tool_api_spec, _tool_solution


class ToolApiObligationTests(unittest.TestCase):
    def test_inconsistent_branches_return_source_linked_report(self):
        outputs = [
            {'kind': 'output', 'outcome': 'succeeded', 'detail': {
                'http_outcome': 'success', 'response_format': 'json'}},
            {'kind': 'output', 'outcome': 'failed', 'detail': {
                'http_outcome': 'invalid_input', 'response_format': 'text'}},
            {'kind': 'output', 'outcome': 'failed', 'detail': {
                'http_outcome': 'internal_error', 'response_format': 'json'}},
        ]
        claim = {'initial': 'start', 'states': [
            {'name': 'start', 'final': False, 'transitions': [
                {'target': 'done', 'expect': output} for output in outputs]},
            {'name': 'done', 'final': True, 'transitions': []}]}
        facts = solution_tool_api(claim)
        self.assertEqual({'conflicting_values': [['json'], ['text']]},
                         facts['interface.response_format'])
        sources = {role: {'atom_id': role} for role in ('manifest', 'contract', 'solution')}
        model = {role: {'source': source} for role, source in sources.items()}
        compiled = {'claims': {'solution': claim}, 'issues': [], 'unresolved': []}
        directions = {name: {'status': 'matched', 'facts': []} for name in (
            'manifest_contract', 'manifest_solution', 'contract_solution')}
        module = 'SPEC_ENGINE_C75.LAYER_4_SPEC_COMPARISON_C88.tool_api_spec__pub.'
        with patch(module + 'load_boundary_model', return_value=model), \
             patch(module + 'compile_lean', return_value=compiled), \
             patch(module + 'compare_obligations', return_value={
                 'status': 'matched', 'sources': sources, 'directions': directions}), \
             patch(module + 'render_solution'):
            report = check_tool_api_spec(None, 'C45', None, None, None)
        self.assertEqual('conflicting', report['status'])
        self.assertEqual(directions, report['directions'])
        self.assertEqual(sources['solution'], report['issues'][0]['source'])
        self.assertEqual('interface.response_format', report['issues'][0]['field'])

    def test_inconsistent_error_fields_remain_visible_without_other_outcome(self):
        claim = {'initial': 'start', 'states': [
            {'name': 'start', 'final': False, 'transitions': [
                {'target': 'done', 'expect': {'kind': 'output', 'outcome': 'failed', 'detail': {
                    'http_outcome': 'invalid_input', 'response_fields': fields}}}
                for fields in (['code'], ['message'], ['code'])]},
            {'name': 'done', 'final': True, 'transitions': []}]}
        self.assertEqual({'conflicting_values': [['code'], ['message']]},
                         solution_tool_api(claim)['error_handling.error_fields'])

    def test_selects_profile_with_inconsistent_operation(self):
        workflow = {'initial': 'start', 'states': [
            {'name': 'start', 'final': False, 'transitions': [
                {'target': 'done', 'expect': {'kind': 'trigger', 'detail': {'operation': operation}}}
                for operation in ('POST /tools', 'POST /other')]},
            {'name': 'done', 'final': True, 'transitions': []}]}
        facts = _tool_solution({'operations': {'invoke': workflow}}, 'POST /tools', None)
        self.assertEqual({'conflicting_values': [['POST /tools'], ['POST /other']]}, facts['operation'])

    def test_query_evidence_covers_each_reachable_success_path(self):
        sql = {'statement_count': 1, 'read_only': True, 'cursor_metadata_only': True}
        effect = {'kind': 'effect', 'target': 'C59', 'outcome': 'succeeded', 'detail': {'sql': sql}}
        success = {'kind': 'output', 'outcome': 'succeeded', 'detail': {'http_outcome': 'success'}}
        claim = {'initial': 'start', 'states': [
            {'name': 'start', 'final': False, 'transitions': [
                {'target': 'report', 'expect': effect},
                {'target': 'report', 'expect': copy.deepcopy(effect)}]},
            {'name': 'report', 'final': False, 'transitions': [
                {'target': 'report', 'expect': {'kind': 'trigger'}},
                {'target': 'done', 'expect': success}]},
            {'name': 'done', 'final': True, 'transitions': []}]}
        self.assertEqual(['one_complete_read_only_statement'], solution_tool_api(claim)['guarantees.query'])
        claim['states'][0]['transitions'].append({'target': 'report', 'expect': {'kind': 'trigger'}})
        self.assertNotIn('guarantees.query', solution_tool_api(claim))
        claim['states'][0]['transitions'].pop()
        other = claim['states'][0]['transitions'][1]['expect']
        other['detail']['sql'] = {}
        self.assertNotIn('guarantees.query', solution_tool_api(claim))
        other['detail']['sql'] = {'statement_count': 1, 'read_only': False}
        self.assertEqual([{'statement_count': 1, 'read_only': False}],
                         solution_tool_api(claim)['guarantees.query'])
        other['detail']['sql'] = {'read_only': 0}
        self.assertNotIn('guarantees.query', solution_tool_api(claim))
        other['detail']['sql'] = {'read_only': False}
        claim['states'][0]['transitions'][1]['target'] = 'dead'
        claim['states'].append({'name': 'dead', 'final': True, 'transitions': []})
        self.assertEqual(['one_complete_read_only_statement'], solution_tool_api(claim)['guarantees.query'])
        other['detail']['sql'] = {'read_only': 0}
        claim['states'][1]['transitions'] = [{'target': 'later', 'expect': other}]
        claim['states'].append({'name': 'later', 'final': False, 'transitions': [
            {'target': 'done', 'expect': success}]})
        self.assertNotIn('guarantees.query', solution_tool_api(claim))

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
