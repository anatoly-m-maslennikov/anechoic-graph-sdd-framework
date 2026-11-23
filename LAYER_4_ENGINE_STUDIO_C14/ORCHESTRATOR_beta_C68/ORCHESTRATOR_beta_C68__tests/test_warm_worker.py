import json
import os
import socket
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from ORCHESTRATOR_beta_C68 import ORCHESTRATOR_beta_C68__shared as module
from ORCHESTRATOR_beta_C68.warm_worker import request


class ColdWorker:
    returncode = 0
    result = None

    def __init__(self, *args, **kwargs):
        pass

    def communicate(self, *args, **kwargs):
        return json.dumps(self.result), ""


def broker(socket_path, requests, response):
    server = socket.socket(socket.AF_UNIX)
    server.bind(socket_path)
    server.listen()

    def serve():
        with server, server.accept()[0] as connection:
            data = b""
            while not data.endswith(b"\n"):
                data += connection.recv(65536)
            requests.append(json.loads(data))
            try:
                if response == "wait":
                    time.sleep(0.3)
                else:
                    connection.sendall(response)
            except BrokenPipeError:
                pass

    thread = threading.Thread(target=serve)
    thread.start()
    return thread


class WarmWorkerTests(unittest.TestCase):
    def test_deadline_free_acceptance_preserves_next_reply(self):
        with tempfile.TemporaryDirectory() as directory:
            socket_path = str(Path(directory) / "broker")
            requests = []
            response = b'{"accepted":true,"pid":123}\n{"result":{"ok":true}}\n'
            thread = broker(socket_path, requests, response)
            with patch.dict(os.environ, ANECHOIC_TEST_IMAGE_DEADLINES="0"):
                self.assertEqual({"ok": True}, request(
                    socket_path, 0, {}, {}, [], lambda _: True))
            thread.join(1)
            self.assertIsNone(requests[0]["start_by"])

    def test_delta_status_reports_count_and_phase_times(self):
        with tempfile.TemporaryDirectory() as directory:
            binding = {"root": directory, "control_root": "control", "manifest_path": "manifest",
                       "manifest_sha256": "a" * 64, "project_prefix": "AN"}
            jobs = module.GenerationJobs("test", binding, "unused")
            reuse = {"base_generation": "old"}
            result = {"base_generation": "old", "paths": [["control/__TKT", "AN-T-1--task.md"]],
                      "snapshot": {}, "snapshot_sha256": "hash"}
            with (patch.object(jobs, "_run_worker", return_value=result),
                  patch.object(module, "admit_generation", return_value={"generation": "next", "kind": "native_delta"})):
                outcome = jobs._attempt_generation(None, reuse, ["control/__TKT/AN-T-1--task.md"])
            self.assertEqual(1, outcome["delta_path_count"])
            self.assertGreaterEqual(outcome["worker_seconds"], 0)
            self.assertGreaterEqual(outcome["admission_seconds"], 0)

    def test_large_batch_uses_cold_worker_with_all_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            binding = {"root": directory, "control_root": "control", "manifest_path": "manifest",
                       "manifest_sha256": "a" * 64, "project_prefix": "AN"}
            paths = [f"control/__TKT/AN-T-{index}--task.md" for index in range(500)]
            reuse = {"base_generation": "old"}
            expected = [[str(Path(path).parent), Path(path).name] for path in sorted(paths)]
            result = {"base_generation": "old", "snapshot": {}, "snapshot_sha256": "hash", "paths": expected}
            ColdWorker.result = result
            jobs = module.GenerationJobs("test", binding, "unused", worker_socket="unused", worker_load_seconds=1)
            with (patch.object(module, "warm_result", side_effect=AssertionError("warm worker called")),
                  patch.object(module.subprocess, "Popen", return_value=ColdWorker()) as process,
                  patch.object(ColdWorker, "communicate", return_value=(json.dumps(result), "")) as communicate):
                self.assertEqual(result, jobs._run_worker(directory, reuse, paths))
            self.assertEqual("cold", jobs.worker_mode)
            self.assertEqual(paths, json.loads(communicate.call_args.args[0])["paths"])
            process.assert_called_once()

    def test_accept_and_fallbacks(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            binding = {"root": directory, "control_root": "control", "manifest_path": "manifest",
                       "manifest_sha256": "a" * 64, "project_prefix": "AN"}
            path = "control/__TKT/AN-T-1--task.md"
            reuse = {"base_generation": "old"}
            result = {"base_generation": "old", "snapshot": {}, "snapshot_sha256": "hash",
                      "paths": [["control/__TKT", "AN-T-1--task.md"]]}
            ColdWorker.result = result
            jobs = module.GenerationJobs("test", binding, "unused", worker_socket=str(root / "broker"),
                                         worker_load_seconds=0.15)
            requests = []
            for response, expected in ((b'{"accepted":true,"pid":123}\n' + json.dumps({"result": result}).encode() + b'\n', "warm"),
                                       (b'{"accepted":false}\n', "cold"),
                                       (b'{"accepted":true,"pid":123}\n{"result":null}\n', "cold"), ("wait", "cold")):
                thread = broker(jobs.worker_socket, requests, response)
                with patch.object(module.subprocess, "Popen", ColdWorker):
                    self.assertEqual(result, jobs._run_worker(directory, reuse, [path]))
                thread.join(1)
                self.assertEqual(expected, jobs.worker_mode)
                (root / "broker").unlink()
            self.assertEqual({"kind", "start_by", "binding", "reuse", "paths"}, set(requests[0]))
            self.assertEqual("ticket_delta", requests[0]["kind"])
            with patch.object(module.subprocess, "Popen", ColdWorker):
                self.assertEqual(result, jobs._run_worker(directory, reuse, [path]))
            self.assertEqual("cold", jobs.worker_mode)


if __name__ == "__main__":
    unittest.main()
