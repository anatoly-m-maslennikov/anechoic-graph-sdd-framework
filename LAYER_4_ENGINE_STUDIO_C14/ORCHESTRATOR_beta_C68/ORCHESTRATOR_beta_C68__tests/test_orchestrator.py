from contextlib import redirect_stderr
import http.client
import importlib
from io import StringIO
import json
import socket
import subprocess
import sys
import tempfile
import threading
import unittest
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from ORCHESTRATOR_beta_C68.generation import parse_worker_result
module = importlib.import_module("ORCHESTRATOR_beta_C68.ORCHESTRATOR_beta_C68__shared")
from ORCHESTRATOR_beta_C68.ORCHESTRATOR_beta_C68__tests.ORCHESTRATOR_beta_C68__tests__shared import (
    project,
)


class UnixConnection(http.client.HTTPConnection):
    def __init__(self, path):
        super().__init__("localhost")
        self.path = path

    def connect(self):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.connect(self.path)


class OrchestratorTests(unittest.TestCase):
    def test_generation_worker_does_not_relay_raw_traceback(self):
        with tempfile.TemporaryDirectory() as directory:
            binding = {"root": directory, "control_root": "control", "manifest_path": "manifest.md",
                       "manifest_sha256": "a" * 64, "project_prefix": "AN"}
            jobs = module.GenerationJobs("test", binding, directory + "/kernel.sock")
            stderr = StringIO()
            with patch.object(subprocess, "Popen") as popen, redirect_stderr(stderr):
                process = popen.return_value
                process.communicate.return_value = ("", "Traceback in inventory\nLimitReached: timeout_seconds\n")
                process.returncode = 1
                with self.assertRaisesRegex(RuntimeError, "^Worker failed: LimitReached: timeout_seconds$"):
                    jobs._run_worker(directory, None, None)
            self.assertNotIn("Traceback in inventory", stderr.getvalue())

    def test_graph_restart_exhaustion_logs_safe_records_and_stops_automatic_retry(self):
        with tempfile.TemporaryDirectory() as directory:
            binding = {"root": directory, "control_root": "control", "manifest_path": "manifest.md",
                       "manifest_sha256": "a" * 64, "project_prefix": "AN"}
            jobs = module.GenerationJobs("test", binding, directory + "/kernel.sock")
            jobs.startup_capture = True
            message = "Project source or dependency inputs changed during capture after one Realization Graph restart"
            payload = {"ingestion_failure": {"source": "build", "issues": [{"code": "realization_scan_failed"}]},
                       "graph_consistency": {
                           "sources": {"change": "changed", "path": "app/main.py", "fields": ["status", "imports"]},
                           "resolution_inputs": {"change": "added", "path": "/absolute/token=private.txt"},
                       }}
            stderr = StringIO()
            first = {"sources": {"change": "removed", "path": "app/first.py"}}
            restart = "anechoic-realization-graph-restart " + json.dumps(first)
            with (patch.object(subprocess, "Popen") as popen, redirect_stderr(stderr),
                  patch.object(jobs, "_record_ingestion_failure") as record_failure):
                process = popen.return_value
                process.communicate.return_value = (json.dumps(payload), f"{restart}\nPrivate traceback\n{message}\n")
                process.returncode = 1
                outcome = jobs._generate(startup=True)
            self.assertEqual("failed", outcome["state"])
            self.assertIn(message, outcome["message"])
            self.assertNotIn("retrying", outcome)
            retry = module.CurrentnessRetry()
            retry.observe(outcome)
            self.assertIsNone(retry.due)
            popen.assert_called_once()
            self.assertEqual(payload["ingestion_failure"], record_failure.call_args.args[0].diagnostic)
            warning, record = (item for item in map(json.loads, stderr.getvalue().splitlines())
                               if item["code"] == "realization_graph_inputs_changed")
            self.assertEqual(("WARNING", "restarting", first), (warning["severity"], warning["outcome"], warning["details"]))
            self.assertEqual(jobs.latest["run_id"], warning["correlation_id"])
            self.assertEqual(("ERROR", "realization_graph_inputs_changed", jobs.latest["run_id"]),
                             (record["severity"], record["code"], record["correlation_id"]))
            self.assertEqual({"sources": payload["graph_consistency"]["sources"],
                              "resolution_inputs": {"change": "added"}}, record["details"])
            self.assertNotIn("private", stderr.getvalue().lower())

    def test_worker_success_relays_first_graph_difference_with_run_id(self):
        with tempfile.TemporaryDirectory() as directory:
            binding = {"root": directory, "control_root": "control", "manifest_path": "manifest.md",
                       "manifest_sha256": "a" * 64, "project_prefix": "AN"}
            jobs = module.GenerationJobs("test", binding, directory + "/kernel.sock")
            jobs.active = {"run_id": "a" * 32}
            details = {"sources": {"change": "added", "path": "app/main.py"}}
            restart = "anechoic-realization-graph-restart " + json.dumps(details)
            stderr = StringIO()
            with patch.object(subprocess, "Popen") as popen, redirect_stderr(stderr):
                process = popen.return_value
                process.communicate.return_value = ("{}", f"\n{restart}\n")
                process.returncode = 0
                self.assertEqual("{}", jobs._communicate_worker(directory, {}))
            record = json.loads(stderr.getvalue())
            self.assertEqual(("WARNING", "restarting", "a" * 32, details),
                             (record["severity"], record["outcome"], record["correlation_id"], record["details"]))

    def test_http_and_real_worker_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "server.sock")
            server = module.Server(path, "test")
            thread = threading.Thread(target=server.serve_forever)
            thread.start()
            self.addCleanup(thread.join)
            self.addCleanup(server.server_close)
            self.addCleanup(server.shutdown)
            def call(method, target, body=None):
                connection = UnixConnection(path)
                connection.request(method, target, body=body)
                response = connection.getresponse()
                result = response.status, json.loads(response.read())
                connection.close()
                return result
            status, health = call("GET", "/health")
            self.assertEqual(200, status)
            self.assertEqual("test", health["result"]["instance_id"])
            self.assertIs(False, health["result"]["lifecycle_active"])
            self.assertEqual(409, call("GET", "/jobs/worker-runs?instance_id=other")[0])
            self.assertEqual(400, call("POST", "/jobs/build", "{}")[0])
            binding = {key: "bad" for key in module.FIELDS}
            binding["instance_id"] = "test"
            status, result = call("POST", "/jobs/build", json.dumps(binding))
            self.assertEqual(502, status)
            self.assertEqual("worker_failed", result["error"]["code"])
            status, result = call("GET", "/jobs/worker-runs?instance_id=test")
            self.assertEqual(200, status)
            self.assertIsNone(result["result"]["active"])
            self.assertEqual("failed", result["result"]["latest"]["state"])

    def test_health_reports_lifecycle_between_admission_and_completion(self):
        jobs = module.GenerationJobs("test", {"root": "/tmp", "control_root": ".",
            "manifest_path": "manifest.md", "manifest_sha256": "a" * 64, "project_prefix": "AN"}, "socket")
        self.assertIs(False, jobs.health()["lifecycle_active"])
        with jobs.lock:
            jobs.lifecycle_job = {}
        self.assertIs(True, jobs.health()["lifecycle_active"])
        with jobs.lock:
            jobs.lifecycle_job = None
        self.assertIs(False, jobs.health()["lifecycle_active"])

    def test_real_worker_success(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            control, manifest = project(root)
            binding = {"instance_id": "test", "root": str(root), "control_root": control.name,
                       "manifest_path": manifest.name, "manifest_sha256": sha256(manifest.read_bytes()).hexdigest(),
                       "project_prefix": "AN"}
            jobs = module.Jobs("test")
            status, result = jobs.build(binding)
            self.assertEqual(200, status, result)
            self.assertEqual([{"reference": "AN-S-1", "summary": "Anechoic"}], result["result"]["atoms"])
            self.assertEqual("succeeded", jobs.status()["latest"]["state"])

    def test_generation_handoff_and_recovery(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            (root / "control").mkdir()
            binding = {"root": str(root), "control_root": "control", "manifest_path": "manifest.md",
                       "manifest_sha256": "a" * 64, "project_prefix": "AN"}
            jobs = module.GenerationJobs("test", binding, str(root / "kernel.sock"))
            sent = []
            worker_requests = []
            class Worker:
                returncode = 0
                def __init__(self, command, **kwargs):
                    output = Path(command[-1])
                    (output / "model.json").write_bytes(b'{"line":"a"}\r\n')
                    (output / "structure.json").write_bytes(b'{}')
                def communicate(self, value=None, timeout=None):
                    worker_requests.append(json.loads(value))
                    return json.dumps({"snapshot": {}, "receipt": {}, "graph": None, "reuse": None}), ""
            class Connection:
                def __init__(self, path):
                    pass
                def request(self, method, path, body, headers):
                    sent.append((method, path, json.loads(body)))
                def getresponse(self):
                    class Response:
                        status = 200
                        def read(self):
                            return b'{"result":{"generation":"g1"}}'
                    return Response()
                def close(self):
                    pass
            with patch.object(subprocess, "Popen", side_effect=OSError("broken")):
                jobs._generate()
            self.assertEqual("failed", jobs.status()["latest"]["state"])
            self.assertIn("broken", jobs.status()["latest"]["message"])
            with patch.object(subprocess, "Popen", Worker), patch(
                    "ORCHESTRATOR_beta_C68.generation.UnixConnection", Connection):
                jobs._generate()
            self.assertEqual("g1", jobs.status()["latest"]["generation"])
            self.assertEqual("full", jobs.status()["latest"]["kind"])
            self.assertEqual([{"binding": binding, "reuse": None}], worker_requests)
            self.assertEqual(("PUT", "/generation"), sent[0][:2])
            self.assertEqual('{"line":"a"}\r\n', sent[0][2]["model"])
            self.assertEqual({"instance_id", "snapshot", "receipt", "graph", "model", "structure"}, set(sent[0][2]))
            self.assertEqual(400, jobs.build({})[0])

    def test_single_active_build_and_timeout(self):
        jobs = module.Jobs("test")
        request = {key: "x" for key in module.FIELDS}
        request["instance_id"] = "test"
        started, release = threading.Event(), threading.Event()
        def worker(*args, **kwargs):
            started.set()
            release.wait(5)
            return subprocess.CompletedProcess([], 0, '{"atoms": []}', '')
        result = []
        with patch.object(subprocess, "run", side_effect=worker):
            thread = threading.Thread(target=lambda: result.append(jobs.build(request)))
            thread.start()
            self.assertTrue(started.wait(5))
            self.assertEqual("running", jobs.status()["active"]["state"])
            self.assertEqual(409, jobs.build(request)[0])
            release.set()
            thread.join(5)
        self.assertEqual((200, {"result": {"atoms": []}}), result[0])
        with patch.object(subprocess, "run", side_effect=subprocess.TimeoutExpired("worker", 1)):
            self.assertEqual(504, jobs.build(request)[0])
        self.assertEqual("worker_timeout", jobs.status()["latest"]["code"])

    def test_ticket_delta_requires_every_event_to_be_a_bounded_ticket_file_mutation(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        control = root / "_anechoic_fixture"
        control.mkdir()
        binding = {"root": str(root), "control_root": control.name, "project_prefix": "AN"}
        old = control / "__TICKETS" / "AN-T-1--original.md"
        new = control / "001_TICKETS" / "AN-T-1--next.md"

        def event(path, destination=None, kind="modified", directory=False):
            return {"old_path": str(path), "new_path": str(destination) if destination is not None else None,
                    "event_type": kind, "is_directory": directory}

        classify = module.ticket_delta_paths
        expected = sorted([old.relative_to(root).as_posix(), new.relative_to(root).as_posix()])
        self.assertEqual(expected, classify(binding, [event(old, new, "moved"), event(new)]))
        for other in ({}, event(root / "AN-T-5--external.md"), event(old, directory=True),
                      event(old, kind="moved"), event(old, new), event(old.with_suffix(".py")),
                      event(control / "__TKT" / "README.md"), event(control / "AN-T-5--other.md")):
            with self.subTest(event=other):
                self.assertIsNone(classify(binding, [event(old), other]))
        paths = [event(old.with_name(f"AN-T-{index}--task.md")) for index in range(1025)]
        self.assertEqual(500, len(classify(binding, paths[:500])))
        self.assertEqual(1024, len(classify(binding, paths[:1024])))
        self.assertIsNone(classify(binding, paths))
        link = control / "__TKT" / "AN-T-2--symbolic.md"
        link.parent.mkdir()
        link.symlink_to(new)
        self.assertIsNone(classify(binding, [event(link)]))

    def test_worker_delta_must_echo_the_base_and_both_path_parts(self):
        path = "_anechoic_fixture/__TKT/AN-T-1--task.md"
        reuse = {"base_generation": "old"}
        result = {"base_generation": "old", "paths": [["_anechoic_fixture/__TKT", "AN-T-1--task.md"]],
                  "snapshot": {}, "snapshot_sha256": "ignored"}
        self.assertEqual(result, parse_worker_result(json.dumps(result), reuse, [path]))
        for invalid in (result | {"base_generation": "new"}, result | {"paths": [path]}):
            with self.assertRaises(ValueError):
                parse_worker_result(json.dumps(invalid), reuse, [path])
        with self.assertRaises(ValueError):
            parse_worker_result(json.dumps(result), reuse, None)


if __name__ == "__main__":
    unittest.main()
