"""Native ticket tree transition scenarios."""

import yaml

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


class NativeTreeCases3:
    def test_backlog_activation_publishes_first_draft_descendant(self):
        parent = self.write(
            "001_TICKETS/TASKS/backlog/AN-T-30-EPIC--parent.md", "AN-T-30"
        )
        parent.write_bytes(
            parent.read_bytes()
            .replace(b"context:\n", b"context:\n  template: epic\n")
            .replace(b"status: active", b"status: backlog")
        )
        child = self.write(
            (
                "001_TICKETS/TASKS/backlog/AN-T-30-EPIC--parent/01_draft/"
                "AN-T-31@1-draft-TASK--child.md"
            ),
            "AN-T-31",
            {"atom": "AN-T-30"},
        )
        child.write_bytes(
            child.read_bytes()
            .replace(b"context:\n", b"context:\n  template: task\n")
            .replace(b"status: active", b"status: draft")
        )
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
        destination = (
            self.control
            / "001_TICKETS/TASKS/AN-T-30-EPIC--parent/AN-T-31-TASK--child.md"
        )
        self.assertEqual(
            "in_queue",
            yaml.safe_load(destination.read_text().split("---", 2)[1])[
                "state"
            ]["status"],
        )
        self.assertFalse(child.exists())

    def test_activation_preflights_all_child_destinations(self):
        parent = self.write(
            "001_TICKETS/TASKS/backlog/AN-T-30-EPIC--parent.md", "AN-T-30"
        )
        parent.write_bytes(
            parent.read_bytes()
            .replace(b"context:\n", b"context:\n  template: epic\n")
            .replace(b"status: active", b"status: backlog")
        )
        branch = "001_TICKETS/TASKS/backlog/AN-T-30-EPIC--parent"
        children = []
        for number in (31, 32):
            child = self.write(
                f"{branch}/backlog/AN-T-{number}-TASK--child.md",
                f"AN-T-{number}",
                {"atom": "AN-T-30"},
            )
            child.write_bytes(
                child.read_bytes()
                .replace(b"context:\n", b"context:\n  template: task\n")
                .replace(b"status: active", b"status: backlog")
            )
            children.append(child)
        collision = (children[1].parent.parent / children[1].name).with_suffix(
            ""
        )
        collision.mkdir()
        before = [path.read_bytes() for path in [parent, *children]]
        outcome = change_ticket_status(
            self.selection,
            {
                "target": {"ref_id": "AN-T-30", "version": 1},
                "targetStatus": "in_queue",
            },
            current_rows=capture_native(self.selection).atoms,
            check_definition=lambda: None,
        )
        self.assertEqual("failed", outcome["outcome"])
        self.assertEqual("destination_exists", outcome["errors"][0]["code"])
        self.assertEqual(
            before, [path.read_bytes() for path in [parent, *children]]
        )
        self.assertTrue(collision.is_dir())

    def test_reopening_epic_preserves_nested_tree_bytes(self):
        for number, status in ((50, "done"), (60, "canceled")):
            with self.subTest(status=status):
                epic_id = f"AN-T-{number}"
                epic = f"{epic_id}-EPIC--parent"
                prefix = f"001_TICKETS/TASKS/{status}/{epic}"
                parent = self.write(prefix + ".md", epic_id)
                parent.write_bytes(
                    parent.read_bytes()
                    .replace(b"context:\n", b"context:\n  template: epic\n")
                    .replace(b"status: active", f"status: {status}".encode())
                )
                before = self._reopening_epic_children(prefix, epic_id, number)
                outcome = change_ticket_status(
                    self.selection,
                    {
                        "target": {"ref_id": epic_id, "version": 1},
                        "targetStatus": "in_queue",
                    },
                    current_rows=capture_native(self.selection).atoms,
                    check_definition=lambda: None,
                )
                self.assertEqual("completed", outcome["outcome"], outcome)
                self.assertEqual("in_queue", outcome["artifact"]["status"])
                destination = self.control / "001_TICKETS/TASKS" / epic
                for relative, raw in before.items():
                    self.assertEqual(
                        raw, (destination / relative).read_bytes()
                    )
                self.assertFalse(parent.exists())
                self.assertFalse(parent.with_suffix("").exists())

    def _reopening_epic_children(self, prefix, epic_id, number):
        done_id, nested_id, canceled_id = (
            f"AN-T-{number + offset}" for offset in (1, 2, 3)
        )
        done = f"done/{done_id}-TASK--done"
        before = {}
        for relative, atom_id, owner, child_status in (
            (done + ".md", done_id, epic_id, "done"),
            (
                f"{done}/{nested_id}-SUBTASK--active.md",
                nested_id,
                done_id,
                "active",
            ),
            (
                f"canceled/{canceled_id}-TASK--canceled.md",
                canceled_id,
                epic_id,
                "canceled",
            ),
        ):
            path = self.write(f"{prefix}/{relative}", atom_id, {"atom": owner})
            raw = path.read_bytes().replace(
                b"context:\n", b"context:\n  template: task\n"
            )
            before[relative] = raw.replace(
                b"status: active", f"status: {child_status}".encode()
            )
            path.write_bytes(before[relative])
        return before

    def test_archive_container_refuses_without_detachment(self):
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
        before = parent.read_bytes(), child.read_bytes()
        with self.assertRaises(InputError):
            archive_ticket(
                self.selection,
                {"target": {"ref_id": "AN-T-30", "version": 1}},
                current_rows=capture_native(self.selection).atoms,
            )
        self.assertEqual(before, (parent.read_bytes(), child.read_bytes()))
