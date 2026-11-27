from pathlib import Path
import sys
import unittest
from unittest.mock import patch


sys.path.insert(0, str((ENGINE := (TOOLS := Path(__file__).resolve()
    .parents[1]).parents[1]) / 'IWE_CONSOLE_C43'))
sys.path.insert(0, str(TOOLS))

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import capture_native
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.ATOM_LIFECYCLE__shared import InputError, SourceChanged
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.ATOM_LIFECYCLE__shared import effects_module as effects
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.ATOM_LIFECYCLE__shared import archive_ticket, change_ticket_status


from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__tests.native_lifecycle_update_support import NativeUpdateSupport


class NativeDirectUpdateTests(NativeUpdateSupport, unittest.TestCase):
    def test_partial_cascade_reports_completed_actions_and_stops(self):
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.ATOM_LIFECYCLE__shared import native_update
        parent = self.write(
            "001_TICKETS/TASKS/AN-T-40-EPIC--parent.md", "AN-T-40"
        )
        parent.write_bytes(parent.read_bytes().replace(b'context:\n', b'context:\n  template: epic\n'))
        children = []
        for identity in ('AN-T-41', 'AN-T-42'):
            child = self.write(f'001_TICKETS/TASKS/AN-T-40-EPIC--parent/{identity}-TASK--child.md',
                               identity, {'atom': 'AN-T-40'})
            child.write_bytes(child.read_bytes().replace(b'context:\n', b'context:\n  template: task\n'))
            children.append(child)
        original_move = native_update._move_ticket
        calls = []
        def fail_second(*args, **kwargs):
            calls.append(args[1]["ref_id"])
            if len(calls) == 2:
                return {
                    "effects": [],
                    "errors": [{"code": "injected", "message": "blocked"}],
                }
            return original_move(*args, **kwargs)
        with patch.object(
            native_update, "_move_ticket", side_effect=fail_second
        ):
            outcome = change_ticket_status(
                self.selection,
                {
                    "target": {"ref_id": "AN-T-40", "version": 1},
                    "targetStatus": "done",
                },
                current_rows=capture_native(self.selection).atoms,
                check_definition=lambda: None,
            )
        self.assertEqual('failed', outcome['outcome'])
        self.assertEqual('AN-T-42', outcome['errors'][0]['target'])
        self.assertTrue(outcome['effects'])
        self.assertEqual(['AN-T-41', 'AN-T-42'], calls)
        self.assertTrue(
            (children[0].parent / "canceled" / children[0].name).is_file()
        )
        self.assertTrue(children[1].is_file())
        self.assertTrue(parent.is_file())

    def test_leaf_status_uses_one_capture(self):
        with patch('FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.native_update.capture_native', wraps=capture_native) as capture:
            outcome = change_ticket_status(self.selection,
                {'target': self.params['target'], 'targetStatus': 'done'},
                current_rows=self.rows, check_definition=lambda: None)
        self.assertEqual('completed', outcome['outcome'])
        self.assertEqual(1, capture.call_count)

    def test_epic_close_moves_valid_companion_and_preserves_descendants(self):
        epic = self.write('001_TICKETS/TASKS/AN-T-2-EPIC--owner.md', 'AN-T-2')
        epic.write_bytes(
            epic.read_bytes().replace(
                b"context:\n", b"context:\n  template: epic\n"
            )
        )
        child = self.write(
            "001_TICKETS/TASKS/AN-T-2-EPIC--owner/done/AN-T-3-TASK--child.md",
            "AN-T-3",
            {"atom": "AN-T-2"},
        )
        child.write_bytes(
            child.read_bytes()
            .replace(b"context:\n", b"context:\n  template: task\n")
            .replace(b"status: active", b"status: done")
        )
        nested = self.write('001_TICKETS/TASKS/AN-T-2-EPIC--owner/done/AN-T-3-TASK--child/canceled/AN-T-4-TASK--nested.md',
                            'AN-T-4', {'atom': 'AN-T-3'})
        nested.write_bytes(nested.read_bytes().replace(b'context:\n', b'context:\n  template: task\n').replace(b'status: active', b'status: canceled'))
        draft = self.write('001_TICKETS/TASKS/AN-T-2-EPIC--owner/01_draft/AN-T-3@2-draft-TASK--child.md',
                           'AN-T-3', {'atom': 'AN-T-2'})
        draft.write_bytes(
            draft.read_bytes()
            .replace(b"context:\n", b"context:\n  template: task\n")
            .replace(b"status: active", b"status: draft")
            .replace(b"version: 1", b"version: 2")
        )
        before = child.read_bytes(), nested.read_bytes(), draft.read_bytes()
        params = {
            "target": {"ref_id": "AN-T-2", "version": 1},
            "targetStatus": "done",
        }
        result = change_ticket_status(self.selection, params, current_rows=capture_native(self.selection).atoms,
                                      check_definition=lambda: None)
        self.assertEqual('completed', result['outcome'])
        destination = epic.parent / 'done' / epic.name
        self.assertTrue(destination.is_file())
        self.assertFalse(epic.exists())
        for path, raw in zip((child, nested, draft), before, strict=False):
            self.assertEqual(raw, (destination.with_suffix('') / path.relative_to(epic.with_suffix(''))).read_bytes())
        self.assertFalse(epic.with_suffix('').exists())

    def test_epic_close_collision_and_failed_remove_keep_tree(self):
        epic = self.write('001_TICKETS/TASKS/AN-T-2-EPIC--owner.md', 'AN-T-2')
        epic.write_bytes(
            epic.read_bytes().replace(
                b"context:\n", b"context:\n  template: epic\n"
            )
        )
        child = self.write(
            "001_TICKETS/TASKS/AN-T-2-EPIC--owner/done/AN-T-3-TASK--child.md",
            "AN-T-3",
            {"atom": "AN-T-2"},
        )
        child.write_bytes(
            child.read_bytes()
            .replace(b"context:\n", b"context:\n  template: task\n")
            .replace(b"status: active", b"status: done")
        )
        params = {
            "target": {"ref_id": "AN-T-2", "version": 1},
            "targetStatus": "done",
        }
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
                return effects.Result(
                    errors=[{"code": "backend_failure", "message": "failure"}]
                )
            return remove(root, path, digest)
        with patch.object(effects, 'remove', side_effect=fail_epic):
            result = change_ticket_status(self.selection, params, current_rows=capture_native(self.selection).atoms,
                                          check_definition=lambda: None)
        self.assertEqual('failed', result['outcome'])
        self.assertEqual(before, (epic.read_bytes(), child.read_bytes()))
        self.assertFalse(destination.exists())
        self.assertFalse(destination.with_suffix('').exists())

    def test_epic_close_no_effect_tree_failure_rolls_back_parent(self):
        epic = self.write('001_TICKETS/TASKS/AN-T-2-EPIC--owner.md', 'AN-T-2')
        epic.write_bytes(epic.read_bytes().replace(b'context:\n', b'context:\n  template: epic\n'))
        child = self.write('001_TICKETS/TASKS/AN-T-2-EPIC--owner/done/AN-T-3-TASK--child.md', 'AN-T-3', {'atom': 'AN-T-2'})
        child.write_bytes(child.read_bytes().replace(b'context:\n', b'context:\n  template: task\n').replace(b'status: active', b'status: done'))
        before = epic.read_bytes(), child.read_bytes()
        destination = epic.parent / 'done' / epic.name
        with patch('FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.native_update.move_directory', return_value=effects.Result(
                errors=[{'code': 'backend_failure', 'message': 'failure'}])):
            result = change_ticket_status(self.selection,
                {'target': {'ref_id': 'AN-T-2', 'version': 1}, 'targetStatus': 'done'},
                current_rows=capture_native(self.selection).atoms, check_definition=lambda: None)
        self.assertEqual('failed', result['outcome'])
        self.assertEqual(before, (epic.read_bytes(), child.read_bytes()))
        self.assertFalse(destination.exists())
        self.assertFalse(destination.with_suffix('').exists())

    def test_epic_close_keeps_destination_when_source_changed_on_remove(self):
        epic = self.write('001_TICKETS/TASKS/AN-T-2-EPIC--owner.md', 'AN-T-2')
        epic.write_bytes(
            epic.read_bytes().replace(
                b"context:\n", b"context:\n  template: epic\n"
            )
        )
        child = self.write('001_TICKETS/TASKS/AN-T-2-EPIC--owner/done/AN-T-3-TASK--child.md', 'AN-T-3', {'atom': 'AN-T-2'})
        child.write_bytes(child.read_bytes().replace(b'context:\n', b'context:\n  template: task\n').replace(b'status: active', b'status: done'))
        before = child.read_bytes()
        destination = epic.parent / 'done' / epic.name
        remove = effects.remove
        def change_source(root, path, digest):
            if path == epic:
                epic.write_bytes(epic.read_bytes() + b"concurrent change")
                return effects.Result(
                    errors=[{"code": "stale_state", "message": "failure"}]
                )
            return remove(root, path, digest)
        with patch.object(effects, "remove", side_effect=change_source):
            result = change_ticket_status(
                self.selection,
                {
                    "target": {"ref_id": "AN-T-2", "version": 1},
                    "targetStatus": "done",
                },
                current_rows=capture_native(self.selection).atoms,
                check_definition=lambda: None,
            )
        self.assertEqual('failed', result['outcome'])
        self.assertIn(b'concurrent change', epic.read_bytes())
        self.assertTrue(destination.is_file())
        self.assertEqual(before, (destination.with_suffix('') / child.relative_to(epic.with_suffix(''))).read_bytes())

    def test_epic_close_rejects_unrelated_tree(self):
        epic = self.write("001_TICKETS/TASKS/AN-T-2-EPIC--owner.md", "AN-T-2")
        epic.write_bytes(
            epic.read_bytes().replace(
                b"context:\n", b"context:\n  template: epic\n"
            )
        )
        unrelated = self.write(
            "001_TICKETS/TASKS/AN-T-2-EPIC--owner/AN-T-4-TASK--unrelated.md",
            "AN-T-4",
            {"component": "C0"},
        )
        params = {
            "target": {"ref_id": "AN-T-2", "version": 1},
            "targetStatus": "done",
        }
        with self.assertRaises(InputError):
            change_ticket_status(
                self.selection,
                params,
                current_rows=capture_native(self.selection).atoms,
                check_definition=lambda: None,
            )
        with self.assertRaises(InputError):
            archive_ticket(
                self.selection,
                {"target": params["target"]},
                current_rows=capture_native(self.selection).atoms,
            )
        self.assertTrue(epic.exists())
        self.assertTrue(unrelated.exists())

    def test_epic_close_rejects_companion_change_during_validation(self):
        epic = self.write('001_TICKETS/TASKS/AN-T-2-EPIC--owner.md', 'AN-T-2')
        epic.write_bytes(epic.read_bytes().replace(b'context:\n', b'context:\n  template: epic\n'))
        child = self.write('001_TICKETS/TASKS/AN-T-2-EPIC--owner/done/AN-T-3-TASK--child.md', 'AN-T-3', {'atom': 'AN-T-2'})
        child.write_bytes(child.read_bytes().replace(b'context:\n', b'context:\n  template: task\n').replace(b'status: active', b'status: done'))
        rows = capture_native(self.selection).atoms
        def capture_then_change(selection, *, domains=None):
            captured = capture_native(selection, domains=domains)
            child.write_bytes(child.read_bytes() + b'concurrent change')
            return captured
        with patch('FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.native_update.capture_native', side_effect=capture_then_change):
            with self.assertRaises(SourceChanged):
                change_ticket_status(self.selection,
                    {'target': {'ref_id': 'AN-T-2', 'version': 1}, 'targetStatus': 'done'},
                    current_rows=rows, check_definition=lambda: None)
        self.assertTrue(epic.exists())
        self.assertIn(b'concurrent change', child.read_bytes())
        self.assertFalse((epic.parent / 'done' / epic.name).exists())

    def test_epic_close_restores_tree_when_definition_changes_after_move(self):
        epic = self.write("001_TICKETS/TASKS/AN-T-2-EPIC--owner.md", "AN-T-2")
        epic.write_bytes(
            epic.read_bytes().replace(
                b"context:\n", b"context:\n  template: epic\n"
            )
        )
        child = self.write(
            "001_TICKETS/TASKS/AN-T-2-EPIC--owner/done/AN-T-3-TASK--child.md",
            "AN-T-3",
            {"atom": "AN-T-2"},
        )
        child.write_bytes(
            child.read_bytes()
            .replace(b"context:\n", b"context:\n  template: task\n")
            .replace(b"status: active", b"status: done")
        )
        destination = epic.parent / "done" / epic.name
        destination.parent.mkdir()
        before = epic.read_bytes(), child.read_bytes()
        calls = []

        def check():
            calls.append(True)
            if len(calls) == 3:
                raise ValueError("definition changed")

        result = change_ticket_status(
            self.selection,
            {
                "target": {"ref_id": "AN-T-2", "version": 1},
                "targetStatus": "done",
            },
            current_rows=capture_native(self.selection).atoms,
            check_definition=check,
        )
        self.assertEqual(
            "definition_revalidation_required", result["errors"][0]["code"]
        )
        self.assertEqual(before, (epic.read_bytes(), child.read_bytes()))
        self.assertFalse(destination.exists())
        self.assertFalse(destination.with_suffix("").exists())

    def test_status_rejects_stale_and_container(self):
        params = {'target': self.params['target'], 'targetStatus': 'done'}
        original = self.path.read_bytes()
        self.path.write_bytes(original.replace(b'version: 1', b'version: 2'))
        with self.assertRaises(SourceChanged):
            change_ticket_status(self.selection, params, current_rows=self.rows, check_definition=lambda: None)
        self.path.write_bytes(original)
        child = self.write('001_TICKETS/ASSETS/AN-T-2-ASSET--child.md', 'AN-T-2', {'atom': 'AN-T-1'})
        with self.assertRaises(InputError):
            change_ticket_status(self.selection, params, current_rows=self.rows, check_definition=lambda: None)
        self.assertTrue(child.exists())
        self.assertEqual(original, self.path.read_bytes())
