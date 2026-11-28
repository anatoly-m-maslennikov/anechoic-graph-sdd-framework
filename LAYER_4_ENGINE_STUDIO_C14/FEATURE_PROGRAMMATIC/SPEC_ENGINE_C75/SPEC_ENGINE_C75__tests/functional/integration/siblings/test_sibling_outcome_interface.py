import os
import shutil
import tempfile
import unittest
from pathlib import Path

# fmt: off
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.\
    LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_4_SPEC_COMPARISON_C88.\
    DELEGATION_VERIFICATION_C89._package__shared import (
    check_sibling_outcome,
)
# fmt: on
# fmt: off
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.\
    LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_4_SPEC_COMPARISON_C88.\
    DELEGATION_VERIFICATION_C89._package__shared import (
    _declares_client,
    check_sibling_binding,
)
# fmt: on
from ...contracts.cli.test_cli_spec import _carrier
from ...workflows.delegation.test_in_process_delegation import BINDING, INTERFACE, carriers
from ...workflows.delegation.test_trace_child_delegation import CONTRACT, MANIFEST, PARENT, pins

from .sibling_outcome_event_cases import SiblingOutcomeEventCases


class SiblingOutcomeInterfaceTests(
    SiblingOutcomeEventCases, unittest.TestCase
):
    def setUp(self):
        self.lean = os.environ.get("ANECHOIC_TEST_LEAN") or shutil.which(
            "lean"
        )
        if not self.lean:
            self.skipTest("Lean executable unavailable")
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        _, self.provider = pins(self.root)
        manifest = MANIFEST.replace(
            "component_id='C2'", "component_id='C3'"
        ).replace(
            "'server': {'render': {",
            "'client': {'renderer': {'component': 'C2', "
            "'interface': 'render'}, 'unrelated': "
            "{'component': 'C2'}}, 'server': {'render': {",
        )
        solution = PARENT.replace("component='C1'", "component='C3'").replace(
            "'output': 'succeeded'",
            "'output': 'succeeded', 'interface': 'render'",
        )
        self.caller = (
            _carrier(
                self.root, "AN-S-5", "component_manifest", "C1", "{}", manifest
            ),
            _carrier(
                self.root,
                "AN-S-6",
                "component_contract",
                "C3",
                "{ANSWERS: [AN-S-5]}",
                CONTRACT.replace("action='render'", "action='run'"),
            ),
            _carrier(
                self.root,
                "AN-S-7",
                "decision",
                "C3",
                "{IS_SOLUTION_FOR: [AN-S-6@1]}",
                solution,
            ),
        )

    def check(self, interface="render", *, event="render"):
        return check_sibling_outcome(
            self.root,
            self.caller,
            "C2",
            self.provider,
            event=event,
            interface=interface,
            lean=self.lean,
        )

    def test_matching_client_event_and_provider(self):
        result = self.check()
        self.assertEqual(
            {"matched"},
            {row["status"] for row in result["directions"].values()},
        )

    def test_interface_and_logical_action_have_independent_names(self):
        action = "workbench_backend_worker_status"
        interface = "workbench_api"
        manifest = self.root / self.provider[0]["path"]
        manifest.write_text(
            manifest.read_text().replace(
                "'server': {'render': {",
                f"'server': {{'{interface}': "
                f"{{'transport': 'http'}}, '{action}': {{",
            )
        )
        for pin in (self.provider[1], self.provider[2], self.caller[2]):
            path = self.root / pin["path"]
            path.write_text(
                path.read_text()
                .replace("action='render'", f"action='{action}'")
                .replace("'action': 'render'", f"'action': '{action}'")
                .replace(
                    "'interface': 'render'", f"'interface': '{interface}'"
                )
            )
        caller_manifest = self.root / self.caller[0]["path"]
        caller_manifest.write_text(
            caller_manifest.read_text().replace(
                "'interface': 'render'", f"'interface': '{interface}'"
            )
        )
        result = self.check(interface)
        self.assertEqual(
            "unresolved", result["directions"]["caller_manifest"]["status"]
        )
        self.configure_http_provider(action, interface)
        result = self.check(interface)
        self.assertEqual(
            {"matched"},
            {row["status"] for row in result["directions"].values()},
            result,
        )

    def configure_http_provider(self, action, interface):
        contract = self.root / self.provider[1]["path"]
        contract.write_text(
            contract.read_text().replace(
                f"action='{action}'",
                f"action='{action}', "
                f"interface='{interface}', transport='http', "
                "route='GET /jobs/worker-runs', operation='worker_runs'",
            )
        )
        solution = self.root / self.provider[2]["path"]
        solution.write_text(
            solution.read_text().replace(
                "'start': {'on': {'show':",
                f"'start': {{'on': {{'request': {{'target': 'running', "
                f"'guard': {{'type': 'matchesTrace', 'params': "
                f"{{'kind': 'trigger', 'target': '{interface}', "
                "'detail': {'transport': 'http', "
                "'route': 'GET /jobs/worker-runs'}}}}}}, "
                "'running': {'on': {'show':",
            )
        )

    def test_sibling_outcome_retains_non_routing_detail(self):
        caller = self.root / self.caller[2]["path"]
        caller.write_text(
            caller.read_text().replace(
                "'interface': 'render'",
                "'interface': 'render', 'model': 'wanted'",
            )
        )
        self.assertEqual(
            {"conflicting"},
            {row["status"] for row in self.check()["directions"].values()},
        )
        for pin in self.provider:
            path = self.root / pin["path"]
            body = path.read_text()
            if pin is self.provider[2]:
                body = body.replace(
                    "'outcome': 'shown'",
                    "'outcome': 'shown', 'detail': {'model': 'wanted'}",
                )
            else:
                body = body.replace(
                    "('workbench_display', 'shown')",
                    "('workbench_display', 'shown', {'model': 'wanted'})",
                )
            path.write_text(body)
        self.assertEqual(
            {"matched"},
            {row["status"] for row in self.check()["directions"].values()},
        )

    def test_explicit_provider_contract_interface_must_match(self):
        path = self.root / self.provider[1]["path"]
        path.write_text(
            path.read_text().replace(
                "action='render'",
                "action='render', interface='unrelated', "
                "transport='in_process', entry='Renderer.render'",
            )
        )
        with self.assertRaisesRegex(
            ValueError, "provider Contract does not use interface render"
        ):
            self.check()

    def test_explicit_provider_solution_interface_must_match(self):
        path = self.root / self.provider[2]["path"]
        path.write_text(
            path.read_text().replace(
                "'start': {'on': {'show':",
                "'start': {'on': {'request': {'target': 'running', "
                "'guard': {'type': 'matchesTrace', 'params': "
                "{'kind': 'trigger', 'target': 'unrelated', "
                "'detail': {'transport': 'in_process', "
                "'entry': 'Renderer.render'}}}}}}, "
                "'running': {'on': {'show':",
            )
        )
        with self.assertRaisesRegex(
            ValueError, "provider Solution does not use interface render"
        ):
            self.check()

    def test_matching_explicit_provider_interfaces(self):
        contract = self.root / self.provider[1]["path"]
        contract.write_text(
            contract.read_text().replace(
                "action='render'",
                "action='render', interface='render', "
                "transport='in_process', entry='Renderer.render'",
            )
        )
        solution = self.root / self.provider[2]["path"]
        solution.write_text(
            solution.read_text().replace(
                "'start': {'on': {'show':",
                "'start': {'on': {'request': {'target': 'running', "
                "'guard': {'type': 'matchesTrace', 'params': "
                "{'kind': 'trigger', 'target': 'render', "
                "'detail': {'transport': 'in_process', "
                "'entry': 'Renderer.render'}}}}}}, "
                "'running': {'on': {'show':",
            )
        )
        self.assertEqual(
            {"matched"},
            {row["status"] for row in self.check()["directions"].values()},
        )


class SiblingTransportTests(unittest.TestCase):
    def test_multiple_declarations_allow_a_compatible_client(self):
        clients = [
            {"component": "C3", "interface": INTERFACE, "transport": "http"},
            {
                "component": "C3",
                "interface": INTERFACE,
                "transport": "in_process",
            },
        ]
        self.assertTrue(
            _declares_client(
                clients, "C3", INTERFACE, None, transport="in_process"
            )
        )

    def test_http_only_client_cannot_select_in_process_binding(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            caller = carriers(
                root,
                "C2",
                1,
                {
                    "client": [
                        {
                            "component": "C3",
                            "interface": INTERFACE,
                            "transport": "http",
                            "routes": ["POST /only"],
                        }
                    ]
                },
                {"kind": "trigger", "target": "caller"},
                {
                    "kind": "effect",
                    "target": "C3",
                    "outcome": "called",
                    "detail": {"interface": INTERFACE, **BINDING},
                },
            )
            provider = carriers(
                root,
                "C3",
                4,
                {"server": {INTERFACE: BINDING}},
                {"kind": "trigger", "target": INTERFACE, "detail": BINDING},
                {"kind": "effect", "target": "C3", "outcome": "called"},
                ", interface='compiler_worker', transport='in_process', "
                "entry='Orchestrator.run_worker'",
            )
            with self.assertRaisesRegex(ValueError, "does not declare client"):
                check_sibling_binding(
                    root,
                    caller,
                    "C3",
                    provider,
                    event="invoke",
                    interface=INTERFACE,
                )
