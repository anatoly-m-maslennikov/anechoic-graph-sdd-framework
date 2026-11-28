from contextlib import redirect_stderr
from io import StringIO
import json
import os
import subprocess
import tempfile
from unittest.mock import patch


from ORCHESTRATOR_beta_C68 import ORCHESTRATOR_beta_C68__shared as module
from ORCHESTRATOR_beta_C68.ORCHESTRATOR_beta_C68__tests.ORCHESTRATOR_beta_C68__tests__shared import (
    RunFixture,
)


class WorkerDiagnosticsCases:
    def test_generation_worker_does_not_relay_raw_traceback(self):
        with tempfile.TemporaryDirectory() as directory:
            binding = {
                "root": directory,
                "control_root": "control",
                "manifest_path": "manifest.md",
                "manifest_sha256": "a" * 64,
                "project_prefix": "AN",
            }
            jobs = module.GenerationJobs(
                "test", binding, directory + "/kernel.sock"
            )
            stderr = StringIO()
            with (
                patch.object(subprocess, "Popen") as popen,
                redirect_stderr(stderr),
            ):
                process = popen.return_value
                process.communicate.return_value = (
                    "",
                    "Traceback in inventory\nLimitReached: timeout_seconds\n",
                )
                process.returncode = 1
                with self.assertRaisesRegex(
                    RuntimeError,
                    "^Worker failed: LimitReached: timeout_seconds$",
                ):
                    jobs._run_worker(directory, None, None)
            self.assertNotIn("Traceback in inventory", stderr.getvalue())

    def test_opt_in_worker_timing_preserves_existing_diagnostics(self):
        prefix, timing_lines, expected = self._worker_timing_lines()
        for enabled, error in (("1", False), ("1", True), ("0", False)):
            with (
                self.subTest(enabled=enabled, error=error),
                tempfile.TemporaryDirectory() as directory,
                patch.dict(
                    os.environ,
                    ANECHOIC_STARTUP_TIMING=enabled,
                    ANECHOIC_LOG_LEVEL="INFO",
                ),
                patch.object(subprocess, "Popen") as popen,
                redirect_stderr(StringIO()) as stderr,
            ):
                self._capture_worker_timing(
                    directory,
                    popen.return_value,
                    timing_lines,
                    expected[-1],
                    error,
                )
                self._check_worker_timing(
                    stderr, prefix, expected, enabled, error
                )

    def _capture_worker_timing(
        self, directory, process, timing_lines, graph, error
    ):
        binding = {
            "root": directory,
            "control_root": "control",
            "manifest_path": "manifest.md",
            "manifest_sha256": "a" * 64,
            "project_prefix": "AN",
        }
        jobs = module.GenerationJobs(
            "test", binding, directory + "/kernel.sock"
        )
        lines = timing_lines + (["Original error"] if error else []) + [graph]
        process.communicate.return_value = (
            "{}",
            "\n".join(lines) + "\n",
        )
        process.returncode = int(error)
        if error:
            with self.assertRaisesRegex(
                RuntimeError, "^Worker failed: Original error$"
            ):
                jobs._communicate_worker(directory, {})
        else:
            self.assertEqual("{}", jobs._communicate_worker(directory, {}))

    def _check_worker_timing(self, stderr, prefix, expected, enabled, error):
        observed = stderr.getvalue().splitlines()
        timings = [line for line in observed if line.startswith(prefix)]
        if enabled == "1":
            start = json.loads(timings[0].removeprefix(prefix))
            self.assertEqual(
                ("worker_started", "cold"),
                (start["phase"], start["mode"]),
            )
            self.assertGreater(start["timestamp_ns"], 0)
            self.assertEqual(expected, timings[1:])
        else:
            self.assertFalse(timings)
        records = [
            json.loads(line)["code"]
            for line in observed
            if not line.startswith(prefix)
        ]
        self.assertIn("realization_graph_inputs_changed", records)
        self.assertEqual(not error, "worker_stderr_present" in records)
        self.assertNotIn("private", stderr.getvalue())

    @staticmethod
    def _worker_timing_lines():
        prefix = "ANECHOIC_STARTUP_TIMING "
        scan = prefix + (
            '{"phase":"scan_started","timestamp_ns":123,"mode":"foregroun'
            'd_capture"}'
        )
        graph = prefix + (
            '{"phase":"realization_graph_ready","timestamp_ns":124,"mode"'
            ':"built"}'
        )
        delta = prefix + json.dumps(
            {
                "phase": "non_archived_load_started",
                "timestamp_ns": 125,
                "changed_paths": 1,
                "checkpoint_validation_ns": 2,
                "comparison_ns": 3,
            }
        )
        spoof = graph[:-1] + ',"path":"private"}'
        oversized = (
            prefix
            + " " * 1024
            + '{"phase":"model_ready","timestamp_ns":125,"mode":"built"}'
        )
        restart = (
            "anechoic-realization-graph-restart "
            '{"sources":{"change":"added","path":"app/main.py"}}'
        )
        lines = [
            scan,
            delta,
            spoof,
            oversized,
            prefix
            + (
                '{"phase":"model_ready","timestamp_ns":1,"mode":"built","mode'
                '":"built"}'
            ),
            restart,
        ]
        return prefix, lines, [scan, delta, graph]

    def test_graph_restart_exhaustion_logs_safe_records_and_stops_automatic_retry(
        self,
    ):
        with tempfile.TemporaryDirectory() as directory:
            binding = {
                "root": directory,
                "control_root": "control",
                "manifest_path": "manifest.md",
                "manifest_sha256": "a" * 64,
                "project_prefix": "AN",
            }
            jobs = module.GenerationJobs(
                "test", binding, directory + "/kernel.sock"
            )
            jobs.startup_capture = True
            message = (
                "Project source or dependency inputs changed during capture "
                "after one Realization Graph restart"
            )
            payload = self._exhaustion_payload()
            stderr = StringIO()
            first = {"sources": {"change": "removed", "path": "app/first.py"}}
            restart = "anechoic-realization-graph-restart " + json.dumps(first)
            self._check_restart_exhaustion(
                jobs,
                payload,
                stderr,
                first,
                restart,
                message,
            )

    def _check_restart_exhaustion(
        self, jobs, payload, stderr, first, restart, message
    ):
        with (
            patch.object(subprocess, "Popen") as popen,
            redirect_stderr(stderr),
            patch.object(jobs, "_record_ingestion_failure") as record_failure,
        ):
            process = popen.return_value
            process.communicate.return_value = (
                json.dumps(payload),
                f"{restart}\nPrivate traceback\n{message}\n",
            )
            process.returncode = 1
            outcome = jobs._generate(startup=True)
        self.assertEqual("failed", outcome["state"])
        self.assertIn(message, outcome["message"])
        self.assertNotIn("retrying", outcome)
        retry = module.CurrentnessRetry()
        retry.observe(outcome)
        self.assertIsNone(retry.due)
        popen.assert_called_once()
        self.assertEqual(
            payload["ingestion_failure"],
            record_failure.call_args.args[0].diagnostic,
        )
        self._check_exhaustion_records(jobs, payload, stderr, first)

    def _check_exhaustion_records(self, jobs, payload, stderr, first):
        warning, record = (
            item
            for item in map(json.loads, stderr.getvalue().splitlines())
            if item["code"] == "realization_graph_inputs_changed"
        )
        self.assertEqual(
            ("WARNING", "restarting", first),
            (warning["severity"], warning["outcome"], warning["details"]),
        )
        self.assertEqual(jobs.latest.run_id, warning["correlation_id"])
        self.assertEqual(
            (
                "ERROR",
                "realization_graph_inputs_changed",
                jobs.latest.run_id,
            ),
            (record["severity"], record["code"], record["correlation_id"]),
        )
        self.assertEqual(
            {
                "sources": payload["graph_consistency"]["sources"],
                "resolution_inputs": {"change": "added"},
            },
            record["details"],
        )
        self.assertNotIn("private", stderr.getvalue().lower())

    @staticmethod
    def _exhaustion_payload():
        return {
            "ingestion_failure": {
                "source": "build",
                "issues": [{"code": "realization_scan_failed"}],
            },
            "graph_consistency": {
                "sources": {
                    "change": "changed",
                    "path": "app/main.py",
                    "fields": ["status", "imports"],
                },
                "resolution_inputs": {
                    "change": "added",
                    "path": "/absolute/token=private.txt",
                },
            },
        }

    def test_worker_success_relays_first_graph_difference_with_run_id(self):
        with tempfile.TemporaryDirectory() as directory:
            binding = {
                "root": directory,
                "control_root": "control",
                "manifest_path": "manifest.md",
                "manifest_sha256": "a" * 64,
                "project_prefix": "AN",
            }
            jobs = module.GenerationJobs(
                "test", binding, directory + "/kernel.sock"
            )
            jobs.active = RunFixture(
                state="running", started_at=0, run_id="a" * 32
            )
            details = {"sources": {"change": "added", "path": "app/main.py"}}
            restart = "anechoic-realization-graph-restart " + json.dumps(
                details
            )
            stderr = StringIO()
            with (
                patch.object(subprocess, "Popen") as popen,
                redirect_stderr(stderr),
            ):
                process = popen.return_value
                process.communicate.return_value = ("{}", f"\n{restart}\n")
                process.returncode = 0
                self.assertEqual("{}", jobs._communicate_worker(directory, {}))
            record = json.loads(stderr.getvalue())
            self.assertEqual(
                ("WARNING", "restarting", "a" * 32, details),
                (
                    record["severity"],
                    record["outcome"],
                    record["correlation_id"],
                    record["details"],
                ),
            )
