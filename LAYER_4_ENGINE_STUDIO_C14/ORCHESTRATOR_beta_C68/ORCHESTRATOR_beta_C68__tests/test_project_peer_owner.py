"""Exercise the candidate's direct peer owner at its process boundary."""

from contextlib import closing
from hashlib import sha256
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
from tempfile import TemporaryDirectory
from time import sleep
import unittest

from .ORCHESTRATOR_beta_C68__tests__shared import Connection, ENGINE, project, wait_for


PROFILE_KEYS = {"ANECHOIC_RUNTIME_PROFILE", "ANECHOIC_WORKBENCH_STORAGE",
                "ANECHOIC_JOURNAL_STORAGE", "ANECHOIC_ARCHIVES"}


def request(path, route, payload=None):
    with closing(Connection(path)) as connection:
        connection.request("GET" if payload is None else "POST", route,
                           None if payload is None else json.dumps(payload))
        response = connection.getresponse()
        return response.status, json.load(response)


class ProjectPeerOwnerTests(unittest.TestCase):
    def setUp(self):
        self.directory = Path(self.enterContext(TemporaryDirectory(prefix="ane-project-peers-", dir="/tmp"))).resolve()
        self.ready = self.directory / "peers.ready"
        self.kernel = self.directory / "db.sock"
        self.jobs = self.directory / "jobs.sock"
        self.root = self.directory / "project"
        self.root.mkdir()
        self.control, self.manifest = project(self.root)
        self.digest = sha256(self.manifest.read_bytes()).hexdigest()
        self.environment = {**os.environ, "PYTHONPATH": str(ENGINE), "ANECHOIC_RUNTIME_PROFILE": "test",
                            "ANECHOIC_WORKBENCH_STORAGE": "memory", "ANECHOIC_JOURNAL_STORAGE": "files",
                            "ANECHOIC_ARCHIVES": "load", "ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY": os.environ.get(
                                "ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY", str(ENGINE.parent / ".anechoic_tmp/workbench/extensions"))}

    def command(self, root):
        return [
            sys.executable, "-B", "-P", "-m", "ORCHESTRATOR_beta_C68.project_peer_owner",
            "--socket", str(self.directory / "api.sock"), "--instance-id", "test", "--project-root", str(root),
            "--control-root", self.control.name, "--manifest-path", self.manifest.name, "--manifest-sha256", self.digest,
            "--project-prefix", "AN", "--project-name", "Anechoic", "--host-root", "/host/project",
            "--workbench-public-url", "http://127.0.0.1/anechoic", "--blacklist", "query_schema",
        ]

    def stop(self, process):
        process.stdin.close()
        try:
            process.wait(timeout=15)
        except subprocess.TimeoutExpired:
            process.terminate()
            process.wait(timeout=15)

    def start(self, *args, root=None, environment=None):
        process = subprocess.Popen([*self.command(root or self.root), *args],
                                   env=self.environment if environment is None else environment, stdin=subprocess.PIPE)
        self.addCleanup(self.stop, process)
        wait_for(self.ready.is_file, process)
        self.assertEqual(b"", self.ready.read_bytes())
        self.assertEqual(0, self.ready.stat().st_mode & 0o077)
        self.assertFalse((self.directory / "binding.json").exists())
        return process

    def peer_pids(self):
        _, kernel = request(self.kernel, "/health")
        _, jobs = request(self.jobs, "/health")
        self.assertEqual(("test", self.digest), (kernel["result"]["instance_id"], kernel["result"]["manifest_sha256"]))
        self.assertEqual("test", jobs["result"]["instance_id"])
        return kernel["result"]["pid"], jobs["result"]["pid"]

    def assert_stopped(self, pids):
        for path in (self.ready, self.kernel, self.jobs):
            self.assertFalse(path.exists(), path)
        for pid in pids:
            with self.assertRaises(ProcessLookupError):
                os.kill(pid, 0)

    def test_ttl_and_parent_eof(self):
        process = self.start("--result-ttl-seconds", "1")
        pids = self.peer_pids()
        wait_for(lambda: request(self.kernel, "/health")[1]["result"]["ready"], process, timeout=60)
        status, result = request(self.kernel, "/database", {"instance_id": "test", "sql": "SELECT 42", "page_size": 1})
        self.assertEqual(200, status, result)
        query_id = result["result"]["query_id"]
        sleep(1.05)
        status, result = request(self.kernel, "/database", {"instance_id": "test", "query_id": query_id,
                                                             "offset": 0, "page_size": 1})
        self.assertEqual(400, status, result)
        self.assertIn("query_id", result["error"]["message"])
        self.stop(process)
        self.assertEqual(0, process.returncode)
        self.assert_stopped(pids)

    def test_exited_peer_reaps_pair(self):
        process = self.start()
        pids = self.peer_pids()
        os.kill(pids[1], signal.SIGKILL)
        self.assertNotEqual(0, process.wait(timeout=15))
        self.assert_stopped(pids)

    def assert_profile(self, name, profile, overrides, expected):
        root = self.directory / name
        root.mkdir()
        project(root)
        environment = {key: value for key, value in self.environment.items() if key not in PROFILE_KEYS}
        environment.update(overrides)
        args = ()
        if profile is not None:
            environment["ANECHOIC_RUNTIME_PROFILE"] = profile
            args = ("--journal-storage", "duckdb")
        projection, journal, archive = expected
        process = self.start(*args, root=root, environment=environment)
        try:
            pids = self.peer_pids()
            runtime = root / ".anechoic_runtime"
            if projection is None:
                databases = set()
            else:
                identity = sha256(b"test").hexdigest()
                databases = {f"projection-{identity}-{self.digest}{projection}.duckdb"}
            self.assertEqual(databases, {file.name for file in (runtime / "iwe_console/beta").glob("*.duckdb")})
            self.assertEqual(journal == "duckdb", (runtime / "db/project.duckdb").is_file())
            status, runs = request(self.jobs, "/jobs/worker-runs?instance_id=test")
            self.assertEqual(200, status)
            self.assertEqual(archive == "skip", runs["result"].get("archive", {}).get("state") == "disabled")
        finally:
            self.stop(process)
        self.assertEqual(0, process.returncode)
        self.assert_stopped(pids)

    def assert_invalid_profile(self, settings, message):
        environment = {key: value for key, value in self.environment.items() if key not in PROFILE_KEYS}
        with subprocess.Popen(self.command(self.root), env=environment | settings,
                              stdin=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as process:
            try:
                self.assertNotEqual(0, process.wait(timeout=15))
                self.assertIn(message, process.stderr.read())
            finally:
                self.stop(process)
        self.assert_stopped(())
        self.assertFalse((self.root / ".anechoic_runtime").exists())

    def test_profiles_reach_kernel_and_orchestrator(self):
        cases = (
            ("legacy", None, {}, ("", "files", "load")),
            ("local", "dev-local", {}, (None, "files", "skip")),
            ("preprod", "dev-preprod", {}, ("", "duckdb", "load")),
            ("test", "test", {}, (None, "files", "load")),
            ("prod", "prod", {}, ("", "duckdb", "load")),
            ("test-native-journal", "test", {"ANECHOIC_JOURNAL_STORAGE": "duckdb"}, (None, "duckdb", "load")),
            ("disk-skip", "dev-local", {"ANECHOIC_WORKBENCH_STORAGE": "disk"}, ("-dev-local-skip", "files", "skip")),
            ("disk-load", "dev-local", {"ANECHOIC_WORKBENCH_STORAGE": "disk", "ANECHOIC_ARCHIVES": "load"},
             ("-dev-local-load", "files", "load")),
        )
        for name, profile, overrides, expected in cases:
            with self.subTest(profile=name):
                self.assert_profile(name, profile, overrides, expected)

        invalid = (
            ({"ANECHOIC_RUNTIME_PROFILE": "unknown"}, "Invalid ANECHOIC_RUNTIME_PROFILE"),
            ({"ANECHOIC_ARCHIVES": "bad"}, "Invalid ANECHOIC_ARCHIVES"),
            ({"ANECHOIC_RUNTIME_PROFILE": "prod", "ANECHOIC_ARCHIVES": "skip"}, "requires the dev-local profile"),
            ({"ANECHOIC_JOURNAL_STORAGE": "bad"}, "Invalid ANECHOIC_JOURNAL_STORAGE"),
            ({"ANECHOIC_WORKBENCH_STORAGE": "bad"}, "Invalid ANECHOIC_WORKBENCH_STORAGE"),
        )
        for settings, message in invalid:
            with self.subTest(settings=settings):
                self.assert_invalid_profile(settings, message)


if __name__ == "__main__":
    unittest.main()
