"""Native lifecycle draft test scenarios."""

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.sources.inventory.native_source_rows__pub import (
    capture_native,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.\
    ATOM_LIFECYCLE.NATIVE_LIFECYCLE.\
    NATIVE_LIFECYCLE__shared import (
    execute_native_lifecycle,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.drafts.native_draft__shared import (
    create_draft,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.drafts.promotion.native_draft_promotion_dispatch import (
    promote_draft,
)


class NativeDraftCases1:
    def test_creates_next_version_without_changing_current_or_manifest(self):
        self.write(
            "001_TICKETS/TASKS/09_archived/AN-T-1@4-TASK--example.md",
            "AN-T-1",
            version=4,
            status="archived",
        )
        self.write(
            "001_TICKETS/TASKS/01_draft/AN-T-1@5-draft-TASK--example.md",
            "AN-T-1",
            version=5,
            status="draft",
        )
        current, manifest = (
            self.path.read_bytes(),
            self.selection.manifest_path.read_bytes(),
        )
        output = create_draft(
            self.selection, self.params, current_rows=self.rows
        )
        self.assertEqual("completed", output["outcome"])
        self.assertEqual("AN-T-1@6-draft", output["savedDraft"]["ref_id"])
        target = self.root / output["savedDraft"]["path"]
        self.assertEqual(
            self.control
            / "001_TICKETS/TASKS/01_draft/AN-T-1@6-draft-TASK--example.md",
            target,
        )
        self.assertEqual("create", output["effects"][-1]["operation"])
        self.assertEqual(current, self.path.read_bytes())
        self.assertEqual(manifest, self.selection.manifest_path.read_bytes())
        self._assert_created_draft_capture()

    def _assert_created_draft_capture(self):
        after = capture_native(self.selection)
        self.assertFalse(after.errors)
        row = next(
            row for row in after.atoms if row["_exact_ref"] == "AN-T-1@6-draft"
        )
        self.assertEqual("draft", row["status"])
        source_header = next(
            row for row in self.rows if row["id"] == "AN-T-1"
        )["header_json"]
        self.assertEqual(
            source_header["identity"], row["header_json"]["identity"]
        )
        self.assertEqual(
            source_header["context"], row["header_json"]["context"]
        )
        self.assertEqual(6, row["header_json"]["state"]["version"])
        self.assertEqual(
            self.params["changes"]["body"].encode(), row["_content_bytes"]
        )

    def test_update_exact_draft_body_and_authored_relation(self):
        text = self.path.read_text().replace(
            "state:\n", "relations:\n  RELATES_TO:\n  - AN-T-9\nstate:\n"
        )
        self.path.write_text(text)
        capture = capture_native(self.selection)
        created = create_draft(
            self.selection, self.params, current_rows=capture.atoms
        )
        self.assertEqual("completed", created["outcome"], created)
        draft = created["savedDraft"]
        capture = capture_native(self.selection)
        row = next(
            r for r in capture.atoms if r["_exact_ref"] == draft["ref_id"]
        )
        updated_at = row["header_json"]["state"]["updated_at"]
        args = {
            "target": {"ref_id": draft["ref_id"], "version": draft["version"]},
            "changes": {
                "body": self.params["changes"]["body"].replace("New", "Saved"),
                "removeRelations": [
                    {"type": "RELATES_TO", "ref_id": "AN-T-9"}
                ],
            },
            "expectedUpdatedAt": updated_at,
        }
        result = execute_native_lifecycle(
            self.selection,
            "atom_lifecycle_update",
            args,
            capture,
            None,
            previous_capture=None,
            ticket_labels=(),
            validate_project_spec=None,
        )
        self.assertEqual("completed", result["outcome"], result)
        self.assertEqual(draft["ref_id"], result["artifact"]["ref_id"])
        self.assertNotEqual(updated_at, result["artifact"]["updated_at"])
        self._assert_updated_draft(args, draft)

    def _assert_updated_draft(self, args, draft):
        after = capture_native(self.selection)
        row = next(
            r for r in after.atoms if r["_exact_ref"] == draft["ref_id"]
        )
        self.assertEqual(
            b"\n# Summary\n\nExample\n\n## Details\n\nSaved\n",
            row["_content_bytes"],
        )
        self.assertFalse(row["header_json"].get("relations"))
        self._assert_stale_and_promoted(args, after)

    def _assert_stale_and_promoted(self, args, after):
        stale = execute_native_lifecycle(
            self.selection,
            "atom_lifecycle_update",
            args,
            after,
            None,
            previous_capture=None,
            ticket_labels=(),
            validate_project_spec=None,
        )
        self.assertEqual("source_changed", stale["errors"][0]["code"])
        self.assertFalse(stale["effects"])
        promoted = promote_draft(
            self.selection,
            {"target": args["target"], "targetStatus": "backlog"},
            current_rows=after.atoms,
        )
        self.assertEqual("completed", promoted["outcome"], promoted)
        self.assertNotIn(
            "AN-T-9",
            (self.path.parent / "backlog" / self.path.name).read_text(),
        )

    def test_exact_draft_no_op_preserves_carrier_and_artifact(self):
        created = create_draft(
            self.selection, self.params, current_rows=self.rows
        )["savedDraft"]
        path = self.root / created["path"]
        before, stat = path.read_bytes(), path.stat()
        capture = capture_native(self.selection)
        body = self.params["changes"]["body"]
        variants = (
            {"body": body},
            {"removeRelations": []},
            {"body": body, "removeRelations": []},
        )
        for changes in variants:
            with self.subTest(changes=changes):
                args = {
                    "target": {
                        "ref_id": created["ref_id"],
                        "version": created["version"],
                    },
                    "changes": changes,
                    "expectedUpdatedAt": created["updated_at"],
                }
                output = execute_native_lifecycle(
                    self.selection,
                    "atom_lifecycle_update",
                    args,
                    capture,
                    None,
                    previous_capture=None,
                    ticket_labels=(),
                    validate_project_spec=None,
                )
                self.assertEqual("completed", output["outcome"], output)
                self.assertEqual(created, output["artifact"])
                self.assertEqual([], output["effects"])
                self.assertEqual(before, path.read_bytes())
                self.assertEqual(stat.st_ino, path.stat().st_ino)
                self.assertEqual(stat.st_mtime_ns, path.stat().st_mtime_ns)
