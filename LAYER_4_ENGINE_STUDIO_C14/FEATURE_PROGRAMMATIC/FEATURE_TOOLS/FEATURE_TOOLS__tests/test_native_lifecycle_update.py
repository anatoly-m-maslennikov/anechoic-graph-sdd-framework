from hashlib import sha256
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

import yaml

TOOLS = Path(__file__).resolve().parents[1]
ENGINE = TOOLS.parents[1]
sys.path[:0] = [str(TOOLS), str(ENGINE / 'IWE_CONSOLE_C43')]

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.native_source_rows__pub import capture_native
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.common import InputError, SourceChanged
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE import effects
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.native_update import archive_ticket, change_ticket_status, direct_update
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.native_carrier_header__pub import canonical_native_header


from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__tests.native_lifecycle_update_support import NativeUpdateSupport


class NativeDirectUpdateTests(NativeUpdateSupport, unittest.TestCase):
    def test_queue_terminal_status_matches_template(self):
        for atom_id, branch, template, allowed, rejected in (
                ('AN-T-2', 'TASKS', 'task', 'done', 'resolved'),
                ('AN-T-3', 'ISSUES', 'question', 'resolved', 'done')):
            path = self.write(f'001_TICKETS/{branch}/{atom_id}-{template.upper()}--example.md', atom_id)
            _, header, body = path.read_text().split('---', 2)
            metadata = yaml.safe_load(header)
            metadata['context']['template'] = template
            metadata['state']['status'] = 'in_queue'
            path.write_text('---\n' + yaml.safe_dump(canonical_native_header(metadata)) + '---' + body)
            target = {'ref_id': atom_id, 'version': 1}
            with self.assertRaises(InputError):
                change_ticket_status(self.selection, {'target': target, 'targetStatus': rejected},
                                     current_rows=capture_native(self.selection).atoms, check_definition=lambda: None)
            outcome = change_ticket_status(self.selection, {'target': target, 'targetStatus': allowed},
                                           current_rows=capture_native(self.selection).atoms, check_definition=lambda: None)
            self.assertEqual(allowed, outcome['artifact']['status'])

    def test_standalone_asset_completes_in_its_directory(self):
        path = self.write('001_TICKETS/ASSETS/AN-T-2-WORK_LOG--example.md', 'AN-T-2')
        _, header, body = path.read_text().split('---', 2)
        metadata = yaml.safe_load(header)
        metadata['context']['template'] = 'work_log'
        metadata['state']['status'] = 'in_queue'
        path.write_text('---\n' + yaml.safe_dump(canonical_native_header(metadata)) + '---' + body)
        target = {'ref_id': 'AN-T-2', 'version': 1}
        outcome = change_ticket_status(self.selection, {'target': target, 'targetStatus': 'complete'},
                                       current_rows=capture_native(self.selection).atoms, check_definition=lambda: None)
        self.assertEqual('complete', outcome['artifact']['status'])
        self.assertEqual(self.control / '001_TICKETS/ASSETS/08_complete' / path.name,
                         self.root / outcome['artifact']['path'])
        self.assertFalse(path.exists())
        self.assertEqual('complete', next(row for row in capture_native(self.selection).atoms
                                          if row['id'] == 'AN-T-2')['status'])

    def test_canonical_ticket_archive_requires_current_replacement(self):
        target_path = self.write('001_TICKETS/TASKS/AN-T-2-TASK--example.md', 'AN-T-2')
        _, header, body = target_path.read_text().split('---', 2)
        metadata = yaml.safe_load(header)
        metadata['context']['template'] = 'task'
        target_path.write_text('---\n' + yaml.safe_dump(canonical_native_header(metadata)) + '---' + body)
        target = {'ref_id': 'AN-T-2', 'version': 1}
        with self.assertRaises(InputError):
            archive_ticket(self.selection, {'target': target}, current_rows=capture_native(self.selection).atoms)
        replacement = self.write('001_TICKETS/TASKS/AN-T-3-TASK--example.md', 'AN-T-3')
        _, header, body = replacement.read_text().split('---', 2)
        metadata = yaml.safe_load(header)
        metadata['context']['template'] = 'task'
        metadata['relations'] = {'IS_REPLACEMENT_FOR': ['AN-T-2']}
        replacement.write_text('---\n' + yaml.safe_dump(canonical_native_header(metadata)) + '---' + body)
        outcome = archive_ticket(self.selection, {'target': target}, current_rows=capture_native(self.selection).atoms)
        self.assertEqual('completed', outcome['outcome'], outcome)
        self.assertEqual('AN-T-2@1', outcome['artifact']['ref_id'])
        self.assertEqual('09_archived', (self.root / outcome['artifact']['path']).parent.name)
        self.assertFalse(target_path.exists())

    def test_canonical_ticket_draft_archive_uses_base_replacement_reference(self):
        path = self.write('001_TICKETS/TASKS/01_draft/AN-T-4@2-draft-TASK--example.md', 'AN-T-4')
        _, header, body = path.read_text().split('---', 2)
        metadata = yaml.safe_load(header)
        metadata['context']['template'] = 'task'
        metadata['state'].update(status='draft', version=2)
        path.write_text('---\n' + yaml.safe_dump(canonical_native_header(metadata)) + '---' + body)
        replacement = self.write('001_TICKETS/TASKS/AN-T-5-TASK--example.md', 'AN-T-5')
        _, header, body = replacement.read_text().split('---', 2)
        metadata = yaml.safe_load(header)
        metadata['context']['template'] = 'task'
        metadata['relations'] = {'IS_REPLACEMENT_FOR': ['AN-T-4']}
        replacement.write_text('---\n' + yaml.safe_dump(canonical_native_header(metadata)) + '---' + body)
        target = {'ref_id': 'AN-T-4@2-draft', 'version': 2}
        outcome = archive_ticket(self.selection, {'target': target}, current_rows=capture_native(self.selection).atoms)
        self.assertEqual('completed', outcome['outcome'], outcome)
        self.assertEqual('AN-T-4@2', outcome['artifact']['ref_id'])
        self.assertFalse(path.exists())


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
        moved = self.control / '001_TICKETS/ASSETS/done' / self.path.name
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
                    extra_path = self.write('001_TICKETS/ASSETS/AN-T-2-ASSET--child.md', 'AN-T-2', {'atom': 'AN-T-1'})
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
        path = self.write('001_TICKETS/ASSETS/01_draft/AN-T-1@2-draft-ASSET--draft.md', 'AN-T-1')
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
        draft = self.write('001_TICKETS/ASSETS/01_draft/AN-T-1@2-draft-ASSET--draft.md', 'AN-T-1')
        draft.write_bytes(draft.read_bytes().replace(b'status: active', b'status: draft').replace(b'version: 1', b'version: 2'))
        rows = capture_native(self.selection).atoms
        body = self.path.read_bytes().split(b'---\n', 2)[2]
        original_draft = draft.read_bytes()
        outcome = archive_ticket(self.selection, {'target': self.params['target']}, current_rows=rows)
        self.assertEqual('completed', outcome['outcome'])
        destination = self.path.parent / '09_archived' / 'AN-T-1@1-ASSET--example.md'
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

    def test_archive_rejects_missing_draft_and_stale_selection(self):
        params = {'target': {'ref_id': 'AN-T-1@1-draft', 'version': 1}}
        with self.assertRaises(SourceChanged):
            archive_ticket(self.selection, params, current_rows=self.rows)
        params['target'] = self.params['target']
        self.path.write_bytes(self.path.read_bytes() + b'stale')
        with self.assertRaises(SourceChanged):
            archive_ticket(self.selection, params, current_rows=self.rows)
        self.assertTrue(self.path.exists())

    def test_body_update_rejects_task(self):
        path = self.write('001_TICKETS/TASKS/AN-T-3-TASK--task.md', 'AN-T-3')
        rows = capture_native(self.selection).atoms
        for row in rows:
            row['_source_sha256'] = sha256((self.root / row['source_path']).read_bytes()).hexdigest()
        params = {'target': {'ref_id': 'AN-T-3', 'version': 1}, 'changes': self.params['changes']}
        before = path.read_bytes()
        with self.assertRaises(InputError):
            direct_update(self.selection, params, current_rows=rows)
        self.assertEqual(before, path.read_bytes())

    def test_body_update_accepts_linked_report_with_original_summary_heading(self):
        path = self.write('001_TICKETS/TASKS/done/AN-T-3-ANALYSIS_REPORT--report.md', 'AN-T-3')
        path.write_bytes(path.read_bytes().replace(
            b'context:\n', b'context:\n  template: Analysis Report\n',
        ).replace(b'## Summary', b'# Summary'))
        body = self.params['changes']['body'].replace('## Summary', '# Summary')
        output = direct_update(self.selection, {
            'target': {'ref_id': 'AN-T-3', 'version': 1}, 'changes': {'body': body},
        }, current_rows=capture_native(self.selection).atoms)
        self.assertEqual('completed', output['outcome'])
        self.assertTrue(path.read_bytes().endswith(body.encode()))
