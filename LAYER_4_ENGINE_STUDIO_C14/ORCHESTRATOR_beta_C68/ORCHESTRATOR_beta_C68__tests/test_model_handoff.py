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
