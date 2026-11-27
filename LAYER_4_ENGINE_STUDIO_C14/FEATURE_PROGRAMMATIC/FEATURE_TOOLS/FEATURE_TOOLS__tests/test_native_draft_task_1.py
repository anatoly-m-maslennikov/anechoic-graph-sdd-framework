import json
import os
from pathlib import Path
import subprocess
from unittest.mock import NonCallableMock
import sys
import unittest
from unittest.mock import patch

import yaml

TOOLS = Path(__file__).resolve().parents[1]
ENGINE = TOOLS.parents[1]
sys.path[:0] = [str(TOOLS), str(ENGINE / 'IWE_CONSOLE_C43')]

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import TICKET_DIRECTORY, capture_native
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.ATOM_LIFECYCLE__shared import InputError, SourceChanged
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.ATOM_LIFECYCLE__shared import create_draft, promote_draft
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import canonical_native_header



import FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__tests.test_native_lifecycle_draft as fixtures


class NewNativeTaskTests(fixtures.NewNativeTaskTests, unittest.TestCase):
    def test_indexed_cli_creates_without_capture_or_model(self):
        request = {'binding': {'root': str(self.root), 'control_root': self.control.name,
            'manifest_path': self.selection.manifest_path.relative_to(self.root).as_posix(),
            'manifest_sha256': self.selection.manifest_sha256, 'project_prefix': 'AN'},
            'name': 'atom_lifecycle_create_draft', 'arguments': self.new,
            'indexed_task': {'max_number': '2', 'manifest_ref': 'AN-S-1@1',
                             'component_ids': ['C00'], 'ticket_labels': ['Task']}}
        self.selection.manifest_path.unlink()
        process = subprocess.run([sys.executable, '-B', '-P', '-m', 'FEATURE_PROGRAMMATIC.FEATURE_TOOLS.native_lifecycle_cli'],
            cwd=ENGINE, env={**os.environ, 'PYTHONPATH': str(ENGINE)}, input=json.dumps(request),
            text=True, capture_output=True, timeout=15)
        self.assertEqual(0, process.returncode, process.stderr)
        result = json.loads(process.stdout)
        self.assertEqual('AN-T-3@1-draft', result['savedDraft']['ref_id'])
        self.assertTrue((self.root / result['savedDraft']['path']).is_file())

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
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.ATOM_LIFECYCLE__shared import change_ticket_status
        target = {'ref_id': 'AN-T-9', 'version': 1}
        queued = change_ticket_status(self.selection, {'target': target, 'targetStatus': 'in_queue'},
                                      current_rows=capture_native(self.selection).atoms, check_definition=lambda: None)
        self.assertEqual(self.control / TICKET_DIRECTORY / 'TASKS', (self.root / queued['artifact']['path']).parent)
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
            return NonCallableMock(
                spec_set=['effects', 'errors'],
                effects=[{'operation': 'create', 'target': str(destination)}],
                errors=[{'code': 'backend_failure', 'message': 'copy interrupted'}])

        with patch('FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.native_update.move_directory', side_effect=partial_move):
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
        snapshot = NonCallableMock(
            spec_set=['components'],
            components={'C21': object()})
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


