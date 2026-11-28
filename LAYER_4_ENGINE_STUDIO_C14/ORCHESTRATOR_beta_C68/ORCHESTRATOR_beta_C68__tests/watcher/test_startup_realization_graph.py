"""Verify that startup graph work follows foreground replay."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Event
import unittest
from unittest.mock import Mock, patch

from ... import ORCHESTRATOR_beta_C68__shared as orchestrator

STARTUP_GRAPH = f"{orchestrator.__package__}.startup_graph"


class StartupRealizationGraphTests(unittest.TestCase):
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
        self.jobs.watcher = Mock()
        self.jobs.watcher.foreground_events.return_value = 0
        self.jobs.watcher.replay_fence.return_value = True
        self.jobs.live_generation = "core"
        self.jobs.generation_reuse = orchestrator.ReuseRecord(
            base_generation="core",
            inputs={"graph": "pending"},
            endpoints={},
            graph_config={},
        )
        self.graph = {
            "base_generation": "core",
            "graph": {},
            "graph_sha256": "b" * 64,
            "reuse": {
                "inputs": {"graph": "c" * 64},
                "graph_config": {},
                "endpoints": {},
            },
        }

    def test_explicit_graph_uses_only_graph_admission(self):
        jobs = self.jobs
        reuse = jobs.generation_reuse.model_dump(exclude_unset=True)
        jobs.watcher.capture_epoch.return_value = 1
        jobs.watcher.capture_fence.return_value = True
        module = STARTUP_GRAPH
        with (
            patch(f"{module}.worker_request", return_value={"structure": {}}),
            patch.object(
                jobs,
                "_communicate_worker",
                return_value=json.dumps(self.graph),
            ) as worker,
            patch(
                f"{module}.admit_generation",
                return_value={"generation": "next"},
            ) as admit,
            patch.object(
                jobs,
                "_capture_generation",
                side_effect=AssertionError("core capture"),
            ),
        ):
            result = jobs._attempt_generation("realization_graph", reuse)
        self.assertEqual(
            {"state": "succeeded", "generation": "next", "result_ids": {}},
            result,
        )
        self.assertEqual(
            {
                "structure": {},
                "graph_only": True,
                "force_graph": True,
                "watcher_guarded": True,
            },
            worker.call_args.args[1],
        )
        self.assertEqual((None, self.graph, None), admit.call_args.args[2:])
        self.assertEqual({"force_graph": True}, admit.call_args.kwargs)
        self.assertEqual("next", jobs.generation_reuse.base_generation)

    def test_background_graph_does_not_hold_startup_replay_open(self):
        jobs = self.jobs
        jobs.graph_queued = jobs.startup_replay = True
        started, release = Event(), Event()

        def capture(directory, request, **options):
            started.set()
            if not release.wait(5):
                raise RuntimeError("Test Worker did not finish")
            return json.dumps(self.graph)

        with (
            patch.object(
                jobs, "_communicate_worker", side_effect=capture
            ) as worker,
            patch(
                f"{STARTUP_GRAPH}.worker_request",
                return_value={"structure": {}},
            ),
            patch(
                f"{STARTUP_GRAPH}.admit_generation",
                return_value={"generation": "core"},
            ) as admit,
        ):
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
        self.assertEqual(
            (
                {"structure": {}, "graph_only": True, "watcher_guarded": True},
                {"graph": True},
            ),
            (worker.call_args.args[1], worker.call_args.kwargs),
        )
        self.assertEqual(self.graph, admit.call_args.args[3])
        self.assertEqual({"graph": "c" * 64}, jobs.generation_reuse.inputs)

    def test_graph_waits_for_archive_and_queued_reconciliation(self):
        jobs = self.jobs
        jobs.graph_queued = True
        jobs.deferred_archive = {}
        with patch(f"{STARTUP_GRAPH}.threading.Thread") as thread:
            jobs._run_startup_graph()
            thread.assert_not_called()
            jobs.archive_run = Mock(state="running")
            jobs.archive_thread = Mock()
            jobs._run_startup_graph()
            thread.assert_not_called()
            jobs.deferred_archive = None
            jobs._run_startup_graph()
            thread.assert_not_called()
            jobs.deferred_archive = {}
            jobs.archive_thread = None
            jobs.archive_run.state = "superseded"
            jobs.archive_dirty = True
            jobs._run_startup_graph()
            thread.assert_not_called()
            jobs.archive_dirty = False
            jobs.archive_reconciliation_pending = True
            jobs._run_startup_graph()
            thread.assert_not_called()
            jobs.archive_reconciliation_pending = False
            jobs.archive_run.state = "failed"
            jobs._run_startup_graph()
            thread.return_value.start.assert_called_once()

    def test_graph_starts_when_archive_is_absent_or_finished(self):
        for deferred, state in (
            (None, None),
            (None, "succeeded"),
            ({}, "failed"),
        ):
            with self.subTest(state=state):
                jobs = self.jobs
                jobs.graph_queued = True
                jobs.graph_thread = None
                jobs.deferred_archive = deferred
                jobs.archive_run = Mock(state=state) if state else None
                with patch(f"{STARTUP_GRAPH}.threading.Thread") as thread:
                    jobs._run_startup_graph()
                    thread.return_value.start.assert_called_once()

    def test_finished_graph_is_processed_while_archive_is_running(self):
        jobs = self.jobs
        jobs.graph_thread = Mock()
        jobs.graph_thread.is_alive.return_value = False
        jobs.archive_thread = Mock()
        jobs.deferred_archive = {}
        with patch.object(jobs, "_finish_startup_graph") as finish:
            jobs._run_startup_graph()
        finish.assert_called_once()
        self.assertIsNone(jobs.graph_thread)

    def test_graph_requeues_concurrent_source_changes(self):
        jobs = self.jobs
        jobs.archive_reconciliation_pending = True
        event = {"event_type": orchestrator.ARCHIVE_RECONCILIATION}
        with patch.object(
            jobs, "_generate", return_value={"state": "succeeded"}
        ):
            jobs._run_queued_generation(
                orchestrator.CurrentnessRetry(),
                Mock(target="realization_graph"),
                [event],
                False,
            )
        self.assertTrue(jobs.archive_reconciliation_pending)
        jobs.watcher.queue.put.assert_called_once_with(event)

    def test_explicit_build_consumes_reconciliation_without_sticking_graph(
        self,
    ):
        jobs = self.jobs
        jobs.archive_reconciliation_pending = True
        job = Mock(target="all")
        event = {"event_type": orchestrator.ARCHIVE_RECONCILIATION}
        with patch.object(
            jobs, "_generate", return_value={"state": "succeeded"}
        ) as generate:
            jobs._run_queued_generation(
                orchestrator.CurrentnessRetry(), job, [event], False
            )
        self.assertFalse(jobs.archive_reconciliation_pending)
        generate.assert_called_once_with("all", changes=())
        jobs.graph_queued = True
        with patch(f"{STARTUP_GRAPH}.threading.Thread") as thread:
            jobs._run_startup_graph()
            thread.return_value.start.assert_called_once()

    def test_explicit_build_preserves_reconciliation_not_in_batch(self):
        self.jobs.archive_reconciliation_pending = True
        with patch.object(
            self.jobs, "_generate", return_value={"state": "failed"}
        ):
            self.jobs._run_queued_generation(
                orchestrator.CurrentnessRetry(), Mock(target="all"), [], False
            )
        self.assertTrue(self.jobs.archive_reconciliation_pending)

    def test_reconciliation_marker_clears_when_event_is_handled(self):
        jobs = self.jobs
        jobs.archive_reconciliation_pending = True
        event = {"event_type": orchestrator.ARCHIVE_RECONCILIATION}
        with patch.object(
            jobs, "_attempt_generation", return_value={}
        ) as attempt:
            jobs._attempt_with_recovery(None, None, [event])
        self.assertFalse(jobs.archive_reconciliation_pending)
        self.assertEqual(
            {"reconciliation": True, "strict": True}, attempt.call_args.kwargs
        )

    def test_graph_from_an_obsolete_generation_is_not_admitted(self):
        self.jobs.graph_result = ("earlier", 0, self.graph)
        with patch(f"{STARTUP_GRAPH}.admit_generation") as admit:
            self.jobs._finish_startup_graph()
        admit.assert_not_called()
        self.assertTrue(self.jobs.graph_queued)
