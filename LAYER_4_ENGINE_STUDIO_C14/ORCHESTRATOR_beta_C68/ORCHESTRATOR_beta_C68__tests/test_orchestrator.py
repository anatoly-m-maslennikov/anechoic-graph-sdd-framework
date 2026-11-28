import http.client
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

from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from ORCHESTRATOR_beta_C68 import ORCHESTRATOR_beta_C68__shared as module
from ORCHESTRATOR_beta_C68.ORCHESTRATOR_beta_C68__tests.ORCHESTRATOR_beta_C68__tests__shared import (
    project,
)


from ORCHESTRATOR_beta_C68.ORCHESTRATOR_beta_C68__tests.generation._worker_diagnostics_cases import (
    WorkerDiagnosticsCases,
)


class UnixConnection(http.client.HTTPConnection):
    def __init__(self, path):
        super().__init__("localhost")
        self.path = path

    def connect(self):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.connect(self.path)


class OrchestratorTests(WorkerDiagnosticsCases, unittest.TestCase):
    def setUp(self):
        model = patch(
            "ORCHESTRATOR_beta_C68.generation.worker.generation_worker.read_accepted_model",
            return_value=None,
        )
        model.start()
        self.addCleanup(model.stop)

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
            self.assertEqual(
                409, call("GET", "/jobs/worker-runs?instance_id=other")[0]
            )
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
        jobs = module.GenerationJobs(
            "test",
            {
                "root": "/tmp",
                "control_root": ".",
                "manifest_path": "manifest.md",
                "manifest_sha256": "a" * 64,
                "project_prefix": "AN",
            },
            "socket",
        )
        self.assertIs(False, jobs.health()["lifecycle_active"])
        with jobs.lock:
            jobs.lifecycle_job = object()
        self.assertIs(True, jobs.health()["lifecycle_active"])
        with jobs.lock:
            jobs.lifecycle_job = None
        self.assertIs(False, jobs.health()["lifecycle_active"])

    def test_real_worker_success(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            control, manifest = project(root)
            binding = {
                "instance_id": "test",
                "root": str(root),
                "control_root": control.name,
                "manifest_path": manifest.name,
                "manifest_sha256": sha256(manifest.read_bytes()).hexdigest(),
                "project_prefix": "AN",
            }
            jobs = module.Jobs("test")
            status, result = jobs.build(binding)
            self.assertEqual(200, status, result)
            self.assertEqual(
                [{"reference": "AN-S-1", "summary": "Anechoic"}],
                result["result"]["atoms"],
            )
            self.assertEqual("succeeded", jobs.status()["latest"]["state"])

    def test_single_active_build_and_timeout(self):
        jobs = module.Jobs("test")
        request = {key: "x" for key in module.FIELDS}
        request["instance_id"] = "test"
        started, release = threading.Event(), threading.Event()

        def worker(*args, **kwargs):
            started.set()
            release.wait(5)
            return subprocess.CompletedProcess([], 0, '{"atoms": []}', "")

        result = []
        with patch.object(subprocess, "run", side_effect=worker):
            thread = threading.Thread(
                target=lambda: result.append(jobs.build(request))
            )
            thread.start()
            self.assertTrue(started.wait(5))
            active = jobs.status()["active"]
            self.assertEqual({"state", "started_at"}, set(active))
            active["state"] = "changed"
            self.assertEqual("running", jobs.status()["active"]["state"])
            with self.assertRaises(ValidationError):
                jobs.active.started_at = "invalid"
            self.assertEqual(409, jobs.build(request)[0])
            release.set()
            thread.join(5)
        self.assertEqual((200, {"result": {"atoms": []}}), result[0])
        self.assertEqual(
            {"state", "started_at", "finished_at"},
            set(jobs.status()["latest"]),
        )
        with patch.object(
            subprocess,
            "run",
            side_effect=subprocess.TimeoutExpired("worker", 1),
        ):
            self.assertEqual(504, jobs.build(request)[0])
        self.assertEqual("worker_timeout", jobs.status()["latest"]["code"])

    def test_ticket_delta_requires_every_event_to_be_a_bounded_ticket_file_mutation(
        self,
    ):
        root = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        control = root / "_anechoic_fixture"
        control.mkdir()
        binding = {
            "root": str(root),
            "control_root": control.name,
            "project_prefix": "AN",
        }
        old = control / "__TICKETS" / "AN-T-1--original.md"
        new = control / "001_TICKETS" / "AN-T-1--next.md"

        classify = module.ticket_delta_paths
        expected = sorted(
            [
                old.relative_to(root).as_posix(),
                new.relative_to(root).as_posix(),
            ]
        )
        self.assertEqual(
            expected,
            classify(
                binding, [_ticket_event(old, new, "moved"), _ticket_event(new)]
            ),
        )
        for other in (
            {},
            _ticket_event(root / "AN-T-5--external.md"),
            _ticket_event(old, directory=True),
            _ticket_event(old, kind="moved"),
            _ticket_event(old, new),
            _ticket_event(old.with_suffix(".py")),
            _ticket_event(control / "__TKT" / "README.md"),
            _ticket_event(control / "AN-T-5--other.md"),
        ):
            with self.subTest(event=other):
                self.assertIsNone(
                    classify(binding, [_ticket_event(old), other])
                )
        self._check_ticket_limits(classify, binding, old, control, new)

    def _check_ticket_limits(self, classify, binding, old, control, new):
        paths = [
            _ticket_event(old.with_name(f"AN-T-{index}--task.md"))
            for index in range(1025)
        ]
        self.assertEqual(500, len(classify(binding, paths[:500])))
        self.assertEqual(1024, len(classify(binding, paths[:1024])))
        self.assertIsNone(classify(binding, paths))
        link = control / "__TKT" / "AN-T-2--symbolic.md"
        link.parent.mkdir()
        link.symlink_to(new)
        self.assertIsNone(classify(binding, [_ticket_event(link)]))

    def test_worker_delta_must_echo_the_base_and_both_path_parts(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        binding = {
            "root": str(root),
            "control_root": "_anechoic_fixture",
            "manifest_path": "manifest.md",
            "manifest_sha256": "a" * 64,
            "project_prefix": "AN",
        }
        jobs = module.GenerationJobs(
            "test", binding, str(root / "kernel.sock")
        )
        path = "_anechoic_fixture/__TKT/AN-T-1--task.md"
        reuse = {"base_generation": "old"}
        result = {
            "base_generation": "old",
            "paths": [["_anechoic_fixture/__TKT", "AN-T-1--task.md"]],
            "snapshot": {},
            "snapshot_sha256": "ignored",
        }
        with patch.object(jobs, "_communicate_worker") as worker:
            worker.return_value = json.dumps(result)
            self.assertEqual(
                result, jobs._run_worker(str(root), reuse, [path])
            )
            for invalid in (
                result | {"base_generation": "new"},
                result | {"paths": [path]},
            ):
                worker.return_value = json.dumps(invalid)
                with self.assertRaises(ValueError):
                    jobs._run_worker(str(root), reuse, [path])
            worker.return_value = json.dumps(result)
            with self.assertRaises(ValueError):
                jobs._run_worker(str(root), reuse, None)


def _ticket_event(path, destination=None, kind="modified", directory=False):
    return {
        "old_path": str(path),
        "new_path": str(destination) if destination is not None else None,
        "event_type": kind,
        "is_directory": directory,
    }


if __name__ == "__main__":
    unittest.main()
