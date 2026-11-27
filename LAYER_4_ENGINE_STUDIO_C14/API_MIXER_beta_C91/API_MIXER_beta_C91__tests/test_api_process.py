"""Exercise the API CLI against private HTTP peers."""

import json
import os
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from importlib import import_module
from pathlib import Path

import httpx2

from ._api_cases_1 import ApiCases1
from ._api_cases_2 import ApiCases2
from ._api_test_generation import (
    DIGEST,
    ENGINE,
    KERNEL as KERNEL,
    MODULE,
    generation as generation,
)

sys.path.insert(0, str(ENGINE))
shared = import_module(
    "API_MIXER_beta_C91.API_MIXER_beta_C91__tests._package__shared"
)
Peer, Server = shared.ApiPeer, shared.Server


class ApiProcessTest(ApiCases1, ApiCases2, unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(dir="/tmp")
        self.path = Path(self.directory.name).resolve()
        self.servers = []
        for kind in ("db", "jobs"):
            server = Server(str(self.path / (kind + ".sock")), Peer)
            os.chmod(self.path / (kind + ".sock"), 0o600)
            server.kind, server.received, server.schema_paths = kind, [], []
            threading.Thread(target=server.serve_forever, daemon=True).start()
            self.servers.append(server)
        (self.path / "peers.ready").touch(mode=0o600)
        self.manifest = self.path / "manifest"
        self.manifest.write_text("manifest")
        info = self.manifest.lstat()
        version = [
            info.st_dev,
            info.st_ino,
            info.st_mode,
            info.st_size,
            info.st_mtime_ns,
            info.st_ctime_ns,
        ]
        self.gate = self.path / "gate"
        self.start_api(version)
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            if self.process.poll() is not None:
                self.fail(self.process.stderr.read().decode())
            if not (self.path / "api.sock").exists():
                time.sleep(0.05)
                continue
            try:
                if self.client.get("/health").json()["state"] == "ready":
                    return
            except httpx2.TransportError:
                time.sleep(0.05)
        self.fail("API did not start")

    def start_api(self, version):
        env = {
            **os.environ,
            "PYTHONPATH": str(ENGINE),
            "ANECHOIC_BETA_DIRECT_MANIFEST": json.dumps(
                {
                    "path": str(self.manifest),
                    "gate": str(self.gate),
                    "version": version,
                }
            ),
        }
        args = self.api_args()
        self.args, self.env = args, env
        self.process = subprocess.Popen(
            args,
            stdin=subprocess.PIPE,
            env=env,
            cwd=ENGINE,
            stderr=subprocess.PIPE,
        )
        self.client = httpx2.Client(
            transport=httpx2.HTTPTransport(uds=str(self.path / "api.sock")),
            base_url="http://private",
            trust_env=False,
            timeout=1,
        )

    def api_args(self):
        args = [
            sys.executable,
            "-B",
            "-P",
            "-m",
            MODULE,
            "--role",
            "api",
            "--socket",
            str(self.path / "api.sock"),
            "--instance-id",
            "instance",
            "--project-root",
            str(self.path),
            "--control-root",
            "control",
            "--manifest-path",
            "manifest",
            "--manifest-sha256",
            DIGEST,
            "--project-prefix",
            "AN",
            "--project-name",
            "Project",
        ]
        return args

    def tearDown(self):
        self.client.close()
        self.process.stdin.close()
        self.process.wait(timeout=10)
        self.process.stderr.close()
        for server in self.servers:
            server.shutdown()
            server.server_close()
        self.directory.cleanup()

    def call(self, arguments, **updates):
        data = {
            "name": "query_run",
            "arguments": arguments,
            "instance_id": "instance",
            "session_id": None,
            "public_base_url": None,
            "asserted_project_root": None,
        }
        return self.client.post("/tools", json=data | updates).json()


if __name__ == "__main__":
    unittest.main()
