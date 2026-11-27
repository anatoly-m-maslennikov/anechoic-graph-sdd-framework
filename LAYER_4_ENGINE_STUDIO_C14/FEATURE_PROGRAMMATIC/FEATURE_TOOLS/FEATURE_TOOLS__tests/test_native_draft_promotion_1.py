from pathlib import Path
import sys
import unittest


TOOLS = Path(__file__).resolve().parents[1]
ENGINE = TOOLS.parents[1]
sys.path[:0] = [str(TOOLS), str(ENGINE / "IWE_CONSOLE_C43")]

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    capture_native,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.ATOM_LIFECYCLE__shared import (
    InputError,
    SourceChanged,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.ATOM_LIFECYCLE__shared import (
    promote_draft,
)


import FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__tests.test_native_lifecycle_draft as fixtures


class NativePromotionTests(fixtures.NativePromotionTests, unittest.TestCase):
    def test_promotes_same_id_and_archives_pinned_current(self):
        old = self.path.read_bytes()
        output = promote_draft(self.selection, self.promotion, current_rows=self.rows)
        self.assertEqual("completed", output["outcome"])
        self.assertEqual(
            ("AN-T-1", 2, "active"),
            (
                output["artifact"]["ref_id"],
                output["artifact"]["version"],
                output["artifact"]["status"],
            ),
        )
        self.assertFalse(self.draft.exists())
        capture = capture_native(self.selection)
        self.assertFalse(capture.errors)
        archived = next(row for row in capture.atoms if row["_exact_ref"] == "AN-T-1@1")
        current = next(row for row in capture.atoms if row["_exact_ref"] == "AN-T-1@2")
        self.assertEqual("Archived", archived["status_group"])
        self.assertEqual("Current", current["status_group"])
        self.assertEqual(old.split(b"---\n", 2)[2], archived["_content_bytes"])
        self.assertIn(b"New", current["_content_bytes"])
        self.assertEqual(
            ["create", "create", "modify", "remove"],
            [e["operation"] for e in output["effects"]],
        )

    def test_promotes_to_another_current_status(self):
        self.promotion["targetStatus"] = "done"
        output = promote_draft(self.selection, self.promotion, current_rows=self.rows)
        self.assertEqual("completed", output["outcome"])
        self.assertFalse(self.path.exists())
        self.assertEqual(
            self.control / "001_TICKETS/TASKS/done/AN-T-1-TASK--example.md",
            self.root / output["artifact"]["path"],
        )
        self.assertFalse(capture_native(self.selection).errors)

    def test_retry_of_revision_promotion_removes_only_pinned_draft(self):
        from unittest.mock import patch
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.ATOM_LIFECYCLE__shared import (
            effects_module as effects,
        )

        with patch(
            "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.native_draft_promotion.effects.remove",
            return_value=effects.Result(errors=[{"code": "injected"}]),
        ):
            output = promote_draft(
                self.selection, self.promotion, current_rows=self.rows
            )
        self.assertEqual("failed", output["outcome"])
        rows = capture_native(self.selection).atoms
        output = promote_draft(self.selection, self.promotion, current_rows=rows)
        self.assertEqual("completed", output["outcome"])
        self.assertEqual(["remove"], [item["operation"] for item in output["effects"]])
        self.assertEqual(2, output["artifact"]["version"])
        self.assertFalse(self.draft.exists())
        self.assertFalse(capture_native(self.selection).errors)

    def test_conflict_and_stale_sources_have_no_effects(self):
        for case in ("collision", "draft", "current", "manifest", "selector"):
            with self.subTest(case=case):
                old, draft, manifest = (
                    self.path.read_bytes(),
                    self.draft.read_bytes(),
                    self.selection.manifest_path.read_bytes(),
                )
                params = {
                    "target": dict(self.promotion["target"]),
                    "targetStatus": "active",
                }
                conflict = None
                if case == "collision":
                    conflict = self.write(
                        "001_TICKETS/TASKS/09_archived/AN-T-1@2-TASK--example.md",
                        "AN-T-1",
                        version=2,
                        status="archived",
                    )
                if case == "draft":
                    self.draft.write_bytes(draft.replace(b"New", b"Changed"))
                if case == "current":
                    self.path.write_bytes(old.replace(b"Old", b"Changed"))
                if case == "manifest":
                    self.selection.manifest_path.write_bytes(manifest + b"changed")
                if case == "selector":
                    params["target"]["ref_id"] = "AN-T-1@2"
                with self.assertRaises((InputError, SourceChanged)):
                    promote_draft(self.selection, params, current_rows=self.rows)
                self.assertTrue(self.path.exists())
                self.assertTrue(self.draft.exists())
                self.path.write_bytes(old)
                self.draft.write_bytes(draft)
                self.selection.manifest_path.write_bytes(manifest)
                if conflict:
                    conflict.unlink()

    def test_unsafe_status_directory_is_refused_before_archival(self):
        outside = self.root / "outside"
        outside.mkdir()
        (self.control / "001_TICKETS/TASKS/done").symlink_to(
            outside, target_is_directory=True
        )
        self.promotion["targetStatus"] = "done"
        with self.assertRaises(InputError):
            promote_draft(self.selection, self.promotion, current_rows=self.rows)
        self.assertFalse((self.control / "001_TICKETS/TASKS/09_archived").exists())
        self.assertEqual([], list(outside.iterdir()))

    def test_failed_replacement_rolls_back_archive(self):
        from unittest.mock import patch
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.ATOM_LIFECYCLE__shared import (
            Result,
        )

        failure = Result(
            errors=[{"code": "stale_state", "message": "injected failure"}]
        )
        with patch(
            "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.native_draft_promotion.effects.replace",
            return_value=failure,
        ):
            output = promote_draft(
                self.selection, self.promotion, current_rows=self.rows
            )
        self.assertEqual("failed", output["outcome"])
        self.assertTrue(output["effects"])
        self.assertTrue(self.draft.exists())
        self.assertTrue(self.path.exists())
        self.assertFalse(
            (
                self.control / "001_TICKETS/TASKS/09_archived/AN-T-1@1-TASK--example.md"
            ).exists()
        )
        self.assertFalse(capture_native(self.selection).errors)

    def test_failed_removal_rolls_back_status_destination_and_archive(self):
        from unittest.mock import patch
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.ATOM_LIFECYCLE__shared import (
            effects_module as effects,
        )

        original_remove = effects.remove
        self.promotion["targetStatus"] = "done"

        def remove(root, path, digest):
            if path == self.path:
                return effects.Result(
                    errors=[{"code": "stale_state", "message": "injected failure"}]
                )
            return original_remove(root, path, digest)

        with patch(
            "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.native_draft_promotion.effects.remove",
            side_effect=remove,
        ):
            output = promote_draft(
                self.selection, self.promotion, current_rows=self.rows
            )
        self.assertEqual("failed", output["outcome"])
        self.assertTrue(self.path.exists())
        self.assertTrue(self.draft.exists())
        self.assertFalse(
            (self.control / "001_TICKETS/TASKS/done/AN-T-1-TASK--example.md").exists()
        )
        self.assertFalse(
            (
                self.control / "001_TICKETS/TASKS/09_archived/AN-T-1@1-TASK--example.md"
            ).exists()
        )
        self.assertFalse(capture_native(self.selection).errors)

    def test_changed_current_retains_generated_carriers_and_reports_uncertainty(self):
        from unittest.mock import patch
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.ATOM_LIFECYCLE__shared import (
            effects_module as effects,
        )

        original_remove = effects.remove
        self.promotion["targetStatus"] = "done"

        def remove(root, path, digest):
            if path == self.path:
                self.path.write_bytes(self.path.read_bytes() + b"external")
                return effects.Result(
                    errors=[{"code": "stale_state", "message": "injected failure"}]
                )
            return original_remove(root, path, digest)

        with patch(
            "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.native_draft_promotion.effects.remove",
            side_effect=remove,
        ):
            output = promote_draft(
                self.selection, self.promotion, current_rows=self.rows
            )
        self.assertEqual("failed", output["outcome"])
        self.assertIn(
            "rollback_unconfirmed", [item["code"] for item in output["errors"]]
        )
        self.assertTrue(self.path.read_bytes().endswith(b"external"))
        self.assertTrue(self.draft.exists())
        self.assertTrue(
            (self.control / "001_TICKETS/TASKS/done/AN-T-1-TASK--example.md").exists()
        )
        self.assertTrue(
            (
                self.control / "001_TICKETS/TASKS/09_archived/AN-T-1@1-TASK--example.md"
            ).exists()
        )

    def test_changed_archive_is_retained_and_reported(self):
        from unittest.mock import patch
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.ATOM_LIFECYCLE__shared import (
            Result,
        )

        archive = (
            self.control / "001_TICKETS/TASKS/09_archived/AN-T-1@1-TASK--example.md"
        )

        def replace(*args):
            archive.write_bytes(archive.read_bytes() + b"external")
            return Result(
                errors=[{"code": "stale_state", "message": "injected failure"}]
            )

        with patch(
            "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.native_draft_promotion.effects.replace",
            side_effect=replace,
        ):
            output = promote_draft(
                self.selection, self.promotion, current_rows=self.rows
            )
        self.assertEqual("failed", output["outcome"])
        self.assertIn(
            "rollback_unconfirmed", [item["code"] for item in output["errors"]]
        )
        self.assertTrue(archive.read_bytes().endswith(b"external"))
        self.assertTrue(self.path.exists())
        self.assertTrue(self.draft.exists())

    def test_changed_draft_after_archival_rolls_back_archive(self):
        from unittest.mock import patch
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.ATOM_LIFECYCLE__shared import (
            common_module as common,
        )

        original_write = common.write_destination

        def write(root, path, raw):
            outcome = original_write(root, path, raw)
            self.draft.write_bytes(self.draft.read_bytes() + b"external")
            return outcome

        with patch(
            "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.native_draft.common.write_destination",
            side_effect=write,
        ):
            output = promote_draft(
                self.selection, self.promotion, current_rows=self.rows
            )
        self.assertEqual("failed", output["outcome"])
        self.assertEqual("source_changed", output["errors"][0]["code"])
        self.assertFalse(
            (
                self.control / "001_TICKETS/TASKS/09_archived/AN-T-1@1-TASK--example.md"
            ).exists()
        )
        self.assertTrue(self.path.exists())
        self.assertTrue(self.draft.read_bytes().endswith(b"external"))
