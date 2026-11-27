"""Check actual Worker groups across abrupt managed-parent exit."""

from contextlib import suppress
import os
from pathlib import Path
import select
import signal
import subprocess
import sys
import unittest

_ENGINE = Path(__file__).resolve().parents[2]
_MODULES = (
    "WORKERS_beta_C69.WORKERS_beta_C69__shared",
    "WORKERS_beta_C69.lifecycle_worker",
)
_KEY = "ANECHOIC_BETA_WORKER_PARENT_PID"
_PARENT = (
    "\n"
    "import os\n"
    "import subprocess\n"
    "import sys\n"
    "\n"
    "worker = subprocess.Popen([sys.executable, '-B',"
    " '-P', '-c', sys.argv[1], sys.argv[2]],\n"
    "    env=os.environ | "
    "{'ANECHOIC_BETA_WORKER_PARENT_PID': "
    "str(os.getpid())},\n"
    "    stdin=int(sys.argv[3]), "
    "start_new_session=True)\n"
    "print(f'worker {worker.pid}', flush=True)\n"
    "worker.wait()\n"
)
_WORKER = """
import runpy
import subprocess
import sys

original = sys.stdin

class WorkInput:
    def read(self):
        descendant = subprocess.Popen([sys.executable, '-B', '-P', '-c',
                                       'from time import sleep; sleep(30)'])
        print(f'descendant {descendant.pid}', flush=True)
        return original.read()

sys.stdin = WorkInput()
module = sys.argv[1]
sys.argv[:] = [module]
runpy.run_module(module, run_name='__main__')
"""


def _line(stream):
    ready, _, _ = select.select([stream], [], [], 10)
    if not ready:
        raise AssertionError("Timed out waiting for the Worker group")
    return stream.readline()


def _env():
    return {**os.environ, "PYTHONPATH": str(_ENGINE)}


class ManagedWorkerParentTests(unittest.TestCase):
    def _assert_group_stops(self, module):
        reader, writer = os.pipe()
        pids = {}
        stopped = False
        try:
            with subprocess.Popen(
                [
                    sys.executable,
                    "-B",
                    "-P",
                    "-c",
                    _PARENT,
                    _WORKER,
                    module,
                    str(reader),
                ],
                env=_env(),
                stdout=subprocess.PIPE,
                pass_fds=(reader,),
                bufsize=0,
            ) as parent:
                try:
                    for _ in range(2):
                        name, pid = _line(parent.stdout).decode().split()
                        pids[name] = int(pid)
                    self.assertEqual(
                        pids["worker"], os.getpgid(pids["descendant"])
                    )
                    parent.kill()
                    self.assertEqual(-signal.SIGKILL, parent.wait(timeout=5))
                    self.assertEqual(b"", _line(parent.stdout))
                    stopped = True
                finally:
                    if parent.poll() is None:
                        parent.kill()
                    if not stopped and "worker" in pids:
                        with suppress(ProcessLookupError, PermissionError):
                            os.killpg(pids["worker"], signal.SIGKILL)
        finally:
            os.close(reader)
            os.close(writer)

    def test_managed_group_stops_after_parent_kill(self):
        for module in _MODULES:
            with self.subTest(module=module):
                self._assert_group_stops(module)

    def test_managed_entry_requires_its_actual_parent_and_isolated_group(self):
        for module in _MODULES:
            command = [sys.executable, "-B", "-P", "-m", module]
            for isolated, parent, message in (
                (False, os.getpid(), "requires an isolated process group"),
                (True, 2**31, "exited before Worker startup"),
            ):
                with self.subTest(module=module, isolated=isolated):
                    reply = subprocess.run(
                        command,
                        env=_env() | {_KEY: str(parent)},
                        start_new_session=isolated,
                        text=True,
                        input="{}",
                        capture_output=True,
                        timeout=10,
                    )
                    self.assertEqual(1, reply.returncode)
                    self.assertIn(message, reply.stderr)
