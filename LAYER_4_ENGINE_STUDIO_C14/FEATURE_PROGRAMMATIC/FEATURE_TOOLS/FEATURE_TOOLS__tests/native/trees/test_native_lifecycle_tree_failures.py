from pathlib import Path
import sys
import unittest
from unittest.mock import patch


sys.path.insert(
    0,
    str(
        (ENGINE := (TOOLS := Path(__file__).resolve().parents[3]).parents[1])
        / "IWE_CONSOLE_C43"
    ),
)
sys.path.insert(0, str(TOOLS))

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.sources.inventory.native_source_rows__pub import (
    capture_native,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.ATOM_LIFECYCLE__shared import (
    effects_module as effects,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.updates.native_update__shared import (
    change_ticket_status,
)


from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__tests.native.native_lifecycle_update_support import (
    NativeUpdateSupport,
)


from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__tests.native.trees.failures import (  # noqa: E402
    _native_lifecycle_tree_failure_cases as cases,
)


class NativeDirectUpdateTests(
    cases.NativeTreeFailureCases, NativeUpdateSupport, unittest.TestCase
):
    def test_partial_cascade_reports_completed_actions_and_stops(self):
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.updates import (
            native_update__shared as native_update,
        )

        parent, children = self._cascade_fixture()
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
        self._assert_partial_cascade(outcome, calls, children, parent)

    def _cascade_fixture(self):
        parent = self.write(
            "001_TICKETS/TASKS/AN-T-40-EPIC--parent.md", "AN-T-40"
        )
        parent.write_bytes(
            parent.read_bytes().replace(
                b"context:\n", b"context:\n  template: epic\n"
            )
        )
        children = []
        for identity in ("AN-T-41", "AN-T-42"):
            child = self.write(
                (
                    "001_TICKETS/TASKS/AN-T-40-EPIC--parent/"
                    f"{identity}"
                    "-TASK--child.md"
                ),
                identity,
                {"atom": "AN-T-40"},
            )
            child.write_bytes(
                child.read_bytes().replace(
                    b"context:\n", b"context:\n  template: task\n"
                )
            )
            children.append(child)
        return parent, children

    def _assert_partial_cascade(self, outcome, calls, children, parent):
        self.assertEqual("failed", outcome["outcome"])
        self.assertEqual("AN-T-42", outcome["errors"][0]["target"])
        self.assertTrue(outcome["effects"])
        self.assertEqual(["AN-T-41", "AN-T-42"], calls)
        self.assertTrue(
            (children[0].parent / "canceled" / children[0].name).is_file()
        )
        self.assertTrue(children[1].is_file())
        self.assertTrue(parent.is_file())

    def test_leaf_status_uses_one_capture(self):
        with patch(
            (
                'FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.updates.native_update__shared.capture_native'
            ),
            wraps=capture_native,
        ) as capture:
            outcome = change_ticket_status(
                self.selection,
                {"target": self.params["target"], "targetStatus": "done"},
                current_rows=self.rows,
                check_definition=lambda: None,
            )
        self.assertEqual("completed", outcome["outcome"])
        self.assertEqual(1, capture.call_count)

    def _valid_epic_companion(self):
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
        nested = self.write(
            (
                "001_TICKETS/TASKS/AN-T-2-EPIC--owner/done/"
                "AN-T-3-TASK--child/canceled/AN-T-4-TASK--nested.md"
            ),
            "AN-T-4",
            {"atom": "AN-T-3"},
        )
        nested.write_bytes(
            nested.read_bytes()
            .replace(b"context:\n", b"context:\n  template: task\n")
            .replace(b"status: active", b"status: canceled")
        )
        draft = self.write(
            (
                "001_TICKETS/TASKS/AN-T-2-EPIC--owner/01_draft/"
                "AN-T-3@2-draft-TASK--child.md"
            ),
            "AN-T-3",
            {"atom": "AN-T-2"},
        )
        draft.write_bytes(
            draft.read_bytes()
            .replace(b"context:\n", b"context:\n  template: task\n")
            .replace(b"status: active", b"status: draft")
            .replace(b"version: 1", b"version: 2")
        )
        return epic, child, nested, draft

    def test_epic_close_moves_valid_companion_and_preserves_descendants(self):
        epic, child, nested, draft = self._valid_epic_companion()
        before = child.read_bytes(), nested.read_bytes(), draft.read_bytes()
        params = {
            "target": {"ref_id": "AN-T-2", "version": 1},
            "targetStatus": "done",
        }
        result = change_ticket_status(
            self.selection,
            params,
            current_rows=capture_native(self.selection).atoms,
            check_definition=lambda: None,
        )
        self.assertEqual("completed", result["outcome"])
        destination = epic.parent / "done" / epic.name
        self.assertTrue(destination.is_file())
        self.assertFalse(epic.exists())
        for path, raw in zip((child, nested, draft), before, strict=False):
            self.assertEqual(
                raw,
                (
                    destination.with_suffix("")
                    / path.relative_to(epic.with_suffix(""))
                ).read_bytes(),
            )
        self.assertFalse(epic.with_suffix("").exists())

    def test_epic_close_collision_and_failed_remove_keep_tree(self):
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
        params = {
            "target": {"ref_id": "AN-T-2", "version": 1},
            "targetStatus": "done",
        }
        destination = epic.parent / "done" / epic.name
        destination.with_suffix("").mkdir(parents=True)
        before = epic.read_bytes(), child.read_bytes()
        result = change_ticket_status(
            self.selection,
            params,
            current_rows=capture_native(self.selection).atoms,
            check_definition=lambda: None,
        )
        self.assertEqual("destination_exists", result["errors"][0]["code"])
        self.assertEqual(before, (epic.read_bytes(), child.read_bytes()))
        destination.with_suffix("").rmdir()
        self._assert_epic_remove_failure(
            epic, child, params, destination, before
        )

    def _assert_epic_remove_failure(
        self, epic, child, params, destination, before
    ):
        remove = effects.remove

        def fail_epic(root, path, digest):
            if path == epic:
                return effects.Result(
                    errors=[{"code": "backend_failure", "message": "failure"}]
                )
            return remove(root, path, digest)

        with patch.object(effects, "remove", side_effect=fail_epic):
            result = change_ticket_status(
                self.selection,
                params,
                current_rows=capture_native(self.selection).atoms,
                check_definition=lambda: None,
            )
        self.assertEqual("failed", result["outcome"])
        self.assertEqual(before, (epic.read_bytes(), child.read_bytes()))
        self.assertFalse(destination.exists())
        self.assertFalse(destination.with_suffix("").exists())
