from unittest.mock import Mock, patch

from .... import ORCHESTRATOR_beta_C68__shared as orchestrator
from ...ORCHESTRATOR_beta_C68__tests__shared import RunFixture


class StartupArchiveCheckpointCases:
    def _test_timed_recovery(self):
        self.jobs.startup_capture = False
        self.jobs.thread = object()
        self.jobs.watcher.replay_fence.return_value = True
        self.jobs.latest = Mock(code="watcher_coverage_lost")
        self.jobs.archive_run = RunFixture(state="succeeded")
        checkpoint = Mock()
        checkpoint.model_dump.return_value = self.reuse
        unchanged = {"base_generation": "old", "unchanged": True}
        with (
            patch(
                "ORCHESTRATOR_beta_C68.generation.worker.generation_worker.read_reuse",
                return_value=checkpoint,
            ) as read,
            patch.object(
                self.jobs, "_run_worker", return_value=unchanged
            ) as worker,
            patch.object(
                orchestrator,
                "confirm_reuse",
                return_value={"generation": "old", "kind": "reused"},
            ) as admit,
        ):
            self.jobs._run_queued_generation(
                orchestrator.CurrentnessRetry(), None, [], True
            )
        read.assert_called_once_with("socket", "test")
        self.assertEqual(self.reuse, worker.call_args.args[1])
        self.check_recovery(worker, admit, unchanged)

    def check_recovery(self, worker, admit, unchanged):
        self.assertEqual(
            {
                "foreground": True,
                "watcher_guarded": True,
                "defer_graph": True,
                "incremental": True,
                "force_model": False,
            },
            worker.call_args.kwargs,
        )
        self.assertEqual(
            unchanged | {"archive_pending": True}, admit.call_args.args[-1]
        )
        self.assertEqual(
            {"control/09_archived/a.md": "c" * 64},
            self.jobs.deferred_archive["checkpoint"]["carrier_hashes"],
        )
        self.assertTrue(self.jobs.archive_dirty)
        self.assertTrue(self.jobs.graph_queued)


test_name = (
    "test_timed_recovery_loads_persisted_checkpoint_"
    "and_preserves_archive_scope"
)
setattr(
    StartupArchiveCheckpointCases,
    test_name,
    StartupArchiveCheckpointCases._test_timed_recovery,
)
