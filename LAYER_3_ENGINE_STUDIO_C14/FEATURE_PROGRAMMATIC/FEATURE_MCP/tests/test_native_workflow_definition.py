"""Exercise admitted native pins without loading or invoking a Workflow body."""

from dataclasses import replace
from hashlib import sha256
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest

import yaml

MCP = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(MCP), str(MCP.parent), str(MCP.parent / "FEATURE_TOOLS")]

from native_project_selection import resolve_native_project  # noqa: E402
from native_workflow_definition import (  # noqa: E402
    NativeDefinitionPin,
    NativeWorkflowDefinitionError,
    bind_native_workflow,
)


class NativeWorkflowDefinitionTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(TemporaryDirectory())).resolve()
        self.control = ".anechoic_anechoic"
        self.manifest = self._write(f"{self.control}/SPEC/AN-S-1-PROJECT_MANIFEST--declare.md", {
            "identity": {"atom_id": "AN-S-1"},
            "context": {"container": {"component": "C0"}, "tier": -1, "template": "project_manifest"},
            "state": {"status": "active", "version": 1},
        }, """## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ProjectManifest
declare_entity(entity_name="Project Manifest", instance=ProjectManifest(name="Anechoic", prefix="AN"))
```
""")
        self.selection = resolve_native_project(
            self.root, self.control,
            validate_manifest=lambda fields, component: SimpleNamespace(**fields),
        )
        self.workflow = self._pin("workflow", "AN-P-1", 3)
        self.step = self._pin("step", "AN-P-2", 2)
        self.action = self._pin("action", "AN-P-3", 1)

    def _write(self, relative, header, body):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"---\n{yaml.safe_dump(header)}---\n\n{body}", encoding="utf-8")
        return path

    def _pin(self, template, atom_id, version, *, relative=None, header_id=None, status="active"):
        relative = relative or f"{self.control}/_PMETA/{atom_id}-{template.upper()}--fixture.md"
        path = self._write(relative, {
            "identity": {"atom_id": header_id or atom_id},
            "context": {"template": template, "container": {"component": "C0"}},
            "state": {"status": status, "version": version},
        }, "## Summary\n\nFixture.\n\n```python\nraise AssertionError('carrier code executed')\n```\n")
        return NativeDefinitionPin(f"{atom_id}@{version}", relative, sha256(path.read_bytes()).hexdigest())

    def _bind(self, **changes):
        binding = {"workflow": self.workflow, "steps": (self.step,), "actions": (self.action,)}
        return bind_native_workflow(self.selection, **(binding | changes))

    def test_exact_active_native_binding_can_be_rechecked(self):
        check = self._bind()
        check()
        check()

    def test_recheck_refuses_changed_bytes_for_each_pin(self):
        check = self._bind()
        for pin in (self.workflow, self.step, self.action):
            with self.subTest(pin=pin.ref_id):
                path = self.root / pin.relative_path
                original = path.read_bytes()
                path.write_bytes(original + b"\n")
                with self.assertRaisesRegex(NativeWorkflowDefinitionError, f"{pin.ref_id} changed"):
                    check()
                path.write_bytes(original)
                check()

    def test_refuses_wrong_tree_and_noncurrent_paths(self):
        for directory in (f"{self.control}/SPEC", f"{self.control}/_PMETA/draft",
                          f"{self.control}/_PMETA/archived", ".anechoic_legacy/_PMETA"):
            with self.subTest(directory=directory):
                pin = self._pin("workflow", "AN-P-1", 3, relative=f"{directory}/AN-P-1-WORKFLOW--fixture.md")
                with self.assertRaisesRegex(NativeWorkflowDefinitionError, "Invalid native PMETA pin"):
                    self._bind(workflow=pin)

    def test_refuses_header_mismatch_even_with_trusted_matching_digest(self):
        for header in ({"status": "draft"}, {"status": "archived"}, {"header_id": "AN-P-9"}):
            with self.subTest(header=header):
                pin = self._pin("workflow", "AN-P-1", 3, **header)
                with self.assertRaisesRegex(NativeWorkflowDefinitionError, "Expected active native workflow"):
                    self._bind(workflow=pin)
        newer = self._pin("workflow", "AN-P-1", 4)
        with self.assertRaisesRegex(NativeWorkflowDefinitionError, "Expected active native workflow"):
            self._bind(workflow=replace(newer, ref_id=self.workflow.ref_id))
        with self.assertRaisesRegex(NativeWorkflowDefinitionError, "Expected active native action"):
            self._bind(workflow=newer, steps=(), actions=(self.step,))

    def test_refuses_bad_digest_and_duplicate_binding(self):
        with self.assertRaisesRegex(NativeWorkflowDefinitionError, "AN-P-3@1 changed"):
            self._bind(actions=(replace(self.action, sha256="0" * 64),))
        with self.assertRaisesRegex(NativeWorkflowDefinitionError, "Duplicate native definition"):
            self._bind(steps=(self.step, self.step))

    def test_recheck_refuses_missing_or_symlinked_source_even_with_same_bytes(self):
        check = self._bind()
        action = self.root / self.action.relative_path
        moved = self.root / ".anechoic_legacy" / action.name
        moved.parent.mkdir()
        action.rename(moved)
        with self.assertRaisesRegex(NativeWorkflowDefinitionError, "AN-P-3@1 is unavailable"):
            check()
        action.symlink_to(moved)
        with self.assertRaisesRegex(NativeWorkflowDefinitionError, "AN-P-3@1 is unavailable"):
            check()

    def test_project_manifest_is_still_pinned_when_admitting_and_rechecking(self):
        check = self._bind()
        self.manifest.write_bytes(self.manifest.read_bytes() + b"\n")
        for verify in (self._bind, check):
            with self.assertRaisesRegex(NativeWorkflowDefinitionError, "AN-S-1@1 changed"):
                verify()


if __name__ == "__main__":
    unittest.main()
