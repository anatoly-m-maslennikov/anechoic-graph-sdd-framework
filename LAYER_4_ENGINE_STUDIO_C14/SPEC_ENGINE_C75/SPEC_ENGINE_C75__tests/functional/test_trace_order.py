import os
import shutil
import unittest

from SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C85.contract_model__pub import parse_trace_contract
from SPEC_ENGINE_C75.LAYER_4_SPEC_COMPARISON_C88.trace_spec__pub import compare_trace_workflow
from SPEC_ENGINE_C75.workflow_model__pub import compile_workflow


from test_trace_spec import transition


class OrderedTraceTests(unittest.TestCase):
    def test_typed_order(self):
        lean = os.environ.get('ANECHOIC_TEST_LEAN') or shutil.which('lean')
        if lean is None:
            self.skipTest('Lean unavailable')
        contract = parse_trace_contract("declare_trace_contract(action='admit', output='ready', "
            "must_effect=(('convert', 'done', {'version': 'current'}),), "
            "must_precede=((('convert', 'done', {'version': 'old'}), "
            "('convert', 'done', {'version': 'current'})),))")
        machine = {'id': 'admit', 'initial': 'start', 'states': {
            'start': {'on': {'first': transition('middle', 'effect', 'convert', 'done')}},
            'middle': {'on': {'second': transition('end', 'effect', 'convert', 'done')}},
            'end': {'on': {'output': transition('done', 'output', outcome='ready')}},
            'done': {'type': 'final'}}}
        first = machine['states']['start']['on']['first']['guard']['params']
        second = machine['states']['middle']['on']['second']['guard']['params']
        first['detail'], second['detail'] = {'version': 'old'}, {'version': 'current'}
        def status():
            workflow = {'action': 'admit', **compile_workflow(machine)['model']}
            return {fact['key']: fact['status'] for fact in compare_trace_workflow(contract, workflow, lean=lean)['facts']}
        self.assertEqual('matched', status()['must_precede'])
        first['detail'], second['detail'] = second['detail'], first['detail']
        self.assertEqual('matched', status()['must_effect'])
        self.assertEqual('conflicting', status()['must_precede'])

    def test_order_literals(self):
        prefix = "declare_trace_contract(action='admit', output='ready', must_effect=(('draft', 'called'),), "
        valid = "must_precede=((('gate', 'passed'), ('draft', 'called')),)"
        claim = parse_trace_contract(prefix + valid + ')')
        self.assertEqual([(('gate', 'passed'), ('draft', 'called'))], claim['must_precede'])
        for value in ("()", "((('gate', 'passed'), ('other', 'called')),)",
                      "((('gate', 'passed'),),)", "((('gate', 'passed'), ('draft', 'called')),)*2"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                parse_trace_contract(prefix + 'must_precede=' + value + ')')
        with self.assertRaises(ValueError):
            parse_trace_contract("declare_trace_contract(action='a', output='o', forbid_effect=('x',), " + valid + ')')
        from SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C85.contract_model__pub import parse_cli_contract
        cli = "declare_cli_contract(interface='i', action='admit', runner='r', path='p', output='ready', "
        self.assertEqual(claim['must_precede'], parse_cli_contract(cli + "must_effect=(('draft', 'called'),), " + valid + ')')['trace']['must_precede'])

    def test_order_paths_and_wildcards(self):
        lean = os.environ.get('ANECHOIC_TEST_LEAN') or shutil.which('lean')
        if lean is None:
            self.skipTest('Lean unavailable')
        contract = parse_trace_contract("declare_trace_contract(action='admit', output='ready', "
            "must_effect=(('draft', 'called'),), must_precede=((('gate', 'passed'), ('draft', 'called')) ,))")
        machine = {'id': 'admit', 'initial': 'start', 'states': {
            'start': {'on': {'first': transition('middle', 'effect', 'gate', 'passed')}},
            'middle': {'on': {'second': transition('end', 'effect', 'draft', 'called')}},
            'end': {'on': {'output': transition('done', 'output', outcome='ready')}},
            'done': {'type': 'final'}}}

        def facts():
            workflow = {'action': 'admit', **compile_workflow(machine)['model']}
            return {fact['key']: fact['status'] for fact in compare_trace_workflow(contract, workflow, lean=lean)['facts']}

        self.assertEqual('matched', facts()['must_precede'])
        first = machine['states']['start']['on']['first']['guard']['params']
        second = machine['states']['middle']['on']['second']['guard']['params']
        first['target'], second['target'] = second['target'], first['target']
        first['outcome'], second['outcome'] = second['outcome'], first['outcome']
        self.assertEqual('matched', facts()['must_effect'])
        self.assertEqual('conflicting', facts()['must_precede'])
        first['target'], second['target'] = second['target'], first['target']
        first['outcome'], second['outcome'] = second['outcome'], first['outcome']
        machine['states']['start']['on']['other'] = transition('other', 'effect', None, None)
        machine['states']['other'] = {'on': {'output': transition('done', 'output', outcome='other')}}
        self.assertEqual('matched', facts()['must_precede'])
        machine['states']['other']['on']['output']['guard']['params']['outcome'] = 'ready'
        self.assertEqual('conflicting', facts()['must_precede'])
