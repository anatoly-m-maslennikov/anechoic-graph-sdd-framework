import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from ORCHESTRATOR_beta_C68 import ORCHESTRATOR_beta_C68__shared as runtime


class BatchedGenerationTests(unittest.TestCase):
    def test_full_build_forwards_the_batch_pin_instead_of_rows(self):
        with TemporaryDirectory() as directory:
            binding = {"root": directory, "control_root": "control", "manifest_path": "manifest.md",
                       "manifest_sha256": "a" * 64, "project_prefix": "AN"}
            jobs = runtime.GenerationJobs("test", binding, directory + "/kernel.sock")
            pin = {"sha256": "b" * 64, "bytes": 701}

            def capture(stage, reuse, paths, **options):
                self.assertIsNone(reuse)
                for name in ("model", "structure"):
                    (Path(stage) / f"{name}.json").write_text("{}")
                return ({"batch_artifact": pin, "receipt": {}, "reuse": None}, None, {})

            with (patch.object(jobs, "_capture_generation", side_effect=capture) as worker,
                  patch("ORCHESTRATOR_beta_C68.generation.UnixConnection") as transport):
                connection = transport.return_value
                response = connection.getresponse.return_value
                response.status = 200
                response.read.return_value = b'{"result":{"generation":"built","result_ids":{}}}'
                result = jobs._attempt_generation("all", None)
            self.assertEqual(("built", "full"), (result["generation"], result["kind"]))
            self.assertEqual(("PUT", "/generation"), connection.request.call_args.args[:2])
            payload = json.loads(connection.request.call_args.args[2])
            stage = worker.call_args.args[0]
            self.assertEqual(pin | {"path": str(Path(stage) / "generation-batches.jsonl")}, payload["batch_artifact"])
            self.assertEqual("all", payload["refresh_target"])
            self.assertTrue({"snapshot", "graph", "carrier_hashes"}.isdisjoint(payload))

    def test_generation_handoff_and_recovery(self):
        with TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            (root / "control").mkdir()
            binding = {"root": str(root), "control_root": "control", "manifest_path": "manifest.md",
                       "manifest_sha256": "a" * 64, "project_prefix": "AN"}
            jobs = runtime.GenerationJobs("test", binding, str(root / "kernel.sock"))
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
                    sent.append((method, path, json.loads(body), body))
                def getresponse(self):
                    class Response:
                        status = 200
                        def read(self):
                            return b'{"result":{"generation":"g1"}}'
                    return Response()
                def close(self):
                    pass
            self._assert_worker_failure(jobs)
            with (patch.object(subprocess, "Popen", Worker),
                  patch("ORCHESTRATOR_beta_C68.generation_worker.read_accepted_model", return_value=None),
                  patch("ORCHESTRATOR_beta_C68.generation.UnixConnection", Connection)):
                jobs._generate()
            self._assert_handoff(jobs, root, binding, worker_requests, sent)

    def _assert_handoff(self, jobs, root, binding, worker_requests, sent):
        self.assertEqual("g1", jobs.status()["latest"]["generation"])
        self.assertEqual("full", jobs.status()["latest"]["kind"])
        self.assertEqual([{"binding": binding, "reuse": None, "batch_full": True,
                           "model_source": {"accepted_model": None,
                                            "spec_database": {"socket": str(root / "kernel.sock"),
                                                              "instance_id": "test"}}}], worker_requests)
        self.assertEqual(("PUT", "/generation"), sent[0][:2])
        self.assertEqual(json.dumps(sent[0][2], ensure_ascii=False, separators=(",", ":")).encode(), sent[0][3])
        self.assertEqual('{"line":"a"}\r\n', sent[0][2]["model"])
        self.assertEqual({"instance_id", "snapshot", "receipt", "graph", "model", "structure"}, set(sent[0][2]))
        self.assertEqual(400, jobs.build({})[0])

    def _assert_worker_failure(self, jobs):
        with (patch.object(subprocess, "Popen", side_effect=OSError("broken")),
              patch("ORCHESTRATOR_beta_C68.generation_worker.read_accepted_model", return_value=None)):
            jobs._generate()
        self.assertEqual("failed", jobs.status()["latest"]["state"])
        self.assertIn("broken", jobs.status()["latest"]["message"])
