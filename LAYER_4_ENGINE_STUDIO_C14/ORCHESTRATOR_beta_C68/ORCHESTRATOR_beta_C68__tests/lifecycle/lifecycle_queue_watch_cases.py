"""Watcher recovery cases for lifecycle queue tests."""

from hashlib import sha256
from threading import Event, Thread
from unittest.mock import patch

from watchdog.events import FileModifiedEvent

from ..ORCHESTRATOR_beta_C68__tests__shared import lifecycle_job


class LifecycleQueueWatchCases:
    def test_worker_reply_admission_preserves_payload_and_refuses_invalid_shape(
        self,
    ):
        effects = [{"path": "control/a.md", "sha256": "a" * 64}]
        delta = {"paths": ["control/a.md"], "base_generation": "base"}
        payload = {
            "lifecycle": {
                "outcome": "completed",
                "effects": effects,
                "artifact": None,
            },
            "delta": delta,
            "projection_error": None,
        }
        run = self.jobs._run_lifecycle
        job = lifecycle_job(self.jobs, "atom_lifecycle_archive", {})
        with patch.object(
            self.jobs, "_run_cold_lifecycle", return_value=payload
        ) as worker:
            admitted = run(job, "base", "hash", {})
            self.assertEqual(
                admitted.lifecycle.model_dump(exclude_unset=True),
                payload["lifecycle"],
            )
            self.assertEqual(admitted.delta, delta)
            self.assertIsNone(admitted.projection_error)
            failure = "Kernel refused delta"
            worker.return_value = {
                "lifecycle": {"outcome": "failed", "effects": []},
                "delta": None,
                "projection_error": failure,
            }
            admitted = run(job, "base", "hash", {})
            self.assertIsNone(admitted.delta)
            self.assertEqual(admitted.projection_error, failure)
            self.assertEqual(
                {"outcome": "failed", "effects": []},
                admitted.lifecycle.model_dump(exclude_unset=True),
            )
            self._assert_invalid_worker_replies(payload, worker, run, job)

    def _assert_invalid_worker_replies(self, payload, worker, run, job):
        for bad in (
            None,
            {},
            payload | {"extra": True},
            payload | {"lifecycle": {}},
            payload | {"lifecycle": {"outcome": 1}},
            payload | {"delta": []},
            payload | {"projection_error": {}},
            payload | {"lifecycle": {"outcome": "ok", "effects": None}},
        ):
            worker.return_value = bad
            with (
                self.subTest(bad=bad),
                self.assertRaisesRegex(
                    ValueError,
                    "^Lifecycle worker returned an invalid outcome$",
                ),
            ):
                run(job, "base", "hash", {})

    def test_dirty_poll_wakes_lifecycle_after_reconciliation(self):
        self.fake_foreground()
        self.poll(False)
        watching, waiting = Event(), Event()
        reconciled, replies = [], []
        epoch = self.jobs.watcher.capture_epoch

        def generate(target=None, *, changes=(), startup=False):
            if not startup:
                reconciled.extend(change["event_type"] for change in changes)
                self.jobs.generation_reuse.base_generation = "reconciled"
                self.kernel.generation = "reconciled"
            return {"state": "succeeded"}

        def observe_coverage(**options):
            proof = epoch(**options)
            if proof is None and self.jobs.lifecycle_job is not None:
                waiting.set()
            return proof

        self.enterContext(
            patch.object(self.jobs, "_generate", side_effect=generate)
        )
        self.enterContext(
            patch.object(self.jobs, "_run_archive", side_effect=watching.set)
        )
        self.enterContext(
            patch.object(
                self.jobs.watcher,
                "capture_epoch",
                side_effect=observe_coverage,
            )
        )
        self.jobs.thread = Thread(target=self.jobs._watch_queue, daemon=True)
        self.jobs.thread.start()
        self.assertTrue(watching.wait(3))
        request = Thread(
            target=lambda: replies.append(self.jobs.lifecycle(self.request)),
            daemon=True,
        )
        request.start()
        self.assertTrue(waiting.wait(3))
        self.worker.assert_not_called()
        self.poll(True)
        request.join(3)
        self._assert_reconciled_reply(request, reconciled, replies)

    def _assert_reconciled_reply(self, request, reconciled, replies):
        self.assertFalse(request.is_alive())
        self.assertEqual(["coverage_recovered"], reconciled)
        self.assertEqual(200, replies[0][0])
        self.assertEqual(
            "reconciled", self.worker.call_args.args[0]["base_generation"]
        )
        self.worker.assert_called_once()

    def test_clean_epoch_does_not_bypass_a_queued_recovery(self):
        self.fake_foreground()
        self.poll(False)
        self.poll(True)
        job = self.queued_job()
        self.jobs._run_queued_lifecycle(job)
        self.assertIs(job, self.jobs.lifecycle_job)
        self.assertFalse(job.event.is_set())
        self.assertEqual(
            ["coverage_recovered"],
            [c["event_type"] for c in self.jobs.watcher.changes(0)],
        )
        self.worker.assert_not_called()

    def test_filtered_write_receipt_does_not_lose_lifecycle_wake(self):
        self.fake_foreground()
        watching, injected = Event(), Event()
        carrier = self._acknowledge_owned_carrier()
        coverage = self.jobs._require_lifecycle_coverage

        def inject_receipt(**options):
            if not injected.is_set():
                self.jobs.watcher.dispatch(FileModifiedEvent(str(carrier)))
                injected.set()
            coverage(**options)

        generate = self.enterContext(
            patch.object(
                self.jobs, "_generate", return_value={"state": "succeeded"}
            )
        )
        self.enterContext(
            patch.object(self.jobs, "_run_archive", side_effect=watching.set)
        )
        self.enterContext(
            patch.object(
                self.jobs,
                "_require_lifecycle_coverage",
                side_effect=inject_receipt,
            )
        )
        self.jobs.thread = Thread(target=self.jobs._watch_queue, daemon=True)
        self.jobs.thread.start()
        self.assertTrue(watching.wait(3))
        replies = []
        request = Thread(
            target=lambda: replies.append(self.jobs.lifecycle(self.request)),
            daemon=True,
        )
        request.start()
        request.join(3)
        self._assert_filtered_reply(request, replies, injected, generate)

    def _acknowledge_owned_carrier(self):
        carrier = self.jobs.watcher.control_root / "owned.md"
        carrier.write_text("Already admitted")
        self.jobs.watcher.acknowledge(
            [
                {
                    "target": "control/owned.md",
                    "operation": "modify",
                    "state": "known",
                    "evidence": sha256(carrier.read_bytes()).hexdigest(),
                }
            ]
        )
        return carrier

    def _assert_filtered_reply(self, request, replies, injected, generate):
        self.assertFalse(request.is_alive())
        status, outcome = replies[0]
        self.assertTrue(injected.is_set())
        self.assertEqual(200, status, outcome)
        generate.assert_called_once_with(startup=True)
        self.worker.assert_called_once()
