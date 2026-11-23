import importlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
module = importlib.import_module("ORCHESTRATOR_beta_C68.ORCHESTRATOR_beta_C68__shared")


def graph_worker(result, requests):
    class Worker:
        returncode = 0
        def __init__(self, *args, **kwargs): pass
        def communicate(self, value=None, timeout=None):
            requests.append(json.loads(value))
            return json.dumps(result), ""
    return Worker


class RestartCheckpointTests(unittest.TestCase):
    def test_admission_flow_records_whether_reuse_proof_is_required(self):
        with tempfile.TemporaryDirectory() as root:
            binding = {"root": root, "control_root": ".", "manifest_path": "m",
                       "manifest_sha256": "hash", "project_prefix": "AN"}
            jobs = module.GenerationJobs("test", binding, "socket")
            witness = {"inputs": {}, "graph_config": None, "endpoints": {}}
            for result, reuse, expected in (({"reuse": witness}, None, True),
                                             ({"reuse": None}, None, False),
                                             ({}, witness, True)):
                with self.subTest(result=result, reuse=reuse), \
                        patch.object(jobs, "_run_worker", return_value=result.copy()), \
                        patch.object(module, "admit_generation", return_value={"generation": "new"}), \
                        patch.object(jobs, "_flow_effect") as effect:
                    jobs._attempt_generation(None, reuse)
                effect.assert_any_call("generation_admission", outcome="succeeded",
                                       detail={"reuse_proof_present": expected})
            with patch.object(jobs, "_run_worker", return_value={"unchanged": True}), \
                    patch.object(module, "confirm_reuse", return_value={"generation": "new"}), \
                    patch.object(jobs, "_flow_effect") as effect:
                jobs._attempt_generation(None, None)
            effect.assert_called_once_with("generation_reuse_check", outcome="succeeded")

    def test_startup_loads_reuse_before_initial_revalidation(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        (root / "control").mkdir()
        binding = {"root": str(root), "control_root": "control", "manifest_path": "manifest.md",
                   "manifest_sha256": "a" * 64, "project_prefix": "AN"}
        jobs = module.GenerationJobs("test id", binding, "socket")
        reuse = {"base_generation": "old", "inputs": {}, "graph_config": None, "endpoints": {}, "carrier_hashes": {"control/a.md": "a" * 64}}
        calls = []
        class Connection:
            def __init__(self, path): pass
            def request(self, method, path): calls.append((method, path))
            def getresponse(self):
                class Response:
                    status = 200
                    def read(self): return json.dumps({"result": reuse}).encode()
                return Response()
            def close(self): pass
        def generate(*args, **kwargs):
            self.assertTrue(jobs.watcher.started)
            self.assertEqual(reuse, jobs.generation_reuse)
            self.assertEqual({"startup": True}, kwargs)
            jobs.stopping.set()
            return {"state": "succeeded"}
        with patch("ORCHESTRATOR_beta_C68.generation.UnixConnection", Connection), \
                patch.object(jobs, "_generate", side_effect=generate), \
                patch.object(jobs.watcher, "start", side_effect=lambda: setattr(jobs.watcher, "started", True)):
            jobs.start()
            jobs.thread.join(5)
        self.assertFalse(jobs.thread.is_alive())
        self.assertEqual([("GET", "/generation/reuse?instance_id=test+id")], calls)

    def test_full_admission_persists_worker_witness(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        (root / "control").mkdir()
        binding = {"root": str(root), "control_root": "control", "manifest_path": "manifest.md",
                   "manifest_sha256": "a" * 64, "project_prefix": "AN"}
        jobs = module.GenerationJobs("test", binding, "socket")
        witness = {"inputs": {}, "graph_config": None, "endpoints": {}}
        payloads = []
        class Connection:
            def __init__(self, path): pass
            def request(self, method, path, body, headers): payloads.append((path, json.loads(body)))
            def getresponse(self):
                class Response:
                    status = 200
                    def read(self): return b'{"result": {"generation": "new"}}'
                return Response()
            def close(self): pass
        def worker(directory, reuse, paths):
            for name in ("model", "structure"):
                (Path(directory) / (name + ".json")).write_text("{}")
            return {"snapshot": {}, "receipt": {}, "graph": None, "reuse": witness, "carrier_hashes": {"control/a.md": "a" * 64}}
        with patch("ORCHESTRATOR_beta_C68.generation.UnixConnection", Connection), \
                patch.object(jobs, "_run_worker", side_effect=worker):
            self.assertEqual("full", jobs._attempt_generation(None, None)["kind"])
        self.assertEqual("/generation", payloads[0][0])
        self.assertEqual(witness, payloads[0][1]["reuse"])
        self.assertEqual({"control/a.md": "a" * 64}, payloads[0][1]["carrier_hashes"])

    def test_startup_revalidates_and_retries_stale_base(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        (root / "control").mkdir()
        binding = {"root": str(root), "control_root": "control", "manifest_path": "manifest.md",
                   "manifest_sha256": "a" * 64, "project_prefix": "AN"}
        jobs = module.GenerationJobs("test", binding, "socket")
        reuse = {"base_generation": "old", "inputs": {}, "graph_config": None, "endpoints": {}}
        jobs.generation_reuse = reuse
        with patch.object(jobs, "_attempt_generation", side_effect=[module.GenerationBaseChanged(),
                          {"state": "succeeded", "generation": "new"}]) as attempt:
            self.assertEqual("succeeded", jobs._generate(startup=True)["state"])
        self.assertEqual([(None, reuse, None), (None, None)], [call.args for call in attempt.call_args_list])
        jobs.generation_reuse = reuse
        with patch.object(jobs, "_attempt_generation", return_value={"state": "succeeded"}) as attempt:
            jobs._generate()
        self.assertIsNone(attempt.call_args.args[1])

    def test_graph_refresh_request_validation_and_admission(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        (root / "control").mkdir()
        binding = {"root": str(root), "control_root": "control", "manifest_path": "manifest.md",
                   "manifest_sha256": "a" * 64, "project_prefix": "AN"}
        jobs = module.GenerationJobs("test id", binding, str(root / "kernel.sock"))
        witness = {"inputs": {}, "graph_config": {}, "endpoints": {}}
        reuse = {**witness, "base_generation": "old"}
        graph_result = {"base_generation": "old", "snapshot": {}, "snapshot_sha256": "s",
                        "graph": {}, "graph_sha256": "g", "reuse": witness}
        calls = []
        class Response:
            status = 200
            def getheader(self, name):
                return "old"
            def read(self):
                return b'{"result": {"generation": "new"}}' if calls[-1][0] == "PUT" else b'{"nodes": []}'
        class Connection:
            def __init__(self, path): pass
            def request(self, method, path, body=None, headers=None):
                calls.append((method, path, json.loads(body) if body else None))
            def getresponse(self): return Response()
            def close(self): pass
        requests = []
        with patch("ORCHESTRATOR_beta_C68.generation.UnixConnection", Connection), \
                patch.object(module.subprocess, "Popen", graph_worker(graph_result, requests)):
            outcome = jobs._attempt_generation(None, reuse)
        self.assertEqual({"binding": binding, "reuse": reuse, "structure": {"nodes": []}}, requests[0])
        self.assertEqual(("GET", "/structure?instance_id=test+id"), calls[0][:2])
        self.assertEqual("/generation/native", calls[1][1])
        self.assertEqual({"instance_id", "base_generation", "snapshot", "snapshot_sha256", "graph", "graph_sha256", "reuse"},
                         set(calls[1][2]))
        self.assertEqual("graph_refresh", outcome["kind"])
        self.assertEqual({**witness, "base_generation": "new"}, jobs.generation_reuse)
        self.assertEqual(witness, calls[1][2]["reuse"])

    def test_checkpoint_worker_shapes_and_derived_paths(self):
        reuse = {"base_generation": "old", "carrier_hashes": {}}
        hashes = {"control/a.md": "a" * 64}
        delta = {"base_generation": "old", "snapshot": {}, "snapshot_sha256": "s",
                 "paths": [["control/__TKT", "AN-T-1--a.md"]], "carrier_hashes": hashes}
        self.assertEqual(delta, module.parse_worker_result(json.dumps(delta), reuse, None))
        unchanged = {"base_generation": "old", "unchanged": True}
        self.assertEqual(unchanged, module.parse_worker_result(json.dumps(unchanged), reuse, None))
        for paths in ([], [["../outside", "a"]], [["control", "../a"]], [["/root", "a"]],
                      [["control", "a"], ["control", "a"]]):
            with self.assertRaises(ValueError):
                module.parse_worker_result(json.dumps(delta | {"paths": paths}), reuse, None)
        for invalid in (unchanged | {"unchanged": False}, unchanged | {"carrier_hashes": {}},
                        unchanged | {"base_generation": "stale"}):
            with self.assertRaises(ValueError):
                module.parse_worker_result(json.dumps(invalid), reuse, None)
        with self.assertRaises(ValueError):
            module.parse_worker_result(json.dumps(unchanged), {"base_generation": "old"}, None)

    def test_unchanged_confirms_base_and_drops_checkpoint(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        (root / "control").mkdir()
        binding = {"root": str(root), "control_root": "control", "manifest_path": "manifest.md",
                   "manifest_sha256": "a" * 64, "project_prefix": "AN"}
        jobs = module.GenerationJobs("test", binding, "socket")
        reuse = {"base_generation": "old", "inputs": {}, "graph_config": None, "endpoints": {},
                 "carrier_hashes": {"control/a.md": "a" * 64}}
        calls = []
        class Connection:
            def __init__(self, path): pass
            def request(self, method, path): calls.append((method, path))
            def getresponse(self):
                class Response:
                    status = 200
                    def read(self): return json.dumps({"result": reuse}).encode()
                return Response()
            def close(self): pass
        result = {"base_generation": "old", "unchanged": True}
        with patch("ORCHESTRATOR_beta_C68.generation.UnixConnection", Connection), \
                patch.object(jobs, "_run_worker", return_value=result):
            outcome = jobs._attempt_generation(None, reuse)
        self.assertEqual("reused", outcome["kind"])
        self.assertEqual([("GET", "/generation/reuse?instance_id=test")], calls)
        self.assertNotIn("carrier_hashes", jobs.generation_reuse)
        reuse["base_generation"] = "new"
        with patch("ORCHESTRATOR_beta_C68.generation.UnixConnection", Connection), \
                patch.object(jobs, "_run_worker", return_value=result):
            with self.assertRaises(module.GenerationBaseChanged):
                jobs._attempt_generation(None, reuse)

    def test_graph_refresh_result_validation(self):
        witness = {"inputs": {}, "graph_config": {}, "endpoints": {}}
        reuse = {**witness, "base_generation": "old"}
        graph_result = {"base_generation": "old", "snapshot": {}, "snapshot_sha256": "s",
                        "graph": {}, "graph_sha256": "g", "reuse": witness}
        for invalid in (graph_result | {"reuse": None}, graph_result | {"reuse": witness | {"extra": 1}},
                        graph_result | {"base_generation": "other"}):
            with self.assertRaises(ValueError):
                module.parse_worker_result(json.dumps(invalid), reuse, None, {})
        with self.assertRaises(ValueError):
            module.parse_worker_result(json.dumps(graph_result), reuse, None)

    def test_structure_fallback_for_unavailable_or_invalid_artifact(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        (root / "control").mkdir()
        binding = {"root": str(root), "control_root": "control", "manifest_path": "manifest.md",
                   "manifest_sha256": "a" * 64, "project_prefix": "AN"}
        jobs = module.GenerationJobs("id", binding, "socket")
        reuse = {"base_generation": "old", "graph_config": {}}
        requests = []
        class Response:
            status = 200
            header = "old"
            body = b'{}'
            def getheader(self, name): return self.header
            def read(self): return self.body
        class Connection:
            def __init__(self, path): pass
            def request(self, *args): pass
            def getresponse(self): return response
            def close(self): pass
        class Worker:
            returncode = 0
            def __init__(self, *args, **kwargs): pass
            def communicate(self, value=None, timeout=None):
                requests.append(json.loads(value))
                return json.dumps({"base_generation": "old", "snapshot": {}, "snapshot_sha256": "s"}), ""
        response = Response()
        with patch("ORCHESTRATOR_beta_C68.generation.UnixConnection", Connection), \
                patch.object(module.subprocess, "Popen", Worker):
            jobs._run_worker(str(root), reuse, None)
            self.assertEqual({}, requests[-1]["structure"])
            for status, header, body in ((409, "old", b'{}'), (200, "other", b'{}'),
                                         (200, None, b'{}'), (200, "old", b'[]'), (200, "old", b'{')):
                response.status, response.header, response.body = status, header, body
                jobs._run_worker(str(root), reuse, None)
                self.assertNotIn("structure", requests[-1])
            jobs._run_worker(str(root), reuse | {"graph_config": None}, None)
            self.assertNotIn("structure", requests[-1])
        with patch("ORCHESTRATOR_beta_C68.generation.UnixConnection", side_effect=OSError("offline")), \
                patch.object(module.subprocess, "Popen", Worker):
            jobs._run_worker(str(root), reuse, None)
            self.assertNotIn("structure", requests[-1])

