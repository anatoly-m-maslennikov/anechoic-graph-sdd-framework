"""Native ticket tree transition scenarios."""

import yaml

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.sources.inventory.native_source_rows__pub import (
    capture_native,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.updates.native_update__shared import (
    change_ticket_status,
)


class NativeTreeCases1:
    def test_cancel_task_preserves_nested_terminal_descendants_and_history(
        self,
    ):
        parent, companion, before = self._terminal_task_fixture()
        result = change_ticket_status(
            self.selection,
            {
                "target": {"ref_id": "AN-T-2", "version": 1},
                "targetStatus": "canceled",
            },
            current_rows=capture_native(self.selection).atoms,
            check_definition=lambda: None,
        )
        self.assertEqual("completed", result["outcome"])
        destination = parent.parent / "canceled" / parent.name
        self.assertFalse(parent.exists())
        self.assertFalse(companion.exists())
        self.assertEqual(
            "canceled",
            yaml.safe_load(destination.read_text().split("---", 2)[1])[
                "state"
            ]["status"],
        )
        for relative, raw in before.items():
            self.assertEqual(
                raw, (destination.with_suffix("") / relative).read_bytes()
            )

    def _terminal_task_fixture(self):
        parent = self.write(
            "001_TICKETS/TASKS/AN-T-2-TASK--parent.md", "AN-T-2"
        )
        parent.write_bytes(
            parent.read_bytes().replace(
                b"context:\n", b"context:\n  template: task\n"
            )
        )
        companion = parent.with_suffix("")
        child = self.write(
            "001_TICKETS/TASKS/AN-T-2-TASK--parent/done/AN-T-3-SUBTASK--child.md",
            "AN-T-3",
            {"atom": "AN-T-2"},
        )
        child.write_bytes(
            child.read_bytes()
            .replace(b"context:\n", b"context:\n  template: task\n")
            .replace(b"status: active", b"status: done")
            .replace(b"version: 1", b"version: 2")
        )
        nested = self.write(
            "001_TICKETS/TASKS/AN-T-2-TASK--parent/done/AN-T-3-SUBTASK--child/canceled/AN-T-4-SUBTASK--nested.md",
            "AN-T-4",
            {"atom": "AN-T-3"},
        )
        nested.write_bytes(
            nested.read_bytes()
            .replace(b"context:\n", b"context:\n  template: task\n")
            .replace(b"status: active", b"status: canceled")
            .replace(
                b"state:\n", b"relations:\n  REFERENCES:\n  - AN-T-2\nstate:\n"
            )
        )
        history = self._terminal_task_history()
        before = {
            path.relative_to(companion): path.read_bytes()
            for path in (child, nested, history)
        }
        return parent, companion, before

    def _terminal_task_history(self):
        history = self.write(
            "001_TICKETS/TASKS/AN-T-2-TASK--parent/09_archived/AN-T-3@1-SUBTASK--child.md",
            "AN-T-3",
            {"atom": "AN-T-2"},
        )
        history.write_bytes(
            history.read_bytes()
            .replace(b"context:\n", b"context:\n  template: task\n")
            .replace(b"status: active", b"status: archived")
        )
        return history

    def test_cancel_task_cancels_unfinished_descendant(self):
        parent = self.write(
            "001_TICKETS/TASKS/AN-T-2-TASK--parent.md", "AN-T-2"
        )
        parent.write_bytes(
            parent.read_bytes().replace(
                b"context:\n", b"context:\n  template: task\n"
            )
        )
        child = self.write(
            "001_TICKETS/TASKS/AN-T-2-TASK--parent/AN-T-3-SUBTASK--child.md",
            "AN-T-3",
            {"atom": "AN-T-2"},
        )
        child.write_bytes(
            child.read_bytes().replace(
                b"context:\n", b"context:\n  template: task\n"
            )
        )
        outcome = change_ticket_status(
            self.selection,
            {
                "target": {"ref_id": "AN-T-2", "version": 1},
                "targetStatus": "canceled",
            },
            current_rows=capture_native(self.selection).atoms,
            check_definition=lambda: None,
        )
        self.assertEqual("completed", outcome["outcome"])
        destination = parent.parent / "canceled" / parent.name
        self.assertTrue(
            (destination.with_suffix("") / "canceled" / child.name).is_file()
        )

    def test_epic_terminal_status_cancels_mixed_nested_descendants(self):
        for number, status in ((10, "done"), (20, "canceled")):
            with self.subTest(status=status):
                self._epic_terminal_case(number, status)

    def _epic_terminal_case(self, number, status):
        prefix = f"001_TICKETS/TASKS/AN-T-{number}-EPIC--parent"
        parent = self.write(prefix + ".md", f"AN-T-{number}")
        parent.write_bytes(
            parent.read_bytes().replace(
                b"context:\n", b"context:\n  template: epic\n"
            )
        )
        done, canceled, active, nested = self._epic_initial_children(
            prefix, number
        )
        resolved, report, draft = self._epic_extra_children(prefix, number)
        before = {
            path.relative_to(parent.with_suffix("")): path.read_bytes()
            for path in (done, canceled, draft)
        }
        outcome = change_ticket_status(
            self.selection,
            {
                "target": {"ref_id": f"AN-T-{number}", "version": 1},
                "targetStatus": status,
            },
            current_rows=capture_native(self.selection).atoms,
            check_definition=lambda: None,
        )
        self._assert_epic_terminal(
            outcome, parent, status, before, active, nested, resolved, report
        )

    def _epic_initial_children(self, prefix, number):
        done = self.write(
            prefix + f"/done/AN-T-{number + 1}-TASK--done.md",
            f"AN-T-{number + 1}",
            {"atom": f"AN-T-{number}"},
        )
        canceled = self.write(
            prefix + f"/canceled/AN-T-{number + 2}-TASK--canceled.md",
            f"AN-T-{number + 2}",
            {"atom": f"AN-T-{number}"},
        )
        active = self.write(
            prefix + f"/AN-T-{number + 3}-TASK--active.md",
            f"AN-T-{number + 3}",
            {"atom": f"AN-T-{number}"},
        )
        nested = self.write(
            prefix
            + f"/done/AN-T-{number + 1}-TASK--done/backlog/AN-T-{number + 4}-SUBTASK--nested.md",
            f"AN-T-{number + 4}",
            {"atom": f"AN-T-{number + 1}"},
        )
        for path, initial in (
            (done, "done"),
            (canceled, "canceled"),
            (active, "active"),
            (nested, "backlog"),
        ):
            path.write_bytes(
                path.read_bytes()
                .replace(b"context:\n", b"context:\n  template: task\n")
                .replace(b"status: active", f"status: {initial}".encode())
            )
        return done, canceled, active, nested

    def _epic_extra_children(self, prefix, number):
        resolved = self.write(
            prefix + f"/resolved/AN-T-{number + 6}-QUESTION--resolved.md",
            f"AN-T-{number + 6}",
            {"atom": f"AN-T-{number}"},
        )
        resolved.write_bytes(
            resolved.read_bytes()
            .replace(b"context:\n", b"context:\n  template: question\n")
            .replace(b"status: active", b"status: resolved")
        )
        report = self.write(
            prefix + f"/ASSETS/AN-T-{number + 5}-WORK_REPORT--report.md",
            f"AN-T-{number + 5}",
            {"atom": f"AN-T-{number}"},
        )
        report.write_bytes(
            report.read_bytes().replace(
                b"context:\n", b"context:\n  template: work_report\n"
            )
        )
        draft = self.write(
            prefix + f"/01_draft/AN-T-{number + 3}@2-draft-TASK--active.md",
            f"AN-T-{number + 3}",
            {"atom": f"AN-T-{number}"},
        )
        draft.write_bytes(
            draft.read_bytes()
            .replace(b"context:\n", b"context:\n  template: task\n")
            .replace(b"status: active", b"status: draft")
            .replace(b"version: 1", b"version: 2")
        )
        return resolved, report, draft

    def _assert_epic_terminal(
        self, outcome, parent, status, before, active, nested, resolved, report
    ):
        self.assertEqual("completed", outcome["outcome"], outcome)
        moved = parent.parent / status / parent.name
        for relative, raw in before.items():
            self.assertEqual(
                raw, (moved.with_suffix("") / relative).read_bytes()
            )
        for path in (active, nested):
            relative = path.relative_to(parent.with_suffix(""))
            new_path = (
                moved.with_suffix("")
                / relative.parent.parent
                / "canceled"
                / relative.name
                if path == nested
                else moved.with_suffix("") / "canceled" / relative.name
            )
            self.assertEqual(
                "canceled",
                yaml.safe_load(new_path.read_text().split("---", 2)[1])[
                    "state"
                ]["status"],
            )
        resolved_path = moved.with_suffix("") / "resolved" / resolved.name
        self.assertEqual(
            "resolved",
            yaml.safe_load(resolved_path.read_text().split("---", 2)[1])[
                "state"
            ]["status"],
        )
        report_path = (
            moved.with_suffix("") / "ASSETS" / "canceled" / report.name
        )
        self.assertEqual(
            "canceled",
            yaml.safe_load(report_path.read_text().split("---", 2)[1])[
                "state"
            ]["status"],
        )
        self.assertFalse(parent.exists())
