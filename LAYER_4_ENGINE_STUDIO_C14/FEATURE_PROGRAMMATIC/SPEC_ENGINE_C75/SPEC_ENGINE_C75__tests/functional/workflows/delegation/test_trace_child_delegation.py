import os
import shutil
import tempfile
import unittest
from pathlib import Path

# fmt: off
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.\
    LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_4_SPEC_COMPARISON_C88.\
    DELEGATION_VERIFICATION_C89._package__shared import (
    check_child_outcome,
    check_sibling_outcome,
)
# fmt: on
# fmt: off
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.SPEC_ENGINE_C75__tests.\
    functional.contracts.cli.test_cli_spec import (
    _carrier,
)
# fmt: on


from ._trace_child_fixtures import CONTRACT, MANIFEST, PARENT, pins
from ._trace_child_fixtures import SOLUTION as SOLUTION


class TraceChildDelegationTests(unittest.TestCase):
    def setUp(self):
        self.lean = os.environ.get("ANECHOIC_TEST_LEAN") or shutil.which(
            "lean"
        )
        if not self.lean:
            self.skipTest("Lean executable unavailable")
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.parent, self.child = pins(self.root)

    def check(self):
        return check_child_outcome(
            self.root,
            self.parent,
            "C2",
            self.child,
            event="render",
            lean=self.lean,
        )

    def statuses(self):
        return {
            name: row["status"]
            for name, row in self.check()["directions"].items()
        }

    def test_solution_must_prove_the_selected_effect(self):
        matched = {
            "caller_manifest": "matched",
            "caller_contract": "matched",
            "caller_solution": "matched",
        }
        self.assertEqual(matched, self.statuses())
        path = self.root / self.child[2]["path"]
        original = path.read_text()
        bypass = (
            "'start': {'on': {'skip': {'target': 'don"
            "e', 'guard': {'type': 'matchesTrace', "
            "'params': {'kind': 'output', 'outcome': 'succeeded'}}}, 'show':"
        )
        for body in (
            original.replace(
                "'target': 'workbench_display'", "'target': 'other'"
            ),
            original.replace("'start': {'on': {'show':", bypass),
        ):
            with self.subTest(body=body):
                path.write_text(body)
                self.assertEqual(
                    {**matched, "caller_solution": "conflicting"},
                    self.statuses(),
                )

    def test_legacy_child_manifest_pin_is_compared_as_a_source_pin(self):
        path = self.root / self.parent["path"]
        source = path.read_text()
        for pin, expected in (
            ("AN-S-1@1", "matched"),
            ("AN-S-999@1", "conflicting"),
        ):
            with self.subTest(pin=pin):
                path.write_text(
                    source.replace(
                        "'output': 'succeeded'",
                        f"'output': 'succeeded', 'manifest': {pin!r}",
                    )
                )
                directions = self.check()["directions"]
                self.assertEqual(
                    {expected},
                    {item["status"] for item in directions.values()},
                )
                for item in directions.values():
                    (fact,) = (
                        fact
                        for fact in item["facts"]
                        if fact["key"] == "manifest"
                    )
                    self.assertEqual(expected, fact["status"])

    def test_missing_manifest_effect_is_unresolved(self):
        path = self.root / self.child[0]["path"]
        path.write_text(
            path.read_text().replace("'workbench_display'", "'other'")
        )
        report = self.check()
        self.assertEqual([], report["issues"])
        self.assertEqual(
            "unresolved", report["directions"]["caller_manifest"]["status"]
        )

    def test_qualified_effect_requires_each_provider_claim_to_imply_it(self):
        parent = self.root / self.parent["path"]
        parent.write_text(
            parent.read_text().replace(
                "'output': 'succeeded'",
                (
                    "'output': 'succeeded', 'model': 'wanted'"
                    ", 'limit': {'at_most': 5}"
                ),
            )
        )
        self.assertEqual({"conflicting"}, set(self.statuses().values()))
        for pin in self.child:
            path = self.root / pin["path"]
            body = path.read_text()
            if pin is self.child[2]:
                body = body.replace(
                    "'outcome': 'shown'",
                    (
                        "'outcome': 'shown', 'detail': {'model': "
                        "'wanted', 'limit': 4}"
                    ),
                )
            else:
                body = body.replace(
                    "('workbench_display', 'shown')",
                    (
                        "('workbench_display', 'shown', {'model':"
                        " 'wanted', 'limit': 4})"
                    ),
                )
            path.write_text(body)
        self.assertEqual({"matched"}, set(self.statuses().values()))
        for pin, direction in zip(
            self.child,
            ("caller_manifest", "caller_contract", "caller_solution"),
        ):
            path = self.root / pin["path"]
            original = path.read_text()
            path.write_text(
                original.replace("'model': 'wanted'", "'model': 'other'")
            )
            self.assertEqual("conflicting", self.statuses()[direction])
            path.write_text(original)

    def test_contract_forbidding_the_child_effect_conflicts(self):
        path = self.root / self.child[1]["path"]
        path.write_text(
            path.read_text().replace(
                "must_effect=(('workbench_display', 'shown'),)",
                "forbid_effect=('workbench_display',)",
            )
        )
        self.assertEqual("conflicting", self.statuses()["caller_contract"])

    def test_repeated_event_requires_identical_expectations(self):
        path = self.root / self.parent["path"]
        alternate = """'alternate': {'on': {'render': {'target': 'done\
', 'guard': {'type': 'matchesTrace',
            'params': {'kind': 'effect', 'target': 'workbench_display'\
, 'outcome': 'shown',
                       'detail': {'component': 'C2', 'action': 'render\
', 'output': 'succeeded'}}}}}},
        'done': {'type': 'final'}"""
        branch = """'start': {'on': {'branch': {'target': 'alternate',\
 'guard': {'type': 'matchesTrace',
            'params': {'kind': 'trigger'}}}, 'render':"""
        source = PARENT.replace("'start': {'on': {'render':", branch).replace(
            "'done': {'type': 'final'}", alternate
        )
        source = path.read_text().replace(PARENT, source)
        path.write_text(source)
        self.assertEqual({"matched"}, set(self.statuses().values()))
        path.write_text(
            source.replace("'output': 'succeeded'", "'output': 'other'", 1)
        )
        self.assertEqual({"unresolved"}, set(self.statuses().values()))

    def test_cli_contract_trace_fields_match(self):
        path = self.root / self.child[1]["path"]
        body = CONTRACT.replace("```python trace", "```python cli").replace(
            "declare_trace_contract(action='render'",
            "declare_cli_contract(interface='render', "
            "runner='uv', path='render.py', action='render'",
        )
        original = path.read_text()
        path.write_text(original.replace(CONTRACT, body))
        self.assertEqual({"matched"}, set(self.statuses().values()))
        failure = body[body.index("```python cli") :].replace(
            "output='succeeded'", "output='failed'"
        )
        path.write_text(original.replace(CONTRACT, body + "\n" + failure))
        self.assertEqual({"matched"}, set(self.statuses().values()))

    def test_child_must_belong_to_parent(self):
        path = self.root / self.child[0]["path"]
        path.write_text(
            path.read_text().replace("component: C1", "component: C9")
        )
        self.child[0]["container_component"] = "C9"
        with self.assertRaises(ValueError):
            self.check()


class TraceSiblingOutcomeTests(unittest.TestCase):
    def test_explicit_interface_declares_sibling_dependency(self):
        lean = os.environ.get("ANECHOIC_TEST_LEAN") or shutil.which("lean")
        if not lean:
            self.skipTest("Lean executable unavailable")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, provider = pins(root)
            caller_manifest = MANIFEST.replace(
                "component_id='C2'", "component_id='C3'"
            ).replace(
                "'server': {'render': {",
                "'client': {'snapshot_client': {'component': 'C2', "
                "'interface': 'render'}}, 'server': {'render': {",
            )
            caller_contract = CONTRACT.replace(
                "action='render'", "action='run'"
            )
            caller = _sibling_caller(root, caller_manifest, caller_contract)

            def check():
                return check_sibling_outcome(
                    root,
                    caller,
                    "C2",
                    provider,
                    event="render",
                    interface="render",
                    lean=lean,
                )

            self.assertEqual(
                {
                    "caller_manifest": "matched",
                    "caller_contract": "matched",
                    "caller_solution": "matched",
                },
                {
                    key: row["status"]
                    for key, row in check()["directions"].items()
                },
            )
            _reject_wrong_sibling(self, root, caller, check)


def _sibling_caller(root, caller_manifest, caller_contract):
    caller = (
        _carrier(
            root,
            "AN-S-5",
            "component_manifest",
            "C1",
            "{}",
            caller_manifest,
        ),
        _carrier(
            root,
            "AN-S-6",
            "component_contract",
            "C3",
            "{ANSWERS: [AN-S-5]}",
            caller_contract,
        ),
        _carrier(
            root,
            "AN-S-7",
            "decision",
            "C3",
            "{IS_SOLUTION_FOR: [AN-S-6@1]}",
            PARENT.replace("component='C1'", "component='C3'").replace(
                "'output': 'succeeded'",
                "'output': 'succeeded', 'interface': 'render'",
            ),
        ),
    )
    return caller


def _reject_wrong_sibling(self, root, caller, check):
    path = root / caller[0]["path"]
    path.write_text(
        path.read_text().replace("'component': 'C2'", "'component': 'C9'")
    )
    with self.assertRaises(ValueError):
        check()
