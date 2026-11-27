"""Exercise worker state with real child processes."""

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
from threading import Thread
import time

import tempfile
import unittest


_PATH = Path(__file__).resolve().parents[1] / "ORCHESTRATOR_C66__shared.py"
_SPEC = importlib.util.spec_from_file_location("orchestrator", _PATH)
_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)
Orchestrator = _MODULE.Orchestrator


def _run(owner, code, *, kind="model_build", timeout=5, cwd=None, env=None):
    return owner.run_worker(
        kind, [sys.executable, "-c", code], cwd=cwd, env=env, timeout=timeout
    )


class TestOrchestrator(unittest.TestCase):
    def test_running_and_completed_snapshots(self):
        temporary = tempfile.TemporaryDirectory()
        tmp_path = Path(temporary.name).resolve()
        owner = Orchestrator()
        result = []
        code = (
            "import os,sys,time; print(os.getcwd()); "
            "print(os.environ['WORKER_TEST']); sys.stdout.flush(); "
            "time.sleep(.4)"
        )
        thread = Thread(
            target=lambda: result.append(
                _run(
                    owner,
                    code,
                    cwd=tmp_path,
                    env={**os.environ, "WORKER_TEST": "yes"},
                )
            )
        )
        thread.start()
        deadline = time.monotonic() + 3
        while (
            not owner.worker_runs()["active"] and time.monotonic() < deadline
        ):
            time.sleep(0.01)
        snapshot = owner.worker_runs()
        assert len(snapshot["active"]) == 1
        active = snapshot["active"][0]
        assert active["pid"] > 0 and active["status"] == "running"
        active["status"] = "changed"
        json.dumps(owner.worker_runs())
        thread.join(5)
        assert not thread.is_alive()
        assert result[0].stdout.decode().splitlines() == [str(tmp_path), "yes"]
        terminal = owner.worker_runs()
        assert terminal["active"] == []
        assert terminal["latest"][0]["status"] == "completed"
        assert terminal["latest"][0]["id"] == active["id"]
        temporary.cleanup()

    def test_nonzero_and_bounded_latest(self):
        owner = Orchestrator()
        result = _run(
            owner, "import sys; sys.stderr.write('bad'); sys.exit(3)"
        )
        assert result.returncode == 3 and result.stderr == b"bad"
        assert owner.worker_runs()["latest"][0]["status"] == "failed"
        _run(owner, "pass")
        _run(owner, "pass", kind="structure_refresh")
        latest = owner.worker_runs()["latest"]
        assert len(latest) == 2
        assert {run["kind"] for run in latest} == {
            "model_build",
            "structure_refresh",
        }
        assert all(run["status"] == "completed" for run in latest)

    def test_timeout_kills_and_reaps(self):
        owner = Orchestrator()
        with self.assertRaises(subprocess.TimeoutExpired):
            _run(owner, "import time; time.sleep(10)", timeout=0.1)
        snapshot = owner.worker_runs()
        assert snapshot["active"] == []
        run = snapshot["latest"][0]
        assert run["status"] == "timed_out"
        with self.assertRaises(ProcessLookupError):
            os.kill(run["pid"], 0)

    def test_stop_kills_active_child_and_rejects_launch(self):
        owner = Orchestrator()
        results = []
        thread = Thread(
            target=lambda: results.append(
                _run(owner, "import time; time.sleep(30)", timeout=40)
            )
        )
        thread.start()
        deadline = time.monotonic() + 3
        while (
            not owner.worker_runs()["active"] and time.monotonic() < deadline
        ):
            time.sleep(0.01)
        active = owner.worker_runs()["active"]
        assert len(active) == 1
        owner.stop()
        owner.stop()
        thread.join(3)
        assert not thread.is_alive()
        assert results[0].returncode != 0
        snapshot = owner.worker_runs()
        assert snapshot["active"] == []
        assert snapshot["latest"][0]["status"] == "cancelled"
        with self.assertRaises(ProcessLookupError):
            os.kill(active[0]["pid"], 0)
        with self.assertRaises(RuntimeError):
            _run(owner, "pass")


if __name__ == "__main__":
    unittest.main()
