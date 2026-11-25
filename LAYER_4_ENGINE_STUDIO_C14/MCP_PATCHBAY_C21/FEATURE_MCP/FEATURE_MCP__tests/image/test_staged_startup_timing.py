"""Check packaged startup timing and resource measurements on the host."""
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock

from .startup_resources__support import cgroup_resources
from .staged_startup__support import (
    PackagedProbe, cold_throughput, started_at_ns, startup_events, startup_outcome, timing_summary,
)
from . import test_staged_startup_docker_e2e


class StartupTimingParsingTests(unittest.TestCase):
    def test_record_timing_waits_for_graph_before_assertion(self):
        probe = Mock(spec=PackagedProbe)
        pending = {'unobserved': ['realization_graph_ready']}
        complete = {'unobserved': [], 'events': [], 'started_at': 'start'}
        probe.timing.side_effect = [pending, complete]
        def wait(check, _label):
            self.assertFalse(check())
            self.assertTrue(check())
        probe.until.side_effect = wait
        probe.assert_timing.return_value = complete
        metrics = {'startup_timing': {}, 'startup_outcomes': {'cold': {}},
                   'cold_ready_seconds': 1, 'cold_first_query_seconds': 2}
        test = test_staged_startup_docker_e2e.PackagedStagedStartupTests()
        self.assertIs(complete, test._record_timing(probe, 'cold', metrics, True))
        probe.assert_timing.assert_called_once_with('cold')

    def test_cold_throughput_uses_kernel_admission_interval(self):
        events = [{'phase': 'non_archived_load_started', 'timestamp_ns': 500_000_000},
                  {'phase': 'non_archived_load_ended', 'timestamp_ns': 2_500_000_000, 'mode': 'full'}]
        self.assertEqual(10, cold_throughput({'events': events}, 20)['live_atoms_per_load_second'])
        self.assertIsNone(cold_throughput({'events': []}, 20)['live_atoms_per_load_second'])

    def test_startup_outcome_keeps_admitted_kind_and_reason(self):
        rows = [['old', 'output', 'generation_result', 'succeeded', '{"kind":"full"}'],
                ['new', 'trigger', 'startup', None, '{}'],
                ['new', 'effect', 'generation_admission', 'succeeded', '{"reuse_proof_present":true}']]
        self.assertIsNone(startup_outcome(rows))
        rows.append(['new', 'output', 'generation_result', 'succeeded', '{"kind":"native_delta","delta_path_count":5}'])
        result = startup_outcome(rows)
        self.assertEqual(('native_delta', 5), (result['kind'], result['delta_path_count']))
        self.assertIsNone(result['reason']['code'])
        self.assertEqual([['generation_admission', 'succeeded', {'reuse_proof_present': True}]],
                         result['reason']['effects'])

    def test_cgroup_counters_preserve_measured_zeros_and_unavailable_fields(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        cgroup, proc = root / 'cgroup', root / 'proc'
        cgroup.mkdir()
        for pid in ('1', 'self'):
            (proc / pid).mkdir(parents=True)
            (proc / pid / 'cgroup').write_text('0::/\n')
        (proc / 'self/mountinfo').write_text(f'29 28 0:26 / {cgroup} ro - cgroup2 cgroup rw\n')
        (cgroup / 'cgroup.procs').write_text(f'1\n{os.getpid()}\n')
        (cgroup / 'cpu.stat').write_text('usage_usec 1250000\n')
        (cgroup / 'io.stat').write_text('8:0 rbytes=64 wbytes=0\n8:1 rbytes=16 wbytes=0\n')
        result = cgroup_resources(cgroup, proc)
        self.assertEqual((1.25, 80, 0), (result['cpu_seconds'], result['block_read_bytes'], result['block_write_bytes']))
        self.assertIsNone(result['peak_memory_bytes'])
        self.assertIn('peak_memory_bytes', result['unavailable'])
        (cgroup / 'memory.peak').write_text('4096\n')
        self.assertEqual(4096, cgroup_resources(cgroup, proc)['peak_memory_bytes'])
        (cgroup / 'io.stat').write_text('')
        self.assertIsNone(cgroup_resources(cgroup, proc)['block_read_bytes'])
        (proc / '1/cgroup').write_text('0::/other\n')
        self.assertIsNone(cgroup_resources(cgroup, proc)['cpu_seconds'])

    def test_filters_prior_starts_and_preserves_details(self):
        start = started_at_ns('2026-11-25T01:02:03.123456789Z')
        lines = [
            'ANECHOIC_STARTUP_TIMING ' + json.dumps({'phase': 'scan_started', 'timestamp_ns': start - 1}),
            'prefix ANECHOIC_STARTUP_TIMING ' + json.dumps({'phase': 'scan_started', 'timestamp_ns': start}),
            'ANECHOIC_STARTUP_TIMING malformed',
            'ANECHOIC_STARTUP_TIMING ' + json.dumps({'phase': 'scan_metrics', 'timestamp_ns': start + 500_000_000,
                                                       'carrier_count': 7, 'changed_paths': 3, 'comparison_ns': 9,
                                                       'checkpoint_validation_ns': 8, 'path': '/secret'}),
            'ANECHOIC_STARTUP_TIMING ' + json.dumps({'phase': 'model_ready', 'timestamp_ns': True}),
            'ANECHOIC_STARTUP_TIMING ' + json.dumps({'phase': [], 'timestamp_ns': start}),
            'ANECHOIC_STARTUP_TIMING ' + json.dumps({'phase': 'model_ready', 'timestamp_ns': start + 1,
                                                       'mode': 'reused'}),
        ]
        self.assertEqual([{'phase': 'model_ready', 'timestamp_ns': start + 1, 'mode': 'reused',
                           'launch_to_phase_seconds': 1e-9},
                          {'phase': 'scan_metrics', 'timestamp_ns': start + 500_000_000,
                           'carrier_count': 7, 'changed_paths': 3, 'comparison_ns': 9,
                           'checkpoint_validation_ns': 8, 'launch_to_phase_seconds': .5}],
                         startup_events('\n'.join(lines), start))
        self.assertEqual(start - 123456789, started_at_ns('2026-11-25T01:02:03Z'))
        with self.assertRaises(ValueError):
            started_at_ns('not-a-docker-start-time')

    def test_missing_phases_and_disabled_archive_are_explicit(self):
        started = '2026-11-25T01:02:03Z'
        start = started_at_ns(started)
        logs = 'ANECHOIC_STARTUP_TIMING ' + json.dumps({
            'phase': 'non_archived_load_ended', 'timestamp_ns': start + 1, 'archive': 'disabled',
        })
        summary = timing_summary(logs, started)
        self.assertEqual({'archive_load_ended': 'disabled'}, summary['not_applicable'])
        self.assertNotIn('archive_load_ended', summary['unobserved'])
        self.assertIn('model_ready', summary['unobserved'])
        self.assertNotIn('non_archived_load_ended', summary['unobserved'])
        self.assertEqual(['worker_started', 'scan_metrics'], summary['optional_phases'])
        self.assertIn('archive_load_ended', timing_summary('', started)['unobserved'])

    def test_scan_duration_uses_same_mode_and_observed_timestamps(self):
        started = '2026-11-25T01:02:03Z'
        start = started_at_ns(started)
        rows = [
            {'phase': 'scan_started', 'timestamp_ns': start + 1_000_000_000, 'mode': 'foreground_capture'},
            {'phase': 'scan_metrics', 'timestamp_ns': start + 2_000_000_000, 'mode': 'foreground_hashes'},
            {'phase': 'scan_metrics', 'timestamp_ns': start + 3_000_000_000, 'mode': 'foreground_capture'},
        ]
        logs = '\n'.join('ANECHOIC_STARTUP_TIMING ' + json.dumps(row) for row in rows)
        events = timing_summary(logs, started)['events']
        self.assertNotIn('scan_seconds', events[1])
        self.assertEqual(2, events[2]['scan_seconds'])

    def test_timing_assertion_rejects_missing_milestones_and_scan_duration(self):
        probe = PackagedProbe.__new__(PackagedProbe)
        probe.case = self
        result = {'unobserved': ['model_ready'], 'not_applicable': {}, 'events': []}
        probe.timing = lambda _phase: result
        with self.assertRaisesRegex(AssertionError, 'model_ready'):
            probe.assert_timing('cold')
        result['unobserved'] = []
        with self.assertRaisesRegex(AssertionError, 'foreground scan timing'):
            probe.assert_timing('cold')
        result['events'] = [{'phase': 'scan_metrics', 'mode': 'foreground_capture', 'scan_seconds': 1.0}]
        self.assertIs(result, probe.assert_timing('cold'))
