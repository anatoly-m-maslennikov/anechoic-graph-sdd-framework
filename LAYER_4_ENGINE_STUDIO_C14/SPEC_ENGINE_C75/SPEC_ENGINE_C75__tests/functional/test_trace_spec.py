import os
import shutil
import unittest

from SPEC_ENGINE_C75.contract_model__pub import parse_trace_contract
from SPEC_ENGINE_C75.trace_spec__pub import compare_trace_workflow
from SPEC_ENGINE_C75.workflow_model__pub import compile_workflow


CONTRACT = "declare_trace_contract(action='admit', output='ready', must_effect=(('kernel', 'ready'),))"


def transition(target, kind, observed=None, outcome=None):
    return {'target': target, 'guard': {'type': 'matchesTrace', 'params': {
        'kind': kind, 'target': observed, 'outcome': outcome}}}


class TraceSpecTests(unittest.TestCase):
    def test_contract_rejects_bad_literals(self):
        for effects in ("()", "(('kernel', ''),)", "(('a', 'b'), ('a', 'b'))", "[('a', 'b')]", "(('a', x),)"):
            with self.subTest(effects=effects), self.assertRaises(ValueError):
                parse_trace_contract(CONTRACT.replace("(('kernel', 'ready'),)", effects))

    def test_lean_detects_bypass_and_missing_output(self):
        lean = os.environ.get('ANECHOIC_TEST_LEAN') or shutil.which('lean')
        if lean is None:
            self.skipTest('Lean unavailable')
        machine = {'id': 'admit', 'initial': 'start', 'states': {
            'start': {'on': {'effect': transition('seen', 'effect', 'kernel', 'ready')}},
            'seen': {'on': {'output': transition('done', 'output', outcome='ready')}},
            'done': {'type': 'final'}}}
        contract = parse_trace_contract(CONTRACT)
        def compare():
            return compare_trace_workflow(contract, {'action': 'admit', **compile_workflow(machine)['model']}, lean=lean)
        self.assertEqual('matched', compare()['status'])
        machine['states']['start']['on']['bypass'] = transition('seen', 'trigger')
        self.assertEqual('conflicting', compare()['status'])
        machine['states']['start']['on']['bypass'] = transition('done', 'output')
        self.assertEqual('conflicting', compare()['status'])
        machine['states']['start']['on']['bypass'] = transition('done', 'output', outcome='')
        self.assertEqual('matched', compare()['status'])
        del machine['states']['start']['on']['bypass']
        machine['states']['seen']['on']['output']['guard']['params']['outcome'] = 'other'
        self.assertEqual('unresolved', compare()['status'])

    def test_forbidden_effect_contract_literals_and_cli(self):
        from SPEC_ENGINE_C75.contract_model__pub import parse_cli_contract

        prefix = "declare_trace_contract(action='admit', output='ready', forbid_effect="
        for value in ("()", "['state']", "('',)", "('state', 'state')", "(target,)"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                parse_trace_contract(prefix + value + ')')
        self.assertEqual(['state'], parse_trace_contract(prefix + "('state',))")['forbid_effect'])
        both = parse_trace_contract(CONTRACT[:-1] + ", forbid_effect=('state',))")
        self.assertIn('must_effect', both)
        self.assertIn('forbid_effect', both)
        cli = "declare_cli_contract(interface='i', action='admit', runner='r', path='p', "
        self.assertEqual(['state'], parse_cli_contract(cli + "output='ready', forbid_effect=('state',))")
                         ['trace']['forbid_effect'])
        for fields in ("output='ready'", "forbid_effect=('state',)"):
            with self.assertRaises(ValueError):
                parse_cli_contract(cli + fields + ')')

    def test_trace_rejects_contradictory_effects(self):
        with self.assertRaisesRegex(ValueError, 'required and forbidden effects contradict'):
            parse_trace_contract(CONTRACT[:-1] + ", forbid_effect=('kernel',))")
        suffix = ", must_precede=((('gate', 'passed'), ('kernel', 'ready')),), forbid_effect=('gate',))"
        with self.assertRaisesRegex(ValueError, 'required and forbidden effects contradict'):
            parse_trace_contract(CONTRACT[:-1] + suffix)

    def test_forbidden_effect_paths(self):
        lean = os.environ.get('ANECHOIC_TEST_LEAN') or shutil.which('lean')
        if lean is None:
            self.skipTest('Lean unavailable')
        contract = parse_trace_contract("declare_trace_contract(action='admit', output='dry', "
                                        "forbid_effect=('service_state',))")
        machine = {'id': 'admit', 'initial': 'start', 'states': {
            'start': {'on': {'dry': transition('done', 'output', outcome='dry'),
                             'apply': transition('applied', 'effect', 'service_state')}},
            'applied': {'on': {'output': transition('done', 'output', outcome='apply')}},
            'done': {'type': 'final'}}}

        def status():
            workflow = {'action': 'admit', **compile_workflow(machine)['model']}
            return compare_trace_workflow(contract, workflow, lean=lean)['facts'][1]['status']

        self.assertEqual('matched', status())
        output = machine['states']['applied']['on']['output']['guard']['params']
        output['outcome'] = 'dry'
        self.assertEqual('conflicting', status())
        output['outcome'] = None
        self.assertEqual('conflicting', status())
        effect = machine['states']['start']['on']['apply']['guard']['params']
        effect['target'] = None
        self.assertEqual('conflicting', status())
        effect['target'] = ''
        self.assertEqual('matched', status())
        machine['states']['start']['on']['dry']['guard']['params']['outcome'] = None
        self.assertEqual('unresolved', status())


class HttpBindingTests(unittest.TestCase):
    def test_multiple_outcomes_require_the_same_endpoint(self):
        from SPEC_ENGINE_C75.lean_spec__pub import _contract_operations

        binding = ", interface='api', transport='http', route='POST /db', operation='query')"
        ready = CONTRACT[:-1] + binding
        failed = ("declare_trace_contract(action='admit', output='failed', "
                  "forbid_effect=('kernel',)" + binding)
        claims = [('python trace', ready), ('python trace', failed)]

        profile = _contract_operations(claims)
        self.assertEqual('POST /db', profile['route'])
        self.assertEqual(['ready', 'failed'], [case['output'] for case in profile['cases']])
        for changed in (failed.replace('/db', '/other'), failed.removesuffix(binding) + ')'):
            with self.subTest(changed=changed), self.assertRaisesRegex(ValueError, 'share one binding'):
                _contract_operations([claims[0], ('python trace', changed)])

    def test_binding_literals_are_all_or_none(self):
        fields = ", interface='database_api', route='query', transport='http', operation='POST /database'"
        self.assertEqual('query', parse_trace_contract(CONTRACT[:-1] + fields + ')')['route'])
        for suffix in (", interface='api'", fields.replace("'http'", "'cli'"),
                       fields.replace("'query'", "''"), fields.replace("'query'", 'name')):
            with self.subTest(suffix=suffix), self.assertRaises(ValueError):
                parse_trace_contract(CONTRACT[:-1] + suffix + ')')

    def test_binding_comparison(self):
        from SPEC_ENGINE_C75.trace_spec__pub import _binding_directions

        lean = os.environ.get('ANECHOIC_TEST_LEAN') or shutil.which('lean')
        if lean is None:
            self.skipTest('Lean unavailable')
        contract = dict(interface='database_api', route='query', transport='http', operation='POST /database')
        server = {'transport': 'http', 'routes': {'query': 'POST /database'}}
        claims = {'manifest': {'boundaries': {'io': {'server': {'database_api': server}}}}}
        expect = {'kind': 'trigger', 'target': 'database_api', 'detail': {
            'route': 'query', 'transport': 'http', 'operation': 'POST /database'}}
        transitions = [{'expect': expect}]
        workflow = {'initial': 'start', 'states': [{'name': 'start', 'transitions': transitions}]}
        sources = dict.fromkeys(('manifest', 'contract', 'solution'), 'source')

        def statuses():
            return {key: value['status'] for key, value in
                    _binding_directions(sources, claims, contract, workflow, lean).items()}

        self.assertEqual({'manifest_contract': 'matched', 'manifest_solution': 'matched',
                          'contract_solution': 'matched'}, statuses())
        server['routes']['query'] = 'POST /other'
        self.assertEqual('conflicting', statuses()['manifest_contract'])
        server['routes']['query'] = 'POST /database'
        expect['detail']['operation'] = 'POST /other'
        self.assertEqual('conflicting', statuses()['contract_solution'])
        expect['detail']['operation'] = 'POST /database'
        del server['routes']['query']
        self.assertEqual('conflicting', statuses()['manifest_contract'])
        server['routes']['query'] = 'POST /database'
        del expect['detail']['route']
        self.assertEqual('unresolved', statuses()['contract_solution'])
        expect['detail']['route'] = 'query'
        transitions.append({'expect': {'kind': 'trigger'}})
        self.assertEqual('conflicting', statuses()['contract_solution'])
        claims['manifest']['boundaries']['io']['server'] = 'unsupported'
        self.assertEqual('unresolved', statuses()['manifest_contract'])

    def test_bound_trace_combines_endpoint_and_effect_scope(self):
        from unittest.mock import patch
        from SPEC_ENGINE_C75.trace_spec__pub import check_trace_spec

        lean = os.environ.get('ANECHOIC_TEST_LEAN') or shutil.which('lean')
        if lean is None:
            self.skipTest('Lean unavailable')
        fields = ", interface='api', route='query', transport='http', operation='POST /db'"
        contract = parse_trace_contract(CONTRACT[:-1] + fields + ')')
        trigger = transition('seen', 'trigger', 'api')
        trigger['guard']['params']['detail'] = {'route': 'query', 'transport': 'http', 'operation': 'POST /db'}
        machine = {'id': 'admit', 'initial': 'start', 'states': {
            'start': {'on': {'trigger': trigger}},
            'seen': {'on': {'effect': transition('returning', 'effect', 'kernel', 'ready')}},
            'returning': {'on': {'output': transition('done', 'output', outcome='ready')}},
            'done': {'type': 'final'}}}
        workflow = {'action': 'admit', **compile_workflow(machine)['model']}
        manifest = {'boundaries': {'io': {'server': {'api': {'transport': 'http', 'routes': {'query': 'POST /db'}}}}}}
        model = {role: {'source': role, 'claims': []} for role in ('manifest', 'contract', 'solution')}
        model['contract']['claims'] = [('python trace', '')]
        compiled = {'claims': {'manifest': manifest, 'contract': contract, 'solution': workflow},
                    'issues': [], 'unresolved': [], 'mermaid': ''}
        with patch('SPEC_ENGINE_C75.boundary_model.load_boundary_model', return_value=model), \
             patch('SPEC_ENGINE_C75.lean_spec__pub.compile_lean', return_value=compiled):
            report = check_trace_spec(None, 'C1', None, None, None, lean=lean)
            self.assertEqual('matched', report['status'])
            workflow['states'][1]['transitions'][0]['expect']['target'] = 'wrong'
            report = check_trace_spec(None, 'C1', None, None, None, lean=lean)
            self.assertEqual('conflicting', report['directions']['contract_solution']['status'])

class OrderedTraceTests(unittest.TestCase):
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
        from SPEC_ENGINE_C75.contract_model__pub import parse_cli_contract
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
