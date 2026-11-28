import os
import unittest
from unittest.mock import patch

from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75._package__shared import (
    verify_formal_chain,
)
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.\
    LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_4_SPEC_COMPARISON_C88.\
    _package__shared import (
    check_trace_spec,
    compare_obligations,
)  # fmt: skip

LEAN = (
    os.environ.get("ANECHOIC_TEST_LEAN")
    or os.environ.get("LEAN_BIN")
    or "lean"
)


def _order_edge(target, kind, observed=None, detail=None):
    params = {"kind": kind, "outcome": "done"}
    if observed is not None:
        params["target"] = observed
    if detail is not None:
        params["detail"] = {"count": detail}
    return {
        "on": {
            "step": {
                "target": target,
                "guard": {"type": "matchesTrace", "params": params},
            }
        }
    }


def _order_solution(early):
    machine = {
        "id": "m",
        "initial": "before",
        "states": {
            "before": _order_edge("gate", "effect", "write", early),
            "gate": _order_edge("after", "effect", "approve"),
            "after": _order_edge("finish", "effect", "write", 1),
            "finish": _order_edge("end", "output"),
            "end": {"type": "final"},
        },
    }
    return (
        "component_workflow(component='C52',action='invoke',"
        f"machine={machine!r})"
    )


def order_model(early):
    boundaries = {
        "io": {
            "server": {
                "invoke": {
                    "outcomes": {
                        "done": {
                            "must_effect": [["write", "done", {"count": 1}]]
                        }
                    }
                }
            }
        }
    }
    contract = (
        "declare_trace_contract(action='invoke',output='done',"
        "must_effect=(('write','done',{'count':1}),),"
        "must_precede=((('approve','done'),('write','done',{'count':1})),))"
    )
    solution = _order_solution(early)
    return {
        "component_id": "C52",
        "manifest": {
            "source": {"atom_id": "M"},
            "boundaries": boundaries,
            "fields": {
                "component_id": "C52",
                "name": "Core",
                "boundaries": boundaries,
            },
        },
        "contract": {
            "source": {"atom_id": "C"},
            "claims": [("python trace", contract)],
        },
        "solution": {
            "source": {"atom_id": "S"},
            "claims": [("python", solution)],
        },
    }


class NumericUnicodeRegressionTests(unittest.TestCase):
    def test_equivalent_number_conflicts_before_approval(self):
        for early, expected in (
            (1, "conflicting"),
            (1.0, "conflicting"),
            (True, "matched"),
            (2, "matched"),
            (1.0000000000000002, "matched"),
        ):
            with self.subTest(early=early):
                source = order_model(early)
                with patch(
                    "FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.formal_chain__pub."
                    "load_boundary_model",
                    return_value=source,
                ):
                    result = verify_formal_chain(
                        ".", "C52", {}, {}, {}, lean=LEAN
                    )
                self.assertEqual("matched", result["translation"]["status"])
                fact = next(
                    f
                    for f in result["directions"]["contract_solution"]["facts"]
                    if f["key"] == "must_precede"
                )
                self.assertEqual(expected, fact["status"])

    def test_non_printable_manifest_name_round_trips(self):
        source = order_model(2)
        source["manifest"]["fields"]["name"] = "Core\N{NO-BREAK SPACE}label"
        with patch(
            "FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.formal_chain__pub."
            "load_boundary_model",
            return_value=source,
        ):
            result = verify_formal_chain(".", "C52", {}, {}, {}, lean=LEAN)
        self.assertEqual("compared", result["outcome"])
        self.assertEqual("matched", result["translation"]["status"])
        self.assertEqual("matched", result["status"])

    def test_non_printable_obligation_compares(self):
        sources = {
            role: {"atom_id": role}
            for role in ("manifest", "contract", "solution")
        }
        obligations = {
            role: {"label": "Core\N{NO-BREAK SPACE}label"} for role in sources
        }
        result = compare_obligations(sources, obligations, lean=LEAN)
        self.assertEqual("matched", result["status"])

    def test_surrogate_effect_cannot_match_a_null_scalar(self):
        source = order_model(2)
        name = "write\x00"
        source["manifest"]["boundaries"]["io"]["server"]["invoke"]["outcomes"][
            "done"
        ]["must_effect"][0][0] = name
        language, contract = source["contract"]["claims"][0]
        source["contract"]["claims"][0] = (
            language,
            contract.replace("'write'", repr(name)),
        )
        language, workflow = source["solution"]["claims"][0]
        loader = (
            "FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75."
            "LAYER_2_FORMAL_SPECIFICATION_C94."
            "LAYER_2_SPEC_READING_C83._package__shared.load_boundary_model"
        )
        with patch(loader, return_value=source):
            source["solution"]["claims"][0] = (
                language,
                workflow.replace("'write'", repr(name)),
            )
            self.assertEqual(
                "matched",
                check_trace_spec(".", "C52", {}, {}, {}, lean=LEAN)["status"],
            )
            source["solution"]["claims"][0] = (
                language,
                workflow.replace("'write'", repr("write\ud800")),
            )
            with self.assertRaisesRegex(ValueError, "Unicode scalar values"):
                check_trace_spec(".", "C52", {}, {}, {}, lean=LEAN)
