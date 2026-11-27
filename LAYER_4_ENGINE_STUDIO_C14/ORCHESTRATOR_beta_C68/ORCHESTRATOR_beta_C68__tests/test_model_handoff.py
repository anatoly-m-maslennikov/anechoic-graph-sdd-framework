import json
import unittest
from unittest.mock import patch

from ORCHESTRATOR_beta_C68.ORCHESTRATOR_beta_C68__shared import GenerationJobs


class ModelHandoffTests(unittest.TestCase):
    def setUp(self):
        binding = {"root": "/tmp", "control_root": "control", "manifest_path": "manifest.md",
                   "manifest_sha256": "a" * 64, "project_prefix": "AN"}
        self.jobs = GenerationJobs("test", binding, "/tmp/kernel.sock")
        self.enterContext(patch("ORCHESTRATOR_beta_C68.generation_worker.read_accepted_model", return_value=None))

    def test_compiler_refresh_uses_conditional_admission(self):
        witness = {"inputs": {"carrier_schema": "a" * 64}, "graph_config": None, "endpoints": {}}
        reuse = {**witness, "base_generation": "old", "carrier_hashes": {}, "folder_hashes": {}}
        reply = {"base_generation": "old", "compiler": {"receipt": {}, "model": "{}", "structure": "{}"},
                 "reuse": witness}
        self.jobs.startup_capture = True
        with (
            patch.object(self.jobs, "_communicate_worker", return_value=json.dumps(reply)) as worker,
            patch.object(self.jobs.watcher, "capture_epoch", return_value="epoch"),
            patch.object(self.jobs.watcher, "capture_fence", return_value=True),
            patch.object(self.jobs.watcher, "archive_roots", return_value=()),
            patch("ORCHESTRATOR_beta_C68.generation.UnixConnection") as connected,
        ):
            connection = connected.return_value
            response = connection.getresponse.return_value
            response.status = 200
            response.read.return_value = b'{"result": {"generation": "new"}}'
            result = self.jobs._attempt_generation(None, reuse)
            self.assertEqual("compiler_refresh", result["kind"])
            self.assertEqual("new", self.jobs.generation_reuse.base_generation)
            request = next(call.args for call in connection.request.call_args_list if call.args[0] == "PUT")
            self.assertEqual(("PUT", "/generation/compiler"), request[:2])
            self.assertEqual({"instance_id": "test", **reply}, json.loads(request[2]))
            self.assertTrue(worker.call_args.args[1]["incremental"])
            self.jobs.startup_capture = True
            worker.return_value = json.dumps(reply | {"base_generation": "stale"})
            with self.assertRaisesRegex(ValueError, "unexpected compiler generation base"):
                self.jobs._attempt_generation(None, reuse)

    def test_only_model_and_all_targets_force_model(self):
        for target in (None, "atoms", "all", "model_tree", "mrt_model_properties"):
            with self.subTest(target=target), \
                    patch.object(self.jobs, "_capture_generation", side_effect=ValueError("stop")) as capture:
                with self.assertRaisesRegex(ValueError, "stop"):
                    self.jobs._attempt_generation(target, None)
                self.assertEqual(target in {"all", "model_tree", "mrt_model_properties"},
                                 capture.call_args.kwargs["force_model"])

    def test_only_full_worker_reply_accepts_diagnostics(self):
        full = {"snapshot": {}, "receipt": {}, "graph": None, "reuse": None, "model_diagnostics": []}
        with patch.object(self.jobs, "_communicate_worker", return_value=json.dumps(full)) as worker:
            self.assertEqual(full, self.jobs._run_worker("/tmp", None, None))
            for value in (None, {}, "bad"):
                worker.return_value = json.dumps(full | {"model_diagnostics": value})
                with self.assertRaises(ValueError):
                    self.jobs._run_worker("/tmp", None, None)
            worker.return_value = json.dumps({"base_generation": "g", "snapshot": {}, "snapshot_sha256": "x",
                                              "model_diagnostics": []})
            with self.assertRaises(ValueError):
                self.jobs._run_worker("/tmp", {"base_generation": "g"}, None)

    def test_failure_forwards_build_diagnostics(self):
        issues = [{"code": "failed"}]
        diagnostics = [{"code": "invalid_model_source"}]
        payload = {"ingestion_failure": {"source": "build", "issues": issues}, "model_diagnostics": diagnostics}
        with patch("ORCHESTRATOR_beta_C68.generation_worker.subprocess.Popen") as popen:
            popen.return_value.returncode = 1
            popen.return_value.communicate.return_value = (json.dumps(payload), "failure")
            with self.assertRaises(RuntimeError) as error:
                self.jobs._communicate_worker("/tmp", {})
        with patch.object(self.jobs, "_record_ingestion_issues") as send:
            self.jobs._record_ingestion_failure(error.exception)
        send.assert_called_once_with("build", issues, model_diagnostics=diagnostics)


class ModelSourceTests(unittest.TestCase):
    def test_force_model_is_only_sent_when_requested(self):
        binding = {"root": "/tmp", "control_root": "control", "manifest_path": "manifest.md",
                   "manifest_sha256": "a" * 64, "project_prefix": "AN"}
        jobs = GenerationJobs("test", binding, "/tmp/kernel.sock")
        reply = {"snapshot": {}, "receipt": {}, "graph": None, "reuse": None}
        with patch("ORCHESTRATOR_beta_C68.generation_worker.read_accepted_model", return_value={}), \
                patch.object(jobs, "_communicate_worker", return_value=json.dumps(reply)) as worker:
            jobs._run_worker("/tmp", None, None, force_model=True)
            self.assertTrue(worker.call_args.args[1]["model_source"]["force_rebuild"])
            jobs._run_worker("/tmp", None, None)
            self.assertNotIn("force_rebuild", worker.call_args.args[1]["model_source"])

    def test_startup_passes_kernel_model_before_worker_runs(self):
        binding = {"root": "/tmp", "control_root": "control", "manifest_path": "manifest.md",
                   "manifest_sha256": "a" * 64, "project_prefix": "AN"}
        jobs = GenerationJobs("test", binding, "/tmp/kernel.sock")
        accepted = {"descriptor": "from kernel"}
        reply = {"snapshot": {}, "receipt": {}, "graph": None, "reuse": None}
        with patch("ORCHESTRATOR_beta_C68.generation_worker.read_accepted_model", return_value=accepted) as read, \
                patch.object(jobs, "_communicate_worker", return_value=json.dumps(reply)) as worker:
            jobs._run_worker("/tmp", None, None)
            read.assert_called_once_with("/tmp/kernel.sock", "test")
            self.assertEqual({"accepted_model": accepted,
                              "spec_database": {"socket": "/tmp/kernel.sock", "instance_id": "test"}},
                             worker.call_args.args[1]["model_source"])
