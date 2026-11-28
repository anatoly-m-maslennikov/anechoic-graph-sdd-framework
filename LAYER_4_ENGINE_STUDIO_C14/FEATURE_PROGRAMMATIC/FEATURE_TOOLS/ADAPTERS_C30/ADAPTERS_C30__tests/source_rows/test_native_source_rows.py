from hashlib import sha256 as sha256
from pathlib import PurePosixPath
import os as os
import unittest
from unittest.mock import NonCallableMock as NonCallableMock, patch

import yaml

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    ReadContext as ReadContext,
    native_carrier_hashes as native_carrier_hashes,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.sources.inventory.native_source_rows__pub import (
    capture_native,
    revalidate_native,
)


from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    ADAPTERS_C30__tests.ADAPTERS_C30__tests__shared import (
    NativeCaptureFixture,
)  # fmt: skip

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model.model_capture import (
    model_inputs as model_inputs,
)


from ._native_source_row_cases import NativeSourceRowCases


class NativeCaptureTests(
    NativeSourceRowCases, NativeCaptureFixture, unittest.TestCase
):
    def \
   test_canonical_header_controls_identity_and_preserves_authored_metadata(
        self,
    ):  # fmt: skip
        path = self.control / "__TKT" / "arbitrary-name.md"
        path.parent.mkdir(parents=True)
        header = {
            "atom_family": "SPEC",
            "atom_id": "AN-S-20",
            "structure": {"container": {"component": "C0"}, "tier": 3},
            "context": {"lens": "example"},
            "state": {
                "status": "active",
                "version": 1,
                "updated_at": "2026-11-19T00:00:00Z",
            },
        }
        path.write_text(
            "---\n" + yaml.safe_dump(header) + "---\n\n## Summary\n\nExample\n"
        )
        result = capture_native(self.selection)
        self.assertEqual({}, result.errors)
        row = next(row for row in result.atoms if row["id"] == "AN-S-20")
        self.assertEqual(header, row["header_json"])
        self.assertEqual(3, row["tier"])
        self.assertEqual("AN-S-20", row["ref"])
        self.assertEqual(
            "C0",
            next(
                edge
                for edge in result.containment
                if edge["source_ref"] == "AN-S-20"
            )["target_ref"],
        )

        duplicate = self.control / "elsewhere.md"
        duplicate.write_bytes(path.read_bytes())
        self.assertTrue(
            any(
                "Duplicate" in error
                for error in capture_native(self.selection).errors.values()
            )
        )

    def test_complete_ticket_asset_is_current(self):
        path = (
            self.control / "001_TICKETS/ASSETS/08_complete/AN-T-14--asset.md"
        )
        path.parent.mkdir(parents=True)
        header = {
            "atom_family": "TKT",
            "atom_id": "AN-T-14",
            "container": {"component": "C0"},
            "priority": 2,
            "context": {"template": "analysis_report"},
            "state": {
                "status": "complete",
                "version": 2,
                "updated_at": "2026-11-19T00:00:00Z",
            },
        }
        path.write_text(
            "---\n" + yaml.safe_dump(header) + "---\n\n## Summary\n\nExample\n"
        )
        result = capture_native(self.selection)
        self.assertEqual({}, result.errors)
        row = next(row for row in result.atoms if row["id"] == "AN-T-14")
        self.assertEqual(
            ("Current", "AN-T-14", "AN-T-14@2"),
            (row["status_group"], row["ref"], row["_exact_ref"]),
        )

    def test_ticket_in_queue_is_current_and_in_progress_is_invalid(self):
        self.write("AN-T-12--queued.md", "AN-T-12", "in_queue", 2)
        self.write("AN-T-13--working.md", "AN-T-13", "in_progress", 1)
        result = capture_native(self.selection)
        row = next(row for row in result.atoms if row["id"] == "AN-T-12")
        self.assertEqual(
            ("Current", "AN-T-12", "AN-T-12@2"),
            (row["status_group"], row["ref"], row["_exact_ref"]),
        )
        self.assertEqual(1, len(result.errors))
        self.assertIn("status", next(iter(result.errors.values())))

    def test_ready_is_current_only_for_spec(self):
        self.write("02_ready/AN-S-2--ready.md", "AN-S-2", "ready", 2)
        self.write("AN-T-3--invalid.md", "AN-T-3", "ready", 1)
        self.write("_PMETA/AN-P-4--invalid.md", "AN-P-4", "ready", 1)
        result = capture_native(self.selection)
        row = next(row for row in result.atoms if row["id"] == "AN-S-2")
        self.assertEqual(
            ("Current", "AN-S-2", "AN-S-2@2"),
            (row["status_group"], row["ref"], row["_exact_ref"]),
        )
        self.assertEqual(2, len(result.errors))
        self.assertTrue(
            all("status" in error for error in result.errors.values())
        )
        self.write("AN-S-2--active.md", "AN-S-2", "active", 3)
        self.assertTrue(
            any(
                "Duplicate" in error
                for error in capture_native(self.selection).errors.values()
            )
        )

    def test_new_folder_names_accept_legacy_headers(self):
        for folder, atom_id in (
            ("001_TICKETS/TASKS/01_draft", "AN-T-10"),
            ("002_PROJECT_CONFIG/09_archived", "AN-P-10"),
            ("__TICKETS/TASKS/01_draft", "AN-T-11"),
            ("__PROJECT_CONFIG/09_archived", "AN-P-11"),
        ):
            status = "draft" if "01_draft" in folder else "archived"
            ref = f"{atom_id}@1" + ("-draft" if status == "draft" else "")
            path = self.control / folder / f"{ref}--example.md"
            path.parent.mkdir(parents=True)
            header = {
                "identity": {"atom_id": atom_id},
                "context": {"container": {"component": "C0"}},
                "state": {
                    "status": status,
                    "version": 1,
                    "updated_at": "2026-11-19T00:00:00Z",
                },
            }
            path.write_text(
                "---\n"
                + yaml.safe_dump(header)
                + "---\n\n## Summary\n\nExample\n"
            )
        result = capture_native(self.selection)
        self.assertEqual({}, result.errors)
        self.assertEqual(
            {"AN-T-10@1-draft", "AN-P-10@1", "AN-T-11@1-draft", "AN-P-11@1"},
            {
                row["ref"]
                for row in result.atoms
                if row["id"] in {"AN-T-10", "AN-P-10", "AN-T-11", "AN-P-11"}
            },
        )

    def test_mixed_project_config_markers_and_nested_definitions(self):
        self.write(
            "002_PROJECT_CONFIG/AN-P-20--legacy.md", "AN-P-20", "active", 1
        )
        self.write(
            "002_PROJECT_CONFIG/CUSTOM_MODEL/AN-C-21--definition.md",
            "AN-C-21",
            "active",
            2,
            {"atom": "AN-P-20"},
        )
        self.write(
            "002_PROJECT_CONFIG/AN-C-21@3-draft--definition.md",
            "AN-C-21",
            "draft",
            3,
        )
        self.write(
            "002_PROJECT_CONFIG/AN-C-21@1--definition.md",
            "AN-C-21",
            "archived",
            1,
        )
        result = capture_native(self.selection)
        self.assertEqual({}, result.errors)
        rows = {row["_exact_ref"]: row for row in result.atoms}
        self.assertEqual(
            ("Current", "AN-C-21"),
            (rows["AN-C-21@2"]["status_group"], rows["AN-C-21@2"]["ref"]),
        )
        self.assertEqual("AN-C-21@3-draft", rows["AN-C-21@3-draft"]["ref"])
        self.assertEqual("AN-C-21@1", rows["AN-C-21@1"]["ref"])
        self.assertEqual(
            "AN-P-20",
            next(
                edge
                for edge in result.containment
                if edge["source_ref"] == "AN-C-21"
            )["target_ref"],
        )

    def test_invalid_and_duplicate_carriers_are_reported(self):
        self.write("one/AN-S-1--one.md", "AN-S-1", "active", 1)
        self.write("two/AN-S-1--two.md", "AN-S-1", "active", 2)
        self.write("AN-T-2--bad.md", "AN-T-2", "bogus", 1)
        result = capture_native(self.selection)
        self.assertEqual(3, len(result.errors))
        self.assertTrue(
            any("Duplicate" in error for error in result.errors.values())
        )
        self.assertTrue(
            any("status" in error for error in result.errors.values())
        )

    def test_installed_methodology_copies_are_excluded(self):
        active = self.write("AN-S-2--definition.md", "AN-S-2", "active", 1)
        copy = self.control / "000_ANECHOIC_framework/sources" / active.name
        copy.parent.mkdir(parents=True)
        copy.write_bytes(active.read_bytes())
        result = capture_native(self.selection)
        self.assertEqual({}, result.errors)
        self.assertEqual(
            {"AN-S-001@1", "AN-S-2@1"},
            {row["_exact_ref"] for row in result.atoms},
        )

    def test_incremental_capture_reads_changes_and_matches_full_after_move(
        self,
    ):
        old = self.write("AN-S-2--old.md", "AN-S-2", "active", 1)
        untouched = self.write("AN-S-3--untouched.md", "AN-S-3", "active", 1)
        previous = capture_native(self.selection)
        new = old.with_name("AN-S-2--new.md")
        old.rename(new)
        changed = {
            PurePosixPath(path.relative_to(self.root).as_posix())
            for path in (old, new)
        }
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
            ADAPTERS_C30__shared import (ReadContext)  # fmt: skip

        read = ReadContext.read
        with patch.object(
            ReadContext, "read", autospec=True, side_effect=read
        ) as reads:
            result = capture_native(
                self.selection, previous=previous, paths=changed
            )
        self.assertNotIn(
            untouched, [call.args[1] for call in reads.call_args_list]
        )
        self.assertEqual(capture_native(self.selection), result)

    def test_incremental_duplicate_and_repair(self):
        original = self.write("one/AN-S-2--one.md", "AN-S-2", "active", 1)
        duplicate = self.control / "two" / original.name
        duplicate.parent.mkdir()
        previous = capture_native(self.selection)
        duplicate.write_bytes(original.read_bytes())
        changed = {PurePosixPath(duplicate.relative_to(self.root).as_posix())}
        result = capture_native(
            self.selection, previous=previous, paths=changed
        )
        self.assertTrue(
            any("Duplicate" in error for error in result.errors.values())
        )
        duplicate.unlink()
        repaired = capture_native(
            self.selection, previous=result, paths=changed
        )
        self.assertEqual(capture_native(self.selection), repaired)
        self.assertEqual(repaired, revalidate_native(self.selection, result))

    def test_manifest_drift_refuses_capture(self):
        self.manifest.write_text("changed", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Manifest changed"):
            capture_native(self.selection)

    def test_revalidation_refuses_new_carrier_between_inventory_passes(self):
        previous = capture_native(self.selection)

        def capture_then_add(*args, **kwargs):
            captured = capture_native(*args, **kwargs)
            self.write("new/AN-S-2--added.md", "AN-S-2", "active", 1)
            return captured

        with patch(
            f"{capture_native.__module__}.capture_native",
            side_effect=capture_then_add,
        ):
            with self.assertRaisesRegex(
                ValueError, "carriers changed during capture"
            ):
                revalidate_native(self.selection, previous)

    def test_archive_rejects_a_draft_marker_and_wrong_tree(self):
        self.write(
            "archived/AN-S-2@1-draft--withdrawn.md", "AN-S-2", "archived", 1
        )
        self.write("__TKT/ASSETS/AN-S-3--wrong-tree.md", "AN-S-3", "active", 1)
        reports = capture_native(self.selection).errors
        self.assertEqual(2, len(reports))
        self.assertTrue(
            any("Filename marker" in error for error in reports.values())
        )
        self.assertTrue(
            any("logical tree" in error for error in reports.values())
        )


if __name__ == "__main__":
    unittest.main()
