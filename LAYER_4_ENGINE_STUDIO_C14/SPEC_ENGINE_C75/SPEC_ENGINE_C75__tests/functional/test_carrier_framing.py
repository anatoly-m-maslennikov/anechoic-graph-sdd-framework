import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from SPEC_ENGINE_C75.carrier_framing__pub import (
    framing_to_lean,
    framing_to_mermaid,
    parse_framing,
)

CONTRACT = 'declare_framing_contract(delimiter=[45,45,45], line_endings=[[10],[13,10]])'
SOLUTION = ('declare_framing_solution(opening_prefixes=[[45,45,45,10],[45,45,45,13,10]], '
            'closing_prefixes=[[13,10,45,45,45,13,10],[13,10,45,45,45,10],'
            '[10,45,45,45,13,10],[10,45,45,45,10]])')
LEAN = shutil.which('lean')
WITNESSES = (
    (b'---\na: b\n---\nbody\x00\xff', (4, 8, 13), b'body\x00\xff'),
    (b'---\r\na: b\r\n---\r\nbody', (5, 9, 16), b'body'),
    (b'---\n---\nbody', (4, 3, 8), b'body'),
    (b'---\r\n---\r\nbody', (5, 4, 10), b'body'),
    (b'body', None, None),
    (b'---\na: b\nbody', None, None),
    (b'---\r\na\n---\r\nbody', (5, 6, 12), b'body'),
    (b'---\na\n---\nbody\n---\nlast', (4, 5, 10), b'body\n---\nlast'),
)


def _overlap_model():
    source = ('declare_framing_solution(opening_prefixes=[[35,10]], '
              'closing_prefixes=[[10,35],[10,35,10]])')
    return framing_to_lean(parse_framing(source, 'solution'), 'solution').replace(
        'CarrierBodySolution', 'OverlapSolution')


class CarrierFramingTests(unittest.TestCase):
    def test_rejects_nonliteral_and_malformed(self):
        for source in (
            'declare_framing_contract(delimiter=[45], line_endings=[[10]], delimiter=[45])',
            'declare_framing_contract(delimiter=[45], line_endings=[[10],[10]])',
            'declare_framing_contract(delimiter=[True], line_endings=[[10]])',
            'declare_framing_contract(delimiter=[256], line_endings=[[10]])',
            'declare_framing_contract(delimiter=[], line_endings=[[10]])',
            'declare_framing_contract(delimiter=[45], line_endings=[[]])',
            'declare_framing_contract(delimiter=list([45]), line_endings=[[10]])',
            CONTRACT + '\nprint(1)',
        ):
            with self.subTest(source=source), self.assertRaises(ValueError):
                parse_framing(source, 'contract')
        with self.assertRaises(ValueError):
            framing_to_lean({'delimiter': (45,), 'line_endings': ((10,),)}, 'solution')

    def test_mermaid_shows_scanner_and_outcomes(self):
        diagram = framing_to_mermaid(parse_framing(SOLUTION, 'solution'))
        self.assertIn('Scan from opening minus one', diagram)
        self.assertIn('Missing delimiter', diagram)
        self.assertIn('unchanged body tail', diagram)

    @unittest.skipUnless(LEAN, 'Lean executable unavailable')
    def test_generated_models_match_formal_witnesses(self):
        generated = [framing_to_lean(parse_framing(src, role), role)
                     for src, role in ((CONTRACT, 'contract'), (SOLUTION, 'solution'))]
        checks = []
        for ns in ('CarrierBodyContract', 'CarrierBodySolution'):
            for raw, bounds, body in WITNESSES:
                value = str(list(raw))
                bound_form = 'none' if bounds is None else f'some {bounds}'
                outcome = 'missingDelimiter' if body is None else f'body {list(body)}'
                checks.append(f'{ns}.bounds {value} == {bound_form}')
                checks.append(f'{ns}.body {value} == {ns}.Outcome.{outcome}')
        alternate = (
            ('contract', 'declare_framing_contract(delimiter=[35], line_endings=[[10]])',
             'CarrierBodyContract'),
            ('solution', ('declare_framing_solution(opening_prefixes=[[35,10]], '
                          'closing_prefixes=[[10,35,10]])'), 'CarrierBodySolution'),
        )
        for role, source, ns in alternate:
            generated.append(framing_to_lean(parse_framing(source, role), role)
                             .replace(ns, 'Alternate' + ns))
            checks.append(f'Alternate{ns}.bounds [35,10,97,10,35,10,0] == some (2,3,6)')
            checks.append(f'Alternate{ns}.body [35,10,97,10,35,10,0] == '
                          f'Alternate{ns}.Outcome.body [0]')
        generated.append(_overlap_model())
        checks.append('OverlapSolution.bounds [35,10,97,10,35,10] == some (2,3,5)')
        program = 'import Lean\n' + '\n'.join(generated)
        program += '\n#eval IO.println (' + ' && '.join(checks) + ')\n'
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'Framing.lean'
            path.write_text(program)
            result = subprocess.run([str(LEAN), str(path)], capture_output=True, text=True, timeout=120, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stdout.strip(), 'true')
