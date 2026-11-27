import json
import os
from pathlib import Path
import shutil
import subprocess
import unittest

from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_2_SPEC_READING_C83._package__shared import load_formal_claim
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_2_SPEC_READING_C83.SPECIFICATION_MODEL_C85._package__shared import parse_trace_contract
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_4_SPEC_COMPARISON_C88._package__shared import compare_trace_values


RULE = """declare_trace_contract(action='run_view', cases={
    'succeeded': {'same_values': ((('reply', 'query_id'), ('display', 'query_id')),)}
})"""


class TraceValuesTests(unittest.TestCase):
    def test_distinct_values_and_missing_observations(self):
        lean = os.environ.get('ANECHOIC_TEST_LEAN') or shutil.which('lean')
        self.assertTrue(lean, 'Lean executable unavailable')
        case, = parse_trace_contract(RULE)['cases']
        for received, displayed, expected in (
            ({'query_id': 'A'}, {'query_id': 'A'}, 'matched'),
            ({'query_id': 'A'}, {'query_id': 'B'}, 'conflicting'),
            ({'query_id': True}, {'query_id': 1}, 'conflicting'),
            ({'query_id': None}, {'query_id': None}, 'matched'),
            ({'query_id': None}, {}, 'unresolved'),
        ):
            with self.subTest(expected=expected, received=received, displayed=displayed):
                result = compare_trace_values(case, [
                    {'event': 'reply', 'detail': received},
                    {'event': 'display', 'detail': displayed},
                ], lean=lean)
                self.assertEqual(expected, result['status'], result)
                self.assertEqual('succeeded', result['output'])

    def test_equal_blank_ids_and_empty_witnesses_fail_nonempty_checks(self):
        rule = """declare_trace_contract(action='verify', cases={'succeeded': {
            'same_values': ((('read', 'pin'), ('result', 'pin')),),
            'value_types': {('read', 'pin'): 'nonempty_string',
                            ('result', 'witnesses'): 'nonempty_array'},
        }})"""
        case, = parse_trace_contract(rule)['cases']
        for pin, witnesses, expected in (
            (None, [], 'conflicting'),
            ('', [], 'conflicting'),
            ('  ', [1], 'conflicting'),
            ('\u00a0\u2003\u202f', [1], 'conflicting'),
            ('\x0b\x1f', [1], 'conflicting'),
            ('\u00a0snapshot', [1], 'matched'),
            ('\u200b', [1], 'matched'),
            ('snapshot', [], 'conflicting'),
            ('snapshot', [1], 'matched'),
        ):
            with self.subTest(pin=pin, witnesses=witnesses):
                report = compare_trace_values(case, [
                    {'event': 'read', 'detail': {'pin': pin}},
                    {'event': 'result', 'detail': {'pin': pin, 'witnesses': witnesses}},
                ])
                self.assertEqual(expected, report['status'], report)

    def test_rejects_self_comparison(self):
        with self.assertRaisesRegex(ValueError, 'distinct named event fields'):
            parse_trace_contract(RULE.replace("('display', 'query_id')", "('reply', 'query_id')"))

    def test_malformed_event_does_not_complete_an_observation(self):
        case, = parse_trace_contract(RULE)['cases']
        report = compare_trace_values(case, [
            {'event': 'reply', 'detail': {'query_id': 'A'}},
            None,
            {'event': 'display', 'detail': {'query_id': 'A'}},
        ])
        self.assertEqual('unresolved', report['status'], report)

    def test_equal_fields_still_need_the_required_type(self):
        rule = RULE.replace("'succeeded': {", "'succeeded': {'value_types': {('display', 'query_id'): 'string'}, ")
        case, = parse_trace_contract(rule)['cases']
        for value, expected in ((False, 'conflicting'), (None, 'conflicting'), ('A', 'matched')):
            with self.subTest(value=value):
                report = compare_trace_values(case, [
                    {'event': 'reply', 'detail': {'query_id': value}},
                    {'event': 'display', 'detail': {'query_id': value}},
                ])
                self.assertEqual(expected, report['status'], report)

    def test_workbench_historical_observations(self):
        root = Path(__file__).resolve().parents[5]
        contract, = (root / '_anechoic_anechoic').rglob('AN-S-3306@3-draft-*.md')
        pin = {'path': str(contract.relative_to(root)), 'atom_id': 'AN-S-3306', 'version': 3,
               'status': 'draft', 'container_component': 'C46'}
        _, declaration, issues = load_formal_claim(root, 'C46', 'contract', pin)
        self.assertFalse(issues, issues)
        case = next(parsed for language, text in declaration['claims'] if language == 'python trace'
                    and (parsed := parse_trace_contract(text)).get('output') == 'succeeded'
                    and parsed['action'] == 'workbench_frontend_run_view')
        script, = (root / 'LAYER_4_ENGINE_STUDIO_C14/ARCHITECTURE_ANALYSIS_C73').rglob(
            'workbench-reply-identity/replay.mjs')
        observed = json.loads(subprocess.check_output(
            ['node', str(script), '--observations'], timeout=30))
        by_probe = {(row['version'], row['queryId']): row for row in observed
                    if row['kind'] == 'run' and 'queryId' in row}
        for version, query_id, expected in (
            ('before', 'run-1', 'conflicting'), ('fixed', 'run-2', 'matched'),
        ):
            row = by_probe[version, query_id]
            result = compare_trace_values(case, [
                {'event': 'run_reply_with_query_id', 'detail': {'query_id': row['queryId']}},
                {'event': 'first_page_received', 'detail': {'query_id': row['accepted']}},
            ])
            self.assertEqual(expected, result['status'], result)
        self.assertNotIn('accepted', by_probe['fixed', 'run-1'])
