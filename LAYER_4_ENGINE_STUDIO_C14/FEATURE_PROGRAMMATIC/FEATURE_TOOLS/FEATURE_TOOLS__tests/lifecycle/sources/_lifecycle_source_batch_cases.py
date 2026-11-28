"""Lifecycle source selection scenarios."""

from unittest.mock import patch

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.sources import (
    source__shared as source_module,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.sources.source__shared import (
    select_source,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.sources.source_binding import (
    SourceSelectionError,
)


class BatchCases:
    def test_batch_current_sources_rechecks_all_candidates(self):
        first = self.carrier("CA-R-10-first.md")
        second = self.carrier("CA-R-11-first.md", identity="CA-R-11")
        with patch.object(
            source_module,
            "_inventory_paths",
            wraps=source_module._inventory_paths,
        ) as inventory:
            pins = source_module.select_current_sources(
                self.selection, ["CA-R-10", "CA-R-11"]
            )
        self.assertEqual(
            {key: pin.path for key, pin in pins.items()},
            {"CA-R-10": first, "CA-R-11": second},
        )
        self.assertEqual(inventory.call_count, 2)
        with self.assertRaisesRegex(
            SourceSelectionError, "missing or ambiguous"
        ):
            source_module.select_current_sources(
                self.selection, ["CA-R-10", "CA-R-12"]
            )
        with self.assertRaises(SourceSelectionError):
            source_module.select_current_sources(self.selection, ["CA-R-10@1"])
        original = source_module.parse_carrier

        def add_duplicate(raw, path):
            if path == second:
                self.carrier("CA-R-10-second.md")
            return original(raw, path)

        with patch.object(
            source_module, "parse_carrier", side_effect=add_duplicate
        ):
            with self.assertRaisesRegex(
                SourceSelectionError, "candidates changed"
            ):
                source_module.select_current_sources(
                    self.selection, ["CA-R-10", "CA-R-11"]
                )

    def test_batch_selects_draft_and_archived_revisions_with_one_inventory(
        self,
    ):
        archived = self.carrier("CA-R-10@1-example.md", status="Archived")
        draft = self.carrier(
            "CA-R-10@2-draft-example.md", version=2, status="Draft"
        )
        with patch.object(
            source_module,
            "_inventory_paths",
            wraps=source_module._inventory_paths,
        ) as inventory:
            pins = source_module.select_sources(
                self.selection, ["CA-R-10@1", "CA-R-10@2-draft"]
            )
        self.assertEqual(inventory.call_count, 2)
        self.assertEqual(pins["CA-R-10@1"].path, archived)
        self.assertEqual(pins["CA-R-10@2-draft"].path, draft)
        self.carrier("CA-R-10@2-draft-other.md", version=2, status="Draft")
        with self.assertRaisesRegex(
            SourceSelectionError, "missing or ambiguous"
        ):
            source_module.select_sources(
                self.selection, ["CA-R-10@1", "CA-R-10@2-draft"]
            )

    def test_symlinked_role_directory_fails_closed(self):
        self.carrier("CA-R-10-first.md")
        (self.folder / "linked").symlink_to(
            self.root, target_is_directory=True
        )
        with self.assertRaises(SourceSelectionError):
            select_source(self.selection, "CA-R-10")

    def test_invalid_version_and_changed_declaration(self):
        self.carrier("CA-R-10@2-draft-example.md", version=3, status="draft")
        with self.assertRaises(SourceSelectionError):
            select_source(self.selection, "CA-R-10@2-draft")
        self.selection.declaration_paths[0].write_text("changed")
        with self.assertRaises(SourceSelectionError):
            select_source(self.selection, "CA-R-10")

    def test_declaration_changed_during_discovery_is_rejected(self):
        self.carrier("CA-R-10-first.md")
        original = source_module.parse_carrier

        def change_declaration(raw, path):
            self.selection.declaration_paths[0].write_text("changed")
            return original(raw, path)

        with patch.object(
            source_module, "parse_carrier", side_effect=change_declaration
        ):
            with self.assertRaises(SourceSelectionError):
                select_source(self.selection, "CA-R-10")
