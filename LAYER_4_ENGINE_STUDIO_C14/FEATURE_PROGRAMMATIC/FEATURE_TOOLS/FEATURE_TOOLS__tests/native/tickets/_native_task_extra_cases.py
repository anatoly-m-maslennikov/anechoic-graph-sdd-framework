"""Native task draft scenarios."""

import yaml

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.sources.inventory.native_source_rows__pub import (
    capture_native,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.header.native_carrier_header__pub import (
    canonical_native_header,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.ATOM_LIFECYCLE__shared import (
    InputError,
    SourceChanged,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.drafts.native_draft__shared import (
    create_draft,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.drafts.promotion.native_draft_promotion_dispatch import (
    promote_draft,
)


class NativeTaskExtraCases:
    def test_canonical_flat_owned_task_keeps_validated_flat_revision_paths(
        self,
    ):
        flat = self._flat_ticket_fixture()
        result = create_draft(
            self.selection,
            {"sourceCurrent": {"ref_id": "AN-T-2", "version": 1}},
            current_rows=capture_native(self.selection).atoms,
        )
        draft = self.root / result["savedDraft"]["path"]
        self.assertEqual(flat.parent / "01_draft", draft.parent)
        result = promote_draft(
            self.selection,
            {
                "target": {
                    "ref_id": result["savedDraft"]["ref_id"],
                    "version": 2,
                },
                "targetStatus": "backlog",
            },
            current_rows=capture_native(self.selection).atoms,
        )
        self.assertEqual(
            flat.parent / "backlog" / flat.name,
            self.root / result["artifact"]["path"],
        )
        self.assertTrue(
            (
                flat.parent
                / "09_archived"
                / flat.name.replace("AN-T-2-", "AN-T-2@1-")
            ).exists()
        )

    def _flat_ticket_fixture(self):
        flat = self.write(
            "001_TICKETS/TASKS/AN-T-2-SUBTASK--example.md", "AN-T-2"
        )
        _, header, body = flat.read_text().split("---", 2)
        metadata = yaml.safe_load(header)
        metadata["context"]["container"] = {"atom": "AN-T-1"}
        metadata["context"]["label"] = "Subtask"
        flat.write_text(
            "---\n"
            + yaml.safe_dump(
                canonical_native_header(metadata), sort_keys=False
            )
            + "---"
            + body
        )
        return flat

    def test_nested_tasks_create_and_promote_revisions(self):
        owner = self.path
        for depth in range(2):
            self.new["newAtom"]["container"] = {"atom": f"AN-T-{depth + 1}"}
            self.new["newAtom"]["body"] = f"\n## Summary\n\nChild {depth}\n"
            result = create_draft(
                self.selection,
                self.new,
                current_rows=capture_native(self.selection).atoms,
            )
            draft = self.root / result["savedDraft"]["path"]
            self.assertEqual(owner.with_suffix("") / "01_draft", draft.parent)
            ref = result["savedDraft"]["ref_id"]
            result = promote_draft(
                self.selection,
                {
                    "target": {"ref_id": ref, "version": 1},
                    "targetStatus": "backlog",
                },
                current_rows=capture_native(self.selection).atoms,
            )
            owner = self.root / result["artifact"]["path"]
            self.assertEqual(draft.parent.parent / "backlog", owner.parent)
        self._assert_nested_revision(owner)

    def _assert_nested_revision(self, owner):
        result = create_draft(
            self.selection,
            {"sourceCurrent": {"ref_id": "AN-T-3", "version": 1}},
            current_rows=capture_native(self.selection).atoms,
        )
        draft = self.root / result["savedDraft"]["path"]
        self.assertEqual(owner.parent.parent / "01_draft", draft.parent)
        result = promote_draft(
            self.selection,
            {
                "target": {
                    "ref_id": result["savedDraft"]["ref_id"],
                    "version": 2,
                },
                "targetStatus": "backlog",
            },
            current_rows=capture_native(self.selection).atoms,
        )
        self.assertEqual("completed", result["outcome"])
        self.assertTrue(
            (
                owner.parent.parent
                / "09_archived"
                / owner.name.replace("AN-T-3-", "AN-T-3@1-")
            ).exists()
        )

    def test_unicode_punctuation_uses_reviewed_slug(self):
        self.new["newAtom"]["body"] = self.new["newAtom"]["body"].replace(
            "Create a Task!", "Create — a Task!"
        )
        output = create_draft(self.selection, self.new, current_rows=self.rows)
        self.assertTrue(
            output["savedDraft"]["path"].endswith("-TASK--create-a-task.md")
        )

    def test_task_owner_and_stale_or_foreign_owner(self):
        self.new["newAtom"]["container"] = {"atom": "AN-T-1"}
        output = create_draft(self.selection, self.new, current_rows=self.rows)
        self.assertEqual("completed", output["outcome"])
        self.assertTrue(
            output["savedDraft"]["path"].endswith("-SUBTASK--create-a-task.md")
        )
        metadata = yaml.safe_load(
            (self.root / output["savedDraft"]["path"])
            .read_text()
            .split("---", 2)[1]
        )
        self.assertEqual(
            {"template": "task", "label": "Subtask"}, metadata["context"]
        )
        ref = output["savedDraft"]["ref_id"]
        promoted = promote_draft(
            self.selection,
            {
                "target": {"ref_id": ref, "version": 1},
                "targetStatus": "backlog",
            },
            current_rows=capture_native(self.selection).atoms,
        )
        self.assertTrue(
            promoted["artifact"]["path"].endswith("-SUBTASK--create-a-task.md")
        )
        self.new["newAtom"]["container"] = {"atom": "XX-T-1"}
        with self.assertRaises(InputError):
            create_draft(self.selection, self.new, current_rows=self.rows)
        self.new["newAtom"]["container"] = {"atom": "AN-T-1"}
        self.path.write_bytes(
            self.path.read_bytes().replace(b"Old", b"Altered")
        )
        with self.assertRaises(SourceChanged):
            create_draft(self.selection, self.new, current_rows=self.rows)
