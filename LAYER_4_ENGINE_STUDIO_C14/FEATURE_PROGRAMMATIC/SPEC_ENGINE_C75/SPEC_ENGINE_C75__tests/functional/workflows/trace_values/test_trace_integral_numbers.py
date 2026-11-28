import os
import shutil
import unittest

from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75._package__shared import (
    compile_workflow,
)
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.\
    LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_2_SPEC_READING_C83.\
    SPECIFICATION_MODEL_C85._package__shared import (
    parse_trace_contract,
)  # fmt: skip
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.\
    LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_4_SPEC_COMPARISON_C88.\
    _package__shared import (
    compare_trace_values,
    compare_trace_workflow,
)  # fmt: skip


def _edge(target, kind, name, outcome, **detail):
    expect = {"kind": kind, "target": name, "outcome": outcome}
    if detail:
        expect["detail"] = detail
    return {"next": {"to": target, "expect": expect}}


def _bounded_workflow(early, later):
    machine = {
        "id": "write",
        "initial": "start",
        "states": {
            "start": {
                "on": _edge("gate", "effect", "draft", "done", count=early)
            },
            "gate": {"on": _edge("write", "effect", "gate", "passed")},
            "write": {
                "on": _edge("out", "effect", "draft", "done", count=later)
            },
            "out": {"on": _edge("end", "output", "result", "done")},
            "end": {"type": "final"},
        },
    }
    return {"action": "write", **compile_workflow(machine)["model"]}


class IntegralTraceNumbersTests(unittest.TestCase):
    def setUp(self):
        self.lean = os.environ.get("ANECHOIC_TEST_LEAN") or shutil.which(
            "lean"
        )
        self.assertTrue(self.lean, "Lean executable unavailable")

    def test_earlier_bounded_effect(self):
        contract = parse_trace_contract(
            "declare_trace_contract(action='write', output='done', "
            "must_effect=(('draft', 'done', {'count': {'at_most': 3}}),), "
            "must_precede=((('gate', 'passed'), "
            "('draft', 'done', {'count': {'at_most': 3}})),))"
        )
        for early, later, expected in (
            (1, 1, "conflicting"),
            (1.0, 1, "conflicting"),
            (1.5, 1.0, "matched"),
            (True, 1.0, "matched"),
            ("1", 1.0, "matched"),
            (-1.0, 1.0, "matched"),
        ):
            with self.subTest(early=early, later=later):
                workflow = _bounded_workflow(early, later)
                result = compare_trace_workflow(
                    contract, workflow, lean=self.lean
                )
                facts = {
                    fact["key"]: fact["status"] for fact in result["facts"]
                }
                self.assertEqual("matched", facts["must_effect"])
                self.assertEqual(expected, facts["must_precede"])

    def test_observed_numeric_values(self):
        values = {
            "integral": (1, 1.0, "matched", "matched"),
            "negative": (-1, -1.0, "matched", "matched"),
            "fractional": (1, 1.5, "conflicting", "conflicting"),
            "nested": ({"rows": [1]}, {"rows": [1.0]}, "matched", None),
            "boolean": (1, True, "conflicting", "conflicting"),
            "string": (1, "1", "conflicting", "conflicting"),
        }
        case = {
            "same_values": [
                (("left", field), ("right", field)) for field in values
            ],
            "value_types": [
                (("right", field), "integer")
                for field, row in values.items()
                if row[3] is not None
            ],
        }
        events = [
            {
                "event": name,
                "detail": {field: row[index] for field, row in values.items()},
            }
            for index, name in enumerate(("left", "right"))
        ]
        result = compare_trace_values(case, events, lean=self.lean)
        expected = [row[2] for row in values.values()]
        expected.extend(
            row[3] for row in values.values() if row[3] is not None
        )
        self.assertEqual(
            expected, [fact["status"] for fact in result["facts"]]
        )
