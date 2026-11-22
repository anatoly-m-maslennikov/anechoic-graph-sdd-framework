"""Exercise the real lifecycle worker and kernel through private sockets."""
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
            binding = {"root": str(root), "control_root": control.name, "manifest_path": manifest.name,
                       "manifest_sha256": sha256(manifest.read_bytes()).hexdigest(), "project_prefix": "AN"}
            (root / "binding.json").write_text(json.dumps(binding))
            db, jobs = str(root / "db.sock"), str(root / "jobs.sock")
            db_module = "KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.DATABASE_SERVER_beta_C71__shared"
            jobs_module = "ORCHESTRATOR_beta_C68.ORCHESTRATOR_beta_C68__shared"
            database = subprocess.Popen([sys.executable, "-B", "-P", "-m", db_module, "--socket", db,
                "--instance-id", "test", "--manifest-sha256", binding["manifest_sha256"]], cwd=engine, env=env)
            orchestrator = None
            try:
                self.wait_socket(db, database)
                orchestrator = subprocess.Popen([sys.executable, "-B", "-P", "-m", jobs_module,
                    "--socket", jobs, "--instance-id", "test", "--binding-file", str(root / "binding.json"),
                    "--database-socket", db], cwd=engine, env=env)
                self.wait_socket(jobs, orchestrator)
                self.assert_lifecycle(jobs, binding)
            finally:
                for process in (orchestrator, database):
                    if process is not None:
                        process.terminate()
                        process.wait(timeout=10)

    def wait_socket(self, path, process):
        deadline = time.monotonic() + 10
        while not Path(path).exists() and process.poll() is None and time.monotonic() < deadline:
            time.sleep(.03)
        self.assertTrue(Path(path).exists())

    def assert_lifecycle(self, path, binding):
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
