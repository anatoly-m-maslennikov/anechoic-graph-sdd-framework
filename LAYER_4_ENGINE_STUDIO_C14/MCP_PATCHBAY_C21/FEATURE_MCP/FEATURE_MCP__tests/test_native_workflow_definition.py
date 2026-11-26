"""Exercise installed status pins through the native Workbench owner."""

from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest

import yaml

MCP = Path(__file__).resolve().parents[1]
STUDIO = MCP.parents[1]
PROGRAMMATIC = STUDIO / "FEATURE_PROGRAMMATIC"

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__shared import resolve_native_project  # noqa: E402


class NativeWorkflowStatusIntegrationTests(unittest.TestCase):
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

    def _write(self, relative, header, body):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"---\n{yaml.safe_dump(header)}---\n\n{body}", encoding="utf-8")
        return path

    def _install_status_fixture(self):
        control = ".anechoic_anechoic"
        ontology = Path(control) / "LAYER_2_META_METHODOLOGY_C58/_DOM/MTD"
        source = STUDIO.parent / "_anechoic_anechoic/ONTOLOGY_SCORE_C82/OCCURRENT_METRONOME_C58/_DOM/MTD"
        refs = ("AN-S-1928@5", "AN-S-1834@1", "AN-S-1831@2")
        rows = []
        for ref in refs:
            atom_id = ref.partition("@")[0]
            original, = source.rglob(f"{atom_id}-MTD-*.md")
            relative = ontology / original.name
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(original.read_bytes())
            rows.append({"_exact_ref": ref, "status_group": "Current", "source_path": relative.as_posix(),
                         "_source_sha256": sha256(path.read_bytes()).hexdigest()})
        return rows

    def test_status_action_uses_native_specifications(self):
        from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import NativeQueryOwner
        from .test_native_query_stdio import _native_inputs
        from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared import polling_source_watcher

        self._install_status_fixture()
        path = self._write(f'{self.control}/__TKT/TASKS/AN-T-4-TASK--verify.md', {
            'identity': {'atom_id': 'AN-T-4'},
            'context': {'template': 'TASK', 'container': {'component': 'C0'}},
            'state': {'status': 'active', 'version': 3, 'updated_at': '2026-11-19T00:00:00Z'},
        }, '## Summary\n\nVerify the status action.\n')
        self.enterContext(polling_source_watcher())
        owner = NativeQueryOwner(self.selection, _native_inputs())
        self.addCleanup(owner.close)
        owner.start()
        status_pins = sorted(("AN-S-1928@5", "AN-S-1834@1", "AN-S-1831@2"))
        pins_sql = (
            "SELECT exact_ref FROM native_references WHERE exact_ref IN ("
            + ", ".join(f"'{pin}'" for pin in status_pins)
            + ") ORDER BY exact_ref"
        )
        expected_pins = [[pin] for pin in status_pins]
        self.assertEqual(expected_pins, owner.run(pins_sql, result_delivery='inline')['rows'])
        ticket_sql = (
            'SELECT a.relative_path, a."header.state.status", a."header.state.version", r.exact_ref '
            'FROM atoms a JOIN native_references r USING (relative_path) '
            "WHERE r.stable_ref = 'AN-T-4'"
        )
        self.assertEqual([[
            f'{self.control}/__TKT/TASKS', 'active', 3, 'AN-T-4@3',
        ]], owner.run(ticket_sql, result_delivery='inline')['rows'])
        outcome = owner.lifecycle('atom_lifecycle_change_status', {
            'target': {'ref_id': 'AN-T-4', 'version': 3}, 'targetStatus': 'Backlog',
        })
        self.assertEqual('completed', outcome['outcome'], outcome)
        self.assertFalse(path.exists())
        self.assertTrue((path.parent / 'backlog' / path.name).is_file())
        self.assertEqual(expected_pins, owner.run(pins_sql, result_delivery='inline')['rows'])
        ticket, = owner.run(ticket_sql, result_delivery='inline')['rows']
        self.assertEqual('AN-T-4@3', ticket[3])
        self.assertEqual('backlog', ticket[1])
        self.assertIn('/TASKS/backlog', ticket[0])

    def test_lifecycle_cannot_revise_or_promote_installed_status_pin(self):
        from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import NativeQueryOwner
        from .test_native_query_stdio import _native_inputs
        from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared import polling_source_watcher

        rows = self._install_status_fixture()
        self.enterContext(polling_source_watcher())
        owner = NativeQueryOwner(self.selection, _native_inputs())
        self.addCleanup(owner.close)
        owner.start()
        atom_id, _, version = rows[0]['_exact_ref'].partition('@')
        for name, field, target in (
            ('atom_lifecycle_update', 'sourceCurrent', {'ref_id': atom_id, 'version': int(version)}),
            ('atom_lifecycle_promote_draft', 'target', {'ref_id': f'{atom_id}@2-draft', 'version': 2}),
        ):
            with self.subTest(name=name):
                result = owner.lifecycle(name, {field: target})
                self.assertEqual('needs_input', result['outcome'])
                self.assertIn('runtime binding', result['requested_input'][field]['error'])


if __name__ == "__main__":
    unittest.main()
