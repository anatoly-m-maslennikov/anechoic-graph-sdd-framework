from pathlib import Path
import sys
import unittest

import yaml

TOOLS = Path(__file__).resolve().parents[1]
ENGINE = TOOLS.parents[1]
sys.path[:0] = [str(TOOLS), str(ENGINE / 'IWE_CONSOLE_C43')]

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.native_source_rows__pub import capture_native
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.common import InputError
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.native_update import archive_ticket, change_ticket_status


from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__tests.native_lifecycle_update_support import NativeUpdateSupport


class NativeDirectUpdateTests(NativeUpdateSupport, unittest.TestCase):
    def test_cancel_task_preserves_nested_terminal_descendants_and_history(self):
        parent = self.write('001_TICKETS/TASKS/AN-T-2-TASK--parent.md', 'AN-T-2')
        parent.write_bytes(parent.read_bytes().replace(b'context:\n', b'context:\n  template: task\n'))
        companion = parent.with_suffix('')
        child = self.write('001_TICKETS/TASKS/AN-T-2-TASK--parent/done/AN-T-3-SUBTASK--child.md',
                           'AN-T-3', {'atom': 'AN-T-2'})
        child.write_bytes(child.read_bytes().replace(b'context:\n', b'context:\n  template: task\n')
                          .replace(b'status: active', b'status: done').replace(b'version: 1', b'version: 2'))
        nested = self.write('001_TICKETS/TASKS/AN-T-2-TASK--parent/done/AN-T-3-SUBTASK--child/canceled/AN-T-4-SUBTASK--nested.md',
                            'AN-T-4', {'atom': 'AN-T-3'})
        nested.write_bytes(nested.read_bytes().replace(b'context:\n', b'context:\n  template: task\n')
                           .replace(b'status: active', b'status: canceled')
                           .replace(b'state:\n', b'relations:\n  REFERENCES:\n  - AN-T-2\nstate:\n'))
        history = self.write('001_TICKETS/TASKS/AN-T-2-TASK--parent/09_archived/AN-T-3@1-SUBTASK--child.md',
                             'AN-T-3', {'atom': 'AN-T-2'})
        history.write_bytes(history.read_bytes().replace(b'context:\n', b'context:\n  template: task\n')
                            .replace(b'status: active', b'status: archived'))
        before = {path.relative_to(companion): path.read_bytes() for path in (child, nested, history)}
        result = change_ticket_status(self.selection,
            {'target': {'ref_id': 'AN-T-2', 'version': 1}, 'targetStatus': 'canceled'},
            current_rows=capture_native(self.selection).atoms, check_definition=lambda: None)
        self.assertEqual('completed', result['outcome'])
        destination = parent.parent / 'canceled' / parent.name
        self.assertFalse(parent.exists())
        self.assertFalse(companion.exists())
        self.assertEqual('canceled', yaml.safe_load(destination.read_text().split('---', 2)[1])['state']['status'])
        for relative, raw in before.items():
            self.assertEqual(raw, (destination.with_suffix('') / relative).read_bytes())

    def test_cancel_task_cancels_unfinished_descendant(self):
        parent = self.write('001_TICKETS/TASKS/AN-T-2-TASK--parent.md', 'AN-T-2')
        parent.write_bytes(parent.read_bytes().replace(b'context:\n', b'context:\n  template: task\n'))
        child = self.write('001_TICKETS/TASKS/AN-T-2-TASK--parent/AN-T-3-SUBTASK--child.md',
                           'AN-T-3', {'atom': 'AN-T-2'})
        child.write_bytes(child.read_bytes().replace(b'context:\n', b'context:\n  template: task\n'))
        outcome = change_ticket_status(self.selection,
            {'target': {'ref_id': 'AN-T-2', 'version': 1}, 'targetStatus': 'canceled'},
            current_rows=capture_native(self.selection).atoms, check_definition=lambda: None)
        self.assertEqual('completed', outcome['outcome'])
        destination = parent.parent / 'canceled' / parent.name
        self.assertTrue((destination.with_suffix('') / 'canceled' / child.name).is_file())

    def test_epic_terminal_status_cancels_mixed_nested_descendants(self):
        for number, status in ((10, 'done'), (20, 'canceled')):
            with self.subTest(status=status):
                prefix = f'001_TICKETS/TASKS/AN-T-{number}-EPIC--parent'
                parent = self.write(prefix + '.md', f'AN-T-{number}')
                parent.write_bytes(parent.read_bytes().replace(b'context:\n', b'context:\n  template: epic\n'))
                done = self.write(prefix + f'/done/AN-T-{number + 1}-TASK--done.md',
                                  f'AN-T-{number + 1}', {'atom': f'AN-T-{number}'})
                canceled = self.write(prefix + f'/canceled/AN-T-{number + 2}-TASK--canceled.md',
                                      f'AN-T-{number + 2}', {'atom': f'AN-T-{number}'})
                active = self.write(prefix + f'/AN-T-{number + 3}-TASK--active.md',
                                    f'AN-T-{number + 3}', {'atom': f'AN-T-{number}'})
                nested = self.write(prefix + f'/done/AN-T-{number + 1}-TASK--done/backlog/AN-T-{number + 4}-SUBTASK--nested.md',
                                    f'AN-T-{number + 4}', {'atom': f'AN-T-{number + 1}'})
                for path, initial in ((done, 'done'), (canceled, 'canceled'), (active, 'active'), (nested, 'backlog')):
                    path.write_bytes(path.read_bytes().replace(b'context:\n', b'context:\n  template: task\n')
                                     .replace(b'status: active', f'status: {initial}'.encode()))
                resolved = self.write(prefix + f'/resolved/AN-T-{number + 6}-QUESTION--resolved.md',
                                      f'AN-T-{number + 6}', {'atom': f'AN-T-{number}'})
                resolved.write_bytes(resolved.read_bytes().replace(b'context:\n', b'context:\n  template: question\n')
                                     .replace(b'status: active', b'status: resolved'))
                report = self.write(prefix + f'/ASSETS/AN-T-{number + 5}-WORK_REPORT--report.md',
                                    f'AN-T-{number + 5}', {'atom': f'AN-T-{number}'})
                report.write_bytes(report.read_bytes().replace(b'context:\n', b'context:\n  template: work_report\n'))
                draft = self.write(prefix + f'/01_draft/AN-T-{number + 3}@2-draft-TASK--active.md',
                                   f'AN-T-{number + 3}', {'atom': f'AN-T-{number}'})
                draft.write_bytes(draft.read_bytes().replace(b'context:\n', b'context:\n  template: task\n')
                                  .replace(b'status: active', b'status: draft').replace(b'version: 1', b'version: 2'))
                before = {path.relative_to(parent.with_suffix('')): path.read_bytes() for path in (done, canceled, draft)}
                outcome = change_ticket_status(self.selection,
                    {'target': {'ref_id': f'AN-T-{number}', 'version': 1}, 'targetStatus': status},
                    current_rows=capture_native(self.selection).atoms, check_definition=lambda: None)
                self.assertEqual('completed', outcome['outcome'], outcome)
                moved = parent.parent / status / parent.name
                for relative, raw in before.items():
                    self.assertEqual(raw, (moved.with_suffix('') / relative).read_bytes())
                for path in (active, nested):
                    relative = path.relative_to(parent.with_suffix(''))
                    new_path = moved.with_suffix('') / relative.parent.parent / 'canceled' / relative.name if path == nested else moved.with_suffix('') / 'canceled' / relative.name
                    self.assertEqual('canceled', yaml.safe_load(new_path.read_text().split('---', 2)[1])['state']['status'])
                resolved_path = moved.with_suffix('') / 'resolved' / resolved.name
                self.assertEqual('resolved', yaml.safe_load(resolved_path.read_text().split('---', 2)[1])['state']['status'])
                report_path = moved.with_suffix('') / 'ASSETS' / 'canceled' / report.name
                self.assertEqual('canceled', yaml.safe_load(report_path.read_text().split('---', 2)[1])['state']['status'])
                self.assertFalse(parent.exists())

    def test_nonterminal_status_moves_companion_without_changing_children(self):
        parent = self.write('001_TICKETS/TASKS/AN-T-30-EPIC--parent.md', 'AN-T-30')
        parent.write_bytes(parent.read_bytes().replace(b'context:\n', b'context:\n  template: epic\n'))
        child = self.write('001_TICKETS/TASKS/AN-T-30-EPIC--parent/AN-T-31-TASK--child.md',
                           'AN-T-31', {'atom': 'AN-T-30'})
        child.write_bytes(child.read_bytes().replace(b'context:\n', b'context:\n  template: task\n'))
        before = child.read_bytes()
        outcome = change_ticket_status(self.selection,
            {'target': {'ref_id': 'AN-T-30', 'version': 1}, 'targetStatus': 'backlog'},
            current_rows=capture_native(self.selection).atoms, check_definition=lambda: None)
        self.assertEqual('completed', outcome['outcome'], outcome)
        destination = self.control / '001_TICKETS/TASKS/backlog/AN-T-30-EPIC--parent'
        self.assertEqual(before, (destination / child.name).read_bytes())
        self.assertFalse(parent.exists())

    def test_task_reopening_preserves_descendant_status(self):
        prefix = '001_TICKETS/TASKS/done/AN-T-40-TASK--parent'
        parent = self.write(prefix + '.md', 'AN-T-40')
        parent.write_bytes(parent.read_bytes().replace(b'context:\n', b'context:\n  template: task\n')
                           .replace(b'status: active', b'status: done'))
        child = self.write(f'{prefix}/done/AN-T-41-SUBTASK--child.md', 'AN-T-41', {'atom': 'AN-T-40'})
        child.write_bytes(child.read_bytes().replace(b'context:\n', b'context:\n  template: task\n')
                          .replace(b'status: active', b'status: done'))
        before = child.read_bytes()
        reopened = change_ticket_status(self.selection,
            {'target': {'ref_id': 'AN-T-40', 'version': 1}, 'targetStatus': 'in_queue'},
            current_rows=capture_native(self.selection).atoms, check_definition=lambda: None)
        self.assertEqual('completed', reopened['outcome'], reopened)
        current = self.control / '001_TICKETS/TASKS/AN-T-40-TASK--parent' / 'done' / child.name
        self.assertEqual(before, current.read_bytes())

    def test_backlog_activation_promotes_nested_tasks_and_preserves_assets(self):
        parent = self.write('001_TICKETS/TASKS/backlog/AN-T-30-EPIC--parent.md', 'AN-T-30')
        parent.write_bytes(parent.read_bytes().replace(b'context:\n', b'context:\n  template: epic\n')
                           .replace(b'status: active', b'status: backlog'))
        branch = '001_TICKETS/TASKS/backlog/AN-T-30-EPIC--parent'
        child = self.write(f'{branch}/backlog/AN-T-31-TASK--child.md', 'AN-T-31', {'atom': 'AN-T-30'})
        child.write_bytes(child.read_bytes().replace(b'context:\n', b'context:\n  template: task\n')
                          .replace(b'status: active', b'status: backlog'))
        grand = self.write(f'{branch}/backlog/AN-T-31-TASK--child/backlog/AN-T-32-SUBTASK--grand.md',
                           'AN-T-32', {'atom': 'AN-T-31'})
        grand.write_bytes(grand.read_bytes().replace(b'context:\n', b'context:\n  template: task\n')
                          .replace(b'status: active', b'status: backlog'))
        asset = grand.parent.parent / 'notes.txt'
        asset.write_text('keep')
        outcome = change_ticket_status(self.selection,
            {'target': {'ref_id': 'AN-T-30', 'version': 1}, 'targetStatus': 'in_queue'},
            current_rows=capture_native(self.selection).atoms, check_definition=lambda: None)
        self.assertEqual('completed', outcome['outcome'], outcome)
        dest = self.control / '001_TICKETS/TASKS/AN-T-30-EPIC--parent/AN-T-31-TASK--child'
        self.assertEqual('in_queue', yaml.safe_load((dest / grand.name).read_text().split('---', 2)[1])['state']['status'])
        self.assertEqual('keep', (dest / 'notes.txt').read_text())
        self.assertEqual('in_queue', yaml.safe_load(dest.with_suffix('.md').read_text().split('---', 2)[1])['state']['status'])

    def test_backlog_activation_publishes_first_draft_descendant(self):
        parent = self.write('001_TICKETS/TASKS/backlog/AN-T-30-EPIC--parent.md', 'AN-T-30')
        parent.write_bytes(parent.read_bytes().replace(b'context:\n', b'context:\n  template: epic\n')
                           .replace(b'status: active', b'status: backlog'))
        child = self.write('001_TICKETS/TASKS/backlog/AN-T-30-EPIC--parent/01_draft/AN-T-31@1-draft-TASK--child.md',
                           'AN-T-31', {'atom': 'AN-T-30'})
        child.write_bytes(child.read_bytes().replace(b'context:\n', b'context:\n  template: task\n')
                          .replace(b'status: active', b'status: draft'))
        outcome = change_ticket_status(self.selection,
            {'target': {'ref_id': 'AN-T-30', 'version': 1}, 'targetStatus': 'in_queue'},
            current_rows=capture_native(self.selection).atoms, check_definition=lambda: None)
        self.assertEqual('completed', outcome['outcome'], outcome)
        destination = self.control / '001_TICKETS/TASKS/AN-T-30-EPIC--parent/AN-T-31-TASK--child.md'
        self.assertEqual('in_queue', yaml.safe_load(destination.read_text().split('---', 2)[1])['state']['status'])
        self.assertFalse(child.exists())

    def test_activation_preflights_all_child_destinations(self):
        parent = self.write('001_TICKETS/TASKS/backlog/AN-T-30-EPIC--parent.md', 'AN-T-30')
        parent.write_bytes(parent.read_bytes().replace(b'context:\n', b'context:\n  template: epic\n')
                           .replace(b'status: active', b'status: backlog'))
        branch = '001_TICKETS/TASKS/backlog/AN-T-30-EPIC--parent'
        children = []
        for number in (31, 32):
            child = self.write(f'{branch}/backlog/AN-T-{number}-TASK--child.md', f'AN-T-{number}', {'atom': 'AN-T-30'})
            child.write_bytes(child.read_bytes().replace(b'context:\n', b'context:\n  template: task\n')
                              .replace(b'status: active', b'status: backlog'))
            children.append(child)
        collision = (children[1].parent.parent / children[1].name).with_suffix('')
        collision.mkdir()
        before = [path.read_bytes() for path in [parent, *children]]
        outcome = change_ticket_status(self.selection,
            {'target': {'ref_id': 'AN-T-30', 'version': 1}, 'targetStatus': 'in_queue'},
            current_rows=capture_native(self.selection).atoms, check_definition=lambda: None)
        self.assertEqual('failed', outcome['outcome'])
        self.assertEqual('destination_exists', outcome['errors'][0]['code'])
        self.assertEqual(before, [path.read_bytes() for path in [parent, *children]])
        self.assertTrue(collision.is_dir())

    def test_reopening_epic_preserves_nested_tree_bytes(self):
        for number, status in ((50, 'done'), (60, 'canceled')):
            with self.subTest(status=status):
                epic_id = f'AN-T-{number}'
                epic = f'{epic_id}-EPIC--parent'
                prefix = f'001_TICKETS/TASKS/{status}/{epic}'
                parent = self.write(prefix + '.md', epic_id)
                parent.write_bytes(parent.read_bytes().replace(b'context:\n', b'context:\n  template: epic\n')
                                   .replace(b'status: active', f'status: {status}'.encode()))
                done_id, nested_id, canceled_id = (f'AN-T-{number + offset}' for offset in (1, 2, 3))
                done = f'done/{done_id}-TASK--done'
                before = {}
                for relative, atom_id, owner, child_status in (
                        (done + '.md', done_id, epic_id, 'done'),
                        (f'{done}/{nested_id}-SUBTASK--active.md', nested_id, done_id, 'active'),
                        (f'canceled/{canceled_id}-TASK--canceled.md', canceled_id, epic_id, 'canceled')):
                    path = self.write(f'{prefix}/{relative}', atom_id, {'atom': owner})
                    raw = path.read_bytes().replace(b'context:\n', b'context:\n  template: task\n')
                    before[relative] = raw.replace(b'status: active', f'status: {child_status}'.encode())
                    path.write_bytes(before[relative])
                outcome = change_ticket_status(self.selection,
                    {'target': {'ref_id': epic_id, 'version': 1}, 'targetStatus': 'in_queue'},
                    current_rows=capture_native(self.selection).atoms, check_definition=lambda: None)
                self.assertEqual('completed', outcome['outcome'], outcome)
                self.assertEqual('in_queue', outcome['artifact']['status'])
                destination = self.control / '001_TICKETS/TASKS' / epic
                for relative, raw in before.items():
                    self.assertEqual(raw, (destination / relative).read_bytes())
                self.assertFalse(parent.exists())
                self.assertFalse(parent.with_suffix('').exists())

    def test_archive_container_refuses_without_detachment(self):
        parent = self.write('001_TICKETS/TASKS/AN-T-30-EPIC--parent.md', 'AN-T-30')
        parent.write_bytes(parent.read_bytes().replace(b'context:\n', b'context:\n  template: epic\n'))
        child = self.write('001_TICKETS/TASKS/AN-T-30-EPIC--parent/AN-T-31-TASK--child.md',
                           'AN-T-31', {'atom': 'AN-T-30'})
        child.write_bytes(child.read_bytes().replace(b'context:\n', b'context:\n  template: task\n'))
        before = parent.read_bytes(), child.read_bytes()
        with self.assertRaises(InputError):
            archive_ticket(self.selection, {'target': {'ref_id': 'AN-T-30', 'version': 1}},
                           current_rows=capture_native(self.selection).atoms)
        self.assertEqual(before, (parent.read_bytes(), child.read_bytes()))
