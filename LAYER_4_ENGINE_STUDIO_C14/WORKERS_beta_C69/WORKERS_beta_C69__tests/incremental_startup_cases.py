from unittest.mock import patch

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared \
    import UnrepresentableCarrierDelta  # fmt: skip


class IncrementalStartupCases:
    def test_hash_probe_errors_fall_back_to_full_capture(self):
        for error in (
            OSError("unreadable file"),
            UnrepresentableCarrierDelta("unavailable file hash"),
        ):
            with patch(
                "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30."
                "ADAPTERS_C30__shared.native_carrier_hashes",
                side_effect=error,
            ):
                self.assertIn("receipt", self.capture())
                self.assertEqual(
                    {"incompatible": True},
                    self.capture(archive_roots=self.roots),
                )
