from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace
import sys
import tempfile
import unittest
from unittest.mock import patch

import yaml

TOOLS = Path(__file__).resolve().parents[1]
ENGINE = TOOLS.parents[1]
sys.path[:0] = [str(TOOLS), str(ENGINE / 'IWE_CONSOLE_C43')]

from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.native_source_rows import capture_native
from ATOM_LIFECYCLE.common import InputError, SourceChanged
from ATOM_LIFECYCLE.native_draft import create_draft, promote_draft
from native_carrier_header import canonical_native_header


class NativeDraftTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        (self.root / '.git').mkdir()
        self.control = self.root / '.anechoic_test'
        self.control.mkdir()
        manifest = self.write('AN-S-1-PROJECT_MANIFEST--manifest.md', 'AN-S-1')
        self.path = self.write('001_TICKETS/TASKS/AN-T-1-TASK--example.md', 'AN-T-1')
        self.selection = SimpleNamespace(root=self.root, control_root=self.control, manifest_path=manifest,
                                         manifest_sha256=sha256(manifest.read_bytes()).hexdigest(), project_prefix='AN')
        self.rows = capture_native(self.selection).atoms
        self.params = {'sourceCurrent': {'ref_id': 'AN-T-1', 'version': 1},
                       'changes': {'body': '\n# Summary\n\nExample\n\n## Details\n\nNew\n'}}

    def write(self, name, identity, *, version=1, status='active', template='task'):
        path = self.control / name
        path.parent.mkdir(parents=True, exist_ok=True)
        header = {'identity': {'atom_id': identity}, 'context': {'container': {'component': 'C0'}, 'template': template},
                  'state': {'status': status, 'version': version, 'updated_at': '2026-01-01'}}
        path.write_text('---\n' + yaml.safe_dump(header) + '---\n\n# Summary\n\nExample\n\n## Details\n\nOld\n')
        return path

    def test_creates_next_version_without_changing_current_or_manifest(self):
        self.write('001_TICKETS/TASKS/09_archived/AN-T-1@4-TASK--example.md', 'AN-T-1', version=4, status='archived')
        self.write('001_TICKETS/TASKS/01_draft/AN-T-1@5-draft-TASK--example.md', 'AN-T-1', version=5, status='draft')
        current, manifest = self.path.read_bytes(), self.selection.manifest_path.read_bytes()
        output = create_draft(self.selection, self.params, current_rows=self.rows)
        self.assertEqual('completed', output['outcome'])
        self.assertEqual('AN-T-1@6-draft', output['savedDraft']['ref_id'])
        target = self.root / output['savedDraft']['path']
        self.assertEqual(self.control / '001_TICKETS/TASKS/01_draft/AN-T-1@6-draft-TASK--example.md', target)
        self.assertEqual('create', output['effects'][-1]['operation'])
        self.assertEqual(current, self.path.read_bytes())
        self.assertEqual(manifest, self.selection.manifest_path.read_bytes())
        after = capture_native(self.selection)
        self.assertFalse(after.errors)
        row = next(row for row in after.atoms if row['_exact_ref'] == 'AN-T-1@6-draft')
        self.assertEqual('draft', row['status'])
        source_header = next(row for row in self.rows if row['id'] == 'AN-T-1')['header_json']
        self.assertEqual(source_header['identity'], row['header_json']['identity'])
        self.assertEqual(source_header['context'], row['header_json']['context'])
        self.assertEqual(6, row['header_json']['state']['version'])
        self.assertEqual(self.params['changes']['body'].encode(), row['_content_bytes'])

    def test_canonical_ticket_revision_preserves_archived_body(self):
        _, header, body = self.path.read_text().split('---', 2)
        canonical = canonical_native_header(yaml.safe_load(header))
        self.path.write_text('---\n' + yaml.safe_dump(canonical, sort_keys=False) + '---' + body)
        output = create_draft(self.selection, self.params, current_rows=capture_native(self.selection).atoms)
        ref = output['savedDraft']['ref_id']
        result = promote_draft(self.selection, {'target': {'ref_id': ref, 'version': 2}, 'targetStatus': 'backlog'},
                               current_rows=capture_native(self.selection).atoms)
        self.assertEqual('completed', result['outcome'])
        archive = self.control / '001_TICKETS/TASKS/09_archived/AN-T-1@1-TASK--example.md'
        _, archived_header, archived_body = archive.read_text().split('---', 2)
        archived = yaml.safe_load(archived_header)
        self.assertEqual(body, archived_body)
        self.assertEqual({**canonical, 'state': archived['state']}, archived)
        self.assertEqual('archived', archived['state']['status'])
        self.assertIn('New', (self.path.parent / 'backlog' / self.path.name).read_text())

    def test_missing_changes_preserves_body(self):
        output = create_draft(self.selection, {'sourceCurrent': self.params['sourceCurrent']}, current_rows=self.rows)
        target = self.root / output['savedDraft']['path']
        self.assertEqual(self.path.read_bytes().split(b'---\n', 2)[2], target.read_bytes().split(b'---\n', 2)[2])

    def test_rejects_stale_and_out_of_scope_inputs(self):
        for case in ('version', 'selector', 'foreign', 'digest', 'path', 'bytes', 'summary', 'extra', 'template', 'manifest'):
            with self.subTest(case=case):
                rows = [dict(row) for row in self.rows]
                params = {'sourceCurrent': dict(self.params['sourceCurrent']), 'changes': dict(self.params['changes'])}
                row = next(row for row in rows if row['id'] == 'AN-T-1')
                original, manifest = self.path.read_bytes(), self.selection.manifest_path.read_bytes()
                if case == 'version': params['sourceCurrent']['version'] = 2
                if case == 'selector': params['sourceCurrent']['extra'] = 'x'
                if case == 'foreign': params['sourceCurrent']['ref_id'] = 'XX-T-1'
                if case == 'digest': row.pop('_source_sha256')
                if case == 'path': row['source_path'] = '../escape.md'
                if case == 'bytes': self.path.write_bytes(original.replace(b'Old', b'Altered'))
                if case == 'summary': params['changes']['body'] = params['changes']['body'].replace('Example', 'Changed')
                if case == 'extra': params['changes']['status'] = 'done'
                if case == 'template': row['header_json'] = {**row['header_json'], 'context': {'template': 'epic'}}
                if case == 'manifest': self.selection.manifest_path.write_bytes(manifest + b'changed')
                with self.assertRaises((InputError, SourceChanged)):
                    create_draft(self.selection, params, current_rows=rows)
                self.assertFalse((self.control / '001_TICKETS/TASKS/01_draft').exists())
                self.path.write_bytes(original)
                self.selection.manifest_path.write_bytes(manifest)

    def test_symlink_draft_directory_cannot_escape(self):
        outside = self.root / 'outside'
        outside.mkdir()
        (self.control / '001_TICKETS/TASKS/01_draft').symlink_to(outside, target_is_directory=True)
        output = create_draft(self.selection, self.params, current_rows=self.rows)
        self.assertEqual('failed', output['outcome'])
        self.assertTrue(output['errors'])
        self.assertEqual([], list(outside.iterdir()))

    def test_wrong_branch_and_template_are_rejected(self):
        for name, template in [('001_TICKETS/ISSUES/AN-T-2-TASK--example.md', 'task'),
                               ('001_TICKETS/TASKS/AN-T-3-QUESTION--example.md', 'question')]:
            identity = 'AN-T-2' if template == 'task' else 'AN-T-3'
            self.write(name, identity, template=template)
            rows = capture_native(self.selection).atoms
            with self.assertRaises((InputError, SourceChanged)):
                create_draft(self.selection, {'sourceCurrent': {'ref_id': identity, 'version': 1}}, current_rows=rows)


class NativeRevisionCarrierTests(unittest.TestCase):
    write = NativeDraftTests.write

    def setUp(self):
        NativeDraftTests.setUp(self)
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
        sys.path.insert(0, str(ENGINE / 'MCP_PATCHBAY_C21' / 'FEATURE_MCP'))
        from native_query import NativeQueryInputs, NativeQueryOwner

        self.spec('UNIT_C9/__DES/AN-S-4-DES--example.md', 'AN-S-4')
        rows = capture_native(self.selection).atoms
        self.selection.structure_snapshot = self.root / 'structure.json'
        self.selection.parameters = {}
        self.selection.control_relative = self.control.relative_to(self.root)
        first = Mock()
        first.component.return_value.source_path = 'AN-S-7-SPEC-COMPONENT_MANIFEST--unit.md'
        later = Mock()
        later.component.return_value.source_path = 'OTHER_C8/AN-S-7-SPEC--unit.md'
        published = [first]

        class Capture:
            @property
            def atoms(self):
                published[0] = later
                return rows

        owner = NativeQueryOwner(self.selection, NativeQueryInputs(lambda *args: None, frozenset(), {}))
        owner._store = SimpleNamespace(_available=True)
        owner._capture = Capture()
        with patch('native_query.read_structure', side_effect=lambda path: published[0]) as read, \
                patch('project_runtime.bind_native_runtime', return_value=nullcontext()), \
                patch.object(owner, '_refresh_after_write'):
            output = owner.lifecycle('atom_lifecycle_create_draft', {
                'sourceCurrent': {'ref_id': 'AN-S-4', 'version': 1},
            })
        self.assertEqual('completed', output['outcome'], output)
        read.assert_called_once_with(self.selection.structure_snapshot)
        first.component.assert_called_once_with('C9')
        later.component.assert_not_called()

    def test_revision_archives_existing_epic_spec_and_pmeta(self):
        cases = [
            ('001_TICKETS/TASKS/AN-T-4-EPIC--example.md', 'AN-T-4', 'epic', '001_TICKETS/TASKS'),
            ('UNIT_C9/__DES/__DOM/AN-S-4-DOM--example.md', 'AN-S-4', 'spec', 'UNIT_C9'),
            ('_PMETA/AN-P-4-ACTION--example.md', 'AN-P-4', 'action', '_PMETA'),
            ('UNIT_C9/AN-S-5-SPEC--example.md', 'AN-S-5', 'root_spec', 'UNIT_C9'),
        ]
        for name, atom_id, kind, owner in cases:
            with self.subTest(kind=kind):
                if kind in {'spec', 'root_spec'}:
                    path = self.spec(name, atom_id, 'DES/DOM' if kind == 'spec' else 'SPEC')
                else:
                    path = self.write(name, atom_id, template=kind)
                old = path.read_bytes().split(b'---\n', 2)[2]
                rows = capture_native(self.selection).atoms
                output = create_draft(self.selection, {'sourceCurrent': {'ref_id': atom_id, 'version': 1},
                    'changes': {'body': old.decode().replace('Old', 'New')}}, current_rows=rows)
                draft = self.root / output['savedDraft']['path']
                self.assertEqual(self.control / owner / '01_draft', draft.parent)
                ref = output['savedDraft']['ref_id']
                result = promote_draft(self.selection, {'target': {'ref_id': ref, 'version': 2},
                    'targetStatus': 'ready' if atom_id.startswith('AN-S-') else 'active'}, current_rows=capture_native(self.selection).atoms)
                self.assertEqual('completed', result['outcome'])
                rows = capture_native(self.selection)
                self.assertFalse(rows.errors)
                archived = next(row for row in rows.atoms if row['_exact_ref'] == atom_id + '@1')
                self.assertEqual(old, archived['_content_bytes'])
                self.assertIn(b'New', (self.root / result['artifact']['path']).read_bytes())
                self.assertFalse(draft.exists())

    def test_legacy_pmeta_revision_serializes_project_config(self):
        path = self.write('002_PROJECT_CONFIG/AN-P-4-ACTION--example.md', 'AN-P-4', template='action')
        _, text, body = path.read_text().split('---', 2)
        header = canonical_native_header(yaml.safe_load(text))
        header['atom_family'] = 'PMETA'
        header['relations'] = {'REFERENCES': ['AN-S-1@1']}
        path.write_text('---\n' + yaml.safe_dump(header, sort_keys=False) + '---' + body)
        original = path.read_bytes()
        rows = lambda: capture_native(self.selection).atoms
        output = create_draft(self.selection, {'sourceCurrent': {'ref_id': 'AN-P-4', 'version': 1}}, current_rows=rows())
        draft = self.root / output['savedDraft']['path']
        _, draft_text, draft_body = draft.read_text().split('---', 2)
        self.assertEqual('PROJECT_CONFIG', yaml.safe_load(draft_text)['atom_family'])
        self.assertEqual(body, draft_body)
        self.assertEqual(original, path.read_bytes())
        result = promote_draft(self.selection, {'target': {'ref_id': 'AN-P-4@2-draft', 'version': 2},
                                                'targetStatus': 'active'}, current_rows=rows())
        for saved in (self.root / result['artifact']['path'],
                      self.control / '002_PROJECT_CONFIG/09_archived/AN-P-4@1-ACTION--example.md'):
            _, saved_text, saved_body = saved.read_text().split('---', 2)
            saved_header = yaml.safe_load(saved_text)
            self.assertEqual('PROJECT_CONFIG', saved_header['atom_family'])
            self.assertEqual(header['relations'], saved_header['relations'])
            self.assertEqual(body, saved_body)

    def test_task_promotion_rejects_status_change_with_flat_child(self):
        child = self.write('001_TICKETS/TASKS/AN-T-2-TASK--child.md', 'AN-T-2')
        _, header, body = child.read_text().split('---', 2)
        metadata = yaml.safe_load(header)
        metadata['context']['container'] = {'atom': 'AN-T-1'}
        child.write_text('---\n' + yaml.safe_dump(metadata) + '---' + body)
        result = create_draft(self.selection, self.params, current_rows=capture_native(self.selection).atoms)
        draft = self.root / result['savedDraft']['path']
        before = self.path.read_bytes(), child.read_bytes(), draft.read_bytes()
        with self.assertRaisesRegex(InputError, 'container'):
            promote_draft(self.selection,
                {'target': {'ref_id': result['savedDraft']['ref_id'], 'version': 2}, 'targetStatus': 'done'},
                current_rows=capture_native(self.selection).atoms)
        self.assertEqual(before, (self.path.read_bytes(), child.read_bytes(), draft.read_bytes()))

    def test_epic_body_revision_preserves_child_carrier(self):
        epic = self.write('001_TICKETS/TASKS/AN-T-4-EPIC--example.md', 'AN-T-4', template='epic')
        child = self.write('001_TICKETS/TASKS/AN-T-4-EPIC--example/done/AN-T-5-TASK--example.md', 'AN-T-5', status='done')
        _, header, body = child.read_text().split('---', 2)
        metadata = yaml.safe_load(header)
        metadata['context']['container'] = {'atom': 'AN-T-4'}
        child.write_text('---\n' + yaml.safe_dump(metadata) + '---' + body)
        before = child.read_bytes()
        result = create_draft(self.selection,
            {'sourceCurrent': {'ref_id': 'AN-T-4', 'version': 1},
             'changes': {'body': epic.read_text().split('---', 2)[2].replace('Old', 'New')}},
            current_rows=capture_native(self.selection).atoms)
        result = promote_draft(self.selection,
            {'target': {'ref_id': result['savedDraft']['ref_id'], 'version': 2}, 'targetStatus': 'active'},
            current_rows=capture_native(self.selection).atoms)
        self.assertEqual('completed', result['outcome'])
        self.assertEqual(before, child.read_bytes())

    def test_existing_component_lens_can_override_project_whitelist(self):
        manifest = self.selection.manifest_path
        manifest.write_text(manifest.read_text().replace("['DES', 'SPEC']", "['SPEC']"))
        self.selection.manifest_sha256 = sha256(manifest.read_bytes()).hexdigest()
        component = self.spec('AN-S-7-SPEC-COMPONENT_MANIFEST--unit.md', 'AN-S-7', 'SPEC', 'C0')
        header, body = component.read_text().split('---\n', 2)[1:]
        component_header = yaml.safe_load(header)
        component_header['context']['template'] = 'component_manifest'
        component.write_text('---\n' + yaml.safe_dump(component_header) + '---\n' + body
                             + '\n### Component ID\n\nC9\n\n### Lens Whitelist\n\n["DevOps/RunTime"]\n')
        path = self.spec('UNIT_C9/__DEVOPS/__RUNTIME/AN-S-6-RUNTIME--example.md', 'AN-S-6', 'DevOps/RunTime')
        previous_header = next(row for row in capture_native(self.selection).atoms if row['id'] == 'AN-S-6')['header_json']
        output = create_draft(self.selection, {'sourceCurrent': {'ref_id': 'AN-S-6', 'version': 1},
            'changes': {'body': path.read_text().split('---\n', 2)[2].replace('Old', 'New')}},
            current_rows=capture_native(self.selection).atoms)
        ref = output['savedDraft']['ref_id']
        result = promote_draft(self.selection, {'target': {'ref_id': ref, 'version': 2}, 'targetStatus': 'ready'},
                               current_rows=capture_native(self.selection).atoms)
        self.assertEqual('completed', result['outcome'])
        current = next(row for row in capture_native(self.selection).atoms if row['_exact_ref'] == 'AN-S-6@2')
        self.assertEqual(previous_header['context'], current['header_json']['context'])
        self.assertIn(b'New', current['_content_bytes'])

    def test_rejects_manifest_and_nested_paths(self):
        cases = [
            (self.selection.manifest_path, 'AN-S-1'),
            (self.spec('UNIT_C9/__DES/nested/AN-S-9-DES--example.md', 'AN-S-9'), 'AN-S-9'),
            (self.spec('UNIT_C9/DES/AN-S-10-DES--example.md', 'AN-S-10'), 'AN-S-10'),
            (self.write('_PMETA/nested/AN-P-9-ACTION--example.md', 'AN-P-9'), 'AN-P-9'),
        ]
        for path, atom_id in cases:
            with self.subTest(atom_id=atom_id):
                with self.assertRaises(InputError):
                    create_draft(self.selection, {'sourceCurrent': {'ref_id': atom_id, 'version': 1}},
                                 current_rows=capture_native(self.selection).atoms)

    def test_first_unpinned_spec_publishes_its_version_and_cleans_up(self):
        for atom_id, lens, version in [('AN-S-8', 'SWD', 1), ('AN-S-9', 'SPEC', 3)]:
            suffix = lens + '--example.md'
            ref = f'{atom_id}@{version}-draft'
            draft = self.spec(f'UNIT_C9/01_draft/{ref}-{suffix}', atom_id, lens)
            header, body = draft.read_text().split('---\n', 2)[1:]
            data = yaml.safe_load(header)
            data['state'].update(status='draft', version=version)
            data['context']['tier'] = 3
            draft.write_text('---\n' + yaml.safe_dump(canonical_native_header(data), sort_keys=False) + '---\n' + body)
            params = {'target': {'ref_id': ref, 'version': version}, 'targetStatus': 'ready'}
            result = promote_draft(self.selection, params, current_rows=capture_native(self.selection).atoms)
            self.assertEqual('completed', result['outcome'], result)
            current = self.control / 'UNIT_C9' / '02_ready' / f'{atom_id}-{suffix}'
            self.assertEqual((current, version), (self.root / result['artifact']['path'], result['artifact']['version']))
            self.assertFalse(draft.exists())
            self.assertEqual(['create', 'remove'], [e['operation'] for e in result['effects'] if e.get('evidence') != 'directory'])
            self.assertFalse(capture_native(self.selection).errors)

    def test_first_spec_cleanup_failure_can_retry_without_rewriting(self):
        from unittest.mock import patch
        from ATOM_LIFECYCLE import effects
        draft = self.spec('UNIT_C9/01_draft/AN-S-8@1-draft-DES--example.md', 'AN-S-8')
        draft.write_text(draft.read_text().replace('status: active', 'status: draft'))
        params = {'target': {'ref_id': 'AN-S-8@1-draft', 'version': 1}, 'targetStatus': 'ready'}
        with patch('ATOM_LIFECYCLE.native_draft.effects.remove', return_value=effects.Result(errors=[{'code': 'injected'}])):
            result = promote_draft(self.selection, params, current_rows=capture_native(self.selection).atoms)
        self.assertEqual('failed', result['outcome'])
        self.assertNotIn('artifact', result)
        self.assertTrue(draft.exists())
        result = promote_draft(self.selection, params, current_rows=capture_native(self.selection).atoms)
        self.assertEqual('completed', result['outcome'])
        self.assertEqual(['remove'], [e['operation'] for e in result['effects']])
        self.assertFalse(draft.exists())

    def test_first_spec_preserves_other_drafts(self):
        old = self.spec('UNIT_C9/01_draft/AN-S-8@1-draft-DES--example.md', 'AN-S-8')
        old.write_text(old.read_text().replace('status: active', 'status: draft'))
        draft = self.spec('UNIT_C9/01_draft/AN-S-8@2-draft-DES--example.md', 'AN-S-8')
        draft.write_text(draft.read_text().replace('status: active', 'status: draft').replace('version: 1', 'version: 2'))
        original = old.read_bytes()
        result = promote_draft(self.selection,
            {'target': {'ref_id': 'AN-S-8@2-draft', 'version': 2}, 'targetStatus': 'ready'},
            current_rows=capture_native(self.selection).atoms)
        self.assertEqual('completed', result['outcome'])
        self.assertEqual(2, result['artifact']['version'])
        self.assertEqual(original, old.read_bytes())
        self.assertFalse(draft.exists())

    def test_first_spec_rejects_unsafe_or_stale_inputs(self):
        for case in ('owner', 'lens', 'template', 'manifest_name', 'filename', 'history', 'stale', 'status'):
            with self.subTest(case=case):
                name = ('SPEC-PROJECT_MANIFEST--example.md' if case == 'manifest_name' else
                        'SWD--example.md' if case == 'filename' else 'DES--example.md')
                draft = self.spec(f'UNIT_C9/01_draft/AN-S-8@1-draft-{name}', 'AN-S-8',
                                  'invalid/lens!' if case == 'lens' else 'DES', 'C8' if case == 'owner' else 'C9')
                header, body = draft.read_text().split('---\n', 2)[1:]
                data = yaml.safe_load(header)
                data['state']['status'] = 'draft'
                if case == 'filename':
                    data['context']['tier'] = 3
                if case == 'template':
                    data['context']['template'] = 'component_manifest'
                draft.write_text('---\n' + yaml.safe_dump(canonical_native_header(data) if case == 'filename' else data) + '---\n' + body)
                history = None
                if case == 'history':
                    history = self.spec('UNIT_C9/09_archived/AN-S-8@2-DES--example.md', 'AN-S-8')
                    history.write_text(history.read_text().replace('status: active', 'status: archived').replace('version: 1', 'version: 2'))
                rows = capture_native(self.selection).atoms
                if case == 'stale':
                    draft.write_bytes(draft.read_bytes() + b'changed')
                before = {p.relative_to(self.control): p.read_bytes() for p in self.control.rglob('*.md')}
                params = {'target': {'ref_id': 'AN-S-8@1-draft', 'version': 1},
                          'targetStatus': 'done' if case == 'status' else 'ready'}
                with self.assertRaises((InputError, SourceChanged)):
                    promote_draft(self.selection, params, current_rows=rows)
                self.assertEqual(before, {p.relative_to(self.control): p.read_bytes() for p in self.control.rglob('*.md')})
                draft.unlink()
                if history:
                    history.unlink()

    def test_spec_retry_after_cleanup_failure(self):
        from unittest.mock import patch
        from ATOM_LIFECYCLE import effects
        self.spec('UNIT_C9/__DES/AN-S-4-DES--example.md', 'AN-S-4')
        output = create_draft(self.selection, {'sourceCurrent': {'ref_id': 'AN-S-4', 'version': 1}},
                              current_rows=capture_native(self.selection).atoms)
        ref = output['savedDraft']['ref_id']
        params = {'target': {'ref_id': ref, 'version': 2}, 'targetStatus': 'ready'}
        original_remove = effects.remove
        def remove(root, path, digest):
            return effects.Result(errors=[{'code': 'injected'}]) if path.parent.name == '01_draft' else original_remove(root, path, digest)
        with patch('ATOM_LIFECYCLE.native_draft.effects.remove', side_effect=remove):
            result = promote_draft(self.selection, params, current_rows=capture_native(self.selection).atoms)
        self.assertEqual('failed', result['outcome'])
        result = promote_draft(self.selection, params, current_rows=capture_native(self.selection).atoms)
        self.assertEqual('completed', result['outcome'])
        self.assertEqual(['remove'], [effect['operation'] for effect in result['effects']])


class NewNativeTaskTests(unittest.TestCase):
    write = NativeDraftTests.write

    def setUp(self):
        NativeDraftTests.setUp(self)
        self.new = {'newAtom': {'template': 'task', 'container': {'component': 'C00'},
                                'body': '\n## Summary\n\nCreate a Task!\n\n## Work\n\nDo it.\n'}}

    def test_new_task_allocates_across_history_and_promotes_version_one(self):
        self.write('001_TICKETS/ISSUES/09_archived/AN-T-8@2-QUESTION--old.md', 'AN-T-8', version=2, status='archived', template='question')
        before = self.path.read_bytes(), self.selection.manifest_path.read_bytes()
        result = create_draft(self.selection, self.new, current_rows=self.rows)
        self.assertEqual('AN-T-9@1-draft', result['savedDraft']['ref_id'])
        draft = self.root / result['savedDraft']['path']
        header = yaml.safe_load(draft.read_text().split('---', 2)[1])
        self.assertEqual(('TKT', 'AN-T-9', 2),
                         (header['atom_family'], header['atom_id'], header['priority']))
        self.assertEqual({'template': 'task', 'label': 'Task'}, header['context'])
        self.assertEqual('AN-T-9@1-draft-TASK--create-a-task.md', draft.name)
        rows = capture_native(self.selection).atoms
        result = promote_draft(self.selection, {'target': {'ref_id': 'AN-T-9@1-draft', 'version': 1}, 'targetStatus': 'backlog'},
                               current_rows=rows)
        self.assertEqual(('AN-T-9', 1, 'backlog'), (result['artifact']['ref_id'], result['artifact']['version'], result['artifact']['status']))
        self.assertFalse(draft.exists())
        from ATOM_LIFECYCLE.native_update import change_ticket_status
        target = {'ref_id': 'AN-T-9', 'version': 1}
        queued = change_ticket_status(self.selection, {'target': target, 'targetStatus': 'in_queue'},
                                      current_rows=capture_native(self.selection).atoms, check_definition=lambda: None)
        self.assertEqual(self.control / '001_TICKETS/TASKS', (self.root / queued['artifact']['path']).parent)
        with self.assertRaises(InputError):
            change_ticket_status(self.selection, {'target': target, 'targetStatus': 'in_progress'},
                                 current_rows=capture_native(self.selection).atoms, check_definition=lambda: None)
        done = change_ticket_status(self.selection, {'target': target, 'targetStatus': 'done'},
                                    current_rows=capture_native(self.selection).atoms, check_definition=lambda: None)
        self.assertEqual('done', done['artifact']['status'])
        capture = capture_native(self.selection)
        self.assertFalse(capture.errors)
        self.assertIn('AN-T-9@1', [row['_exact_ref'] for row in capture.atoms])
        self.assertEqual(before, (self.path.read_bytes(), self.selection.manifest_path.read_bytes()))

    def test_new_draft_publishes_nested_drafts_and_preserves_assets(self):
        created = create_draft(self.selection, self.new, current_rows=self.rows)
        ref = created['savedDraft']['ref_id']
        draft = self.root / created['savedDraft']['path']
        labels = ('Task', 'Epic', 'Version')
        child_result = create_draft(self.selection, {'newAtom': {
            'template': 'task', 'label': 'Epic', 'container': {'atom': ref.split('@')[0]},
            'body': '\n## Summary\n\nChild\n'}}, current_rows=capture_native(self.selection).atoms,
            ticket_labels=labels)
        child = self.root / child_result['savedDraft']['path']
        self.assertEqual(draft.with_suffix('') / '01_draft', child.parent)
        child_id = child_result['savedDraft']['atom_id']
        grand_result = create_draft(self.selection, {'newAtom': {
            'template': 'task', 'label': 'Version', 'container': {'atom': child_id},
            'body': '\n## Summary\n\nGrand\n'}}, current_rows=capture_native(self.selection).atoms,
            ticket_labels=labels)
        grand = self.root / grand_result['savedDraft']['path']
        asset = grand.parent.parent / 'notes.txt'
        asset.write_text('keep')
        outcome = promote_draft(self.selection, {'target': {'ref_id': ref, 'version': 1}, 'targetStatus': 'backlog'},
                                current_rows=capture_native(self.selection).atoms)
        self.assertEqual('completed', outcome['outcome'], outcome)
        parent = self.root / outcome['artifact']['path']
        child_current = parent.with_suffix('') / f'backlog/{child_id}-EPIC--child.md'
        grand_id = grand_result['savedDraft']['atom_id']
        grand_current = child_current.with_suffix('') / f'backlog/{grand_id}-VERSION--grand.md'
        header = yaml.safe_load(grand_current.read_text().split('---', 2)[1])
        self.assertEqual('backlog', header['state']['status'])
        self.assertEqual({'template': 'task', 'label': 'Version'}, header['context'])
        self.assertEqual('keep', (child_current.with_suffix('') / 'notes.txt').read_text())
        self.assertFalse(draft.exists())

    def test_draft_tree_destination_collision_has_no_effect(self):
        created = create_draft(self.selection, self.new, current_rows=self.rows)
        ref = created['savedDraft']['ref_id']
        draft = self.root / created['savedDraft']['path']
        child = draft.with_suffix('') / '01_draft/AN-T-10@1-draft-TASK--child.md'
        child.parent.mkdir(parents=True)
        header = {'identity': {'atom_id': 'AN-T-10'},
                  'context': {'container': {'atom': ref.split('@')[0]}, 'template': 'task'},
                  'state': {'status': 'draft', 'version': 1, 'updated_at': '2026-01-01'}}
        child.write_text('---\n' + yaml.safe_dump(header) + '---\n\n## Summary\n\nChild\n')
        collision = child.parent.parent / 'backlog/AN-T-10-TASK--child'
        collision.mkdir(parents=True)
        before = draft.read_bytes(), child.read_bytes()
        outcome = promote_draft(self.selection, {'target': {'ref_id': ref, 'version': 1}, 'targetStatus': 'backlog'},
                                current_rows=capture_native(self.selection).atoms)
        self.assertEqual('destination_exists', outcome['errors'][0]['code'])
        self.assertEqual(before, (draft.read_bytes(), child.read_bytes()))
        self.assertTrue(collision.is_dir())

    def test_incomplete_child_companion_blocks_parent_retry(self):
        parent = create_draft(self.selection, self.new, current_rows=self.rows)['savedDraft']
        child = create_draft(self.selection, {'newAtom': {
            'template': 'task', 'container': {'atom': parent['atom_id']}, 'body': '## Summary\n\nChild\n',
        }}, current_rows=capture_native(self.selection).atoms)['savedDraft']
        companion = (self.root / child['path']).with_suffix('')
        companion.mkdir()
        note = companion / 'notes.txt'
        note.write_text('keep')
        params = {'target': {'ref_id': parent['ref_id'], 'version': 1}, 'targetStatus': 'backlog'}

        def partial_move(root, source, destination):
            destination.mkdir()
            return SimpleNamespace(effects=[{'operation': 'create', 'target': str(destination)}],
                                   errors=[{'code': 'backend_failure', 'message': 'copy interrupted'}])

        with patch('ATOM_LIFECYCLE.native_update.move_directory', side_effect=partial_move):
            outcome = promote_draft(self.selection, params, current_rows=capture_native(self.selection).atoms)
        self.assertEqual('backend_failure', outcome['errors'][0]['code'])
        with self.assertRaisesRegex(InputError, 'interrupted child publication'):
            promote_draft(self.selection, params, current_rows=capture_native(self.selection).atoms)
        self.assertEqual('keep', note.read_text())
        self.assertTrue((self.root / parent['path']).is_file())

    def test_new_epic_and_sub_epic_create_and_promote(self):
        self.new['newAtom']['template'] = 'epic'
        for container, label in (({'component': 'C00'}, 'EPIC'), ({'atom': 'AN-T-2'}, 'SUB_EPIC')):
            self.new['newAtom']['container'] = container
            result = create_draft(self.selection, self.new, current_rows=capture_native(self.selection).atoms)
            draft = self.root / result['savedDraft']['path']
            self.assertIn(f'-{label}--', draft.name)
            result = promote_draft(self.selection,
                {'target': {'ref_id': result['savedDraft']['ref_id'], 'version': 1}, 'targetStatus': 'backlog'},
                current_rows=capture_native(self.selection).atoms)
            self.assertEqual('completed', result['outcome'])
            self.assertIn(f'-{label}--', result['artifact']['path'])
            self.assertFalse(draft.exists())
        self.assertFalse(capture_native(self.selection).errors)

    def test_epic_uses_admitted_project_component(self):
        self.new['newAtom'].update(template='epic', container={'component': 'C21'})
        snapshot = SimpleNamespace(components={'C21': object()})
        result = create_draft(self.selection, self.new, current_rows=self.rows, structure_snapshot=snapshot)
        draft = self.root / result['savedDraft']['path']
        header = yaml.safe_load(draft.read_text().split('---', 2)[1])
        self.assertEqual({'component': 'C21'}, header['container'])
        result = promote_draft(self.selection,
            {'target': {'ref_id': result['savedDraft']['ref_id'], 'version': 1}, 'targetStatus': 'backlog'},
            current_rows=capture_native(self.selection).atoms, structure_snapshot=snapshot)
        self.assertEqual('completed', result['outcome'])

    def test_create_rejects_label_outside_model_vocabulary(self):
        self.new['newAtom']['label'] = 'Milestone'
        with self.assertRaisesRegex(InputError, 'declared navigation Label'):
            create_draft(self.selection, self.new, current_rows=self.rows, ticket_labels=('Task',))

    def test_canonical_flat_owned_task_keeps_validated_flat_revision_paths(self):
        flat = self.write('001_TICKETS/TASKS/AN-T-2-SUBTASK--example.md', 'AN-T-2')
        _, header, body = flat.read_text().split('---', 2)
        metadata = yaml.safe_load(header)
        metadata['context']['container'] = {'atom': 'AN-T-1'}
        metadata['context']['label'] = 'Subtask'
        flat.write_text('---\n' + yaml.safe_dump(canonical_native_header(metadata), sort_keys=False) + '---' + body)
        result = create_draft(self.selection, {'sourceCurrent': {'ref_id': 'AN-T-2', 'version': 1}},
                              current_rows=capture_native(self.selection).atoms)
        draft = self.root / result['savedDraft']['path']
        self.assertEqual(flat.parent / '01_draft', draft.parent)
        result = promote_draft(self.selection, {'target': {'ref_id': result['savedDraft']['ref_id'], 'version': 2},
                                                'targetStatus': 'backlog'},
                               current_rows=capture_native(self.selection).atoms)
        self.assertEqual(flat.parent / 'backlog' / flat.name, self.root / result['artifact']['path'])
        self.assertTrue((flat.parent / '09_archived' / flat.name.replace('AN-T-2-', 'AN-T-2@1-')).exists())

    def test_nested_tasks_create_and_promote_revisions(self):
        owner = self.path
        for depth in range(2):
            self.new['newAtom']['container'] = {'atom': f'AN-T-{depth + 1}'}
            self.new['newAtom']['body'] = f'\n## Summary\n\nChild {depth}\n'
            result = create_draft(self.selection, self.new, current_rows=capture_native(self.selection).atoms)
            draft = self.root / result['savedDraft']['path']
            self.assertEqual(owner.with_suffix('') / '01_draft', draft.parent)
            ref = result['savedDraft']['ref_id']
            result = promote_draft(self.selection, {'target': {'ref_id': ref, 'version': 1}, 'targetStatus': 'backlog'},
                                   current_rows=capture_native(self.selection).atoms)
            owner = self.root / result['artifact']['path']
            self.assertEqual(draft.parent.parent / 'backlog', owner.parent)
        result = create_draft(self.selection, {'sourceCurrent': {'ref_id': 'AN-T-3', 'version': 1}},
                              current_rows=capture_native(self.selection).atoms)
        draft = self.root / result['savedDraft']['path']
        self.assertEqual(owner.parent.parent / '01_draft', draft.parent)
        result = promote_draft(self.selection, {'target': {'ref_id': result['savedDraft']['ref_id'], 'version': 2},
                                                'targetStatus': 'backlog'},
                               current_rows=capture_native(self.selection).atoms)
        self.assertEqual('completed', result['outcome'])
        self.assertTrue((owner.parent.parent / '09_archived' / owner.name.replace('AN-T-3-', 'AN-T-3@1-')).exists())

    def test_unicode_punctuation_uses_reviewed_slug(self):
        self.new['newAtom']['body'] = self.new['newAtom']['body'].replace('Create a Task!', 'Create — a Task!')
        output = create_draft(self.selection, self.new, current_rows=self.rows)
        self.assertTrue(output['savedDraft']['path'].endswith('-TASK--create-a-task.md'))

    def test_task_owner_and_stale_or_foreign_owner(self):
        self.new['newAtom']['container'] = {'atom': 'AN-T-1'}
        output = create_draft(self.selection, self.new, current_rows=self.rows)
        self.assertEqual('completed', output['outcome'])
        self.assertTrue(output['savedDraft']['path'].endswith('-SUBTASK--create-a-task.md'))
        metadata = yaml.safe_load((self.root / output['savedDraft']['path']).read_text().split('---', 2)[1])
        self.assertEqual({'template': 'task', 'label': 'Subtask'}, metadata['context'])
        ref = output['savedDraft']['ref_id']
        promoted = promote_draft(self.selection, {'target': {'ref_id': ref, 'version': 1}, 'targetStatus': 'backlog'},
                                 current_rows=capture_native(self.selection).atoms)
        self.assertTrue(promoted['artifact']['path'].endswith('-SUBTASK--create-a-task.md'))
        self.new['newAtom']['container'] = {'atom': 'XX-T-1'}
        with self.assertRaises(InputError):
            create_draft(self.selection, self.new, current_rows=self.rows)
        self.new['newAtom']['container'] = {'atom': 'AN-T-1'}
        self.path.write_bytes(self.path.read_bytes().replace(b'Old', b'Altered'))
        with self.assertRaises(SourceChanged):
            create_draft(self.selection, self.new, current_rows=self.rows)

    def test_canonical_owner_template_is_authored_not_filename(self):
        _, header, body = self.path.read_text().split('---', 2)
        metadata = yaml.safe_load(header)
        metadata['context']['template'] = 'epic'
        self.path.write_text('---\n' + yaml.safe_dump(canonical_native_header(metadata), sort_keys=False) + '---' + body)
        self.new['newAtom']['container'] = {'atom': 'AN-T-1'}
        output = create_draft(self.selection, self.new, current_rows=capture_native(self.selection).atoms)
        self.assertEqual('completed', output['outcome'])
        result = promote_draft(self.selection,
            {'target': {'ref_id': output['savedDraft']['ref_id'], 'version': 1}, 'targetStatus': 'backlog'},
            current_rows=capture_native(self.selection).atoms)
        self.assertEqual('completed', result['outcome'])

    def test_epic_owner_is_checked_again_at_promotion(self):
        epic = self.write('001_TICKETS/TASKS/AN-T-10-EPIC--parent.md', 'AN-T-10', template='epic')
        self.new['newAtom']['container'] = {'atom': 'AN-T-10'}
        output = create_draft(self.selection, self.new, current_rows=capture_native(self.selection).atoms)
        ref = output['savedDraft']['ref_id']
        rows = capture_native(self.selection).atoms
        epic.write_bytes(epic.read_bytes() + b'changed')
        with self.assertRaises(SourceChanged):
            promote_draft(self.selection, {'target': {'ref_id': ref, 'version': 1}, 'targetStatus': 'backlog'},
                          current_rows=rows)
        self.assertTrue((self.root / output['savedDraft']['path']).exists())

    def test_rejects_unselected_component_and_unknown_fields(self):
        self.new['newAtom']['container'] = {'component': 'C999'}
        with self.assertRaises(InputError):
            create_draft(self.selection, self.new, current_rows=self.rows)
        self.new['newAtom']['container'] = {'component': 'C00'}
        self.new['newAtom']['extra'] = 'x'
        with self.assertRaises(InputError):
            create_draft(self.selection, self.new, current_rows=self.rows)

    def test_first_promotion_rejects_stale_draft(self):
        output = create_draft(self.selection, self.new, current_rows=self.rows)
        ref = output['savedDraft']['ref_id']
        params = {'target': {'ref_id': ref, 'version': 1}, 'targetStatus': 'backlog'}
        rows = capture_native(self.selection).atoms
        draft = self.root / output['savedDraft']['path']
        draft.write_bytes(draft.read_bytes() + b'changed')
        with self.assertRaises(SourceChanged):
            promote_draft(self.selection, params, current_rows=rows)


    def test_retry_after_draft_cleanup_failure_is_guarded_and_idempotent(self):
        from unittest.mock import patch
        from ATOM_LIFECYCLE import effects
        output = create_draft(self.selection, self.new, current_rows=self.rows)
        ref = output['savedDraft']['ref_id']
        path = self.root / output['savedDraft']['path']
        params = {'target': {'ref_id': ref, 'version': 1}, 'targetStatus': 'backlog'}
        rows = capture_native(self.selection).atoms
        with patch('ATOM_LIFECYCLE.native_draft.effects.remove', return_value=effects.Result(errors=[{'code': 'injected'}])):
            failed = promote_draft(self.selection, params, current_rows=rows)
        self.assertEqual('failed', failed['outcome'])
        self.assertTrue(path.exists())
        rows = capture_native(self.selection).atoms
        with self.assertRaises(InputError):
            promote_draft(self.selection, {**params, 'targetStatus': 'done'}, current_rows=rows)
        result = promote_draft(self.selection, params, current_rows=rows)
        self.assertEqual('completed', result['outcome'])
        self.assertEqual(['remove'], [item['operation'] for item in result['effects']])
        self.assertFalse(path.exists())

    def test_retry_refuses_changed_published_body(self):
        from unittest.mock import patch
        from ATOM_LIFECYCLE import effects
        output = create_draft(self.selection, self.new, current_rows=self.rows)
        ref = output['savedDraft']['ref_id']
        params = {'target': {'ref_id': ref, 'version': 1}, 'targetStatus': 'backlog'}
        with patch('ATOM_LIFECYCLE.native_draft.effects.remove', return_value=effects.Result(errors=[{'code': 'injected'}])):
            promote_draft(self.selection, params, current_rows=capture_native(self.selection).atoms)
        current = self.control / '001_TICKETS/TASKS/backlog/AN-T-2-TASK--create-a-task.md'
        current.write_bytes(current.read_bytes() + b'changed')
        with self.assertRaises(InputError):
            promote_draft(self.selection, params, current_rows=capture_native(self.selection).atoms)
        self.assertTrue((self.root / output['savedDraft']['path']).exists())


class NativePromotionTests(unittest.TestCase):
    write = NativeDraftTests.write

    def setUp(self):
        NativeDraftTests.setUp(self)
        output = create_draft(self.selection, self.params, current_rows=self.rows)
        self.draft = self.root / output['savedDraft']['path']
        self.rows = capture_native(self.selection).atoms
        self.promotion = {'target': {'ref_id': 'AN-T-1@2-draft', 'version': 2}, 'targetStatus': 'active'}

    def test_promotes_same_id_and_archives_pinned_current(self):
        old = self.path.read_bytes()
        output = promote_draft(self.selection, self.promotion, current_rows=self.rows)
        self.assertEqual('completed', output['outcome'])
        self.assertEqual(('AN-T-1', 2, 'active'), (output['artifact']['ref_id'], output['artifact']['version'], output['artifact']['status']))
        self.assertFalse(self.draft.exists())
        capture = capture_native(self.selection)
        self.assertFalse(capture.errors)
        archived = next(row for row in capture.atoms if row['_exact_ref'] == 'AN-T-1@1')
        current = next(row for row in capture.atoms if row['_exact_ref'] == 'AN-T-1@2')
        self.assertEqual('Archived', archived['status_group'])
        self.assertEqual('Current', current['status_group'])
        self.assertEqual(old.split(b'---\n', 2)[2], archived['_content_bytes'])
        self.assertIn(b'New', current['_content_bytes'])
        self.assertEqual(['create', 'create', 'modify', 'remove'], [e['operation'] for e in output['effects']])

    def test_promotes_to_another_current_status(self):
        self.promotion['targetStatus'] = 'done'
        output = promote_draft(self.selection, self.promotion, current_rows=self.rows)
        self.assertEqual('completed', output['outcome'])
        self.assertFalse(self.path.exists())
        self.assertEqual(self.control / '001_TICKETS/TASKS/done/AN-T-1-TASK--example.md', self.root / output['artifact']['path'])
        self.assertFalse(capture_native(self.selection).errors)

    def test_retry_of_revision_promotion_removes_only_pinned_draft(self):
        from unittest.mock import patch
        from ATOM_LIFECYCLE import effects
        with patch('ATOM_LIFECYCLE.native_draft.effects.remove', return_value=effects.Result(errors=[{'code': 'injected'}])):
            output = promote_draft(self.selection, self.promotion, current_rows=self.rows)
        self.assertEqual('failed', output['outcome'])
        rows = capture_native(self.selection).atoms
        output = promote_draft(self.selection, self.promotion, current_rows=rows)
        self.assertEqual('completed', output['outcome'])
        self.assertEqual(['remove'], [item['operation'] for item in output['effects']])
        self.assertEqual(2, output['artifact']['version'])
        self.assertFalse(self.draft.exists())
        self.assertFalse(capture_native(self.selection).errors)

    def test_conflict_and_stale_sources_have_no_effects(self):
        for case in ('collision', 'draft', 'current', 'manifest', 'selector'):
            with self.subTest(case=case):
                old, draft, manifest = self.path.read_bytes(), self.draft.read_bytes(), self.selection.manifest_path.read_bytes()
                params = {'target': dict(self.promotion['target']), 'targetStatus': 'active'}
                conflict = None
                if case == 'collision':
                    conflict = self.write('001_TICKETS/TASKS/09_archived/AN-T-1@2-TASK--example.md', 'AN-T-1', version=2, status='archived')
                if case == 'draft': self.draft.write_bytes(draft.replace(b'New', b'Changed'))
                if case == 'current': self.path.write_bytes(old.replace(b'Old', b'Changed'))
                if case == 'manifest': self.selection.manifest_path.write_bytes(manifest + b'changed')
                if case == 'selector': params['target']['ref_id'] = 'AN-T-1@2'
                with self.assertRaises((InputError, SourceChanged)):
                    promote_draft(self.selection, params, current_rows=self.rows)
                self.assertTrue(self.path.exists())
                self.assertTrue(self.draft.exists())
                self.path.write_bytes(old)
                self.draft.write_bytes(draft)
                self.selection.manifest_path.write_bytes(manifest)
                if conflict: conflict.unlink()

    def test_unsafe_status_directory_is_refused_before_archival(self):
        outside = self.root / 'outside'
        outside.mkdir()
        (self.control / '001_TICKETS/TASKS/done').symlink_to(outside, target_is_directory=True)
        self.promotion['targetStatus'] = 'done'
        with self.assertRaises(InputError):
            promote_draft(self.selection, self.promotion, current_rows=self.rows)
        self.assertFalse((self.control / '001_TICKETS/TASKS/09_archived').exists())
        self.assertEqual([], list(outside.iterdir()))

    def test_failed_replacement_rolls_back_archive(self):
        from unittest.mock import patch
        from ATOM_LIFECYCLE.effects import Result
        failure = Result(errors=[{'code': 'stale_state', 'message': 'injected failure'}])
        with patch('ATOM_LIFECYCLE.native_draft.effects.replace', return_value=failure):
            output = promote_draft(self.selection, self.promotion, current_rows=self.rows)
        self.assertEqual('failed', output['outcome'])
        self.assertTrue(output['effects'])
        self.assertTrue(self.draft.exists())
        self.assertTrue(self.path.exists())
        self.assertFalse((self.control / '001_TICKETS/TASKS/09_archived/AN-T-1@1-TASK--example.md').exists())
        self.assertFalse(capture_native(self.selection).errors)


    def test_failed_removal_rolls_back_status_destination_and_archive(self):
        from unittest.mock import patch
        from ATOM_LIFECYCLE import effects
        original_remove = effects.remove
        self.promotion['targetStatus'] = 'done'
        def remove(root, path, digest):
            if path == self.path:
                return effects.Result(errors=[{'code': 'stale_state', 'message': 'injected failure'}])
            return original_remove(root, path, digest)
        with patch('ATOM_LIFECYCLE.native_draft.effects.remove', side_effect=remove):
            output = promote_draft(self.selection, self.promotion, current_rows=self.rows)
        self.assertEqual('failed', output['outcome'])
        self.assertTrue(self.path.exists())
        self.assertTrue(self.draft.exists())
        self.assertFalse((self.control / '001_TICKETS/TASKS/done/AN-T-1-TASK--example.md').exists())
        self.assertFalse((self.control / '001_TICKETS/TASKS/09_archived/AN-T-1@1-TASK--example.md').exists())
        self.assertFalse(capture_native(self.selection).errors)

    def test_changed_current_retains_generated_carriers_and_reports_uncertainty(self):
        from unittest.mock import patch
        from ATOM_LIFECYCLE import effects
        original_remove = effects.remove
        self.promotion['targetStatus'] = 'done'
        def remove(root, path, digest):
            if path == self.path:
                self.path.write_bytes(self.path.read_bytes() + b'external')
                return effects.Result(errors=[{'code': 'stale_state', 'message': 'injected failure'}])
            return original_remove(root, path, digest)
        with patch('ATOM_LIFECYCLE.native_draft.effects.remove', side_effect=remove):
            output = promote_draft(self.selection, self.promotion, current_rows=self.rows)
        self.assertEqual('failed', output['outcome'])
        self.assertIn('rollback_unconfirmed', [item['code'] for item in output['errors']])
        self.assertTrue(self.path.read_bytes().endswith(b'external'))
        self.assertTrue(self.draft.exists())
        self.assertTrue((self.control / '001_TICKETS/TASKS/done/AN-T-1-TASK--example.md').exists())
        self.assertTrue((self.control / '001_TICKETS/TASKS/09_archived/AN-T-1@1-TASK--example.md').exists())

    def test_changed_archive_is_retained_and_reported(self):
        from unittest.mock import patch
        from ATOM_LIFECYCLE.effects import Result
        archive = self.control / '001_TICKETS/TASKS/09_archived/AN-T-1@1-TASK--example.md'
        def replace(*args):
            archive.write_bytes(archive.read_bytes() + b'external')
            return Result(errors=[{'code': 'stale_state', 'message': 'injected failure'}])
        with patch('ATOM_LIFECYCLE.native_draft.effects.replace', side_effect=replace):
            output = promote_draft(self.selection, self.promotion, current_rows=self.rows)
        self.assertEqual('failed', output['outcome'])
        self.assertIn('rollback_unconfirmed', [item['code'] for item in output['errors']])
        self.assertTrue(archive.read_bytes().endswith(b'external'))
        self.assertTrue(self.path.exists())
        self.assertTrue(self.draft.exists())

    def test_changed_draft_after_archival_rolls_back_archive(self):
        from unittest.mock import patch
        from ATOM_LIFECYCLE import common
        original_write = common.write_destination
        def write(root, path, raw):
            outcome = original_write(root, path, raw)
            self.draft.write_bytes(self.draft.read_bytes() + b'external')
            return outcome
        with patch('ATOM_LIFECYCLE.native_draft.common.write_destination', side_effect=write):
            output = promote_draft(self.selection, self.promotion, current_rows=self.rows)
        self.assertEqual('failed', output['outcome'])
        self.assertEqual('source_changed', output['errors'][0]['code'])
        self.assertFalse((self.control / '001_TICKETS/TASKS/09_archived/AN-T-1@1-TASK--example.md').exists())
        self.assertTrue(self.path.exists())
        self.assertTrue(self.draft.read_bytes().endswith(b'external'))


class ComponentContractLifecycleTests(unittest.TestCase):
    write = NativeDraftTests.write
    spec = NativeRevisionCarrierTests.spec

    def setUp(self):
        NativeRevisionCarrierTests.setUp(self)
        manifest = self.selection.manifest_path
        manifest.write_text(manifest.read_text().replace('component: C0}', 'component: C00}'))
        self.selection.manifest_sha256 = sha256(manifest.read_bytes()).hexdigest()
        declaration = self.spec('AN-S-2-SPEC--component.md', 'AN-S-2', lens='SPEC', component='C0')
        self.spec('UNIT_C9/__DES/AN-S-4-DES--example.md', 'AN-S-4')
        self.record = SimpleNamespace(source_path=declaration.relative_to(self.control).as_posix(),
                                      sha256=sha256(declaration.read_bytes()).hexdigest(),
                                      parent='C00', lens_whitelist=None)
        self.snapshot = SimpleNamespace(components={'C9': self.record}, component=lambda key: {'C9': self.record}[key])
        self.body = '\n## Summary\n\nImport graph contract\n\n## Guarantee\n\nThe graph includes imports.\n'
        self.new = {'newAtom': {'template': 'component_contract', 'container': {'component': 'C9'},
                                'lens': 'DES', 'body': self.body}}

    def create(self):
        return create_draft(self.selection, self.new, current_rows=capture_native(self.selection).atoms,
                            structure_snapshot=self.snapshot)

    def promote(self, ref, version):
        return promote_draft(self.selection, {'target': {'ref_id': ref, 'version': version}, 'targetStatus': 'ready'},
                             current_rows=capture_native(self.selection).atoms,
                             structure_snapshot=self.snapshot)

    def test_new_contract_reports_a_busy_writer_without_effects(self):
        from unittest.mock import patch

        with patch('ATOM_LIFECYCLE.native_draft._project_write_lock', side_effect=BlockingIOError):
            with self.assertRaisesRegex(SourceChanged, 'native Atom write is in progress'):
                self.create()
        self.assertFalse((self.control / 'UNIT_C9/01_draft').exists())

    def test_first_and_revised_publication_retains_pins(self):
        result = self.create()
        self.assertEqual('AN-S-5@1-draft', result['savedDraft']['ref_id'])
        draft = self.root / result['savedDraft']['path']
        self.assertEqual('AN-S-5@1-draft-DES-COMPONENT_CONTRACT--import-graph-contract.md', draft.name)
        metadata = yaml.safe_load(draft.read_text().split('---', 2)[1])
        self.assertEqual({'container': {'component': 'C9'}, 'tier': 1}, {'container': metadata['container'], 'tier': metadata['tier']})
        self.assertEqual({'template': 'component_contract', 'lens': 'DES'}, metadata['context'])
        result = self.promote('AN-S-5@1-draft', 1)
        self.assertEqual('completed', result['outcome'])
        self.assertFalse(draft.exists())
        self.assertEqual(1, result['artifact']['version'])
        current = self.root / result['artifact']['path']
        self.assertEqual(self.control / 'UNIT_C9/02_ready/AN-S-5-DES-COMPONENT_CONTRACT--import-graph-contract.md', current)
        revised = create_draft(self.selection, {'sourceCurrent': {'ref_id': 'AN-S-5', 'version': 1},
                               'changes': {'body': self.body.replace('includes imports', 'includes direct imports')}},
                               current_rows=capture_native(self.selection).atoms, structure_snapshot=self.snapshot)
        result = self.promote(revised['savedDraft']['ref_id'], 2)
        self.assertEqual('completed', result['outcome'])
        self.assertIn('direct imports', current.read_text())
        self.assertTrue((self.control / 'UNIT_C9/09_archived/AN-S-5@1-DES-COMPONENT_CONTRACT--import-graph-contract.md').exists())

    def test_rejects_wrong_owner_lens_and_invalid_guarantees(self):
        from copy import deepcopy
        for case in ('owner', 'bad_owner', 'lens', 'bad_lens', 'disabled', 'empty_whitelist', 'no_whitelist', 'missing', 'duplicate', 'code', 'summary'):
            with self.subTest(case=case):
                request = deepcopy(self.new)
                manifest = self.selection.manifest_path
                old_manifest = manifest.read_bytes()
                if case == 'owner': request['newAtom']['container'] = {'component': 'C99'}
                if case == 'bad_owner': request['newAtom']['container'] = {'component': 'bad'}
                if case == 'lens': request['newAtom']['lens'] = 'MISSING'
                if case == 'bad_lens': request['newAtom']['lens'] = None
                if case == 'disabled': self.record.lens_whitelist = ('SPEC',)
                if case == 'empty_whitelist': self.record.lens_whitelist = ()
                if case == 'no_whitelist':
                    manifest.write_bytes(old_manifest.replace(b", lens_whitelist=['DES', 'SPEC']", b''))
                    self.selection.manifest_sha256 = sha256(manifest.read_bytes()).hexdigest()
                if case == 'missing': request['newAtom']['body'] = self.body.replace('## Guarantee', '## Details')
                if case == 'duplicate': request['newAtom']['body'] += '\n## Guarantee\n\nMore prose.\n'
                if case == 'code': request['newAtom']['body'] = self.body.replace('The graph includes imports.', '```python\npass\n```')
                if case == 'summary': request['newAtom']['body'] = self.body.replace('## Summary', '# Summary')
                with self.assertRaises((InputError, SourceChanged)):
                    create_draft(self.selection, request, current_rows=capture_native(self.selection).atoms,
                                 structure_snapshot=self.snapshot)
                self.record.lens_whitelist = None
                manifest.write_bytes(old_manifest)
                self.selection.manifest_sha256 = sha256(old_manifest).hexdigest()
                self.assertFalse((self.control / 'UNIT_C9/01_draft').exists())

    def test_tampered_draft_and_revision_are_not_published(self):
        result = self.create()
        draft = self.root / result['savedDraft']['path']
        draft.write_text(draft.read_text().replace('The graph includes imports.', ''))
        with self.assertRaises(InputError):
            self.promote('AN-S-5@1-draft', 1)
        self.assertTrue(draft.exists())
        draft.write_text(draft.read_text().replace('## Guarantee\n\n', '## Guarantee\n\nThe graph includes imports.'))
        self.promote('AN-S-5@1-draft', 1)
        revised = create_draft(self.selection, {'sourceCurrent': {'ref_id': 'AN-S-5', 'version': 1},
                               'changes': {'body': self.body}}, current_rows=capture_native(self.selection).atoms,
                               structure_snapshot=self.snapshot)
        draft = self.root / revised['savedDraft']['path']
        draft.write_text(draft.read_text().replace('The graph includes imports.', ''))
        with self.assertRaises(InputError):
            self.promote('AN-S-5@2-draft', 2)
        self.assertTrue(draft.exists())
        self.assertFalse((self.control / 'UNIT_C9/09_archived').exists())

    def test_realistic_snapshot_inherits_only_nearest_whitelist(self):
        import json
        from LAYER_3_ENGINE_STUDIO_C14.KERNEL_MIXER_C59.MANIFEST_RUNTIME_C62.structure_host_pkg3.snapshot import parse_structure

        manifest = self.selection.manifest_path
        manifest.write_text(manifest.read_text().replace("['DES', 'SPEC']", "['SPEC']"))
        self.selection.manifest_sha256 = sha256(manifest.read_bytes()).hexdigest()
        components = {}
        for cid, parent, path, lenses in (
                ('C14', 'C00', 'AN-S-10-SPEC--c14.md', ['SPEC']),
                ('C43', 'C14', 'STUDIO_C14/AN-S-11-SPEC--c43.md', ['SPEC']),
                ('C61', 'C43', 'STUDIO_C14/CONSOLE_C43/AN-S-12-SPEC--c61.md', ['DES'])):
            declaration = self.spec(path, path.split('/')[-1].split('-SPEC')[0], lens='SPEC', component=parent)
            components[cid] = {'parent': parent, 'ref': 'AN-S-1@1',
                               'sha256': sha256(declaration.read_bytes()).hexdigest(),
                               'source_path': declaration.relative_to(self.control).as_posix(),
                               'fields': {'name': cid, 'lens_whitelist': lenses}}
        (self.control / 'STUDIO_C14/CONSOLE_C43/FEATURE_C61').mkdir(parents=True)
        self.snapshot = parse_structure(json.dumps({'model_sha256': 'model',
            'project': {'ref': 'AN-S-1@1', 'sha256': self.selection.manifest_sha256},
            'components': components, 'packages': {}}).encode())
        self.new['newAtom']['container'] = {'component': 'C61'}
        result = self.create()
        self.assertEqual('completed', result['outcome'])
        result = self.promote(result['savedDraft']['ref_id'], 1)
        self.assertEqual('completed', result['outcome'])
        self.assertIn('STUDIO_C14/CONSOLE_C43/FEATURE_C61/02_ready/', result['artifact']['path'])

    def test_archive_spec_draft_preserves_body_and_allocates_unused_version(self):
        from ATOM_LIFECYCLE.native_update import archive_spec_draft
        created = self.create()['savedDraft']
        draft = self.root / created['path']
        _, header, body = draft.read_text().split('---', 2)
        metadata = yaml.safe_load(header)
        metadata['state']['status'] = 'archived'
        occupied = draft.parent.parent / '09_archived' / draft.name.replace('@1-draft-', '@1-')
        occupied.parent.mkdir()
        occupied.write_text('---\n' + yaml.safe_dump(metadata) + '---' + body)
        target = {'ref_id': created['ref_id'], 'version': 1}
        outcome = archive_spec_draft(self.selection, {'target': target},
                                     current_rows=capture_native(self.selection).atoms,
                                     structure_snapshot=self.snapshot)
        self.assertEqual('AN-S-5@2', outcome['artifact']['ref_id'])
        self.assertEqual(created['ref_id'], outcome['sourceRef'])
        archived = self.root / outcome['artifact']['path']
        self.assertEqual(body, archived.read_text().split('---', 2)[2])
        self.assertEqual('archived', yaml.safe_load(archived.read_text().split('---', 2)[1])['state']['status'])
        self.assertTrue(occupied.exists())
        self.assertFalse(draft.exists())

    def test_ready_spec_starts_and_then_archives(self):
        from ATOM_LIFECYCLE.native_update import change_spec_status
        created = self.create()
        ready = self.promote(created['savedDraft']['ref_id'], 1)
        ready_path = self.root / ready['artifact']['path']
        self.assertEqual('02_ready', ready_path.parent.name)
        target = {'ref_id': 'AN-S-5', 'version': 1}
        started = change_spec_status(self.selection, {'target': target, 'targetStatus': 'active'},
                                     current_rows=capture_native(self.selection).atoms,
                                     structure_snapshot=self.snapshot)
        active_path = self.root / started['artifact']['path']
        self.assertEqual(self.control / 'UNIT_C9', active_path.parent)
        self.assertFalse(ready_path.exists())
        archived = change_spec_status(self.selection, {'target': target, 'targetStatus': 'archived'},
                                      current_rows=capture_native(self.selection).atoms,
                                      structure_snapshot=self.snapshot)
        self.assertEqual('09_archived', (self.root / archived['artifact']['path']).parent.name)
        self.assertFalse(active_path.exists())

    def test_reader_validates_active_contract(self):
        from native_component_contract import read_component_contract
        from VALIDATE_ATOMS.validate_atoms_workers.parsing import parse_carrier
        result = self.create()
        result = self.promote(result['savedDraft']['ref_id'], 1)
        path = self.root / result['artifact']['path']
        carrier = parse_carrier(path.read_bytes(), path)
        carrier.metadata['state']['status'] = 'active'
        fields = read_component_contract(path, carrier, 'C9', 'AN')
        self.assertEqual(('AN-S-5@1', 'AN-S-5', 'C9', 'The graph includes imports.'),
                         (fields['ref_id'], fields['atom_id'], fields['component_id'], fields['guarantee']))
        with self.assertRaises(ValueError):
            read_component_contract(path, carrier, 'C8', 'AN')
        carrier.metadata['tier'] = 2
        with self.assertRaises(ValueError):
            read_component_contract(path, carrier, 'C9', 'AN')

    def test_owner_manifest_change_is_refused(self):
        (self.control / self.record.source_path).write_text('changed')
        with self.assertRaises(SourceChanged):
            self.create()

    def test_reader_ignores_inactive_and_non_contract(self):
        from native_component_contract import read_component_contract
        carrier = SimpleNamespace(metadata={'context': {'template': 'component_contract'}, 'state': {'status': 'draft'}}, body='')
        self.assertIsNone(read_component_contract(Path('x'), carrier, 'C9', 'AN'))
        carrier.metadata = {'context': {}, 'state': {'status': 'active'}}
        self.assertIsNone(read_component_contract(Path('x'), carrier, 'C9', 'AN'))


if __name__ == '__main__':
    unittest.main()
