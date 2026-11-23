from hashlib import sha256
from pathlib import Path
import sys
import unittest

import yaml

TOOLS = Path(__file__).resolve().parents[1]
ENGINE = TOOLS.parents[1]
sys.path[:0] = [str(TOOLS), str(ENGINE / 'IWE_CONSOLE_C43')]

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import capture_native
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.ATOM_LIFECYCLE__shared import InputError
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.ATOM_LIFECYCLE__shared import archive_ticket, change_ticket_status


from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__tests.native_lifecycle_update_support import NativeUpdateSupport


class NativeDirectUpdateTests(NativeUpdateSupport, unittest.TestCase):
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
        reopened = change_ticket_status(self.selection, {'target': self.params['target'], 'targetStatus': 'in_queue'},
                                        current_rows=rows, check_definition=lambda: None)
        self.assertEqual('completed', reopened['outcome'])
        self.assertTrue(self.path.exists())
        self.assertFalse(destination.exists())

    def test_status_uses_each_branch_and_current_status_folder(self):
        for number, (branch, status) in enumerate((('TASKS', 'backlog'), ('ISSUES', 'resolved'),
                                                    ('ASSETS', 'canceled')), 2):
            identity = f'AN-T-{number}'
            path = self.write(f'001_TICKETS/{branch}/{identity}-TICKET--example.md', identity)
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

    def test_flat_descendants_are_rejected_without_detachment(self):
        self.path.write_bytes(self.path.read_bytes().replace(b'context:\n', b'context:\n  template: epic\n'))
        child = self.write('001_TICKETS/TASKS/done/AN-T-2-TASK--child.md', 'AN-T-2', {'atom': 'AN-T-1'})
        child.write_bytes(child.read_bytes().replace(b'status: active', b'status: done'))
        params = {'target': self.params['target'], 'targetStatus': 'done'}
        before = self.path.read_bytes(), child.read_bytes()
        with self.assertRaises(InputError):
            change_ticket_status(self.selection, params, current_rows=capture_native(self.selection).atoms,
                                 check_definition=lambda: None)
        self.assertEqual(before, (self.path.read_bytes(), child.read_bytes()))

    def test_nested_leaf_status_and_archive_use_local_slots(self):
        epic = self.write('001_TICKETS/TASKS/AN-T-2-EPIC--owner.md', 'AN-T-2')
        epic.write_bytes(epic.read_bytes().replace(b'context:\n', b'context:\n  template: epic\n'))
        task = self.write('001_TICKETS/TASKS/AN-T-2-EPIC--owner/AN-T-3-TASK--child.md', 'AN-T-3', {'atom': 'AN-T-2'})
        task.write_bytes(task.read_bytes().replace(b'context:\n', b'context:\n  template: task\n'))
        report = self.write('001_TICKETS/TASKS/AN-T-2-EPIC--owner/ASSETS/AN-T-4-WORK_REPORT--report.md',
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
            self.assertTrue((path.parent / '09_archived' / path.name.replace(identity, identity + '@1')).is_file())
            self.assertFalse(moved.exists())
