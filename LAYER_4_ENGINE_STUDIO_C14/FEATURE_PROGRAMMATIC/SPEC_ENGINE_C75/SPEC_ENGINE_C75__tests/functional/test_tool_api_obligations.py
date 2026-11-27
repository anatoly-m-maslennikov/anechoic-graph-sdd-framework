import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75._package__shared import verify_formal_chain
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_4_SPEC_COMPARISON_C88._package__shared import (
    _tool_solution,
    check_tool_api_spec,
    solution_tool_api,
)

from .test_cli_spec import _carrier
from .test_manifest_child_delegation import _manifest


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
        module = 'FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_4_SPEC_COMPARISON_C88.tool_api_spec__pub.'
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

    def test_partial_outcomes_keep_conflicts_and_incomplete_evidence(self):
        def output(detail):
            return {'target': 'done', 'expect': {'kind': 'output', 'outcome': 'succeeded',
                                                'detail': {'http_outcome': 'success', **detail}}}
        full = {'status_code': 200, 'envelope': 'result'}
        claim = {'initial': 'start', 'states': [
            {'name': 'start', 'final': False, 'transitions': [output(full)]},
            {'name': 'done', 'final': True, 'transitions': []},
            {'name': 'unreachable', 'final': False, 'transitions': [output({'status_code': 503})]}]}
        transitions = claim['states'][0]['transitions']
        self.assertEqual([200, 'result'], solution_tool_api(claim)['outcomes.success'])
        for partial in ({'status_code': 503}, {'envelope': 'error'}):
            transitions.append(output(partial))
            self.assertIn('conflicting_values', solution_tool_api(claim)['outcomes.success'])
            transitions.pop()
        transitions.append(output({'status_code': 200}))
        self.assertNotIn('outcomes.success', solution_tool_api(claim))
        transitions.pop()
        transitions.append(output(full))
        self.assertEqual(
            [200, "result"], solution_tool_api(claim)["outcomes.success"]
        )
        for name in ("invalid_input", "internal_error"):
            for transition in transitions:
                transition['expect']['outcome'] = 'failed'
                transition['expect']['detail']['http_outcome'] = name
            transitions.append(copy.deepcopy(transitions[0]))
            del transitions[-1]['expect']['detail']['envelope']
            transitions[-1]['expect']['detail']['status_code'] = 503
            self.assertIn('conflicting_values', solution_tool_api(claim)[f'outcomes.{name}'])
            transitions.pop()

    def test_partial_outcome_compares_known_fields_against_contract(self):
        sources = {role: {'source': {'atom_id': role}} for role in ('manifest', 'contract', 'solution')}
        output = {'kind': 'output', 'outcome': 'succeeded', 'detail': {'http_outcome': 'success'}}
        workflow = {'initial': 'start', 'states': [
            {'name': 'start', 'final': False, 'transitions': [{'target': 'done', 'expect': output}]},
            {'name': 'done', 'final': True, 'transitions': []}]}
        contract = {'profile': 'tool_api', 'operation': 'POST /tools', 'facts': [],
                    'outcomes': [('success', 200, 'result')]}
        compiled = {'claims': {'contract': contract, 'solution': workflow}, 'issues': [], 'unresolved': []}
        module = 'FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_4_SPEC_COMPARISON_C88.tool_api_spec__pub.'
        with patch(module + 'load_boundary_model', return_value=sources), \
             patch(module + 'compile_lean', return_value=compiled), \
             patch(module + 'render_solution'):
            for detail, status in (({'status_code': 503}, 'conflicting'),
                                   ({'status_code': 200}, 'unresolved'),
                                   ({'envelope': 'other'}, 'conflicting'),
                                   ({'status_code': 200, 'envelope': 'result'}, 'matched')):
                output['detail'] = {'http_outcome': 'success', **detail}
                report = check_tool_api_spec(None, 'C45', None, None, None)
                facts = report['directions']['contract_solution']['facts']
                outcome = next(fact for fact in facts if fact['key'] == 'outcomes.success')
                self.assertEqual(status, outcome['status'])

    def test_public_comparison_covers_each_terminal_branch(self):
        sources = {role: {'source': {'atom_id': role}} for role in ('manifest', 'contract', 'solution')}
        full = {'http_outcome': 'success', 'status_code': 200, 'envelope': 'result',
                'response_format': 'json', 'response_fields': ['value']}
        outputs = [{'kind': 'output', 'outcome': 'succeeded', 'detail': copy.deepcopy(full)} for _ in range(2)]
        workflow = {'initial': 'start', 'states': [
            {'name': 'start', 'final': False, 'transitions': [
                {'target': 'done', 'expect': output} for output in outputs]},
            {'name': 'done', 'final': True, 'transitions': []}]}
        contract = {'operation': 'POST /tools', 'facts': [
            ('interface.response_format', ['json']), ('output_format.result_fields', ['value'])],
            'outcomes': [('success', 200, 'result')]}
        compiled = {'claims': {'contract': contract, 'solution': workflow}, 'issues': [], 'unresolved': []}
        module = 'FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_4_SPEC_COMPARISON_C88.tool_api_spec__pub.'
        with patch(module + 'load_boundary_model', return_value=sources), \
             patch(module + 'compile_lean', return_value=compiled), patch(module + 'render_solution'):
            cases = [({'status_code': 503}, 'outcomes.success', 'conflicting'),
                     ({'status_code': 200, 'envelope': 'result'}, 'outcomes.success', 'unresolved'),
                     ({'http_outcome': 'success', 'status_code': 200, 'envelope': 'result'},
                      'interface.response_format', 'unresolved'),
                     ({'http_outcome': 'success', 'status_code': 200, 'envelope': 'result'},
                      'output_format.result_fields', 'unresolved'),
                     ({**full, 'response_format': 'text'}, 'interface.response_format', 'conflicting'),
                     (full, 'output_format.result_fields', 'matched')]
            for detail, key, status in cases:
                outputs[1]['detail'] = detail
                report = check_tool_api_spec(None, 'C45', None, None, None)
                facts = report['directions']['contract_solution']['facts']
                self.assertEqual(status, next(fact['status'] for fact in facts if fact['key'] == key))

    def test_unclassified_failure_keeps_format_disagreement(self):
        claim = {'initial': 'start', 'states': [
            {'name': 'start', 'final': False, 'transitions': [
                {'target': 'done', 'expect': {'kind': 'output', 'outcome': 'failed', 'detail': detail}}
                for detail in ({'http_outcome': 'invalid_input', 'response_format': 'json'},
                               {'response_format': 'text'})]},
            {'name': 'done', 'final': True, 'transitions': []}]}
        self.assertEqual({'conflicting_values': [['json'], ['text']]},
                         solution_tool_api(claim)['interface.response_format'])

    def test_public_delivery_and_internal_message_require_each_branch(self):
        sources = {role: {'source': {'atom_id': role}} for role in ('manifest', 'contract', 'solution')}
        success = {'http_outcome': 'success', 'status_code': 200, 'envelope': 'result',
                   'result_types': {'text': 'string_or_null', 'value': 'object'},
                   'delivery_mode': 'requested', 'include_submitted_sql': False,
                   'retain_result_by': 'query_id', 'bookmark_requires_save': True}
        failure = {'http_outcome': 'internal_error', 'status_code': 500,
                   'envelope': 'error', 'message': 'internal error'}
        outputs = [{'kind': 'output', 'outcome': outcome, 'detail': copy.deepcopy(detail)}
                   for outcome, detail in [('succeeded', success), ('succeeded', success),
                                           ('failed', failure), ('failed', failure)]]
        workflow = {'initial': 'start', 'states': [
            {'name': 'start', 'final': False, 'transitions': [
                {'target': 'done', 'expect': output} for output in outputs]},
            {'name': 'done', 'final': True, 'transitions': []}]}
        expected = {'output_format.text': ['string_or_null'], 'output_format.value': ['object'],
                    'guarantees.query_output': ['requested_delivery_without_submitted_sql'],
                    'effects.query_result': ['retained'], 'effects.bookmark': ['explicit_save_only'],
                    'error_handling.internal_message': ['internal error']}
        contract = {'operation': 'POST /tools', 'facts': list(expected.items()),
                    'outcomes': [('success', 200, 'result'), ('internal_error', 500, 'error')]}
        compiled = {'claims': {'contract': contract, 'solution': workflow}, 'issues': [], 'unresolved': []}
        module = 'FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_4_SPEC_COMPARISON_C88.tool_api_spec__pub.'
        with patch(module + 'load_boundary_model', return_value=sources), \
             patch(module + 'compile_lean', return_value=compiled), patch(module + 'render_solution'):
            def statuses():
                report = check_tool_api_spec(None, 'C45', None, None, None)
                return {fact['key']: fact['status'] for fact in report['directions']['contract_solution']['facts']}
            actual = statuses()
            self.assertTrue(all(actual[key] == 'matched' for key in expected))
            outputs[1]['detail'] = {'http_outcome': 'success', 'status_code': 200, 'envelope': 'result'}
            outputs[3]['detail'] = {'http_outcome': 'internal_error', 'status_code': 500, 'envelope': 'error'}
            actual = statuses()
            self.assertTrue(all(actual[key] == 'unresolved' for key in expected))
            outputs[0]['detail']['delivery_mode'] = 'wrong'
            del outputs[0]['detail']['include_submitted_sql']
            outputs[2]['detail']['message'] = 'wrong'
            actual = statuses()
            self.assertEqual('conflicting', actual['guarantees.query_output'])
            self.assertEqual('conflicting', actual['error_handling.internal_message'])

    def test_unclassified_terminal_in_public_formal_chain(self):
        def body(language, source):
            return f'## Claim\n\n### Formal Claim\n\n```{language}\n{source}\n```\n'
        contract = ("declare_tool_api_contract(operation='POST /tools', "
                    "outcomes={'success': (200, 'result'), 'invalid_input': (400, 'typed_error'), "
                    "'internal_error': (500, 'typed_error')}, "
                    "checks={'interface': {'response_format': 'json'}})")
        def edge(outcome, name, status, envelope):
            return {'to': 'done', 'expect': {'kind': 'output', 'outcome': outcome, 'detail': {
                'http_outcome': name, 'status_code': status, 'envelope': envelope, 'response_format': 'json'}}}
        transitions = {'good': edge('succeeded', 'success', 200, 'result'),
                       'invalid': edge('failed', 'invalid_input', 400, 'typed_error'),
                       'failure': edge('failed', 'internal_error', 500, 'typed_error')}
        machine = {'id': 'g', 'initial': 'start', 'states': {
            'start': {'on': {'request': {'to': 'serve', 'expect': {
                'kind': 'trigger', 'detail': {'operation': 'POST /tools'}}}}},
            'serve': {'on': transitions}, 'done': {'type': 'final'}}}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = _manifest(root, 'AN-S-1', 'C1', 'C2', body('python contract', contract),
                                 {'state': {'reads': [], 'writes': []}})
            for terminal in (None, {'kind': 'output', 'outcome': 'partial',
                                    'detail': {'status_code': 503, 'response_format': 'json'}},
                             {'kind': 'effect', 'target': 'query', 'outcome': 'skipped'}):
                if terminal is not None:
                    transitions['incomplete'] = {'to': 'done', 'expect': terminal}
                source = f"component_workflow(component='C2', action='invoke', machine={machine!r})"
                solution = _carrier(root, 'AN-S-2', 'solution', 'C2', '{ANSWERS: [AN-S-1@1]}',
                                    body('python', source))
                report = verify_formal_chain(root, 'C2', manifest, solution)
                self.assertEqual('matched' if terminal is None else 'unresolved', report['status'])
                if terminal is not None:
                    self.assertTrue(any(row['field'] == 'http_outcome' for row in report['unresolved']))

    def test_selects_profile_with_inconsistent_operation(self):
        workflow = {'initial': 'start', 'states': [
            {'name': 'start', 'final': False, 'transitions': [
                {'target': 'done', 'expect': {'kind': 'trigger', 'detail': {'operation': operation}}}
                for operation in ('POST /tools', 'POST /other')]},
            {'name': 'done', 'final': True, 'transitions': []}]}
        facts = _tool_solution({'operations': {'invoke': workflow}}, 'POST /tools', None)
        self.assertEqual({'conflicting_values': [['POST /tools'], ['POST /other']]}, facts['operation'])

    def test_query_evidence_covers_each_reachable_success_path(self):
        sql = {'statement_count': 1, 'read_only': True, 'cursor_metadata_only': True,
               'uses_full_submitted_sql': True, 'uses_selected_project': True}
        effect = {'kind': 'effect', 'target': 'C59', 'outcome': 'succeeded',
                  'detail': {'operation': 'run', 'sql': sql}}
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
            'operation': 'run',
            'input_types': {'name': 'string', 'arguments': 'object', 'nullable_strings': ['session_id']},
            'matches_admitted_instance': True, 'tool_enabled': True, 'tool_in_registry': True,
            'sql': {'statement_count': 1, 'read_only': True, 'cursor_metadata_only': True,
                    'uses_full_submitted_sql': True, 'uses_selected_project': True}}}
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
