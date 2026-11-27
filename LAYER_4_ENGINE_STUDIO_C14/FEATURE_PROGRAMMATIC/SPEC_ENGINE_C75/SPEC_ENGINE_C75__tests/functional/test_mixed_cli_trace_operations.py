import os
import shutil
import tempfile
import unittest
from pathlib import Path

from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75._package__shared import (
    verify_formal_chain,
)
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_4_SPEC_COMPARISON_C88._package__shared import (
    check_cli_spec,
)
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_4_SPEC_COMPARISON_C88._package__shared import (
    check_trace_spec,
)
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.SPEC_ENGINE_C75__tests.functional.test_cli_spec import (
    _CONTRACT, _MANIFEST, _SOLUTION, _carrier,
)
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.SPEC_ENGINE_C75__tests.functional.test_trace_child_delegation import (
    CONTRACT as TRACE_CONTRACT, SOLUTION as TRACE_SOLUTION,
)


def combined(first, second):
    return first + '\n' + second[second.index('```'):]


class MixedCliTraceOperationsTests(unittest.TestCase):
    def test_cli_and_logical_operations_remain_independent(self):
        lean = os.environ.get('ANECHOIC_TEST_LEAN') or shutil.which('lean')
        if not lean:
            self.skipTest('Lean executable unavailable')
        manifest = _MANIFEST.replace("'server': {'suite': {", "'server': {'render': {'outcomes': "
            "{'succeeded': {'must_effect': [('workbench_display', 'shown')]}}}, 'suite': {")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pins = (
                _carrier(root, 'AN-S-1', 'component_manifest', 'C1', '{}', manifest),
                _carrier(root, 'AN-S-2', 'component_contract', 'C2', '{ANSWERS: [AN-S-1]}',
                         combined(_CONTRACT, TRACE_CONTRACT)),
                _carrier(root, 'AN-S-3', 'decision', 'C2', '{IS_SOLUTION_FOR: [AN-S-2@1]}',
                         combined(_SOLUTION, TRACE_SOLUTION)),
            )

            def cli():
                return check_cli_spec(
                    root,
                    "C2",
                    *pins,
                    interface="suite",
                    action="run",
                    lean=lean,
                )

            def trace():
                return check_trace_spec(root, 'C2', *pins, action='render', lean=lean)

            self.assertEqual({'matched'}, {row['status'] for row in cli()['directions'].values()})
            self.assertEqual('matched', trace()['directions']['contract_solution']['status'])
            selected = verify_formal_chain(root, 'C2', *pins, action='render', lean=lean)
            self.assertEqual('compared', selected['outcome'])
            self.assertIn('workbench_display', selected['mermaid'])
            self.assertNotIn('exit_status_class', selected['mermaid'])
            self.assertNotIn('workbench_display', cli()['mermaid'])
            whole = check_cli_spec(root, 'C2', *pins, interface='suite', lean=lean)
            self.assertEqual('unresolved', whole['status'])
            self.assertIn('boundaries.io.server.render.outcomes.succeeded',
                          {row['field'] for row in whole['unresolved']})
            for action in (None, 'run'):
                gap = verify_formal_chain(root, 'C2', *pins, action=action, lean=lean)
                self.assertEqual('incomplete', gap['outcome'])
                self.assertIn('check_cli_spec', gap['unresolved'][0]['message'])
            path = root / pins[2]['path']
            path.write_text(path.read_text().replace("'target': 'workbench_display'", "'target': 'wrong'"))
            self.assertEqual('conflicting', trace()['directions']['contract_solution']['status'])
            self.assertEqual({'matched'}, {row['status'] for row in cli()['directions'].values()})

    def test_selects_cli_action_on_shared_interface(self):
        lean = os.environ.get('ANECHOIC_TEST_LEAN') or shutil.which('lean')
        if not lean:
            self.skipTest("Lean executable unavailable")
        inspect_contract = _CONTRACT.replace(
            "action='run'", "action='inspect'"
        )
        inspect_solution = _SOLUTION.replace(
            "action='run'", "action='inspect'"
        ).replace("'pass':", "'inspected':")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pins = (
                _carrier(root, 'AN-S-1', 'component_manifest', 'C1', '{}', _MANIFEST),
                _carrier(root, 'AN-S-2', 'component_contract', 'C2', '{ANSWERS: [AN-S-1]}',
                         combined(_CONTRACT, inspect_contract)),
                _carrier(root, 'AN-S-3', 'decision', 'C2', '{IS_SOLUTION_FOR: [AN-S-2@1]}',
                         combined(_SOLUTION, inspect_solution)),
            )
            for action, event in (("run", "pass"), ("inspect", "inspected")):
                report = check_cli_spec(
                    root,
                    "C2",
                    *pins,
                    interface="suite",
                    action=action,
                    lean=lean,
                )
                self.assertEqual(
                    {"matched"},
                    {row["status"] for row in report["directions"].values()},
                )
                self.assertIn(f" : {event} / output", report["mermaid"])
            with self.assertRaisesRegex(
                ValueError, "No CLI Contract for Action"
            ):
                check_cli_spec(
                    root,
                    "C2",
                    *pins,
                    interface="suite",
                    action="missing",
                    lean=lean,
                )
