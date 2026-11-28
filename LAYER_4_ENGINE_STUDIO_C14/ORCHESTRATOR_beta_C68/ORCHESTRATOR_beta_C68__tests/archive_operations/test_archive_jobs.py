"""Check retry decisions for deferred archive capture."""

from contextlib import redirect_stderr
from errno import EACCES
from io import StringIO
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import Mock, patch

from watchdog.events import FileModifiedEvent, FileMovedEvent

from ORCHESTRATOR_beta_C68.archive_operations import archive_jobs
from ORCHESTRATOR_beta_C68.archive_operations.archive_operations__shared import (
    ArchiveCoverageLost,
    ArchiveInputsChanged,
)
from ORCHESTRATOR_beta_C68.generation.generation__shared import WorkerIngestionFailure
from ..ORCHESTRATOR_beta_C68__tests__shared import RunFixture, project_jobs
from ORCHESTRATOR_beta_C68.ORCHESTRATOR_beta_C68__tests.archive_operations._archive_reconciliation_cases import ArchiveReconciliationCases


class ArchiveJobsTests(ArchiveReconciliationCases, unittest.TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(TemporaryDirectory())).resolve()
        self.jobs = project_jobs(self.root)
        self.watcher = self.jobs.watcher
        self.addCleanup(self.watcher.close)
        self.jobs.watcher = Mock()
        self.jobs.watcher.archive_roots.return_value = ("control/09_archived",)
        self.jobs._communicate_worker = Mock(
            return_value=json.dumps({"snapshot": {}, "carrier_hashes": {}})
        )
        self.jobs._record_ingestion_issues = Mock()
        self.deferred = {
            "roots": ["control/09_archived"],
            "endpoints": {},
            "carrier_hashes": {},
        }
        self.jobs._accept_deferred_archive(self.deferred)

    def test_changed_fence_or_root_inventory_retries_without_watcher_event(
        self,
    ):
        for fence, after in ((False, ("control/09_archived",)), (True, ())):
            with self.subTest(fence=fence):
                self.jobs.archive_run = RunFixture(
                    state="running", started_at=0
                )
                self.jobs.archive_dirty = False
                self.jobs.watcher.capture_fence.return_value = fence
                self.jobs.watcher.archive_roots.side_effect = [
                    ("control/09_archived",),
                    after,
                ]
                with self.assertRaises(ArchiveInputsChanged) as changed:
                    self.jobs._archive_snapshot({})
                self.jobs.archive_result = changed.exception
                self.jobs._finish_archive()
                self.assertEqual("superseded", self.jobs.archive_run.state)
                self.assertTrue(self.jobs.archive_dirty)
        self.jobs._record_ingestion_issues.assert_not_called()

    def test_batched_archive_is_forwarded_and_cleaned_after_admission(self):
        self.jobs.deferred_archive["snapshot"] = {"atoms": [], "relations": []}
        self.jobs.archive_run = RunFixture(state="running", started_at=0)
        self.jobs.live_generation = "base"
        self.jobs.watcher.capture_fence.return_value = True
        descriptor = {"sha256": "a" * 64, "bytes": 1}

        def capture(directory, request):
            self.assertTrue(request["batch_full"])
            self.assertEqual(
                self.jobs.deferred_archive["snapshot"],
                request["archive"]["seed"]["snapshot"],
            )
            (Path(directory) / "generation-batches.jsonl").write_bytes(b"x")
            return {"batch_artifact": descriptor, "snapshot_sha256": "b" * 64}

        with patch.object(
            self.jobs, "_run_archive_worker", side_effect=capture
        ):
            self.jobs.archive_result = self.jobs._archive_snapshot(
                {}, None, self.jobs.deferred_archive
            )
        directory = Path(self.jobs.archive_result[1]["_archive_temp"].name)
        self.assertTrue(directory.name.startswith("anechoic-archive-"))
        with patch.object(
            archive_jobs,
            "admit_generation",
            return_value={"generation": "new"},
        ) as admit:
            self.jobs._finish_archive()
        self.assertEqual("succeeded", self.jobs.archive_run.state)
        self.assertFalse(directory.exists())
        self.assertEqual(str(directory.resolve()), admit.call_args.args[2])
        self.assertEqual(descriptor, admit.call_args.args[3]["batch_artifact"])
        self.assertEqual("base", admit.call_args.args[3]["base_generation"])

    def test_batched_archive_is_cleaned_on_fence_and_admission_failure(self):
        self.jobs.deferred_archive["snapshot"] = {"atoms": [], "relations": []}
        self.jobs.archive_run = RunFixture(state="running", started_at=0)
        directories = []

        def capture(directory, _request):
            directories.append(Path(directory))
            (directories[-1] / "generation-batches.jsonl").write_bytes(b"x")
            return {
                "batch_artifact": {"sha256": "a" * 64, "bytes": 1},
                "snapshot_sha256": "b" * 64,
            }

        with patch.object(
            self.jobs, "_run_archive_worker", side_effect=capture
        ):
            self.jobs.watcher.capture_fence.return_value = False
            with self.assertRaises(ArchiveInputsChanged):
                self.jobs._archive_snapshot(
                    {}, None, self.jobs.deferred_archive
                )
            self.assertFalse(directories[-1].exists())
            self.jobs.watcher.capture_fence.return_value = True
            self.jobs.archive_result = self.jobs._archive_snapshot(
                {}, None, self.jobs.deferred_archive
            )
        with patch.object(
            archive_jobs,
            "admit_generation",
            side_effect=ValueError("rejected"),
        ):
            self.jobs._finish_archive()
        self.assertFalse(directories[-1].exists())
        self.assertEqual("failed", self.jobs.archive_run.state)

    def test_fence_coverage_loss_fails_without_restarting(self):
        self.jobs.archive_run = RunFixture(state="running", started_at=0)
        self.jobs.watcher.capture_fence.return_value = None
        with self.assertRaises(ArchiveCoverageLost) as failure:
            self.jobs._archive_snapshot({})
        self.jobs.archive_result = failure.exception
        self.jobs._finish_archive()
        self.assertEqual("failed", self.jobs.archive_run.state)
        self.assertFalse(self.jobs.archive_dirty)
        source, issues = self.jobs._record_ingestion_issues.call_args.args
        self.assertEqual("archive", source)
        self.assertIn("coverage was lost", issues[0]["message"])

    def test_archive_fence_logs_first_safe_observation_and_existing_run_id(
        self,
    ):
        root = self.root
        watcher = self.jobs.watcher = self.watcher
        control = watcher.control_root
        archive = control / "09_archived"
        archive.mkdir(parents=True)
        watcher.start()
        self.assertTrue(watcher.watch_archives())
        self.jobs.archive_run = RunFixture(
            state="running", started_at=0, run_id="b" * 32
        )

        def capture(_directory, _request):
            watcher.dispatch(
                FileMovedEvent(
                    str(root.parent / "outside.md"),
                    str(archive / "first\nfile.md"),
                )
            )
            watcher.capture_epoch(archive=True)
            watcher.dispatch(FileModifiedEvent(str(archive / "later.md")))
            return {}

        diagnostics = StringIO()
        with (
            patch.object(
                self.jobs, "_run_archive_worker", side_effect=capture
            ),
            redirect_stderr(diagnostics),
        ):
            with self.assertRaisesRegex(
                ArchiveInputsChanged, "Archived Atom paths changed"
            ):
                self.jobs._archive_snapshot({})
        self._assert_fence_diagnostics(diagnostics, root)

    def _assert_fence_diagnostics(self, diagnostics, root):
        raw = diagnostics.getvalue()
        self.assertEqual(1, len(raw.splitlines()))
        self.assertNotIn(str(root), raw)
        self.assertNotIn("outside.md", raw)
        self.assertNotIn("later.md", raw)
        record = json.loads(raw)
        self.assertEqual(
            ("archive", "b" * 32, "source_changed"),
            (record["phase"], record["run_id"], record["reason"]),
        )
        self.assertEqual(
            {
                "kind": "moved",
                "destination": "control/09_archived/first file.md",
            },
            record["observation"],
        )

    def test_terminal_archive_coverage_error_survives_warning_filter(self):
        watcher = self.watcher
        archived = watcher.control_root / "09_archived" / "old.md"
        archived.parent.mkdir(parents=True)
        archived.touch()
        watcher.start()
        self.assertTrue(watcher.watch_archives())
        epoch = watcher.capture_epoch(archive=True, trace=True)
        self.assertIsNotNone(epoch)
        lstat = os.lstat

        def unreadable(path, *args, **kwargs):
            if path == str(archived):
                raise PermissionError(
                    EACCES, "Archive carrier cannot be read", path
                )
            return lstat(path, *args, **kwargs)

        with (
            patch.dict(os.environ, ANECHOIC_LOG_LEVEL="ERROR"),
            patch.object(os, "lstat", side_effect=unreadable),
            redirect_stderr(StringIO()) as stderr,
        ):
            self.assertIsNone(
                watcher.capture_fence(
                    epoch, archive=True, timeout=3, run_id="a" * 32
                )
            )
        observed = json.loads(stderr.getvalue())
        self.assertEqual(
            ("ERROR", "failed", "a" * 32),
            (
                observed["severity"],
                observed["outcome"],
                observed["correlation_id"],
            ),
        )
        self.assertEqual(
            ("archive", "coverage_lost"),
            (observed["phase"], observed["reason"]),
        )

    def test_live_refresh_retries_failed_archive_only_when_deferred_inputs_change(
        self,
    ):
        self.jobs.archive_run = RunFixture(state="failed", started_at=0)
        self.jobs._accept_deferred_archive(dict(self.deferred))
        self.assertFalse(self.jobs.archive_dirty)
        self.jobs._accept_deferred_archive(
            self.deferred | {"carrier_hashes": {"off-path.md": "a" * 64}}
        )
        self.assertTrue(self.jobs.archive_dirty)

    def test_off_path_archive_changes_supersede_pinned_capture(self):
        self.jobs.archive_run = RunFixture(state="running", started_at=0)
        self.jobs._accept_deferred_archive(dict(self.deferred))
        self.assertFalse(self.jobs.archive_dirty)
        self.jobs._accept_deferred_archive(
            self.deferred | {"carrier_hashes": {"off-path.md": "a" * 64}}
        )
        self.assertTrue(self.jobs.archive_dirty)
        self.jobs.archive_dirty = False
        self.jobs._accept_deferred_archive(
            self.deferred | {"roots": ["control/other/09_archived"]}
        )
        self.assertTrue(self.jobs.archive_dirty)

    def test_preserves_worker_diagnostic_rows_under_archive_source(self):
        issues = [
            {
                "relative_path": "control/09_archived/bad.md",
                "code": "invalid_schema",
            }
        ]
        self.jobs.archive_run = RunFixture(state="running", started_at=0)
        self.jobs.archive_result = WorkerIngestionFailure(
            "Worker failed", {"source": "atom", "issues": issues}
        )
        self.jobs._finish_archive()
        self.jobs._record_ingestion_issues.assert_called_once_with(
            "archive", issues
        )
