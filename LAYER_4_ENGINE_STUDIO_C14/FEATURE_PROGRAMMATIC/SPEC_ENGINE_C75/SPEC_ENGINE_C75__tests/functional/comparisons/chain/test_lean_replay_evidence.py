import json
import os
import shutil
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75 import formal_chain__pub as chain
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75._package__shared import (
    verify_formal_chain,
)

from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_1_SOURCE_ADAPTERS_C95.\
    _package__shared import SourceError, read_source  # fmt: skip
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.\
    LAYER_3_LEAN_TRANSLATOR_C84._package__shared import (
    run_lean_json,
)  # fmt: skip

from .lean_replay_fixtures import (
    assert_observations,
    assert_replay,
    comparison_mutations,
    default_failure_standard,
)
from .test_direct_manifest_chain import _manifest, _pins
from ...workflows.trace.test_trace_cases import FIRST, SECOND, SOLUTION


class LeanReplayEvidenceTests(unittest.TestCase):
    def test_stage_observations_detect_changed_renderer_input(self):
        lean = os.environ.get("ANECHOIC_TEST_LEAN") or shutil.which("lean")
        self.assertTrue(lean, "Lean executable unavailable")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pins = _pins(root, _manifest("python trace", FIRST), SOLUTION)
            result = verify_formal_chain(root, "C15", *pins, lean=lean)
            self.assertEqual("compared", result["outcome"], result)
            evidence = result["evidence"]
            actual = json.loads(evidence["validation_programs"][0]["stdout"])
            claims = {
                role: row[0]["claim"]
                for role, row in zip(
                    ("manifest", "contract", "solution"),
                    actual[-1][0],
                    strict=True,
                )
            }

            assert_observations(self, evidence, evidence["stages"], claims)
            fake = {"status": "matched", "issues": [], "unresolved": []}
            fake["claims"] = claims
            with patch.object(
                chain, "validate_translation", return_value=fake
            ):
                missing = verify_formal_chain(root, "C15", *pins, lean=lean)
            self.assertEqual("incomplete", missing["outcome"], missing)
            self.assertIn(
                "Missing Lean validation observation",
                missing["diagnostics"][0]["message"],
            )
            original = chain.render_solution

            def changed(model, claim, **options):
                claim = deepcopy(claim)
                claim["states"][0]["transitions"][0]["event"] = "forged_event"
                return original(model, claim, **options)

            with patch.object(chain, "render_solution", side_effect=changed):
                failed = verify_formal_chain(root, "C15", *pins, lean=lean)
            self.assertEqual("incomplete", failed["outcome"], failed)
            self.assertIn(
                "Rendering Solution identity",
                failed["diagnostics"][0]["message"],
            )
            self.assertNotIn("evidence", failed)

    def test_changed_action_or_comparison_model_is_incomplete(self):
        lean = os.environ.get("ANECHOIC_TEST_LEAN") or shutil.which("lean")
        self.assertTrue(lean, "Lean executable unavailable")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = _manifest(
                "python trace", FIRST, FIRST.replace("'compile'", "'audit'")
            )
            solution = (
                SOLUTION
                + "\n```\n\n```python\n"
                + SOLUTION.replace("'compile'", "'audit'")
            )
            pins = _pins(root, manifest, solution)
            for name, mutate, message in comparison_mutations():
                with (
                    self.subTest(name=name),
                    patch.object(chain, name, side_effect=mutate),
                ):
                    result = verify_formal_chain(
                        root, "C15", *pins, action="compile", lean=lean
                    )
                    self.assertEqual("incomplete", result["outcome"], result)
                    self.assertIn(message, result["diagnostics"][0]["message"])

    def test_draft_failure_standard_on_public_incomplete_response(self):
        root = Path(__file__).resolve().parents[7]
        standard = default_failure_standard(self, root)
        claim = standard.body.split("```lean\n", 1)[1].split("```", 1)[0]
        lean = os.environ.get("ANECHOIC_TEST_LEAN") or shutil.which("lean")
        self.assertTrue(lean, "Lean executable unavailable")
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            manifest, solution = _pins(
                work, _manifest("python trace", FIRST), SOLUTION
            )
            bad = {**solution, "sha256": "0" * 64}
            with self.assertRaises(SourceError) as caught:
                read_source(work, bad, "solution")
            result = verify_formal_chain(work, "C15", manifest, solution=bad)
        error = caught.exception
        (diagnostic,) = result["diagnostics"]
        self.assertEqual("incomplete", result["outcome"])
        self.assertEqual(
            (error.source, error.field),
            (diagnostic["source"], diagnostic["field"]),
        )
        self.assertEqual((bad, "sha256"), (error.source, error.field))
        self.assertNotEqual(
            (error.source, error.field), (manifest, diagnostic["field"])
        )
        self.assertNotEqual(
            (error.source, error.field), (diagnostic["source"], "source_pin")
        )
        self.assertEqual(error.role, diagnostic["role"])
        self.assertEqual(str(error), diagnostic["message"])
        reported = bool(result["diagnostics"])
        failure = result["outcome"] == "incomplete"
        values = [(reported, failure), (False, failure), (reported, False)]
        checks = ", ".join(
            f"{{ProgrammaticFailures.conforms .response true {str(d).lower()} "
            f"{str(f).lower()} false}}"
            for d, f in values
        )
        program = claim + f'\n#eval IO.println s!"[{checks}]"\n'
        self.assertEqual([True, False, False], run_lean_json(program, lean))

    def test_single_outcome_receipt_names_its_implicit_action(self):
        lean = os.environ.get("ANECHOIC_TEST_LEAN") or shutil.which("lean")
        self.assertTrue(lean, "Lean executable unavailable")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pins = _pins(root, _manifest("python trace", FIRST), SOLUTION)
            evidence = verify_formal_chain(root, "C15", *pins, lean=lean)[
                "evidence"
            ]
        self.assertEqual("compile", evidence["action"])
        facts = {
            fact["key"]: (fact.get("action"), fact.get("output"))
            for fact in evidence["coverage"]
            if fact["direction"] == "manifest_solution"
        }
        self.assertEqual(("compile", "python"), facts["must_effect"])
        self.assertEqual(("compile", "python"), facts["terminal_output"])

    def test_receipts_replay_and_failures_have_no_receipt(self):
        lean = os.environ.get("ANECHOIC_TEST_LEAN") or shutil.which("lean")
        self.assertTrue(lean, "Lean executable unavailable")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pins = _pins(
                root, _manifest("python trace", FIRST, SECOND), SOLUTION
            )
            model_pins = set()
            for expected in ("matched", "conflicting"):
                result = verify_formal_chain(
                    root, "C15", *pins, action="compile", lean=lean
                )
                self.assertEqual(expected, result["status"], result)
                evidence = result["evidence"]
                self.assertRegex(evidence["model_pin"], r"^[0-9a-f]{64}$")
                model_pins.add(evidence["model_pin"])
                self.assertTrue(evidence["validation_programs"])
                self.assertTrue(evidence["comparison_programs"])
                assert_replay(self, evidence, expected, root, lean)
                path = root / pins[1]["path"]
                path.write_text(
                    path.read_text().replace(
                        "'target': 'parser'", "'target': 'wrong'"
                    )
                )
            self.assertEqual(2, len(model_pins))
            failed = verify_formal_chain(
                root, "C15", *pins, action="compile", lean="/missing/lean"
            )
            self.assertEqual("incomplete", failed["outcome"])
            self.assertNotIn("evidence", failed)
