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
from ATOM_LIFECYCLE import effects
from ATOM_LIFECYCLE.native_update import archive_ticket, change_ticket_status, direct_update
from native_carrier_header import canonical_native_header


class NativeDirectUpdateTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        (self.root / '.git').mkdir()
        self.control = self.root / '.anechoic_test'
        self.control.mkdir()
        manifest = self.write('AN-S-1-PROJECT_MANIFEST--manifest.md', 'AN-S-1')
        self.path = self.write('__TKT/ASSETS/AN-T-1-ASSET--example.md', 'AN-T-1')
        self.selection = SimpleNamespace(root=self.root, control_root=self.control, manifest_path=manifest,
                                         manifest_sha256=sha256(manifest.read_bytes()).hexdigest(), project_prefix='AN')
        self.rows = capture_native(self.selection).atoms
        for row in self.rows:
            row['_source_sha256'] = sha256((self.root / row['source_path']).read_bytes()).hexdigest()
        self.params = {'target': {'ref_id': 'AN-T-1', 'version': 1},
                       'changes': {'body': '\n## Summary\n\nExample\n\n## Details\n\nNew\n'}}

    def write(self, name, identity, container=None):
        path = self.control / name
        path.parent.mkdir(parents=True, exist_ok=True)
        header = {'identity': {'atom_id': identity}, 'context': {'container': container or {'component': 'C0'}},
                  'state': {'status': 'active', 'version': 1, 'updated_at': '2026-11-19T00:00:00Z'}}
        path.write_text('---\n' + yaml.safe_dump(header) + '---\n\n## Summary\n\nExample\n\n## Details\n\nOld\n')
        return path

    def test_body_update_preserves_header_and_identity(self):
        before = self.path.read_bytes()
        output = direct_update(self.selection, self.params, current_rows=self.rows)
        self.assertEqual('completed', output['outcome'])
        self.assertEqual('modify', output['effects'][0]['operation'])
        self.assertEqual(('AN-T-1', 1, 'active'), (output['artifact']['ref_id'], output['artifact']['version'], output['artifact']['status']))
        self.assertEqual(before.split(b'---\n', 2)[1], self.path.read_bytes().split(b'---\n', 2)[1])
        self.assertIn(b'New', self.path.read_bytes())

    def test_canonical_ticket_body_and_status_updates_preserve_header(self):
        raw = self.path.read_text()
        _, header, body = raw.split('---', 2)
        metadata = yaml.safe_load(header)
        metadata['context']['template'] = 'asset'
        canonical = canonical_native_header(metadata)
        self.path.write_text('---\n' + yaml.safe_dump(canonical, sort_keys=False) + '---' + body)
        rows = capture_native(self.selection).atoms
        before = self.path.read_bytes().split(b'---\n', 2)[1]
        self.assertEqual('completed', direct_update(self.selection, self.params, current_rows=rows)['outcome'])
        self.assertEqual(before, self.path.read_bytes().split(b'---\n', 2)[1])
        rows = capture_native(self.selection).atoms
        output = change_ticket_status(self.selection,
            {'target': self.params['target'], 'targetStatus': 'done'},
            current_rows=rows, check_definition=lambda: None)
        self.assertEqual('completed', output['outcome'])
        moved = self.control / '__TKT/ASSETS/done' / self.path.name
        after = yaml.safe_load(moved.read_text().split('---', 2)[1])
        self.assertEqual({**canonical, 'state': after['state']}, after)
        self.assertEqual('done', after['state']['status'])

    def test_stale_or_invalid_inputs_have_no_effect(self):
        for case in ('version', 'header', 'header_bytes', 'missing_digest', 'path', 'wrong_path', 'summary', 'extra', 'child', 'companion'):
            with self.subTest(case=case):
                original = self.path.read_bytes()
                rows = [dict(row) for row in self.rows]
                params = {'target': dict(self.params['target']), 'changes': dict(self.params['changes'])}
                ticket = next(row for row in rows if row['id'] == 'AN-T-1')
                extra_path = None
                if case == 'version':
                    params['target']['version'] = 2
                elif case == 'header':
                    self.path.write_bytes(original.replace(b'version: 1', b'version: 2'))
                elif case == 'header_bytes':
                    self.path.write_bytes(original.replace(b'version: 1', b'version: 01'))
                elif case == 'missing_digest':
                    ticket.pop('_source_sha256')
                elif case == 'path':
                    ticket['source_path'] = '../outside.md'
                elif case == 'wrong_path':
                    ticket['source_path'] = str(Path(ticket['source_path']).with_name('AN-T-1-other.md'))
                elif case == 'summary':
                    params['changes']['body'] = params['changes']['body'].replace('Example', 'Different')
                elif case == 'extra':
                    params['changes']['status'] = 'done'
                elif case == 'child':
                    extra_path = self.write('__TKT/ASSETS/AN-T-2-ASSET--child.md', 'AN-T-2', {'atom': 'AN-T-1'})
                else:
                    extra_path = self.path.with_suffix('')
                    extra_path.mkdir()
                expected = self.path.read_bytes()
                with self.assertRaises((InputError, SourceChanged)):
                    direct_update(self.selection, params, current_rows=rows)
                self.assertEqual(expected, self.path.read_bytes())
                self.path.write_bytes(original)
                if extra_path is not None:
                    extra_path.rmdir() if extra_path.is_dir() else extra_path.unlink()

    def test_draft_asset_update_uses_exact_reference(self):
        path = self.write('__TKT/ASSETS/000_draft/AN-T-1@2-draft-ASSET--draft.md', 'AN-T-1')
        path.write_bytes(path.read_bytes().replace(b'status: active', b'status: draft').replace(b'version: 1', b'version: 2'))
        rows = capture_native(self.selection).atoms
        before = path.read_bytes()
        params = {'target': {'ref_id': 'AN-T-1@2-draft', 'version': 2}, 'changes': self.params['changes']}
        outcome = direct_update(self.selection, params, current_rows=rows)
        self.assertEqual('completed', outcome['outcome'])
        self.assertEqual(('AN-T-1', 'AN-T-1@2-draft', 2, 'draft'),
                         tuple(outcome['artifact'][key] for key in ('atom_id', 'ref_id', 'version', 'status')))
        self.assertEqual(before.split(b'---\n', 2)[1], path.read_bytes().split(b'---\n', 2)[1])
        self.assertIn(b'New', path.read_bytes())
        self.assertTrue(self.path.exists())
        params['target']['version'] = 1
        with self.assertRaises(InputError):
            direct_update(self.selection, params, current_rows=rows)

    def test_archive_preserves_draft_and_version(self):
        draft = self.write('__TKT/ASSETS/000_draft/AN-T-1@2-draft-ASSET--draft.md', 'AN-T-1')
        draft.write_bytes(draft.read_bytes().replace(b'status: active', b'status: draft').replace(b'version: 1', b'version: 2'))
        rows = capture_native(self.selection).atoms
        body = self.path.read_bytes().split(b'---\n', 2)[2]
        original_draft = draft.read_bytes()
        outcome = archive_ticket(self.selection, {'target': self.params['target']}, current_rows=rows)
        self.assertEqual('completed', outcome['outcome'])
        destination = self.path.parent / '099_archived' / 'AN-T-1@1-ASSET--example.md'
        self.assertFalse(self.path.exists())
        self.assertEqual(body, destination.read_bytes().split(b'---\n', 2)[2])
        self.assertEqual(original_draft, draft.read_bytes())
        self.assertEqual(('AN-T-1@1', 1, 'archived'),
                         tuple(outcome['artifact'][key] for key in ('ref_id', 'version', 'status')))
        capture = capture_native(self.selection)
        self.assertEqual({}, capture.errors)
        self.assertEqual({'AN-T-1@1', 'AN-T-1@2-draft'},
                         {row['ref'] for row in capture.atoms if row['id'] == 'AN-T-1'})

    def test_status_failed_removal_rolls_back_only_when_proven(self):
        params = {'target': self.params['target'], 'targetStatus': 'done'}
        destination = self.path.parent / 'done' / self.path.name
        destination.parent.mkdir()
        remove = effects.remove
        def failed(root, path, digest):
            if path == self.path:
                return effects.Result(errors=[{'code': 'backend_failure', 'message': 'failure'}])
            return remove(root, path, digest)
        with patch.object(effects, 'remove', side_effect=failed):
            outcome = change_ticket_status(self.selection, params, current_rows=self.rows, check_definition=lambda: None)
        self.assertEqual(['create', 'remove'], [effect['operation'] for effect in outcome['effects']])
        self.assertTrue(self.path.exists())
        self.assertFalse(destination.exists())
        def uncertain(root, path, digest):
            return effects.Result(effects=[{'operation': 'remove', 'state': 'unknown'}],
                                  errors=[{'code': 'effect_uncertain', 'message': 'failure'}])
        with patch.object(effects, 'remove', side_effect=uncertain):
            outcome = change_ticket_status(self.selection, params, current_rows=self.rows, check_definition=lambda: None)
        self.assertEqual(['create', 'remove'], [effect['operation'] for effect in outcome['effects']])
        self.assertEqual('unknown', outcome['effects'][1]['state'])
        self.assertTrue(destination.exists())

    def test_archive_rejects_draft_and_stale_selection(self):
        params = {'target': {'ref_id': 'AN-T-1@1-draft', 'version': 1}}
        with self.assertRaises(InputError):
            archive_ticket(self.selection, params, current_rows=self.rows)
        params['target'] = self.params['target']
        self.path.write_bytes(self.path.read_bytes() + b'stale')
        with self.assertRaises(SourceChanged):
            archive_ticket(self.selection, params, current_rows=self.rows)
        self.assertTrue(self.path.exists())

    def test_body_update_rejects_task(self):
        path = self.write('__TKT/TASKS/AN-T-3-TASK--task.md', 'AN-T-3')
        rows = capture_native(self.selection).atoms
        for row in rows:
            row['_source_sha256'] = sha256((self.root / row['source_path']).read_bytes()).hexdigest()
        params = {'target': {'ref_id': 'AN-T-3', 'version': 1}, 'changes': self.params['changes']}
        before = path.read_bytes()
        with self.assertRaises(InputError):
            direct_update(self.selection, params, current_rows=rows)
        self.assertEqual(before, path.read_bytes())

    def test_body_update_accepts_linked_report_with_original_summary_heading(self):
        path = self.write('__TKT/TASKS/done/AN-T-3-ANALYSIS_REPORT--report.md', 'AN-T-3')
        path.write_bytes(path.read_bytes().replace(
            b'context:\n', b'context:\n  template: Analysis Report\n',
        ).replace(b'## Summary', b'# Summary'))
        body = self.params['changes']['body'].replace('## Summary', '# Summary')
        output = direct_update(self.selection, {
            'target': {'ref_id': 'AN-T-3', 'version': 1}, 'changes': {'body': body},
        }, current_rows=capture_native(self.selection).atoms)
        self.assertEqual('completed', output['outcome'])
        self.assertTrue(path.read_bytes().endswith(body.encode()))

    def test_status_moves_and_preserves_body_and_identity(self):
        before = self.path.read_bytes()
        checks = []
        params = {'target': self.params['target'], 'targetStatus': 'Done'}
        output = change_ticket_status(self.selection, params, current_rows=self.rows,
                                      check_definition=lambda: checks.append(True))
        destination = self.path.parent / 'done' / self.path.name
        self.assertEqual('completed', output['outcome'])
        self.assertEqual(['create', 'create', 'remove'], [item['operation'] for item in output['effects']])
        self.assertEqual(3, len(checks))
        self.assertFalse(self.path.exists())
        self.assertEqual(before.split(b'---\n', 2)[2], destination.read_bytes().split(b'---\n', 2)[2])
        parsed = yaml.safe_load(destination.read_text().split('---\n', 2)[1])
        self.assertEqual(('AN-T-1', 1, 'done'), (parsed['identity']['atom_id'], parsed['state']['version'], parsed['state']['status']))
        self.assertNotEqual('2026-11-19T00:00:00Z', parsed['state']['updated_at'])
        self.assertEqual(destination.relative_to(self.root).as_posix(), output['artifact']['path'])
        rows = capture_native(self.selection).atoms
        for row in rows:
            row['_source_sha256'] = sha256((self.root / row['source_path']).read_bytes()).hexdigest()
        reopened = change_ticket_status(self.selection, {'target': self.params['target'], 'targetStatus': 'active'},
                                        current_rows=rows, check_definition=lambda: None)
        self.assertEqual('completed', reopened['outcome'])
        self.assertTrue(self.path.exists())
        self.assertFalse(destination.exists())

    def test_status_uses_each_branch_and_current_status_folder(self):
        for number, (branch, status) in enumerate((('TASKS', 'backlog'), ('ISSUES', 'resolved'),
                                                    ('ASSETS', 'canceled')), 2):
            identity = f'AN-T-{number}'
            path = self.write(f'__TKT/{branch}/{identity}-TICKET--example.md', identity)
            rows = capture_native(self.selection).atoms
            for row in rows:
                row['_source_sha256'] = sha256((self.root / row['source_path']).read_bytes()).hexdigest()
            outcome = change_ticket_status(self.selection,
                                           {'target': {'ref_id': identity, 'version': 1}, 'targetStatus': status},
                                           current_rows=rows, check_definition=lambda: None)
            self.assertEqual('completed', outcome['outcome'])
            self.assertTrue((path.parent / status / path.name).is_file())
            self.assertFalse(path.exists())

    def test_status_collision_and_definition_failure_preserve_source(self):
        params = {'target': self.params['target'], 'targetStatus': 'done'}
        original = self.path.read_bytes()
        destination = self.path.parent / 'done' / self.path.name
        destination.parent.mkdir()
        destination.write_bytes(b'occupied')
        outcome = change_ticket_status(self.selection, params, current_rows=self.rows, check_definition=lambda: None)
        self.assertEqual('failed', outcome['outcome'])
        self.assertEqual([], outcome['effects'])
        self.assertEqual(original, self.path.read_bytes())
        self.assertEqual(b'occupied', destination.read_bytes())
        destination.unlink()
        calls = []
        def check():
            calls.append(True)
            if len(calls) == 2:
                raise ValueError('definition changed')
        outcome = change_ticket_status(self.selection, params, current_rows=self.rows, check_definition=check)
        self.assertEqual('failed', outcome['outcome'])
        self.assertEqual(['create', 'remove'], [effect['operation'] for effect in outcome['effects']])
        self.assertEqual('definition_revalidation_required', outcome['errors'][0]['code'])
        self.assertEqual(original, self.path.read_bytes())
        self.assertFalse(destination.exists())

    def test_status_reports_partial_when_source_changes_before_removal(self):
        params = {'target': self.params['target'], 'targetStatus': 'done'}
        destination = self.path.parent / 'done' / self.path.name
        destination.parent.mkdir()
        calls = []
        def check():
            calls.append(True)
            if len(calls) == 2:
                self.path.write_bytes(self.path.read_bytes() + b'Changed concurrently')
        outcome = change_ticket_status(self.selection, params, current_rows=self.rows, check_definition=check)
        self.assertEqual('failed', outcome['outcome'])
        self.assertEqual(['create'], [effect['operation'] for effect in outcome['effects']])
        self.assertEqual('stale_state', outcome['errors'][0]['code'])
        self.assertTrue(destination.exists())
        self.assertIn(b'Changed concurrently', self.path.read_bytes())

    def test_epic_done_requires_terminal_descendants_and_preserves_them(self):
        self.path.write_bytes(self.path.read_bytes().replace(b'context:\n', b'context:\n  template: epic\n'))
        child = self.write('__TKT/TASKS/done/AN-T-2-TASK--child.md', 'AN-T-2', {'atom': 'AN-T-1'})
        child.write_bytes(child.read_bytes().replace(b'status: active', b'status: done'))
        grandchild = self.write('__TKT/TASKS/AN-T-3-TASK--child.md', 'AN-T-3', {'atom': 'AN-T-2'})
        params = {'target': self.params['target'], 'targetStatus': 'done'}
        rows = capture_native(self.selection).atoms
        original = self.path.read_bytes()
        with self.assertRaises(InputError):
            change_ticket_status(self.selection, params, current_rows=rows, check_definition=lambda: None)
        self.assertEqual(original, self.path.read_bytes())
        grandchild.write_bytes(grandchild.read_bytes().replace(b'status: active', b'status: canceled'))
        before = (child.read_bytes(), grandchild.read_bytes())
        outcome = change_ticket_status(self.selection, params, current_rows=rows, check_definition=lambda: None)
        self.assertEqual('completed', outcome['outcome'])
        self.assertEqual(before, (child.read_bytes(), grandchild.read_bytes()))

    def test_nested_leaf_status_and_archive_use_local_slots(self):
        epic = self.write('__TKT/TASKS/AN-T-2-EPIC--owner.md', 'AN-T-2')
        epic.write_bytes(epic.read_bytes().replace(b'context:\n', b'context:\n  template: epic\n'))
        task = self.write('__TKT/TASKS/AN-T-2-EPIC--owner/AN-T-3-TASK--child.md', 'AN-T-3', {'atom': 'AN-T-2'})
        task.write_bytes(task.read_bytes().replace(b'context:\n', b'context:\n  template: task\n'))
        report = self.write('__TKT/TASKS/AN-T-2-EPIC--owner/ASSETS/AN-T-4-WORK_REPORT--report.md',
                            'AN-T-4', {'atom': 'AN-T-2'})
        report.write_bytes(report.read_bytes().replace(b'context:\n', b'context:\n  template: work_report\n'))
        for path, identity in ((task, 'AN-T-3'), (report, 'AN-T-4')):
            params = {'target': {'ref_id': identity, 'version': 1}, 'targetStatus': 'done'}
            result = change_ticket_status(self.selection, params, current_rows=capture_native(self.selection).atoms,
                                          check_definition=lambda: None)
            self.assertEqual('completed', result['outcome'])
            moved = path.parent / 'done' / path.name
            self.assertTrue(moved.is_file())
            result = archive_ticket(self.selection, {'target': params['target']},
                                    current_rows=capture_native(self.selection).atoms)
            self.assertEqual('completed', result['outcome'])
            self.assertTrue((path.parent / '099_archived' / path.name.replace(identity, identity + '@1')).is_file())
            self.assertFalse(moved.exists())

    def test_epic_close_moves_valid_companion_and_preserves_descendants(self):
        epic = self.write('__TKT/TASKS/AN-T-2-EPIC--owner.md', 'AN-T-2')
        epic.write_bytes(epic.read_bytes().replace(b'context:\n', b'context:\n  template: epic\n'))
        child = self.write('__TKT/TASKS/AN-T-2-EPIC--owner/done/AN-T-3-TASK--child.md', 'AN-T-3', {'atom': 'AN-T-2'})
        child.write_bytes(child.read_bytes().replace(b'context:\n', b'context:\n  template: task\n').replace(b'status: active', b'status: done'))
        nested = self.write('__TKT/TASKS/AN-T-2-EPIC--owner/done/AN-T-3-TASK--child/canceled/AN-T-4-TASK--nested.md',
                            'AN-T-4', {'atom': 'AN-T-3'})
        nested.write_bytes(nested.read_bytes().replace(b'context:\n', b'context:\n  template: task\n').replace(b'status: active', b'status: canceled'))
        draft = self.write('__TKT/TASKS/AN-T-2-EPIC--owner/000_draft/AN-T-3@2-draft-TASK--child.md',
                           'AN-T-3', {'atom': 'AN-T-2'})
        draft.write_bytes(draft.read_bytes().replace(b'context:\n', b'context:\n  template: task\n').replace(
            b'status: active', b'status: draft').replace(b'version: 1', b'version: 2'))
        before = child.read_bytes(), nested.read_bytes(), draft.read_bytes()
        params = {'target': {'ref_id': 'AN-T-2', 'version': 1}, 'targetStatus': 'done'}
        result = change_ticket_status(self.selection, params, current_rows=capture_native(self.selection).atoms,
                                      check_definition=lambda: None)
        self.assertEqual('completed', result['outcome'])
        destination = epic.parent / 'done' / epic.name
        self.assertTrue(destination.is_file())
        self.assertFalse(epic.exists())
        for path, raw in zip((child, nested, draft), before):
            self.assertEqual(raw, (destination.with_suffix('') / path.relative_to(epic.with_suffix(''))).read_bytes())
        self.assertFalse(epic.with_suffix('').exists())

    def test_epic_close_collision_and_failed_remove_keep_tree(self):
        epic = self.write('__TKT/TASKS/AN-T-2-EPIC--owner.md', 'AN-T-2')
        epic.write_bytes(epic.read_bytes().replace(b'context:\n', b'context:\n  template: epic\n'))
        child = self.write('__TKT/TASKS/AN-T-2-EPIC--owner/done/AN-T-3-TASK--child.md', 'AN-T-3', {'atom': 'AN-T-2'})
        child.write_bytes(child.read_bytes().replace(b'context:\n', b'context:\n  template: task\n').replace(b'status: active', b'status: done'))
        params = {'target': {'ref_id': 'AN-T-2', 'version': 1}, 'targetStatus': 'done'}
        destination = epic.parent / 'done' / epic.name
        destination.with_suffix('').mkdir(parents=True)
        before = epic.read_bytes(), child.read_bytes()
        result = change_ticket_status(self.selection, params, current_rows=capture_native(self.selection).atoms,
                                      check_definition=lambda: None)
        self.assertEqual('destination_exists', result['errors'][0]['code'])
        self.assertEqual(before, (epic.read_bytes(), child.read_bytes()))
        destination.with_suffix('').rmdir()
        remove = effects.remove
        def fail_epic(root, path, digest):
            if path == epic:
                return effects.Result(errors=[{'code': 'backend_failure', 'message': 'failure'}])
            return remove(root, path, digest)
        with patch.object(effects, 'remove', side_effect=fail_epic):
            result = change_ticket_status(self.selection, params, current_rows=capture_native(self.selection).atoms,
                                          check_definition=lambda: None)
        self.assertEqual('failed', result['outcome'])
        self.assertEqual(before, (epic.read_bytes(), child.read_bytes()))
        self.assertFalse(destination.exists())
        self.assertFalse(destination.with_suffix('').exists())

    def test_epic_close_no_effect_tree_failure_rolls_back_parent(self):
        epic = self.write('__TKT/TASKS/AN-T-2-EPIC--owner.md', 'AN-T-2')
        epic.write_bytes(epic.read_bytes().replace(b'context:\n', b'context:\n  template: epic\n'))
        child = self.write('__TKT/TASKS/AN-T-2-EPIC--owner/done/AN-T-3-TASK--child.md', 'AN-T-3', {'atom': 'AN-T-2'})
        child.write_bytes(child.read_bytes().replace(b'context:\n', b'context:\n  template: task\n').replace(b'status: active', b'status: done'))
        before = epic.read_bytes(), child.read_bytes()
        destination = epic.parent / 'done' / epic.name
        with patch('ATOM_LIFECYCLE.native_update.move_directory', return_value=effects.Result(
                errors=[{'code': 'backend_failure', 'message': 'failure'}])):
            result = change_ticket_status(self.selection,
                {'target': {'ref_id': 'AN-T-2', 'version': 1}, 'targetStatus': 'done'},
                current_rows=capture_native(self.selection).atoms, check_definition=lambda: None)
        self.assertEqual('failed', result['outcome'])
        self.assertEqual(before, (epic.read_bytes(), child.read_bytes()))
        self.assertFalse(destination.exists())
        self.assertFalse(destination.with_suffix('').exists())

    def test_epic_close_keeps_destination_when_source_changed_on_remove(self):
        epic = self.write('__TKT/TASKS/AN-T-2-EPIC--owner.md', 'AN-T-2')
        epic.write_bytes(epic.read_bytes().replace(b'context:\n', b'context:\n  template: epic\n'))
        child = self.write('__TKT/TASKS/AN-T-2-EPIC--owner/done/AN-T-3-TASK--child.md', 'AN-T-3', {'atom': 'AN-T-2'})
        child.write_bytes(child.read_bytes().replace(b'context:\n', b'context:\n  template: task\n').replace(b'status: active', b'status: done'))
        before = child.read_bytes()
        destination = epic.parent / 'done' / epic.name
        remove = effects.remove
        def change_source(root, path, digest):
            if path == epic:
                epic.write_bytes(epic.read_bytes() + b'concurrent change')
                return effects.Result(errors=[{'code': 'stale_state', 'message': 'failure'}])
            return remove(root, path, digest)
        with patch.object(effects, 'remove', side_effect=change_source):
            result = change_ticket_status(self.selection,
                {'target': {'ref_id': 'AN-T-2', 'version': 1}, 'targetStatus': 'done'},
                current_rows=capture_native(self.selection).atoms, check_definition=lambda: None)
        self.assertEqual('failed', result['outcome'])
        self.assertIn(b'concurrent change', epic.read_bytes())
        self.assertTrue(destination.is_file())
        self.assertEqual(before, (destination.with_suffix('') / child.relative_to(epic.with_suffix(''))).read_bytes())

    def test_epic_close_rejects_nonterminal_and_unrelated_tree(self):
        epic = self.write('__TKT/TASKS/AN-T-2-EPIC--owner.md', 'AN-T-2')
        epic.write_bytes(epic.read_bytes().replace(b'context:\n', b'context:\n  template: epic\n'))
        child = self.write('__TKT/TASKS/AN-T-2-EPIC--owner/AN-T-3-TASK--child.md', 'AN-T-3', {'atom': 'AN-T-2'})
        child.write_bytes(child.read_bytes().replace(b'context:\n', b'context:\n  template: task\n'))
        params = {'target': {'ref_id': 'AN-T-2', 'version': 1}, 'targetStatus': 'done'}
        with self.assertRaises(InputError):
            change_ticket_status(self.selection, params, current_rows=capture_native(self.selection).atoms,
                                 check_definition=lambda: None)
        child.write_bytes(child.read_bytes().replace(b'status: active', b'status: done'))
        done = child.parent / 'done' / child.name
        done.parent.mkdir()
        child.rename(done)
        unrelated = self.write('__TKT/TASKS/AN-T-2-EPIC--owner/AN-T-4-TASK--unrelated.md',
                               'AN-T-4', {'component': 'C0'})
        with self.assertRaises(InputError):
            change_ticket_status(self.selection, params, current_rows=capture_native(self.selection).atoms,
                                 check_definition=lambda: None)
        with self.assertRaises(InputError):
            archive_ticket(self.selection, {'target': params['target']}, current_rows=capture_native(self.selection).atoms)
        self.assertTrue(epic.exists())
        self.assertTrue(done.exists())
        self.assertTrue(unrelated.exists())

    def test_epic_close_rejects_companion_change_during_validation(self):
        epic = self.write('__TKT/TASKS/AN-T-2-EPIC--owner.md', 'AN-T-2')
        epic.write_bytes(epic.read_bytes().replace(b'context:\n', b'context:\n  template: epic\n'))
        child = self.write('__TKT/TASKS/AN-T-2-EPIC--owner/done/AN-T-3-TASK--child.md', 'AN-T-3', {'atom': 'AN-T-2'})
        child.write_bytes(child.read_bytes().replace(b'context:\n', b'context:\n  template: task\n').replace(b'status: active', b'status: done'))
        rows = capture_native(self.selection).atoms
        def capture_then_change(selection):
            captured = capture_native(selection)
            child.write_bytes(child.read_bytes() + b'concurrent change')
            return captured
        with patch('ATOM_LIFECYCLE.native_update.capture_native', side_effect=capture_then_change):
            with self.assertRaises(SourceChanged):
                change_ticket_status(self.selection,
                    {'target': {'ref_id': 'AN-T-2', 'version': 1}, 'targetStatus': 'done'},
                    current_rows=rows, check_definition=lambda: None)
        self.assertTrue(epic.exists())
        self.assertIn(b'concurrent change', child.read_bytes())
        self.assertFalse((epic.parent / 'done' / epic.name).exists())

    def test_epic_close_restores_tree_when_definition_changes_after_move(self):
        epic = self.write('__TKT/TASKS/AN-T-2-EPIC--owner.md', 'AN-T-2')
        epic.write_bytes(epic.read_bytes().replace(b'context:\n', b'context:\n  template: epic\n'))
        child = self.write('__TKT/TASKS/AN-T-2-EPIC--owner/done/AN-T-3-TASK--child.md', 'AN-T-3', {'atom': 'AN-T-2'})
        child.write_bytes(child.read_bytes().replace(b'context:\n', b'context:\n  template: task\n').replace(b'status: active', b'status: done'))
        destination = epic.parent / 'done' / epic.name
        destination.parent.mkdir()
        before = epic.read_bytes(), child.read_bytes()
        calls = []
        def check():
            calls.append(True)
            if len(calls) == 3:
                raise ValueError('definition changed')
        result = change_ticket_status(self.selection,
            {'target': {'ref_id': 'AN-T-2', 'version': 1}, 'targetStatus': 'done'},
            current_rows=capture_native(self.selection).atoms, check_definition=check)
        self.assertEqual('definition_revalidation_required', result['errors'][0]['code'])
        self.assertEqual(before, (epic.read_bytes(), child.read_bytes()))
        self.assertFalse(destination.exists())
        self.assertFalse(destination.with_suffix('').exists())

    def test_status_rejects_stale_and_container(self):
        params = {'target': self.params['target'], 'targetStatus': 'done'}
        original = self.path.read_bytes()
        self.path.write_bytes(original.replace(b'version: 1', b'version: 2'))
        with self.assertRaises(SourceChanged):
            change_ticket_status(self.selection, params, current_rows=self.rows, check_definition=lambda: None)
        self.path.write_bytes(original)
        child = self.write('__TKT/ASSETS/AN-T-2-ASSET--child.md', 'AN-T-2', {'atom': 'AN-T-1'})
        with self.assertRaises(InputError):
            change_ticket_status(self.selection, params, current_rows=self.rows, check_definition=lambda: None)
        self.assertTrue(child.exists())
        self.assertEqual(original, self.path.read_bytes())


if __name__ == '__main__':
    unittest.main()
