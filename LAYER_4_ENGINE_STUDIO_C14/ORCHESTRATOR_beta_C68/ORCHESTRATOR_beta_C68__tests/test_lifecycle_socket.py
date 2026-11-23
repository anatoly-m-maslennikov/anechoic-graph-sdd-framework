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

from ..ORCHESTRATOR_beta_C68__shared import GenerationJobs
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
        for parent, expected in (("LAYER_1_META_ONTOLOGY_C9/_SPEC", True), ("_SPEC", False)):
            row = carrier | {"source_path": f"{control}/{parent}/AN-S-2-SPEC--claim.md"}
            self.assertEqual(expected, lifecycle._requires_project_capture(spec, context | {"carriers": [row]}, control))

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
