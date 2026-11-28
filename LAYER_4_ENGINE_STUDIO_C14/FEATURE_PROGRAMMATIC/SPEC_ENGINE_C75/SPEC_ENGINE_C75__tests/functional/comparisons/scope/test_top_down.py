import os
import shutil
import unittest
from unittest.mock import patch

from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.\
    LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_4_SPEC_COMPARISON_C88.\
    _package__shared import compare_obligations  # fmt: skip


def _numeric_obligations():
    return {
        "manifest": {
            "equal": {"x": [1]},
            "different": 1,
            "missing": None,
            "boolean": [True],
            "precise": 9007199254740993,
            "zero": -0.0,
        },
        "contract": {
            "equal": {"x": [1.0]},
            "different": 2,
            "boolean": [1],
            "precise": 9007199254740992.0,
            "zero": 0,
        },
        "solution": {},
    }


class TopDownTests(unittest.TestCase):
    def test_lean_compares_all_directions_and_preserves_pins(self):
        lean = os.environ.get("ANECHOIC_TEST_LEAN") or shutil.which("lean")
        if lean is None:
            self.skipTest("Lean executable unavailable")
        sources = {
            role: {"atom_id": role, "version": "1"}
            for role in ("manifest", "contract", "solution")
        }
        result = compare_obligations(
            sources, _numeric_obligations(), lean=lean
        )
        self.assertEqual(sources, result["sources"])
        direction = result["directions"]["manifest_contract"]
        self.assertEqual("conflicting", direction["status"])
        self.assertEqual(
            {
                "different": "conflicting",
                "equal": "matched",
                "missing": "unresolved",
                "boolean": "conflicting",
                "precise": "conflicting",
                "zero": "matched",
            },
            {fact["key"]: fact["status"] for fact in direction["facts"]},
        )
        self.assertEqual(
            "unresolved", result["directions"]["contract_solution"]["status"]
        )
        empty = compare_obligations(
            sources, {role: {} for role in sources}, lean=lean
        )
        self.assertEqual("unresolved", empty["status"])
        self.assertTrue(
            all(
                direction["status"] == "unresolved"
                for direction in empty["directions"].values()
            )
        )

    def test_lean_failure_is_explicit(self):
        roles = ("manifest", "contract", "solution")
        with patch(
            "subprocess.run", side_effect=FileNotFoundError("missing Lean")
        ):
            with self.assertRaisesRegex(ValueError, "Lean comparison failed"):
                compare_obligations(
                    {role: {} for role in roles}, {role: {} for role in roles}
                )

    def test_malformed_obligations_are_rejected_before_lean(self):
        sources = {role: {} for role in ("manifest", "contract", "solution")}
        for malformed in (None, {1: "value"}):
            obligations = {**sources, "solution": malformed}
            with self.subTest(malformed=malformed):
                with self.assertRaisesRegex(
                    ValueError, "contain each comparison role"
                ):
                    compare_obligations(
                        sources, obligations, lean="/missing/lean"
                    )

    def test_malformed_lean_rows_are_rejected(self):
        sources = {role: {} for role in ("manifest", "contract", "solution")}
        obligations = {role: {"value": 1} for role in sources}
        for output in (
            "null",
            '[["matched"]]',
            '[null, ["matched"], ["matched"]]',
            '[[], ["matched"], ["matched"]]',
            '[["mismatch"], ["matched"], ["matched"]]',
        ):
            with self.subTest(output=output), patch("subprocess.run") as run:
                run.return_value.returncode = 0
                run.return_value.stdout = output
                with self.assertRaisesRegex(
                    ValueError, "unexpected Lean comparison output"
                ):
                    compare_obligations(sources, obligations)
