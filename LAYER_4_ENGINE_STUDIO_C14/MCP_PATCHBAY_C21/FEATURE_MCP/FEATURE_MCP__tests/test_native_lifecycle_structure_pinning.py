"""Pin the Structure snapshot before lifecycle selects captured rows."""
from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import NonCallableMock
import tempfile
import unittest

import yaml

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import capture_native


class NativeLifecycleStructurePinningTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        (self.root / '.git').mkdir()
        self.control = self.root / '.anechoic_test'
        self.control.mkdir()
        manifest = self.write('AN-S-1-PROJECT_MANIFEST--manifest.md', 'AN-S-1')
        self.path = self.write('001_TICKETS/TASKS/AN-T-1-TASK--example.md', 'AN-T-1')
        self.selection = NonCallableMock(
            spec_set=['root', 'control_root', 'manifest_path', 'manifest_sha256',
                'project_prefix', 'structure_snapshot', 'parameters',
                'control_relative'],
            root=self.root, control_root=self.control, manifest_path=manifest,
                                         manifest_sha256=sha256(manifest.read_bytes()).hexdigest(), project_prefix='AN')
        del self.selection.structure_snapshot, self.selection.parameters, self.selection.control_relative
        self.rows = capture_native(self.selection).atoms
        self.params = {'sourceCurrent': {'ref_id': 'AN-T-1', 'version': 1},
                       'changes': {'body': '\n# Summary\n\nExample\n\n## Details\n\nNew\n'}}
        manifest = self.selection.manifest_path
        manifest.write_text("""---
identity: {atom_id: AN-S-1}
context: {container: {component: C0}, tier: -1, lens: SPEC, template: project_manifest}
state: {status: active, version: 1}
---
## Summary

Manifest

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ProjectManifest
declare_entity(entity_name='Project Manifest', instance=ProjectManifest(name='Test', prefix='AN', lens_whitelist=['DES', 'SPEC']))
```
""")
        self.selection.manifest_sha256 = sha256(manifest.read_bytes()).hexdigest()


    def write(self, name, identity, *, version=1, status='active', template='task'):
        path = self.control / name
        path.parent.mkdir(parents=True, exist_ok=True)
        header = {'identity': {'atom_id': identity}, 'context': {'container': {'component': 'C0'}, 'template': template},
                  'state': {'status': status, 'version': version, 'updated_at': '2026-01-01'}}
        path.write_text('---\n' + yaml.safe_dump(header) + '---\n\n# Summary\n\nExample\n\n## Details\n\nOld\n')
        return path


    def spec(self, name, atom_id, lens='DES', component='C9'):
        path = self.write(name, atom_id)
        header, body = path.read_text().split('---\n', 2)[1:]
        data = yaml.safe_load(header)
        data['context'] = {'container': {'component': component}, 'lens': lens}
        path.write_text('---\n' + yaml.safe_dump(data) + '---\n' + body)
        return path


    def test_lifecycle_pins_structure_before_selecting_rows(self):
        from contextlib import nullcontext
        from unittest.mock import Mock, patch
        from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import NativeQueryInputs, NativeQueryOwner

        self.spec('UNIT_C9/__DES/AN-S-4-DES--example.md', 'AN-S-4')
        capture = capture_native(self.selection)
        self.selection.structure_snapshot = self.root / 'structure.json'
        self.selection.parameters = {}
        self.selection.control_relative = self.control.relative_to(self.root)
        first = Mock()
        first.component.return_value.source_path = 'AN-S-7-SPEC-COMPONENT_MANIFEST--unit.md'
        later = Mock()
        later.component.return_value.source_path = 'OTHER_C8/AN-S-7-SPEC--unit.md'
        published = [first]

        class Capture:
            versions = capture.versions
            carrier_hashes = capture.carrier_hashes
            errors = capture.errors
            ingestion_issues = capture.ingestion_issues
            containment = capture.containment
            status_domains = capture.status_domains
            classified_templates = capture.classified_templates

            @property
            def atoms(self):
                published[0] = later
                return capture.atoms

        owner = NativeQueryOwner(self.selection, NativeQueryInputs(lambda *args: None, frozenset(), {}))
        owner._store = SimpleNamespace(_available=True)
        owner._capture = Capture()
        owner_module = 'KERNEL_MIXER_C59.native_service_owner'
        with patch(f'{owner_module}.read_structure', side_effect=lambda path: published[0]) as read, \
                patch(f'{owner_module}.bind_native_runtime', return_value=nullcontext()), \
                patch.object(owner, '_refresh_after_write'):
            output = owner.lifecycle('atom_lifecycle_create_draft', {
                'sourceCurrent': {'ref_id': 'AN-S-4', 'version': 1},
            })
        self.assertEqual('completed', output['outcome'], output)
        read.assert_called_once_with(self.selection.structure_snapshot)
        first.component.assert_called_once_with('C9')
        later.component.assert_not_called()


