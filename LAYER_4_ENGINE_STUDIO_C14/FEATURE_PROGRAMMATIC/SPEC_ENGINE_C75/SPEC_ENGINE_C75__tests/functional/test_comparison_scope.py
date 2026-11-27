import os
import shutil
import tempfile
import unittest
from pathlib import Path

from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75._package__shared import verify_formal_chain

from .test_cli_spec import _carrier
from .test_manifest_child_delegation import _manifest
from .test_shape_spec import CONTRACT, SOLUTION

_SHAPES = {'Atom': {'fields': {'header': 'Header', 'content': 'Content'}},
           'Plan': {'base': 'Atom'}}
_TRACE = ("declare_trace_contract(action='compile', output='done', "
          "must_effect=(('parser', 'called'),))")
_TOOL = ("declare_tool_api_contract(operation='POST /tools', "
         "outcomes={'success': (200, 'result'), 'invalid_input': (400, 'typed_error'), "
         "'internal_error': (500, 'typed_error')})")


def _fence(language, claim):
    return f'```{language}\n{claim}\n```\n'


def _workflow(action, states):
    machine = {'id': action, 'initial': 'start',
               'states': {**states, 'done': {'type': 'final'}}}
    return _fence('python', f"component_workflow(component='C2', action={action!r}, machine={machine!r})")


def _compile():
    return _workflow('compile', {
        'start': {'on': {'parsed': {'to': 'parsed', 'expect': {
            'kind': 'effect', 'target': 'parser', 'outcome': 'called'}}}},
        'parsed': {'on': {'done': {'to': 'done', 'expect': {'kind': 'output', 'outcome': 'done'}}}},
    })


def _response(name, status, envelope, **detail):
    return {'to': 'done', 'expect': {
        'kind': 'output', 'outcome': 'succeeded' if name == 'success' else 'failed',
        'detail': {'http_outcome': name, 'status_code': status, 'envelope': envelope, **detail}}}


def _invoke(*requests):
    requests = requests or ({'operation': 'POST /tools'},)
    states = {'start': {'on': {
        f'request_{index}': {'to': 'serving', 'expect': {
            'kind': 'trigger', 'detail': request}}
        for index, request in enumerate(requests)
    }}}
    states['serving'] = {'on': {
        name: _response(name, status, envelope)
        for name, status, envelope in (('success', 200, 'result'), ('invalid_input', 400, 'typed_error'),
                                        ('internal_error', 500, 'typed_error'))
    }}
    return _workflow('invoke', states)


class ComparisonScopeTests(unittest.TestCase):
    def setUp(self):
        self.lean = os.environ.get('ANECHOIC_TEST_LEAN') or shutil.which('lean')
        if self.lean is None:
            self.skipTest('Lean executable unavailable')
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)

    def check(self, contract, solution, boundaries, action=None):
        manifest = _manifest(self.root, 'AN-S-1', 'C1', 'C2', contract, boundaries)
        candidate = _carrier(self.root, 'AN-S-2', 'solution', 'C2', '{ANSWERS: [AN-S-1@1]}',
                             f'## Claim\n\n### Formal Claim\n\n{solution}')
        return verify_formal_chain(self.root, 'C2', manifest, candidate, action=action, lean=self.lean)

    def test_shape_comparison_reports_unchecked_logical_outcome(self):
        for kind, values in (('must_effect', [('parser', 'called')]), ('forbid_effect', ['parser'])):
            with self.subTest(kind=kind):
                io = {'class_shapes': _SHAPES,
                      'server': {'compile': {'outcomes': {'done': {kind: values}}}}}
                report = self.check(_fence('python shape', CONTRACT), _fence('python shape', SOLUTION), {'io': io})
                self.assertEqual('matched', report['translation']['status'], report)
                self.assertEqual('unresolved', report['status'], report)
                self.assertEqual('unresolved', report['directions']['manifest_solution']['status'])
                self.assertIn('boundaries.io.server.compile.outcomes.done',
                              {gap['field'] for gap in report['unresolved']})

    def test_trace_comparison_reports_unchecked_shape_only_for_whole_chain(self):
        io = {'class_shapes': _SHAPES,
              'server': {'compile': {'outcomes': {'done': {'must_effect': [('parser', 'called')]}}}}}
        contract = _fence('python trace', _TRACE)
        report = self.check(contract, _compile(), {'io': io})
        self.assertEqual('unresolved', report['status'], report)
        self.assertIn('boundaries.io.class_shapes', {gap['field'] for gap in report['unresolved']})
        selected = self.check(contract, _compile(), {'io': io}, action='compile')
        self.assertEqual('matched', selected['status'], selected)
        self.assertEqual('compile', selected['evidence']['action'])

    def test_selects_tool_and_trace_actions_in_the_same_chain(self):
        contract = _fence('python contract', _TOOL) + '\n' + _fence('python trace', _TRACE)
        solution = _invoke() + '\n' + _compile()
        for action, required in (('invoke', 'outcomes.success'), ('compile', 'must_effect')):
            with self.subTest(action=action):
                report = self.check(contract, solution, {'state': {'reads': [], 'writes': []}}, action=action)
                self.assertEqual('matched', report.get('status'), report)
                self.assertEqual(action, report['evidence']['action'])
                facts = report['directions']['manifest_solution']['facts']
                self.assertTrue(any(fact['key'] == required and fact['status'] == 'matched' for fact in facts))

    def test_reports_unchecked_obligations_alongside_a_tool_conflict(self):
        io = {'class_shapes': _SHAPES,
              'server': {'invoke': {'outcomes': {'succeeded': {'must_effect': [('parser', 'called')]}}}}}
        solution = _invoke({'operation': 'POST /tools'}, {'operation': 'POST /other'})
        report = self.check(_fence('python contract', _TOOL), solution, {'io': io})
        self.assertEqual('conflicting', report['status'], report)
        required = {'boundaries.io.class_shapes', 'boundaries.io.server.invoke.outcomes.succeeded'}
        self.assertEqual(required, {gap['field'] for gap in report['unresolved']})
        facts = report['evidence']['coverage']
        self.assertTrue(required <= {fact['key'] for fact in facts if fact['status'] == 'unresolved'})

    def test_every_request_branch_must_support_the_declared_format(self):
        contract = _fence('python contract', _TOOL[:-1]
                          + ", checks={'interface': {'request_format': 'json'}})")
        request = {'operation': 'POST /tools'}
        json_request = {**request, 'request_format': 'json'}
        text_request = {**request, 'request_format': 'text'}
        for primary, alternate, status in (
                (json_request, json_request, 'matched'),
                (json_request, request, 'unresolved'),
                (json_request, text_request, 'conflicting'),
                (request, text_request, 'conflicting')):
            with self.subTest(primary=primary, alternate=alternate, status=status):
                report = self.check(contract, _invoke(primary, alternate),
                                    {'state': {'reads': [], 'writes': []}}, action='invoke')
                self.assertEqual('compared', report['outcome'], report.get('diagnostics'))
                facts = report['directions']['manifest_solution']['facts']
                fact = next(row for row in facts if row['key'] == 'interface.request_format')
                self.assertEqual(status, fact['status'])
                self.assertEqual(status, report['status'])

    def test_invalid_input_dispatch_is_checked_on_each_reachable_path(self):
        tool = _TOOL[:-1] + ", checks={'effects': {'invalid_input_dispatch': 'none'}})"
        contract = _fence('python contract', tool) + '\n' + _fence('python trace', _TRACE)
        responses = {
            'success': _response('success', 200, 'result'),
            'internal_error': _response('internal_error', 500, 'typed_error'),
        }
        for provider, late, expected in (
            ('C59', None, 'matched'),
            ('C59', {}, 'conflicting'),
            ('C59', {'provider_dispatched': True}, 'conflicting'),
            ('C8', {}, 'unresolved'),
        ):
            with self.subTest(provider=provider, late=late):
                after = dict(responses)
                if late is not None:
                    after['late_reject'] = _response('invalid_input', 400, 'typed_error', **late)
                states = {
                    'start': {'on': {'request': {'to': 'routing', 'expect': {
                        'kind': 'trigger', 'detail': {'operation': 'POST /tools'}}}}},
                    'routing': {'on': {
                        'reject': _response('invalid_input', 400, 'typed_error', provider_dispatched=False),
                        'dispatch': {'to': 'called', 'expect': {'kind': 'effect', 'target': provider,
                                                               'outcome': 'succeeded'}},
                    }},
                    'called': {'on': after},
                }
                solution = _workflow('invoke', states) + '\n' + _compile()
                report = self.check(contract, solution, {'state': {'reads': [], 'writes': []}}, action='invoke')
                self.assertEqual('compared', report['outcome'], report)
                self.assertEqual(expected, report['status'])
                fact = next(row for row in report['evidence']['coverage']
                            if row['key'] == 'effects.invalid_input_dispatch')
                self.assertEqual(expected, fact['status'])

    def test_provider_precondition_requires_evidence_on_each_dispatch_branch(self):
        contract = _fence('python contract', _TOOL[:-1]
                          + ", checks={'preconditions': {'project_binding': 'matching_instance'}})")
        for detail, status in (({'matches_admitted_instance': True}, 'matched'),
                               ({}, 'unresolved'),
                               ({'matches_admitted_instance': False}, 'conflicting')):
            with self.subTest(detail=detail):
                states = {'start': {'on': {'request': {'to': 'routing', 'expect': {
                    'kind': 'trigger', 'detail': {'operation': 'POST /tools'}}}}},
                    'routing': {'on': {'reject': _response('invalid_input', 400, 'typed_error')}},
                    'called': {'on': {'success': _response('success', 200, 'result'),
                                      'error': _response('internal_error', 500, 'typed_error')}}}
                for name, evidence in (('primary', {'matches_admitted_instance': True}), ('alternate', detail)):
                    states['routing']['on'][name] = {'to': 'called', 'expect': {
                        'kind': 'effect', 'target': 'C59', 'outcome': 'succeeded', 'detail': evidence}}
                report = self.check(contract, _workflow('invoke', states),
                                    {'state': {'reads': [], 'writes': []}})
                self.assertEqual('compared', report['outcome'], report)
                fact = next(row for row in report['evidence']['coverage']
                            if row['key'] == 'preconditions.project_binding')
                self.assertEqual(status, fact['status'])
                self.assertEqual(status, report['status'])

    def test_query_guarantee_requires_whole_sql_and_selected_project(self):
        contract = _fence('python contract', _TOOL[:-1]
                          + ", checks={'guarantees': {'query': 'one_complete_read_only_statement'}})")
        sql = {'statement_count': 1, 'read_only': True, 'cursor_metadata_only': True}
        complete = {**sql, 'uses_full_submitted_sql': True, 'uses_selected_project': True}
        for operation, evidence, status in (
                ('run', complete, 'matched'),
                ('run', sql, 'unresolved'),
                ('run', {**sql, 'uses_full_submitted_sql': True}, 'unresolved'),
                ('operation', complete, 'unresolved'),
                ('run', {**complete, 'uses_full_submitted_sql': False}, 'conflicting'),
                ('run', {**complete, 'uses_selected_project': False}, 'conflicting'),
                ('run', {**sql, 'read_only': False}, 'conflicting')):
            with self.subTest(operation=operation, evidence=evidence):
                states = {'start': {'on': {'request': {'to': 'routing', 'expect': {
                    'kind': 'trigger', 'detail': {'operation': 'POST /tools'}}}}},
                    'routing': {'on': {
                        'reject': _response('invalid_input', 400, 'typed_error'),
                        'dispatch': {'to': 'called', 'expect': {
                            'kind': 'effect', 'target': 'C59', 'outcome': 'succeeded', 'detail': {
                                'sql': evidence, 'operation': operation, 'matches_admitted_instance': True}}}}},
                    'called': {'on': {'success': _response('success', 200, 'result'),
                                      'error': _response('internal_error', 500, 'typed_error')}}}
                report = self.check(contract, _workflow('invoke', states),
                                    {'state': {'reads': [], 'writes': []}})
                self.assertEqual('compared', report['outcome'], report)
                fact = next(row for row in report['evidence']['coverage'] if row['key'] == 'guarantees.query')
                self.assertEqual(status, fact['status'])
                self.assertEqual(status, report['status'])
