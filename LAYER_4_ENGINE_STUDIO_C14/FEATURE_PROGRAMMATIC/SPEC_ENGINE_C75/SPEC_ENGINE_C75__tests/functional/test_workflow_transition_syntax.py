import json
import unittest

from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_2_SPEC_READING_C83.SPECIFICATION_MODEL_C85._package__shared import normalize_workflow, parse_workflow
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_3_LEAN_TRANSLATOR_C84._package__shared import compile_lean
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_3_MERMAID_RENDERER_C87._package__shared import render_solution
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75._package__shared import compile_workflow


def machine(branch):
    return {'id': 'invoke', 'initial': 'start', 'states': {
        'start': {'on': {'finish': branch}}, 'done': {'type': 'final'}}}


class WorkflowTransitionSyntaxTests(unittest.TestCase):
    def test_equivalent_source_and_outputs(self):
        params = {'kind': 'output', 'outcome': 'done', 'detail': {'rows': 45}}
        branches = [{'target': 'done', 'guard': {'type': 'matchesTrace', 'params': params}},
                    {'to': 'done', 'expect': params}]
        compiled = []
        for branch in branches:
            source = f"component_workflow(component='C45', action='invoke', machine={machine(branch)!r})"
            parsed = parse_workflow(source)
            workflow = compile_workflow(parsed['machine'])
            model = {'component_id': 'C45',
                     'manifest': {'fields': {'component_id': 'C45', 'name': 'Backend'}, 'boundaries': None,
                                  'source': {'atom_id': 'AN-S-1'}},
                     'contract': {'claims': [], 'source': {'atom_id': 'AN-S-2'}},
                     'solution': {'claims': [('python', source)], 'source': {'atom_id': 'AN-S-3'}}}
            lean = compile_lean(model)
            self.assertIn('solution', lean['compiled_roles'])
            compiled.append((json.dumps(workflow['model'], sort_keys=True), workflow['mermaid'],
                             lean['lean'], render_solution(model, lean['claims']['solution'])))
        self.assertEqual(*compiled)

    def test_rejects_incomplete_mixed_and_invalid_branches(self):
        for branch in ({'to': 'done'}, {'expect': {'kind': 'output'}},
                       {'to': 'done', 'expect': {'kind': 'output'}, 'target': 'done'},
                       {'to': 'done', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'output'}}},
                       {'to': 'done', 'expect': {'kind': 'bad'}},
                       {'to': 'missing', 'expect': {'kind': 'output'}},
                       {'to': 'done', 'expect': {'kind': 'output', 'extra': 1}}):
            with self.subTest(branch=branch), self.assertRaises(ValueError):
                normalize_workflow(machine(branch))

    def test_mixed_alternative_branches_use_same_overlap_validation(self):
        branches = [{'to': 'done', 'expect': {'kind': 'output'}},
                    {'target': 'done', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'output'}}}]
        with self.assertRaisesRegex(ValueError, 'overlapping guards'):
            normalize_workflow(machine(branches))
