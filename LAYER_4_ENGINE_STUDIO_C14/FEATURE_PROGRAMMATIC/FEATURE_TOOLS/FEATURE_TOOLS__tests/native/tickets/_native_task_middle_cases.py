"""Native task draft scenarios."""

from unittest.mock import NonCallableMock, patch
import yaml

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.sources.inventory.native_source_rows__pub import (
    capture_native,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.ATOM_LIFECYCLE__shared import (
    InputError,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.drafts.native_draft__shared import (
    create_draft,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.drafts.promotion.native_draft_promotion_dispatch import (
    promote_draft,
)


class NativeTaskMiddleCases:
    def test_draft_tree_destination_collision_has_no_effect(self):
        created = create_draft(
            self.selection, self.new, current_rows=self.rows
        )
        ref = created["savedDraft"]["ref_id"]
        draft = self.root / created["savedDraft"]["path"]
        child = (
            draft.with_suffix("") / "01_draft/AN-T-10@1-draft-TASK--child.md"
        )
        child.parent.mkdir(parents=True)
        header = {
            "identity": {"atom_id": "AN-T-10"},
            "context": {
                "container": {"atom": ref.split("@")[0]},
                "template": "task",
            },
            "state": {
                "status": "draft",
                "version": 1,
                "updated_at": "2026-01-01",
            },
        }
        child.write_text(
            "---\n" + yaml.safe_dump(header) + "---\n\n## Summary\n\nChild\n"
        )
        collision = child.parent.parent / "backlog/AN-T-10-TASK--child"
        collision.mkdir(parents=True)
        before = draft.read_bytes(), child.read_bytes()
        outcome = promote_draft(
            self.selection,
            {
                "target": {"ref_id": ref, "version": 1},
                "targetStatus": "backlog",
            },
            current_rows=capture_native(self.selection).atoms,
        )
        self.assertEqual("destination_exists", outcome["errors"][0]["code"])
        self.assertEqual(before, (draft.read_bytes(), child.read_bytes()))
        self.assertTrue(collision.is_dir())

    def test_incomplete_child_companion_blocks_parent_retry(self):
        parent = create_draft(
            self.selection, self.new, current_rows=self.rows
        )["savedDraft"]
        child = create_draft(
            self.selection,
            {
                "newAtom": {
                    "template": "task",
                    "container": {"atom": parent["atom_id"]},
                    "body": "## Summary\n\nChild\n",
                }
            },
            current_rows=capture_native(self.selection).atoms,
        )["savedDraft"]
        companion = (self.root / child["path"]).with_suffix("")
        companion.mkdir()
        note = companion / "notes.txt"
        note.write_text("keep")
        params = {
            "target": {"ref_id": parent["ref_id"], "version": 1},
            "targetStatus": "backlog",
        }

        def partial_move(root, source, destination):
            destination.mkdir()
            return NonCallableMock(
                spec_set=["effects", "errors"],
                effects=[{"operation": "create", "target": str(destination)}],
                errors=[
                    {"code": "backend_failure", "message": "copy interrupted"}
                ],
            )

        with patch(
            (
                'FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.updates.native_update__shared.move_directory'
            ),
            side_effect=partial_move,
        ):
            outcome = promote_draft(
                self.selection,
                params,
                current_rows=capture_native(self.selection).atoms,
            )
        self._assert_incomplete_child(outcome, params, note, parent)

    def _assert_incomplete_child(self, outcome, params, note, parent):
        self.assertEqual("backend_failure", outcome["errors"][0]["code"])
        with self.assertRaisesRegex(
            InputError, "interrupted child publication"
        ):
            promote_draft(
                self.selection,
                params,
                current_rows=capture_native(self.selection).atoms,
            )
        self.assertEqual("keep", note.read_text())
        self.assertTrue((self.root / parent["path"]).is_file())

    def test_new_epic_and_sub_epic_create_and_promote(self):
        self.new["newAtom"]["template"] = "epic"
        for container, label in (
            ({"component": "C00"}, "EPIC"),
            ({"atom": "AN-T-2"}, "SUB_EPIC"),
        ):
            self.new["newAtom"]["container"] = container
            result = create_draft(
                self.selection,
                self.new,
                current_rows=capture_native(self.selection).atoms,
            )
            draft = self.root / result["savedDraft"]["path"]
            self.assertIn(f"-{label}--", draft.name)
            result = promote_draft(
                self.selection,
                {
                    "target": {
                        "ref_id": result["savedDraft"]["ref_id"],
                        "version": 1,
                    },
                    "targetStatus": "backlog",
                },
                current_rows=capture_native(self.selection).atoms,
            )
            self.assertEqual("completed", result["outcome"])
            self.assertIn(f"-{label}--", result["artifact"]["path"])
            self.assertFalse(draft.exists())
        self.assertFalse(capture_native(self.selection).errors)

    def test_epic_uses_admitted_project_component(self):
        self.new["newAtom"].update(
            template="epic", container={"component": "C21"}
        )
        snapshot = NonCallableMock(
            spec_set=["components"], components={"C21": object()}
        )
        result = create_draft(
            self.selection,
            self.new,
            current_rows=self.rows,
            structure_snapshot=snapshot,
        )
        draft = self.root / result["savedDraft"]["path"]
        header = yaml.safe_load(draft.read_text().split("---", 2)[1])
        self.assertEqual({"component": "C21"}, header["container"])
        result = promote_draft(
            self.selection,
            {
                "target": {
                    "ref_id": result["savedDraft"]["ref_id"],
                    "version": 1,
                },
                "targetStatus": "backlog",
            },
            current_rows=capture_native(self.selection).atoms,
            structure_snapshot=snapshot,
        )
        self.assertEqual("completed", result["outcome"])

    def test_create_rejects_label_outside_model_vocabulary(self):
        self.new["newAtom"]["label"] = "Milestone"
        with self.assertRaisesRegex(InputError, "declared navigation Label"):
            create_draft(
                self.selection,
                self.new,
                current_rows=self.rows,
                ticket_labels=("Task",),
            )
