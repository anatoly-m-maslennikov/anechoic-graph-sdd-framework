"""Threshold format and literal fallback remain static declaration data."""

import unittest


from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model.claims.claims__shared import (
    parse_native_model_claim,
    NativeModelClaimError,
)
from FEATURE_PROGRAMMATIC.FEATURE_FORMAL_MODEL_ENGINE.claim_compiler.compiler_claim import (
    compiler_model_statements,
)
from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.\
    FEATURE_PROJECT_TOOLS__tests.\
    FEATURE_PROJECT_TOOLS__tests__shared \
    import (
    THRESHOLD as CLAIM,
)  # fmt: skip


class ThresholdTests(unittest.TestCase):
    def test_constraints_and_fallback(self):
        decl = parse_native_model_claim(CLAIM)
        self.assertEqual(
            compiler_model_statements(decl),
            (
                (
                    "Project.Settings.AI Agent Confidence Threshold{::1} :: "
                    "[int, 0..100]{::1} ?== 90"
                ),
                "Project.Settings.AI Agent Confidence Threshold.*[]{::0}",
            ),
        )

    def test_bad_values(self):
        for bad in (
            CLAIM.replace("fallback_value=90", "fallback_value=101"),
            CLAIM.replace("maximum_value=100", "maximum_value=-1"),
        ):
            with self.assertRaises(NativeModelClaimError):
                parse_native_model_claim(bad)
