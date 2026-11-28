"""Check the admitted carrier models and the comparison failure boundary."""

import hashlib
import json
import shutil
import unittest
from pathlib import Path
from unittest.mock import patch

from ARCHITECTURE_ANALYSIS_C73.IMPLEMENTATION_VERIFICATION_C74 \
    .carrier_compare import compare  # fmt: skip
from ARCHITECTURE_ANALYSIS_C73.IMPLEMENTATION_VERIFICATION_C74 \
    .carrier.carrier_formal import _PATHS as _PATHS  # fmt: skip
from ARCHITECTURE_ANALYSIS_C73.IMPLEMENTATION_VERIFICATION_C74 \
    .carrier.carrier_formal import formal_inputs as formal_inputs  # fmt: skip
from ARCHITECTURE_ANALYSIS_C73.IMPLEMENTATION_VERIFICATION_C74 \
    .carrier.carrier_model import _SOURCE, generate  # fmt: skip


from ARCHITECTURE_ANALYSIS_C73.IMPLEMENTATION_VERIFICATION_C74.\
    IMPLEMENTATION_VERIFICATION_C74__tests.functional.carrier_comparison \
    import _carrier_compare_helpers as helpers, _carrier_compare_more_helpers as more_helpers


ROOT = helpers.ROOT
SPEC = helpers.SPEC
_formal_witnesses = helpers._formal_witnesses
_pins = helpers._pins
_run_pinned_cli = helpers._run_pinned_cli


class CarrierModelTests(unittest.TestCase):
    def test_cli_requires_exact_source_digests(self):
        request = {
            **_formal_witnesses()["sources"],
            "implementation_sha256": "invalid",
        }
        result = _run_pinned_cli(request)
        self.assertEqual(result.returncode, 1, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["status"], "unresolved")
        self.assertIn("implementation_sha256", report["reason"])

    @unittest.skipUnless(shutil.which("lean"), "Lean is unavailable")
    def test_cli_replays_the_actual_pinned_framing_comparison(self):
        source_digest = hashlib.sha256(
            (ROOT / _SOURCE).read_bytes()
        ).hexdigest()
        pins = _formal_witnesses()["sources"]
        request = {**pins, "implementation_sha256": source_digest}
        result = _run_pinned_cli(request)
        self.assertEqual(
            result.returncode, 0, result.stderr + result.stdout[:1200]
        )
        report = json.loads(result.stdout)
        self.assertEqual(report["formal"]["sources"], pins)
        self.assertEqual(report["evidence"]["source_sha256"], source_digest)
        self.assertEqual(report["status"], "no_mismatch_in_cases")
        self.assertEqual(len(report["cases"]), 133)
        self.assertTrue(report["evidence"]["unresolved"])
        self.assertFalse(report["findings"])
        self.assertEqual(report["proof"]["status"], "proved")
        self.assertEqual(report["proof"]["quantified_over"], ["input", "path"])
        self.assertIn(
            (
                "CPython regex execution and path"
                " conversion require separate evi"
                "dence."
            ),
            report["evidence"]["unresolved"],
        )
        formal = self._report_formal(report)
        self._assert_failed_proof_keeps_samples(formal, request)
        self._assert_missing_theorem_keeps_samples(formal, request)
        stale = _run_pinned_cli(
            {**request, "solution": {**pins["solution"], "sha256": "0" * 64}}
        )
        self.assertEqual(stale.returncode, 1, stale.stderr)
        failure = json.loads(stale.stdout)
        self.assertEqual(failure["status"], "unresolved")
        self.assertEqual(
            failure["formal"]["diagnostics"][0]["field"], "sha256"
        )
        self.assertFalse(failure["cases"])

    def _report_formal(self, report):
        formal = {
            **report["formal"],
            "cases": [
                {
                    "input": row["raw"],
                    "manifest": row["manifest"],
                    "solution": row["solution"],
                }
                for row in report["cases"]
            ],
        }
        return formal

    def _assert_failed_proof_keeps_samples(self, formal, request):
        model, evidence = generate(ROOT)
        declaration = "def closingPatterns : List (List Nat) := "
        self.assertEqual(model.count(declaration), 1)
        mutated = model.replace(
            declaration, declaration + "[201, 202, 203] :: "
        )
        module = (
            "ARCHITECTURE_ANALYSIS_C73.IMPLEM"
            "ENTATION_VERIFICATION_C74.carrier."
            "carrier__shared"
        )
        with patch(f"{module}.generate", return_value=(mutated, evidence)):
            report = compare(
                ROOT, **request, formal_verifier=lambda *args, **kwargs: formal
            )
        self._assert_unresolved_proof(report)

    def _assert_missing_theorem_keeps_samples(self, formal, request):
        read_bytes = Path.read_bytes

        def without_manifest_body(path):
            raw = read_bytes(path)
            if path.name != "framing_equivalence_proof.lean":
                return raw
            head, removed = raw.split(b"theorem manifest_body", maxsplit=1)
            self.assertIn(b"end C30ImplementationEquivalence", removed)
            return head + b"end C30ImplementationEquivalence\n"

        with patch.object(Path, "read_bytes", without_manifest_body):
            report = compare(
                ROOT, **request, formal_verifier=lambda *args, **kwargs: formal
            )
        self._assert_unresolved_proof(report)
        self.assertIn(
            "C30ImplementationEquivalence.manifest_body",
            report["proof"]["reason"],
        )

    def _assert_unresolved_proof(self, report):
        self.assertEqual(len(report["cases"]), 133)
        self.assertFalse(report["findings"])
        self.assertTrue(
            all(
                row["code_matches_python"]
                and row["manifest_matches_code"]
                and row["solution_matches_code"]
                for row in report["cases"]
            )
        )
        self.assertEqual(report["proof"]["status"], "unresolved")
        self.assertEqual(report["status"], "unresolved")

    def test_live_source_and_analysis(self):
        return helpers._test_live_source_and_analysis(self)

    def test_unknown_source_fails_closed(self):
        return helpers._test_unknown_source_fails_closed(self)

    def test_missing_lean_is_unresolved(self):
        return helpers._test_missing_lean_is_unresolved(self)

    def test_unbound_solution_is_rejected(self):
        return helpers._test_unbound_solution_is_rejected(self)

    def test_embedded_contract_uses_manifest_hash(self):
        return helpers._test_embedded_contract_uses_manifest_hash(self)

    def test_duplicate_function_is_rejected(self):
        return helpers._test_duplicate_function_is_rejected(self)

    def test_extra_lean_output_is_unresolved(self):
        return helpers._test_extra_lean_output_is_unresolved(self)

    @unittest.skipUnless(shutil.which("lean"), "Lean is unavailable")
    def test_direct_comparison_checks_the_python_oracle(self):
        return helpers._test_direct_comparison_checks_the_python_oracle(self)

    def test_direct_comparison_rejects_different_solution_pin(self):
        return helpers._test_direct_comparison_rejects_different_solution_pin(
            self
        )

    def test_direct_comparison_replays_digest_pins(self):
        return more_helpers._test_direct_comparison_replays_digest_pins(self)

    def test_direct_comparison_checks_both_formal_hashes(self):
        return helpers._test_direct_comparison_checks_both_formal_hashes(self)

    def test_direct_comparison_reads_the_manifest_operations(self):
        return (
            more_helpers._test_direct_comparison_reads_the_manifest_operations(
                self
            )
        )

    @unittest.skipUnless(shutil.which("lean"), "Lean is unavailable")
    def test_direct_comparison_rejects_constant_path_in_lowered_errors(self):
        formal = _formal_witnesses()
        model, evidence = generate(ROOT)
        self.assertIn("path ++", model)
        mutated = model.replace(
            "path ++",
            '(if path.isEmpty then "carrier.md" else "carrier.md") ++',
        )
        module = (
            "ARCHITECTURE_ANALYSIS_C73.IMPLEM"
            "ENTATION_VERIFICATION_C74.carrier."
            "carrier__shared"
        )
        with patch(f"{module}.generate", return_value=(mutated, evidence)):
            report = compare(
                ROOT, **_pins(formal), formal_verifier=lambda *a, **kw: formal
            )
        self.assertEqual(report["status"], "unresolved")
        self.assertFalse(report["cases"][1]["code_matches_python"])

    @unittest.skipUnless(shutil.which("lean"), "Lean is unavailable")
    def test_confirmed_spec_mismatch_has_python_witness(self):
        blocks = [
            SPEC,
            SPEC.replace("CarrierBodyContract", "CarrierBodySolution"),
        ]
        with patch(
            (
                "ARCHITECTURE_ANALYSIS_C73.IMPLEM"
                "ENTATION_VERIFICATION_C74.carrie"
                "r_compare.formal_inputs"
            ),
            return_value=(blocks, {}),
        ):
            report = compare(ROOT)
        self.assertEqual(report["status"], "mismatch")
        self.assertTrue(
            all(case["code_matches_python"] for case in report["cases"])
        )
        self.assertTrue(
            any(
                row["case"] == "empty_crlf" and row["bounds"]
                for row in report["findings"]
            )
        )


if __name__ == "__main__":
    unittest.main()
