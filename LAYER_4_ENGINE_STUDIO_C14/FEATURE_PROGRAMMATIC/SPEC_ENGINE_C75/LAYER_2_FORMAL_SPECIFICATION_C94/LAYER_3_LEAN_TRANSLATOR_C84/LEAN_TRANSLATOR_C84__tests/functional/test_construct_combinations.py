import itertools
from importlib import import_module
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75._package__shared import (
    compile_workflow,
)

_FORMAL = (
    "FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94."
)
parse_trace_contract = import_module(
    _FORMAL + "LAYER_2_SPEC_READING_C83.SPECIFICATION_MODEL_C85."
    "_package__shared"
).parse_trace_contract
_lean = import_module(_FORMAL + "LAYER_3_LEAN_TRANSLATOR_C84._package__shared")
_program = _lean._program
run_lean_json = _lean.run_lean_json


LEAN_NUMBERS = (
    "\n"
    'example : detailImplies "1.0" "1" = true := by '
    "native_decide\n"
    'example : detailImplies "-1.0" "-1" = true := by '
    "native_decide\n"
    'example : detailImplies "true" "1" = false := by '
    "native_decide\n"
    'example : detailImplies "1.00000000000000000001" "1" = '
    "false := by native_decide\n"
    'example : detailImplies "9007199254740992.0" '
    '"9007199254740993" = false := by native_decide\n'
    'example : detailImplies "1" "{\\"at_most\\":2}" = true := '
    "by native_decide\n"
    'example : detailImplies "1.0" "{\\"at_most\\":2}" = true '
    ":= by native_decide\n"
    'example : detailImplies "10e-1" "{\\"at_most\\":2}" = true '
    ":= by native_decide\n"
    'example : detailImplies "1.5" "{\\"at_most\\":2}" = false '
    ":= by native_decide\n"
    'example : detailImplies "3" "{\\"at_most\\":2}" = false := '
    "by native_decide\n"
    'example : detailImplies "-1" "{\\"at_most\\":2}" = false '
    ":= by native_decide\n"
    'example : detailImplies "true" "{\\"at_most\\":2}" = false '
    ":= by native_decide\n"
    'example : detailImplies "{\\"at_most\\":1}" '
    '"{\\"at_most\\":2}" = true := by native_decide\n'
)


def transition(target, kind, observed=None, outcome=None, detail=None):
    params = {"kind": kind, "target": observed, "outcome": outcome}
    if detail is not None:
        params["detail"] = detail
    return {
        "target": target,
        "guard": {"type": "matchesTrace", "params": params},
    }


def workflow(first, second, alternate=None):
    states = {
        "start": {"on": {"first": first}},
        "middle": {"on": {"second": second}},
        "end": {
            "on": {"output": transition("done", "output", outcome="ready")}
        },
        "done": {"type": "final"},
    }
    if alternate:
        states["start"]["on"]["alternate"] = transition(
            "done", "output", outcome=alternate
        )
    return {
        "action": "run",
        **compile_workflow(
            {"id": "run", "initial": "start", "states": states}
        )["model"],
    }


def add_order_cases(programs, expected):
    contract = parse_trace_contract(
        "declare_trace_contract(action='run', output='ready', "
        "must_effect=(('convert', 'done', {'version': 'current'}),), "
        "must_precede=((('convert', 'done', {'version': 'old'}), "
        "('convert', 'done', {'version': 'current'})),))"
    )
    for first, second in itertools.product(("old", "current"), repeat=2):
        first_edge = transition(
            "middle", "effect", "convert", "done", {"version": first}
        )
        second_edge = transition(
            "end", "effect", "convert", "done", {"version": second}
        )
        programs.append(_program(contract, workflow(first_edge, second_edge)))
        effect = "matched" if "current" in (first, second) else "conflicting"
        order = (
            "matched"
            if (first, second) in (("old", "old"), ("old", "current"))
            else "conflicting"
        )
        expected.append(["matched", effect, order, "matched"])


def add_bound_cases(programs, expected):
    bound = parse_trace_contract(
        "declare_trace_contract(action='run', output='ready', "
        "must_effect=(('query', 'done', {'rows': {'at_most': 2}}),))"
    )
    for rows, alternate in itertools.product(
        (2, 3), (None, "failed", "ready")
    ):
        first_edge = transition(
            "middle", "effect", "query", "done", {"rows": rows}
        )
        second_edge = transition("end", "trigger")
        programs.append(
            _program(bound, workflow(first_edge, second_edge, alternate))
        )
        expected.append(
            [
                "matched",
                "matched"
                if rows <= 2 and alternate != "ready"
                else "conflicting",
                "matched",
            ]
        )


class ConstructCombinationTests(unittest.TestCase):
    def test_lean_evaluation_rejects_non_json_numeric_constants(self):
        lean = (
            os.environ.get("ANECHOIC_TEST_LEAN")
            or os.environ.get("LEAN_BIN")
            or shutil.which("lean")
        )
        self.assertTrue(
            lean, "Set ANECHOIC_TEST_LEAN or LEAN_BIN, or put lean on PATH"
        )
        for token in ("NaN", "Infinity", "-Infinity"):
            with (
                self.subTest(token=token),
                self.assertRaisesRegex(ValueError, "invalid Lean output"),
            ):
                run_lean_json(f'#eval IO.println "[{token}]"', lean)
        self.assertEqual(
            [0, 2.5, "NaN", None],
            run_lean_json('#eval IO.println r#"[0,2.5,"NaN",null]"#', lean),
        )

    def test_history_sensitive_comparison_is_unresolved(self):
        lean = (
            os.environ.get("ANECHOIC_TEST_LEAN")
            or os.environ.get("LEAN_BIN")
            or shutil.which("lean")
        )
        self.assertTrue(
            lean, "Set ANECHOIC_TEST_LEAN or LEAN_BIN, or put lean on PATH"
        )
        contract = {
            "action": "run",
            "output": "ready",
            "must_effect": [("query", "done")],
            "forbid_effect": ["publish"],
            "must_precede": [(("query", "done"), ("show", "done"))],
        }
        first = transition("middle", "effect", "query", "done")
        second = transition("end", "effect", "show", "done")
        first["guard"]["params"]["bind"] = {"request": "request_id"}
        second["guard"]["params"]["same_as"] = {"reply_id": "request"}
        program = _program(contract, workflow(first, second))
        self.assertEqual(
            ["matched"] + ["unresolved"] * 4, run_lean_json(program, lean)
        )

    def test_json_number_equality_and_bounds(self):
        lean = (
            os.environ.get("ANECHOIC_TEST_LEAN")
            or os.environ.get("LEAN_BIN")
            or shutil.which("lean")
        )
        self.assertTrue(
            lean, "Set ANECHOIC_TEST_LEAN or LEAN_BIN, or put lean on PATH"
        )
        contract = parse_trace_contract(
            "declare_trace_contract(action='run', output='ready', "
            "must_effect=(('query', 'done'),))"
        )
        first = transition("middle", "effect", "query", "done")
        second = transition("end", "trigger")
        program = _program(contract, workflow(first, second)) + LEAN_NUMBERS
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "Numbers.lean"
            path.write_text(program)
            result = subprocess.run(
                [lean, str(path)],
                capture_output=True,
                text=True,
                timeout=45,
                check=False,
            )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_generated_trace_combinations(self):
        lean = (
            os.environ.get("ANECHOIC_TEST_LEAN")
            or os.environ.get("LEAN_BIN")
            or shutil.which("lean")
        )
        self.assertTrue(
            lean, "Set ANECHOIC_TEST_LEAN or LEAN_BIN, or put lean on PATH"
        )
        programs, expected = [], []
        add_order_cases(programs, expected)
        add_bound_cases(programs, expected)

        source = "import Lean\n" + "\n".join(
            f"namespace Case{i}\n{program[12:]}\nend Case{i}"
            for i, program in enumerate(programs)
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "Combinations.lean"
            path.write_text(source, encoding="utf-8")
            result = subprocess.run(
                [lean, str(path)],
                capture_output=True,
                text=True,
                timeout=45,
                check=False,
            )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual(
            expected, [json.loads(line) for line in result.stdout.splitlines()]
        )
