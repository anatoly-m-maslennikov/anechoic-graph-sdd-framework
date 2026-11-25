"""Exercise lifecycle dispatch around watcher recovery and request expiry."""

from pathlib import Path
from hashlib import sha256
import json
from tempfile import TemporaryDirectory
from threading import Event, Thread
from time import monotonic, monotonic_ns
import unittest
from unittest.mock import Mock, patch

from pydantic import ValidationError
from watchdog.events import FileModifiedEvent

from ..ORCHESTRATOR_beta_C68__shared import PollComplete
from .ORCHESTRATOR_beta_C68__tests__shared import Kernel, kernel_server, lifecycle_job, project_jobs, restore_reuse


class LifecycleKernel(Kernel):
    def do_GET(self):
        if self.path == "/structure?instance_id=test":
            self.reply(200, self.server.structure, [("x-anechoic-generation", self.server.generation)])
        else:
            self.reply(404, {})

    def do_POST(self):
        request = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        if self.path != "/database" or request["instance_id"] != "test":
            self.reply(404, {})
            return
        row = [self.server.generation, *self.server.query_values]
        self.reply(200, {"result": {"rows": [row]}})


class LifecycleQueueTests(unittest.TestCase):
    def setUp(self):
        root = Path(self.enterContext(TemporaryDirectory())).resolve()
        (root / "control").mkdir()
        self.kernel = self.enterContext(kernel_server(root, LifecycleKernel))
        self.jobs = project_jobs(root, database_socket=str(root / "kernel.sock"))
        self.request = self.jobs.binding | {"instance_id": "test", "name": "atom_lifecycle_create_draft",
            "arguments": {"newAtom": {"template": "task", "container": {"component": "C00"}}}}
        restore_reuse(self.jobs, "original")
        self.structure = {"project": {"ref": "AN-S-1@1"}, "components": {}}
        self.kernel.structure = self.structure
        self.kernel.generation = "original"
        self.kernel.query_values = ["1", "[]"]
        self.worker = self.enterContext(patch.object(self.jobs, "_run_cold_lifecycle", return_value={
            "lifecycle": {"outcome": "completed"}, "delta": None, "projection_error": None}))
        self.addCleanup(self.jobs.close)

    def test_worker_reply_admission_preserves_payload_and_refuses_invalid_shape(self):
        effects = [{"path": "control/a.md", "sha256": "a" * 64}]
        delta = {"paths": ["control/a.md"], "base_generation": "base"}
        payload = {"lifecycle": {"outcome": "completed", "effects": effects, "artifact": None},
                   "delta": delta, "projection_error": None}
        run = self.jobs._run_lifecycle
        job = lifecycle_job(self.jobs, "atom_lifecycle_archive", {})
        with patch.object(self.jobs, "_run_cold_lifecycle", return_value=payload) as worker:
            admitted = run(job, "base", "hash", {})
            self.assertEqual(admitted.lifecycle.model_dump(exclude_unset=True), payload["lifecycle"])
            self.assertEqual(admitted.delta, delta)
            self.assertIsNone(admitted.projection_error)
            failure = "Kernel refused delta"
            worker.return_value = {"lifecycle": {"outcome": "failed", "effects": []},
                                   "delta": None, "projection_error": failure}
            admitted = run(job, "base", "hash", {})
            self.assertIsNone(admitted.delta)
            self.assertEqual(admitted.projection_error, failure)
            self.assertEqual({"outcome": "failed", "effects": []}, admitted.lifecycle.model_dump(exclude_unset=True))
            for bad in (None, {}, payload | {"extra": True}, payload | {"lifecycle": {}},
                        payload | {"lifecycle": {"outcome": 1}}, payload | {"delta": []},
                        payload | {"projection_error": {}}, payload | {"lifecycle": {"outcome": "ok", "effects": None}}):
                worker.return_value = bad
                with self.subTest(bad=bad), self.assertRaisesRegex(
                        ValueError, "^Lifecycle worker returned an invalid outcome$"):
                    run(job, "base", "hash", {})

    def poll(self, clean):
        source = str(self.jobs.watcher.control_root)
        started = monotonic_ns()
        self.jobs.watcher.observer.emitters[0]._snapshot_started = started
        self.jobs.watcher.on_poll_complete(PollComplete(source, started=started, clean=clean))

    def fake_foreground(self):
        emitter = Mock(baseline_clean=True)
        emitter.watch.path = str(self.jobs.watcher.control_root)
        self.jobs.watcher.observer = Mock(emitters=[emitter])
        self.poll(True)

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

        self.enterContext(patch.object(self.jobs, "_generate", side_effect=generate))
        self.enterContext(patch.object(self.jobs, "_run_archive", side_effect=watching.set))
        self.enterContext(patch.object(self.jobs.watcher, "capture_epoch", side_effect=observe_coverage))
        self.jobs.thread = Thread(target=self.jobs._watch_queue, daemon=True)
        self.jobs.thread.start()
        self.assertTrue(watching.wait(3))
        request = Thread(target=lambda: replies.append(self.jobs.lifecycle(self.request)), daemon=True)
        request.start()
        self.assertTrue(waiting.wait(3))
        self.worker.assert_not_called()
        self.poll(True)
        request.join(3)
        self.assertFalse(request.is_alive())
        self.assertEqual(["coverage_recovered"], reconciled)
        self.assertEqual(200, replies[0][0])
        self.assertEqual("reconciled", self.worker.call_args.args[0]["base_generation"])
        self.worker.assert_called_once()

    def test_clean_epoch_does_not_bypass_a_queued_recovery(self):
        self.fake_foreground()
        self.poll(False)
        self.poll(True)
        job = self.queued_job()
        self.jobs._run_queued_lifecycle(job)
        self.assertIs(job, self.jobs.lifecycle_job)
        self.assertFalse(job.event.is_set())
        self.assertEqual(["coverage_recovered"], [c["event_type"] for c in self.jobs.watcher.changes(0)])
        self.worker.assert_not_called()

    def test_filtered_write_receipt_does_not_lose_lifecycle_wake(self):
        self.fake_foreground()
        watching, injected = Event(), Event()
        carrier = self.jobs.watcher.control_root / "owned.md"
        carrier.write_text("Already admitted")
        self.jobs.watcher.acknowledge([{
            "target": "control/owned.md", "operation": "modify", "state": "known",
            "evidence": sha256(carrier.read_bytes()).hexdigest(),
        }])
        coverage = self.jobs._require_lifecycle_coverage

        def inject_receipt(**options):
            if not injected.is_set():
                self.jobs.watcher.dispatch(FileModifiedEvent(str(carrier)))
                injected.set()
            coverage(**options)

        generate = self.enterContext(patch.object(self.jobs, "_generate", return_value={"state": "succeeded"}))
        self.enterContext(patch.object(self.jobs, "_run_archive", side_effect=watching.set))
        self.enterContext(patch.object(self.jobs, "_require_lifecycle_coverage", side_effect=inject_receipt))
        self.jobs.thread = Thread(target=self.jobs._watch_queue, daemon=True)
        self.jobs.thread.start()
        self.assertTrue(watching.wait(3))
        replies = []
        request = Thread(target=lambda: replies.append(self.jobs.lifecycle(self.request)), daemon=True)
        request.start()
        request.join(3)
        self.assertFalse(request.is_alive())
        status, outcome = replies[0]
        self.assertTrue(injected.is_set())
        self.assertEqual(200, status, outcome)
        generate.assert_called_once_with(startup=True)
        self.worker.assert_called_once()

    def test_admitted_context_keeps_coordinated_writes_on_the_project_path(self):
        for name, ref, descendants, carriers, coordinated in (
            ("change_status", "AN-T-1", True, [], True),
            ("change_status", "AN-T-1", False, [], False),
            ("archive", "AN-S-2", True, [self.carrier("LAYER_1_META_ONTOLOGY_C9/_SPEC")], True),
            ("archive", "AN-S-2", True, [self.carrier("_SPEC")], False),
        ):
            with self.subTest(name=name, descendants=descendants, carriers=carriers), \
                    patch.object(self.jobs, "lifecycle_job", None):
                self.kernel.query_values = [
                    json.dumps(self.structure), None, "[]", "1", "2", json.dumps(carriers), descendants, "[]",
                ]
                request = lifecycle_job(self.jobs, f"atom_lifecycle_{name}", {"target": {"ref_id": ref}})
                base, structure, facts = self.jobs._lifecycle_inputs(request)
                self.assertEqual(("original", self.structure), (base, structure))
                if coordinated:
                    self.assertEqual({}, facts)
                else:
                    self.assertEqual(carriers, facts["lifecycle_context"]["carriers"])
                    self.assertEqual(descendants, facts["lifecycle_context"]["has_descendants"])

    @staticmethod
    def carrier(parent):
        return {"id": "AN-S-2", "status": "active",
                "source_path": f"control/{parent}/AN-S-2-SPEC--claim.md"}

    def queued_job(self):
        return lifecycle_job(self.jobs, self.request["name"], self.request["arguments"])

    def test_job_defaults_preserve_identity_and_validate_assignments(self):
        arguments = self.request["arguments"]
        first = self.queued_job()
        self.assertIs(arguments, first.arguments)
        with self.assertRaises(ValidationError):
            first.started = "yes"
        self.jobs.lifecycle_job = None
        second = self.queued_job()
        self.assertIsNot(first.event, second.event)
        outcome = {"lifecycle": {"outcome": "completed"}}
        second.outcome = outcome
        self.assertIs(outcome, second.outcome)

    def test_sampling_and_undispatched_poll_defer_write_once(self):
        self.fake_foreground()
        watcher = self.jobs.watcher
        job = self.queued_job()
        with watcher.managed_write:
            self.jobs._run_queued_lifecycle(job)
        self.assertFalse(job.started)
        emitter = watcher.observer.emitters[0]
        emitter._snapshot_started += 1
        self.jobs._run_queued_lifecycle(job)
        self.assertFalse(job.started)
        self.assertIs(job, self.jobs.lifecycle_job)
        self.worker.assert_not_called()
        self.poll(True)

        worker_reply = self.worker.return_value

        def write(*args):
            self.assertTrue(watcher.managed_write.locked())
            return worker_reply

        self.worker.side_effect = write
        self.jobs._run_queued_lifecycle(job)
        self.assertTrue(job.event.is_set())
        self.assertFalse(watcher.managed_write.locked())
        self.worker.assert_called_once()

    def test_expired_preflight_cannot_dispatch_or_clear_the_next_job(self):
        entered, release = Event(), Event()

        def inputs(_):
            entered.set()
            if not release.wait(3):
                raise RuntimeError("Lifecycle preflight was not released")
            return "original", self.structure, {}

        job = self.queued_job()
        self.enterContext(patch.object(self.jobs, "_lifecycle_inputs", side_effect=inputs))
        dispatch = Thread(target=self.jobs._run_queued_lifecycle, args=(job,), daemon=True)
        self.addCleanup(release.set)
        dispatch.start()
        self.assertTrue(entered.wait(3))
        job.deadline = monotonic()
        status, result = self.jobs._await_lifecycle(job)
        self.assertEqual((504, "lifecycle_deadline_exceeded"), (status, result["error"]["code"]))
        self.assertIn("no lifecycle write was attempted", result["error"]["message"])
        self.assertIsNone(self.jobs.lifecycle_job)
        next_job = self.queued_job()
        release.set()
        dispatch.join(3)
        self.assertFalse(dispatch.is_alive())
        self.assertIs(next_job, self.jobs.lifecycle_job)
        self.worker.assert_not_called()

    def test_deadline_after_dispatch_retains_the_unknown_outcome(self):
        job = self.queued_job()
        job.started, job.deadline = True, monotonic()
        status, result = self.jobs._await_lifecycle(job)
        self.assertEqual((504, "write_outcome_unknown"), (status, result["error"]["code"]))
        self.assertIs(job, self.jobs.lifecycle_job)
