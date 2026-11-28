"""Check packaged startup timing and resource measurements on the host."""

import json


from ....image.historical import (
    historical_generation_load__support as generation_load,
)
from ....image.image__shared import PackagedProbe
from ....image.image__shared import started_at_ns
from ....image.image__shared import startup_events
from ....image.image__shared import timing_summary

summarize_queries = generation_load.summarize_queries
capture_workers = generation_load.capture_workers
archive_running = generation_load.archive_running
BATCH_START = generation_load.BATCH_START
BATCH_SIZE = generation_load.BATCH_SIZE
BATCH_SQL = generation_load.BATCH_SQL
watcher_detection_bounds = generation_load.watcher_detection_bounds


class _StartupTimingCases:
    def _assert_filtered_startup_events(self, lines, start):
        expected = [
            {
                "phase": "model_ready",
                "timestamp_ns": start + 1,
                "mode": "reused",
                "launch_to_phase_seconds": 1e-9,
            },
            {
                "phase": "scan_metrics",
                "timestamp_ns": start + 500_000_000,
                "carrier_count": 7,
                "changed_paths": 3,
                "comparison_ns": 9,
                "checkpoint_validation_ns": 8,
                "launch_to_phase_seconds": 0.5,
            },
        ]
        self.assertEqual(expected, startup_events("\n".join(lines), start))

    def test_filters_prior_starts_and_preserves_details(self):
        start = started_at_ns("2026-11-25T01:02:03.123456789Z")
        lines = [
            "ANECHOIC_STARTUP_TIMING "
            + json.dumps({"phase": "scan_started", "timestamp_ns": start - 1}),
            "prefix ANECHOIC_STARTUP_TIMING "
            + json.dumps({"phase": "scan_started", "timestamp_ns": start}),
            "ANECHOIC_STARTUP_TIMING malformed",
            "ANECHOIC_STARTUP_TIMING "
            + json.dumps({
                "phase": "scan_metrics",
                "timestamp_ns": start + 500_000_000,
                "carrier_count": 7,
                "changed_paths": 3,
                "comparison_ns": 9,
                "checkpoint_validation_ns": 8,
                "path": "/secret",
            }),
            "ANECHOIC_STARTUP_TIMING "
            + json.dumps({"phase": "model_ready", "timestamp_ns": True}),
            "ANECHOIC_STARTUP_TIMING "
            + json.dumps({"phase": [], "timestamp_ns": start}),
            "ANECHOIC_STARTUP_TIMING "
            + json.dumps({
                "phase": "model_ready",
                "timestamp_ns": start + 1,
                "mode": "reused",
            }),
        ]
        self._assert_filtered_startup_events(lines, start)
        self.assertEqual(
            start - 123456789, started_at_ns("2026-11-25T01:02:03Z")
        )
        with self.assertRaises(ValueError):
            started_at_ns("not-a-docker-start-time")

    def test_missing_phases_and_disabled_archive_are_explicit(self):
        started = "2026-11-25T01:02:03Z"
        start = started_at_ns(started)
        logs = "ANECHOIC_STARTUP_TIMING " + json.dumps({
            "phase": "non_archived_load_ended",
            "timestamp_ns": start + 1,
            "archive": "disabled",
        })
        summary = timing_summary(logs, started)
        self.assertEqual(
            {"archive_load_ended": "disabled"}, summary["not_applicable"]
        )
        self.assertNotIn("archive_load_ended", summary["unobserved"])
        self.assertIn("model_ready", summary["unobserved"])
        self.assertNotIn("non_archived_load_ended", summary["unobserved"])
        self.assertEqual(
            ["worker_started", "scan_metrics"], summary["optional_phases"]
        )
        self.assertIn(
            "archive_load_ended", timing_summary("", started)["unobserved"]
        )

    def test_scan_duration_uses_same_mode_and_observed_timestamps(self):
        started = "2026-11-25T01:02:03Z"
        start = started_at_ns(started)
        rows = [
            {
                "phase": "scan_started",
                "timestamp_ns": start + 1_000_000_000,
                "mode": "foreground_capture",
            },
            {
                "phase": "scan_metrics",
                "timestamp_ns": start + 2_000_000_000,
                "mode": "foreground_hashes",
            },
            {
                "phase": "scan_metrics",
                "timestamp_ns": start + 3_000_000_000,
                "mode": "foreground_capture",
            },
        ]
        logs = "\n".join(
            "ANECHOIC_STARTUP_TIMING " + json.dumps(row) for row in rows
        )
        events = timing_summary(logs, started)["events"]
        self.assertNotIn("scan_seconds", events[1])
        self.assertEqual(2, events[2]["scan_seconds"])

    def test_timing_assertion_rejects_missing_milestones_and_scan_duration(
        self,
    ):
        probe = PackagedProbe.__new__(PackagedProbe)
        probe.case = self
        result = {
            "unobserved": ["model_ready"],
            "not_applicable": {},
            "events": [],
        }
        probe.timing = lambda _phase: result
        with self.assertRaisesRegex(AssertionError, "model_ready"):
            probe.assert_timing("cold")
        result["unobserved"] = []
        with self.assertRaisesRegex(AssertionError, "foreground scan timing"):
            probe.assert_timing("cold")
        result["events"] = [
            {
                "phase": "scan_metrics",
                "mode": "foreground_capture",
                "scan_seconds": 1.0,
            }
        ]
        self.assertIs(result, probe.assert_timing("cold"))
