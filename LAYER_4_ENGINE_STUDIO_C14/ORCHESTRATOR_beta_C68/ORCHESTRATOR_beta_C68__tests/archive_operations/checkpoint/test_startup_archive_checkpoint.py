"""Exercise the default startup checkpoint and deferred Archive protocol."""

from ORCHESTRATOR_beta_C68.ORCHESTRATOR_beta_C68__tests.archive_operations.checkpoint.startup_archive_checkpoint_cases import StartupArchiveCheckpointCases
from contextlib import redirect_stderr
from io import StringIO
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import Mock, patch

from .... import ORCHESTRATOR_beta_C68__shared as orchestrator
from ...ORCHESTRATOR_beta_C68__tests__shared import kernel_server


from ORCHESTRATOR_beta_C68.ORCHESTRATOR_beta_C68__tests.archive_operations.checkpoint._startup_checkpoint_observations import (
    StartupCheckpointObservations,
    timing_records,
)


class StartupArchiveCheckpointTests(
    StartupArchiveCheckpointCases,
    StartupCheckpointObservations,
    unittest.TestCase,
):
    def setUp(self):
        root = Path(self.enterContext(TemporaryDirectory())).resolve()
        binding = {
            "root": str(root),
            "control_root": "control",
            "manifest_path": "manifest.md",
            "manifest_sha256": "a" * 64,
            "project_prefix": "AN",
        }
        self.jobs = orchestrator.GenerationJobs("test", binding, "socket")
        self.jobs.startup_capture = True
        self.jobs.watcher = Mock()
        self.jobs.watcher.archive_roots.return_value = ()
        self.jobs.watcher.capture_fence.return_value = True
        self.jobs._record_ingestion_issues = Mock()
        self.reuse = {
            "base_generation": "old",
            "inputs": {"carrier_schema": "a" * 64},
            "graph_config": None,
            "endpoints": {},
            "carrier_hashes": {
                "control/a.md": "b" * 64,
                "control/09_archived/a.md": "c" * 64,
            },
            "folder_hashes": {
                "control": "d" * 64,
                "control/09_archived": "e" * 64,
            },
        }

    def test_scoped_startup_loads_archive_checkpoint_in_background(self):
        foreground = self.reuse | {
            "checkpoint_scope": "foreground",
            "carrier_hashes": {},
            "folder_hashes": {},
        }
        self.jobs.deferred_archive = self.jobs._restart_archive(
            foreground, {"unchanged": True}
        )
        result = {"unchanged": True}
        self.jobs.watcher.watch_archives.return_value = True
        record = orchestrator.ReuseRecord.model_validate(
            self.reuse | {"checkpoint_scope": "archive"}
        )
        with (
            patch(
                "ORCHESTRATOR_beta_C68.archive_operations.archive_jobs.read_reuse",
                return_value=record,
            ) as read,
            patch.object(
                self.jobs, "_archive_snapshot", return_value=({}, result)
            ) as capture,
        ):
            self.jobs._capture_archive(self.jobs.deferred_archive)
        read.assert_called_once_with("socket", "test", scope="archive")
        self.assertEqual(
            {"control/09_archived/a.md": "c" * 64},
            capture.call_args.args[1]["carrier_hashes"],
        )
        self.assertEqual(({}, result), self.jobs.archive_result)

    def test_missing_background_checkpoint_forces_archive_replacement(self):
        foreground = self.reuse | {
            "checkpoint_scope": "foreground",
            "carrier_hashes": {},
            "folder_hashes": {},
        }
        self.jobs.deferred_archive = self.jobs._restart_archive(
            foreground, {"unchanged": True}
        )
        self.jobs.watcher.watch_archives.return_value = True
        with (
            patch(
                "ORCHESTRATOR_beta_C68.archive_operations.archive_jobs.read_reuse",
                return_value=None,
            ),
            patch.object(
                self.jobs,
                "_archive_snapshot",
                return_value=({}, {"snapshot": {}}),
            ) as capture,
        ):
            self.jobs._capture_archive(self.jobs.deferred_archive)
        self.assertIsNone(capture.call_args.args[1])
        self.assertTrue(self.jobs.archive_result[1]["replace"])

    def test_legacy_or_uncovered_checkpoint_builds_fresh_foreground(self):
        result = {
            "snapshot": {},
            "deferred_archive": {
                "roots": [],
                "snapshot": {"atoms": []},
                "endpoints": {},
            },
        }
        legacy = {
            key: value
            for key, value in self.reuse.items()
            if key != "folder_hashes"
        }
        for reuse, epoch in ((legacy, ("watcher", 1)), (self.reuse, None)):
            self.jobs.startup_capture = True
            self.jobs.watcher.capture_epoch.return_value = epoch
            with (
                patch.object(
                    self.jobs, "_run_worker", return_value=result.copy()
                ) as worker,
                patch.object(
                    orchestrator,
                    "admit_generation",
                    return_value={"generation": "new", "kind": "full"},
                ),
            ):
                self.assertEqual(
                    "full", self.jobs._attempt_generation(None, reuse)["kind"]
                )
            self.assertIsNone(worker.call_args.args[1])
            self.assertEqual(
                {
                    "foreground": True,
                    "watcher_guarded": epoch is not None,
                    "force_model": False,
                },
                worker.call_args.kwargs,
            )

    def test_replay_coverage_loss_discards_result_until_recovery(self):
        self.jobs.thread = object()
        self.jobs.watcher.watch_code = False
        self.jobs.watcher.replay_fence.return_value = None
        with (
            patch.object(
                self.jobs, "_run_worker", return_value={"snapshot": {}}
            ) as worker,
            patch.object(self.jobs, "_admit_live_result") as admit,
        ):
            outcome = self.jobs._generate(startup=True)
        self.assertEqual("watcher_coverage_lost", outcome["code"])
        self.assertTrue(outcome["retrying"])
        worker.assert_called_once()
        admit.assert_not_called()

    def test_recovery_falls_back_to_fenced_capture_for_an_incompatible_delta(
        self,
    ):
        checkpoint = Mock()
        checkpoint.model_dump.return_value = self.reuse
        outcome = {"state": "succeeded", "kind": "full"}
        with (
            patch(
                "ORCHESTRATOR_beta_C68.generation.worker.generation_worker.read_reuse",
                return_value=checkpoint,
            ),
            patch.object(
                self.jobs,
                "_attempt_generation",
                side_effect=[
                    orchestrator.DeltaRequiresReconciliation(),
                    outcome,
                ],
            ) as attempt,
        ):
            self.assertEqual(
                outcome, self.jobs._recover_watcher_coverage(None)
            )
        self.assertEqual(
            [(None, self.reuse), (None, None)],
            [call.args for call in attempt.call_args_list],
        )
        self.assertTrue(
            all(
                call.kwargs == {"recover_coverage": True}
                for call in attempt.call_args_list
            )
        )

    def test_failed_replay_capture_retries_only_with_a_queued_source_change(
        self,
    ):
        self.jobs.thread = object()
        self.jobs.watcher.watch_code = False
        self.jobs.watcher.replay_fence.return_value = True
        self.jobs.watcher.foreground_events.side_effect = [0, 1, 1, 1]
        error = ValueError("Original ingestion issue")
        with (
            patch.object(self.jobs, "_run_worker", side_effect=error),
            patch.object(self.jobs, "_record_ingestion_failure") as record,
        ):
            changed = self.jobs._generate(startup=True)
            stable = self.jobs._generate(startup=True)
        self.assertTrue(changed["retrying"])
        self.assertEqual("Original ingestion issue", stable["message"])
        self.assertNotIn("retrying", stable)
        self.assertEqual(
            [error, error], [call.args[0] for call in record.call_args_list]
        )

    def test_archive_delta_admits_against_latest_live_generation(self):
        self.jobs.deferred_archive = self.jobs._restart_archive(
            self.reuse, {"unchanged": True}
        )
        archive = self.jobs.deferred_archive["checkpoint"]
        old = {
            "base_generation": "old",
            "paths": [["control/09_archived", "a.md"]],
            "snapshot": {},
            "carrier_hashes": {},
            "snapshot_sha256": "0" * 64,
        }
        self.jobs._communicate_worker = Mock(return_value=json.dumps(old))
        _, result = self.jobs._archive_snapshot({}, archive)
        self.assertEqual(old, result)
        request = self.jobs._communicate_worker.call_args.args[1]
        self.assertTrue(request["incremental"])
        self.assertEqual(archive, request["reuse"])
        self.jobs.live_generation = "latest"
        root = Path(self.jobs.binding["root"])
        with (
            kernel_server(root) as kernel,
            patch.dict(os.environ, ANECHOIC_STARTUP_TIMING="1"),
            redirect_stderr(StringIO()) as stderr,
        ):
            self.jobs.database_socket = str(root / "kernel.sock")
            kernel.reject = True
            with self.assertRaisesRegex(
                RuntimeError, "Kernel rejected generation"
            ):
                self.jobs._admit_archive(result)
            self.assertFalse(timing_records(stderr))
            kernel.reject = False
            self.jobs._admit_archive(result)
        (record,) = timing_records(stderr)
        self.assertGreater(record.pop("timestamp_ns"), 0)
        self.assertEqual(
            {"phase": "archive_load_ended", "mode": "native_delta"}, record
        )
        self.assertEqual(["/generation/archive"] * 2, kernel.paths)
        self.assertEqual(
            [old | {"instance_id": "test", "base_generation": "latest"}] * 2,
            kernel.payloads,
        )
        self.assertIsNone(self.jobs.deferred_archive)

    def test_full_archive_reply_requires_closed_envelope(self):
        request = {"reuse": None, "archive": {"roots": (), "endpoints": {}}}
        valid = {
            "snapshot": {"atoms": []},
            "carrier_hashes": {"control/a.md": "hash"},
        }
        self.jobs._communicate_worker = Mock(return_value=json.dumps(valid))
        self.assertEqual(
            valid, self.jobs._run_archive_worker("/test", request)
        )
        for invalid in (
            valid | {"extra": 1},
            {"snapshot": {}},
            valid | {"snapshot": []},
            valid | {"carrier_hashes": []},
        ):
            with self.subTest(invalid=invalid):
                self.jobs._communicate_worker.return_value = json.dumps(
                    invalid
                )
                with self.assertRaisesRegex(
                    ValueError, "Worker returned invalid Archive result"
                ):
                    self.jobs._run_archive_worker("/test", request)

    def test_archive_incompatibility_recaptures_only_archive(self):
        captured = {
            "snapshot": {"atoms": [], "relations": []},
            "carrier_hashes": {},
        }
        self.jobs._communicate_worker = Mock(
            side_effect=['{"incompatible":true}', json.dumps(captured)]
        )
        request = {
            "reuse": self.reuse,
            "archive": {"roots": (), "endpoints": {}},
        }
        result = self.jobs._run_archive_worker("/test", request)
        self.assertEqual(captured | {"replace": True}, result)
        first, second = [
            call.args[1]
            for call in self.jobs._communicate_worker.call_args_list
        ]
        self.assertEqual(request | {"incremental": True}, first)
        self.assertEqual(request | {"reuse": None}, second)
