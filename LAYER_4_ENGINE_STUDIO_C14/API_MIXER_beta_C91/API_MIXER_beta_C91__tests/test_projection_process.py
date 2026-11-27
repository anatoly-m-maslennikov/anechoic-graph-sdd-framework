"""Exercise projection control through both API CLI entry points."""

import json
import os
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path

import httpx2

from ._projection_cases_1 import ProjectionCases1
from ._projection_cases_2 import ProjectionCases2
from .projection_peer_fixture import (
    DIGEST,
    INSTANCE,
    Owner,
    Peer,
    Server,
)

ENGINE = Path(__file__).resolve().parents[2]


class ProjectionTest(ProjectionCases1, ProjectionCases2, unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir="/tmp")
        self.path = Path(self.temp.name).resolve()
        self.servers = []
        for kind, handler in (("db", Peer), ("jobs", Peer), ("owner", Owner)):
            server = Server(str(self.path / (kind + ".sock")), handler)
            os.chmod(self.path / (kind + ".sock"), 0o600)
            server.kind, server.requests = kind, []
            threading.Thread(target=server.serve_forever, daemon=True).start()
            self.servers.append(server)
        self.prepare_owner()
        self.manifest = self.path / "manifest"
        self.manifest.write_text("manifest")
        info = self.manifest.stat()
        self.version = [
            info.st_dev,
            info.st_ino,
            info.st_mode,
            info.st_size,
            info.st_mtime_ns,
            info.st_ctime_ns,
        ]
        self.gate = self.path / "gate"
        (self.path / "peers.ready").touch(mode=0o600)
        self.processes, self.clients = [], []
        self.start_apis()

    def prepare_owner(self):
        root = str(self.path)
        owner = self.servers[2]
        owner.releases, owner.cold = [], True
        owner.binding = {
            "root": root,
            "control_root": root + "/control",
            "control_relative": "control",
            "instance_id": INSTANCE,
            "project_name": "Project",
            "project_prefix": "AN",
            "manifest_path": root + "/manifest",
            "manifest_ref": "AN-S-1",
            "manifest_sha256": DIGEST,
            "parameters": {},
            "host_root": None,
            "tool_blacklist": [],
            "release_workflows_enabled": False,
        }
        self.worker_binding = {
            "root": root,
            "control_root": "control",
            "manifest_path": "manifest",
            "manifest_sha256": DIGEST,
            "project_prefix": "AN",
        }
        owner.lease = {
            "database_socket": root + "/db.sock",
            "orchestrator_socket": root + "/jobs.sock",
            "worker_binding": self.worker_binding,
        }

    def start_apis(self):
        root = str(self.path)
        direct = [
            "API_MIXER_beta_C91.API_MIXER_beta_C91__shared",
            "--role",
            "api",
            "--socket",
            root + "/direct.sock",
            "--instance-id",
            INSTANCE,
            "--project-root",
            root,
            "--control-root",
            "control",
            "--manifest-path",
            "manifest",
            "--manifest-sha256",
            DIGEST,
            "--project-prefix",
            "AN",
        ]
        shared = [
            "API_MIXER_beta_C91.shared_runtime",
            "--socket",
            root + "/shared.sock",
            "--peer-owner-socket",
            root + "/owner.sock",
        ]
        for args, name in ((direct, "direct"), (shared, "shared")):
            self.start_api(args, name, root)

    def start_api(self, args, name, root):
        env = {
            **os.environ,
            "PYTHONPATH": str(ENGINE),
            "ANECHOIC_LOG_LEVEL": "ERROR",
        }
        if name == "direct":
            env["ANECHOIC_BETA_DIRECT_MANIFEST"] = json.dumps(
                {
                    "path": str(self.manifest),
                    "gate": str(self.gate),
                    "version": self.version,
                }
            )
        process = subprocess.Popen(
            [sys.executable, "-B", "-P", "-m", *args],
            cwd=ENGINE,
            env=env,
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        client = httpx2.Client(
            transport=httpx2.HTTPTransport(uds=root + "/" + name + ".sock"),
            base_url="http://private",
            timeout=5,
            trust_env=False,
        )
        self.processes.append(process)
        self.clients.append(client)
        deadline = time.monotonic() + 10
        while (
            not (self.path / (name + ".sock")).exists()
            and process.poll() is None
            and time.monotonic() < deadline
        ):
            time.sleep(0.05)
        if not (self.path / (name + ".sock")).exists():
            self.fail("API process did not start")

    def tearDown(self):
        for client in self.clients:
            client.close()
        for process in self.processes:
            process.stdin.close()
            process.wait(timeout=10)
            process.stderr.close()
        for server in self.servers:
            server.shutdown()
            server.server_close()
        self.temp.cleanup()

    def call(self, index, name, arguments):
        data = {
            "name": name,
            "arguments": arguments,
            "session_id": None,
            "public_base_url": None,
        }
        if index == 0:
            data.update(instance_id=INSTANCE, asserted_project_root=None)
        else:
            data["arguments"] = {"project_root": str(self.path), **arguments}
        return self.clients[index].post("/tools", json=data).json()


if __name__ == "__main__":
    unittest.main()
