import os
import shutil
import tempfile
import unittest
from pathlib import Path

from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_2_SPEC_READING_C83.SPECIFICATION_MODEL_C85._package__shared import (
    normalize_claim,
)
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_4_SPEC_COMPARISON_C88._package__shared import (
    check_cli_spec,
)
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.SPEC_ENGINE_C75__tests.functional.test_cli_spec import (
    _CONTRACT, _MANIFEST, _SOLUTION, _carrier,
)

LEAN = os.environ.get("ANECHOIC_TEST_LEAN") or shutil.which("lean")
BASE = (
    "declare_cli_contract(interface='suite', action='run', runner='uv', path='suite.py', "
    "outcomes={'succeeded': 'zero', 'failed': 'nonzero'}, "
)
FIRST = BASE + "output='succeeded', must_effect=(('audit', 'ok'),))"
SECOND = BASE + "output='failed', must_effect=(('audit', 'ok'),))"
SOLUTION = _SOLUTION.replace("'running': {'on': {", """'running': {'on': {
            'audit': {'target': 'reporting', 'guard': {'type': 'matchesTrace', 'params':
                {'kind': 'effect', 'target': 'audit', 'outcome': 'ok'}}}}},
        'reporting': {'on': {""")


def fences(*claims):
    return '## Claim\n\n### Formal Claim\n\n' + '\n'.join(
        f'```python cli\n{claim}\n```\n' for claim in claims)


class CliTraceCasesTests(unittest.TestCase):
    def test_cases_require_unique_outputs_and_identical_common_fields(self):
        def normalize(*claims):
            return normalize_claim(
                "contract",
                {"claims": [("python cli", claim) for claim in claims]},
                "C2",
            )

        profile, error = normalize(FIRST, SECOND)
        self.assertIsNone(error)
        self.assertEqual(
            ["succeeded", "failed"],
            [case["output"] for case in profile["cases"]],
        )
        for second in (
            FIRST,
            SECOND.replace("runner='uv'", "runner='other'"),
            SECOND.replace("'failed': 'nonzero'", "'failed': 'zero'"),
            BASE[:-2] + ")",
        ):
            with self.subTest(second=second):
                profile, error = normalize(FIRST, second)
                self.assertIsNone(profile)
                self.assertTrue(error)

    @unittest.skipUnless(LEAN, 'Lean unavailable')
    def test_each_case_is_compared_and_failures_are_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pins = (
                _carrier(root, 'AN-S-1', 'component_manifest', 'C1', '{}', _MANIFEST),
                _carrier(root, 'AN-S-2', 'component_contract', 'C2', '{ANSWERS: [AN-S-1]}',
                         fences(FIRST, SECOND)),
                _carrier(root, 'AN-S-3', 'decision', 'C2', '{IS_SOLUTION_FOR: [AN-S-2@1]}', SOLUTION),
            )
            def check():
                return check_cli_spec(root, 'C2', *pins, interface='suite', lean=LEAN)
            report = check()
            facts = report['directions']['contract_solution']['facts']
            self.assertEqual({'succeeded': 'matched', 'failed': 'matched'},
                             {fact['output']: fact['status'] for fact in facts if fact['key'] == 'must_effect'})
            self.assertEqual([], report['uncovered_outcomes'])
            path = root / pins[1]['path']
            original = path.read_text()
            path.write_text(
                original.replace(
                    SECOND,
                    SECOND.replace("('audit', 'ok')", "('other', 'ok')"),
                )
            )
            facts = check()["directions"]["contract_solution"]["facts"]
            self.assertEqual(
                {"succeeded": "matched", "failed": "conflicting"},
                {
                    fact["output"]: fact["status"]
                    for fact in facts
                    if fact["key"] == "must_effect"
                },
            )
            path.write_text(original)
            solution = root / pins[2]['path']
            solution.write_text(solution.read_text().replace("'outcome': 'failed'", "'outcome': 'other'"))
            report = check()
            self.assertEqual([{'action': 'run', 'output': 'other'}], report['uncovered_outcomes'])
            self.assertEqual('unresolved', next(fact['status'] for fact in
                             report['directions']['contract_solution']['facts']
                             if fact.get('output') == 'failed' and fact['key'] == 'must_effect'))
            path.write_text(original.replace(SECOND, FIRST))
            self.assertTrue(check()['unresolved'])

    @unittest.skipUnless(LEAN, 'Lean unavailable')
    def test_exact_codes_satisfy_classes_and_keep_exact_conflicts(self):
        solution = _SOLUTION.replace(
            "'exit_status_class': 'zero'", "'exit_code': 0"
        ).replace("'exit_status_class': 'nonzero'", "'exit_code': 2")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pins = (
                _carrier(
                    root, "AN-S-1", "component_manifest", "C1", "{}", _MANIFEST
                ),
                _carrier(
                    root,
                    "AN-S-2",
                    "component_contract",
                    "C2",
                    "{ANSWERS: [AN-S-1]}",
                    _CONTRACT,
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
            def status():
                return check_cli_spec(
                    root, "C2", *pins, interface="suite", lean=LEAN
                )["directions"]["contract_solution"]["status"]

            self.assertEqual("matched", status())
            path = root / pins[1]["path"]
            path.write_text(
                path.read_text().replace(
                    "outcomes={'succeeded': 'zero', 'failed': 'nonzero'}",
                    "exit_codes={'succeeded': 0, 'failed': 1}",
                )
            )
            self.assertEqual("conflicting", status())
