"""Trace specification test cases."""

import os
import shutil

from ....._package__shared import compile_workflow
from .....LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_4_SPEC_COMPARISON_C88.\
    _package__shared import compare_trace_workflow  # fmt: skip
from .....LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_2_SPEC_READING_C83.\
    SPECIFICATION_MODEL_C85._package__shared import (
    parse_trace_contract,
)  # fmt: skip

from ._trace_spec_support import CONTRACT, transition


class _TraceRejectionCases:
    def test_contract_rejects_bad_literals(self):
        for effects in (
            "()",
            "(('kernel', ''),)",
            "(('a', 'b'), ('a', 'b'))",
            "[('a', 'b')]",
            "(('a', x),)",
        ):
            with self.subTest(effects=effects), self.assertRaises(ValueError):
                parse_trace_contract(
                    CONTRACT.replace("(('kernel', 'ready'),)", effects)
                )

    def test_lean_detects_bypass_and_missing_output(self):
        lean = os.environ.get("ANECHOIC_TEST_LEAN") or shutil.which("lean")
        if lean is None:
            self.skipTest("Lean unavailable")
        machine = self._fixture_4()
        contract = parse_trace_contract(CONTRACT)

        def compare():
            return compare_trace_workflow(
                contract,
                {"action": "admit", **compile_workflow(machine)["model"]},
                lean=lean,
            )

        self.assertEqual("matched", compare()["status"])
        machine["states"]["start"]["on"]["bypass"] = transition(
            "seen", "trigger"
        )
        self.assertEqual("conflicting", compare()["status"])
        machine["states"]["start"]["on"]["bypass"] = transition(
            "done", "output"
        )
        self.assertEqual("conflicting", compare()["status"])
        machine["states"]["start"]["on"]["bypass"] = transition(
            "done", "output", outcome=""
        )
        result = compare()
        self.assertEqual("matched", result["facts"][1]["status"])
        self.assertEqual("unresolved", result["status"])
        del machine["states"]["start"]["on"]["bypass"]
        machine["states"]["seen"]["on"]["output"]["guard"]["params"][
            "outcome"
        ] = "other"
        self.assertEqual("unresolved", compare()["status"])

    def _fixture_4(self):
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

    def test_forbidden_effect_contract_literals_and_cli(self):
        # fmt: off
        from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.\
            LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_2_SPEC_READING_C83.\
            SPECIFICATION_MODEL_C85._package__shared import (
            parse_cli_contract,
        )
        # fmt: on

        prefix = (
            "declare_trace_contract(action='admit', "
            "output='ready', forbid_effect="
        )
        for value in (
            "()",
            "['state']",
            "('',)",
            "('state', 'state')",
            "(target,)",
        ):
            with self.subTest(value=value), self.assertRaises(ValueError):
                parse_trace_contract(prefix + value + ")")
        self.assertEqual(
            ["state"],
            parse_trace_contract(prefix + "('state',))")["forbid_effect"],
        )
        both = parse_trace_contract(
            CONTRACT[:-1] + ", forbid_effect=('state',))"
        )
        self.assertIn("must_effect", both)
        self.assertIn("forbid_effect", both)
        cli = (
            "declare_cli_contract(interface='i', "
            "action='admit', runner='r', path='p', "
        )
        self.assertEqual(
            ["state"],
            parse_cli_contract(
                cli + "output='ready', forbid_effect=('state',))"
            )["trace"]["forbid_effect"],
        )
        for fields in ("output='ready'", "forbid_effect=('state',)"):
            with self.assertRaises(ValueError):
                parse_cli_contract(cli + fields + ")")

    def test_trace_rejects_contradictory_effects(self):
        with self.assertRaisesRegex(
            ValueError, "required and forbidden effects contradict"
        ):
            parse_trace_contract(
                CONTRACT[:-1] + ", forbid_effect=('kernel',))"
            )
        suffix = (
            ", must_precede=((('gate', 'passed'), "
            "('kernel', 'ready')),), forbid_effect=('gate',))"
        )
        with self.assertRaisesRegex(
            ValueError, "required and forbidden effects contradict"
        ):
            parse_trace_contract(CONTRACT[:-1] + suffix)

    def test_forbidden_effect_paths(self):
        lean = os.environ.get("ANECHOIC_TEST_LEAN") or shutil.which("lean")
        if lean is None:
            self.skipTest("Lean unavailable")
        contract = parse_trace_contract(
            "declare_trace_contract(action='admit', output='dry', "
            "forbid_effect=('service_state',))"
        )
        machine = self._fixture_5()

        def status():
            workflow = {
                "action": "admit",
                **compile_workflow(machine)["model"],
            }
            return compare_trace_workflow(contract, workflow, lean=lean)[
                "facts"
            ][1]["status"]

        self.assertEqual("matched", status())
        output = machine["states"]["applied"]["on"]["output"]["guard"][
            "params"
        ]
        output["outcome"] = "dry"
        self.assertEqual("conflicting", status())
        del output["outcome"]
        self.assertEqual("conflicting", status())
        effect = machine["states"]["start"]["on"]["apply"]["guard"]["params"]
        del effect["target"]
        self.assertEqual("conflicting", status())
        effect["target"] = ""
        self.assertEqual("matched", status())
        machine["states"]["start"]["on"]["dry"]["guard"]["params"][
            "outcome"
        ] = None
        self.assertEqual("unresolved", status())

    def _fixture_5(self):
        return {
            "id": "admit",
            "initial": "start",
            "states": {
                "start": {
                    "on": {
                        "dry": transition("done", "output", outcome="dry"),
                        "apply": transition(
                            "applied", "effect", "service_state"
                        ),
                    }
                },
                "applied": {
                    "on": {
                        "output": transition("done", "output", outcome="apply")
                    }
                },
                "done": {"type": "final"},
            },
        }
