from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace
import sys
import unittest

import yaml

TOOLS = Path(__file__).resolve().parents[1]
ENGINE = TOOLS.parents[1]
sys.path[:0] = [str(TOOLS), str(ENGINE / 'IWE_CONSOLE_C43')]

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import capture_native
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.ATOM_LIFECYCLE__shared import InputError, SourceChanged
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.ATOM_LIFECYCLE__shared import create_draft



import FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__tests.test_native_lifecycle_draft as fixtures


class ComponentContractLifecycleTests(fixtures.ComponentContractLifecycleTests, unittest.TestCase):
    def test_new_contract_reports_a_busy_writer_without_effects(self):
        from unittest.mock import patch

        with patch('FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.native_draft._project_write_lock', side_effect=BlockingIOError):
            with self.assertRaisesRegex(SourceChanged, 'native Atom write is in progress'):
                self.create()
        self.assertFalse((self.control / 'UNIT_C9/01_draft').exists())


    def test_revision_uses_selection_snapshot_path_and_validates_its_parent(self):
        import json
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.ATOM_LIFECYCLE__shared import _revision_root

        draft = self.create()['savedDraft']
        self.promote(draft['ref_id'], draft['version'])
        rows = capture_native(self.selection).atoms
        row = next(row for row in rows if row['id'] == 'AN-S-5' and row['status_group'] == 'Current')
        snapshot_path = self.root / 'structure.json'
        self.selection.structure_snapshot = snapshot_path
        data = {'model_sha256': 'model', 'project': {'ref': 'p', 'sha256': 'h'},
                'components': {'C9': {'parent': 'C00', 'ref': 'r', 'sha256': 'h',
                                       'fields': {'name': 'Unit'}, 'source_path': self.record.source_path}}}
        snapshot_path.write_text(json.dumps(data), encoding='utf-8')
        self.assertEqual(self.control / 'UNIT_C9', _revision_root(self.selection, row))
        data['components']['C9']['source_path'] = 'OTHER_C8/component.md'
        snapshot_path.write_text(json.dumps(data), encoding='utf-8')
        with self.assertRaisesRegex(InputError, 'SPEC carrier must be in its lens and component root'):
            _revision_root(self.selection, row)
        snapshot_path.write_text('{invalid', encoding='utf-8')
        with self.assertRaises(InputError):
            _revision_root(self.selection, row)
        self.assertEqual(self.control / 'UNIT_C9', _revision_root(self.selection, row, self.snapshot))


    def test_first_and_revised_publication_retains_pins(self):
        result = self.create()
        self.assertEqual('AN-S-5@1-draft', result['savedDraft']['ref_id'])
        draft = self.root / result['savedDraft']['path']
        self.assertEqual('AN-S-5@1-draft-DES-COMPONENT_CONTRACT--import-graph-contract.md', draft.name)
        metadata = yaml.safe_load(draft.read_text().split('---', 2)[1])
        self.assertEqual({'container': {'component': 'C9'}, 'tier': 0}, {'container': metadata['container'], 'tier': metadata['tier']})
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
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import read_structure

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
        snapshot_path = self.root / 'structure.json'
        snapshot_path.write_text(json.dumps({'model_sha256': 'model',
            'project': {'ref': 'AN-S-1@1', 'sha256': self.selection.manifest_sha256},
            'components': components, 'packages': {}}), encoding='utf-8')
        self.snapshot = read_structure(snapshot_path)
        self.new['newAtom']['container'] = {'component': 'C61'}
        result = self.create()
        self.assertEqual('completed', result['outcome'])
        result = self.promote(result['savedDraft']['ref_id'], 1)
        self.assertEqual('completed', result['outcome'])
        self.assertIn('STUDIO_C14/CONSOLE_C43/FEATURE_C61/02_ready/', result['artifact']['path'])


    def test_archive_spec_draft_preserves_body_and_allocates_unused_version(self):
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.ATOM_LIFECYCLE__shared import archive_spec_draft
        created = self.create()['savedDraft']
        draft = self.root / created['path']
        _, header, body = draft.read_text().split('---', 2)
        metadata = yaml.safe_load(header)
        metadata['state']['status'] = 'archived'
        metadata['tier'] = 1
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
        self.assertEqual(1, yaml.safe_load(occupied.read_text().split('---', 2)[1])['tier'])
        self.assertFalse(draft.exists())


    def test_ready_spec_starts_and_then_archives(self):
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.ATOM_LIFECYCLE__shared import change_spec_status
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
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.component_contract__pub import read_component_contract
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import parse_carrier
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
        carrier.metadata['tier'] = 1
        with self.assertRaises(ValueError):
            read_component_contract(path, carrier, 'C9', 'AN')


    def test_owner_manifest_change_is_refused(self):
        (self.control / self.record.source_path).write_text('changed')
        with self.assertRaises(SourceChanged):
            self.create()


    def test_reader_ignores_inactive_and_non_contract(self):
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.component_contract__pub import read_component_contract
        carrier = SimpleNamespace(metadata={'context': {'template': 'component_contract'}, 'state': {'status': 'draft'}}, body='')
        self.assertIsNone(read_component_contract(Path('x'), carrier, 'C9', 'AN'))
        carrier.metadata = {'context': {}, 'state': {'status': 'active'}}
        self.assertIsNone(read_component_contract(Path('x'), carrier, 'C9', 'AN'))


