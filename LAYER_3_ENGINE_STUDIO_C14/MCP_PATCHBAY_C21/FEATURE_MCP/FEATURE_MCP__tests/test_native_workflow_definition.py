"""Exercise native Workflow pins and the SPEC contract for status changes."""

from dataclasses import replace
from hashlib import sha256
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest

import yaml

MCP = Path(__file__).resolve().parents[1]
STUDIO = MCP.parents[1]
PROGRAMMATIC = STUDIO / "FEATURE_PROGRAMMATIC"
sys.path[:0] = [str(MCP), str(PROGRAMMATIC), str(PROGRAMMATIC / "FEATURE_TOOLS"), str(STUDIO / "IWE_CONSOLE_C43")]

from native_project_selection import resolve_native_project  # noqa: E402
from native_workflow_definition import (  # noqa: E402
    STATUS_SPECIFICATIONS,
    NativeDefinitionPin,
    NativeWorkflowDefinitionError,
    bind_native_workflow,
    bind_status_specifications,
)


class NativeWorkflowDefinitionTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(TemporaryDirectory())).resolve()
        self.control = ".anechoic_anechoic"
        self.manifest = self._write(f"{self.control}/AN-S-1-PROJECT_MANIFEST--declare.md", {
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

    def test_project_config_workflow_pin(self):
        pin = self._pin("workflow", "AN-P-4", 1,
                        relative=f"{self.control}/002_PROJECT_CONFIG/AN-P-4-WORKFLOW--fixture.md")
        self._bind(workflow=pin)()
        pin = self._pin("workflow", "AN-C-4", 1,
                        relative=f"{self.control}/002_PROJECT_CONFIG/AN-C-4-WORKFLOW--fixture.md")
        self._bind(workflow=pin)()

    def _bind(self, **changes):
        binding = {"workflow": self.workflow, "steps": (self.step,), "actions": (self.action,)}
        return bind_native_workflow(self.selection, **(binding | changes))

    def _status_binding(self):
        ontology = Path(self.control) / "LAYER_1_META_ONTOLOGY_C9"
        source = STUDIO.parent / "_anechoic_anechoic" / ontology.name
        rows = []
        for (native, _) in STATUS_SPECIFICATIONS.values():
            atom_id = native.partition("@")[0]
            original, = source.rglob(f"{atom_id}-DOM-*.md")
            relative = ontology / original.relative_to(source)
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(original.read_bytes())
            rows.append({"_exact_ref": native, "status_group": "Current", "source_path": relative.as_posix(),
                         "_source_sha256": sha256(path.read_bytes()).hexdigest()})
        return rows

    def test_native_status_binding_checks_sources_and_manifest(self):
        rows = self._status_binding()
        check = bind_status_specifications(self.selection, current_rows=rows)
        check()
        for row in rows:
            path = self.root / row["source_path"]
            original = path.read_bytes()
            path.write_bytes(original + b"changed")
            with self.assertRaisesRegex(NativeWorkflowDefinitionError, "changed"):
                check()
            row["_source_sha256"] = sha256(path.read_bytes()).hexdigest()
            with self.assertRaisesRegex(NativeWorkflowDefinitionError, "body differs"):
                bind_status_specifications(self.selection, current_rows=rows)
            path.write_bytes(original)
            row["_source_sha256"] = sha256(original).hexdigest()
        self.manifest.write_bytes(self.manifest.read_bytes() + b"changed")
        with self.assertRaisesRegex(NativeWorkflowDefinitionError, "AN-S-1@1 changed"):
            check()

    def test_native_status_binding_refuses_invalid_inventory_and_header(self):
        rows = self._status_binding()
        for invalid in (rows + rows[:1], rows[1:]):
            with self.assertRaisesRegex(NativeWorkflowDefinitionError, "Missing or ambiguous"):
                bind_status_specifications(self.selection, current_rows=invalid)
        path = self.root / rows[0]["source_path"]
        path.write_bytes(path.read_bytes().replace(b"status: active", b"status: draft"))
        rows[0]["_source_sha256"] = sha256(path.read_bytes()).hexdigest()
        with self.assertRaisesRegex(NativeWorkflowDefinitionError, "Expected active native workflow"):
            bind_status_specifications(self.selection, current_rows=rows)

    def test_status_action_uses_native_specifications(self):
        from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.native_source_rows import capture_native
        from ATOM_LIFECYCLE.native_update import change_ticket_status
        from project_runtime import bind_native_runtime

        self._status_binding()
        path = self._write(f'{self.control}/__TKT/TASKS/AN-T-4-TASK--verify.md', {
            'identity': {'atom_id': 'AN-T-4'},
            'context': {'template': 'TASK', 'container': {'component': 'C0'}},
            'state': {'status': 'active', 'version': 3, 'updated_at': '2026-11-19T00:00:00Z'},
        }, '## Summary\n\nVerify the status action.\n')
        before = capture_native(self.selection)
        self.assertEqual({}, before.errors)
        check = bind_status_specifications(self.selection, current_rows=before.atoms)
        with bind_native_runtime(self.selection):
            outcome = change_ticket_status(self.selection, {
                'target': {'ref_id': 'AN-T-4', 'version': 3}, 'targetStatus': 'Backlog',
            }, current_rows=before.atoms, check_definition=check)
        self.assertEqual('completed', outcome['outcome'], outcome)
        self.assertFalse(path.exists())
        after = capture_native(self.selection)
        self.assertEqual({}, after.errors)
        ticket, = [row for row in after.atoms if row['id'] == 'AN-T-4']
        self.assertEqual(('backlog', 'AN-T-4@3'), (ticket['status'], ticket['_exact_ref']))
        self.assertIn('/TASKS/backlog/', ticket['source_path'])

    def test_lifecycle_cannot_revise_or_promote_installed_status_pin(self):
        from native_query import NativeQueryInputs, NativeQueryOwner

        rows = self._status_binding()
        owner = NativeQueryOwner(self.selection, NativeQueryInputs(
            lambda *args: None, frozenset(), {},
        ))
        owner._store = SimpleNamespace(_available=True)
        owner._capture = SimpleNamespace(atoms=rows)
        atom_id, _, version = rows[0]['_exact_ref'].partition('@')
        for name, field, target in (
            ('atom_lifecycle_update', 'sourceCurrent', {'ref_id': atom_id, 'version': int(version)}),
            ('atom_lifecycle_promote_draft', 'target', {'ref_id': f'{atom_id}@2-draft', 'version': 2}),
        ):
            with self.subTest(name=name):
                result = owner.lifecycle(name, {field: target})
                self.assertEqual('needs_input', result['outcome'])
                self.assertIn('runtime binding', result['requested_input'][field]['error'])

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
                with self.assertRaisesRegex(NativeWorkflowDefinitionError, "Invalid native PROJECT_CONFIG pin"):
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
