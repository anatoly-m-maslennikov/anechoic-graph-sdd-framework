import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from WORKERS_beta_C69 import WORKERS_beta_C69__shared as worker


class IncrementalCompileTests(unittest.TestCase):
    def _managed_request(self):
        reuse = {
            "base_generation": "base",
            "inputs": {"manifest": "old", "carrier_schema": "s"},
            "endpoints": {},
            "graph_config": None,
        }
        source = {
            "accepted_model": {"model_inputs_sha256": "accepted"},
            "spec_database": {"socket": "socket", "instance_id": "id"},
        }
        return {
            "binding": {},
            "reuse": reuse,
            "incremental": True,
            "foreground": True,
            "watcher_guarded": True,
            "defer_graph": True,
            "model_source": source,
        }

    def test_managed_refresh_uses_ingested_model_selection(self):
        request = self._managed_request()
        source = request["model_source"]
        inputs, finish = {"spec_rows": ["admitted"]}, object()
        receipt = {"manifest_sha256": "m"}

        def compile_capture(binding, stage, captured, selected, finalizer):
            self.assertIs(inputs, captured)
            self.assertEqual(source, selected)
            self.assertIs(finish, finalizer)
            (stage / "model.json").write_text('{"bindings":{}}')
            (stage / "structure.json").write_text("{}")
            return (receipt, {}, {"new": 1}, []), None

        with (
            tempfile.TemporaryDirectory() as directory,
            patch(
                "WORKERS_beta_C69.refresh.native_refresh.artifact_inputs",
                return_value={"manifest": "new", "carrier_schema": "s"},
            ),
            patch.object(
                worker,
                "_compile",
                side_effect=AssertionError("file-scanning compile"),
            ),
            patch(
                "WORKERS_beta_C69.generation.worker_generation._prepare_generation",
                return_value=(None, None, None, finish, inputs, None),
            ),
            patch.object(
                worker, "_compile_and_capture", side_effect=compile_capture
            ),
            patch(
                "WORKERS_beta_C69.refresh.native_refresh.startup_incremental",
                return_value={"base_generation": "base", "unchanged": True},
            ),
            patch.object(
                worker,
                "build_generation",
                side_effect=AssertionError("full capture"),
            ),
        ):
            result = worker._run(request, Path(directory) / "output")
        self.assertEqual(receipt, result["compiler"]["receipt"])
        self.assertEqual({"new": 1}, result["reuse"]["endpoints"])

    def test_managed_model_diagnostics_force_full_generation(self):
        request = self._managed_request()
        with (
            tempfile.TemporaryDirectory() as directory,
            patch(
                "WORKERS_beta_C69.refresh.native_refresh.artifact_inputs",
                return_value={"manifest": "new", "carrier_schema": "s"},
            ),
            patch.object(
                worker,
                "_compile_managed_refresh",
                return_value=({}, {}, {}, [{"code": "invalid_model_source"}]),
            ),
            patch.object(
                worker, "build_generation", return_value={"built": True}
            ) as build,
        ):
            result = worker._run(request, Path(directory) / "output")
        self.assertEqual({"built": True}, result)
        self.assertEqual(
            request["model_source"], build.call_args.kwargs["model_source"]
        )

    def test_changed_status_domains_force_full_generation(self):
        request = self._managed_request()
        request["reuse"]["status_domains"] = {
            key: ["old"] for key in ("S", "T", "P", "C")
        }

        def compile_model(output, source, domains, capture, binding, stage):
            (stage / "model.json").write_text('{"bindings":{}}')
            (stage / "structure.json").write_text("{}")
            return {}, {}, {}, []

        with (
            tempfile.TemporaryDirectory() as directory,
            patch(
                "WORKERS_beta_C69.refresh.native_refresh.artifact_inputs",
                return_value={"manifest": "new", "carrier_schema": "s"},
            ),
            patch.object(worker, "_compile_managed_refresh", compile_model),
            patch.object(
                worker, "build_generation", return_value={"full": True}
            ),
        ):
            result = worker._run(request, Path(directory) / "output")
        self.assertEqual({"full": True}, result)

    def test_run_compiles_before_capture_and_uses_candidate_endpoints(self):
        # fmt: off
        old = {"manifest": "old", "carrier_schema": "schema",
               "graph": "pending"}
        new = {**old, "manifest": "new"}
        reuse = {"base_generation": "base", "inputs": old,
                 "endpoints": {"old": 1}, "graph_config": None}
        request = {"binding": {}, "reuse": reuse, "incremental": True,
                   "foreground": True, "watcher_guarded": True,
                   "defer_graph": True}
        receipt = {"manifest_sha256": "m", "model_sha256": "a",
                   "model_descriptor_sha256": "b", "structure_sha256": "c"}
        delta = {"base_generation": "base", "paths": ["x"], "snapshot": {},
                 "snapshot_sha256": "hash", "carrier_hashes": {}}

        def compile_model(binding, stage):
            (stage / "model.json").write_text('{"model":1,"bindings":{}}')
            (stage / "structure.json").write_text('{"structure":1}')
            return receipt, {}, {"new": 1}

        with (tempfile.TemporaryDirectory() as directory,
              patch("WORKERS_beta_C69.refresh.native_refresh.artifact_inputs",
                    return_value=new),
              patch.object(worker, "_compile", side_effect=compile_model),
              patch("WORKERS_beta_C69.refresh.native_refresh.startup_incremental",
                    return_value=delta) as incremental,
              patch.object(worker, "build_generation",
                           side_effect=AssertionError("full capture"))):
            result = worker._run(request, Path(directory) / "output")
            incremental.return_value = {"base_generation": "base",
                                        "unchanged": True}
            unchanged = worker._run(request, Path(directory) / "output")
        self.assertNotIn("delta", unchanged)
        self.assertEqual({"new": 1}, incremental.call_args.args[1].endpoints)
        self.assertEqual(new, incremental.call_args.kwargs["before"])
        self.assertEqual({"receipt": receipt,
                          "model": '{"model":1,"bindings":{}}',
                          "structure": '{"structure":1}'}, result["compiler"])
        self.assertEqual({key: value for key, value in delta.items()
                          if key != "base_generation"}, result["delta"])
        self.assertEqual(new, result["reuse"]["inputs"])
        # fmt: on

    def test_compile_failure_propagates(self):
        reuse = {
            "base_generation": "base",
            "inputs": {"manifest": "old", "carrier_schema": "s"},
            "endpoints": {},
            "graph_config": None,
        }
        request = {
            "binding": {},
            "reuse": reuse,
            "incremental": True,
            "foreground": True,
            "watcher_guarded": True,
            "defer_graph": True,
        }
        with (
            tempfile.TemporaryDirectory() as directory,
            patch(
                "WORKERS_beta_C69.refresh.native_refresh.artifact_inputs",
                return_value={"manifest": "new", "carrier_schema": "s"},
            ),
            patch.object(
                worker, "_compile", side_effect=ValueError("compile failed")
            ),
            patch.object(
                worker,
                "build_generation",
                side_effect=AssertionError("full capture"),
            ),
        ):
            with self.assertRaisesRegex(ValueError, "compile failed"):
                worker._run(request, Path(directory) / "output")
