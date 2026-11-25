import itertools
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C85.contract_model__pub import (
    parse_trace_contract,
)
from SPEC_ENGINE_C75.LAYER_3_LEAN_TRANSLATOR_C84.trace_lean__pub import _program
from SPEC_ENGINE_C75.workflow_model__pub import compile_workflow


def transition(target, kind, observed=None, outcome=None, detail=None):
    params = {'kind': kind, 'target': observed, 'outcome': outcome}
    if detail is not None:
        params['detail'] = detail
    return {'target': target, 'guard': {'type': 'matchesTrace', 'params': params}}


def workflow(first, second, alternate=None):
    states = {
        'start': {'on': {'first': first}},
        'middle': {'on': {'second': second}},
        'end': {'on': {'output': transition('done', 'output', outcome='ready')}},
        'done': {'type': 'final'},
    }
    if alternate:
        states['start']['on']['alternate'] = transition('done', 'output', outcome=alternate)
    return {'action': 'run', **compile_workflow({'id': 'run', 'initial': 'start', 'states': states})['model']}


class ConstructCombinationTests(unittest.TestCase):
    def test_generated_trace_combinations(self):
        lean = os.environ.get('ANECHOIC_TEST_LEAN') or os.environ.get('LEAN_BIN') or shutil.which('lean')
        self.assertTrue(lean, 'Set ANECHOIC_TEST_LEAN or LEAN_BIN, or put lean on PATH')
        programs, expected = [], []
        contract = parse_trace_contract("declare_trace_contract(action='run', output='ready', "
            "must_effect=(('convert', 'done', {'version': 'current'}),), "
            "must_precede=((('convert', 'done', {'version': 'old'}), "
            "('convert', 'done', {'version': 'current'})),))")
        # The current-then-old pair is the minimized order regression.
        # The table requires a current effect and an earlier old effect.
        for first, second in itertools.product(('old', 'current'), repeat=2):
            first_edge = transition('middle', 'effect', 'convert', 'done', {'version': first})
            second_edge = transition('end', 'effect', 'convert', 'done', {'version': second})
            programs.append(_program(contract, workflow(first_edge, second_edge)))
            effect = 'matched' if 'current' in (first, second) else 'conflicting'
            order = 'matched' if (first, second) in (('old', 'old'), ('old', 'current')) else 'conflicting'
            expected.append(['matched', effect, order, 'matched'])

        bound = parse_trace_contract("declare_trace_contract(action='run', output='ready', "
            "must_effect=(('query', 'done', {'rows': {'at_most': 2}}),))")
        # A ready alternate bypasses the bound; an alternate output does not.
        for rows, alternate in itertools.product((2, 3), (None, 'failed', 'ready')):
            first_edge = transition('middle', 'effect', 'query', 'done', {'rows': rows})
            second_edge = transition('end', 'trigger')
            programs.append(_program(bound, workflow(first_edge, second_edge, alternate)))
            expected.append(['matched', 'matched' if rows <= 2 and alternate != 'ready' else 'conflicting', 'matched'])

        source = 'import Lean\n' + '\n'.join(
            f'namespace Case{i}\n{program[12:]}\nend Case{i}'
            for i, program in enumerate(programs))
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'Combinations.lean'
            path.write_text(source, encoding='utf-8')
            result = subprocess.run([lean, str(path)], capture_output=True, text=True, timeout=45, check=False)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual(expected, [json.loads(line) for line in result.stdout.splitlines()])
