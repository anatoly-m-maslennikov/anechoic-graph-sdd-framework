"""Restart checkpoint test cases."""

import importlib
import json
import tempfile
from unittest.mock import patch

from ORCHESTRATOR_beta_C68 import ORCHESTRATOR_beta_C68__shared as module
from ...ORCHESTRATOR_beta_C68__tests__shared import lifecycle_job, restore_reuse
from ORCHESTRATOR_beta_C68.ORCHESTRATOR_beta_C68__tests.generation.restart.restart_checkpoint_test_support import _reuse_connection


class RestartLifecycleCases:
    def _indexed_job(self, template, **options):
        jobs = self._jobs(**options)
        restore_reuse(jobs, "base")
        jobs.generation_reuse.status_domains = {
            "S": ["active"],
            "T": ["active"],
            "P": ["active"],
            "C": ["active"],
        }
        job = lifecycle_job(
            jobs,
            "atom_lifecycle_create_draft",
            {
                "newAtom": {
                    "template": template,
                    "container": {"component": "C00"},
                },
            },
        )
        return jobs, job

    def test_warm_dispatch_only_marks_unknown_after_possible_write(self):
        jobs, job = self._indexed_job(
            "epic", worker_socket="worker", worker_load_seconds=1
        )
        structure = {"components": {}, "project": {"ref": "AN-S-1@1"}}
        lifecycle = importlib.import_module("ORCHESTRATOR_beta_C68.lifecycle.lifecycle")
        for error, expected in (
            (lifecycle.WarmLifecycleUnavailable("Worker refused"), "known"),
            (ValueError("Worker closed the connection"), "unknown"),
        ):
            with (
                self.subTest(expected=expected),
                patch.object(
                    lifecycle, "read_structure", return_value=structure
                ),
                patch.object(
                    lifecycle, "ticket_allocation", return_value=("1", [])
                ),
                patch.object(
                    lifecycle, "run_lifecycle", side_effect=error
                ) as worker,
                patch.object(jobs, "_run_cold_lifecycle") as cold,
            ):
                self.assertEqual(
                    expected, jobs._execute_lifecycle(job)["write_state"]
                )
                self.assertEqual(
                    expected == "unknown", jobs.unconfirmed_lifecycle_write
                )
                worker.assert_called_once()
                cold.assert_not_called()

    def test_unadmitted_write_blocks_second_indexed_allocation(self):
        jobs, job = self._indexed_job("task")
        structure = {"components": {}, "project": {"ref": "AN-S-1@1"}}
        reply = {
            "lifecycle": {
                "outcome": "failed",
                "effects": [],
                "errors": [{"code": "effect_uncertain"}],
            },
            "projection_error": "Kernel refused delta",
            "delta": None,
        }
        with (
            patch(
                "ORCHESTRATOR_beta_C68.lifecycle.lifecycle.read_structure",
                return_value=structure,
            ),
            patch(
                "ORCHESTRATOR_beta_C68.lifecycle.lifecycle.ticket_allocation",
                return_value=("1", []),
            ) as lookup,
            patch.object(
                jobs, "_run_cold_lifecycle", return_value=reply
            ) as worker,
        ):
            self.assertEqual(
                "failed", jobs._execute_lifecycle(job)["projection"]["state"]
            )
            jobs.generation_reuse.base_generation = "unrelated-admission"
            refusal = jobs._execute_lifecycle(job)
        self.assertEqual("known", refusal["write_state"])
        self.assertEqual("blocked", refusal["lifecycle"]["outcome"])
        self.assertEqual(
            "write_blocked", refusal["lifecycle"]["errors"][0]["code"]
        )
        self.assertEqual("blocked", refusal["projection"]["state"])
        lookup.assert_called_once()
        worker.assert_called_once()

    def test_admission_flow_records_whether_reuse_proof_is_required(self):
        with tempfile.TemporaryDirectory() as root:
            binding = {
                "root": root,
                "control_root": ".",
                "manifest_path": "m",
                "manifest_sha256": "hash",
                "project_prefix": "AN",
            }
            jobs = module.GenerationJobs("test", binding, "socket")
            witness = {"inputs": {}, "graph_config": None, "endpoints": {}}
            for result, reuse, expected in (
                ({"reuse": witness}, None, True),
                ({"reuse": None}, None, False),
                ({}, witness, True),
            ):
                with (
                    self.subTest(result=result, reuse=reuse),
                    patch.object(
                        jobs, "_run_worker", return_value=result.copy()
                    ),
                    patch.object(
                        module,
                        "admit_generation",
                        return_value={"generation": "new"},
                    ),
                    patch.object(jobs, "_flow_effect") as effect,
                ):
                    jobs._attempt_generation(None, reuse)
                effect.assert_any_call(
                    "generation_admission",
                    outcome="succeeded",
                    detail={"reuse_proof_present": expected},
                )
            self._assert_unchanged_proof(jobs)

    def _assert_unchanged_proof(self, jobs):
        with (
            patch.object(
                jobs, "_run_worker", return_value={"unchanged": True}
            ),
            patch.object(
                module, "confirm_reuse", return_value={"generation": "new"}
            ),
            patch.object(jobs, "_flow_effect") as effect,
        ):
            jobs._attempt_generation(None, None)
        effect.assert_called_once_with(
            "generation_reuse_check", outcome="succeeded"
        )

    def _startup_generate(self, jobs, reuse, witness, *args, **kwargs):
        self.assertTrue(jobs.watcher.started)
        self.assertEqual(
            reuse, jobs.generation_reuse.model_dump(exclude_unset=True)
        )
        self.assertEqual({"startup": True}, kwargs)
        self.assertFalse(jobs.watcher.has_archive_roots())
        self.assertTrue(jobs._capture_options(reuse, None)[0]["foreground"])
        reply = {"base_generation": "old", "unchanged": True}
        with patch.object(
            jobs, "_communicate_worker", return_value=json.dumps(reply)
        ) as worker:
            self.assertEqual(
                reply, jobs._run_worker(jobs.binding["root"], reuse, None)
            )
        self.assertEqual(witness, worker.call_args.args[1]["reuse"])
        jobs.stopping.set()
        return {"state": "succeeded"}

    def test_startup_reconciles_persisted_pending_after_archive_tree_removed(
        self,
    ):
        jobs = self._jobs("test id")
        witness = {
            "base_generation": "old",
            "inputs": {},
            "graph_config": None,
            "endpoints": {},
            "carrier_hashes": {"control/a.md": "a" * 64},
        }
        reuse = witness | {
            "archive_pending": True,
            "checkpoint_scope": "foreground",
        }
        calls = []

        Connection = _reuse_connection(reuse, calls)

        def generate(*args, **kwargs):
            return self._startup_generate(
                jobs, reuse, witness, *args, **kwargs
            )

        with (
            patch(
                "ORCHESTRATOR_beta_C68.generation.generation.UnixConnection", Connection
            ),
            patch.object(jobs, "_generate", side_effect=generate),
            patch.object(
                jobs.watcher,
                "start",
                side_effect=lambda: setattr(jobs.watcher, "started", True),
            ),
        ):
            jobs.start()
            jobs.thread.join(5)
        self.assertFalse(jobs.thread.is_alive())
        self.assertEqual(
            [
                (
                    "GET",
                    "/generation/reuse?instance_id=test+id&scope=foreground",
                )
            ],
            calls,
        )
