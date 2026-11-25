import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from SPEC_ENGINE_C75.LAYER_3_LEAN_TRANSLATOR_C84.lean_spec__pub import compile_lean


CONTRACT = 'declare_framing_contract(delimiter=[45,45,45], line_endings=[[10],[13,10]])'
SOLUTION = (
    'declare_framing_solution(opening_prefixes=[[45,45,45,10],[45,45,45,13,10]], '
    'closing_prefixes=[[10,45,45,45,10],[13,10,45,45,45,13,10],'
    '[10,45,45,45,13,10],[13,10,45,45,45,10]])'
)
ASSERTIONS = '''
example : CarrierBodyContract.body [45,45,45,10,97,10,45,45,45,10,98] =
    CarrierBodyContract.Outcome.body [98] := by decide
example : CarrierBodySolution.body [45,45,45,10,97,10,45,45,45,10,98] =
    CarrierBodySolution.Outcome.body [98] := by decide
example : CarrierBodySolution.body [97,98] =
    CarrierBodySolution.Outcome.missingDelimiter := by decide
'''


def model(solution):
    return {
        'component_id': 'C52',
        'manifest': {'source': {'atom_id': 'M'},
                     'fields': {'component_id': 'C52', 'name': 'Core'}, 'boundaries': None},
        'contract': {'source': {'atom_id': 'C'}, 'claims': [('python framing', CONTRACT)]},
        'solution': {'source': {'atom_id': 'S'}, 'claims': [('python framing', solution)]},
    }


class LeanTranslationTests(unittest.TestCase):
    def test_framing_semantics_and_negative_control(self):
        lean = os.environ.get('ANECHOIC_TEST_LEAN') or os.environ.get('LEAN_BIN') or shutil.which('lean')
        self.assertTrue(lean, 'Set ANECHOIC_TEST_LEAN or LEAN_BIN, or put lean on PATH to run functional tests')
        valid = compile_lean(model(SOLUTION))
        changed = compile_lean(model(SOLUTION.replace('[10,45,45,45,10],', '')))
        for result in (valid, changed):
            self.assertEqual(['manifest', 'contract', 'solution'], result['compiled_roles'])
            self.assertFalse([gap for gap in result['unresolved']
                              if gap['field'] in ('contract', 'solution')])
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'Translation.lean'
            for source, succeeds in ((valid['lean'] + ASSERTIONS, True),
                                     (changed['lean'], True),
                                     (changed['lean'] + ASSERTIONS, False)):
                path.write_text(source)
                checked = subprocess.run([lean, str(path)], capture_output=True, text=True, timeout=45)
                if succeeds:
                    self.assertEqual(0, checked.returncode, checked.stdout + checked.stderr)
                else:
                    self.assertNotEqual(0, checked.returncode, checked.stdout + checked.stderr)

    def test_python_literals_survive_in_emitted_lean(self):
        lean = os.environ.get('ANECHOIC_TEST_LEAN') or os.environ.get('LEAN_BIN') or shutil.which('lean')
        self.assertTrue(lean, 'Set ANECHOIC_TEST_LEAN or LEAN_BIN, or put lean on PATH')
        boundary = model(SOLUTION)
        boundary['contract']['claims'] = [('python trace', r'''declare_trace_contract(
            action='run', output='done', must_effect=(('store', 'saved',
            {'flag': False, 'zero': 0, 'nothing': None, 'special': 'λ"\\\n\t'}),))''')]
        compiled = compile_lean(boundary)
        self.assertIn('contract', compiled['compiled_roles'])
        oracle = r'''
#eval match AnechoicSpec.contract, Lean.Json.parse r#"{"source":{"atom_id":"C"},"claim":{"action":"run","output":"done","must_effect":[["store","saved",{"flag":false,"zero":0,"nothing":null,"special":"λ\"\\\n\t"}]]}}"# with
  | .ok actual, .ok expected => actual == expected
  | _, _ => false
'''
        source = compiled['lean']
        self.assertEqual(1, source.count('false'))
        mutated = source.replace('false', 'true ', 1)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'Literals.lean'
            for program, expected in ((source, 'true'), (mutated, 'false')):
                path.write_text(program + oracle)
                checked = subprocess.run([lean, str(path)], capture_output=True, text=True, timeout=45)
                self.assertEqual(0, checked.returncode, checked.stdout + checked.stderr)
                self.assertEqual(expected, checked.stdout.strip())
