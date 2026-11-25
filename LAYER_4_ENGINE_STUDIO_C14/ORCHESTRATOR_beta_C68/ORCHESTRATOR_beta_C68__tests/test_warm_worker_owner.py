"""Exercise optional warm Worker startup and cleanup through the shared owner CLI."""

from contextlib import suppress
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
from tempfile import TemporaryDirectory
from time import monotonic, sleep
import unittest


ENGINE = Path(__file__).resolve().parents[2]
FALLBACK = "Beta warm worker unavailable; using cold worker startup"
TIMEOUT = 15

HEALTH_PEER = """
import json
from pathlib import Path
import signal
import socket
import sys

mode,address,probe = sys.argv[1:]
with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as server:
    server.bind(address)
    server.listen()
    with server.accept()[0] as connection, connection.makefile("rb") as stream:
        request = json.loads(stream.readline())
        marker = Path(probe)
        temporary = marker.with_suffix(".tmp")
        temporary.write_text(json.dumps(request))
        temporary.replace(marker)
        if mode == "invalid_health":
            connection.sendall(b'{"ready":true,"pid":0}\\n')
        signal.pause()
"""

OWNER_CLI = """
import json
from pathlib import Path
from runpy import run_module
import subprocess
import sys
from unittest.mock import patch

mode, receipt, probe, health_peer = sys.argv[1:5]
del sys.argv[1:5]
launch = subprocess.Popen

def observe(args, *rest, **options):
    if "WORKERS_beta_C69.warm_worker" not in args:
        return launch(args, *rest, **options)
    address = args[args.index("--socket") + 1]
    if mode == "spawn_failure":
        raise OSError("Fixture worker could not start")
    if mode in ("invalid_health", "unready"):
        args = [sys.executable, "-B", "-c", health_peer, mode, address, probe]
    worker = launch(args, *rest, **options)
    record = Path(receipt)
    temporary = record.with_suffix(".tmp")
    temporary.write_text(json.dumps({"pid": worker.pid, "socket": address}))
    temporary.replace(record)
    if mode == "listener_failure":
        Path(sys.argv[sys.argv.index("--socket") + 1]).touch()
    return worker

with patch.object(subprocess, "Popen", observe):
    run_module("ORCHESTRATOR_beta_C68.shared_peer_owner", run_name="__main__")
"""


def exchange(address, request):
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
        client.settimeout(TIMEOUT)
        client.connect(str(address))
        client.sendall(json.dumps(request).encode() + b"\n")
        with client.makefile("rb") as stream:
            return json.loads(stream.readline())


class WarmWorkerOwnerTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(TemporaryDirectory(prefix="ane-warm-owner-", dir="/tmp"))).resolve()
        self.address = self.root / "owner.sock"
        self.receipt = self.root / "worker.json"
        self.probe = self.root / "probe.json"
        self.log = self.root / "owner.log"

    def start_owner(self, mode):
        settings = self.root / "host.toml"
        settings.write_text(f"schema_version=1\n[shared_mcp]\nproject_root={json.dumps(str(self.root))}\nhttp_port=8092\n")
        env = {**os.environ, "PYTHONPATH": str(ENGINE), "ANECHOIC_TEST_IMAGE_DEADLINES": "0"}
        with self.log.open("wb") as stderr:
            self.owner = subprocess.Popen(
                [sys.executable, "-B", "-P", "-c", OWNER_CLI, mode, str(self.receipt), str(self.probe),
                 HEALTH_PEER, "--socket", str(self.address), "--host-settings", str(settings)],
                cwd=ENGINE, env=env, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=stderr,
            )
        self.addCleanup(self.clean_up)

    def clean_up(self):
        try:
            if not self.owner.stdin.closed:
                self.owner.stdin.close()
            try:
                self.owner.wait(timeout=TIMEOUT)
            except subprocess.TimeoutExpired:
                self.owner.kill()
                self.owner.wait(timeout=TIMEOUT)
        finally:
            if self.receipt.is_file():
                worker = json.loads(self.receipt.read_text())
                pid = worker["pid"]
                with suppress(ProcessLookupError):
                    if os.getpgid(pid) == pid:
                        os.killpg(pid, signal.SIGKILL)

    def wait_for(self, read):
        deadline = monotonic() + TIMEOUT
        while self.owner.poll() is None and monotonic() < deadline:
            try:
                return read()
            except (FileNotFoundError, ConnectionRefusedError):
                sleep(0.02)
        self.fail(f"Peer owner did not reach its expected state: {self.log.read_text()}")

    def assert_owner_ready(self):
        value = self.wait_for(lambda: exchange(self.address, {"operation": "status"}))["result"]
        self.assertEqual(0, value["loaded_project_count"])

    def assert_worker_reaped(self, worker):
        with self.assertRaises(ProcessLookupError):
            os.kill(worker["pid"], 0)

    def assert_worker_cleaned(self, worker):
        self.assert_worker_reaped(worker)
        self.assertFalse(Path(worker["socket"]).parent.exists())

    def stop_owner(self):
        self.owner.stdin.close()
        self.assertEqual(0, self.owner.wait(timeout=TIMEOUT), self.log.read_text())
        self.assertFalse(self.address.exists())

    def test_owner_keeps_ready_worker_until_shutdown(self):
        self.start_owner("ready")
        self.assert_owner_ready()
        worker = json.loads(self.receipt.read_text())
        self.assertEqual({"ready": True, "pid": worker["pid"]}, exchange(worker["socket"], {"kind": "health"}))
        self.stop_owner()
        self.assert_worker_cleaned(worker)
        self.assertNotIn(FALLBACK, self.log.read_text())

    def test_owner_reaps_invalid_health_worker_before_falling_back(self):
        self.start_owner("invalid_health")
        self.assert_owner_ready()
        self.assertEqual({"kind": "health"}, json.loads(self.probe.read_text()))
        worker = json.loads(self.receipt.read_text())
        self.assert_worker_reaped(worker)
        self.assertEqual(1, self.log.read_text().count(FALLBACK))
        self.stop_owner()
        self.assert_worker_cleaned(worker)

    def test_spawn_failure_leaves_owner_available_for_cold_start(self):
        self.start_owner("spawn_failure")
        self.assert_owner_ready()
        self.assertFalse(self.receipt.exists())
        self.assertEqual(1, self.log.read_text().count(FALLBACK))
        self.stop_owner()

    def test_closing_parent_pipe_cancels_unready_worker_startup(self):
        self.start_owner("unready")
        self.assertEqual({"kind": "health"}, json.loads(self.wait_for(self.probe.read_text)))
        self.assertFalse(self.address.exists())
        worker = json.loads(self.receipt.read_text())
        os.kill(worker["pid"], 0)
        self.stop_owner()
        self.assert_worker_cleaned(worker)
        self.assertNotIn(FALLBACK, self.log.read_text())

    def test_listener_failure_propagates_after_warm_worker_cleanup(self):
        self.start_owner("listener_failure")
        self.assertNotEqual(0, self.owner.wait(timeout=TIMEOUT))
        self.assertIn("Address already in use", self.log.read_text())
        self.assertNotIn(FALLBACK, self.log.read_text())
        self.assert_worker_cleaned(json.loads(self.receipt.read_text()))


if __name__ == "__main__":
    unittest.main()
