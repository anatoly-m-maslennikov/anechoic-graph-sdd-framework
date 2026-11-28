"""Trace specification test cases."""

import os
import shutil

from ....._package__shared import compile_workflow
from .....LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_2_SPEC_READING_C83.\
    SPECIFICATION_MODEL_C85._package__shared import (
    parse_trace_contract,
)  # fmt: skip

from ._trace_spec_support import CONTRACT, transition


class _HttpCases:
    def test_multiple_outcomes_require_the_same_endpoint(self):
        # fmt: off
        from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.\
            LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_2_SPEC_READING_C83.\
            SPECIFICATION_MODEL_C85._package__shared import (
            _contract_operations,
        )
        # fmt: on

        binding = (
            ", interface='api', transport='http', "
            "route='POST /db', operation='query')"
        )
        ready = CONTRACT[:-1] + binding
        failed = (
            "declare_trace_contract(action='admit', output='failed', "
            "forbid_effect=('kernel',)" + binding
        )
        claims = [("python trace", ready), ("python trace", failed)]

        profile = _contract_operations(claims)
        self.assertEqual("POST /db", profile["endpoint"])
        self.assertEqual(
            ["ready", "failed"], [case["output"] for case in profile["cases"]]
        )
        for changed in (
            failed.replace("/db", "/other"),
            failed.removesuffix(binding) + ")",
        ):
            with (
                self.subTest(changed=changed),
                self.assertRaisesRegex(ValueError, "share one binding"),
            ):
                _contract_operations([claims[0], ("python trace", changed)])

    def test_binding_literals_are_all_or_none(self):
        fields = (
            ", interface='database_api', route='query', "
            "transport='http', operation='POST /database'"
        )
        self.assertEqual(
            "query",
            parse_trace_contract(CONTRACT[:-1] + fields + ")")["route_name"],
        )
        for suffix in (
            ", interface='api'",
            fields.replace("'http'", "'cli'"),
            fields.replace("'query'", "''"),
            fields.replace("'query'", "name"),
        ):
            with self.subTest(suffix=suffix), self.assertRaises(ValueError):
                parse_trace_contract(CONTRACT[:-1] + suffix + ")")

    def test_binding_comparison(self):
        # fmt: off
        from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.\
            LAYER_2_FORMAL_SPECIFICATION_C94.\
            LAYER_4_SPEC_COMPARISON_C88._package__shared import (
            _binding_directions,
        )
        # fmt: on

        lean = os.environ.get("ANECHOIC_TEST_LEAN") or shutil.which("lean")
        if lean is None:
            self.skipTest("Lean unavailable")
        contract = dict(
            interface="database_api",
            endpoint="POST /database",
            transport="http",
            route_name="query",
        )
        server = {"transport": "http", "routes": {"query": "POST /database"}}
        claims = {
            "manifest": {
                "boundaries": {"io": {"server": {"database_api": server}}}
            }
        }
        expect = self._fixture_6()
        transitions = [{"expect": expect}]
        workflow = {
            "initial": "start",
            "states": [{"name": "start", "transitions": transitions}],
        }
        sources = dict.fromkeys(("manifest", "contract", "solution"), "source")

        def statuses():
            return {
                key: value["status"]
                for key, value in _binding_directions(
                    sources, claims, contract, workflow, lean
                ).items()
            }

        self._check_binding_changes(
            statuses, server, expect, transitions, claims
        )

    def _check_binding_changes(
        self, statuses, server, expect, transitions, claims
    ):
        self.assertEqual(
            {
                "manifest_contract": "matched",
                "manifest_solution": "matched",
                "contract_solution": "matched",
            },
            statuses(),
        )
        server["routes"]["query"] = "POST /other"
        self.assertEqual("conflicting", statuses()["manifest_contract"])
        server["routes"]["query"] = "POST /database"
        expect["detail"]["operation"] = "POST /other"
        self.assertEqual("conflicting", statuses()["contract_solution"])
        expect["detail"]["operation"] = "POST /database"
        del server["routes"]["query"]
        self.assertEqual("conflicting", statuses()["manifest_contract"])
        server["routes"]["query"] = "POST /database"
        del expect["detail"]["route"]
        self.assertEqual("unresolved", statuses()["contract_solution"])
        expect["detail"]["route"] = "query"
        expect["detail"]["endpoint"] = "POST /database"
        self.assertEqual("unresolved", statuses()["contract_solution"])
        del expect["detail"]["endpoint"]
        transitions.append({"expect": {"kind": "trigger"}})
        self.assertEqual("conflicting", statuses()["contract_solution"])
        claims["manifest"]["boundaries"]["io"]["server"] = "unsupported"
        self.assertEqual("unresolved", statuses()["manifest_contract"])

    def _fixture_6(self):
        return {
            "kind": "trigger",
            "target": "database_api",
            "detail": {
                "route": "query",
                "transport": "http",
                "operation": "POST /database",
            },
        }

    def test_bound_trace_combines_endpoint_and_effect_scope(self):
        # fmt: off
        from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.\
            LAYER_2_FORMAL_SPECIFICATION_C94.\
            LAYER_4_SPEC_COMPARISON_C88._package__shared import (
            check_trace_spec,
        )
        # fmt: on

        lean = os.environ.get("ANECHOIC_TEST_LEAN") or shutil.which("lean")
        if lean is None:
            self.skipTest("Lean unavailable")
        fields = (
            ", interface='api', route='query', "
            "transport='http', operation='POST /db'"
        )
        contract = parse_trace_contract(CONTRACT[:-1] + fields + ")")
        trigger = transition("seen", "trigger", "api")
        trigger["guard"]["params"]["detail"] = {
            "route": "query",
            "transport": "http",
            "operation": "POST /db",
        }
        machine = self._fixture_7(trigger)
        workflow = {"action": "admit", **compile_workflow(machine)["model"]}
        manifest = self._fixture_8()
        model = {
            role: {"source": role, "claims": []}
            for role in ("manifest", "contract", "solution")
        }
        model["contract"]["claims"] = [("python trace", "")]
        model["solution"]["claims"] = [("python", "")]
        compiled = self._fixture_9(contract, manifest, workflow)
        self._check_bound_trace(
            model, compiled, workflow, lean, check_trace_spec
        )

    def _check_bound_trace(
        self, model, compiled, workflow, lean, check_trace_spec
    ):
        from unittest.mock import patch

        with (
            patch(
                "FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75."
                "LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_2_SPEC_READING_C83."
                "_package__shared.load_boundary_model",
                return_value=model,
            ),
            patch(
                "FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75."
                "LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_3_LEAN_TRANSLATOR_C84."
                "_package__shared.compile_lean",
                return_value=compiled,
            ),
        ):
            report = check_trace_spec(None, "C1", None, None, None, lean=lean)
            self.assertEqual("matched", report["status"])
            workflow["states"][1]["transitions"][0]["expect"]["target"] = (
                "wrong"
            )
            report = check_trace_spec(None, "C1", None, None, None, lean=lean)
            self.assertEqual(
                "conflicting",
                report["directions"]["contract_solution"]["status"],
            )

    def _fixture_9(self, contract, manifest, workflow):
        return {
            "claims": {
                "manifest": manifest,
                "contract": contract,
                "solution": workflow,
            },
            "issues": [],
            "unresolved": [],
        }

    def _fixture_8(self):
        return {
            "boundaries": {
                "io": {
                    "server": {
                        "api": {
                            "transport": "http",
                            "routes": {"query": "POST /db"},
                        }
                    }
                }
            }
        }

    def _fixture_7(self, trigger):
        return {
            "id": "admit",
            "initial": "start",
            "states": {
                "start": {"on": {"trigger": trigger}},
                "seen": {
                    "on": {
                        "effect": transition(
                            "returning", "effect", "kernel", "ready"
                        )
                    }
                },
                "returning": {
                    "on": {
                        "output": transition("done", "output", outcome="ready")
                    }
                },
                "done": {"type": "final"},
            },
        }
