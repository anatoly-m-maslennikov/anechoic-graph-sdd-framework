"""Exercise exact Ticket revisions and archive placement."""

import yaml

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.header.native_carrier_header__pub import (
    canonical_native_header,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.sources.inventory.native_source_rows__pub import (
    capture_native,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.updates.native_update_archive import (
    archive_ticket,
    direct_update,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.ATOM_LIFECYCLE__shared import (
    InputError,
    SourceChanged,
)


class _TicketRevisionCases:
    def test_canonical_ticket_archive_requires_current_replacement(self):
        target_path = self.write(
            "001_TICKETS/TASKS/AN-T-2-TASK--example.md", "AN-T-2"
        )
        _, header, body = target_path.read_text().split("---", 2)
        metadata = yaml.safe_load(header)
        metadata["context"]["template"] = "task"
        target_path.write_text(
            "---\n"
            + yaml.safe_dump(canonical_native_header(metadata))
            + "---"
            + body
        )
        target = {"ref_id": "AN-T-2", "version": 1}
        with self.assertRaises(InputError):
            archive_ticket(
                self.selection,
                {"target": target},
                current_rows=capture_native(self.selection).atoms,
            )
        replacement = self.write(
            "001_TICKETS/TASKS/AN-T-3-TASK--example.md", "AN-T-3"
        )
        _, header, body = replacement.read_text().split("---", 2)
        metadata = yaml.safe_load(header)
        metadata["context"]["template"] = "task"
        metadata["relations"] = {"IS_REPLACEMENT_FOR": ["AN-T-2"]}
        replacement.write_text(
            "---\n"
            + yaml.safe_dump(canonical_native_header(metadata))
            + "---"
            + body
        )
        outcome = archive_ticket(
            self.selection,
            {"target": target},
            current_rows=capture_native(self.selection).atoms,
        )
        self.assertEqual("completed", outcome["outcome"], outcome)
        self.assertEqual("AN-T-2@1", outcome["artifact"]["ref_id"])
        self.assertEqual(
            "09_archived",
            (self.root / outcome["artifact"]["path"]).parent.name,
        )
        self.assertFalse(target_path.exists())

    def test_canonical_ticket_draft_archive_uses_base_replacement_reference(
        self,
    ):
        path = self.write(
            "001_TICKETS/TASKS/01_draft/AN-T-4@2-draft-TASK--example.md",
            "AN-T-4",
        )
        _, header, body = path.read_text().split("---", 2)
        metadata = yaml.safe_load(header)
        metadata["context"]["template"] = "task"
        metadata["state"].update(status="draft", version=2)
        path.write_text(
            "---\n"
            + yaml.safe_dump(canonical_native_header(metadata))
            + "---"
            + body
        )
        replacement = self.write(
            "001_TICKETS/TASKS/AN-T-5-TASK--example.md", "AN-T-5"
        )
        _, header, body = replacement.read_text().split("---", 2)
        metadata = yaml.safe_load(header)
        metadata["context"]["template"] = "task"
        metadata["relations"] = {"IS_REPLACEMENT_FOR": ["AN-T-4"]}
        replacement.write_text(
            "---\n"
            + yaml.safe_dump(canonical_native_header(metadata))
            + "---"
            + body
        )
        target = {"ref_id": "AN-T-4@2-draft", "version": 2}
        outcome = archive_ticket(
            self.selection,
            {"target": target},
            current_rows=capture_native(self.selection).atoms,
        )
        self.assertEqual("completed", outcome["outcome"], outcome)
        self.assertEqual("AN-T-4@2", outcome["artifact"]["ref_id"])
        self.assertFalse(path.exists())

    def test_draft_asset_update_uses_exact_reference(self):
        path = self.write(
            "001_TICKETS/ASSETS/01_draft/AN-T-1@2-draft-ASSET--draft.md",
            "AN-T-1",
        )
        path.write_bytes(
            path.read_bytes()
            .replace(b"status: active", b"status: draft")
            .replace(b"version: 1", b"version: 2")
        )
        rows = capture_native(self.selection).atoms
        before = path.read_bytes()
        params = {
            "target": {"ref_id": "AN-T-1@2-draft", "version": 2},
            "changes": self.params["changes"],
        }
        outcome = direct_update(self.selection, params, current_rows=rows)
        self.assertEqual("completed", outcome["outcome"])
        self.assertEqual(
            ("AN-T-1", "AN-T-1@2-draft", 2, "draft"),
            tuple(
                outcome["artifact"][key]
                for key in ("atom_id", "ref_id", "version", "status")
            ),
        )
        self.assertEqual(
            before.split(b"---\n", 2)[1],
            path.read_bytes().split(b"---\n", 2)[1],
        )
        self.assertIn(b"New", path.read_bytes())
        self.assertTrue(self.path.exists())
        params["target"]["version"] = 1
        with self.assertRaises(InputError):
            direct_update(self.selection, params, current_rows=rows)

    def test_archive_preserves_draft_and_version(self):
        draft = self.write(
            "001_TICKETS/ASSETS/01_draft/AN-T-1@2-draft-ASSET--draft.md",
            "AN-T-1",
        )
        draft.write_bytes(
            draft.read_bytes()
            .replace(b"status: active", b"status: draft")
            .replace(b"version: 1", b"version: 2")
        )
        rows = capture_native(self.selection).atoms
        body = self.path.read_bytes().split(b"---\n", 2)[2]
        original_draft = draft.read_bytes()
        outcome = archive_ticket(
            self.selection,
            {"target": self.params["target"]},
            current_rows=rows,
        )
        self.assertEqual("completed", outcome["outcome"])
        destination = (
            self.path.parent / "09_archived" / "AN-T-1@1-ASSET--example.md"
        )
        self.assertFalse(self.path.exists())
        self.assertEqual(body, destination.read_bytes().split(b"---\n", 2)[2])
        self.assertEqual(original_draft, draft.read_bytes())
        self.assertEqual(
            ("AN-T-1@1", 1, "archived"),
            tuple(
                outcome["artifact"][key]
                for key in ("ref_id", "version", "status")
            ),
        )
        capture = capture_native(self.selection)
        self.assertEqual({}, capture.errors)
        self.assertEqual(
            {"AN-T-1@1", "AN-T-1@2-draft"},
            {row["ref"] for row in capture.atoms if row["id"] == "AN-T-1"},
        )

    def test_archive_rejects_missing_draft_and_stale_selection(self):
        params = {"target": {"ref_id": "AN-T-1@1-draft", "version": 1}}
        with self.assertRaises(SourceChanged):
            archive_ticket(self.selection, params, current_rows=self.rows)
        params["target"] = self.params["target"]
        self.path.write_bytes(self.path.read_bytes() + b"stale")
        with self.assertRaises(SourceChanged):
            archive_ticket(self.selection, params, current_rows=self.rows)
        self.assertTrue(self.path.exists())
