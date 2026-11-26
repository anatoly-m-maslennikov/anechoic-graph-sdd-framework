import os
import shutil
import unittest

from SPEC_ENGINE_C75.LAYER_3_LEAN_TRANSLATOR_C84.lean_check__pub import run_lean_json
from SPEC_ENGINE_C75.LAYER_3_LEAN_TRANSLATOR_C84.trace_lean__pub import _program
from SPEC_ENGINE_C75.LAYER_3_MERMAID_RENDERER_C87.workflow_diagram__pub import render_workflow_diagram


def workflow(expect):
    return {'action': 'run', 'initial': 'start', 'states': [
        {'name': 'start', 'final': False, 'transitions': [
            {'event': 'effect', 'target': 'end', 'expect': expect}]},
        {'name': 'end', 'final': False, 'transitions': [
            {'event': 'finish', 'target': 'done', 'expect': {'kind': 'output', 'outcome': 'ready'}}]},
        {'name': 'done', 'final': True, 'transitions': []},
    ]}


class NullTraceGuardTests(unittest.TestCase):
    def test_null_is_not_wildcard_in_lean(self):
        lean = os.environ.get('ANECHOIC_TEST_LEAN') or os.environ.get('LEAN_BIN') or shutil.which('lean')
        self.assertTrue(lean, 'Set ANECHOIC_TEST_LEAN or LEAN_BIN, or put lean on PATH')
        contract = {'action': 'run', 'output': 'ready', 'forbid_effect': ['reserved'],
                    'must_precede': [(('prior', 'done'), ('reserved', 'done'))]}
        for expect, statuses in [
            ({'kind': 'effect', 'outcome': 'done'}, ['conflicting', 'conflicting']),
            ({'kind': 'effect', 'target': None, 'outcome': 'done'}, ['matched', 'matched']),
            ({'kind': 'effect', 'target': 'reserved'}, ['conflicting', 'conflicting']),
            ({'kind': 'effect', 'target': 'reserved', 'outcome': None}, ['conflicting', 'matched']),
            ({'kind': 'effect', 'target': 'reserved', 'outcome': 'done'}, ['conflicting', 'conflicting']),
        ]:
            with self.subTest(expect=expect):
                self.assertEqual(['matched', *statuses, 'matched'],
                                 run_lean_json(_program(contract, workflow(expect)), lean))

    def test_mermaid_identifies_fields_and_explicit_null(self):
        labels = [render_workflow_diagram(workflow(expect)) for expect in (
            {'kind': 'output', 'target': 'ready'},
            {'kind': 'output', 'outcome': 'ready'},
            {'kind': 'output', 'target': None},
            {'kind': 'output'},
            {'kind': 'output', 'target': 'null'},
        )]
        self.assertEqual(len(labels), len(set(labels)))
        self.assertIn('target=null', labels[2])
        self.assertIn('target=#quot;null#quot;', labels[4])
