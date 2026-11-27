import os
import shutil
import unittest
from unittest.mock import patch

from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_2_SPEC_READING_C83.SPECIFICATION_MODEL_C85._package__shared import parse_trace_contract
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_3_LEAN_TRANSLATOR_C84._package__shared import compile_lean
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75._package__shared import verify_formal_chain
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.SPEC_ENGINE_C75__tests.functional.test_trace_cases import FIRST, SECOND, SOLUTION, model


RESOURCES = "{'cpu_cores': 0.5, 'ram_mib': 1536, 'disk_mib': 4096}"
LATENCY = "{'from': 'request_received', 'to': 'response_sent', 'workload': 'single', 'statistic': 'p95', 'max_ms': 45}"
THROUGHPUT = "{'from': 'request_received', 'to': 'query_visible', 'workload': 'batch', 'min_requests_per_second': 2.5}"
PERFORMANCE = "{'resources': " + RESOURCES + ", 'measurements': {'response': " + LATENCY + ", 'completion': " + THROUGHPUT + "}}"


def claim(performance=PERFORMANCE, binding=''):
    return "declare_trace_contract(action='compile', output='python', performance=" + performance + binding + ")"


class TracePerformanceTests(unittest.TestCase):
    def test_unbound_and_bound_declarations(self):
        expected = parse_trace_contract(claim())['performance']
        self.assertEqual({'cpu_cores': 0.5, 'ram_mib': 1536, 'disk_mib': 4096}, expected['resources'])
        self.assertEqual({'response', 'completion'}, set(expected['measurements']))
        for binding in (", interface='i', transport='http', route='/x', operation='POST /x'",
                        ", interface='i', transport='in_process', entry='service.run'"):
            self.assertEqual(expected, parse_trace_contract(claim(binding=binding))['performance'])
        self.assertNotIn('performance', parse_trace_contract(FIRST))

    def test_rejects_invalid_performance(self):
        invalid = [
            "{}", PERFORMANCE.replace(RESOURCES, "{}"),
            PERFORMANCE.replace("'cpu_cores': 0.5", "'cpu_cores': True"),
            PERFORMANCE.replace("'cpu_cores': 0.5", "'cpu_cores': 1e999"),
            PERFORMANCE.replace("'cpu_cores': 0.5", "'cpu_cores': -1"),
            PERFORMANCE.replace("'ram_mib': 1536", "'ram_mib': 1.5"),
            PERFORMANCE.replace("'disk_mib': 4096", "'disk_mib': 0"),
            PERFORMANCE.replace("'disk_mib': 4096", "'disk_mib': True"),
            PERFORMANCE.replace("'disk_mib': 4096", "'disk_mib': 1, 'gpu': 1"),
            PERFORMANCE.replace("'measurements': {", "'measurements': {'response': " + LATENCY + ", "),
            PERFORMANCE.replace("'measurements': {'response': " + LATENCY + ", 'completion': " + THROUGHPUT + "}", "'measurements': {}"),
            PERFORMANCE.replace("'from': 'request_received'", "'from': ' '", 1),
            PERFORMANCE.replace("'to': 'response_sent'", "'to': 'request_received'"),
            PERFORMANCE.replace("'workload': 'single'", "'workload': ''"),
            PERFORMANCE.replace("'statistic': 'p95'", "'statistic': 'average'"),
            PERFORMANCE.replace("'max_ms': 45", "'max_ms': True"),
            PERFORMANCE.replace("'max_ms': 45", "'max_ms': 1.5"),
            PERFORMANCE.replace("'max_ms': 45", "'max_ms': 0"),
            PERFORMANCE.replace("'min_requests_per_second': 2.5", "'min_requests_per_second': 1e999"),
            PERFORMANCE.replace("'min_requests_per_second': 2.5", "'min_requests_per_second': False"),
            PERFORMANCE.replace("'min_requests_per_second': 2.5", "'min_requests_per_second': 2, 'statistic': 'p95'"),
            PERFORMANCE.replace("'max_ms': 45", "'max_ms': 45, 'other': 1"),
            PERFORMANCE.replace("'max_ms': 45", "'max_ms': 45, 'max_ms': 46"),
        ]
        for value in invalid:
            with self.subTest(value=value), self.assertRaises(ValueError):
                parse_trace_contract(claim(value))

    def test_translation_and_comparison_across_cases_and_operations(self):
        lean = os.environ.get('ANECHOIC_TEST_LEAN') or os.environ.get('LEAN_BIN') or shutil.which('lean')
        self.assertTrue(lean, 'Set ANECHOIC_TEST_LEAN or LEAN_BIN, or put lean on PATH')
        sample = model()
        boundaries = {'state': {'reads': [], 'writes': []}}
        sample['manifest']['fields']['boundaries'] = sample['manifest']['boundaries'] = boundaries
        sample['contract']['claims'] = [('python trace', FIRST[:-1] + ', performance=' + PERFORMANCE + ')'),
            ('python trace', SECOND[:-1] + ', performance=' + PERFORMANCE + ')'),
            ('python trace', FIRST.replace('compile', 'other')[:-1] + ', performance=' + PERFORMANCE + ')')]
        sample['solution']['claims'].append(('python', SOLUTION.replace("action='compile'", "action='other'")))
        compiled = compile_lean(sample)
        self.assertEqual(parse_trace_contract(claim())['performance'],
                         compiled['claims']['contract']['operations']['compile']['cases'][0]['performance'])
        for action, expected in ((None, {('compile', 'python'), ('compile', 'cfel'), ('other', 'python')}),
                                 ('compile', {('compile', 'python'), ('compile', 'cfel')}),
                                 ('other', {('other', 'python')})):
            with patch('FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.formal_chain__pub.load_boundary_model', return_value=sample):
                result = verify_formal_chain('.', 'C15', {}, {}, {}, action=action, lean=lean)
            self.assertEqual('matched', result['translation']['status'])
            facts = [fact for fact in result['directions']['contract_solution']['facts'] if fact['key'] == 'performance']
            self.assertEqual(expected, {(fact['action'], fact['output']) for fact in facts})
            self.assertEqual(2 * len(expected), len(facts))
            self.assertEqual({'unresolved'}, {fact['status'] for fact in facts})
            self.assertEqual('unresolved', result['directions']['contract_solution']['status'])
        changed = {**compiled, 'lean': compiled['lean'].replace('1536', '1537', 1)}
        with patch('FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.formal_chain__pub.load_boundary_model', return_value=sample), \
             patch('FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.formal_chain__pub.compile_lean', return_value=changed):
            result = verify_formal_chain('.', 'C15', {}, {}, {}, lean=lean)
        self.assertEqual('incomplete', result['outcome'])
        self.assertEqual('conflicting', result['translation']['status'])
