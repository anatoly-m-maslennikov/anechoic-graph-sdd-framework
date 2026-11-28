import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from ..._package__shared import compile_lean, lean_string


CONTRACT = (
    "declare_framing_contract(delimiter=[45,45,45], "
    "line_endings=[[10],[13,10]])"
)
SOLUTION = (
    "declare_framing_solution(opening_prefixes=[[45,45,45,10],[45,45,45,1"
    "3,10]], closing_prefixes=[[10,45,45,45,10],[13,10,45,45,45,13,10],[1"
    "0,45,45,45,13,10],[13,10,45,45,45,10]])"
)
ASSERTIONS = """
example : CarrierBodyContract.body [45,45,45,10,97,10,45,45,45,10,98] =
    CarrierBodyContract.Outcome.body [98] := by decide
example : CarrierBodySolution.body [45,45,45,10,97,10,45,45,45,10,98] =
    CarrierBodySolution.Outcome.body [98] := by decide
example : CarrierBodySolution.body [97,98] =
    CarrierBodySolution.Outcome.missingDelimiter := by decide
"""


LONG_ORACLE = """
def expectedDetail : String := String.ofList (
  List.replicate 8192 'a' ++ [Char.ofNat 8205] ++ List.replicate 8192 'b')
def actualDetail : Except String Lean.Json := do
  let contract ← AnechoicSpec.contract
  let claim ← contract.getObjVal? "claim"
  let effects ← claim.getObjVal? "must_effect"
  let effect ← effects.getArrVal? 0
  let fields ← effect.getArrVal? 2
  fields.getObjVal? "detail"
#eval match actualDetail with
  | .ok value => value == Lean.Json.str expectedDetail
  | .error _ => false
"""


LITERALS_ORACLE = (
    "\n"
    "#eval match AnechoicSpec.contract, Lean.Json.parse "
    'r#"{"source":{"atom_id":"C"},"claim":{"action":"run","output":"d'
    'one","must_effect":[["store","saved",{"flag":false,"zero":0,"not'
    'hing":null,"special":"λ\\"\\\\\\n\\t"}]]}}"# with\n'
    "  | .ok actual, .ok expected => actual == expected\n"
    "  | _, _ => false\n"
)


def model(solution):
    return {
        "component_id": "C52",
        "manifest": {
            "source": {"atom_id": "M"},
            "fields": {"component_id": "C52", "name": "Core"},
            "boundaries": None,
        },
        "contract": {
            "source": {"atom_id": "C"},
            "claims": [("python framing", CONTRACT)],
        },
        "solution": {
            "source": {"atom_id": "S"},
            "claims": [("python framing", solution)],
        },
    }


class LeanTranslationTests(unittest.TestCase):
    def test_long_normalized_declaration_preserves_unicode(self):
        lean = (
            os.environ.get("ANECHOIC_TEST_LEAN")
            or os.environ.get("LEAN_BIN")
            or shutil.which("lean")
        )
        self.assertTrue(lean, "Set ANECHOIC_TEST_LEAN or LEAN_BIN")
        value = "a" * 8192 + "\u200d" + "b" * 8192
        boundary = model(SOLUTION)
        boundary["contract"]["claims"] = [
            (
                "python trace",
                (
                    'declare_trace_contract(action="run", output="done", '
                    'must_effect=(("store", "saved", {"detail": '
                    f"{value!r}"
                    "}),))"
                ),
            )
        ]
        boundary["solution"]["claims"] = []
        compiled = compile_lean(boundary)
        self.assertIn("contract", compiled["compiled_roles"])
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "LongDeclaration.lean"
            path.write_text(compiled["lean"] + LONG_ORACLE, encoding="utf-8")
            checked = subprocess.run(
                [lean, str(path)],
                capture_output=True,
                text=True,
                timeout=45,
            )
        self.assertEqual(
            0,
            checked.returncode,
            checked.stdout + checked.stderr,
        )
        self.assertEqual("true", checked.stdout.strip())

    def test_lean_string_round_trips_controls_and_escaped_sequences(self):
        lean = (
            os.environ.get("ANECHOIC_TEST_LEAN")
            or os.environ.get("LEAN_BIN")
            or shutil.which("lean")
        )
        self.assertTrue(lean, "Set ANECHOIC_TEST_LEAN or LEAN_BIN")
        controls = "".join(map(chr, (*range(32), *range(127, 160))))
        value = controls + r"a\x00\u200d\n\r\t\0\\" + '"λ\u200d\U0001f600'
        source = f"#eval ({lean_string(value)} : String).toList.map Char.toNat"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "StringRoundTrip.lean"
            path.write_text(source, encoding="utf-8")
            checked = subprocess.run(
                [lean, str(path)],
                capture_output=True,
                text=True,
                timeout=45,
            )
        self.assertEqual(
            0,
            checked.returncode,
            checked.stdout + checked.stderr,
        )
        self.assertEqual(list(map(ord, value)), json.loads(checked.stdout))

    def test_lean_string_rejects_surrogates(self):
        for surrogate in ("\ud800", "\udfff"):
            with self.assertRaisesRegex(ValueError, "Unicode scalar values"):
                lean_string("a" + surrogate + "b")

    def test_framing_semantics_and_negative_control(self):
        lean = (
            os.environ.get("ANECHOIC_TEST_LEAN")
            or os.environ.get("LEAN_BIN")
            or shutil.which("lean")
        )
        self.assertTrue(
            lean,
            (
                "Set ANECHOIC_TEST_LEAN or LEAN_BIN, or put lean on PATH to "
                "run functional tests"
            ),
        )
        valid = compile_lean(model(SOLUTION))
        changed = compile_lean(
            model(SOLUTION.replace("[10,45,45,45,10],", ""))
        )
        for result in (valid, changed):
            self.assertEqual(
                ["manifest", "contract", "solution"], result["compiled_roles"]
            )
            self.assertFalse(
                [
                    gap
                    for gap in result["unresolved"]
                    if gap["field"] in ("contract", "solution")
                ]
            )
        self._check_framing_programs(lean, valid, changed)

    def _check_framing_programs(self, lean, valid, changed):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "Translation.lean"
            for source, succeeds in (
                (valid["lean"] + ASSERTIONS, True),
                (changed["lean"], True),
                (changed["lean"] + ASSERTIONS, False),
            ):
                path.write_text(source)
                checked = subprocess.run(
                    [lean, str(path)],
                    capture_output=True,
                    text=True,
                    timeout=45,
                )
                if succeeds:
                    self.assertEqual(
                        0, checked.returncode, checked.stdout + checked.stderr
                    )
                else:
                    self.assertNotEqual(
                        0, checked.returncode, checked.stdout + checked.stderr
                    )

    def test_python_literals_survive_in_emitted_lean(self):
        lean = (
            os.environ.get("ANECHOIC_TEST_LEAN")
            or os.environ.get("LEAN_BIN")
            or shutil.which("lean")
        )
        self.assertTrue(
            lean, "Set ANECHOIC_TEST_LEAN or LEAN_BIN, or put lean on PATH"
        )
        boundary = model(SOLUTION)
        boundary["contract"]["claims"] = [
            (
                "python trace",
                (
                    "declare_trace_contract(\n"
                    "            action='run', output='done', "
                    "must_effect=(('store', 'saved',\n"
                    "            {'flag': False, 'zero': 0, 'nothing': None, "
                    "'special': 'λ\"\\\\\\n\\t'}),))"
                ),
            )
        ]
        compiled = compile_lean(boundary)
        self.assertIn("contract", compiled["compiled_roles"])
        source = compiled["lean"]
        self.assertEqual(1, source.count("false"))
        mutated = source.replace("false", "true ", 1)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "Literals.lean"
            for program, expected in ((source, "true"), (mutated, "false")):
                path.write_text(program + LITERALS_ORACLE)
                checked = subprocess.run(
                    [lean, str(path)],
                    capture_output=True,
                    text=True,
                    timeout=45,
                )
                self.assertEqual(
                    0, checked.returncode, checked.stdout + checked.stderr
                )
                self.assertEqual(expected, checked.stdout.strip())
