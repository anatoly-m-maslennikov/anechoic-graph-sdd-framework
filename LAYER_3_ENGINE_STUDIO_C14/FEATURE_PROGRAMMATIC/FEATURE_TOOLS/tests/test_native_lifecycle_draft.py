from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace
import sys
import tempfile
import unittest

import yaml

TOOLS = Path(__file__).resolve().parents[1]
ENGINE = TOOLS.parents[1]
sys.path[:0] = [str(TOOLS), str(ENGINE / 'IWE_CONSOLE_C43')]

from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.native_source_rows import capture_native
from ATOM_LIFECYCLE.common import InputError, SourceChanged
from ATOM_LIFECYCLE.native_draft import create_draft, promote_draft


class NativeDraftTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        (self.root / '.git').mkdir()
        self.control = self.root / '.anechoic_test'
        self.control.mkdir()
        manifest = self.write('AN-S-1-PROJECT_MANIFEST--manifest.md', 'AN-S-1')
        self.path = self.write('__TKT/TASKS/AN-T-1-TASK--example.md', 'AN-T-1')
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
        self.write('__TKT/TASKS/archived/AN-T-1@4-TASK--example.md', 'AN-T-1', version=4, status='archived')
        self.write('__TKT/TASKS/draft/AN-T-1@5-draft-TASK--example.md', 'AN-T-1', version=5, status='draft')
        current, manifest = self.path.read_bytes(), self.selection.manifest_path.read_bytes()
        output = create_draft(self.selection, self.params, current_rows=self.rows)
        self.assertEqual('completed', output['outcome'])
        self.assertEqual('AN-T-1@6-draft', output['savedDraft']['ref_id'])
        target = self.root / output['savedDraft']['path']
        self.assertEqual(self.control / '__TKT/TASKS/draft/AN-T-1@6-draft-TASK--example.md', target)
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
                self.assertFalse((self.control / '__TKT/TASKS/draft').exists())
                self.path.write_bytes(original)
                self.selection.manifest_path.write_bytes(manifest)

    def test_symlink_draft_directory_cannot_escape(self):
        outside = self.root / 'outside'
        outside.mkdir()
        (self.control / '__TKT/TASKS/draft').symlink_to(outside, target_is_directory=True)
        output = create_draft(self.selection, self.params, current_rows=self.rows)
        self.assertEqual('failed', output['outcome'])
        self.assertTrue(output['errors'])
        self.assertEqual([], list(outside.iterdir()))

    def test_wrong_branch_and_template_are_rejected(self):
        for name, template in [('__TKT/ISSUES/AN-T-2-TASK--example.md', 'task'),
                               ('__TKT/TASKS/AN-T-3-EPIC--example.md', 'epic')]:
            identity = 'AN-T-2' if template == 'task' else 'AN-T-3'
            self.write(name, identity, template=template)
            rows = capture_native(self.selection).atoms
            with self.assertRaises((InputError, SourceChanged)):
                create_draft(self.selection, {'sourceCurrent': {'ref_id': identity, 'version': 1}}, current_rows=rows)


class NewNativeTaskTests(unittest.TestCase):
    write = NativeDraftTests.write

    def setUp(self):
        NativeDraftTests.setUp(self)
        self.new = {'newAtom': {'template': 'task', 'container': {'component': 'C00'},
                                'body': '\n## Summary\n\nCreate a Task!\n\n## Work\n\nDo it.\n'}}

    def test_new_task_allocates_across_history_and_promotes_version_one(self):
        self.write('__TKT/ISSUES/archived/AN-T-8@2-QUESTION--old.md', 'AN-T-8', version=2, status='archived', template='question')
        before = self.path.read_bytes(), self.selection.manifest_path.read_bytes()
        result = create_draft(self.selection, self.new, current_rows=self.rows)
        self.assertEqual('AN-T-9@1-draft', result['savedDraft']['ref_id'])
        draft = self.root / result['savedDraft']['path']
        self.assertEqual('AN-T-9@1-draft-TASK--create-a-task.md', draft.name)
        rows = capture_native(self.selection).atoms
        result = promote_draft(self.selection, {'target': {'ref_id': 'AN-T-9@1-draft', 'version': 1}, 'targetStatus': 'active'},
                               current_rows=rows, migration_refs=[])
        self.assertEqual(('AN-T-9', 1, 'active'), (result['artifact']['ref_id'], result['artifact']['version'], result['artifact']['status']))
        self.assertFalse(draft.exists())
        capture = capture_native(self.selection)
        self.assertFalse(capture.errors)
        self.assertIn('AN-T-9@1', [row['_exact_ref'] for row in capture.atoms])
        self.assertEqual(before, (self.path.read_bytes(), self.selection.manifest_path.read_bytes()))

    def test_unicode_punctuation_uses_reviewed_slug(self):
        self.new['newAtom']['body'] = self.new['newAtom']['body'].replace('Create a Task!', 'Create — a Task!')
        output = create_draft(self.selection, self.new, current_rows=self.rows)
        self.assertTrue(output['savedDraft']['path'].endswith('-TASK--create-a-task.md'))

    def test_task_owner_and_stale_or_foreign_owner(self):
        self.new['newAtom']['container'] = {'atom': 'AN-T-1'}
        output = create_draft(self.selection, self.new, current_rows=self.rows)
        self.assertEqual('completed', output['outcome'])
        self.new['newAtom']['container'] = {'atom': 'XX-T-1'}
        with self.assertRaises(InputError):
            create_draft(self.selection, self.new, current_rows=self.rows)
        self.new['newAtom']['container'] = {'atom': 'AN-T-1'}
        self.path.write_bytes(self.path.read_bytes().replace(b'Old', b'Altered'))
        with self.assertRaises(SourceChanged):
            create_draft(self.selection, self.new, current_rows=self.rows)

    def test_epic_owner_is_checked_again_at_promotion(self):
        epic = self.write('__TKT/TASKS/AN-T-10-EPIC--parent.md', 'AN-T-10', template='epic')
        self.new['newAtom']['container'] = {'atom': 'AN-T-10'}
        output = create_draft(self.selection, self.new, current_rows=capture_native(self.selection).atoms)
        ref = output['savedDraft']['ref_id']
        rows = capture_native(self.selection).atoms
        epic.write_bytes(epic.read_bytes() + b'changed')
        with self.assertRaises(SourceChanged):
            promote_draft(self.selection, {'target': {'ref_id': ref, 'version': 1}, 'targetStatus': 'active'},
                          current_rows=rows, migration_refs=[])
        self.assertTrue((self.root / output['savedDraft']['path']).exists())

    def test_rejects_unselected_component_and_unknown_fields(self):
        self.new['newAtom']['container'] = {'component': 'C999'}
        with self.assertRaises(InputError):
            create_draft(self.selection, self.new, current_rows=self.rows)
        self.new['newAtom']['container'] = {'component': 'C00'}
        self.new['newAtom']['extra'] = 'x'
        with self.assertRaises(InputError):
            create_draft(self.selection, self.new, current_rows=self.rows)

    def test_first_promotion_rejects_migration_pin_and_stale_draft(self):
        output = create_draft(self.selection, self.new, current_rows=self.rows)
        ref = output['savedDraft']['ref_id']
        params = {'target': {'ref_id': ref, 'version': 1}, 'targetStatus': 'active'}
        rows = capture_native(self.selection).atoms
        with self.assertRaises(InputError):
            promote_draft(self.selection, params, current_rows=rows, migration_refs=[(None, 'old.md', ref)])
        draft = self.root / output['savedDraft']['path']
        draft.write_bytes(draft.read_bytes() + b'changed')
        with self.assertRaises(SourceChanged):
            promote_draft(self.selection, params, current_rows=rows, migration_refs=[])


    def test_retry_after_draft_cleanup_failure_is_guarded_and_idempotent(self):
        from unittest.mock import patch
        from ATOM_LIFECYCLE import effects
        output = create_draft(self.selection, self.new, current_rows=self.rows)
        ref = output['savedDraft']['ref_id']
        path = self.root / output['savedDraft']['path']
        params = {'target': {'ref_id': ref, 'version': 1}, 'targetStatus': 'active'}
        rows = capture_native(self.selection).atoms
        with patch('ATOM_LIFECYCLE.native_draft.effects.remove', return_value=effects.Result(errors=[{'code': 'injected'}])):
            failed = promote_draft(self.selection, params, current_rows=rows, migration_refs=[])
        self.assertEqual('failed', failed['outcome'])
        self.assertTrue(path.exists())
        rows = capture_native(self.selection).atoms
        with self.assertRaises(InputError):
            promote_draft(self.selection, params, current_rows=rows, migration_refs=[(None, 'old.md', ref)])
        with self.assertRaises(InputError):
            promote_draft(self.selection, {**params, 'targetStatus': 'done'}, current_rows=rows, migration_refs=[])
        result = promote_draft(self.selection, params, current_rows=rows, migration_refs=[])
        self.assertEqual('completed', result['outcome'])
        self.assertEqual(['remove'], [item['operation'] for item in result['effects']])
        self.assertFalse(path.exists())

    def test_retry_refuses_changed_published_body(self):
        from unittest.mock import patch
        from ATOM_LIFECYCLE import effects
        output = create_draft(self.selection, self.new, current_rows=self.rows)
        ref = output['savedDraft']['ref_id']
        params = {'target': {'ref_id': ref, 'version': 1}, 'targetStatus': 'active'}
        with patch('ATOM_LIFECYCLE.native_draft.effects.remove', return_value=effects.Result(errors=[{'code': 'injected'}])):
            promote_draft(self.selection, params, current_rows=capture_native(self.selection).atoms, migration_refs=[])
        current = self.control / '__TKT/TASKS/AN-T-2-TASK--create-a-task.md'
        current.write_bytes(current.read_bytes() + b'changed')
        with self.assertRaises(InputError):
            promote_draft(self.selection, params, current_rows=capture_native(self.selection).atoms, migration_refs=[])
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
        output = promote_draft(self.selection, self.promotion, current_rows=self.rows,
                               migration_refs=[('CA-P-1@1', 'old.md', 'AN-T-1@1')])
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
        output = promote_draft(self.selection, self.promotion, current_rows=self.rows, migration_refs=[])
        self.assertEqual('completed', output['outcome'])
        self.assertFalse(self.path.exists())
        self.assertEqual(self.control / '__TKT/TASKS/done/AN-T-1-TASK--example.md', self.root / output['artifact']['path'])
        self.assertFalse(capture_native(self.selection).errors)

    def test_retry_of_revision_promotion_removes_only_pinned_draft(self):
        from unittest.mock import patch
        from ATOM_LIFECYCLE import effects
        with patch('ATOM_LIFECYCLE.native_draft.effects.remove', return_value=effects.Result(errors=[{'code': 'injected'}])):
            output = promote_draft(self.selection, self.promotion, current_rows=self.rows, migration_refs=[])
        self.assertEqual('failed', output['outcome'])
        rows = capture_native(self.selection).atoms
        output = promote_draft(self.selection, self.promotion, current_rows=rows, migration_refs=[])
        self.assertEqual('completed', output['outcome'])
        self.assertEqual(['remove'], [item['operation'] for item in output['effects']])
        self.assertEqual(2, output['artifact']['version'])
        self.assertFalse(self.draft.exists())
        self.assertFalse(capture_native(self.selection).errors)

    def test_pinned_draft_is_refused_without_effects(self):
        before = self.path.read_bytes(), self.draft.read_bytes()
        with self.assertRaises(InputError):
            promote_draft(self.selection, self.promotion, current_rows=self.rows,
                          migration_refs=[('CA-P-1@2-draft', 'old.md', 'AN-T-1@2-draft')])
        self.assertEqual(before, (self.path.read_bytes(), self.draft.read_bytes()))
        self.assertFalse((self.control / '__TKT/TASKS/archived').exists())

    def test_conflict_and_stale_sources_have_no_effects(self):
        for case in ('collision', 'draft', 'current', 'manifest', 'selector', 'invalid_refs'):
            with self.subTest(case=case):
                old, draft, manifest = self.path.read_bytes(), self.draft.read_bytes(), self.selection.manifest_path.read_bytes()
                params = {'target': dict(self.promotion['target']), 'targetStatus': 'active'}
                conflict = None
                refs = []
                if case == 'collision':
                    conflict = self.write('__TKT/TASKS/archived/AN-T-1@2-TASK--example.md', 'AN-T-1', version=2, status='archived')
                if case == 'draft': self.draft.write_bytes(draft.replace(b'New', b'Changed'))
                if case == 'current': self.path.write_bytes(old.replace(b'Old', b'Changed'))
                if case == 'manifest': self.selection.manifest_path.write_bytes(manifest + b'changed')
                if case == 'selector': params['target']['ref_id'] = 'AN-T-1@2'
                if case == 'invalid_refs': refs = [('broken',)]
                with self.assertRaises((InputError, SourceChanged)):
                    promote_draft(self.selection, params, current_rows=self.rows, migration_refs=refs)
                self.assertTrue(self.path.exists())
                self.assertTrue(self.draft.exists())
                self.path.write_bytes(old)
                self.draft.write_bytes(draft)
                self.selection.manifest_path.write_bytes(manifest)
                if conflict: conflict.unlink()

    def test_unsafe_status_directory_is_refused_before_archival(self):
        outside = self.root / 'outside'
        outside.mkdir()
        (self.control / '__TKT/TASKS/done').symlink_to(outside, target_is_directory=True)
        self.promotion['targetStatus'] = 'done'
        with self.assertRaises(InputError):
            promote_draft(self.selection, self.promotion, current_rows=self.rows, migration_refs=[])
        self.assertFalse((self.control / '__TKT/TASKS/archived').exists())
        self.assertEqual([], list(outside.iterdir()))

    def test_failed_replacement_rolls_back_archive(self):
        from unittest.mock import patch
        from ATOM_LIFECYCLE.effects import Result
        failure = Result(errors=[{'code': 'stale_state', 'message': 'injected failure'}])
        with patch('ATOM_LIFECYCLE.native_draft.effects.replace', return_value=failure):
            output = promote_draft(self.selection, self.promotion, current_rows=self.rows, migration_refs=[])
        self.assertEqual('failed', output['outcome'])
        self.assertTrue(output['effects'])
        self.assertTrue(self.draft.exists())
        self.assertTrue(self.path.exists())
        self.assertFalse((self.control / '__TKT/TASKS/archived/AN-T-1@1-TASK--example.md').exists())
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
            output = promote_draft(self.selection, self.promotion, current_rows=self.rows, migration_refs=[])
        self.assertEqual('failed', output['outcome'])
        self.assertTrue(self.path.exists())
        self.assertTrue(self.draft.exists())
        self.assertFalse((self.control / '__TKT/TASKS/done/AN-T-1-TASK--example.md').exists())
        self.assertFalse((self.control / '__TKT/TASKS/archived/AN-T-1@1-TASK--example.md').exists())
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
            output = promote_draft(self.selection, self.promotion, current_rows=self.rows, migration_refs=[])
        self.assertEqual('failed', output['outcome'])
        self.assertIn('rollback_unconfirmed', [item['code'] for item in output['errors']])
        self.assertTrue(self.path.read_bytes().endswith(b'external'))
        self.assertTrue(self.draft.exists())
        self.assertTrue((self.control / '__TKT/TASKS/done/AN-T-1-TASK--example.md').exists())
        self.assertTrue((self.control / '__TKT/TASKS/archived/AN-T-1@1-TASK--example.md').exists())

    def test_changed_archive_is_retained_and_reported(self):
        from unittest.mock import patch
        from ATOM_LIFECYCLE.effects import Result
        archive = self.control / '__TKT/TASKS/archived/AN-T-1@1-TASK--example.md'
        def replace(*args):
            archive.write_bytes(archive.read_bytes() + b'external')
            return Result(errors=[{'code': 'stale_state', 'message': 'injected failure'}])
        with patch('ATOM_LIFECYCLE.native_draft.effects.replace', side_effect=replace):
            output = promote_draft(self.selection, self.promotion, current_rows=self.rows, migration_refs=[])
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
            output = promote_draft(self.selection, self.promotion, current_rows=self.rows, migration_refs=[])
        self.assertEqual('failed', output['outcome'])
        self.assertEqual('source_changed', output['errors'][0]['code'])
        self.assertFalse((self.control / '__TKT/TASKS/archived/AN-T-1@1-TASK--example.md').exists())
        self.assertTrue(self.path.exists())
        self.assertTrue(self.draft.read_bytes().endswith(b'external'))


if __name__ == '__main__':
    unittest.main()
