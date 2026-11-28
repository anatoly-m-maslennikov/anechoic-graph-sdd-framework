"""Lifecycle assertions for shared Project queries."""


class SharedQueryLifecycle:
    async def check_console_lifecycle(self, http, first, second):
        ref = {"ref_id": "EX-T-1"}
        current = await self.console(
            http, first, "iwe_console_atom_document", ref
        )
        self.assertEqual(
            ("EX-T-1@1", 1), (current["exact_ref"], current["version"])
        )
        self.assertIn("Example task", current["body"])
        self.assertIn("in_queue", current["ticket_statuses"])
        created = await self.console(
            http,
            first,
            "atom_lifecycle_create_draft",
            {
                "sourceCurrent": ref | {"version": current["version"]},
            },
        )
        self.assertEqual("completed", created["status"], created)
        draft_ref = created["savedDraft"]["ref_id"]
        draft = await self.console(
            http, first, "iwe_console_atom_document", {"ref_id": draft_ref}
        )
        self.assertEqual(
            (draft_ref, "draft"), (draft["exact_ref"], draft["status"])
        )
        self.assertIn(
            draft_ref, {revision["ref_id"] for revision in draft["history"]}
        )
        await self.check_console_promotion(
            http, first, second, ref, current, draft, draft_ref
        )

    async def check_console_promotion(
        self, http, first, second, ref, current, draft, draft_ref
    ):
        updated = await self.console(
            http,
            first,
            "atom_lifecycle_update",
            {
                "target": {"ref_id": draft_ref, "version": draft["version"]},
                "expectedUpdatedAt": draft["updated_at"],
                "changes": {
                    "body": draft["body"]
                    + "\n## Work\n\nEdited through IWE Console.\n"
                },
            },
        )
        self.assertEqual("completed", updated["status"], updated)
        published = await self.console(
            http,
            first,
            "atom_lifecycle_promote_draft",
            {
                "target": {"ref_id": draft_ref, "version": draft["version"]},
                "targetStatus": "backlog",
            },
        )
        self.assertEqual("completed", published["status"], published)
        after = await self.console(
            http, first, "iwe_console_atom_document", ref
        )
        self.assertEqual("EX-T-1@2", after["exact_ref"])
        self.assertIn("Edited through IWE Console.", after["body"])
        self.assertIn("in_queue", after["ticket_statuses"])
        archived = await self.console(
            http, first, "iwe_console_atom_document", {"ref_id": "EX-T-1@1"}
        )
        self.assertEqual(
            ("EX-T-1@1", "archived"),
            (
                archived["exact_ref"],
                archived["status"],
            ),
        )
        self.assertEqual(current["body"], archived["body"])
        await self.check_console_history(http, first, second, ref, current)

    async def check_console_history(self, http, first, second, ref, current):
        missing = await self.tool_rest(
            http,
            first,
            "iwe_console_atom_document",
            {"ref_id": "EX-T-1@999"},
            self.instances[first],
        )
        self.assertEqual("atom_not_found", missing["error"]["code"])
        other = await self.console(
            http, second, "iwe_console_atom_document", ref
        )
        self.assertEqual("EX-T-1@1", other["exact_ref"])
        self.assertIn("Changed second task", other["body"])
