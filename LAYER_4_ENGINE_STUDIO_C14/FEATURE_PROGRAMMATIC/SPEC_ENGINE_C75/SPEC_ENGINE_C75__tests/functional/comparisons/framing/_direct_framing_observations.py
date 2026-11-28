"""Framing projections and comparison evidence test cases."""

from importlib import import_module
from unittest.mock import patch
import tempfile
from pathlib import Path

from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75._package__shared import (
    verify_formal_chain,
)
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.\
    LAYER_3_LEAN_TRANSLATOR_C84._package__shared import (
    compile_lean,
    run_lean_json,
)  # fmt: skip

from ..chain.test_direct_manifest_chain import _manifest, _pins


CONTRACT = (
    "declare_framing_contract(delimiter=[35], line_endings=[[10], [13, 10]])"
)
SOLUTION = (
    "declare_framing_solution(opening_prefixes=[[35, 10], [35, 13, 10]], "
    "closing_prefixes=[[10, 35, 10], [10, 35, 13, 10], "
    "[13, 10, 35, 10], [13, 10, 35, 13, 10]])"
)


def framing_pins(root, solution=SOLUTION):
    boundaries = (
        "{'code': {'exports': {'api.read': 'public'}}, "
        "'state': {'reads': ['disk'], 'writes': []}}"
    )
    pins = _pins(
        root,
        _manifest("python framing", CONTRACT, boundaries=boundaries),
        solution,
    )
    path = root / pins[1]["path"]
    path.write_text(
        path.read_text().replace("```python\n", "```python framing\n")
    )
    return pins


_TRANSLATION_VALIDATOR = (
    "FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75."
    "LAYER_2_FORMAL_SPECIFICATION_C94."
    "LAYER_4_TRANSLATION_VALIDATOR_C86.translation_validation__pub"
)


def _replace_observation(program, field, replacement):
    original = next(
        line
        for line in program.splitlines()
        if line.startswith(f'    ("{field}",')
    )
    closing = ")," if field == "bounds" else ")]"
    changed = program.replace(
        original,
        f'    ("{field}", Lean.toJson ({field}.map fun _ => '
        f"{replacement}){closing}",
        1,
    )
    return changed


class FramingObservationCases:
    def test_checks_binary_bodies_and_retains_other_coverage_gaps(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = verify_formal_chain(
                root, "C15", *framing_pins(root), lean=self.lean
            )
        self.assertEqual(
            "compared", result["outcome"], result.get("diagnostics")
        )
        self.assertEqual("bounded_match", result["status"])
        self.assertIn("namespace CarrierBodySolution", result["lean"])
        validation = result["translation"]
        self.assertEqual("bounded_match", validation["status"])
        fields = {gap["field"] for gap in validation["coverage_unresolved"]}
        self.assertEqual(
            {
                "boundaries.state",
                "boundaries.code.exports",
                "contract",
                "solution",
            },
            fields,
        )
        cases = {bytes(row["input"]): row for row in result["cases"]}
        for raw, expected in [
            (b"", {"bounds": None, "body": None}),
            (b"#\n#", {"bounds": None, "body": None}),
            (b"#\n#\n\x00\xff", {"bounds": [2, 1, 4], "body": [0, 255]}),
            (b"#\r\n#\r\n\x00\xff", {"bounds": [3, 2, 6], "body": [0, 255]}),
        ]:
            self.assertEqual(expected, cases[raw]["manifest"])
            self.assertEqual(expected, cases[raw]["solution"])

    def test_mismatch_reports_acceptance_and_body_witnesses(self):
        solution = SOLUTION.replace("[13, 10, 35, 13, 10]", "[13, 10, 35, 13]")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = verify_formal_chain(
                root, "C15", *framing_pins(root, solution), lean=self.lean
            )
        self.assertEqual("conflicting", result["status"])
        self.assertEqual("bounded_match", result["translation"]["status"])
        mismatches = result["directions"]["manifest_solution"]["facts"]
        self.assertTrue(
            any(
                case["manifest"]["bounds"] is None
                and case["solution"]["bounds"]
                for case in mismatches
            )
        )
        self.assertTrue(
            any(
                case["manifest"]["body"] == [0, 255]
                and case["solution"]["body"] == [10, 0, 255]
                for case in mismatches
            )
        )

    def test_rejects_a_changed_validated_framing_result(self):
        chain = import_module(verify_formal_chain.__module__)
        original = chain.validate_translation

        def changed(*args, **kwargs):
            result = original(*args, **kwargs)
            result["framing_comparison"]["cases"] = []
            return result

        with (
            tempfile.TemporaryDirectory() as directory,
            patch.object(chain, "validate_translation", side_effect=changed),
        ):
            root = Path(directory)
            result = verify_formal_chain(
                root,
                "C15",
                *framing_pins(root),
                action="framing",
                lean=self.lean,
            )
        self.assertEqual("incomplete", result["outcome"])
        self.assertIn(
            "Framing comparison identity", result["diagnostics"][0]["message"]
        )

    def test_rejects_malformed_framing_observations_even_when_roles_agree(
        self,
    ):
        for field, replacement in (
            ("bounds", "([0, 1] : List Nat)"),
            ("body", '"not bytes"'),
            ("body", "([256] : List Nat)"),
            ("body", "([42] : List Nat)"),
            ("body", "Lean.Json.null"),
        ):
            with self.subTest(field=field, replacement=replacement):

                def malformed(
                    program,
                    *args,
                    field=field,
                    replacement=replacement,
                    **kwargs,
                ):
                    changed = _replace_observation(program, field, replacement)
                    return run_lean_json(changed, *args, **kwargs)

                with (
                    tempfile.TemporaryDirectory() as directory,
                    patch(
                        _TRANSLATION_VALIDATOR + ".run_lean_json",
                        side_effect=malformed,
                    ),
                ):
                    root = Path(directory)
                    report = verify_formal_chain(
                        root, "C15", *framing_pins(root), lean=self.lean
                    )
                self.assertEqual("incomplete", report["outcome"])
                self.assertEqual(
                    "translation", report["diagnostics"][0]["field"]
                )
                self.assertEqual(
                    "Unexpected Lean framing comparison output",
                    report["diagnostics"][0]["message"],
                )

    def test_rejects_framing_observations_that_hide_a_role_mismatch(self):

        def copied_projection(program, *args, **kwargs):
            compared = (
                "manifestBounds == solutionBounds && "
                "manifestBody == solutionBody"
            )
            equality = f"Lean.toJson ({compared})"
            projection = "framingResult solutionBounds solutionBody"
            self.assertEqual(1, program.count(equality))
            self.assertEqual(1, program.count(projection))
            changed = program.replace(
                equality, f"Lean.toJson (true || ({compared}))"
            )
            changed = changed.replace(
                projection, "framingResult manifestBounds manifestBody"
            )
            return run_lean_json(changed, *args, **kwargs)

        solution = SOLUTION.replace("[13, 10, 35, 13, 10]", "[13, 10, 35, 13]")
        with (
            tempfile.TemporaryDirectory() as directory,
            patch(
                _TRANSLATION_VALIDATOR + ".run_lean_json",
                side_effect=copied_projection,
            ),
        ):
            root = Path(directory)
            result = verify_formal_chain(
                root, "C15", *framing_pins(root, solution), lean=self.lean
            )
        self.assertEqual("incomplete", result["outcome"])
        (diagnostic,) = result["diagnostics"]
        self.assertEqual("translation", diagnostic["field"])
        self.assertEqual(
            "Unexpected Lean framing comparison output", diagnostic["message"]
        )

    def test_changed_lean_cannot_produce_a_comparison(self):
        def changed(model):
            compiled = compile_lean(model)
            compiled["lean"] = compiled["lean"].replace(
                "some (start, close, stop)", "some (start, close, stop + 1)", 1
            )
            return compiled

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with patch(
                "FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75."
                "formal_chain__pub.compile_lean",
                side_effect=changed,
            ):
                result = verify_formal_chain(
                    root, "C15", *framing_pins(root), lean=self.lean
                )
        self.assertEqual("incomplete", result["outcome"])
        self.assertEqual("conflicting", result["translation"]["status"])
        self.assertNotIn("cases", result)
