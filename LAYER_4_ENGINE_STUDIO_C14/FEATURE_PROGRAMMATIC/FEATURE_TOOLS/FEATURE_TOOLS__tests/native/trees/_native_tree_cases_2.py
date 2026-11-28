"""Native ticket tree transition scenarios."""

import yaml

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.sources.inventory.native_source_rows__pub import (
    capture_native,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.updates.native_update__shared import (
    change_ticket_status,
)


class NativeTreeCases2:
    def test_nonterminal_status_moves_companion_without_changing_children(
        self,
    ):
        parent = self.write(
            "001_TICKETS/TASKS/AN-T-30-EPIC--parent.md", "AN-T-30"
        )
        parent.write_bytes(
            parent.read_bytes().replace(
                b"context:\n", b"context:\n  template: epic\n"
            )
        )
        child = self.write(
            "001_TICKETS/TASKS/AN-T-30-EPIC--parent/AN-T-31-TASK--child.md",
            "AN-T-31",
            {"atom": "AN-T-30"},
        )
        child.write_bytes(
            child.read_bytes().replace(
                b"context:\n", b"context:\n  template: task\n"
            )
        )
        before = child.read_bytes()
        outcome = change_ticket_status(
            self.selection,
            {
                "target": {"ref_id": "AN-T-30", "version": 1},
                "targetStatus": "backlog",
            },
            current_rows=capture_native(self.selection).atoms,
            check_definition=lambda: None,
        )
        self.assertEqual("completed", outcome["outcome"], outcome)
        destination = (
            self.control / "001_TICKETS/TASKS/backlog/AN-T-30-EPIC--parent"
        )
        self.assertEqual(before, (destination / child.name).read_bytes())
        self.assertFalse(parent.exists())

    def test_task_reopening_preserves_descendant_status(self):
        prefix = "001_TICKETS/TASKS/done/AN-T-40-TASK--parent"
        parent = self.write(prefix + ".md", "AN-T-40")
        parent.write_bytes(
            parent.read_bytes()
            .replace(b"context:\n", b"context:\n  template: task\n")
            .replace(b"status: active", b"status: done")
        )
        child = self.write(
            f"{prefix}/done/AN-T-41-SUBTASK--child.md",
            "AN-T-41",
            {"atom": "AN-T-40"},
        )
        child.write_bytes(
            child.read_bytes()
            .replace(b"context:\n", b"context:\n  template: task\n")
            .replace(b"status: active", b"status: done")
        )
        before = child.read_bytes()
        reopened = change_ticket_status(
            self.selection,
            {
                "target": {"ref_id": "AN-T-40", "version": 1},
                "targetStatus": "in_queue",
            },
            current_rows=capture_native(self.selection).atoms,
            check_definition=lambda: None,
        )
        self.assertEqual("completed", reopened["outcome"], reopened)
        current = (
            self.control
            / "001_TICKETS/TASKS/AN-T-40-TASK--parent"
            / "done"
            / child.name
        )
        self.assertEqual(before, current.read_bytes())

    def test_backlog_activation_promotes_nested_tasks_and_preserves_assets(
        self,
    ):
        parent, grand = self._backlog_activation_fixture()
        outcome = change_ticket_status(
            self.selection,
            {
                "target": {"ref_id": "AN-T-30", "version": 1},
                "targetStatus": "in_queue",
            },
            current_rows=capture_native(self.selection).atoms,
            check_definition=lambda: None,
        )
        self.assertEqual("completed", outcome["outcome"], outcome)
        dest = (
            self.control
            / "001_TICKETS/TASKS/AN-T-30-EPIC--parent/AN-T-31-TASK--child"
        )
        self.assertEqual(
            "in_queue",
            yaml.safe_load((dest / grand.name).read_text().split("---", 2)[1])[
                "state"
            ]["status"],
        )
        self.assertEqual("keep", (dest / "notes.txt").read_text())
        self.assertEqual(
            "in_queue",
            yaml.safe_load(
                dest.with_suffix(".md").read_text().split("---", 2)[1]
            )["state"]["status"],
        )

    def _backlog_activation_fixture(self):
        parent = self.write(
            "001_TICKETS/TASKS/backlog/AN-T-30-EPIC--parent.md", "AN-T-30"
        )
        parent.write_bytes(
            parent.read_bytes()
            .replace(b"context:\n", b"context:\n  template: epic\n")
            .replace(b"status: active", b"status: backlog")
        )
        branch = "001_TICKETS/TASKS/backlog/AN-T-30-EPIC--parent"
        child = self.write(
            f"{branch}/backlog/AN-T-31-TASK--child.md",
            "AN-T-31",
            {"atom": "AN-T-30"},
        )
        child.write_bytes(
            child.read_bytes()
            .replace(b"context:\n", b"context:\n  template: task\n")
            .replace(b"status: active", b"status: backlog")
        )
        grand = self.write(
            (
                f"{branch}"
                "/backlog/AN-T-31-TASK--child/backlog/AN-T-32-SUBTASK--grand."
                "md"
            ),
            "AN-T-32",
            {"atom": "AN-T-31"},
        )
        grand.write_bytes(
            grand.read_bytes()
            .replace(b"context:\n", b"context:\n  template: task\n")
            .replace(b"status: active", b"status: backlog")
        )
        asset = grand.parent.parent / "notes.txt"
        asset.write_text("keep")
        return parent, grand
