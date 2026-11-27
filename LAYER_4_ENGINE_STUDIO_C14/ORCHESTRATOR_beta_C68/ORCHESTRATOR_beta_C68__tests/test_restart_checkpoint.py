from .restart_checkpoint_cases import RestartCheckpointCases
import subprocess
import importlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from ORCHESTRATOR_beta_C68 import ORCHESTRATOR_beta_C68__shared as module
from .ORCHESTRATOR_beta_C68__tests__shared import lifecycle_job, restore_reuse


def graph_worker(result, requests):
    class Worker:
        returncode = 0
        def __init__(self, *args, **kwargs): pass
        def communicate(self, value=None, timeout=None):
            requests.append(json.loads(value))
            return json.dumps(result), ""
    return Worker


class RestartCheckpointTests(RestartCheckpointCases, unittest.TestCase):
    def setUp(self):
        model = patch("ORCHESTRATOR_beta_C68.generation_worker.read_accepted_model", return_value=None)
        model.start()
        self.addCleanup(model.stop)

    def _jobs(self, instance_id="test", **options):
        root = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        (root / "control").mkdir()
        binding = {"root": str(root), "control_root": "control", "manifest_path": "manifest.md",
                   "manifest_sha256": "a" * 64, "project_prefix": "AN"}
        return module.GenerationJobs(instance_id, binding, str(root / "kernel.sock"), **options)

    def test_warm_dispatch_only_marks_unknown_after_possible_write(self):
        jobs = self._jobs(worker_socket="worker", worker_load_seconds=1)
        restore_reuse(jobs, "base")
        jobs.generation_reuse.status_domains = {"S": ["active"], "T": ["active"], "P": ["active"], "C": ["active"]}
        job = lifecycle_job(jobs, "atom_lifecycle_create_draft", {
            "newAtom": {"template": "epic", "container": {"component": "C00"}}})
        structure = {"components": {}, "project": {"ref": "AN-S-1@1"}}
        lifecycle = importlib.import_module("ORCHESTRATOR_beta_C68.lifecycle")
        for error, expected in ((lifecycle.WarmLifecycleUnavailable("Worker refused"), "known"),
                                (ValueError("Worker closed the connection"), "unknown")):
            with self.subTest(expected=expected), patch.object(lifecycle, "read_structure", return_value=structure), \
                    patch.object(lifecycle, "ticket_allocation", return_value=("1", [])), \
                    patch.object(lifecycle, "run_lifecycle", side_effect=error) as worker, \
                    patch.object(jobs, "_run_cold_lifecycle") as cold:
                self.assertEqual(expected, jobs._execute_lifecycle(job)["write_state"])
                self.assertEqual(expected == "unknown", jobs.unconfirmed_lifecycle_write)
                worker.assert_called_once()
                cold.assert_not_called()

    def test_unadmitted_write_blocks_second_indexed_allocation(self):
        jobs = self._jobs()
        restore_reuse(jobs, "base")
        jobs.generation_reuse.status_domains = {"S": ["active"], "T": ["active"], "P": ["active"], "C": ["active"]}
        job = lifecycle_job(jobs, "atom_lifecycle_create_draft", {
            "newAtom": {"template": "task", "container": {"component": "C00"}}})
        structure = {"components": {}, "project": {"ref": "AN-S-1@1"}}
        reply = {"lifecycle": {"outcome": "failed", "effects": [], "errors": [{"code": "effect_uncertain"}]},
                 "projection_error": "Kernel refused delta", "delta": None}
        with patch("ORCHESTRATOR_beta_C68.lifecycle.read_structure", return_value=structure), \
                patch("ORCHESTRATOR_beta_C68.lifecycle.ticket_allocation", return_value=("1", [])) as lookup, \
                patch.object(jobs, "_run_cold_lifecycle", return_value=reply) as worker:
            self.assertEqual("failed", jobs._execute_lifecycle(job)["projection"]["state"])
            jobs.generation_reuse.base_generation = "unrelated-admission"
            refusal = jobs._execute_lifecycle(job)
        self.assertEqual("known", refusal["write_state"])
        self.assertEqual("blocked", refusal["lifecycle"]["outcome"])
        self.assertEqual("write_blocked", refusal["lifecycle"]["errors"][0]["code"])
        self.assertEqual("blocked", refusal["projection"]["state"])
        lookup.assert_called_once()
        worker.assert_called_once()

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

    def test_startup_reconciles_persisted_pending_after_archive_tree_removed(self):
        jobs = self._jobs("test id")
        witness = {"base_generation": "old", "inputs": {}, "graph_config": None, "endpoints": {},
                   "carrier_hashes": {"control/a.md": "a" * 64}}
        reuse = witness | {"archive_pending": True, "checkpoint_scope": "foreground"}
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
            self.assertEqual(reuse, jobs.generation_reuse.model_dump(exclude_unset=True))
            self.assertEqual({"startup": True}, kwargs)
            self.assertFalse(jobs.watcher.has_archive_roots())
            self.assertTrue(jobs._capture_options(reuse, None)[0]["foreground"])
            reply = {"base_generation": "old", "unchanged": True}
            with patch.object(jobs, "_communicate_worker", return_value=json.dumps(reply)) as worker:
                self.assertEqual(reply, jobs._run_worker(jobs.binding["root"], reuse, None))
            self.assertEqual(witness, worker.call_args.args[1]["reuse"])
            jobs.stopping.set()
            return {"state": "succeeded"}
        with patch("ORCHESTRATOR_beta_C68.generation.UnixConnection", Connection), \
                patch.object(jobs, "_generate", side_effect=generate), \
                patch.object(jobs.watcher, "start", side_effect=lambda: setattr(jobs.watcher, "started", True)):
            jobs.start()
            jobs.thread.join(5)
        self.assertFalse(jobs.thread.is_alive())
        self.assertEqual([("GET", "/generation/reuse?instance_id=test+id&scope=foreground")], calls)

    def test_scoped_request_never_falls_back_to_full_checkpoint(self):
        calls = []
        result = {"base_generation": "old", "inputs": {}, "graph_config": None, "endpoints": {}}
        class Connection:
            def __init__(self, path): pass
            def request(self, method, path): calls.append(path)
            def getresponse(self):
                class Response:
                    status = 403 if len(calls) == 1 else 200
                    def read(self): return json.dumps({"result": result}).encode()
                return Response()
            def close(self): pass
        with patch("ORCHESTRATOR_beta_C68.generation.UnixConnection", Connection):
            self.assertIsNone(module.read_reuse("socket", "test", scope="foreground"))
            self.assertIsNone(module.read_reuse("socket", "test", scope="foreground"))
        self.assertEqual(["/generation/reuse?instance_id=test&scope=foreground"] * 2, calls)

    def test_full_admission_persists_worker_witness(self):
        jobs = self._jobs()
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
        def worker(directory, reuse, paths, *, force_model=False):
            self.assertFalse(force_model)
            for name in ("model", "structure"):
                (Path(directory) / (name + ".json")).write_text("{}")
            return {"snapshot": {}, "receipt": {}, "graph": None, "reuse": witness, "model_diagnostics": [], "carrier_hashes": {"control/a.md": "a" * 64}}
        with patch("ORCHESTRATOR_beta_C68.generation.UnixConnection", Connection), \
                patch.object(jobs, "_run_worker", side_effect=worker):
            self.assertEqual("full", jobs._attempt_generation(None, None)["kind"])
        self.assertEqual("/generation", payloads[0][0])
        self.assertEqual(witness, payloads[0][1]["reuse"])
        self.assertEqual([], payloads[0][1]["model_diagnostics"])
        self.assertEqual({"control/a.md": "a" * 64}, payloads[0][1]["carrier_hashes"])

    def test_startup_revalidates_and_retries_stale_base(self):
        jobs = self._jobs()
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
        jobs = self._jobs("test id")
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
                patch.object(subprocess, "Popen", graph_worker(graph_result, requests)):
            outcome = jobs._attempt_generation(None, reuse)
        self.assertEqual({"binding": jobs.binding, "reuse": reuse, "structure": {"nodes": []},
                          "model_source": {"accepted_model": None,
                                           "spec_database": {"socket": str(jobs.database_socket),
                                                             "instance_id": "test id"}}, "batch_full": True}, requests[0])
        self.assertEqual(("GET", "/structure?instance_id=test+id"), calls[0][:2])
        self.assertEqual("/generation/native", calls[1][1])
        self.assertEqual({"instance_id", "base_generation", "snapshot", "snapshot_sha256", "graph", "graph_sha256", "reuse"},
                         set(calls[1][2]))
        self.assertEqual("graph_refresh", outcome["kind"])
        self.assertEqual({**witness, "base_generation": "new"}, jobs.generation_reuse.model_dump(exclude_unset=True))
        self.assertEqual(witness, calls[1][2]["reuse"])

    def test_checkpoint_worker_shapes_and_derived_paths(self):
        jobs = self._jobs()
        root = jobs.binding["root"]
        reuse = {"base_generation": "old", "carrier_hashes": {}}
        hashes = {"control/a.md": "a" * 64}
        delta = {"base_generation": "old", "snapshot": {}, "snapshot_sha256": "s",
                 "paths": [["control/__TKT", "AN-T-1--a.md"]], "carrier_hashes": hashes}
        unchanged = {"base_generation": "old", "unchanged": True}
        bad_paths = ([], [["../outside", "a"]], [["control", "../a"]], [["/root", "a"]],
                     [["control", "a"], ["control", "a"]])
        invalid = [delta | {"paths": paths} for paths in bad_paths]
        invalid.extend((unchanged | {"unchanged": False}, unchanged | {"carrier_hashes": {}},
                        unchanged | {"base_generation": "stale"}))
        with patch.object(jobs, "_communicate_worker") as worker:
            for result in (delta, unchanged):
                worker.return_value = json.dumps(result)
                self.assertEqual(result, jobs._run_worker(root, reuse, None))
            for result in invalid:
                worker.return_value = json.dumps(result)
                with self.subTest(result=result), self.assertRaises(ValueError):
                    jobs._run_worker(root, reuse, None)
            worker.return_value = json.dumps(unchanged)
            with self.assertRaises(ValueError):
                jobs._run_worker(root, {"base_generation": "old"}, None)

    def test_unchanged_confirms_base_and_drops_checkpoint(self):
        jobs = self._jobs()
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
                patch.object(jobs, "_record_ingestion_issues"), \
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
        jobs = self._jobs()
        root = jobs.binding["root"]
        witness = {"inputs": {}, "graph_config": {}, "endpoints": {}}
        reuse = {"base_generation": "old"}
        graph_result = {"base_generation": "old", "snapshot": {}, "snapshot_sha256": "s",
                        "graph": {}, "graph_sha256": "g", "reuse": witness}
        with patch.object(jobs, "_communicate_worker") as worker:
            for invalid in (graph_result | {"reuse": None}, graph_result | {"reuse": witness | {"extra": 1}},
                            graph_result | {"base_generation": "other"}):
                worker.return_value = json.dumps(invalid)
                with self.subTest(result=invalid), self.assertRaises(ValueError):
                    jobs._run_worker(root, reuse, None, structure={})
            worker.return_value = json.dumps(graph_result)
            with self.assertRaises(ValueError):
                jobs._run_worker(root, reuse, None)
