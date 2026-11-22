"""Exercise the fixed lifecycle CLI with real attested Model and Structure."""
import json
import os
import shutil
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

    def test_epic_and_create_draft_revision(self):
        with tempfile.TemporaryDirectory(prefix="ane-lifecycle-", dir="/tmp") as directory:
            binding, _, _ = generation_fixture(directory)
            def run(name, arguments):
                result = invoke(binding, name, arguments)
                self.assertEqual(0, result.returncode, result.stderr)
                value = json.loads(result.stdout)
                self.assertEqual("completed", value["outcome"], value)
                return value
            created = run("atom_lifecycle_create_draft", {"newAtom": {
                "template": "epic", "container": {"component": "C00"}, "body": "## Summary\n\nEpic canary.\n"}})
            draft = created["savedDraft"]
            self.assertTrue(created["effects"])
            run("atom_lifecycle_promote_draft", {"target": {"ref_id": draft["ref_id"], "version": 1},
                                                   "targetStatus": "backlog"})
            revised = run("atom_lifecycle_create_draft", {
                "sourceCurrent": {"ref_id": draft["atom_id"], "version": 1},
                "changes": {"body": "## Summary\n\nEpic canary.\n\nRevised.\n"}})
            revision = revised["savedDraft"]
            self.assertEqual(2, revision["version"])
            promoted = run("atom_lifecycle_promote_draft", {
                "target": {"ref_id": revision["ref_id"], "version": 2}, "targetStatus": "backlog"})
            self.assertEqual(2, promoted["artifact"]["version"])
            self.assertTrue(any("@1-" in effect["target"] for effect in promoted["effects"]))

    def test_ticket_status_checks_installed_definitions(self):
        with tempfile.TemporaryDirectory(prefix="ane-lifecycle-", dir="/tmp") as directory:
            binding, _, _ = generation_fixture(directory)
            source_root = ENGINE.parent / "_anechoic_anechoic" / "LAYER_1_META_ONTOLOGY_C9"
            control = Path(binding["root"]) / binding["control_root"]
            shutil.copytree(source_root, control / "LAYER_1_META_ONTOLOGY_C9")
            shutil.copytree(ENGINE.parent / "_anechoic_anechoic" / "__PROJECT_CONFIG" / "CUSTOM_MODEL",
                            control / "__PROJECT_CONFIG" / "CUSTOM_MODEL")
            def run(name, arguments):
                result = invoke(binding, name, arguments)
                self.assertEqual(0, result.returncode, result.stderr)
                return json.loads(result.stdout)
            created = run("atom_lifecycle_create_draft", {"newAtom": {
                "template": "task", "container": {"component": "C00"}, "body": "## Summary\n\nStatus canary.\n"}})
            self.assertEqual("completed", created["outcome"], created)
            draft = created["savedDraft"]
            target = {"ref_id": draft["ref_id"], "version": 1}
            self.assertEqual("completed", run("atom_lifecycle_promote_draft", {
                "target": target, "targetStatus": "backlog"})["outcome"])
            target["ref_id"] = draft["atom_id"]
            changed = run("atom_lifecycle_change_status", {"target": target, "targetStatus": "in_queue"})
            self.assertEqual("completed", changed["outcome"], changed)
            self.assertEqual("in_queue", changed["artifact"]["status"])
            self.assertTrue(changed["effects"])
            rejected = run("atom_lifecycle_change_status", {"target": target, "targetStatus": "nonsense"})
            self.assertEqual("needs_input", rejected["outcome"])
            self.assertEqual([], rejected["effects"])
            installed = next((control / "LAYER_1_META_ONTOLOGY_C9").rglob("AN-S-1831-*.md"))
            installed.write_bytes(installed.read_bytes() + b"changed\n")
            blocked = run("atom_lifecycle_change_status", {"target": target, "targetStatus": "done"})
            self.assertEqual("blocked", blocked["outcome"], blocked)
            self.assertEqual("definition_revalidation_required", blocked["errors"][0]["code"])
            self.assertEqual([], blocked["effects"])

    def test_archive_requires_current_replacement(self):
        with tempfile.TemporaryDirectory(prefix="ane-lifecycle-", dir="/tmp") as directory:
            binding, _, _ = generation_fixture(directory)
            source = ENGINE.parent / "_anechoic_anechoic"
            control = Path(binding["root"]) / binding["control_root"]
            for relative in ("LAYER_1_META_ONTOLOGY_C9", "LAYER_1_META_ONTOLOGY_C9/_SPEC",
                             "__PROJECT_CONFIG/CUSTOM_MODEL"):
                destination = control / relative
                destination.mkdir(parents=True, exist_ok=True)
                for path in (source / relative).glob("*.md"):
                    shutil.copy2(path, destination / path.name)
            def run(name, arguments):
                result = invoke(binding, name, arguments)
                self.assertEqual(0, result.returncode, result.stderr)
                return json.loads(result.stdout)
            def create(summary):
                draft = run("atom_lifecycle_create_draft", {"newAtom": {"template": "task",
                    "container": {"component": "C00"}, "body": f"## Summary\n\n{summary}\n"}})["savedDraft"]
                promoted = run("atom_lifecycle_promote_draft", {
                    "target": {"ref_id": draft["ref_id"], "version": 1}, "targetStatus": "backlog"})
                self.assertEqual("completed", promoted["outcome"], promoted)
                return promoted["artifact"]
            original = create("Original")
            target = {"ref_id": original["atom_id"], "version": 1}
            refused = run("atom_lifecycle_archive", {"target": target})
            self.assertEqual("needs_input", refused["outcome"], refused)
            self.assertEqual([], refused["effects"])
            replacement = create("Replacement")
            path = Path(binding["root"]) / replacement["path"]
            data = path.read_text()
            self.assertNotIn("\nrelations:", data)
            path.write_text(data.replace("\n---\n", "\nrelations:\n  IS_REPLACEMENT_FOR: [" +
                                         original["atom_id"] + "]\n---\n", 1))
            archived = run("atom_lifecycle_archive", {"target": target})
            self.assertEqual("completed", archived["outcome"], archived)
            self.assertEqual("archived", archived["artifact"]["status"])
            self.assertTrue(archived["effects"])
            self.assertFalse((Path(binding["root"]) / original["path"]).exists())

    def test_invalid_binding_and_out_of_scope_refused(self):
        with tempfile.TemporaryDirectory(prefix="ane-lifecycle-", dir="/tmp") as directory:
            binding, _, _ = generation_fixture(directory)
            result = invoke({**binding, "manifest_sha256": "0" * 64}, "atom_lifecycle_create_draft", {})
            self.assertNotEqual(0, result.returncode)
            result = invoke(binding, "atom_lifecycle_create_draft", {"newAtom": {"template": "component_contract"}})
            self.assertNotEqual(0, result.returncode)
