"""Run formal exact-Draft outcomes through the declared C16 CLI."""

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75._package__shared import (
    verify_formal_chain,
)

ROOT = Path(__file__).resolve().parents[7]
ENGINE = ROOT / "LAYER_4_ENGINE_STUDIO_C14"
BASE = "_anechoic_anechoic/LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC_C15/"
MANIFEST = {
    "path": BASE
    + "01_draft/AN-S-3056@68-draft-SPEC-COMPONENT_MANIFEST--declare-tools.md",
    "atom_id": "AN-S-3056",
    "version": 68,
    "status": "draft",
    "container_component": "C15",
}
SOLUTION = {
    "path": BASE + "FEATURE_TOOLS_C16/01_draft/AN-S-5042@1-draft-DES-SOLUTION"
    "--update-one-exact-draft.md",
    "atom_id": "AN-S-5042",
    "version": 1,
    "status": "draft",
    "container_component": "C16",
}


_FAULT_SCRIPT = """
import os
from pathlib import Path
import runpy
import sys
fault, target = sys.argv[1], Path(sys.argv[2])
original_replace, original_open = os.replace, os.open
target_dir = target.parent.stat()
published = False
def is_target(parent, name):
    if parent is None or name != target.name:
        return False
    actual = os.fstat(parent)
    return (actual.st_dev, actual.st_ino) == (target_dir.st_dev, \
target_dir.st_ino)
def replace(source, destination, *, src_dir_fd=None, dst_dir_fd=None):
    global published
    replacing_target = is_target(dst_dir_fd, destination)
    if replacing_target and fault == 'write_rejected':
        raise OSError('injected replacement failure')
    original_replace(source, destination, src_dir_fd=src_dir_fd, \
dst_dir_fd=dst_dir_fd)
    if replacing_target:
        published = True
def open_file(name, flags, mode=0o777, *, dir_fd=None):
    if published and is_target(dir_fd, name):
        raise OSError('injected readback failure')
    return original_open(name, flags, mode, dir_fd=dir_fd)
os.replace, os.open = replace, open_file
runpy.run_module('FEATURE_PROGRAMMATIC.FEATURE_TOOLS.native_lifecycle_cli', \
run_name='__main__')
"""


def invoke(request, fault=None, target=None):
    command = [
        sys.executable,
        "-B",
        "-P",
        "-m",
        "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.native_lifecycle_cli",
    ]
    if fault:
        command = [
            sys.executable,
            "-B",
            "-P",
            "-c",
            _FAULT_SCRIPT,
            fault,
            str(target),
        ]
    process = subprocess.run(
        command,
        cwd=ENGINE,
        env={**os.environ, "PYTHONPATH": str(ENGINE)},
        input=json.dumps(request),
        text=True,
        capture_output=True,
        timeout=30,
        check=True,
    )
    return json.loads(process.stdout)


def project(root):
    (root / ".git").mkdir()
    control = root / ".anechoic_test"
    control.mkdir()
    manifest = control / "AN-S-1-PROJECT_MANIFEST--manifest.md"
    manifest.write_text("project fixture")
    digest = hashlib.sha256(manifest.read_bytes()).hexdigest()
    binding = {
        "root": str(root),
        "control_root": control.name,
        "manifest_path": manifest.relative_to(root).as_posix(),
        "manifest_sha256": digest,
        "project_prefix": "AN",
    }
    request = {
        "binding": binding,
        "name": "atom_lifecycle_create_draft",
        "arguments": {
            "newAtom": {
                "template": "task",
                "container": {"component": "C00"},
                "body": "\n## Summary\n\nExample\n\n## Work\n\nOriginal\n",
            }
        },
        "indexed_task": {
            "max_number": "0",
            "manifest_ref": "AN-S-1@1",
            "component_ids": ["C00"],
            "ticket_labels": ["Task"],
        },
    }
    created = invoke(request)["savedDraft"]
    return binding, created


def update_request(binding, draft, changes, expected):
    ref = draft["ref_id"]
    carrier = {
        "ref": ref,
        "_exact_ref": ref,
        "source_path": draft["path"],
        "version": draft["version"],
        "status": "draft",
        "status_group": "Draft",
        "id": draft["atom_id"],
        "owner_kind": "Component",
        "owner_ref": "C00",
        "read": True,
    }
    structure = {
        "model_sha256": "fixture",
        "project": {"ref": "AN-S-1@1", "sha256": binding["manifest_sha256"]},
        "components": {},
        "packages": {},
    }
    return {
        "binding": binding,
        "name": "atom_lifecycle_update",
        "arguments": {
            "target": {"ref_id": ref, "version": draft["version"]},
            "changes": changes,
            "expectedUpdatedAt": expected,
        },
        "lifecycle_context": {
            "structure": structure,
            "model": None,
            "carriers": [carrier],
            "max_numbers": {"T": "1", "S": "1"},
            "lenses": [],
            "ticket_labels": [],
        },
    }


_VARIANTS = {
    "completed": ("body",),
    "preflight_rejected": ("stale", "unowned_relation", "summary"),
    "write_rejected": ("write_rejected",),
    "effect_uncertain": ("effect_uncertain",),
}


def _variant_inputs(draft, variant):
    expected = "stale" if variant == "stale" else draft["updated_at"]
    body = "\n## Summary\n\nExample\n\n## Work\n\nSaved\n"
    if variant == "summary":
        body = body.replace("Example", "Changed")
    changes = (
        {"removeRelations": [{"type": "RELATES_TO", "ref_id": "AN-T-9"}]}
        if variant == "unowned_relation"
        else {"body": body}
    )
    return expected, changes


class GeneratedExactDraftTests(unittest.TestCase):
    def test_generated_outcomes(self):
        lean = os.environ.get("LEAN_BIN") or shutil.which("lean")
        if not lean:
            self.skipTest("Lean unavailable")
        report = verify_formal_chain(
            ROOT,
            "C16",
            MANIFEST,
            solution=SOLUTION,
            action="update_exact_draft",
            lean=lean,
        )
        self.assertEqual("compared", report["outcome"], report)
        facts = report["evidence"]["coverage"]
        self.assertTrue(
            all(fact["status"] == "matched" for fact in facts), facts
        )
        cases = {
            fact["output"]
            for fact in facts
            if fact.get("direction") == "manifest_solution"
        }
        self.assertEqual(
            {
                "completed",
                "preflight_rejected",
                "write_rejected",
                "effect_uncertain",
            },
            cases,
        )
        for case, variant in (
            (case, variant)
            for case in sorted(cases)
            for variant in _VARIANTS[case]
        ):
            with (
                self.subTest(case=case, variant=variant),
                tempfile.TemporaryDirectory() as directory,
            ):
                self.check_variant(case, variant, Path(directory).resolve())

    def check_variant(self, case, variant, root):
        binding, draft = project(root)
        path = root / draft["path"]
        before = path.read_bytes()
        before_files = {
            p.relative_to(root) for p in root.rglob("*") if p.is_file()
        }
        expected, changes = _variant_inputs(draft, variant)
        fault = (
            case if case in ("write_rejected", "effect_uncertain") else None
        )
        result = invoke(
            update_request(binding, draft, changes, expected), fault, path
        )
        if fault:
            self.assert_write_failure(
                case, draft, result, before, path.read_bytes()
            )
            self.assertEqual(
                before_files,
                {p.relative_to(root) for p in root.rglob("*") if p.is_file()},
            )
        elif case == "completed":
            self.assertEqual("completed", result["outcome"], result)
            self.assertEqual(draft["ref_id"], result["artifact"]["ref_id"])
            self.assertEqual(draft["version"], result["artifact"]["version"])
            self.assertNotEqual(
                draft["updated_at"], result["artifact"]["updated_at"]
            )
            self.assertIn(b"Saved", path.read_bytes())
        else:
            if variant == "stale":
                self.assertEqual("source_changed", result["errors"][0]["code"])
            else:
                self.assertEqual("needs_input", result["outcome"])
            if variant == "summary":
                self.assertIn("summary", result["requested_input"])
            self.assertEqual([], result["effects"])
            self.assertEqual(before, path.read_bytes())

    def assert_write_failure(self, case, draft, result, before, after):
        self.assertEqual("failed", result["outcome"])
        self.assertNotIn("artifact", result)
        if case == "write_rejected":
            self.assertEqual("backend_failure", result["errors"][0]["code"])
            self.assertEqual([], result["effects"])
            self.assertEqual(before, after)
        else:
            self.assertEqual("effect_uncertain", result["errors"][0]["code"])
            (receipt,) = result["effects"]
            self.assertEqual(
                ("modify", draft["path"], "unknown"),
                (receipt["operation"], receipt["target"], receipt["state"]),
            )
            self.assertNotEqual(before, after)
            self.assertIn(b"Saved", after)
