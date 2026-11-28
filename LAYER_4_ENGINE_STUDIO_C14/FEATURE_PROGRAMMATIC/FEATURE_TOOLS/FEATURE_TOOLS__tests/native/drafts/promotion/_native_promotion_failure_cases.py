"""Exercise rollback and uncertain outcomes during Draft promotion."""

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.sources.inventory.native_source_rows__pub import (
    capture_native,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.drafts.promotion.native_draft_promotion_dispatch import (
    promote_draft,
)


class _PromotionFailureCases:
    def test_failed_replacement_rolls_back_archive(self):
        from unittest.mock import patch
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.ATOM_LIFECYCLE__shared import (
            Result,
        )

        failure = Result(
            errors=[{"code": "stale_state", "message": "injected failure"}]
        )
        with patch(
            (
                'FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.drafts.promotion.native_draft_promotion__shared.effects.replace'
            ),
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
                self.control
                / "001_TICKETS/TASKS/09_archived/AN-T-1@1-TASK--example.md"
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
                    errors=[
                        {"code": "stale_state", "message": "injected failure"}
                    ]
                )
            return original_remove(root, path, digest)

        with patch(
            (
                'FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.drafts.promotion.native_draft_promotion__shared.effects.remove'
            ),
            side_effect=remove,
        ):
            output = promote_draft(
                self.selection, self.promotion, current_rows=self.rows
            )
        self.assertEqual("failed", output["outcome"])
        self.assertTrue(self.path.exists())
        self.assertTrue(self.draft.exists())
        self.assertFalse(
            (
                self.control / "001_TICKETS/TASKS/done/AN-T-1-TASK--example.md"
            ).exists()
        )
        self.assertFalse(
            (
                self.control
                / "001_TICKETS/TASKS/09_archived/AN-T-1@1-TASK--example.md"
            ).exists()
        )
        self.assertFalse(capture_native(self.selection).errors)

    def test_changed_current_retains_generated_carriers_and_reports_uncertainty(
        self,
    ):
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
                    errors=[
                        {"code": "stale_state", "message": "injected failure"}
                    ]
                )
            return original_remove(root, path, digest)

        with patch(
            (
                'FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.drafts.promotion.native_draft_promotion__shared.effects.remove'
            ),
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
            (
                self.control / "001_TICKETS/TASKS/done/AN-T-1-TASK--example.md"
            ).exists()
        )
        self.assertTrue(
            (
                self.control
                / "001_TICKETS/TASKS/09_archived/AN-T-1@1-TASK--example.md"
            ).exists()
        )

    def test_changed_archive_is_retained_and_reported(self):
        from unittest.mock import patch
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.ATOM_LIFECYCLE__shared import (
            Result,
        )

        archive = (
            self.control
            / "001_TICKETS/TASKS/09_archived/AN-T-1@1-TASK--example.md"
        )

        def replace(*args):
            archive.write_bytes(archive.read_bytes() + b"external")
            return Result(
                errors=[{"code": "stale_state", "message": "injected failure"}]
            )

        with patch(
            (
                'FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.drafts.promotion.native_draft_promotion__shared.effects.replace'
            ),
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
            (
                'FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.drafts.native_draft__shared.common.write_destination'
            ),
            side_effect=write,
        ):
            output = promote_draft(
                self.selection, self.promotion, current_rows=self.rows
            )
        self.assertEqual("failed", output["outcome"])
        self.assertEqual("source_changed", output["errors"][0]["code"])
        self.assertFalse(
            (
                self.control
                / "001_TICKETS/TASKS/09_archived/AN-T-1@1-TASK--example.md"
            ).exists()
        )
        self.assertTrue(self.path.exists())
        self.assertTrue(self.draft.read_bytes().endswith(b"external"))
