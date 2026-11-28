import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from ..cli._cli_static_imports import (
    parse_workflow,
    render_solution,
    check_cli_spec,
    compare_obligations,
    feasible_terminals,
)
from ..cli.test_cli_spec import _carrier

from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75._package__shared import (
    compile_workflow,
    verify_formal_chain,
)

LEAN = os.environ.get("ANECHOIC_TEST_LEAN") or shutil.which("lean")
ENGINE = Path(__file__).resolve().parents[6]
REPLAY = ENGINE / (
    "IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IMPORT_GRAPH_C61/Work"
    "flowTrace.lean"
)
CONTRACT = (
    "## Summary\n"
    "\n"
    "Declare the Component.\n"
    "\n"
    "## Purpose\n"
    "\n"
    "Model one public Action.\n"
    "\n"
    "## Component Identity\n"
    "\n"
    "```python\n"
    "from anechoic.formal_claims import declare_entity\n"
    "from anechoic.model import ComponentManifest\n"
    "declare_entity(entity_name='Component Manifest', "
    "instance=ComponentManifest(\n"
    "    component_id='C2', name='Example'))\n"
    "```\n"
    "\n"
    "## Component Boundaries\n"
    "\n"
    "```python\n"
    "{'state': {'reads': [], 'writes': []}}\n"
    "```\n"
    "\n"
    "## Component Contract\n"
    "\n"
    "```python cli\n"
    "declare_cli_contract(interface='suite', action='invoke', "
    "exit_codes={'succeeded': 0, 'failed': 1})\n"
    "```\n"
)
MACHINE = {
    "id": "example",
    "initial": "start",
    "states": {
        "start": {
            "on": {
                "request": {
                    "to": "issue",
                    "expect": {
                        "kind": "trigger",
                        "target": "suite",
                        "detail": {"transport": "cli", "seed": "A"},
                        "bind": {"ticket": "seed"},
                    },
                }
            }
        },
        "issue": {
            "on": {
                "accept": {
                    "to": "done",
                    "expect": {
                        "kind": "output",
                        "outcome": "succeeded",
                        "detail": {"seed": "B", "exit_code": 0},
                        "same_as": {"seed": "ticket"},
                    },
                },
                "reject": {
                    "to": "done",
                    "expect": {
                        "kind": "output",
                        "outcome": "failed",
                        "detail": {"exit_code": 1},
                    },
                },
            }
        },
        "done": {"type": "final"},
    },
}


def solution(machine):
    return (
        "## Claim\n\n### Formal Claim\n\n```python\n"
        "component_workflow(component='C2', action='invoke', "
        f"machine={machine!r})\n```\n"
    )


def replay(machine, outcome, seed):
    model = compile_workflow(
        parse_workflow(
            "component_workflow(component='C2', action='invoke', "
            f"machine={machine!r})"
        )["machine"]
    )["model"]
    events = [
        {
            "kind": "trigger",
            "name": "request",
            "target": "suite",
            "outcome": None,
            "detail": {"transport": "cli", "seed": "A"},
        },
        {
            "kind": "output",
            "name": "accept" if outcome == "succeeded" else "reject",
            "target": None,
            "outcome": outcome,
            "detail": {"seed": seed, "exit_code": 0}
            if outcome == "succeeded"
            else {"exit_code": 1},
        },
    ]
    result = subprocess.run(
        [LEAN, "--run", str(REPLAY)],
        input=json.dumps({"model": model, "events": events, "complete": True}),
        text=True,
        capture_output=True,
        check=True,
    )
    return json.loads(result.stdout)["status"]


def _prepare_cli_case(root, contract, codes):
    manifest = _carrier(
        root, "AN-S-1", "component_manifest", "C1", "{}", contract
    )
    path = root / manifest["path"]
    path.write_text(path.read_text().replace("tier: 4", "tier: 1"))
    machine = json.loads(json.dumps(MACHINE))
    branches = machine["states"]["issue"]["on"]
    branches["accept"]["expect"]["detail"]["seed"] = "A"
    for index, code in enumerate(codes):
        detail = {} if code is None else {"exit_code": code}
        branches[f"alternate{index}"] = {
            "to": "done",
            "expect": {
                "kind": "output",
                "outcome": "failed",
                "detail": detail,
            },
        }
    pin = _carrier(
        root,
        "AN-S-2",
        "solution",
        "C2",
        "{ANSWERS: [AN-S-1@1]}",
        solution(machine),
    )
    return manifest, pin


def _correlated_pins(root):
    manifest = _carrier(
        root, "AN-S-1", "component_manifest", "C1", "{}", CONTRACT
    )
    manifest_path = root / manifest["path"]
    manifest_path.write_text(
        manifest_path.read_text().replace("tier: 4", "tier: 1")
    )
    machine = json.loads(json.dumps(MACHINE))
    pin = _carrier(
        root,
        "AN-S-2",
        "solution",
        "C2",
        "{ANSWERS: [AN-S-1@1]}",
        solution(machine),
    )
    return manifest, pin, machine


@unittest.skipUnless(LEAN, "Lean unavailable")
class CliReachabilityTests(unittest.TestCase):
    def _check_comparison(self, root, manifest, pin, key, expected):
        comparator = (
            "FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECI"
            "FICATION_C94.LAYER_4_SPEC_COMPARISON_C88.cli_spec__pub"
        )
        calls = Mock()
        with (
            patch(
                (
                    "FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.form"
                    "al_chain__pub.render_solution"
                ),
                wraps=render_solution,
            ) as render,
            patch(
                f"{comparator}.compare_obligations",
                wraps=compare_obligations,
            ) as compare,
        ):
            calls.attach_mock(render, "render")
            calls.attach_mock(compare, "compare")
            result = verify_formal_chain(
                root, "C2", manifest, solution=pin, lean=LEAN
            )
        self.assertEqual("compared", result["outcome"], result)
        self.assertEqual("matched", result["translation"]["status"])
        self.assertEqual(
            ["render", "compare"],
            [call[0] for call in calls.mock_calls],
        )
        self.assertIn('state "issue" as S1', result["mermaid"])
        self.assertIn("S1 --> S2 : alternate", result["mermaid"])
        (fact,) = [
            fact
            for fact in result["directions"]["manifest_solution"]["facts"]
            if fact["key"] == key
        ]
        self.assertEqual(expected, fact["status"])
        self.assertEqual(expected, result["status"])

    def test_cli_terminal_exit_status_facts_and_comparison_order(self):
        class_contract = CONTRACT.replace(
            "exit_codes={'succeeded': 0, 'failed': 1}",
            "outcomes={'succeeded': 'zero', 'failed': 'nonzero'}",
        )
        for contract, codes, key, expected in (
            (class_contract, (2,), "outcomes", "matched"),
            (class_contract, (0,), "outcomes", "conflicting"),
            (CONTRACT, (2,), "exit_codes", "conflicting"),
            (class_contract, (None,), "outcomes", "unresolved"),
            (class_contract, (0, None), "outcomes", "conflicting"),
            (CONTRACT, (2, None), "exit_codes", "conflicting"),
        ):
            with (
                self.subTest(codes=codes, obligation=key),
                tempfile.TemporaryDirectory() as directory,
            ):
                root = Path(directory)
                manifest, pin = _prepare_cli_case(root, contract, codes)
                self._check_comparison(root, manifest, pin, key, expected)

    def test_impossible_and_feasible_correlated_outcomes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest, pin, machine = _correlated_pins(root)

            def status():
                return check_cli_spec(
                    root,
                    "C2",
                    manifest,
                    solution=pin,
                    interface="suite",
                    lean=LEAN,
                )["status"]

            self.assertNotEqual("matched", status())
            self.assertEqual("different", replay(machine, "succeeded", "A"))
            self.assertEqual("different", replay(machine, "succeeded", "B"))
            self.assertEqual("matched", replay(machine, "failed", "A"))
            machine["states"]["issue"]["on"]["accept"]["expect"]["detail"][
                "seed"
            ] = "A"
            (root / pin["path"]).write_text(
                (root / pin["path"]).read_text().split("## Claim")[0]
                + solution(machine)
            )
            self.assertEqual("matched", status())
            self.assertEqual("matched", replay(machine, "succeeded", "A"))
            self.assertEqual("matched", replay(machine, "failed", "A"))
            del machine["states"]["start"]["on"]["request"]["expect"][
                "detail"
            ]["seed"]
            path = root / pin["path"]
            path.write_text(
                path.read_text().split("## Claim")[0] + solution(machine)
            )
            self.assertEqual("unresolved", status())


class UnknownReachabilityTests(unittest.TestCase):
    def test_unknown_binding_is_unresolved(self):
        machine = json.loads(json.dumps(MACHINE))
        del machine["states"]["start"]["on"]["request"]["expect"]["detail"][
            "seed"
        ]
        workflow = parse_workflow(
            "component_workflow(component='C2', action='invoke', "
            f"machine={machine!r})"
        )
        self.assertIsNone(
            feasible_terminals(compile_workflow(workflow["machine"])["model"])
        )
