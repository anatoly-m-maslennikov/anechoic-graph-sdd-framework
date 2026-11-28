import shutil
import tempfile
import unittest
from pathlib import Path

from ._cli_spec_case_helpers import (
    _check_query,
    _check_subcommands,
    _subcommand_route,
)
from ._cli_static_imports import check_cli_spec, parse_cli_contract
from ._cli_spec_fixtures import (
    _CONTRACT as _CONTRACT,
    _MANIFEST as _MANIFEST,
    _QUERY_CONTRACT as _QUERY_CONTRACT,
    _QUERY_SOLUTION as _QUERY_SOLUTION,
    _SOLUTION as _SOLUTION,
    _carrier as _carrier,
)


def _pins(root, manifest, contract, solution):
    return (
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


class CliSpecTests(unittest.TestCase):
    def test_cli_chain_and_mutations(self):
        if shutil.which("lean") is None:
            self.skipTest("Lean executable unavailable")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pins = _pins(root, _MANIFEST, _CONTRACT, _SOLUTION)
            report = check_cli_spec(root, "C2", *pins, interface="suite")
            self.assertEqual(
                {
                    "manifest_contract": "matched",
                    "manifest_solution": "matched",
                    "contract_solution": "matched",
                },
                {
                    name: row["status"]
                    for name, row in report["directions"].items()
                },
            )
            self.assertIn('state "running" as S1', report["mermaid"])
            self.assertIn("S1 --> S2 : pass", report["mermaid"])
            solution = root / pins[2]["path"]
            original = solution.read_text(encoding="utf-8")
            for old, new, outcome in (
                (
                    "'exit_status_class': 'zero'",
                    "'exit_status_class': 'nonzero'",
                    "conflicting",
                ),
                (
                    ", 'detail': {'exit_status_class': 'nonzero'}",
                    "",
                    "unresolved",
                ),
            ):
                with self.subTest(outcome=outcome):
                    solution.write_text(
                        original.replace(old, new, 1), encoding="utf-8"
                    )
                    direction = check_cli_spec(
                        root, "C2", *pins, interface="suite"
                    )["directions"]["contract_solution"]
                    self.assertEqual(outcome, direction["status"])

    def test_cli_contract_rejects_nonliteral_or_ambiguous_outcomes(self):
        declaration = (
            "declare_cli_contract(interface='test_suite', action='run', "
            "runner='uv', path='suite.py', outcomes=%s)"
        )
        for outcomes in (
            "{'ok': True}",
            "{'ok': 1}",
            "{'ok': 'zero', 'ok': 'nonzero'}",
            "{'ok': get_status()}",
        ):
            with (
                self.subTest(outcomes=outcomes),
                self.assertRaises(ValueError),
            ):
                parse_cli_contract(declaration % outcomes)

    def test_cli_exit_codes_distinguish_nonzero_values(self):
        if shutil.which("lean") is None:
            self.skipTest("Lean executable unavailable")
        contract = _CONTRACT.replace(
            "outcomes={'succeeded': 'zero', 'failed': 'nonzero'}",
            "exit_codes={'succeeded': 0, 'failed': 1}",
        )
        solution = _SOLUTION.replace(
            "'exit_status_class': 'zero'", "'exit_code': 0"
        ).replace("'exit_status_class': 'nonzero'", "'exit_code': 1")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pins = _pins(root, _MANIFEST, contract, solution)
            self.assertEqual(
                "matched",
                check_cli_spec(root, "C2", *pins, interface="suite")[
                    "directions"
                ]["contract_solution"]["status"],
            )
            path = root / pins[2]["path"]
            path.write_text(
                path.read_text(encoding="utf-8").replace(
                    "'exit_code': 1", "'exit_code': 130"
                ),
                encoding="utf-8",
            )
            self.assertEqual(
                "conflicting",
                check_cli_spec(root, "C2", *pins, interface="suite")[
                    "directions"
                ]["contract_solution"]["status"],
            )

    def test_cli_contract_rejects_invalid_exit_codes(self):
        declaration = (
            "declare_cli_contract(interface='suite', "
            "action='run', runner='uv', "
            "path='suite.py', exit_codes={'failed': %s})"
        )
        for code in ("True", "-1", "256", "'1'"):
            with self.subTest(code=code), self.assertRaises(ValueError):
                parse_cli_contract(declaration % code)

    def test_cli_required_effect_blocks_a_terminal_bypass(self):
        if shutil.which("lean") is None:
            self.skipTest("Lean executable unavailable")
        manifest = _MANIFEST.replace(
            "'path': 'suite.py'", "'module': 'engine.suite'"
        )
        contract = _CONTRACT.replace(
            "path='suite.py'", "module='engine.suite'"
        ).replace(
            "outcomes={'succeeded': 'zero', 'failed': 'nonzero'}",
            "output='succeeded', must_effect=(('C2', 'succeeded'),)",
        )
        bypass = (
            "'running': {'on': {\n"
            "            'bypass': {'target': 'reporting', "
            "'guard': {'type': 'matchesTrace', 'params': "
            "{'kind': 'trigger'}}},"
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pins = _pins(root, manifest, contract, _QUERY_SOLUTION)
            path = root / pins[2]["path"]
            initial = path.read_text(encoding="utf-8")
            for body, expected in (
                (initial, "matched"),
                (
                    initial.replace("'running': {'on': {", bypass, 1),
                    "conflicting",
                ),
            ):
                with self.subTest(expected=expected):
                    path.write_text(body, encoding="utf-8")
                    report = check_cli_spec(
                        root, "C2", *pins, interface="suite"
                    )
                    direction = report["directions"]["contract_solution"]
                    self.assertEqual(expected, direction["status"])
                    effect = next(
                        row
                        for row in direction["facts"]
                        if row["key"] == "must_effect"
                    )
                    self.assertEqual(expected, effect["status"])

    def test_cli_contract_requires_one_entry_point(self):
        declaration = (
            "declare_cli_contract(interface='suite', action='run', runner='uv'"
        )
        self.assertEqual(
            "engine.suite",
            parse_cli_contract(declaration + ", module='engine.suite')")[
                "module"
            ],
        )
        for entry in ("", ", path='suite.py', module='engine.suite'"):
            with (
                self.subTest(entry=entry),
                self.assertRaisesRegex(ValueError, "exactly one"),
            ):
                parse_cli_contract(declaration + entry + ")")

    def test_cli_subcommands_require_the_declared_first_dispatch(self):
        if shutil.which("lean") is None:
            self.skipTest("Lean executable unavailable")
        manifest = _MANIFEST.replace(
            "'path': 'suite.py'",
            "'path': 'suite.py', 'subcommands': {'local': 'C2'}",
        )
        contract = _CONTRACT.replace(
            "outcomes={'succeeded': 'zero', 'failed': 'nonzero'}",
            "subcommands={'local': 'C2'}",
        )
        route = _subcommand_route()
        solution = _SOLUTION.replace("'running': {'on': {", route)
        bypass = (
            "'invoking': {'on': {'skip': {'target': 'done',\n"
            "            'guard': {'type': 'matchesTrace', "
            "'params': {'kind': 'output'}}},"
        )
        generic = (
            "'running': {'on': {'generic': {'target': "
            "'done',\n"
            "            'guard': {'type': 'matchesTrace', "
            "'params': {'kind': 'trigger'}}}, 'select':"
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pins = _pins(root, manifest, contract, solution)
            path = root / pins[2]["path"]
            original = path.read_text(encoding="utf-8")
            _check_subcommands(
                self,
                root,
                pins,
                path,
                original,
                bypass,
                generic,
                check_cli_spec,
            )

    def test_query_checks_require_the_ranked_read_on_every_success_path(self):
        if shutil.which("lean") is None:
            self.skipTest("Lean executable unavailable")
        manifest = _MANIFEST.replace(
            "'path': 'suite.py'",
            "'module': 'engine.suite', "
            "'arguments': ['--query', '<text>'], "
            "'output_fields': ['records', 'trace']",
        )
        bypass = """'running': {'on': {
            'skip': {'target': 'reporting', 'guard': {'type': 'matchesTrace',
                'params': {'kind': 'trigger'}}},"""
        initial_bypass = (
            "'idle': {'on': {'skip_request': {'target': "
            "'running',\n"
            "            'guard': {'type': 'matchesTrace', "
            "'params': {'kind': 'output'}}},"
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pins = _pins(root, manifest, _QUERY_CONTRACT, _QUERY_SOLUTION)
            report = check_cli_spec(root, "C2", *pins, interface="suite")
            self.assertTrue(
                all(
                    item["status"] == "matched"
                    for item in report["directions"].values()
                )
            )
            solution = root / pins[2]["path"]
            original = solution.read_text(encoding="utf-8")
            _check_query(
                self,
                root,
                pins,
                solution,
                original,
                bypass,
                initial_bypass,
                check_cli_spec,
            )
