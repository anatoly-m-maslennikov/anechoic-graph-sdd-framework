"""Ticket replacement promotion scenarios."""

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.sources.inventory.native_source_rows__pub import (
    capture_native,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.ATOM_LIFECYCLE__shared import (
    InputError,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.drafts.promotion.native_draft_promotion_dispatch import (
    promote_draft,
)


class TicketReplacementCases:
    def add_replacement(self, draft):
        import yaml

        _, text, body = draft.read_text().split("---", 2)
        header = yaml.safe_load(text)
        header["relations"] = {"IS_REPLACEMENT_FOR": ["AN-T-1"]}
        draft.write_text(
            "---\n" + yaml.safe_dump(header, sort_keys=False) + "---" + body
        )

    def test_first_ticket_archives_explicit_predecessor(self):
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.drafts.native_draft__shared import (
            create_draft,
        )

        result = create_draft(self.selection, self.new, current_rows=self.rows)
        self.add_replacement(self.root / result["savedDraft"]["path"])
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
        self.assertEqual("completed", result["outcome"], result)
        self.assertFalse(self.path.exists())
        self.assertTrue(
            (
                self.control
                / "001_TICKETS/TASKS/09_archived/AN-T-1@1-TASK--example.md"
            ).exists()
        )

    def _prepare_ticket_replacement(self):
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.drafts.native_draft__shared import (
            create_draft,
        )

        parent = create_draft(
            self.selection, self.new, current_rows=self.rows
        )["savedDraft"]
        child = create_draft(
            self.selection,
            {
                "newAtom": {
                    "template": "task",
                    "container": {"atom": parent["atom_id"]},
                    "body": "\n## Summary\n\nChild\n",
                }
            },
            current_rows=capture_native(self.selection).atoms,
        )["savedDraft"]
        child_path = self.root / child["path"]
        self.add_replacement(child_path)
        params = {
            "target": {"ref_id": parent["ref_id"], "version": 1},
            "targetStatus": "backlog",
        }
        original = self.path.read_text()
        backlog = self.path.parent / "backlog" / self.path.name
        backlog.parent.mkdir()
        backlog.write_text(
            original.replace("status: active", "status: backlog")
        )
        self.path.unlink()
        return params, child_path, original, backlog

    def test_ticket_tree_checks_and_archives_child_replacement_predecessor(
        self,
    ):
        params, child_path, original, backlog = (
            self._prepare_ticket_replacement()
        )
        with self.assertRaisesRegex(InputError, "Current Ready or Active"):
            promote_draft(
                self.selection,
                params,
                current_rows=capture_native(self.selection).atoms,
            )
        self.assertTrue(backlog.exists())
        self.assertTrue(child_path.exists())
        backlog.unlink()
        self.path.write_text(original)
        result = promote_draft(
            self.selection,
            params,
            current_rows=capture_native(self.selection).atoms,
        )
        self.assertEqual("completed", result["outcome"], result)
        self.assertFalse(self.path.exists())
        self.assertFalse(child_path.exists())
        self.assertTrue(
            (
                self.control
                / "001_TICKETS/TASKS/09_archived/AN-T-1@1-TASK--example.md"
            ).exists()
        )
