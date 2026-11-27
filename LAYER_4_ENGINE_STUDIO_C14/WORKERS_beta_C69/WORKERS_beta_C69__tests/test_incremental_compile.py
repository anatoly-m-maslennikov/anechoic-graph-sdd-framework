import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from WORKERS_beta_C69 import WORKERS_beta_C69__shared as worker


class IncrementalCompileTests(unittest.TestCase):
    def test_managed_refresh_uses_ingested_model_selection(self):
        reuse = {"base_generation": "base", "inputs": {"manifest": "old", "carrier_schema": "s"},
                 "endpoints": {}, "graph_config": None}
        source = {"accepted_model": {"model_inputs_sha256": "accepted"}}
        request = {"binding": {}, "reuse": reuse, "incremental": True, "foreground": True,
                   "watcher_guarded": True, "defer_graph": True, "model_source": source}
        with tempfile.TemporaryDirectory() as directory, \
                patch("WORKERS_beta_C69.native_refresh.artifact_inputs",
                      return_value={"manifest": "new", "carrier_schema": "s"}), \
                patch.object(worker, "_compile", side_effect=AssertionError("file-scanning compile")), \
                patch.object(worker, "build_generation", return_value={"built": True}) as build:
            self.assertEqual({"built": True}, worker._run(request, Path(directory) / "output"))
        self.assertEqual(source, build.call_args.kwargs["model_source"])

    def test_run_compiles_before_capture_and_uses_candidate_endpoints(self):
        old = {"manifest": "old", "carrier_schema": "schema", "graph": "pending"}
        new = {**old, "manifest": "new"}
        reuse = {"base_generation": "base", "inputs": old, "endpoints": {"old": 1},
                 "graph_config": None}
        request = {"binding": {}, "reuse": reuse, "incremental": True, "foreground": True,
                   "watcher_guarded": True, "defer_graph": True}
        receipt = {"manifest_sha256": "m", "model_sha256": "a",
                   "model_descriptor_sha256": "b", "structure_sha256": "c"}
        delta = {"base_generation": "base", "paths": ["x"], "snapshot": {},
                 "snapshot_sha256": "hash", "carrier_hashes": {}}

        def compile_model(binding, stage):
            (stage / "model.json").write_text('{"model":1}')
            (stage / "structure.json").write_text('{"structure":1}')
            return receipt, {}, {"new": 1}

        with tempfile.TemporaryDirectory() as directory, \
                patch("WORKERS_beta_C69.native_refresh.artifact_inputs", return_value=new), \
                patch.object(worker, "_compile", side_effect=compile_model), \
                patch("WORKERS_beta_C69.native_refresh.startup_incremental", return_value=delta) as incremental, \
                patch.object(worker, "build_generation", side_effect=AssertionError("full capture")):
            result = worker._run(request, Path(directory) / "output")
            incremental.return_value = {"base_generation": "base", "unchanged": True}
            unchanged = worker._run(request, Path(directory) / "output")
        self.assertNotIn("delta", unchanged)
        self.assertEqual({"new": 1}, incremental.call_args.args[1].endpoints)
        self.assertEqual(new, incremental.call_args.kwargs["before"])
        self.assertEqual({"receipt": receipt, "model": '{"model":1}',
                          "structure": '{"structure":1}'}, result["compiler"])
        self.assertEqual({key: value for key, value in delta.items() if key != "base_generation"},
                         result["delta"])
        self.assertEqual(new, result["reuse"]["inputs"])

    def test_compile_failure_propagates(self):
        reuse = {"base_generation": "base", "inputs": {"manifest": "old", "carrier_schema": "s"},
                 "endpoints": {}, "graph_config": None}
        request = {"binding": {}, "reuse": reuse, "incremental": True, "foreground": True,
                   "watcher_guarded": True, "defer_graph": True}
        with tempfile.TemporaryDirectory() as directory, \
                patch("WORKERS_beta_C69.native_refresh.artifact_inputs",
                      return_value={"manifest": "new", "carrier_schema": "s"}), \
                patch.object(worker, "_compile", side_effect=ValueError("compile failed")), \
                patch.object(worker, "build_generation", side_effect=AssertionError("full capture")):
            with self.assertRaisesRegex(ValueError, "compile failed"):
                worker._run(request, Path(directory) / "output")
