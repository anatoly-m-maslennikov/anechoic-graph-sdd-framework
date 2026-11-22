"""Exercise the fixed lifecycle CLI with real attested Model and Structure."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from .WORKERS_beta_C69__tests__shared import generation_fixture

ENGINE = Path(__file__).resolve().parents[2]


def invoke(binding, name, arguments):
    payload = {"binding": binding, "name": name, "arguments": arguments}
    return subprocess.run([sys.executable, "-B", "-P", "-m", "WORKERS_beta_C69.lifecycle_worker"],
        cwd=ENGINE, env={**os.environ, "PYTHONPATH": str(ENGINE)}, input=json.dumps(payload),
        text=True, capture_output=True, timeout=120)


class LifecycleWorkerTests(unittest.TestCase):
    def test_task_create_revise_and_promote(self):
        with tempfile.TemporaryDirectory(prefix="ane-lifecycle-", dir="/tmp") as directory:
            binding, _, _ = generation_fixture(directory)
            def run(name, arguments):
                result = invoke(binding, name, arguments)
                self.assertEqual(0, result.returncode, result.stderr)
                value = json.loads(result.stdout)
                self.assertEqual("completed", value["outcome"], value)
                return value
            created = run("atom_lifecycle_create_draft", {"newAtom": {
                "template": "task", "container": {"component": "C00"}, "body": "## Summary\n\nCanary.\n"}})
            draft = created["savedDraft"]
            run("atom_lifecycle_promote_draft", {"target": {"ref_id": draft["ref_id"], "version": 1},
                                                   "targetStatus": "backlog"})
            revised = run("atom_lifecycle_update", {"sourceCurrent": {"ref_id": draft["atom_id"], "version": 1},
                "changes": {"body": "## Summary\n\nCanary.\n\nRevised.\n"}})
            draft = revised["savedDraft"]
            promoted = run("atom_lifecycle_promote_draft", {"target": {"ref_id": draft["ref_id"], "version": 2},
                                                            "targetStatus": "backlog"})
            self.assertEqual(2, promoted["artifact"]["version"])
            self.assertTrue(any("@1-" in effect["target"] for effect in promoted["effects"]))

    def test_invalid_binding_and_out_of_scope_refused(self):
        with tempfile.TemporaryDirectory(prefix="ane-lifecycle-", dir="/tmp") as directory:
            binding, _, _ = generation_fixture(directory)
            result = invoke({**binding, "manifest_sha256": "0" * 64}, "atom_lifecycle_create_draft", {})
            self.assertNotEqual(0, result.returncode)
            result = invoke(binding, "atom_lifecycle_create_draft", {"newAtom": {"template": "component_contract"}})
            self.assertNotEqual(0, result.returncode)
