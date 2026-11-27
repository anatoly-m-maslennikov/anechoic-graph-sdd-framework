import os
import shutil
import tempfile
import unittest
from importlib import import_module
from pathlib import Path
from unittest.mock import patch

from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75._package__shared import verify_formal_chain
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_2_SPEC_READING_C83.SPECIFICATION_MODEL_C85._package__shared import (
    validate_declaration,
)
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_3_LEAN_TRANSLATOR_C84._package__shared import (
    compile_lean,
    run_lean_json,
)
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_4_SPEC_COMPARISON_C88._package__shared import (
    check_cli_spec,
    check_tool_api_spec,
    check_trace_spec,
)

from .test_cli_spec import _SOLUTION
from .test_direct_manifest_chain import _manifest, _pins
from .test_trace_cases import FIRST as TRACE
from .test_trace_cases import SECOND as OTHER_TRACE
from .test_trace_cases import SOLUTION as TRACE_SOLUTION

CONTRACT = 'declare_framing_contract(delimiter=[35], line_endings=[[10], [13, 10]])'
SOLUTION = (
    'declare_framing_solution(opening_prefixes=[[35, 10], [35, 13, 10]], '
    'closing_prefixes=[[10, 35, 10], [10, 35, 13, 10], [13, 10, 35, 10], [13, 10, 35, 13, 10]])'
)


def framing_pins(root, solution=SOLUTION):
    boundaries = "{'code': {'exports': {'api.read': 'public'}}, 'state': {'reads': ['disk'], 'writes': []}}"
    pins = _pins(root, _manifest('python framing', CONTRACT, boundaries=boundaries), solution)
    path = root / pins[1]['path']
    path.write_text(path.read_text().replace('```python\n', '```python framing\n'))
    return pins


class DirectFramingChainTests(unittest.TestCase):
    def setUp(self):
        self.lean = os.environ.get('ANECHOIC_TEST_LEAN') or os.environ.get('LEAN_BIN') or shutil.which('lean')
        self.assertTrue(self.lean, 'Lean executable unavailable')

    def test_checks_binary_bodies_and_retains_other_coverage_gaps(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = verify_formal_chain(root, 'C15', *framing_pins(root), lean=self.lean)
        self.assertEqual('compared', result['outcome'], result.get('diagnostics'))
        self.assertEqual('bounded_match', result['status'])
        self.assertIn('namespace CarrierBodySolution', result['lean'])
        validation = result['translation']
        self.assertEqual('bounded_match', validation['status'])
        fields = {gap['field'] for gap in validation['coverage_unresolved']}
        self.assertEqual({'boundaries.state', 'boundaries.code.exports', 'contract', 'solution'}, fields)
        cases = {bytes(row['input']): row for row in result['cases']}
        for raw, expected in [
            (b'', {'bounds': None, 'body': None}),
            (b'#\n#', {'bounds': None, 'body': None}),
            (b'#\n#\n\x00\xff', {'bounds': [2, 1, 4], 'body': [0, 255]}),
            (b'#\r\n#\r\n\x00\xff', {'bounds': [3, 2, 6], 'body': [0, 255]}),
        ]:
            self.assertEqual(expected, cases[raw]['manifest'])
            self.assertEqual(expected, cases[raw]['solution'])

    def test_mismatch_reports_acceptance_and_body_witnesses(self):
        solution = SOLUTION.replace('[13, 10, 35, 13, 10]', '[13, 10, 35, 13]')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = verify_formal_chain(root, 'C15', *framing_pins(root, solution), lean=self.lean)
        self.assertEqual('conflicting', result['status'])
        self.assertEqual('bounded_match', result['translation']['status'])
        mismatches = result['directions']['manifest_solution']['facts']
        self.assertTrue(any(case['manifest']['bounds'] is None and case['solution']['bounds'] for case in mismatches))
        self.assertTrue(any(case['manifest']['body'] == [0, 255] and case['solution']['body'] == [10, 0, 255]
                            for case in mismatches))

    def test_rejects_a_changed_validated_framing_result(self):
        chain = import_module(verify_formal_chain.__module__)
        original = chain.validate_translation

        def changed(*args, **kwargs):
            result = original(*args, **kwargs)
            result['framing_comparison']['cases'] = []
            return result

        with tempfile.TemporaryDirectory() as directory, patch.object(
                chain, 'validate_translation', side_effect=changed):
            root = Path(directory)
            result = verify_formal_chain(root, 'C15', *framing_pins(root),
                                         action='framing', lean=self.lean)
        self.assertEqual('incomplete', result['outcome'])
        self.assertIn('Framing comparison identity',
                      result['diagnostics'][0]['message'])

    def test_rejects_malformed_framing_observations_even_when_roles_agree(self):
        entry = (
            'FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94'
            '.LAYER_4_TRANSLATION_VALIDATOR_C86.translation_validation__pub'
        )
        for field, replacement in (
            ('bounds', '([0, 1] : List Nat)'),
            ('body', '"not bytes"'),
            ('body', '([256] : List Nat)'),
            ('body', '([42] : List Nat)'),
            ('body', 'Lean.Json.null'),
        ):
            with self.subTest(field=field, replacement=replacement):
                def malformed(program, *args, field=field, replacement=replacement, **kwargs):
                    original = next(line for line in program.splitlines()
                                    if line.startswith(f'    ("{field}",'))
                    closing = '),' if field == 'bounds' else ')]'
                    changed = program.replace(
                        original,
                        f'    ("{field}", Lean.toJson ({field}.map fun _ => {replacement}){closing}',
                        1,
                    )
                    return run_lean_json(changed, *args, **kwargs)

                with tempfile.TemporaryDirectory() as directory, patch(
                    entry + '.run_lean_json', side_effect=malformed,
                ):
                    root = Path(directory)
                    report = verify_formal_chain(root, 'C15', *framing_pins(root), lean=self.lean)
                self.assertEqual('incomplete', report['outcome'])
                self.assertEqual('translation', report['diagnostics'][0]['field'])
                self.assertEqual('Unexpected Lean framing comparison output',
                                 report['diagnostics'][0]['message'])

    def test_rejects_framing_observations_that_hide_a_role_mismatch(self):
        entry = (
            'FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94'
            '.LAYER_4_TRANSLATION_VALIDATOR_C86.translation_validation__pub'
        )

        def copied_projection(program, *args, **kwargs):
            compared = 'manifestBounds == solutionBounds && manifestBody == solutionBody'
            equality = f'Lean.toJson ({compared})'
            projection = 'framingResult solutionBounds solutionBody'
            self.assertEqual(1, program.count(equality))
            self.assertEqual(1, program.count(projection))
            changed = program.replace(equality, f'Lean.toJson (true || ({compared}))')
            changed = changed.replace(projection, 'framingResult manifestBounds manifestBody')
            return run_lean_json(changed, *args, **kwargs)

        solution = SOLUTION.replace('[13, 10, 35, 13, 10]', '[13, 10, 35, 13]')
        with tempfile.TemporaryDirectory() as directory, patch(entry + '.run_lean_json', side_effect=copied_projection):
            root = Path(directory)
            result = verify_formal_chain(root, 'C15', *framing_pins(root, solution), lean=self.lean)
        self.assertEqual('incomplete', result['outcome'])
        diagnostic, = result['diagnostics']
        self.assertEqual('translation', diagnostic['field'])
        self.assertEqual('Unexpected Lean framing comparison output', diagnostic['message'])

    def test_whole_chain_framing_retains_other_modeled_io(self):
        boundaries = {'io': {
            'class_shapes': {'Atom': {'fields': {'header': 'Header'}}, 'Plan': {'base': 'Atom'}},
            'server': {'invoke': {'outcomes': {'succeeded': {'must_effect': [('parser', 'called')]}}}},
        }}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pins = _pins(root, _manifest('python framing', CONTRACT, boundaries=repr(boundaries)), SOLUTION)
            path = root / pins[1]['path']
            path.write_text(path.read_text().replace('```python\n', '```python framing\n'))
            report = verify_formal_chain(root, 'C15', *pins, lean=self.lean)
        self.assertEqual('bounded_match', report['status'], report)
        self.assertIn('boundaries.io', {gap['field'] for gap in report['translation']['coverage_unresolved']})

    def test_mixed_manifest_and_solution_select_independent_actions(self):
        boundaries = "{'io': {'server': {'suite': {'transport': 'cli', 'runner': 'uv', 'path': 'suite.py'}}}}"
        cli = ("declare_cli_contract(interface='suite', action='run', "
               "outcomes={'succeeded': 'zero', 'failed': 'nonzero'})")
        workflow = _SOLUTION.split('```')[1].replace("component='C2'", "component='C15'")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pins = _pins(root, _manifest('python framing', CONTRACT, boundaries=boundaries)
                         + f'\n```python cli\n{cli}\n```\n', SOLUTION)
            path = root / pins[1]['path']
            path.write_text(path.read_text().replace('```python\n', '```python framing\n')
                            + f'\n```{workflow}```\n')
            report = validate_declaration(root, 'C15', 'manifest', pins[0])
            self.assertFalse(any(item['field'] == 'contract' for item in report['unresolved']), report)
            framing = verify_formal_chain(root, 'C15', *pins, action='framing', lean=self.lean)
            self.assertEqual('bounded_match', framing['status'], framing)
            cli = verify_formal_chain(root, 'C15', *pins, action='run', lean=self.lean)
            self.assertEqual('matched', cli['directions']['manifest_solution']['status'], cli)
            unselected = verify_formal_chain(root, 'C15', *pins, lean=self.lean)
            self.assertEqual('incomplete', unselected['outcome'])

    def test_direct_cli_selects_workflow_in_both_fence_orders(self):
        boundaries = "{'io': {'server': {'suite': {'transport': 'cli', 'runner': 'uv', 'path': 'suite.py'}}}}"
        cli = ("declare_cli_contract(interface='suite', action='run', "
               "outcomes={'succeeded': 'zero', 'failed': 'nonzero'})")
        workflow = _SOLUTION.split('```')[1].replace("component='C2'", "component='C15'")
        for framing_first in (True, False):
            with self.subTest(framing_first=framing_first), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                manifest_framing = _manifest('python framing', CONTRACT, boundaries=boundaries)
                manifest_cli = f'\n```python cli\n{cli}\n```\n'
                manifest = (manifest_framing + manifest_cli if framing_first else
                            manifest_framing.replace('\n```python framing', manifest_cli + '\n```python framing', 1))
                pins = _pins(root, manifest, SOLUTION)
                path = root / pins[1]['path']
                framing = path.read_text().replace('```python\n', '```python framing\n')
                workflow_fence = f'\n```{workflow}```\n'
                path.write_text(framing + workflow_fence if framing_first else
                                framing.replace('```python framing', workflow_fence + '```python framing', 1))
                report = check_cli_spec(root, 'C15', *pins, interface='suite', action='run', lean=self.lean)
                self.assertEqual('matched', report['directions']['manifest_solution']['status'], report)
                self.assertIn('stateDiagram-v2', report['mermaid'])

    def test_direct_trace_and_tool_select_workflow(self):
        tool = ("declare_tool_api_contract(operation='POST /tools', "
                "outcomes={'success': (200, 'result'), 'invalid_input': (400, 'typed_error'), "
                "'internal_error': (500, 'typed_error')})")
        for language, claim, check in (('python trace', TRACE, check_trace_spec),
                                       ('python contract', tool, check_tool_api_spec)):
            with self.subTest(language=language), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                manifest = (_manifest('python framing', CONTRACT)
                            + f'\n```{language}\n{claim}\n```\n')
                pins = _pins(root, manifest, SOLUTION)
                path = root / pins[1]['path']
                framing = path.read_text().replace('```python\n', '```python framing\n')
                path.write_text(framing + f'\n```python\n{TRACE_SOLUTION}\n```\n')
                report = check(root, 'C15', *pins, action='compile', lean=self.lean)
                self.assertIn('stateDiagram-v2', report['mermaid'])

    def test_framing_selection_rejects_reserved_workflow_name_in_either_carrier(self):
        for role, repeated in (('contract', False), ('contract', True), ('solution', False)):
            with self.subTest(role=role, repeated=repeated), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                trace, workflow = TRACE, TRACE_SOLUTION
                if role == 'contract':
                    trace = trace.replace("action='compile'", "action='framing'")
                else:
                    workflow = workflow.replace("action='compile'", "action='framing'")
                manifest = _manifest('python framing', CONTRACT)
                manifest += f'\n```python trace\n{trace}\n```\n'
                if repeated:
                    other = OTHER_TRACE.replace("action='compile'", "action='framing'")
                    manifest += f'\n```python trace\n{other}\n```\n'
                pins = _pins(root, manifest, SOLUTION)
                path = root / pins[1]['path']
                framing = path.read_text().replace('```python\n', '```python framing\n')
                path.write_text(framing + f'\n```python\n{workflow}\n```\n')
                result = verify_formal_chain(root, 'C15', *pins, action='framing', lean=self.lean)
                self.assertEqual('incomplete', result['outcome'])
                diagnostic, = result['diagnostics']
                self.assertIn("'framing' is reserved", diagnostic['message'])
                self.assertEqual(role, diagnostic['role'])
                pin = pins[1] if role == 'solution' else pins[0]
                self.assertEqual(pin['path'], diagnostic['source']['path'])

    def test_changed_lean_cannot_produce_a_comparison(self):
        def changed(model):
            compiled = compile_lean(model)
            compiled['lean'] = compiled['lean'].replace(
                'some (start, close, stop)', 'some (start, close, stop + 1)', 1)
            return compiled

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with patch('FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.formal_chain__pub.compile_lean', side_effect=changed):
                result = verify_formal_chain(root, 'C15', *framing_pins(root), lean=self.lean)
        self.assertEqual('incomplete', result['outcome'])
        self.assertEqual('conflicting', result['translation']['status'])
        self.assertNotIn('cases', result)
