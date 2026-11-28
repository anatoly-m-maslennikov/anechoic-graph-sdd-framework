"""Exercise lifecycle dispatch around watcher recovery and request expiry."""

from pathlib import Path
import json
from tempfile import TemporaryDirectory
from threading import Event, Thread
from time import monotonic, monotonic_ns
import unittest
from unittest.mock import Mock, patch

from pydantic import ValidationError

from ORCHESTRATOR_beta_C68.watching.watcher_poll import (
    PollComplete,
)
from ORCHESTRATOR_beta_C68.ORCHESTRATOR_beta_C68__tests.lifecycle.lifecycle_queue_watch_cases import LifecycleQueueWatchCases
from ..ORCHESTRATOR_beta_C68__tests__shared import (
    Kernel,
    kernel_server,
    lifecycle_job,
    project_jobs,
    restore_reuse,
)


class LifecycleKernel(Kernel):
    def do_GET(self):
        if self.path == "/structure?instance_id=test":
            self.reply(
                200,
                self.server.structure,
                [("x-anechoic-generation", self.server.generation)],
            )
        else:
            self.reply(404, {})

    def do_POST(self):
        request = json.loads(
            self.rfile.read(int(self.headers["Content-Length"]))
        )
        if self.path != "/database" or request["instance_id"] != "test":
            self.reply(404, {})
            return
        row = (
            [self.server.archive_versions]
            if "duckdb_tables()" in request["sql"]
            else [self.server.generation, *self.server.query_values]
        )
        self.reply(200, {"result": {"rows": [row]}})


class LifecycleQueueTests(LifecycleQueueWatchCases, unittest.TestCase):
    def setUp(self):
        root = Path(self.enterContext(TemporaryDirectory())).resolve()
        (root / "control").mkdir()
        self.kernel = self.enterContext(kernel_server(root, LifecycleKernel))
        self.jobs = project_jobs(
            root, database_socket=str(root / "kernel.sock")
        )
        self.request = self.jobs.binding | {
            "instance_id": "test",
            "name": "atom_lifecycle_create_draft",
            "arguments": {
                "newAtom": {
                    "template": "task",
                    "container": {"component": "C00"},
                }
            },
        }
        restore_reuse(self.jobs, "original")
        self.jobs.generation_reuse.status_domains = {
            "S": ["active"],
            "T": ["active"],
            "P": ["active"],
            "C": ["active"],
        }
        self.structure = {"project": {"ref": "AN-S-1@1"}, "components": {}}
        self.kernel.structure = self.structure
        self.kernel.generation = "original"
        self.kernel.query_values = ["1", "[]"]
        self.kernel.archive_versions = False
        self.worker = self.enterContext(
            patch.object(
                self.jobs,
                "_run_cold_lifecycle",
                return_value={
                    "lifecycle": {"outcome": "completed"},
                    "delta": None,
                    "projection_error": None,
                },
            )
        )
        self.addCleanup(self.jobs.close)

    def poll(self, clean):
        source = str(self.jobs.watcher.control_root)
        started = monotonic_ns()
        self.jobs.watcher.observer.emitters[0]._snapshot_started = started
        self.jobs.watcher.on_poll_complete(
            PollComplete(source, started=started, clean=clean)
        )

    def fake_foreground(self):
        emitter = Mock(baseline_clean=True)
        emitter.watch.path = str(self.jobs.watcher.control_root)
        self.jobs.watcher.observer = Mock(emitters=[emitter])
        self.poll(True)

    def test_admitted_context_keeps_coordinated_writes_on_the_project_path(
        self,
    ):
        for name, ref, descendants, carriers, coordinated in (
            ("change_status", "AN-T-1", True, [], True),
            ("change_status", "AN-T-1", False, [], False),
            (
                "archive",
                "AN-S-2",
                True,
                [self.carrier("LAYER_1_META_ONTOLOGY_C9/_SPEC")],
                True,
            ),
            ("archive", "AN-S-2", True, [self.carrier("_SPEC")], False),
        ):
            with self.subTest(
                name=name, descendants=descendants, carriers=carriers
            ):
                self.assert_lifecycle_context(
                    name, ref, descendants, carriers, coordinated
                )

    def test_model_lifecycle_uses_capture_for_relocated_claims(self):
        owner = "control/ONTOLOGY_SCORE_C91/CONTINUANT_PITCHFORK_C9"
        for status, path, target, coordinated in (
            ("active", f"{owner}/_DES/a.md", None, True),
            ("draft", f"{owner}/_SPEC/01_draft/a.md", None, False),
            ("draft", f"{owner}/_SPEC/01_draft/a.md", "active", True),
            (
                "draft",
                "elsewhere/CONTINUANT_PITCHFORK_C9/a.md",
                "active",
                False,
            ),
        ):
            with self.subTest(status=status, source=path, target=target):
                carrier = {
                    "id": "AN-S-2",
                    "status": status,
                    "source_path": path,
                }
                self.assert_lifecycle_context(
                    "change_status",
                    "AN-S-2",
                    False,
                    [carrier],
                    coordinated,
                    target,
                )

    def test_only_model_claims_require_capture_on_archive(self):
        owner = "control/ONTOLOGY_SCORE_C82/CONTINUANT_PITCHFORK_C9"
        for filename, coordinated in (
            ("_DES/AN-S-2-DES--prose.md", False),
            ("_DES/AN-S-2-DES-MANIFEST_PROPERTY--property.md", True),
            ("_SPEC/AN-S-2-SPEC-MANIFEST_NODE--node.md", True),
        ):
            carrier = {
                "id": "AN-S-2",
                "status": "active",
                "source_path": f"{owner}/{filename}",
            }
            for name, target in (
                ("archive", None),
                ("change_status", "archived"),
            ):
                with self.subTest(source=filename, operation=name):
                    self.assert_lifecycle_context(
                        name, "AN-S-2", False, [carrier], coordinated, target
                    )

    def assert_lifecycle_context(
        self, name, ref, descendants, carriers, coordinated, target=None
    ):
        self.kernel.query_values = [
            json.dumps(self.structure),
            None,
            "[]",
            "1",
            "2",
            json.dumps(carriers),
            descendants,
            "[]",
            "0",
        ]
        arguments = {"target": {"ref_id": ref}}
        if target is not None:
            arguments["targetStatus"] = target
        with patch.object(self.jobs, "lifecycle_job", None):
            job = lifecycle_job(self.jobs, f"atom_lifecycle_{name}", arguments)
            base, structure, facts = self.jobs._lifecycle_inputs(job)
        self.assertEqual(("original", self.structure), (base, structure))
        if coordinated:
            self.assertEqual({}, facts)
        else:
            self.assertEqual(carriers, facts["lifecycle_context"]["carriers"])
            self.assertEqual(
                descendants, facts["lifecycle_context"]["has_descendants"]
            )

    def test_pending_archive_accepts_allocation_after_first_checkpoint(self):
        self.jobs.deferred_archive = {}
        code, payload = self.jobs.lifecycle(self.request)
        self.assertEqual(
            (409, "archive_pending"), (code, payload["error"]["code"])
        )
        self.kernel.archive_versions = True
        with patch.object(
            self.jobs, "_await_lifecycle", return_value=(200, {})
        ) as accepted:
            self.assertEqual((200, {}), self.jobs.lifecycle(self.request))
        job = accepted.call_args.args[0]
        self.assertTrue(job.archive_versions)
        _, _, facts = self.jobs._lifecycle_inputs(job)
        self.assertEqual("1", facts["indexed_task"]["max_number"])

    @staticmethod
    def carrier(parent):
        return {
            "id": "AN-S-2",
            "status": "active",
            "source_path": f"control/{parent}/AN-S-2-SPEC--claim.md",
        }

    def queued_job(self):
        return lifecycle_job(
            self.jobs, self.request["name"], self.request["arguments"]
        )

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
        self.enterContext(
            patch.object(self.jobs, "_lifecycle_inputs", side_effect=inputs)
        )
        dispatch = Thread(
            target=self.jobs._run_queued_lifecycle, args=(job,), daemon=True
        )
        self.addCleanup(release.set)
        dispatch.start()
        self.assertTrue(entered.wait(3))
        job.deadline = monotonic()
        status, result = self.jobs._await_lifecycle(job)
        self.assertEqual(
            (504, "lifecycle_deadline_exceeded"),
            (status, result["error"]["code"]),
        )
        self.assertIn(
            "no lifecycle write was attempted", result["error"]["message"]
        )
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
        self.assertEqual(
            (504, "write_outcome_unknown"), (status, result["error"]["code"])
        )
        self.assertIs(job, self.jobs.lifecycle_job)
