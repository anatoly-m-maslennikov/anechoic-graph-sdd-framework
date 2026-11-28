"""Trace specification test cases."""

import os
import shutil

from ....._package__shared import compile_workflow
from .....LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_4_SPEC_COMPARISON_C88.\
    _package__shared import compare_trace_workflow  # fmt: skip

from ._trace_spec_support import transition


class _TraceImplicationCases:
    def test_upper_bound_implication(self):
        lean = os.environ.get("ANECHOIC_TEST_LEAN") or shutil.which("lean")
        if lean is None:
            self.skipTest("Lean unavailable")
        contract = {
            "action": "admit",
            "output": "ready",
            "must_effect": [
                (
                    "query_retained",
                    "observed",
                    {
                        "rows": {"at_most": 45},
                        "serialized_bytes": {"at_most": 300},
                    },
                )
            ],
        }
        machine = self._fixture_1()
        params = machine["states"]["start"]["on"]["effect"]["guard"]["params"]

        def status(detail):
            params["detail"] = detail
            workflow = {"action": "admit"}
            workflow.update(compile_workflow(machine)["model"])
            return compare_trace_workflow(contract, workflow, lean=lean)[
                "facts"
            ][1]["status"]

        for detail in (
            {"rows": 45, "serialized_bytes": 300},
            {"rows": {"at_most": 40}, "serialized_bytes": {"at_most": 299}},
        ):
            self.assertEqual("matched", status(detail))
        for detail in (
            {"rows": 46, "serialized_bytes": 300},
            {"rows": True, "serialized_bytes": 300},
            {"rows": {"at_most": 46}, "serialized_bytes": 300},
            {"rows": {"at_most": 40, "extra": 1}, "serialized_bytes": 300},
            {"rows": 45},
        ):
            self.assertEqual("conflicting", status(detail))

    def _fixture_1(self):
        return {
            "id": "admit",
            "initial": "start",
            "states": {
                "start": {
                    "on": {
                        "effect": transition(
                            "seen", "effect", "query_retained", "observed"
                        )
                    }
                },
                "seen": {
                    "on": {
                        "output": transition("done", "output", outcome="ready")
                    }
                },
                "done": {"type": "final"},
            },
        }

    def test_effect_details_and_manifest_implication(self):
        lean = os.environ.get("ANECHOIC_TEST_LEAN") or shutil.which("lean")
        if lean is None:
            self.skipTest("Lean unavailable")
        effect = (
            "database",
            "queried",
            {"sql": "current", "limit": 1, "enabled": True, "unused": None},
        )
        contract = {
            "action": "admit",
            "output": "ready",
            "must_effect": [effect],
        }
        machine = self._fixture_2()
        detail = machine["states"]["start"]["on"]["effect"]["guard"]["params"][
            "detail"
        ] = dict(effect[2], extra="ok")

        def status():
            workflow = {"action": "admit"}
            workflow.update(compile_workflow(machine)["model"])
            return compare_trace_workflow(contract, workflow, lean=lean)[
                "facts"
            ][1]["status"]

        self.assertEqual("matched", status())
        for key, wrong in [
            ("sql", "previous"),
            ("limit", True),
            ("enabled", 1),
            ("unused", "null"),
        ]:
            old, detail[key] = detail[key], wrong
            self.assertEqual("conflicting", status())
            detail[key] = old
        del detail["sql"]
        self.assertEqual("conflicting", status())
        detail["sql"] = "\ud800"
        effect[2]["sql"] = "\ufffd"
        self.assertEqual("conflicting", status())
        effect[2]["sql"] = "current"
        self._check_manifest_contract(contract, lean)

    def _check_manifest_contract(self, contract, lean):
        # fmt: off
        from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.\
            LAYER_2_FORMAL_SPECIFICATION_C94.\
            LAYER_4_SPEC_COMPARISON_C88._package__shared import (
            _manifest_contract,
        )
        # fmt: on
        manifest = {
            "action": "admit",
            "output": "ready",
            "must_effect": [("database", "queried", {"sql": "current"})],
        }
        self.assertEqual(
            "matched", _manifest_contract([manifest], contract, lean)["status"]
        )
        manifest["must_effect"][0][2]["limit"] = True
        self.assertEqual(
            "conflicting",
            _manifest_contract([manifest], contract, lean)["status"],
        )
        manifest["must_effect"] = [["database", "queried"]]
        self.assertEqual(
            "matched", _manifest_contract([manifest], contract, lean)["status"]
        )
        # fmt: off
        from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.\
            LAYER_2_FORMAL_SPECIFICATION_C94.\
            LAYER_4_SPEC_COMPARISON_C88.DELEGATION_VERIFICATION_C89.\
            _package__shared import (
            _declared_outcome,
        )
        # fmt: on

        required = {
            "action": "admit",
            "output": "ready",
            "effect": ("database", "queried"),
        }
        self.assertEqual(
            required["effect"],
            _declared_outcome([contract], required)["effect"],
        )

    def _fixture_2(self):
        return {
            "id": "admit",
            "initial": "start",
            "states": {
                "start": {
                    "on": {
                        "effect": transition(
                            "seen", "effect", "database", "queried"
                        )
                    }
                },
                "seen": {
                    "on": {
                        "output": transition("done", "output", outcome="ready")
                    }
                },
                "done": {"type": "final"},
            },
        }

    def test_terminal_output_coverage_is_separate_from_case_effects(self):
        lean = os.environ.get("ANECHOIC_TEST_LEAN") or shutil.which("lean")
        if lean is None:
            self.skipTest("Lean unavailable")
        contract = {
            "action": "admit",
            "output": "ready",
            "must_effect": [("kernel", "ready")],
        }
        machine = self._fixture_3()

        def facts():
            workflow = {"action": "admit"}
            workflow.update(compile_workflow(machine)["model"])
            return {
                fact["key"]: fact["status"]
                for fact in compare_trace_workflow(
                    contract, workflow, lean=lean
                )["facts"]
            }

        machine["states"]["start"]["on"]["silent"] = transition(
            "done", "effect", "other", "done"
        )
        self.assertEqual(
            {
                "action": "matched",
                "must_effect": "matched",
                "terminal_output": "conflicting",
            },
            facts(),
        )
        machine["states"]["start"]["on"]["silent"] = transition(
            "done", "output", outcome="other"
        )
        self.assertEqual("matched", facts()["terminal_output"])
        machine["states"]["start"]["on"]["silent"] = transition(
            "done", "output"
        )
        self.assertEqual("unresolved", facts()["terminal_output"])
        machine["states"]["start"]["on"]["silent"] = transition(
            "done", "output", outcome="  "
        )
        self.assertEqual("unresolved", facts()["terminal_output"])
        machine["states"] = {"start": {"type": "final"}}
        self.assertEqual("conflicting", facts()["terminal_output"])

    def _fixture_3(self):
        return {
            "id": "admit",
            "initial": "start",
            "states": {
                "start": {
                    "on": {
                        "effect": transition(
                            "seen", "effect", "kernel", "ready"
                        )
                    }
                },
                "seen": {
                    "on": {
                        "output": transition("done", "output", outcome="ready")
                    }
                },
                "done": {"type": "final"},
            },
        }
