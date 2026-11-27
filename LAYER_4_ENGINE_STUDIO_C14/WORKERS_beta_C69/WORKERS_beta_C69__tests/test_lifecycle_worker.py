"""Exercise the fixed lifecycle CLI with real attested Model and Structure."""

from ._lifecycle_cases_0 import LifecycleCases0
from ._lifecycle_cases_1 import LifecycleCases1
from ._lifecycle_cases_2 import LifecycleCases2
from hashlib import sha256
import json
import os
import shutil
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch as patch

from .WORKERS_beta_C69__tests__shared import (
    command_with_fixture as command_with_fixture,
    generation_fixture as generation_fixture,
)

ENGINE = Path(__file__).resolve().parents[2]


def structure_digest(binding):
    module = "WORKERS_beta_C69.manifest_build_CS4.manifest_build_CS4__shared"
    with tempfile.TemporaryDirectory(
        prefix="ane-lifecycle-structure-"
    ) as directory:
        result = subprocess.run(
            [
                sys.executable,
                "-B",
                "-P",
                "-m",
                module,
                "--output-dir",
                str(Path(directory).resolve()),
            ],
            cwd=ENGINE,
            env={**os.environ, "PYTHONPATH": str(ENGINE)},
            input=json.dumps(binding),
            text=True,
            capture_output=True,
            timeout=120,
        )
    return (
        json.loads(result.stdout)["structure_sha256"]
        if result.returncode == 0
        else "invalid"
    )


def invoke(
    binding, name, arguments, *, structure_sha256=None, indexed_task=None
):
    payload = {
        "binding": binding,
        "name": name,
        "arguments": arguments,
        "base_generation": "test-generation",
        "structure_sha256": structure_sha256 or structure_digest(binding),
    }
    if indexed_task is not None:
        payload["indexed_task"] = indexed_task
    return subprocess.run(
        [
            sys.executable,
            "-B",
            "-P",
            "-m",
            "WORKERS_beta_C69.lifecycle_worker",
        ],
        cwd=ENGINE,
        env={**os.environ, "PYTHONPATH": str(ENGINE)},
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        timeout=120,
    )


def copy_lifecycle_definitions(control):
    source = ENGINE.parent / "_anechoic_anechoic"
    for relative in (
        "LAYER_1_META_ONTOLOGY_C9",
        "LAYER_1_META_ONTOLOGY_C9/_SPEC",
        "LAYER_1_META_ONTOLOGY_C9/_DOM/CONT",
        "__PROJECT_CONFIG/CUSTOM_MODEL",
    ):
        destination = control / relative
        destination.mkdir(parents=True, exist_ok=True)
        for path in (
            source
            / (
                relative.replace(
                    "LAYER_1_META_ONTOLOGY_C9",
                    "ONTOLOGY_SCORE_C82/CONTINUANT_PITCHFORK_C9",
                )
                if relative.startswith("LAYER_1_META_ONTOLOGY_C9")
                else relative
            )
        ).glob("*.md"):
            shutil.copy2(path, destination / path.name)


def ticket_asset_fixture(binding):
    root = Path(binding["root"])
    tickets = root / binding["control_root"] / "__TICKETS"
    task = tickets / "TASKS/AN-T-100-TASK--owner.md"
    typed = task.with_suffix("") / "ASSETS/AN-T-101-ANALYSIS_REPORT--canary.md"
    untyped = tickets / "ASSETS/01_draft/AN-T-102@1-draft--canary.md"
    for path in (typed, untyped):
        path.parent.mkdir(parents=True, exist_ok=True)
    timestamp = "  updated_at: '2026-11-19T00:00:00Z'\n---\n"
    task_header = (
        "---\natom_family: TKT\natom_id: AN-T-100\ncontainer:\n  "
        "component: C00\n"
        "priority: 2\ncontext:\n  template: task\n  label: Task\nstate:\n"
        "  status: in_queue\n  version: 1\n" + timestamp
    )
    typed_header = (
        "---\natom_family: TKT\natom_id: AN-T-101\ncontainer:\n  atom: "
        "AN-T-100\n"
        "priority: 2\ncontext:\n  template: Analysis Report\nstate:\n"
        "  status: in_queue\n  version: 2\n" + timestamp
    )
    untyped_header = (
        "---\nidentity:\n  atom_id: AN-T-102\ncontext:\n  container:\n"
        "    component: C00\nstate:\n  status: draft\n  version: 1\n"
        + timestamp
    )
    before = "\n## Summary\n\nCanary.\n"
    body = before + "\n## Work\n\nUpdated.\n"
    task.write_text(task_header + before, encoding="utf-8")
    typed.write_text(typed_header + before, encoding="utf-8")
    untyped.write_text(untyped_header + before, encoding="utf-8")
    return (
        root,
        task,
        typed,
        untyped,
        task_header,
        typed_header,
        untyped_header,
        before,
        body,
    )


class LifecycleWorkerTests(
    LifecycleCases0, LifecycleCases1, LifecycleCases2, unittest.TestCase
):
    @staticmethod
    def warning_arguments(name, binding):
        if name == "atom_lifecycle_direct_update":
            *_, body = ticket_asset_fixture(binding)
            return {
                "target": {"ref_id": "AN-T-101", "version": 2},
                "changes": {"body": body},
            }
        return {
            "newAtom": {
                "template": "task",
                "container": {"component": "C00"},
                "body": "## Summary\n\nCanary.\n",
            }
        }

    @staticmethod
    def warning_delta(binding, paths, _endpoints, **_options):
        (target,) = paths
        digest = sha256(
            (Path(binding["root"]) / target).read_bytes()
        ).hexdigest()
        return {
            "carrier_hashes": {target: digest},
            "snapshot": {
                "atoms": [],
                "ingestion_issues": [
                    {"relative_path": target, "code": "parse_error"}
                ],
            },
        }
