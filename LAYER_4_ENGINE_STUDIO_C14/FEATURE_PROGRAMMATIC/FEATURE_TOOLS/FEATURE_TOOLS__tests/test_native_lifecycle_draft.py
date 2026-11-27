from dataclasses import replace
from hashlib import sha256
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

import yaml

TOOLS = Path(__file__).resolve().parents[1]
ENGINE = TOOLS.parents[1]
sys.path[:0] = [str(TOOLS), str(ENGINE / 'IWE_CONSOLE_C43')]

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import capture_native, parse_structure
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__shared import NativeProjectSelection, execute_native_lifecycle
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.ATOM_LIFECYCLE__shared import InputError, SourceChanged
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.ATOM_LIFECYCLE__shared import create_draft, promote_draft
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import canonical_native_header


def collide_first_two_links(attempts):
    link = os.link

    def collide(source, filename, **options):
        attempts.append(filename)
        if len(attempts) <= 2:
            mode = os.O_WRONLY | os.O_CREAT | os.O_EXCL
            with os.fdopen(os.open(filename, mode, 0o600, dir_fd=options["dst_dir_fd"]), "wb") as occupied:
                occupied.write(b"occupied")
        return link(source, filename, **options)

    return collide

class NativeDraftTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        (self.root / '.git').mkdir()
        self.control = self.root / '.anechoic_test'
        self.control.mkdir()
        manifest = self.write('AN-S-1-PROJECT_MANIFEST--manifest.md', 'AN-S-1')
        self.path = self.write('001_TICKETS/TASKS/AN-T-1-TASK--example.md', 'AN-T-1')
        self.selection = NativeProjectSelection(
            root=self.root, control_root=self.control, control_relative=self.control.relative_to(self.root),
            instance_id='a' * 64, project_name='Test', project_prefix='AN',
            manifest_path=manifest, manifest_ref='AN-S-1@1',
            manifest_sha256=sha256(manifest.read_bytes()).hexdigest(),
        )
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

    def test_update_exact_draft_body_and_authored_relation(self):
        text = self.path.read_text().replace('state:\n', 'relations:\n  RELATES_TO:\n  - AN-T-9\nstate:\n')
        self.path.write_text(text)
        capture = capture_native(self.selection)
        created = create_draft(self.selection, self.params, current_rows=capture.atoms)
        self.assertEqual('completed', created['outcome'], created)
        draft = created['savedDraft']
        capture = capture_native(self.selection)
        row = next(r for r in capture.atoms if r['_exact_ref'] == draft['ref_id'])
        updated_at = row['header_json']['state']['updated_at']
        args = {'target': {'ref_id': draft['ref_id'], 'version': draft['version']},
                'changes': {'body': self.params['changes']['body'].replace('New', 'Saved'),
                            'removeRelations': [{'type': 'RELATES_TO', 'ref_id': 'AN-T-9'}]},
                'expectedUpdatedAt': updated_at}
        result = execute_native_lifecycle(
            self.selection, 'atom_lifecycle_update', args, capture, None,
            previous_capture=None, ticket_labels=(), validate_project_spec=None,
        )
        self.assertEqual('completed', result['outcome'], result)
        self.assertEqual(draft['ref_id'], result['artifact']['ref_id'])
        self.assertNotEqual(updated_at, result['artifact']['updated_at'])
        after = capture_native(self.selection)
        row = next(r for r in after.atoms if r['_exact_ref'] == draft['ref_id'])
        self.assertEqual(b'\n# Summary\n\nExample\n\n## Details\n\nSaved\n', row['_content_bytes'])
        self.assertFalse(row['header_json'].get('relations'))
        stale = execute_native_lifecycle(
            self.selection, 'atom_lifecycle_update', args, after, None,
            previous_capture=None, ticket_labels=(), validate_project_spec=None,
        )
        self.assertEqual('source_changed', stale['errors'][0]['code'])
        self.assertFalse(stale['effects'])
        promoted = promote_draft(self.selection, {'target': args['target'], 'targetStatus': 'backlog'},
                                 current_rows=after.atoms)
        self.assertEqual('completed', promoted['outcome'], promoted)
        self.assertNotIn('AN-T-9', (self.path.parent / 'backlog' / self.path.name).read_text())

    def test_exact_draft_no_op_preserves_carrier_and_artifact(self):
        created = create_draft(self.selection, self.params,
                               current_rows=self.rows)['savedDraft']
        path = self.root / created['path']
        before, stat = path.read_bytes(), path.stat()
        capture = capture_native(self.selection)
        body = self.params['changes']['body']
        variants = ({'body': body}, {'removeRelations': []},
                    {'body': body, 'removeRelations': []})
        for changes in variants:
            with self.subTest(changes=changes):
                args = {
                    'target': {'ref_id': created['ref_id'],
                               'version': created['version']},
                    'changes': changes,
                    'expectedUpdatedAt': created['updated_at'],
                }
                output = execute_native_lifecycle(
                    self.selection, 'atom_lifecycle_update', args, capture,
                    None, previous_capture=None, ticket_labels=(),
                    validate_project_spec=None,
                )
                self.assertEqual('completed', output['outcome'], output)
                self.assertEqual(created, output['artifact'])
                self.assertEqual([], output['effects'])
                self.assertEqual(before, path.read_bytes())
                self.assertEqual(stat.st_ino, path.stat().st_ino)
                self.assertEqual(stat.st_mtime_ns, path.stat().st_mtime_ns)

    def test_indexed_max_and_real_collision_retries(self):
        from unittest.mock import Mock, patch
        capture = capture_native(self.selection)
        indexed = Mock(atoms=capture.atoms, errors=[], max_archived_version=7)
        attempts = []
        directory = self.path.parent / '01_draft'
        directory.mkdir()

        with patch('FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.native_draft.revalidate_native', return_value=indexed), \
             patch('os.link', side_effect=collide_first_two_links(attempts)):
            result = create_draft(self.selection, self.params, current_rows=self.rows)
        self.assertEqual('completed', result['outcome'], result)
        self.assertEqual('AN-T-1@10-draft', result['savedDraft']['ref_id'])
        self.assertEqual(3, len(attempts))
        self.assertEqual([b'occupied', b'occupied'], [(directory / name).read_bytes() for name in attempts[:2]])

    def test_revision_does_not_retry_other_write_errors(self):
        from unittest.mock import patch
        with patch('os.link', side_effect=PermissionError('failed')) as write:
            result = create_draft(self.selection, self.params, current_rows=self.rows)
        self.assertEqual('failed', result['outcome'])
        self.assertEqual(1, write.call_count)

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
                if case == 'version':
                    params['sourceCurrent']['version'] = 2
                if case == 'selector':
                    params['sourceCurrent']['extra'] = 'x'
                if case == 'foreign':
                    params['sourceCurrent']['ref_id'] = 'XX-T-1'
                if case == 'digest':
                    row.pop('_source_sha256')
                if case == 'path':
                    row['source_path'] = '../escape.md'
                if case == 'bytes':
                    self.path.write_bytes(original.replace(b'Old', b'Altered'))
                if case == 'summary':
                    params['changes']['body'] = params['changes']['body'].replace('Example', 'Changed')
                if case == 'extra':
                    params['changes']['status'] = 'done'
                if case == 'template':
                    row['header_json'] = {**row['header_json'], 'context': {'template': 'epic'}}
                if case == 'manifest':
                    self.selection.manifest_path.write_bytes(manifest + b'changed')
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


class NativeRevisionCarrierTests:
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
        self.selection = replace(self.selection, manifest_sha256=sha256(manifest.read_bytes()).hexdigest())

    def spec(self, name, atom_id, lens='DES', component='C9'):
        path = self.write(name, atom_id)
        header, body = path.read_text().split('---\n', 2)[1:]
        data = yaml.safe_load(header)
        data['context'] = {'container': {'component': component}, 'lens': lens}
        path.write_text('---\n' + yaml.safe_dump(data) + '---\n' + body)
        return path


class NewNativeTaskTests:
    write = NativeDraftTests.write

    def setUp(self):
        NativeDraftTests.setUp(self)
        self.new = {'newAtom': {'template': 'task', 'container': {'component': 'C00'},
                                'body': '\n## Summary\n\nCreate a Task!\n\n## Work\n\nDo it.\n'}}


class NativePromotionTests:
    write = NativeDraftTests.write

    def setUp(self):
        NativeDraftTests.setUp(self)
        output = create_draft(self.selection, self.params, current_rows=self.rows)
        self.draft = self.root / output['savedDraft']['path']
        self.rows = capture_native(self.selection).atoms
        self.promotion = {'target': {'ref_id': 'AN-T-1@2-draft', 'version': 2}, 'targetStatus': 'active'}


class ComponentContractLifecycleTests:
    write = NativeDraftTests.write

    spec = NativeRevisionCarrierTests.spec

    def setUp(self):
        NativeRevisionCarrierTests.setUp(self)
        manifest = self.selection.manifest_path
        manifest.write_text(manifest.read_text().replace('component: C0}', 'component: C00}'))
        self.selection = replace(self.selection, manifest_sha256=sha256(manifest.read_bytes()).hexdigest())
        declaration = self.spec('AN-S-2-SPEC--component.md', 'AN-S-2', lens='SPEC', component='C0')
        self.spec('UNIT_C9/__DES/AN-S-4-DES--example.md', 'AN-S-4')
        self.snapshot = parse_structure(json.dumps({'model_sha256': 'model',
            'project': {'ref': 'AN-S-1@1', 'sha256': sha256(manifest.read_bytes()).hexdigest()},
            'components': {'C9': {'parent': 'C00', 'ref': 'AN-S-2@1',
                'sha256': sha256(declaration.read_bytes()).hexdigest(),
                'fields': {'name': 'Unit', 'lens_whitelist': None},
                'source_path': declaration.relative_to(self.control).as_posix()}},
            'packages': {}}).encode())
        self.record = self.snapshot.components['C9']
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
