"""Exercise the default startup checkpoint and deferred Archive protocol."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import Mock, patch

from .. import ORCHESTRATOR_beta_C68__shared as orchestrator
from .. import archive_jobs


class StartupArchiveCheckpointTests(unittest.TestCase):
    def setUp(self):
        root = Path(self.enterContext(TemporaryDirectory())).resolve()
        binding = {"root": str(root), "control_root": "control", "manifest_path": "manifest.md",
                   "manifest_sha256": "a" * 64, "project_prefix": "AN"}
        self.jobs = orchestrator.GenerationJobs("test", binding, "socket")
        self.jobs.startup_capture = True
        self.jobs.watcher = Mock()
        self.jobs.watcher.archive_roots.return_value = ()
        self.jobs.watcher.capture_fence.return_value = True
        self.jobs._record_ingestion_issues = Mock()
        self.reuse = {"base_generation": "old", "inputs": {"carrier_schema": "a" * 64},
                      "graph_config": None, "endpoints": {}, "carrier_hashes": {"control/a.md": "b" * 64,
                          "control/09_archived/a.md": "c" * 64},
                      "folder_hashes": {"control": "d" * 64, "control/09_archived": "e" * 64}}

    def test_unchanged_live_reconciles_previously_known_archive_after_all_roots_removed(self):
        unchanged = {"base_generation": "old", "unchanged": True}
        with (patch.object(self.jobs, "_run_worker", return_value=unchanged) as worker,
              patch.object(orchestrator, "confirm_reuse", return_value={"generation": "old", "kind": "reused"}) as admit):
            outcome = self.jobs._attempt_generation(None, self.reuse)
        self.assertEqual("reused", outcome["kind"])
        self.assertEqual({"incremental": True, "foreground": True, "watcher_guarded": True}, worker.call_args.kwargs)
        self.assertTrue(admit.call_args.args[-1]["archive_pending"])
        deferred = self.jobs.deferred_archive
        self.assertEqual([], deferred["roots"])
        self.assertEqual({"control/09_archived/a.md": "c" * 64}, deferred["checkpoint"]["carrier_hashes"])
        self.assertEqual({"control/09_archived": "e" * 64}, deferred["checkpoint"]["folder_hashes"])
        self.assertNotIn("folder_hashes", self.jobs.generation_reuse)

    def test_legacy_or_uncovered_checkpoint_builds_fresh_foreground(self):
        result = {"snapshot": {}, "deferred_archive": {"roots": [], "snapshot": {"atoms": []}, "endpoints": {}}}
        legacy = {key: value for key, value in self.reuse.items() if key != "folder_hashes"}
        for reuse, epoch in ((legacy, ("watcher", 1)), (self.reuse, None)):
            self.jobs.startup_capture = True
            self.jobs.watcher.capture_epoch.return_value = epoch
            with (patch.object(self.jobs, "_run_worker", return_value=result.copy()) as worker,
                  patch.object(orchestrator, "admit_generation", return_value={"generation": "new", "kind": "full"})):
                self.assertEqual("full", self.jobs._attempt_generation(None, reuse)["kind"])
            self.assertIsNone(worker.call_args.args[1])
            self.assertEqual({"foreground": True, "watcher_guarded": epoch is not None}, worker.call_args.kwargs)

    def test_failed_foreground_fence_keeps_legacy_error_and_passes_run_id(self):
        self.jobs.active = {"run_id": "a" * 32}
        for fence in (False, None):
            with self.subTest(fence=fence), patch.object(self.jobs, "_run_worker", return_value={}):
                self.jobs.watcher.capture_fence.return_value = fence
                with self.assertRaisesRegex(ValueError, "Native Project carriers changed during generation"):
                    self.jobs._attempt_generation(None, None)
                self.assertEqual("a" * 32, self.jobs.watcher.capture_fence.call_args.kwargs["run_id"])
        self.jobs.watcher.capture_epoch.assert_called_with(trace=True)

    def test_archive_delta_admits_against_latest_live_generation(self):
        self.jobs.deferred_archive = self.jobs._restart_archive(self.reuse, {"unchanged": True})
        archive = self.jobs.deferred_archive["checkpoint"]
        old = {"base_generation": "old", "paths": [["control/09_archived", "a.md"]],
               "snapshot": {}, "carrier_hashes": {}, "snapshot_sha256": "0" * 64}
        self.jobs._communicate_worker = Mock(return_value=json.dumps(old))
        _, result = self.jobs._archive_snapshot({}, archive)
        self.assertEqual(old, result)
        request = self.jobs._communicate_worker.call_args.args[1]
        self.assertTrue(request["incremental"])
        self.assertEqual(archive, request["reuse"])
        self.jobs.live_generation = "latest"
        with patch.object(archive_jobs, "admit_generation", return_value={"generation": "complete"}) as admit:
            self.jobs._admit_archive(result)
        self.assertEqual("latest", admit.call_args.args[3]["base_generation"])
        self.assertTrue(admit.call_args.kwargs["archive"])
        self.assertIsNone(self.jobs.deferred_archive)

    def test_archive_incompatibility_recaptures_only_archive(self):
        captured = {"snapshot": {"atoms": [], "relations": []}, "carrier_hashes": {}}
        self.jobs._communicate_worker = Mock(side_effect=['{"incompatible":true}', json.dumps(captured)])
        request = {"reuse": self.reuse, "archive": {"roots": (), "endpoints": {}}}
        result = self.jobs._run_archive_worker("/test", request)
        self.assertEqual(captured | {"replace": True}, result)
        first, second = [call.args[1] for call in self.jobs._communicate_worker.call_args_list]
        self.assertEqual(request | {"incremental": True}, first)
        self.assertEqual(request | {"reuse": None}, second)
