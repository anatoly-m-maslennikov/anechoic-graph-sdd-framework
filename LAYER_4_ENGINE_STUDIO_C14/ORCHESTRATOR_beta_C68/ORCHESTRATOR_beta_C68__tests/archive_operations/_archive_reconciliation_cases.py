"""Archive reconciliation scenario tests."""

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from ... import ORCHESTRATOR_beta_C68__shared as orchestrator
from ORCHESTRATOR_beta_C68.archive_operations import archive_jobs
from ORCHESTRATOR_beta_C68.generation.generation__shared import DeltaRequiresReconciliation
from ..ORCHESTRATOR_beta_C68__tests__shared import RunFixture


class ArchiveReconciliationCases:
    def test_combines_archive_issues_and_reconciles_collision_with_live_scope(
        self,
    ):
        deferred = {"relative_path": "off-path.md", "code": "invalid_schema"}
        archived = {
            "relative_path": "09_archived/bad.md",
            "code": "invalid_schema",
        }
        self.deferred["snapshot"] = {
            "atoms": [],
            "relations": [],
            "ingestion_issues": [deferred],
        }
        result = {
            "snapshot": {
                "atoms": [],
                "relations": [],
                "ingestion_issues": [archived],
            },
            "carrier_hashes": {},
        }
        self.assertEqual(
            [archived, deferred],
            self.jobs._archive_snapshot_payload(result)["snapshot"][
                "ingestion_issues"
            ],
        )
        self.jobs.archive_run = RunFixture(state="running", started_at=0)
        self.jobs.archive_result = ({}, result)
        with patch.object(
            self.jobs,
            "_admit_archive",
            side_effect=DeltaRequiresReconciliation,
        ):
            self.jobs._finish_archive()
        self.assertEqual("superseded", self.jobs.archive_run.state)
        self.assertEqual(
            "archive_reconciliation",
            self.jobs.watcher.queue.put.call_args.args[0]["event_type"],
        )
        self.assertTrue(self.jobs.archive_reconciliation_pending)
        self.jobs._record_ingestion_issues.assert_not_called()

    def test_incremental_reconciliation_tries_full_archive_once(self):
        self.deferred.update(
            {"checkpoint": {}, "snapshot": {"atoms": [], "relations": []}}
        )
        self.jobs.archive_run = RunFixture(state="running", started_at=0)
        self.jobs.archive_result = ({}, {"unchanged": True})
        with patch.object(
            self.jobs,
            "_admit_archive",
            side_effect=DeltaRequiresReconciliation,
        ):
            self.jobs._finish_archive()
        self.assertEqual("superseded", self.jobs.archive_run.state)
        self.assertTrue(self.jobs.archive_dirty)
        self.assertNotIn("checkpoint", self.jobs.deferred_archive)
        self.jobs.watcher.queue.put.assert_not_called()

        self._assert_full_archive_reconciliation()

    def _assert_full_archive_reconciliation(self):
        replacement = {
            "snapshot": {"atoms": [], "relations": []},
            "carrier_hashes": {},
        }
        self.jobs.watcher.watch_archives.return_value = True
        with patch.object(
            self.jobs, "_archive_snapshot", return_value=({}, replacement)
        ) as capture:
            self.jobs._capture_archive(self.jobs.deferred_archive)
        capture.assert_called_once_with({}, None, self.jobs.deferred_archive)
        self.assertTrue(self.jobs.archive_result[1]["replace"])
        self.jobs.archive_dirty = False
        self.jobs.archive_run = RunFixture(state="running", started_at=0)
        pending, captured = (
            self.jobs.deferred_archive,
            self.jobs.archive_result,
        )
        with patch.object(
            archive_jobs,
            "admit_generation",
            return_value={"generation": "new"},
        ) as admit:
            self.jobs._finish_archive()
        self.assertEqual("succeeded", self.jobs.archive_run.state)
        self.assertIsNone(self.jobs.deferred_archive)
        self.assertTrue(admit.call_args.args[3]["replace"])
        self.jobs.deferred_archive, self.jobs.archive_result = (
            pending,
            captured,
        )
        self.jobs.archive_run = RunFixture(state="running", started_at=0)
        with patch.object(
            self.jobs,
            "_admit_archive",
            side_effect=DeltaRequiresReconciliation,
        ):
            self.jobs._finish_archive()
        self.assertEqual("superseded", self.jobs.archive_run.state)
        self.assertFalse(self.jobs.archive_dirty)
        self.assertEqual(
            "archive_reconciliation",
            self.jobs.watcher.queue.put.call_args.args[0]["event_type"],
        )

    def test_explicit_full_rebuild_supersedes_archive_only_after_admission(
        self,
    ):
        root = Path(self.enterContext(TemporaryDirectory())).resolve()
        binding = {
            "root": str(root),
            "control_root": ".",
            "manifest_path": "manifest.md",
            "manifest_sha256": "a" * 64,
            "project_prefix": "AN",
        }
        result = {"snapshot": {"atoms": [{"status_group": "Archived"}]}}
        for target, inflight in ((None, object()), ("all", None)):
            with self.subTest(target=target):
                self._assert_full_rebuild(binding, result, target, inflight)

    def _assert_full_rebuild(self, binding, result, target, inflight):
        jobs = orchestrator.GenerationJobs("test", binding, "socket")
        jobs.deferred_archive = self.deferred
        jobs.archive_run = RunFixture(state="running", started_at=0)
        jobs.inflight = inflight
        reuse = {"base_generation": "old"}
        with (
            patch.object(jobs, "_run_worker", return_value=result) as worker,
            patch(
                "ORCHESTRATOR_beta_C68.generation.generation.admit_generation",
                side_effect=[
                    ValueError("Kernel rejected generation"),
                    {
                        "generation": "full",
                        "result_ids": {"old": "new"},
                    },
                ],
            ) as admit,
        ):
            with self.assertRaisesRegex(
                ValueError, "Kernel rejected generation"
            ):
                jobs._attempt_generation(target, reuse)
            self.assertIs(self.deferred, jobs.deferred_archive)
            outcome = jobs._attempt_generation(target, reuse)
        self.assertIsNone(jobs.deferred_archive)
        self.assertEqual({"old": "new"}, outcome["result_ids"])
        self.assertEqual(
            ((None, None), {"force_model": target == "all"}),
            (worker.call_args.args[1:], worker.call_args.kwargs),
        )
        self.assertEqual((result, target), admit.call_args.args[-2:])
        jobs.archive_result = ({}, {"snapshot": {}})
        with patch.object(jobs, "_admit_archive") as archive:
            jobs._finish_archive()
        self.assertEqual("superseded", jobs.archive_run.state)
        archive.assert_not_called()
