"""Keep foreground-only runtimes independent of archived Atom history."""
import json
from contextlib import closing
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import Mock, patch

from .. import ORCHESTRATOR_beta_C68__shared as orchestrator
from .ORCHESTRATOR_beta_C68__tests__shared import Connection, watch_project


class SkipArchivesTests(unittest.TestCase):
    def setUp(self):
        root = Path(self.enterContext(TemporaryDirectory())).resolve()
        self.binding = {"root": str(root), "control_root": "control", "manifest_path": "manifest.md",
                        "manifest_sha256": "a" * 64, "project_prefix": "AN"}
        self.jobs = orchestrator.GenerationJobs("test", self.binding, "socket", skip_archives=True)
        self.jobs.watcher = Mock()
        self.jobs.watcher.capture_epoch.return_value = ("watcher", 1)
        self.jobs.watcher.capture_fence.return_value = True
        self.jobs.watcher.replay_fence.return_value = True
        self.jobs.watcher.watch_code = False

    def test_startup_refresh_manual_and_reconciliation_stay_foreground(self):
        deferred = {"roots": ["control/09_archived"], "snapshot": {"atoms": [{}]}, "endpoints": {}}
        result = {"snapshot": {}, "deferred_archive": deferred}
        self.jobs.thread = object()
        with (patch.object(self.jobs, "_run_worker", side_effect=lambda *a, **k: result.copy()) as worker,
              patch.object(self.jobs, "_admit_live_result", return_value={"generation": "new"}) as admit):
            for startup, target, reconciliation in ((True, None, False), (False, None, False),
                                                      (False, "manual", False), (False, None, True)):
                self.jobs.startup_capture = startup
                self.jobs._attempt_generation(target, {"base_generation": "old"}, ["control/a.md"],
                                              reconciliation=reconciliation)
        for index, call in enumerate(worker.call_args_list):
            if index in (0, 2):
                self.assertEqual((None, None), call.args[1:])
            else:
                self.assertEqual(({"base_generation": "old"}, ["control/a.md"]), call.args[1:])
            self.assertTrue(call.kwargs["foreground"])
        self.assertTrue(all("archive_pending" not in call.args[1] for call in admit.call_args_list))
        self.assertIsNone(self.jobs.deferred_archive)

    def test_archive_events_are_excluded_and_moves_keep_the_live_endpoint(self):
        root = Path(self.binding["root"]) / "control"
        live, archive = str(root / "__TKT" / "AN-T-1--task.md"), str(root / "09_archived" / "AN-T-1--task.md")
        def change(old, new=None, event="modified"):
            return {"old_path": old, "new_path": new, "event_type": event, "is_directory": False}
        changes = [change(archive), change(live, archive, "moved"), change(archive, live, "moved")]
        self.assertEqual([change(live, event="deleted"), change(live, event="created")],
                         self.jobs._partition_archive_changes(changes))

    def test_defensive_archive_delta_forces_foreground_capture(self):
        with (patch.object(self.jobs, "_run_worker", return_value={"snapshot": {}}) as worker,
              patch.object(self.jobs, "_admit_live_result", return_value={"generation": "new"})):
            self.jobs._attempt_generation(None, {"base_generation": "old"}, ["control/09_archived/a.md"])
        self.assertIsNone(worker.call_args.args[2])
        self.assertTrue(worker.call_args.kwargs["foreground"])

    def test_off_path_archived_delta_reconciles_before_admission(self):
        reuse = {"base_generation": "old"}
        delta = {"paths": [["control/__TKT", "AN-T-1--task.md"]],
                 "snapshot": {"atoms": [{"status_group": "Archived"}]}}
        foreground = {"snapshot": {"atoms": []}, "deferred_archive": {
            "roots": [], "snapshot": {"atoms": [{"status_group": "Archived"}]}, "endpoints": {}}}
        self.jobs.generation_reuse = reuse
        with (patch.object(orchestrator, "ticket_delta_paths", return_value=["control/__TKT/AN-T-1--task.md"]),
              patch.object(self.jobs, "_run_worker", side_effect=[delta, foreground]) as worker,
              patch.object(self.jobs, "_admit_live_result", return_value={"generation": "new"}) as admit):
            outcome = self.jobs._generate(changes=[{"event_type": "modified"}])
        self.assertEqual("succeeded", outcome["state"])
        self.assertEqual(2, worker.call_count)
        self.assertIsNone(worker.call_args.args[2])
        self.assertTrue(worker.call_args.kwargs["foreground"])
        admit.assert_called_once()
        self.assertEqual({"atoms": []}, admit.call_args.args[1]["snapshot"])

    def test_archive_worker_and_watcher_never_start_and_status_is_disabled(self):
        self.jobs._run_archive()
        self.jobs.watcher.watch_archives.assert_not_called()
        self.jobs.watcher.start_ticket_watch.assert_not_called()
        self.assertIsNone(self.jobs.archive_thread)
        self.assertEqual({"state": "disabled"}, self.jobs.status()["archive"])

    def test_lifecycle_refuses_before_dispatch_including_cold_path(self):
        request = self.binding | {"instance_id": "test", "name": "atom_lifecycle_update", "arguments": {}}
        status, body = self.jobs.lifecycle(request)
        self.assertEqual((409, "archive_disabled"), (status, body["error"]["code"]))
        with patch("subprocess.Popen") as process, self.assertRaisesRegex(RuntimeError, "archive_disabled"):
            self.jobs._run_cold_lifecycle({})
        process.assert_not_called()

    def test_cli_serves_foreground_only_project(self):
        root = Path(self.enterContext(TemporaryDirectory(prefix="ane-skip-", dir="/tmp"))).resolve()
        control, manifest, socket, kernel, _ = self.enterContext(watch_project(root, skip_archives=True))
        binding = {"instance_id": "test", "root": str(root), "control_root": control.name,
                   "manifest_path": manifest.name, "manifest_sha256": sha256(manifest.read_bytes()).hexdigest(),
                   "project_prefix": "AN"}
        with closing(Connection(socket)) as connection:
            connection.request("GET", "/jobs/worker-runs?instance_id=test")
            status = connection.getresponse()
            self.assertEqual(200, status.status)
            self.assertEqual({"state": "disabled"}, json.load(status)["result"]["archive"])
            request = binding | {"name": "atom_lifecycle_update", "arguments": {}}
            connection.request("POST", "/jobs/lifecycle", json.dumps(request))
            refusal = connection.getresponse()
            self.assertEqual(409, refusal.status)
            self.assertEqual("archive_disabled", json.load(refusal)["error"]["code"])
        self.assertEqual(["/generation"], kernel.paths)
