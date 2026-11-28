"""Native lifecycle tree failure scenarios."""

from unittest.mock import patch

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.sources.inventory.native_source_rows__pub import (
    capture_native,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.ATOM_LIFECYCLE__shared import (
    InputError,
    SourceChanged,
    effects_module as effects,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.updates.native_update_archive import (
    archive_ticket,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.updates.native_update__shared import (
    change_ticket_status,
)


class NativeTreeFailureCases:
    def test_epic_close_no_effect_tree_failure_rolls_back_parent(self):
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
        before = epic.read_bytes(), child.read_bytes()
        destination = epic.parent / "done" / epic.name
        with patch(
            (
                'FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.updates.native_update__shared.move_directory'
            ),
            return_value=effects.Result(
                errors=[{"code": "backend_failure", "message": "failure"}]
            ),
        ):
            result = change_ticket_status(
                self.selection,
                {
                    "target": {"ref_id": "AN-T-2", "version": 1},
                    "targetStatus": "done",
                },
                current_rows=capture_native(self.selection).atoms,
                check_definition=lambda: None,
            )
        self.assertEqual("failed", result["outcome"])
        self.assertEqual(before, (epic.read_bytes(), child.read_bytes()))
        self.assertFalse(destination.exists())
        self.assertFalse(destination.with_suffix("").exists())

    def test_epic_close_keeps_destination_when_source_changed_on_remove(self):
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
        before = child.read_bytes()
        destination = epic.parent / "done" / epic.name
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
        self._assert_changed_epic(result, epic, child, destination, before)

    def _assert_changed_epic(self, result, epic, child, destination, before):
        self.assertEqual("failed", result["outcome"])
        self.assertIn(b"concurrent change", epic.read_bytes())
        self.assertTrue(destination.is_file())
        self.assertEqual(
            before,
            (
                destination.with_suffix("")
                / child.relative_to(epic.with_suffix(""))
            ).read_bytes(),
        )

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
        rows = capture_native(self.selection).atoms

        def capture_then_change(selection, *, domains=None):
            captured = capture_native(selection, domains=domains)
            child.write_bytes(child.read_bytes() + b"concurrent change")
            return captured

        with patch(
            (
                'FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.updates.native_update__shared.capture_native'
            ),
            side_effect=capture_then_change,
        ):
            with self.assertRaises(SourceChanged):
                change_ticket_status(
                    self.selection,
                    {
                        "target": {"ref_id": "AN-T-2", "version": 1},
                        "targetStatus": "done",
                    },
                    current_rows=rows,
                    check_definition=lambda: None,
                )
        self.assertTrue(epic.exists())
        self.assertIn(b"concurrent change", child.read_bytes())
        self.assertFalse((epic.parent / "done" / epic.name).exists())

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
        params = {"target": self.params["target"], "targetStatus": "done"}
        original = self.path.read_bytes()
        self.path.write_bytes(original.replace(b"version: 1", b"version: 2"))
        with self.assertRaises(SourceChanged):
            change_ticket_status(
                self.selection,
                params,
                current_rows=self.rows,
                check_definition=lambda: None,
            )
        self.path.write_bytes(original)
        child = self.write(
            "001_TICKETS/ASSETS/AN-T-2-ASSET--child.md",
            "AN-T-2",
            {"atom": "AN-T-1"},
        )
        with self.assertRaises(InputError):
            change_ticket_status(
                self.selection,
                params,
                current_rows=self.rows,
                check_definition=lambda: None,
            )
        self.assertTrue(child.exists())
        self.assertEqual(original, self.path.read_bytes())
