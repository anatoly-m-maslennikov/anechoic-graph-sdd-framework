"""Check retry decisions for deferred archive capture."""
from contextlib import redirect_stderr
from io import StringIO
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Lock
import unittest
from unittest.mock import Mock, patch

from watchdog.events import FileModifiedEvent, FileMovedEvent

from .. import ORCHESTRATOR_beta_C68__shared as orchestrator
from ..archive_jobs import ArchiveCoverageLost, ArchiveInputsChanged, ArchiveJobs
from ..generation import WorkerIngestionFailure
from ..watcher import SourceWatcher
from ..watcher_diagnostics import report_fence_failure


class ArchiveJobsTests(unittest.TestCase):
    def setUp(self):
        self.jobs = ArchiveJobs()
        self.jobs._initialize_archive()
        self.jobs.binding = {}
        self.jobs.lock = Lock()
        self.jobs.watcher = Mock()
        self.jobs.watcher.archive_roots.return_value = ("control/09_archived",)
        self.jobs._communicate_worker = Mock(return_value="{}")
        self.jobs._record_ingestion_issues = Mock()
        self.deferred = {"roots": ["control/09_archived"], "endpoints": {}, "carrier_hashes": {}}
        self.jobs._accept_deferred_archive(self.deferred)

    def test_changed_fence_or_root_inventory_retries_without_watcher_event(self):
        for fence, after in ((False, ("control/09_archived",)), (True, ())):
            with self.subTest(fence=fence):
                self.jobs.archive_run = {"state": "running"}
                self.jobs.archive_dirty = False
                self.jobs.watcher.capture_fence.return_value = fence
                self.jobs.watcher.archive_roots.side_effect = [("control/09_archived",), after]
                with self.assertRaises(ArchiveInputsChanged) as changed:
                    self.jobs._archive_snapshot({})
                self.jobs.archive_result = changed.exception
                self.jobs._finish_archive()
                self.assertEqual("superseded", self.jobs.archive_run["state"])
                self.assertTrue(self.jobs.archive_dirty)
        self.jobs._record_ingestion_issues.assert_not_called()

    def test_fence_coverage_loss_fails_without_restarting(self):
        self.jobs.archive_run = {"state": "running"}
        self.jobs.watcher.capture_fence.return_value = None
        with self.assertRaises(ArchiveCoverageLost) as failure:
            self.jobs._archive_snapshot({})
        self.jobs.archive_result = failure.exception
        self.jobs._finish_archive()
        self.assertEqual("failed", self.jobs.archive_run["state"])
        self.assertFalse(self.jobs.archive_dirty)
        source, issues = self.jobs._record_ingestion_issues.call_args.args
        self.assertEqual("archive", source)
        self.assertIn("coverage was lost", issues[0]["message"])

    def test_archive_fence_logs_first_safe_observation_and_existing_run_id(self):
        root = Path(self.enterContext(TemporaryDirectory())).resolve()
        control = root / "control"
        archive = control / "09_archived"
        archive.mkdir(parents=True)
        watcher = self.jobs.watcher = SourceWatcher(root, control, defer_archives=True)
        self.addCleanup(watcher.close)
        watcher.start()
        self.assertTrue(watcher.watch_archives())
        self.jobs.archive_run = {"state": "running", "run_id": "b" * 32}

        def capture(_directory, _request):
            watcher.dispatch(FileMovedEvent(str(root.parent / "outside.md"), str(archive / "first\nfile.md")))
            watcher.capture_epoch(archive=True)
            watcher.dispatch(FileModifiedEvent(str(archive / "later.md")))
            return {}

        diagnostics = StringIO()
        with patch.object(self.jobs, "_run_archive_worker", side_effect=capture), redirect_stderr(diagnostics):
            with self.assertRaisesRegex(ArchiveInputsChanged, "Archived Atom paths changed"):
                self.jobs._archive_snapshot({})
        raw = diagnostics.getvalue()
        self.assertEqual(1, len(raw.splitlines()))
        self.assertNotIn(str(root), raw)
        self.assertNotIn("outside.md", raw)
        self.assertNotIn("later.md", raw)
        record = json.loads(raw)
        self.assertEqual(("archive", "b" * 32, "source_changed"),
                         (record["phase"], record["run_id"], record["reason"]))
        self.assertEqual({"kind": "moved", "destination": "control/09_archived/first file.md"},
                         record["observation"])

    def test_terminal_archive_coverage_error_survives_warning_filter(self):
        import os

        report = {"code": "watcher_fence_failed", "phase": "archive", "reason": "coverage_lost", "run_id": "a" * 32}
        with patch.dict(os.environ, ANECHOIC_LOG_LEVEL="ERROR"), redirect_stderr(StringIO()) as stderr:
            report_fence_failure(report)
        observed = json.loads(stderr.getvalue())
        self.assertEqual(("ERROR", "failed", "a" * 32),
                         (observed["severity"], observed["outcome"], observed["correlation_id"]))

    def test_live_refresh_retries_failed_archive_only_when_deferred_inputs_change(self):
        self.jobs.archive_run = {"state": "failed"}
        self.jobs._accept_deferred_archive(dict(self.deferred))
        self.assertFalse(self.jobs.archive_dirty)
        self.jobs._accept_deferred_archive(self.deferred | {"carrier_hashes": {"off-path.md": "a" * 64}})
        self.assertTrue(self.jobs.archive_dirty)

    def test_off_path_archive_changes_can_join_in_flight_capture(self):
        self.jobs.archive_run = {"state": "running"}
        self.jobs._accept_deferred_archive(self.deferred | {"carrier_hashes": {"off-path.md": "a" * 64}})
        self.assertFalse(self.jobs.archive_dirty)
        self.jobs._accept_deferred_archive(self.deferred | {"roots": ["control/other/09_archived"]})
        self.assertTrue(self.jobs.archive_dirty)

    def test_preserves_worker_diagnostic_rows_under_archive_source(self):
        issues = [{"relative_path": "control/09_archived/bad.md", "code": "invalid_schema"}]
        self.jobs.archive_run = {"state": "running"}
        self.jobs.archive_result = WorkerIngestionFailure("Worker failed", {"source": "atom", "issues": issues})
        self.jobs._finish_archive()
        self.jobs._record_ingestion_issues.assert_called_once_with("archive", issues)

    def test_explicit_full_rebuild_supersedes_archive_only_after_admission(self):
        root = Path(self.enterContext(TemporaryDirectory())).resolve()
        binding = {"root": str(root), "control_root": ".", "manifest_path": "manifest.md",
                   "manifest_sha256": "a" * 64, "project_prefix": "AN"}
        result = {"snapshot": {"atoms": [{"status_group": "Archived"}]}}
        for target, inflight in ((None, {}), ("all", None)):
            with self.subTest(target=target):
                jobs = orchestrator.GenerationJobs("test", binding, "socket")
                jobs.deferred_archive = self.deferred
                jobs.archive_run = {"state": "running"}
                jobs.inflight = inflight
                reuse = {"base_generation": "old"}
                with (patch.object(jobs, "_run_worker", return_value=result) as worker,
                      patch.object(orchestrator, "admit_generation", side_effect=[
                          ValueError("Kernel rejected generation"), {"generation": "full", "result_ids": {"old": "new"}},
                      ]) as admit):
                    with self.assertRaisesRegex(ValueError, "Kernel rejected generation"):
                        jobs._attempt_generation(target, reuse)
                    self.assertIs(self.deferred, jobs.deferred_archive)
                    outcome = jobs._attempt_generation(target, reuse)
                self.assertIsNone(jobs.deferred_archive)
                self.assertEqual({"old": "new"}, outcome["result_ids"])
                self.assertEqual(((None, None), {}), (worker.call_args.args[1:], worker.call_args.kwargs))
                self.assertEqual((result, target), admit.call_args.args[-2:])
                jobs.archive_result = ({}, {"snapshot": {}})
                with patch.object(jobs, "_admit_archive") as archive:
                    jobs._finish_archive()
                self.assertEqual("superseded", jobs.archive_run["state"])
                archive.assert_not_called()
