"""Exercise the real lifecycle worker and kernel through private sockets."""
from contextlib import closing
from hashlib import sha256
import http.client
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
import unittest

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
    def test_real_lifecycle_and_generation_admission(self):
        engine = Path(__file__).resolve().parents[2]
        env = {**os.environ, "PYTHONPATH": str(engine), "ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY":
               str(engine.parent / ".anechoic_tmp/workbench/extensions")}
        with tempfile.TemporaryDirectory(prefix="ane-lifecycle-admit-", dir="/tmp") as directory:
            root = Path(directory).resolve()
            control, manifest = project(root)
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
        request = {**binding, "instance_id": "test", "name": "atom_lifecycle_create_draft",
                   "arguments": {"newAtom": {"template": "task", "container": {"component": "C00"},
                                              "body": "## Summary\n\nLifecycle admission canary.\n"}}}
        connection = Connection(path)
        try:
            connection.request("POST", "/jobs/lifecycle", json.dumps(request))
            response = connection.getresponse()
            result = json.loads(response.read())
        finally:
            connection.close()
        self.assertEqual(200, response.status, result)
        self.assertEqual("known", result["result"]["write_state"], result)
        self.assertEqual("completed", result["result"]["lifecycle"]["outcome"], result)
        self.assertEqual("ready", result["result"]["projection"]["state"], result)
        self.assertEqual(atom_id, result["result"]["lifecycle"]["savedDraft"]["atom_id"])

    def assert_visible(self, path, refs):
        sql = "SELECT reference FROM atoms WHERE status_group = 'Draft' ORDER BY reference"
        with closing(Connection(path)) as connection:
            connection.request("POST", "/database", json.dumps({"instance_id": "test", "sql": sql}))
            response = connection.getresponse()
            result = json.loads(response.read())
        self.assertEqual(200, response.status, result)
        self.assertEqual([[ref] for ref in refs], result["result"]["rows"])
