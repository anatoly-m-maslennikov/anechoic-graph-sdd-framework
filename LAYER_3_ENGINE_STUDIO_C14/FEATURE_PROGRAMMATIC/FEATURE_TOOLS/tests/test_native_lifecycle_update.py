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
        path = self.write('__TKT/ASSETS/draft/AN-T-1@2-draft-ASSET--draft.md', 'AN-T-1')
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
        draft = self.write('__TKT/ASSETS/draft/AN-T-1@2-draft-ASSET--draft.md', 'AN-T-1')
        draft.write_bytes(draft.read_bytes().replace(b'status: active', b'status: draft').replace(b'version: 1', b'version: 2'))
        rows = capture_native(self.selection).atoms
        body = self.path.read_bytes().split(b'---\n', 2)[2]
        original_draft = draft.read_bytes()
        outcome = archive_ticket(self.selection, {'target': self.params['target']}, current_rows=rows)
        self.assertEqual('completed', outcome['outcome'])
        destination = self.path.parent / 'archived' / 'AN-T-1@1-ASSET--example.md'
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
