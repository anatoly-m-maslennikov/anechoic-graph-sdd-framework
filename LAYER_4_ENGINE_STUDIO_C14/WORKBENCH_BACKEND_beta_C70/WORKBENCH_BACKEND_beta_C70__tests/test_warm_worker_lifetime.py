"""C70 owns a single optional worker independently of Project peers."""
import io
import json
from contextlib import redirect_stderr
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from WORKBENCH_BACKEND_beta_C70.WORKBENCH_BACKEND_beta_C70__shared import open_warm_worker

WORKER = "WORKBENCH_BACKEND_beta_C70.warm_worker"


class Client:
    def __init__(self, calls):
        self.calls = calls

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def settimeout(self, timeout):
        pass

    def connect(self, path):
        self.calls.append(("connect", path))

    def sendall(self, data):
        self.calls.append(("request", json.loads(data)))

    def recv(self, size):
        return b'{"ready":true,"pid":1234}\n'


class WarmWorkerLifetimeTests(unittest.TestCase):
    def test_ready_worker_is_checked_and_stopped_after_use(self):
        calls = []
        process = SimpleNamespace(pid=1234, poll=lambda: None)
        with patch(WORKER + ".subprocess.Popen", return_value=process), \
             patch(WORKER + "._stop", side_effect=lambda peer: calls.append(("stop", peer.pid))), \
             patch(WORKER + ".socket.socket", side_effect=lambda *a: Client(calls)):
            with open_warm_worker() as worker:
                self.assertTrue(worker[0].endswith("/worker.sock"))
                self.assertGreaterEqual(worker[1], 0)
                self.assertEqual(calls[-1], ("request", {"kind": "health"}))
                self.assertFalse(any(call[0] == "stop" for call in calls))
            self.assertEqual(calls[-1], ("stop", 1234))

    def test_failed_start_falls_back_once(self):
        output = io.StringIO()
        with patch(WORKER + ".subprocess.Popen", side_effect=OSError("unavailable")), \
             redirect_stderr(output), open_warm_worker() as worker:
            self.assertIsNone(worker)
        self.assertEqual(output.getvalue().count("using cold worker startup"), 1)

    def test_body_error_propagates_after_worker_cleanup(self):
        process = SimpleNamespace(pid=1234, poll=lambda: None)
        with patch(WORKER + ".subprocess.Popen", return_value=process), \
             patch(WORKER + "._stop") as stop, \
             patch(WORKER + ".socket.socket", side_effect=lambda *a: Client([])):
            with self.assertRaisesRegex(OSError, "body"):
                with open_warm_worker():
                    raise OSError("body")
            stop.assert_called_once_with(process)
