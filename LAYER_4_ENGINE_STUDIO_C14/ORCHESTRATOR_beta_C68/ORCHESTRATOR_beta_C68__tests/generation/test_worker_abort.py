"""Verify run-scoped abort against real Worker child processes."""

import os
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch

from ORCHESTRATOR_beta_C68.ORCHESTRATOR_beta_C68__shared import GenerationJobs

from ..ORCHESTRATOR_beta_C68__tests__shared import RunFixture

MODULE = "ORCHESTRATOR_beta_C68.ORCHESTRATOR_beta_C68__shared"
WORKER_MODULE = "ORCHESTRATOR_beta_C68.generation.worker.generation_worker."
WARM_BROKER = """
import os
import sys
import time
from pathlib import Path
from WORKERS_beta_C69 import warm_worker

marker = Path(sys.argv.pop(1))
capture = warm_worker._ticket_delta

def pause_first_capture(*args):
    if not marker.exists():
        marker.write_text(str(os.getpid()))
        time.sleep(60)
    return capture(*args)

warm_worker._ticket_delta = pause_first_capture
warm_worker.main()
"""


def wait_for(check):
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        value = check()
        if value:
            return value
        time.sleep(0.01)
    raise AssertionError("Worker did not reach the expected state")


def warm_inputs(root):
    control = root / "_anechoic_test"
    tickets = control / "__TKT"
    tickets.mkdir(parents=True)
    manifest = root / "manifest.md"
    manifest.write_text("Pinned bytes")
    ticket = tickets / "AN-T-2--ticket.md"
    ticket.write_text("""---
atom_family: TKT
atom_id: AN-T-2
container: {component: C00}
priority: 2
context: {template: task}
state: {status: active, version: 1, updated_at: '2026-11-22T00:00:00Z'}
---

## Summary

Changed ticket.
""")
    binding = {
        "root": str(root),
        "control_root": control.name,
        "manifest_path": manifest.name,
        "manifest_sha256": sha256(manifest.read_bytes()).hexdigest(),
        "project_prefix": "AN",
    }
    change = {
        "is_directory": False,
        "event_type": "modified",
        "old_path": str(ticket),
    }
    reuse = {
        "base_generation": "base",
        "inputs": {},
        "graph_config": {},
        "endpoints": {
            "CONTAINED_BY": [{"inverse_alias": "CONTAINS"}, False],
            "CONTAINS": [{}, True],
        },
    }
    return binding, change, reuse


def _spawn_sleeper(real_popen):
    def spawn(*args, **kwargs):
        return real_popen(
            [sys.executable, "-c", "import time; time.sleep(60)"],
            **kwargs,
        )

    return spawn


def _cold_binding(root):
    binding = {
        "root": str(root),
        "control_root": "control",
        "manifest_path": "manifest.md",
        "manifest_sha256": "a" * 64,
        "project_prefix": "AN",
    }
    return binding


class WorkerAbortTests(unittest.TestCase):
    def test_warm_abort_reaps_child_and_preserves_broker(self):
        with tempfile.TemporaryDirectory(
            prefix="ane-warm-", dir="/tmp"
        ) as directory:
            root = Path(directory).resolve()
            address, marker = root / "broker.sock", root / "child"
            binding, change, reuse = warm_inputs(root)
            broker = subprocess.Popen(
                [
                    sys.executable,
                    "-B",
                    "-c",
                    WARM_BROKER,
                    str(marker),
                    "--socket",
                    str(address),
                ],
                start_new_session=True,
            )
            try:
                self._assert_warm_run(
                    address, binding, reuse, change, marker, broker
                )
            finally:
                broker.terminate()
                broker.wait(timeout=5)

    def _assert_warm_run(
        self, address, binding, reuse, change, marker, broker
    ):
        wait_for(address.exists)
        jobs = GenerationJobs(
            "instance",
            binding,
            "/tmp/unused",
            worker_socket=str(address),
            worker_load_seconds=2,
        )

        def admit_generation(*args):
            active = jobs.status()["active"]
            self.assertFalse(active["worker_alive"])
            request = {
                "instance_id": "instance",
                "run_id": active["run_id"],
            }
            self.assertEqual(409, jobs.abort(request)[0])
            return {"generation": "next"}

        with (
            patch(MODULE + ".Flow.finish"),
            patch(
                ("ORCHESTRATOR_beta_C68.generation.worker.generation_worker.subprocess.Popen"),
                side_effect=AssertionError("Cold Worker started"),
            ),
            patch(
                MODULE + ".admit_generation",
                side_effect=admit_generation,
            ) as admit,
        ):
            jobs.generation_reuse = reuse
            self._assert_warm_abort(jobs, change, marker, broker.pid)
            admit.assert_not_called()
            self.assertIsNone(broker.poll())
            jobs.generation_reuse = reuse
            self.assertEqual(
                "succeeded", jobs._generate(changes=[change])["state"]
            )
            self.assertEqual("warm", jobs.status()["latest"]["worker_mode"])
            admit.assert_called_once()

    def _assert_warm_abort(self, jobs, change, marker, broker_pid):
        thread = threading.Thread(
            target=jobs._generate, kwargs={"changes": [change]}, daemon=True
        )
        thread.start()
        wait_for(marker.exists)
        pid = int(wait_for(marker.read_text))
        self.assertNotEqual(broker_pid, pid)
        self.assertEqual(pid, os.getpgid(pid))

        def live_run():
            active = jobs.status()["active"]
            return active if active and active["worker_alive"] else None

        run_id = wait_for(live_run)["run_id"]
        self.assertEqual(
            409, jobs.abort({"instance_id": "instance", "run_id": "stale"})[0]
        )
        self.assertEqual(
            202, jobs.abort({"instance_id": "instance", "run_id": run_id})[0]
        )
        self.assertEqual(
            409, jobs.abort({"instance_id": "instance", "run_id": run_id})[0]
        )
        thread.join(5)
        self.assertFalse(thread.is_alive())
        latest = jobs.status()["latest"]
        self.assertEqual(
            ("aborted", "worker_aborted", run_id, "warm"),
            (
                latest["state"],
                latest["code"],
                latest["run_id"],
                latest["worker_mode"],
            ),
        )
        self.assertIsNone(jobs.status()["active"])
        with self.assertRaises(ProcessLookupError):
            os.getpgid(pid)

    def test_cold_worker_abort_is_scoped_and_terminal(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            (root / "control").mkdir()
            binding = _cold_binding(root)
            jobs = GenerationJobs("instance", binding, "/tmp/unused")
            real_popen = subprocess.Popen

            spawn = _spawn_sleeper(real_popen)

            with (
                patch(WORKER_MODULE + "worker_request", return_value={}),
                patch(WORKER_MODULE + "read_accepted_model", return_value={}),
                patch(WORKER_MODULE + "subprocess.Popen", side_effect=spawn),
                patch(MODULE + ".admit_generation") as admit,
                patch(MODULE + ".Flow.finish"),
            ):
                thread = threading.Thread(target=jobs._generate)
                thread.start()
                deadline = time.monotonic() + 5
                while time.monotonic() < deadline:
                    active = jobs.status()["active"]
                    if active and active["worker_alive"]:
                        break
                    time.sleep(0.01)
                self.assertTrue(active and active["worker_alive"])
                run_id = active["run_id"]
                self._assert_cold_requests(jobs, run_id)
                thread.join(5)
                self.assertFalse(thread.is_alive())
                self.assertEqual(
                    ("aborted", run_id),
                    (jobs.latest.state, jobs.latest.run_id),
                )
                self.assertIsNone(jobs.status()["active"])
                admit.assert_not_called()

    def _assert_cold_requests(self, jobs, run_id):
        self.assertEqual(
            409,
            jobs.abort({"instance_id": "other", "run_id": run_id})[0],
        )
        self.assertEqual(
            409,
            jobs.abort({"instance_id": "instance", "run_id": "stale"})[0],
        )
        self.assertEqual(
            400,
            jobs.abort(
                {
                    "instance_id": "instance",
                    "run_id": run_id,
                    "extra": 1,
                }
            )[0],
        )
        self.assertEqual(
            202,
            jobs.abort({"instance_id": "instance", "run_id": run_id})[0],
        )
        self.assertEqual(
            409,
            jobs.abort({"instance_id": "instance", "run_id": run_id})[0],
        )

    def test_abort_rejects_lifecycle_and_admission(self):
        with tempfile.TemporaryDirectory() as directory:
            binding = {
                "root": directory,
                "control_root": "control",
                "manifest_path": "m",
                "manifest_sha256": "a" * 64,
                "project_prefix": "AN",
            }
            jobs = GenerationJobs("instance", binding, "/tmp/unused")
            jobs.active = RunFixture(
                state="running", started_at=0, run_id="run"
            )
            jobs.lifecycle_job = object()
            self.assertEqual(
                409,
                jobs.abort({"instance_id": "instance", "run_id": "run"})[0],
            )
            jobs.lifecycle_job = None
            self.assertEqual(
                409,
                jobs.abort({"instance_id": "instance", "run_id": "run"})[0],
            )
