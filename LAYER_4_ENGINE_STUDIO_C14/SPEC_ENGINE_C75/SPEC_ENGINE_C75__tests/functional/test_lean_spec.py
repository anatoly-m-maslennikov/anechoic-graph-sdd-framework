import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from SPEC_ENGINE_C75.lean_spec__pub import compile_lean


_CONTRACT = """declare_contract(operation='POST /tools', outcomes={
    'success': (200, 'result'), 'invalid_input': (400, 'typed_error'),
    'internal_error': (500, 'typed_error')})"""
_SOLUTION = """component_workflow(component='C45', action='invoke', machine={
    'id': 'invoke', 'initial': 'start', 'states': {
        'start': {'on': {'finish': {'target': 'done', 'guard': {
            'type': 'matchesTrace', 'params': {'kind': 'output'}}}}},
        'done': {'type': 'final'}}})"""


class LeanSpecTests(unittest.TestCase):
    def test_tool_contract_and_status_trace_keep_separate_operations(self):
        from SPEC_ENGINE_C75.tool_api_spec__pub import _tool_contract, _tool_solution

        model = self._model()
        model['contract']['claims'].append(('python trace',
            "declare_trace_contract(action='status', output='succeeded', "
            "must_effect=(('status', 'returned'),))"))
        tool = _SOLUTION.replace("'kind': 'output'", "'kind': 'trigger', 'detail': {'operation': 'POST /tools'}")
        status = tool.replace("'invoke'", "'status'").replace('POST /tools', 'GET /status')
        model['solution']['claims'] = [('python', tool), ('python', status)]
        compiled = compile_lean(model)
        self.assertEqual(['manifest', 'contract', 'solution'], compiled['compiled_roles'])
        claims = compiled['claims']
        self.assertEqual('POST /tools', _tool_contract(claims['contract'])['operation'])
        self.assertIn('status', claims['contract']['operations'])
        self.assertEqual(['POST /tools'], _tool_solution(claims['solution'], 'POST /tools', None)['operation'])
        self.assertEqual(['GET /status'], _tool_solution(claims['solution'], 'POST /tools', 'status')['operation'])

    def test_same_workflow_model_emits_lean_and_mermaid(self):
        model = self._model()
        compiled = compile_lean(model)
        self.assertEqual(['manifest', 'contract', 'solution'], compiled['compiled_roles'])
        self.assertIn('start --> done : finish / output', compiled['mermaid'])
        self.assertIn('AN-S-3', compiled['lean'])
        self.assertIn('finish', compiled['lean'])
        lean = shutil.which('lean')
        if lean is not None:
            with tempfile.TemporaryDirectory() as directory:
                program = Path(directory) / 'Spec.lean'
                program.write_text(compiled['lean'] + '\n#eval AnechoicSpec.solution.isOk\n')
                checked = subprocess.run([lean, str(program)], capture_output=True, text=True, timeout=60)
                self.assertEqual(0, checked.returncode, checked.stdout + checked.stderr)
                self.assertEqual('true', checked.stdout.strip())

    def test_unsupported_claim_keeps_its_source(self):
        model = self._model()
        model['solution']['claims'] = [('lean', 'def solution := True')]
        compiled = compile_lean(model)
        self.assertEqual(['manifest', 'contract'], compiled['compiled_roles'])
        self.assertIsNone(compiled['mermaid'])
        self.assertEqual(model['solution']['source'], compiled['unresolved'][-1]['source'])

    def test_startup_arguments_are_emitted_and_validated(self):
        model = self._model()
        original = compile_lean(model)
        source = _SOLUTION.replace("action='invoke',", "action='invoke', startup={'required_arguments': ['--socket', '--project-root']},")
        model['solution']['claims'] = [('python', source)]
        compiled = compile_lean(model)
        self.assertEqual({'required_arguments': ['--socket', '--project-root']},
                         compiled['claims']['solution']['startup'])
        self.assertIn('--project-root', compiled['lean'])
        self.assertEqual(original['mermaid'], compiled['mermaid'])
        self.assertNotIn('startup', original['claims']['solution'])
        for invalid in ("['--socket', '--socket']", "['socket']", "['--bad flag']", "'--socket'",
                        "[1]", "['--socket=foo']"):
            with self.subTest(invalid=invalid):
                model['solution']['claims'] = [('python', source.replace("['--socket', '--project-root']", invalid))]
                result = compile_lean(model)
                self.assertNotIn('solution', result['compiled_roles'])
                self.assertTrue(result['unresolved'])

    def _model(self):
        fields = {'component_id': 'C45', 'name': 'Backend'}
        return {'component_id': 'C45', 'manifest': {'fields': fields, 'boundaries': None,
                                                    'source': {'atom_id': 'AN-S-1'}},
                'contract': {'claims': [('python contract', _CONTRACT)], 'source': {'atom_id': 'AN-S-2'}},
                'solution': {'claims': [('python', _SOLUTION)], 'source': {'atom_id': 'AN-S-3'}}}
