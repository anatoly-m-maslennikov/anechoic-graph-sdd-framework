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


def structure_digest(binding):
    module = "WORKERS_beta_C69.manifest_build_CS4.manifest_build_CS4__shared"
    with tempfile.TemporaryDirectory(prefix="ane-lifecycle-structure-") as directory:
        result = subprocess.run([sys.executable, "-B", "-P", "-m", module, "--output-dir", str(Path(directory).resolve())],
            cwd=ENGINE, env={**os.environ, "PYTHONPATH": str(ENGINE)}, input=json.dumps(binding),
            text=True, capture_output=True, timeout=120)
    return json.loads(result.stdout)["structure_sha256"] if result.returncode == 0 else "invalid"


def invoke(binding, name, arguments, *, structure_sha256=None, indexed_task=None):
    payload = {"binding": binding, "name": name, "arguments": arguments, "base_generation": "test-generation",
               "structure_sha256": structure_sha256 or structure_digest(binding)}
    if indexed_task is not None:
        payload["indexed_task"] = indexed_task
    return subprocess.run([sys.executable, "-B", "-P", "-m", "WORKERS_beta_C69.lifecycle_worker"],
        cwd=ENGINE, env={**os.environ, "PYTHONPATH": str(ENGINE)}, input=json.dumps(payload),
        text=True, capture_output=True, timeout=120)


def copy_lifecycle_definitions(control):
    source = ENGINE.parent / "_anechoic_anechoic"
    for relative in ("LAYER_1_META_ONTOLOGY_C9", "LAYER_1_META_ONTOLOGY_C9/_SPEC", "__PROJECT_CONFIG/CUSTOM_MODEL"):
        destination = control / relative
        destination.mkdir(parents=True, exist_ok=True)
        for path in (source / relative).glob("*.md"):
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
    task_header = ("---\natom_family: TKT\natom_id: AN-T-100\ncontainer:\n  component: C00\n"
                   "priority: 2\ncontext:\n  template: task\n  label: Task\nstate:\n"
                   "  status: in_queue\n  version: 1\n" + timestamp)
    typed_header = ("---\natom_family: TKT\natom_id: AN-T-101\ncontainer:\n  atom: AN-T-100\n"
                    "priority: 2\ncontext:\n  template: Analysis Report\nstate:\n"
                    "  status: in_queue\n  version: 2\n" + timestamp)
    untyped_header = ("---\nidentity:\n  atom_id: AN-T-102\ncontext:\n  container:\n"
                      "    component: C00\nstate:\n  status: draft\n  version: 1\n" + timestamp)
    before = "\n## Summary\n\nCanary.\n"
    body = before + "\n## Work\n\nUpdated.\n"
    task.write_text(task_header + before, encoding="utf-8")
    typed.write_text(typed_header + before, encoding="utf-8")
    untyped.write_text(untyped_header + before, encoding="utf-8")
    return root, task, typed, untyped, task_header, typed_header, untyped_header, before, body


class LifecycleWorkerTests(unittest.TestCase):
    def test_stale_structure_refuses_before_write(self):
        with tempfile.TemporaryDirectory(prefix="ane-lifecycle-", dir="/tmp") as directory:
            binding, _, _ = generation_fixture(directory)
            response = invoke(binding, "atom_lifecycle_create_draft", {"newAtom": {
                "template": "task", "container": {"component": "C00"}, "body": "## Summary\n\nCanary.\n"}},
                structure_sha256="0" * 64)
            self.assertEqual(0, response.returncode, response.stderr)
            value = json.loads(response.stdout)
            self.assertEqual("failed", value["lifecycle"]["outcome"], value)
            self.assertEqual([], value["lifecycle"].get("effects", []))
            self.assertIn("admitted Model and Structure inputs", value["projection_error"])
            self.assertIsNone(value["delta"])

    def test_task_create_revise_and_promote(self):
        with tempfile.TemporaryDirectory(prefix="ane-lifecycle-", dir="/tmp") as directory:
            binding, _, _ = generation_fixture(directory)
            def run(name, arguments):
                result = invoke(binding, name, arguments)
                self.assertEqual(0, result.returncode, result.stderr)
                response = json.loads(result.stdout)
                self.assertIsNone(response["projection_error"], response)
                value = response["lifecycle"]
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
                response = json.loads(result.stdout)
                self.assertIsNone(response["projection_error"], response)
                value = response["lifecycle"]
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
                response = json.loads(result.stdout)
                self.assertIsNone(response["projection_error"], response)
                return response["lifecycle"]
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
            control = Path(binding["root"]) / binding["control_root"]
            copy_lifecycle_definitions(control)
            def run(name, arguments):
                result = invoke(binding, name, arguments)
                self.assertEqual(0, result.returncode, result.stderr)
                response = json.loads(result.stdout)
                self.assertIsNone(response["projection_error"], response)
                return response["lifecycle"]
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
            original_path = Path(binding["root"]) / original["path"]
            container = original_path.with_suffix("")
            container.mkdir()
            refused = run("atom_lifecycle_archive", {"target": target})
            self.assertEqual("needs_input", refused["outcome"], refused)
            self.assertEqual([], refused["effects"])
            container.rmdir()
            archived = run("atom_lifecycle_archive", {"target": target})
            self.assertEqual("completed", archived["outcome"], archived)
            self.assertEqual("archived", archived["artifact"]["status"])
            self.assertTrue(archived["effects"])
            self.assertFalse((Path(binding["root"]) / original["path"]).exists())

    def test_ticket_asset_direct_update(self):
        with tempfile.TemporaryDirectory(prefix="ane-lifecycle-", dir="/tmp") as directory:
            binding, _, _ = generation_fixture(directory)
            root, task, typed, untyped, task_header, typed_header, untyped_header, before, body = (
                ticket_asset_fixture(binding))

            def update(ref, version, change=body):
                response = invoke(binding, "atom_lifecycle_direct_update", {
                    "target": {"ref_id": ref, "version": version}, "changes": {"body": change}})
                self.assertEqual(0, response.returncode, response.stderr)
                value = json.loads(response.stdout)
                self.assertIsNone(value["projection_error"], value)
                return value["lifecycle"]

            for ref, version, path, header in (
                ("AN-T-101", 2, typed, typed_header), ("AN-T-102@1-draft", 1, untyped, untyped_header)
            ):
                with self.subTest(ref=ref):
                    result = update(ref, version)
                    self.assertEqual("completed", result["outcome"], result)
                    self.assertEqual((ref, version, path.relative_to(root).as_posix()), (
                        result["artifact"]["ref_id"], result["artifact"]["version"], result["artifact"]["path"]))
                    self.assertEqual((header + body).encode(), path.read_bytes())

            for ref, version, field in (("AN-T-100", 1, "target"), ("ZZ-T-101", 2, "target"),
                                        ("AN-T-101", 2, "summary")):
                with self.subTest(ref=ref, field=field):
                    change = body.replace("Canary.", "Changed summary.") if field == "summary" else body
                    result = update(ref, version, change)
                    self.assertEqual("needs_input", result["outcome"], result)
                    self.assertIn(field, result["requested_input"])
                    self.assertEqual([], result["effects"])
            stale = update("AN-T-101", 1)
            self.assertEqual("source_changed", stale["errors"][0]["code"], stale)
            self.assertEqual([], stale["effects"])
            self.assertEqual((task_header + before).encode(), task.read_bytes())
            self.assertEqual((typed_header + body).encode(), typed.read_bytes())
            self.assertEqual((untyped_header + body).encode(), untyped.read_bytes())

    def test_invalid_binding_and_out_of_scope_refused(self):
        with tempfile.TemporaryDirectory(prefix="ane-lifecycle-", dir="/tmp") as directory:
            binding, _, _ = generation_fixture(directory)
            result = invoke({**binding, "manifest_sha256": "0" * 64}, "atom_lifecycle_create_draft", {})
            self.assertNotEqual(0, result.returncode)
            result = invoke(binding, "atom_lifecycle_create_draft", {"newAtom": {"template": "component_contract"}})
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertNotEqual("completed", json.loads(result.stdout)["lifecycle"]["outcome"])

    def test_indexed_worker_uses_only_published_carrier(self):
        with tempfile.TemporaryDirectory(prefix="ane-indexed-", dir="/tmp") as directory:
            binding, _, manifest = generation_fixture(directory)
            manifest.unlink()
            indexed = {"max_number": "100", "manifest_ref": "AN-S-1@1", "component_ids": ["C00"],
                       "ticket_labels": ["Task"],
                       "endpoints": {"CONTAINED_BY": [{"inverse_alias": "CONTAINS"}, False], "CONTAINS": [{}, True]}}
            result = invoke(binding, "atom_lifecycle_create_draft", {"newAtom": {
                "template": "task", "container": {"component": "C00"}, "body": "## Summary\n\nCanary.\n"}},
                structure_sha256="admitted", indexed_task=indexed)
            self.assertEqual(0, result.returncode, result.stderr)
            response = json.loads(result.stdout)
            self.assertIsNone(response["projection_error"], response)
            created = response["lifecycle"]["savedDraft"]
            self.assertEqual("AN-T-101@1-draft", created["ref_id"])
            self.assertEqual([created["path"]], list(response["delta"]["carrier_hashes"]))
