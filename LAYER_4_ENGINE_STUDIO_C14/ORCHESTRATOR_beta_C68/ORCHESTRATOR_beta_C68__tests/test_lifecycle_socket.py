"""Exercise the real lifecycle worker and kernel through private sockets."""
from contextlib import closing
from hashlib import sha256
import http.client
import importlib
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

from watchdog.events import DirCreatedEvent, DirDeletedEvent, DirMovedEvent, FileCreatedEvent
from watchdog.utils.dirsnapshot import DirectorySnapshot

from ..ORCHESTRATOR_beta_C68__shared import GenerationJobs
from ..watcher import SourceWatcher
from ..watcher_poll import PollComplete
from .ORCHESTRATOR_beta_C68__tests__shared import project


class Connection(http.client.HTTPConnection):
    def __init__(self, path):
        super().__init__("localhost", timeout=610)
        self.path = path

    def connect(self):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.settimeout(self.timeout)
        self.sock.connect(self.path)


class LifecycleSocketTests(unittest.TestCase):
    def archive_receipts(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        control = root / "control"
        archive = control / "09_archived"
        archive.mkdir(parents=True)
        owned = archive / "owned.md"
        owned.write_text("admitted")
        watcher = SourceWatcher(root, control, defer_archives=True)
        effects = [
            {"target": "control/09_archived", "operation": "create", "state": "known", "evidence": "directory"},
            {"target": "control/09_archived/owned.md", "operation": "create", "state": "known",
             "evidence": sha256(owned.read_bytes()).hexdigest()},
        ]
        return watcher, archive, owned, effects

    def archive_poll(self, watcher):
        control = str(watcher.control_root)
        started = time.monotonic_ns()
        watcher._proof.remember_archive_sample(control, started, DirectorySnapshot(control))
        self.assertIsNone(watcher._proof.sampled_archive_carriers(started, ()))
        watcher.on_poll_complete(PollComplete(control, started=started, clean=True, archive=True))

    def test_admitted_archive_creation_filters_only_its_directory_and_files(self):
        watcher, archive, owned, effects = self.archive_receipts()
        external = archive / "external.md"
        external.write_text("independent")
        before = (object(), 0, 0)
        with patch.object(watcher, "capture_epoch", return_value=(before[0], 1, 0)):
            watcher.acknowledge(effects, archive_epoch=before)
            for event in (DirCreatedEvent(str(archive)), FileCreatedEvent(str(owned)),
                          DirCreatedEvent(str(archive)), FileCreatedEvent(str(external))):
                watcher.dispatch(event)
            self.assertEqual([str(external)], [change["old_path"] for change in watcher.changes(0.1)])
            self.archive_poll(watcher)
            self.assertEqual([], watcher.changes(0.1))
            watcher.dispatch(DirDeletedEvent(str(archive)))
            watcher.dispatch(DirMovedEvent(str(archive), str(archive.parent / "moved")))
            self.assertEqual(["deleted", "moved"], [change["event_type"] for change in watcher.changes(0.1)])
            archive.rename(watcher.root / "old")
            archive.mkdir()
            watcher.dispatch(DirCreatedEvent(str(archive)))
            self.assertEqual(["created"], [change["event_type"] for change in watcher.changes(0.1)])

    def test_archive_directory_receipts_require_continuous_watcher_coverage(self):
        watcher, archive, _, effects = self.archive_receipts()
        observer = object()
        cases = [
            (None, (observer, 0, 0)),
            ((observer, 0, 0), (observer, 0, 1)),
            ((observer, 0, 0), (object(), 0, 0)),
        ]
        for before, after in cases:
            with self.subTest(before=before, after=after), patch.object(watcher, "capture_epoch", return_value=after):
                watcher.acknowledge(effects, archive_epoch=before)
                watcher.dispatch(DirCreatedEvent(str(archive)))
                self.assertEqual(["created"], [change["event_type"] for change in watcher.changes(0.1)])

    def test_archive_directory_create_survives_removal_before_first_carrier_event(self):
        watcher, archive, owned, effects = self.archive_receipts()
        before = (object(), 0, 0)
        with patch.object(watcher, "capture_epoch", return_value=(before[0], 1, 0)):
            watcher.acknowledge(effects, archive_epoch=before)
            watcher.dispatch(DirCreatedEvent(str(archive)))
            self.assertEqual([], watcher.changes(0.1))
            owned.unlink()
            self.archive_poll(watcher)
            self.assertEqual(["created"], [change["event_type"] for change in watcher.changes(0.1)])

    def test_lifecycle_receipts_cover_delayed_watcher_events(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        binding = {"root": str(root), "control_root": "control", "manifest_path": "manifest.md",
                   "manifest_sha256": "a" * 64, "project_prefix": "AN"}
        watcher = GenerationJobs("test", binding, "socket").watcher
        first, second = root / "first.md", root / "second.md"
        for path in (first, second):
            path.write_text(path.name)
            watcher.acknowledge([{"target": path.name, "operation": "create", "state": "known",
                                  "evidence": sha256(path.read_bytes()).hexdigest()}])
            watcher.queue.put({"old_path": str(path), "new_path": None, "is_directory": False})
        self.assertEqual([], watcher.changes(0.1))
        first.write_text("external edit")
        event = {"old_path": str(first), "new_path": None, "is_directory": False}
        watcher.queue.put(event)
        self.assertEqual([event], watcher.changes(0.1))

    def test_admitted_context_keeps_coordinated_writes_on_the_project_path(self):
        lifecycle = importlib.import_module("ORCHESTRATOR_beta_C68.lifecycle")
        control = "_anechoic_test"
        context = {"has_descendants": True, "carriers": []}
        task = {"name": "atom_lifecycle_change_status", "arguments": {"target": {"ref_id": "AN-T-1"}}}
        self.assertTrue(lifecycle._requires_project_capture(task, context, control))
        self.assertFalse(lifecycle._requires_project_capture(task, context | {"has_descendants": False}, control))
        spec = {"name": "atom_lifecycle_archive", "arguments": {"target": {"ref_id": "AN-S-2"}}}
        carrier = {"id": "AN-S-2", "status": "active"}
        for parent, expected in (("LAYER_1_META_ONTOLOGY_C9/_SPEC", True),
                                 ("ONTOLOGY_SCORE_C82/CONTINUANT_PITCHFORK_C9/_DES", True), ("_SPEC", False)):
            row = carrier | {"source_path": f"{control}/{parent}/AN-S-2-SPEC--claim.md"}
            self.assertEqual(expected, lifecycle._requires_project_capture(spec, context | {"carriers": [row]}, control))

    def test_replacement_promotion_uses_project_capture(self):
        lifecycle = importlib.import_module("ORCHESTRATOR_beta_C68.lifecycle")
        job = {"name": "atom_lifecycle_promote_draft", "arguments": {
            "target": {"ref_id": "AN-S-3196@3-draft", "version": 3}, "targetStatus": "ready"}}
        draft = {"id": "AN-S-3196", "_exact_ref": "AN-S-3196@3-draft", "version": 3,
                 "status_group": "Draft", "status": "draft", "source_path": "control/_SPEC/draft.md",
                 "replaces": True}
        context = {"has_descendants": False, "carriers": [draft]}
        self.assertTrue(lifecycle._requires_project_capture(job, context, "control"))
        self.assertFalse(lifecycle._requires_project_capture(job, context | {"carriers": [draft | {"replaces": False}]}, "control"))
        self.assertFalse(lifecycle._requires_project_capture(job, context | {"carriers": [draft | {"version": 2}]}, "control"))
        job["name"] = "atom_lifecycle_update"
        self.assertFalse(lifecycle._requires_project_capture(job, context, "control"))
        jobs = lifecycle.LifecycleJobs()
        jobs.startup_capture, jobs.deferred_archive = False, None
        jobs.generation_reuse = {"base_generation": "base", "endpoints": {}}
        jobs.database_socket, jobs.instance_id = "socket", "test"
        jobs.binding = {"project_prefix": "AN", "control_root": "control"}
        context["structure"] = {}
        with patch.object(lifecycle, "lifecycle_context", return_value=context):
            _, _, facts = jobs._lifecycle_inputs(job)
        self.assertNotIn("replaces", facts["lifecycle_context"]["carriers"][0])
        self.assertNotIn("has_descendants", facts["lifecycle_context"])

    def test_ready_spec_with_outgoing_replacement_uses_project_capture_for_activation(self):
        lifecycle = importlib.import_module("ORCHESTRATOR_beta_C68.lifecycle")
        job = {"name": "atom_lifecycle_change_status", "arguments": {
            "target": {"ref_id": "AN-S-2", "version": 1}, "targetStatus": "active"}}
        row = {"id": "AN-S-2", "status_group": "Current", "status": "ready",
               "source_path": "control/02_ready/AN-S-2-SPEC--claim.md", "replaces": True}
        context = {"has_descendants": False, "carriers": [row]}
        self.assertTrue(lifecycle._requires_project_capture(job, context, "control"))
        self.assertFalse(lifecycle._requires_project_capture(job, context | {"carriers": [row | {"replaces": False}]},
                                                             "control"))

    def test_real_lifecycle_and_generation_admission(self):
        engine = Path(__file__).resolve().parents[2]
        env = {**os.environ, "PYTHONPATH": str(engine)}
        env.setdefault("ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY", str(engine.parent / ".anechoic_tmp/workbench/extensions"))
        with tempfile.TemporaryDirectory(prefix="ane-lifecycle-admit-", dir="/tmp") as directory:
            root = Path(directory).resolve()
            control, manifest = project(root)
            manifest.write_text(manifest.read_text().replace("prefix='AN'", "prefix='AN', lens_whitelist=['SPEC']"))
            self.write_archived_tickets(control)
            binding = {"root": str(root), "control_root": control.name, "manifest_path": manifest.name,
                       "manifest_sha256": sha256(manifest.read_bytes()).hexdigest(), "project_prefix": "AN"}
            (root / "binding.json").write_text(json.dumps(binding))
            db, jobs = str(root / "db.sock"), str(root / "jobs.sock")
            db_module = "KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.DATABASE_SERVER_beta_C71__shared"
            jobs_module = "ORCHESTRATOR_beta_C68.ORCHESTRATOR_beta_C68__shared"
            database = subprocess.Popen([sys.executable, "-B", "-P", "-m", db_module, "--socket", db,
                "--instance-id", "test", "--manifest-sha256", binding["manifest_sha256"]], cwd=engine, env=env)
            orchestrator = worker = None
            try:
                self.wait_socket(db, database)
                worker = subprocess.Popen([sys.executable, "-B", "-P", "-m", "WORKERS_beta_C69.warm_worker",
                    "--socket", str(root / "worker.sock")], cwd=engine, env=env)
                self.wait_socket(root / "worker.sock", worker)
                orchestrator = subprocess.Popen([sys.executable, "-B", "-P", "-m", jobs_module,
                    "--socket", jobs, "--instance-id", "test", "--binding-file", str(root / "binding.json"),
                    "--database-socket", db, "--worker-socket", str(root / "worker.sock"),
                    "--worker-load-seconds", "1"], cwd=engine, env=env)
                self.wait_socket(jobs, orchestrator)
                self.wait_for_archive(db)
                self.assert_lifecycle(jobs, binding, "AN-T-101")
                self.assert_lifecycle(jobs, binding, "AN-T-102")
                self.assert_visible(db, ["AN-T-101@1-draft", "AN-T-102@1-draft"])
                self.assert_indexed_transitions(jobs, db, binding)
            finally:
                for process in (orchestrator, worker, database):
                    if process is not None:
                        process.terminate()
                        process.wait(timeout=10)

    def wait_socket(self, path, process):
        deadline = time.monotonic() + 10
        while not Path(path).exists() and process.poll() is None and time.monotonic() < deadline:
            time.sleep(.03)
        self.assertTrue(Path(path).exists())

    def wait_for_archive(self, path):
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            with closing(Connection(path)) as connection:
                connection.request("GET", "/health")
                result = json.loads(connection.getresponse().read())["result"]
            if result["ready"] and not result["archive_pending"]:
                return
            time.sleep(.03)
        self.fail("Archive admission did not complete")

    def write_archived_tickets(self, control):
        archive = control / "__TICKETS/TASKS/09_archived"
        archive.mkdir(parents=True)
        for number in ("00099", "100"):
            atom = f"AN-T-{number}"
            (archive / f"{atom}@1-TASK--archived.md").write_text(
                f"---\natom_family: TKT\natom_id: {atom}\ncontainer: {{component: C00}}\n"
                "priority: 2\ncontext: {template: task}\nstate: {status: archived, version: 1, "
                "updated_at: '2026-11-23T00:00:00Z'}\n---\n\n## Summary\n\nArchived Task.\n",
                encoding="utf-8",
            )

    def assert_lifecycle(self, path, binding, atom_id):
        result = self.call_lifecycle(path, binding, "create_draft", {"newAtom": {
            "template": "task", "container": {"component": "C00"},
            "body": "## Summary\n\nLifecycle admission canary.\n"}})
        self.assertEqual(atom_id, result["savedDraft"]["atom_id"])

    def call_lifecycle(self, path, binding, operation, arguments):
        request = {**binding, "instance_id": "test", "name": "atom_lifecycle_" + operation,
                   "arguments": arguments}
        with closing(Connection(path)) as connection:
            connection.request("POST", "/jobs/lifecycle", json.dumps(request))
            response = connection.getresponse()
            result = json.loads(response.read())
        self.assertEqual(200, response.status, result)
        self.assertEqual("known", result["result"]["write_state"], result)
        self.assertEqual("completed", result["result"]["lifecycle"]["outcome"], result)
        self.assertEqual("ready", result["result"]["projection"]["state"], result)
        return result["result"]["lifecycle"]

    def assert_indexed_transitions(self, path, database, binding):
        def call(operation, arguments):
            return self.call_lifecycle(path, binding, operation, arguments)

        task = {"ref_id": "AN-T-101", "version": 1}
        call("promote_draft", {"target": task | {"ref_id": "AN-T-101@1-draft"}, "targetStatus": "backlog"})
        revision = call("update", {"sourceCurrent": task})["savedDraft"]
        self.assertEqual("AN-T-101@2-draft", revision["ref_id"])
        asset_body = "## Summary\n\nMeasure indexed Ticket Asset.\n"
        asset = call("create_asset", {"newAtom": {"template": "work_report", "body": asset_body}})["artifact"]
        call("direct_update", {"target": {"ref_id": asset["ref_id"], "version": 1},
                               "changes": {"body": asset_body + "\nUpdated.\n"}})
        draft = call("create_draft", {"newAtom": {"template": "component_contract", "container": {"component": "C00"},
                    "lens": "SPEC", "body": "## Summary\n\nAdmitted Contract.\n\n## Guarantee\n\nReturn results.\n"}})["savedDraft"]
        contract = {"ref_id": draft["atom_id"], "version": 1}
        call("promote_draft", {"target": contract | {"ref_id": draft["ref_id"]}, "targetStatus": "ready"})
        call("change_status", {"target": contract, "targetStatus": "active"})
        call("archive", {"target": contract})
        self.assert_visible(database, ["AN-T-101@2-draft", "AN-T-102@1-draft"])

    def assert_visible(self, path, refs):
        sql = "SELECT reference FROM atoms WHERE status_group = 'Draft' ORDER BY reference"
        with closing(Connection(path)) as connection:
            connection.request("POST", "/database", json.dumps({"instance_id": "test", "sql": sql}))
            response = connection.getresponse()
            result = json.loads(response.read())
        self.assertEqual(200, response.status, result)
        self.assertEqual([[ref] for ref in refs], result["result"]["rows"])
