from ORCHESTRATOR_beta_C68.ORCHESTRATOR_beta_C68__tests.generation.restart.restart_lifecycle_cases import RestartLifecycleCases
from ORCHESTRATOR_beta_C68.ORCHESTRATOR_beta_C68__tests.generation.restart.restart_graph_cases import RestartGraphCases
from ORCHESTRATOR_beta_C68.ORCHESTRATOR_beta_C68__tests.generation.restart.restart_checkpoint_cases import RestartCheckpointCases
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from ORCHESTRATOR_beta_C68 import ORCHESTRATOR_beta_C68__shared as module


def graph_worker(result, requests):
    class Worker:
        returncode = 0

        def __init__(self, *args, **kwargs):
            pass

        def communicate(self, value=None, timeout=None):
            requests.append(json.loads(value))
            return json.dumps(result), ""

    return Worker


class RestartCheckpointTests(
    RestartLifecycleCases,
    RestartGraphCases,
    RestartCheckpointCases,
    unittest.TestCase,
):
    def setUp(self):
        model = patch(
            "ORCHESTRATOR_beta_C68.generation.worker.generation_worker.read_accepted_model",
            return_value=None,
        )
        model.start()
        self.addCleanup(model.stop)

    def _jobs(self, instance_id="test", **options):
        root = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        (root / "control").mkdir()
        binding = {
            "root": str(root),
            "control_root": "control",
            "manifest_path": "manifest.md",
            "manifest_sha256": "a" * 64,
            "project_prefix": "AN",
        }
        return module.GenerationJobs(
            instance_id, binding, str(root / "kernel.sock"), **options
        )

    def test_startup_revalidates_and_retries_stale_base(self):
        jobs = self._jobs()
        reuse = {
            "base_generation": "old",
            "inputs": {},
            "graph_config": None,
            "endpoints": {},
        }
        jobs.generation_reuse = reuse
        with patch.object(
            jobs,
            "_attempt_generation",
            side_effect=[
                module.GenerationBaseChanged(),
                {"state": "succeeded", "generation": "new"},
            ],
        ) as attempt:
            self.assertEqual(
                "succeeded", jobs._generate(startup=True)["state"]
            )
        self.assertEqual(
            [(None, reuse, None), (None, None)],
            [call.args for call in attempt.call_args_list],
        )
        jobs.generation_reuse = reuse
        with patch.object(
            jobs, "_attempt_generation", return_value={"state": "succeeded"}
        ) as attempt:
            jobs._generate()
        self.assertIsNone(attempt.call_args.args[1])

    def test_checkpoint_worker_shapes_and_derived_paths(self):
        jobs = self._jobs()
        root = jobs.binding["root"]
        reuse = {"base_generation": "old", "carrier_hashes": {}}
        hashes = {"control/a.md": "a" * 64}
        delta = {
            "base_generation": "old",
            "snapshot": {},
            "snapshot_sha256": "s",
            "paths": [["control/__TKT", "AN-T-1--a.md"]],
            "carrier_hashes": hashes,
        }
        unchanged = {"base_generation": "old", "unchanged": True}
        bad_paths = (
            [],
            [["../outside", "a"]],
            [["control", "../a"]],
            [["/root", "a"]],
            [["control", "a"], ["control", "a"]],
        )
        invalid = [delta | {"paths": paths} for paths in bad_paths]
        invalid.extend(
            (
                unchanged | {"unchanged": False},
                unchanged | {"carrier_hashes": {}},
                unchanged | {"base_generation": "stale"},
            )
        )
        with patch.object(jobs, "_communicate_worker") as worker:
            for result in (delta, unchanged):
                worker.return_value = json.dumps(result)
                self.assertEqual(result, jobs._run_worker(root, reuse, None))
            for result in invalid:
                worker.return_value = json.dumps(result)
                with (
                    self.subTest(result=result),
                    self.assertRaises(ValueError),
                ):
                    jobs._run_worker(root, reuse, None)
            worker.return_value = json.dumps(unchanged)
            with self.assertRaises(ValueError):
                jobs._run_worker(root, {"base_generation": "old"}, None)

    def test_graph_refresh_result_validation(self):
        jobs = self._jobs()
        root = jobs.binding["root"]
        witness = {"inputs": {}, "graph_config": {}, "endpoints": {}}
        reuse = {"base_generation": "old"}
        graph_result = {
            "base_generation": "old",
            "snapshot": {},
            "snapshot_sha256": "s",
            "graph": {},
            "graph_sha256": "g",
            "reuse": witness,
        }
        with patch.object(jobs, "_communicate_worker") as worker:
            for invalid in (
                graph_result | {"reuse": None},
                graph_result | {"reuse": witness | {"extra": 1}},
                graph_result | {"base_generation": "other"},
            ):
                worker.return_value = json.dumps(invalid)
                with (
                    self.subTest(result=invalid),
                    self.assertRaises(ValueError),
                ):
                    jobs._run_worker(root, reuse, None, structure={})
            worker.return_value = json.dumps(graph_result)
            with self.assertRaises(ValueError):
                jobs._run_worker(root, reuse, None)
