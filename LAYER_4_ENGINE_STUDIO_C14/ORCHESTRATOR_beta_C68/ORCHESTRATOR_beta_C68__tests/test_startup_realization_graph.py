"""Verify that startup graph work follows foreground replay."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Event
import unittest
from unittest.mock import Mock, patch

from .. import ORCHESTRATOR_beta_C68__shared as orchestrator
from .. import startup_graph
from ..startup_checkpoint import ReuseRecord


class StartupRealizationGraphTests(unittest.TestCase):
    def setUp(self):
        root = Path(self.enterContext(TemporaryDirectory())).resolve()
        binding = {"root": str(root), "control_root": "control", "manifest_path": "manifest.md",
                   "manifest_sha256": "a" * 64, "project_prefix": "AN"}
        self.jobs = orchestrator.GenerationJobs("test", binding, "socket")
        self.jobs.watcher = Mock()
        self.jobs.watcher.foreground_events.return_value = 0
        self.jobs.watcher.replay_fence.return_value = True
        self.jobs.live_generation = "core"
        self.jobs.generation_reuse = ReuseRecord(base_generation="core", inputs={"graph": "pending"},
                                                endpoints={}, graph_config={})
        self.graph = {"base_generation": "core", "graph": {}, "graph_sha256": "b" * 64,
                      "reuse": {"inputs": {"graph": "c" * 64}, "graph_config": {}, "endpoints": {}}}

    def test_background_graph_does_not_hold_startup_replay_open(self):
        jobs = self.jobs
        jobs.graph_queued = jobs.startup_replay = True
        started, release = Event(), Event()

        def capture(directory, request, **options):
            started.set()
            if not release.wait(5):
                raise RuntimeError("Test Worker did not finish")
            return json.dumps(self.graph)

        with (patch.object(jobs, "_communicate_worker", side_effect=capture) as worker,
              patch.object(startup_graph, "worker_request", return_value={"structure": {}}),
              patch.object(startup_graph, "admit_generation", return_value={"generation": "core"}) as admit):
            jobs._run_startup_graph()
            worker.assert_not_called()
            jobs.startup_replay = False
            jobs._run_startup_graph()
            self.assertTrue(started.wait(3))
            self.assertFalse(jobs.health()["startup_replay_pending"])
            admit.assert_not_called()
            release.set()
            jobs.graph_thread.join(5)
            jobs._run_startup_graph()
        self.assertEqual(({"structure": {}, "graph_only": True, "watcher_guarded": True}, {"graph": True}),
                         (worker.call_args.args[1], worker.call_args.kwargs))
        self.assertEqual(self.graph, admit.call_args.args[3])
        self.assertEqual({"graph": "c" * 64}, jobs.generation_reuse.inputs)

    def test_graph_from_an_obsolete_generation_is_not_admitted(self):
        self.jobs.graph_result = ("earlier", 0, self.graph)
        with patch.object(startup_graph, "admit_generation") as admit:
            self.jobs._finish_startup_graph()
        admit.assert_not_called()
        self.assertTrue(self.jobs.graph_queued)
