import shutil
import tempfile
import unittest
from pathlib import Path

from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_4_SPEC_COMPARISON_C88.DELEGATION_VERIFICATION_C89._package__shared import (
    check_cli_child_dispatch,
)
from .test_cli_spec import _CONTRACT, _MANIFEST, _SOLUTION, _carrier


def _parent_workflow():
    route = """'running': {'on': {'select': {'target': 'invoking', 'guard': {'type': 'matchesTrace',
        'params': {'kind': 'trigger', 'detail': {'command': 'local'}}}}}},
        'invoking': {'on': {'dispatch': {'target': 'reporting', 'guard': {'type': 'matchesTrace',
        'params': {'kind': 'effect', 'target': 'C2'}}}}},
        'reporting': {'on': {"""
    return (_SOLUTION.replace("component='C2'", "component='C1'")
            .replace("'running': {'on': {", route))


def _pins(root):
    parent = _carrier(
        root, "AN-S-4", "decision", "C1", "{}", _parent_workflow()
    )
    manifest = _MANIFEST.replace(
        "'path': 'suite.py'", "'path': 'suite.py', 'command': 'local'"
    )
    solution = _SOLUTION.replace(
        "'path': 'suite.py'", "'path': 'suite.py', 'command': 'local'"
    )
    contract = _CONTRACT.replace(
        "path='suite.py'", "path='suite.py', command='local'"
    ).replace(
        "outcomes={'succeeded': 'zero', 'failed': 'nonzero'}",
        "arguments=('--secret', '<value>'), checks={'guarantees': {'priority': 'exact_name_first'}}",
    )
    child = (
        _carrier(root, "AN-S-1", "component_manifest", "C1", "{}", manifest),
        _carrier(
            root,
            "AN-S-2",
            "component_contract",
            "C2",
            "{ANSWERS: [AN-S-1]}",
            contract,
        ),
        _carrier(
            root,
            "AN-S-3",
            "decision",
            "C2",
            "{IS_SOLUTION_FOR: [AN-S-2@1]}",
            solution,
        ),
    )
    return parent, child


class CliChildDispatchTests(unittest.TestCase):
    def test_child_route_and_first_dispatch(self):
        if shutil.which('lean') is None:
            self.skipTest('Lean executable unavailable')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            parent, child = _pins(root)
            path = root / parent['path']
            original = path.read_text(encoding='utf-8')
            for old, new, expected in (
                ("", "", "matched"),
                (
                    "'target': 'reporting', 'guard': {'type': 'matchesTrace',\n        'params': {'kind': 'effect', 'target': 'C2'}}}}},",
                    "'target': 'later', 'guard': {'type': 'matchesTrace',\n        'params': {'kind': 'effect', 'target': 'C3'}}}}},\n        'later': {'on': {'dispatch': {'target': 'reporting', 'guard': {'type': 'matchesTrace',\n        'params': {'kind': 'effect', 'target': 'C2'}}}}},",
                    "conflicting",
                ),
                ("'command': 'local'", "'command': 'other'", "unresolved"),
            ):
                with self.subTest(expected=expected):
                    path.write_text(original.replace(old, new) if old else original, encoding='utf-8')
                    report = check_cli_child_dispatch(root, parent, 'C2', child, interface='suite', command='local')
                    directions = report['directions']
                    self.assertEqual({'caller_manifest', 'caller_contract', 'caller_solution'}, set(directions))
                    self.assertEqual({expected}, {row['status'] for row in directions.values()})
                    self.assertEqual(2, len(report['unmodeled']))
                    if expected == 'matched':
                        for row in directions.values():
                            self.assertEqual(
                                {
                                    "transport",
                                    "runner",
                                    "entry_point",
                                    "command",
                                    "component",
                                },
                                {fact["key"] for fact in row["facts"]},
                            )
                    self.assertTrue(
                        all("facts" in row for row in directions.values())
                    )

    def test_incomplete_entry_or_competing_unqualified_edge_is_unresolved(
        self,
    ):
        if shutil.which("lean") is None:
            self.skipTest("Lean executable unavailable")
        competing = """'running': {'on': {'other': {'target': 'done', 'guard': {'type': 'matchesTrace',
        'params': {'kind': 'effect', 'target': 'C3'}}}, 'select':"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            parent, child = _pins(root)
            path = root / parent['path']
            original = path.read_text(encoding='utf-8')
            for old, new in (
                ("'runner': 'uv', 'path': 'suite.py'", ''),
                ("'running': {'on': {'select':", competing),
            ):
                with self.subTest(old=old):
                    self.assertIn(old, original)
                    path.write_text(
                        original.replace(old, new, 1), encoding="utf-8"
                    )
                    report = check_cli_child_dispatch(
                        root,
                        parent,
                        "C2",
                        child,
                        interface="suite",
                        command="local",
                    )
                    self.assertEqual(
                        {"unresolved"},
                        {
                            row["status"]
                            for row in report["directions"].values()
                        },
                    )

    def test_parent_must_be_declared_by_child_manifest(self):
        if shutil.which('lean') is None:
            self.skipTest('Lean executable unavailable')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            parent, child = _pins(root)
            manifest = root / child[0]["path"]
            manifest.write_text(
                manifest.read_text(encoding="utf-8").replace(
                    "component: C1", "component: C9"
                ),
                encoding="utf-8",
            )
            child[0]["container_component"] = "C9"
            with self.assertRaisesRegex(ValueError, "not a declared child"):
                check_cli_child_dispatch(
                    root,
                    parent,
                    "C2",
                    child,
                    interface="suite",
                    command="local",
                )

    def test_selects_caller_and_provider_actions(self):
        if shutil.which('lean') is None:
            self.skipTest('Lean executable unavailable')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            parent, child = _pins(root)
            for pin in (parent, *child[1:]):
                path = root / pin["path"]
                original = path.read_text(encoding="utf-8")
                extra = original[original.index("```") :].replace(
                    "action='run'", "action='inspect'"
                )
                if pin is parent:
                    extra = extra.replace("'target': 'C2'", "'target': 'C3'")
                path.write_text(original + "\n" + extra, encoding="utf-8")
            for caller_action, expected in (
                ("run", "matched"),
                ("inspect", "conflicting"),
            ):
                report = check_cli_child_dispatch(
                    root,
                    parent,
                    "C2",
                    child,
                    interface="suite",
                    command="local",
                    caller_action=caller_action,
                    action="run",
                )
                self.assertEqual(
                    {expected},
                    {row["status"] for row in report["directions"].values()},
                )
