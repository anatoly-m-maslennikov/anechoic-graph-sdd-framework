"""Native lifecycle draft test scenarios."""

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


class NativeDraftCases2:
    def test_revision_does_not_retry_other_write_errors(self):
        from unittest.mock import patch

        with patch("os.link", side_effect=PermissionError("failed")) as write:
            result = create_draft(
                self.selection, self.params, current_rows=self.rows
            )
        self.assertEqual("failed", result["outcome"])
        self.assertEqual(1, write.call_count)

    def test_canonical_ticket_revision_preserves_archived_body(self):
        _, header, body = self.path.read_text().split("---", 2)
        canonical = canonical_native_header(yaml.safe_load(header))
        self.path.write_text(
            "---\n" + yaml.safe_dump(canonical, sort_keys=False) + "---" + body
        )
        output = create_draft(
            self.selection,
            self.params,
            current_rows=capture_native(self.selection).atoms,
        )
        ref = output["savedDraft"]["ref_id"]
        result = promote_draft(
            self.selection,
            {
                "target": {"ref_id": ref, "version": 2},
                "targetStatus": "backlog",
            },
            current_rows=capture_native(self.selection).atoms,
        )
        self.assertEqual("completed", result["outcome"])
        archive = (
            self.control
            / "001_TICKETS/TASKS/09_archived/AN-T-1@1-TASK--example.md"
        )
        _, archived_header, archived_body = archive.read_text().split("---", 2)
        archived = yaml.safe_load(archived_header)
        self.assertEqual(body, archived_body)
        self.assertEqual({**canonical, "state": archived["state"]}, archived)
        self.assertEqual("archived", archived["state"]["status"])
        self.assertIn(
            "New", (self.path.parent / "backlog" / self.path.name).read_text()
        )

    def test_missing_changes_preserves_body(self):
        output = create_draft(
            self.selection,
            {"sourceCurrent": self.params["sourceCurrent"]},
            current_rows=self.rows,
        )
        target = self.root / output["savedDraft"]["path"]
        self.assertEqual(
            self.path.read_bytes().split(b"---\n", 2)[2],
            target.read_bytes().split(b"---\n", 2)[2],
        )

    def _alter_stale_draft_content(
        self, case, params, row, original, manifest
    ):
        if case == "bytes":
            self.path.write_bytes(original.replace(b"Old", b"Altered"))
        if case == "summary":
            params["changes"]["body"] = params["changes"]["body"].replace(
                "Example", "Changed"
            )
        if case == "extra":
            params["changes"]["status"] = "done"
        if case == "template":
            row["header_json"] = {
                **row["header_json"],
                "context": {"template": "epic"},
            }
        if case == "manifest":
            self.selection.manifest_path.write_bytes(manifest + b"changed")

    def _alter_stale_draft_input(self, case, params, row, original, manifest):
        if case == "version":
            params["sourceCurrent"]["version"] = 2
        if case == "selector":
            params["sourceCurrent"]["extra"] = "x"
        if case == "foreign":
            params["sourceCurrent"]["ref_id"] = "XX-T-1"
        if case == "digest":
            row.pop("_source_sha256")
        if case == "path":
            row["source_path"] = "../escape.md"
        self._alter_stale_draft_content(case, params, row, original, manifest)

    def test_rejects_stale_and_out_of_scope_inputs(self):
        for case in (
            "version",
            "selector",
            "foreign",
            "digest",
            "path",
            "bytes",
            "summary",
            "extra",
            "template",
            "manifest",
        ):
            with self.subTest(case=case):
                rows = [dict(row) for row in self.rows]
                params = {
                    "sourceCurrent": dict(self.params["sourceCurrent"]),
                    "changes": dict(self.params["changes"]),
                }
                row = next(row for row in rows if row["id"] == "AN-T-1")
                original, manifest = (
                    self.path.read_bytes(),
                    self.selection.manifest_path.read_bytes(),
                )
                self._alter_stale_draft_input(
                    case, params, row, original, manifest
                )
                with self.assertRaises((InputError, SourceChanged)):
                    create_draft(self.selection, params, current_rows=rows)
                self.assertFalse(
                    (self.control / "001_TICKETS/TASKS/01_draft").exists()
                )
                self.path.write_bytes(original)
                self.selection.manifest_path.write_bytes(manifest)

    def test_symlink_draft_directory_cannot_escape(self):
        outside = self.root / "outside"
        outside.mkdir()
        (self.control / "001_TICKETS/TASKS/01_draft").symlink_to(
            outside, target_is_directory=True
        )
        output = create_draft(
            self.selection, self.params, current_rows=self.rows
        )
        self.assertEqual("failed", output["outcome"])
        self.assertTrue(output["errors"])
        self.assertEqual([], list(outside.iterdir()))

    def test_wrong_branch_and_template_are_rejected(self):
        for name, template in [
            ("001_TICKETS/ISSUES/AN-T-2-TASK--example.md", "task"),
            ("001_TICKETS/TASKS/AN-T-3-QUESTION--example.md", "question"),
        ]:
            identity = "AN-T-2" if template == "task" else "AN-T-3"
            self.write(name, identity, template=template)
            rows = capture_native(self.selection).atoms
            with self.assertRaises((InputError, SourceChanged)):
                create_draft(
                    self.selection,
                    {"sourceCurrent": {"ref_id": identity, "version": 1}},
                    current_rows=rows,
                )
