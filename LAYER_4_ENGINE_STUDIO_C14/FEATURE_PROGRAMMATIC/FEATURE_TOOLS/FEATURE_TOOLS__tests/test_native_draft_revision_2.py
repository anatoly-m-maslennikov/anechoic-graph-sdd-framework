from pathlib import Path
import sys
import unittest


sys.path.insert(
    0,
    str(
        (ENGINE := (TOOLS := Path(__file__).resolve().parents[1]).parents[1])
        / "IWE_CONSOLE_C43"
    ),
)
sys.path.insert(0, str(TOOLS))

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared \
    import capture_native  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.ATOM_LIFECYCLE__shared \
    import (
        create_draft,
        promote_draft,
    )  # fmt: skip


import FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__tests.test_native_lifecycle_draft as fixtures


class NativeRevisionCarrierTests(
    fixtures.NativeRevisionCarrierTests, unittest.TestCase
):
    def test_spec_retry_after_cleanup_failure(self):
        from unittest.mock import patch
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.\
            ATOM_LIFECYCLE__shared \
            import effects_module as effects  # fmt: skip

        self.spec("UNIT_C9/__DES/AN-S-4-DES--example.md", "AN-S-4")
        output = create_draft(
            self.selection,
            {"sourceCurrent": {"ref_id": "AN-S-4", "version": 1}},
            current_rows=capture_native(self.selection).atoms,
        )
        ref = output["savedDraft"]["ref_id"]
        params = {
            "target": {"ref_id": ref, "version": 2},
            "targetStatus": "ready",
        }
        original_remove = effects.remove

        def remove(root, path, digest):
            return (
                effects.Result(errors=[{"code": "injected"}])
                if path.parent.name == "01_draft"
                else original_remove(root, path, digest)
            )

        with patch(
            (
                "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.native_draf"
                "t_promotion.effects.remove"
            ),
            side_effect=remove,
        ):
            result = promote_draft(
                self.selection,
                params,
                current_rows=capture_native(self.selection).atoms,
            )
        self.assertEqual("failed", result["outcome"])
        result = promote_draft(
            self.selection,
            params,
            current_rows=capture_native(self.selection).atoms,
        )
        self.assertEqual("completed", result["outcome"])
        self.assertEqual(
            ["remove"], [effect["operation"] for effect in result["effects"]]
        )
