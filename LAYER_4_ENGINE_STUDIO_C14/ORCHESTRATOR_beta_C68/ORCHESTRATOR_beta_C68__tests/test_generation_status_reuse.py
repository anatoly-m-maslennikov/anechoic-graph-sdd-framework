"""Keep Status domains pinned to the admitted generation after a rebuild."""

import unittest
from unittest.mock import NonCallableMock, patch

from ORCHESTRATOR_beta_C68 import ORCHESTRATOR_beta_C68__shared as orchestrator
from ORCHESTRATOR_beta_C68.ORCHESTRATOR_beta_C68__shared import GenerationJobs


def _request(name, arguments):
    request = NonCallableMock(
        spec_set=["name", "arguments", "archive_versions"],
        arguments=arguments,
        archive_versions=False,
    )
    request.name = name
    return request


def _lifecycle_inputs(jobs, request, context):
    with (
        patch.object(jobs, "_require_lifecycle_coverage"),
        patch(
            "ORCHESTRATOR_beta_C68.lifecycle.lifecycle_context",
            return_value=context,
        ),
        patch(
            "ORCHESTRATOR_beta_C68.lifecycle.requires_project_capture",
            return_value=False,
        ),
    ):
        return jobs._lifecycle_inputs(request)


def _generation(binding, witness, domains, prior, admitted_base):
    jobs = GenerationJobs("test", binding, "/tmp/kernel.sock")
    jobs.startup_replay = False
    result = {"snapshot": {}, "reuse": witness.copy()}
    accepted = orchestrator.ReuseRecord(
        **witness,
        base_generation=admitted_base,
        status_domains=domains,
    )
    with (
        patch.object(
            jobs,
            "_capture_generation",
            return_value=(result, prior, {}),
        ),
        patch.object(
            jobs,
            "_admit_live_result",
            return_value={"generation": "new"},
        ),
        patch.object(jobs, "_accept_live_generation"),
        patch(
            "ORCHESTRATOR_beta_C68.generation.read_reuse",
            return_value=accepted,
        ),
    ):
        jobs._attempt_generation(None, prior)
    saved = jobs.generation_reuse.model_dump(exclude_unset=True)
    return jobs, saved


class GenerationStatusReuseTest(unittest.TestCase):
    def _assert_admitted_domains(self, jobs, saved, domains, admitted_base):
        self.assertEqual("new", saved["base_generation"])
        context = {
            "structure": {"components": []},
            "carriers": [],
            "has_descendants": False,
        }
        request = _request(
            "atom_lifecycle_change_status",
            {"target": {"ref_id": "AN-T-1"}},
        )
        base, _, facts = _lifecycle_inputs(jobs, request, context)
        self.assertEqual("new", base)
        if admitted_base == "new":
            self.assertEqual(domains, saved["status_domains"])
            self.assertEqual(
                domains,
                facts["lifecycle_context"]["status_domains"],
            )
        else:
            self.assertNotIn("status_domains", saved)
            self.assertEqual({}, facts)
            for name, arguments in (
                (
                    "atom_lifecycle_create_draft",
                    {"sourceCurrent": {"ref_id": "AN-T-2"}},
                ),
                (
                    "atom_lifecycle_create_asset",
                    {"owner": {"ref_id": "AN-T-2"}},
                ),
            ):
                request = _request(name, arguments)
                _, _, facts = _lifecycle_inputs(jobs, request, context)
                self.assertEqual({}, facts)

    def test_cold_and_rebuild_use_admitted_domains_in_indexed_lifecycle(self):
        binding = {
            "root": "/tmp",
            "control_root": "control",
            "manifest_path": "manifest.md",
            "manifest_sha256": "a" * 64,
            "project_prefix": "AN",
        }
        witness = {"inputs": {}, "graph_config": None, "endpoints": {}}
        domains = {
            "S": ["active"],
            "T": ["active", "triage"],
            "P": ["active"],
            "C": ["active"],
        }
        for prior in (
            None,
            witness
            | {
                "base_generation": "old",
                "status_domains": {
                    "S": ["active"],
                    "T": ["active"],
                    "P": ["active"],
                    "C": ["active"],
                },
            },
        ):
            for admitted_base in ("new", "stale"):
                with self.subTest(prior=prior, admitted_base=admitted_base):
                    jobs, saved = _generation(
                        binding, witness, domains, prior, admitted_base
                    )
                    self._assert_admitted_domains(
                        jobs, saved, domains, admitted_base
                    )

    def test_carrier_delta_retains_domains_without_reloading_checkpoint(self):
        binding = {
            "root": "/tmp",
            "control_root": "control",
            "manifest_path": "manifest.md",
            "manifest_sha256": "a" * 64,
            "project_prefix": "AN",
        }
        jobs = GenerationJobs("test", binding, "/tmp/kernel.sock")
        domains = {
            "S": ["active"],
            "T": ["active", "triage"],
            "P": ["active"],
            "C": ["active"],
        }
        prior = {
            "inputs": {},
            "graph_config": None,
            "endpoints": {},
            "base_generation": "old",
            "status_domains": domains,
        }
        result = {
            "base_generation": "old",
            "paths": [["control", "a.md"]],
            "snapshot": {"atoms": []},
        }
        with (
            patch.object(
                jobs, "_capture_generation", return_value=(result, prior, {})
            ),
            patch.object(
                jobs, "_admit_live_result", return_value={"generation": "new"}
            ),
            patch.object(jobs, "_accept_live_generation"),
            patch("ORCHESTRATOR_beta_C68.generation.read_reuse") as read,
        ):
            jobs._attempt_generation(None, prior)
        read.assert_not_called()
        self.assertEqual(domains, jobs.generation_reuse.status_domains)

    def test_new_task_without_domains_uses_full_capture(self):
        binding = {
            "root": "/tmp",
            "control_root": "control",
            "manifest_path": "manifest.md",
            "manifest_sha256": "a" * 64,
            "project_prefix": "AN",
        }
        jobs = GenerationJobs("test", binding, "/tmp/kernel.sock")
        jobs.startup_replay = False
        jobs.generation_reuse = orchestrator.ReuseRecord(
            base_generation="new",
            inputs={},
            graph_config=None,
            endpoints={},
        )
        request = _request(
            "atom_lifecycle_create_draft",
            {
                "newAtom": {
                    "template": "task",
                    "container": {"component": "C00"},
                },
            },
        )
        structure = {"components": {}, "project": {"ref": "AN-S-1@1"}}
        with (
            patch.object(jobs, "_require_lifecycle_coverage"),
            patch(
                "ORCHESTRATOR_beta_C68.lifecycle.read_structure",
                return_value=structure,
            ),
            patch(
                "ORCHESTRATOR_beta_C68.lifecycle.ticket_allocation"
            ) as allocation,
        ):
            self.assertEqual(
                ("new", structure, {}), jobs._lifecycle_inputs(request)
            )
        allocation.assert_not_called()
