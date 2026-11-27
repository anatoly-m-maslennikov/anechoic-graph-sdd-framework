import json
import os
import subprocess
import sys
import unittest
from hashlib import sha256
from importlib import import_module
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_2_SPEC_READING_C83.SPECIFICATION_MODEL_C85._package__shared import normalize_workflow, parse_workflow
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94 \
    .LAYER_2_SPEC_READING_C83._package__shared import load_manifest
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94 \
    .LAYER_2_SPEC_READING_C83.SPECIFICATION_MODEL_C85._package__shared import (
        parse_trace_contract,
    )
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_3_LEAN_TRANSLATOR_C84._package__shared import compile_lean
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94 \
    .LAYER_3_MERMAID_RENDERER_C87._package__shared import (
        render_solution,
        render_workflow_diagram,
    )
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94 \
    .LAYER_4_SPEC_COMPARISON_C88._package__shared import compare_trace_values
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75._package__shared import (
    compile_workflow,
    verify_formal_chain,
)


def machine(branch):
    return {'id': 'invoke', 'initial': 'start', 'states': {
        'start': {'on': {'finish': branch}}, 'done': {'type': 'final'}}}


def _spec_pin(root, atom, owner):
    path, = (root / '_anechoic_anechoic').rglob(f'{atom}-*.md')
    return {'path': path.relative_to(root).as_posix(), 'atom_id': atom,
            'version': 6, 'status': 'active', 'container_component': owner,
            'sha256': sha256(path.read_bytes()).hexdigest()}


def _compilation_case():
    root = Path(__file__).resolve().parents[5]
    pin = _spec_pin(root, 'AN-S-3395', 'C15')
    claims = load_manifest(root, 'C75', pin)['contract']['claims']
    rule, = (rule for language, source in claims if language == 'python trace'
             if (rule := parse_trace_contract(source))['action']
             == 'compile_workflow')
    return next(case for case in rule['cases'] if case['output'] == 'compiled')


def _translated_handoff(source, root, scratch, authored, lean):
    implementation = scratch / 'Implementation.lean'
    digest = sha256(source.read_bytes()).hexdigest()
    tool = 'ARCHITECTURE_ANALYSIS_C73.IMPLEMENTATION_VERIFICATION_C74'
    subprocess.run(
        [sys.executable, '-B', '-m', f'{tool}.code_to_lean', str(source),
         '--sha256', digest, '--output', str(implementation)],
        cwd=root / 'LAYER_4_ENGINE_STUDIO_C14', capture_output=True,
        text=True, check=True, timeout=1800)
    witness = Path(__file__).with_name('workflow_handoff.lean').read_text()
    arena = scratch / 'Compare.lean'
    arena.write_text('import Lean\n' + implementation.read_text() + '\n'
                     + authored.removeprefix('import Lean\n') + '\n' + witness)
    result = subprocess.run(
        [lean, '-DwarningAsError=true', str(arena)], capture_output=True,
        text=True, check=True, timeout=120)
    return json.loads(result.stdout)


class WorkflowTransitionSyntaxTests(unittest.TestCase):
    def test_composite_labels_preserve_distinct_actions(self):
        configuration = machine({'to': 'done', 'expect': {'kind': 'output'}})
        operations = {}
        for action in ("check/a", "check_a", ' x%%;"\n '):
            source = (
                f"component_workflow(component='C87', action={action!r}, "
                f"machine={configuration!r})"
            )
            claim = parse_workflow(source)
            operations[claim['action']] = normalize_workflow(claim['machine'])
        model = {'solution': {'claims': [('python workflow', '')]}}
        diagram = render_solution(model, {'operations': operations})
        self.assertIn('operation_1_check_a: check/a', diagram)
        self.assertIn('operation_2_check_a: check_a', diagram)
        self.assertIn('operation_3__x______: #32;x#37;#37;#59;#34;#10;#32;',
                      diagram)
        self.assertIn('[*] --> operation_1_check_a_S0', diagram)
        self.assertIn('operation_2_check_a_S0 --> operation_2_check_a_S1',
                      diagram)

    def test_compilation_renders_and_returns_the_same_model(self):
        configuration = machine({'to': 'done', 'expect': {'kind': 'output'}})
        case = _compilation_case()
        expected = normalize_workflow(configuration)
        module = import_module(compile_workflow.__module__)
        self.assertIs(module.normalize_workflow, normalize_workflow)
        self.assertIs(module.render_workflow_diagram, render_workflow_diagram)
        with patch.object(module, 'render_workflow_diagram',
                          wraps=module.render_workflow_diagram) as render:
            result = compile_workflow(configuration)
            observed = render.call_args.args[0]
            render.assert_called_once()
            with self.assertRaises(ValueError):
                compile_workflow({**configuration, 'initial': 'missing'})
            render.assert_called_once()
        events = [
            {'event': 'C75.workflow_model', 'detail': {'model': expected}},
            {'event': 'C75.workflow_diagram', 'detail': {'model': observed}},
            {'event': 'result', 'detail': result},
        ]
        changed = {**events[1],
                   'detail': {'model': {**observed, 'id': 'other'}}}
        for rows, status in (
            (events, 'matched'),
            ([events[0], changed, events[2]], 'conflicting'),
            ([events[0], events[2]], 'unresolved'),
        ):
            with self.subTest(status=status):
                report = compare_trace_values(case, rows)
                self.assertEqual(status, report['status'], report)

    @unittest.skipUnless(all(os.environ.get(name) for name in (
        'AUTOFORM_CHECKOUT', 'JOERN_HOME', 'LEAN_PATH')),
        'Autoform and its Lean libraries are not configured')
    def test_translated_workflow_preserves_the_authored_handoff(self):
        root = Path(__file__).resolve().parents[5]
        pins = {'manifest': _spec_pin(root, 'AN-S-3395', 'C15'),
                'solution': _spec_pin(root, 'AN-S-5022', 'C75')}
        lean = os.environ.get('ANECHOIC_TEST_LEAN', 'lean')
        formal = verify_formal_chain(root, 'C75', **pins,
                                     action='compile_workflow', lean=lean)
        self.assertEqual(pins, formal['sources'])
        self.assertEqual('matched', formal['translation']['status'])
        self.assertEqual('compile_workflow', formal['evidence']['action'])
        self.assertFalse(formal['issues'], formal)
        module = import_module(compile_workflow.__module__)
        source = Path(module.__file__)
        self.assertEqual('workflow_model__pub.py', source.name)
        self.assertIs(compile_workflow, module.compile_workflow)
        raw = source.read_bytes()
        call = b'render_workflow_diagram(model)'
        self.assertEqual(1, raw.count(call))
        expected = dict.fromkeys((
            'spec', 'imports', 'input', 'ordered', 'render_model',
            'return_model', 'return_diagram', 'invalid'), True)
        with TemporaryDirectory() as directory:
            work = Path(directory)
            baseline = _translated_handoff(
                source, root, work, formal['lean'], lean)
            self.assertEqual(expected, baseline)
            changed = work / source.name
            changed.write_bytes(raw.replace(
                call, b'render_workflow_diagram(config)'))
            mutant = _translated_handoff(
                changed, root, work, formal['lean'], lean)
        self.assertEqual({**expected, 'render_model': False}, mutant)

    def test_equivalent_source_and_outputs(self):
        params = {"kind": "output", "outcome": "done", "detail": {"rows": 45}}
        branches = [
            {
                "target": "done",
                "guard": {"type": "matchesTrace", "params": params},
            },
            {"to": "done", "expect": params},
        ]
        compiled = []
        for branch in branches:
            source = f"component_workflow(component='C45', action='invoke', machine={machine(branch)!r})"
            parsed = parse_workflow(source)
            workflow = compile_workflow(parsed["machine"])
            model = {
                "component_id": "C45",
                "manifest": {
                    "fields": {"component_id": "C45", "name": "Backend"},
                    "boundaries": None,
                    "source": {"atom_id": "AN-S-1"},
                },
                "contract": {"claims": [], "source": {"atom_id": "AN-S-2"}},
                "solution": {
                    "claims": [("python", source)],
                    "source": {"atom_id": "AN-S-3"},
                },
            }
            lean = compile_lean(model)
            self.assertIn("solution", lean["compiled_roles"])
            compiled.append(
                (
                    json.dumps(workflow["model"], sort_keys=True),
                    workflow["mermaid"],
                    lean["lean"],
                    render_solution(model, lean["claims"]["solution"]),
                )
            )
        self.assertEqual(*compiled)

    def test_rejects_incomplete_mixed_and_invalid_branches(self):
        for branch in (
            {"to": "done"},
            {"expect": {"kind": "output"}},
            {"to": "done", "expect": {"kind": "output"}, "target": "done"},
            {
                "to": "done",
                "guard": {
                    "type": "matchesTrace",
                    "params": {"kind": "output"},
                },
            },
            {"to": "done", "expect": {"kind": "bad"}},
            {"to": "missing", "expect": {"kind": "output"}},
            {"to": "done", "expect": {"kind": "output", "extra": 1}},
        ):
            with self.subTest(branch=branch), self.assertRaises(ValueError):
                normalize_workflow(machine(branch))

    def test_mixed_alternative_branches_use_same_overlap_validation(self):
        branches = [
            {"to": "done", "expect": {"kind": "output"}},
            {
                "target": "done",
                "guard": {
                    "type": "matchesTrace",
                    "params": {"kind": "output"},
                },
            },
        ]
        with self.assertRaisesRegex(ValueError, "overlapping guards"):
            normalize_workflow(machine(branches))
