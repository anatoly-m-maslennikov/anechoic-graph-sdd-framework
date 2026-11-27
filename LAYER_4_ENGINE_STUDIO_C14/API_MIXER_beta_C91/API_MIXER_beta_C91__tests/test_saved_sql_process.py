"""Exercise saved SQL through the C91 CLIs and a real Kernel."""

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

from ._saved_sql_cases_1 import SavedSqlCases1
from ._saved_sql_cases_2 import SavedSqlCases2

ENGINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ENGINE))
shared = import_module(
    "API_MIXER_beta_C91.API_MIXER_beta_C91__tests._package__shared"
)
Jobs, Owner, Server, generation = (
    shared.Jobs,
    shared.Owner,
    shared.Server,
    shared.saved_sql_generation,
)

DIGEST = "a" * 64
INSTANCE = "b" * 64
KERNEL = (
    "KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71."
    "DATABASE_SERVER_beta_C71__shared"
)


class SavedSqlProcessTest(SavedSqlCases1, SavedSqlCases2, unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir="/tmp")
        self.root = Path(self.temp.name).resolve()
        self.processes, self.clients, self.servers = [], [], []
        self.env = {
            **os.environ,
            "PYTHONPATH": str(ENGINE),
            "ANECHOIC_LOG_LEVEL": "ERROR",
            "ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY": str(
                ENGINE.parent / ".anechoic_tmp/workbench/extensions"
            ),
        }
        for name, handler in (("jobs", Jobs), ("owner", Owner)):
            server = Server(str(self.root / (name + ".sock")), handler)
            server.requests = []
            os.chmod(self.root / (name + ".sock"), 0o600)
            threading.Thread(target=server.serve_forever, daemon=True).start()
            self.servers.append(server)
        self.configure_owner()
        self.start_kernel()
        self.start_apis()

    def configure_owner(self):
        root = str(self.root)
        owner = self.servers[1]
        owner.binding = {
            "root": root,
            "control_root": root + "/control",
            "control_relative": "control",
            "instance_id": INSTANCE,
            "project_name": "Project A",
            "project_prefix": "AN",
            "manifest_path": root + "/manifest",
            "manifest_ref": "AN-S-1",
            "manifest_sha256": DIGEST,
            "parameters": {
                "runtime": {
                    "workbench": {
                        "public_url": "https://configured.test/workbench"
                    }
                }
            },
            "host_root": None,
            "tool_blacklist": [],
            "release_workflows_enabled": False,
        }
        owner.lease = {
            "database_socket": root + "/db.sock",
            "orchestrator_socket": root + "/jobs.sock",
            "worker_binding": {
                "root": root,
                "control_root": "control",
                "manifest_path": "manifest",
                "manifest_sha256": DIGEST,
                "project_prefix": "AN",
            },
        }

    def start(self, module, args, socket_name):
        command = [sys.executable, "-B", "-P", "-m", module, *args]
        process = subprocess.Popen(
            command,
            cwd=ENGINE,
            env=self.env,
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
        self.processes.append(process)
        path = self.root / socket_name
        deadline = time.monotonic() + 20
        while (
            not path.exists()
            and process.poll() is None
            and time.monotonic() < deadline
        ):
            time.sleep(0.05)
        if not path.exists():
            if process.poll() is None:
                process.terminate()
            self.fail(process.stderr.read().decode())
        client = httpx2.Client(
            transport=httpx2.HTTPTransport(uds=str(path)),
            base_url="http://private",
            trust_env=False,
            timeout=20,
        )
        self.clients.append(client)
        return client

    def start_kernel(self):
        args = [
            "--socket",
            str(self.root / "db.sock"),
            "--instance-id",
            INSTANCE,
            "--manifest-sha256",
            DIGEST,
            "--project-root",
            str(self.root),
            "--journal-relative",
            "control/journal",
        ]
        self.kernel = self.start(KERNEL, args, "db.sock")
        response = self.kernel.put("/generation", json=generation())
        self.assertEqual(200, response.status_code, response.text)
        (self.root / "peers.ready").touch(mode=0o600)

    def start_direct(self, socket_name, public_url):
        root = str(self.root)
        direct = [
            "--role",
            "api",
            "--socket",
            str(self.root / socket_name),
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
            "--project-name",
            "Project A",
        ]
        if public_url is not None:
            direct.extend(("--workbench-public-url", public_url))
        return self.start(
            "API_MIXER_beta_C91.API_MIXER_beta_C91__shared",
            direct,
            socket_name,
        )

    def start_apis(self):
        self.direct = self.start_direct(
            "direct.sock", "https://configured.test/workbench"
        )
        shared = [
            "--socket",
            str(self.root / "shared.sock"),
            "--peer-owner-socket",
            str(self.root / "owner.sock"),
        ]
        self.shared = self.start(
            "API_MIXER_beta_C91.shared_runtime", shared, "shared.sock"
        )

    def tearDown(self):
        for client in self.clients:
            client.close()
        for process in reversed(self.processes):
            if process is self.processes[0]:
                process.terminate()
            else:
                process.stdin.close()
            process.wait(timeout=10)
            if not process.stdin.closed:
                process.stdin.close()
            process.stderr.close()
        for server in self.servers:
            server.shutdown()
            server.server_close()
        self.temp.cleanup()

    def call(
        self,
        shared,
        name,
        args,
        *,
        base="http://example.test",
        asserted=True,
        session=None,
    ):
        body = {
            "name": name,
            "arguments": args.copy(),
            "session_id": session,
            "public_base_url": base,
        }
        if shared:
            body["arguments"]["project_root"] = str(self.root)
        else:
            body.update(
                instance_id=INSTANCE,
                asserted_project_root=str(self.root) if asserted else None,
            )
        return (
            (self.shared if shared else self.direct)
            .post("/tools", json=body)
            .json()
        )

    def value(self, shared, name, args, **options):
        result = self.call(shared, name, args, **options)
        self.assertIn("result", result, result)
        return result["result"]["value"]


if __name__ == "__main__":
    unittest.main()
