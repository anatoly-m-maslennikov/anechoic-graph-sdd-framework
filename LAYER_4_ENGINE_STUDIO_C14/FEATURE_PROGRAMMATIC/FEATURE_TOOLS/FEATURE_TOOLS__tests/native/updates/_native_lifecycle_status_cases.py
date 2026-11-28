"""Native status and archive local-slot scenarios."""

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.sources.inventory.native_source_rows__pub import (
    capture_native,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.ATOM_LIFECYCLE__shared import (
    InputError,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.updates.native_update_archive import (
    archive_ticket,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.updates.native_update__shared import (
    change_ticket_status,
)


class NativeLifecycleStatusCases:
    def test_status_reports_partial_when_source_changes_before_removal(self):
        params = {"target": self.params["target"], "targetStatus": "done"}
        destination = self.path.parent / "done" / self.path.name
        destination.parent.mkdir()
        calls = []

        def check():
            calls.append(True)
            if len(calls) == 2:
                self.path.write_bytes(
                    self.path.read_bytes() + b"Changed concurrently"
                )

        outcome = change_ticket_status(
            self.selection,
            params,
            current_rows=self.rows,
            check_definition=check,
        )
        self.assertEqual("failed", outcome["outcome"])
        self.assertEqual(
            ["create"], [effect["operation"] for effect in outcome["effects"]]
        )
        self.assertEqual("stale_state", outcome["errors"][0]["code"])
        self.assertTrue(destination.exists())
        self.assertIn(b"Changed concurrently", self.path.read_bytes())

    def test_flat_descendants_are_rejected_without_detachment(self):
        self.path.write_bytes(
            self.path.read_bytes().replace(
                b"context:\n", b"context:\n  template: epic\n"
            )
        )
        child = self.write(
            "001_TICKETS/TASKS/done/AN-T-2-TASK--child.md",
            "AN-T-2",
            {"atom": "AN-T-1"},
        )
        child.write_bytes(
            child.read_bytes().replace(b"status: active", b"status: done")
        )
        params = {"target": self.params["target"], "targetStatus": "done"}
        before = self.path.read_bytes(), child.read_bytes()
        with self.assertRaises(InputError):
            change_ticket_status(
                self.selection,
                params,
                current_rows=capture_native(self.selection).atoms,
                check_definition=lambda: None,
            )
        self.assertEqual(before, (self.path.read_bytes(), child.read_bytes()))

    def test_nested_leaf_status_and_archive_use_local_slots(self):
        epic = self.write("001_TICKETS/TASKS/AN-T-2-EPIC--owner.md", "AN-T-2")
        epic.write_bytes(
            epic.read_bytes().replace(
                b"context:\n", b"context:\n  template: epic\n"
            )
        )
        task = self.write(
            "001_TICKETS/TASKS/AN-T-2-EPIC--owner/AN-T-3-TASK--child.md",
            "AN-T-3",
            {"atom": "AN-T-2"},
        )
        task.write_bytes(
            task.read_bytes().replace(
                b"context:\n", b"context:\n  template: task\n"
            )
        )
        report = self.write(
            (
                "001_TICKETS/TASKS/AN-T-2-EPIC--owner/ASSETS/"
                "AN-T-4-WORK_REPORT--report.md"
            ),
            "AN-T-4",
            {"atom": "AN-T-2"},
        )
        report.write_bytes(
            report.read_bytes().replace(
                b"context:\n", b"context:\n  template: work_report\n"
            )
        )
        self._assert_nested_leaf_slots(task, report)

    def _assert_nested_leaf_slots(self, task, report):
        for path, identity in ((task, "AN-T-3"), (report, "AN-T-4")):
            params = {
                "target": {"ref_id": identity, "version": 1},
                "targetStatus": "done",
            }
            result = change_ticket_status(
                self.selection,
                params,
                current_rows=capture_native(self.selection).atoms,
                check_definition=lambda: None,
            )
            self.assertEqual("completed", result["outcome"])
            moved = path.parent / "done" / path.name
            self.assertTrue(moved.is_file())
            result = archive_ticket(
                self.selection,
                {"target": params["target"]},
                current_rows=capture_native(self.selection).atoms,
            )
            self.assertEqual("completed", result["outcome"])
            self.assertTrue(
                (
                    path.parent
                    / "09_archived"
                    / path.name.replace(identity, identity + "@1")
                ).is_file()
            )
            self.assertFalse(moved.exists())
