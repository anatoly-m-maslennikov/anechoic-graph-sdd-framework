import os
import shutil
import unittest

from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_2_SPEC_READING_C83.SPECIFICATION_MODEL_C85._package__shared import parse_trace_contract
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_4_SPEC_COMPARISON_C88._package__shared import compare_trace_workflow
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75._package__shared import compile_workflow


CONTRACT = "declare_trace_contract(action='admit', output='ready', must_effect=(('kernel', 'ready'),))"


def transition(target, kind, observed=None, outcome=None):
    params = {'kind': kind}
    if observed is not None:
        params['target'] = observed
    if outcome is not None:
        params['outcome'] = outcome
    return {'target': target, 'guard': {'type': 'matchesTrace', 'params': params}}


class TraceSpecTests(unittest.TestCase):
    def test_upper_bound_implication(self):
        lean = os.environ.get('ANECHOIC_TEST_LEAN') or shutil.which('lean')
        if lean is None:
            self.skipTest('Lean unavailable')
        contract = {'action': 'admit', 'output': 'ready', 'must_effect': [
            ('query_retained', 'observed', {'rows': {'at_most': 45}, 'serialized_bytes': {'at_most': 300}})]}
        machine = {'id': 'admit', 'initial': 'start', 'states': {
            'start': {'on': {'effect': transition('seen', 'effect', 'query_retained', 'observed')}},
            'seen': {'on': {'output': transition('done', 'output', outcome='ready')}},
            'done': {'type': 'final'}}}
        params = machine['states']['start']['on']['effect']['guard']['params']
        def status(detail):
            params['detail'] = detail
            workflow = {'action': 'admit', **compile_workflow(machine)['model']}
            return compare_trace_workflow(contract, workflow, lean=lean)['facts'][1]['status']
        for detail in ({'rows': 45, 'serialized_bytes': 300},
                       {'rows': {'at_most': 40}, 'serialized_bytes': {'at_most': 299}}):
            self.assertEqual('matched', status(detail))
        for detail in ({'rows': 46, 'serialized_bytes': 300}, {'rows': True, 'serialized_bytes': 300},
                       {'rows': {'at_most': 46}, 'serialized_bytes': 300},
                       {'rows': {'at_most': 40, 'extra': 1}, 'serialized_bytes': 300}, {'rows': 45}):
            self.assertEqual('conflicting', status(detail))

    def test_effect_details_and_manifest_implication(self):
        from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_4_SPEC_COMPARISON_C88._package__shared import _manifest_contract

        lean = os.environ.get('ANECHOIC_TEST_LEAN') or shutil.which('lean')
        if lean is None:
            self.skipTest('Lean unavailable')
        effect = ('database', 'queried', {'sql': 'current', 'limit': 1, 'enabled': True, 'unused': None})
        contract = {'action': 'admit', 'output': 'ready', 'must_effect': [effect]}
        machine = {'id': 'admit', 'initial': 'start', 'states': {
            'start': {'on': {'effect': transition('seen', 'effect', 'database', 'queried')}},
            'seen': {'on': {'output': transition('done', 'output', outcome='ready')}},
            'done': {'type': 'final'}}}
        detail = machine['states']['start']['on']['effect']['guard']['params']['detail'] = dict(effect[2], extra='ok')

        def status():
            workflow = {'action': 'admit', **compile_workflow(machine)['model']}
            return compare_trace_workflow(contract, workflow, lean=lean)['facts'][1]['status']

        self.assertEqual('matched', status())
        for key, wrong in [('sql', 'previous'), ('limit', True), ('enabled', 1), ('unused', 'null')]:
            old, detail[key] = detail[key], wrong
            self.assertEqual('conflicting', status())
            detail[key] = old
        del detail['sql']
        self.assertEqual('conflicting', status())
        detail['sql'] = '\ud800'
        effect[2]['sql'] = '\ufffd'
        self.assertEqual('conflicting', status())
        effect[2]['sql'] = 'current'
        manifest = {'action': 'admit', 'output': 'ready', 'must_effect': [('database', 'queried', {'sql': 'current'})]}
        self.assertEqual('matched', _manifest_contract([manifest], contract, lean)['status'])
        manifest['must_effect'][0][2]['limit'] = True
        self.assertEqual('conflicting', _manifest_contract([manifest], contract, lean)['status'])
        manifest['must_effect'] = [['database', 'queried']]
        self.assertEqual('matched', _manifest_contract([manifest], contract, lean)['status'])
        from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_4_SPEC_COMPARISON_C88.DELEGATION_VERIFICATION_C89._package__shared import _declared_outcome
        required = {'action': 'admit', 'output': 'ready', 'effect': ('database', 'queried')}
        self.assertEqual(required['effect'], _declared_outcome([contract], required)['effect'])

    def test_terminal_output_coverage_is_separate_from_case_effects(self):
        lean = os.environ.get('ANECHOIC_TEST_LEAN') or shutil.which('lean')
        if lean is None:
            self.skipTest('Lean unavailable')
        contract = {'action': 'admit', 'output': 'ready', 'must_effect': [('kernel', 'ready')]}
        machine = {'id': 'admit', 'initial': 'start', 'states': {
            'start': {'on': {'effect': transition('seen', 'effect', 'kernel', 'ready')}},
            'seen': {'on': {'output': transition('done', 'output', outcome='ready')}},
            'done': {'type': 'final'}}}

        def facts():
            workflow = {'action': 'admit', **compile_workflow(machine)['model']}
            return {fact['key']: fact['status'] for fact in compare_trace_workflow(contract, workflow, lean=lean)['facts']}

        machine['states']['start']['on']['silent'] = transition('done', 'effect', 'other', 'done')
        self.assertEqual({'action': 'matched', 'must_effect': 'matched', 'terminal_output': 'conflicting'}, facts())
        machine['states']['start']['on']['silent'] = transition('done', 'output', outcome='other')
        self.assertEqual('matched', facts()['terminal_output'])
        machine['states']['start']['on']['silent'] = transition('done', 'output')
        self.assertEqual('unresolved', facts()['terminal_output'])
        machine['states']['start']['on']['silent'] = transition('done', 'output', outcome='  ')
        self.assertEqual('unresolved', facts()['terminal_output'])
        machine['states'] = {'start': {'type': 'final'}}
        self.assertEqual('conflicting', facts()['terminal_output'])

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
        result = compare()
        self.assertEqual('matched', result['facts'][1]['status'])
        self.assertEqual('unresolved', result['status'])
        del machine['states']['start']['on']['bypass']
        machine['states']['seen']['on']['output']['guard']['params']['outcome'] = 'other'
        self.assertEqual('unresolved', compare()['status'])

    def test_forbidden_effect_contract_literals_and_cli(self):
        from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_2_SPEC_READING_C83.SPECIFICATION_MODEL_C85._package__shared import parse_cli_contract

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
        del output['outcome']
        self.assertEqual('conflicting', status())
        effect = machine['states']['start']['on']['apply']['guard']['params']
        del effect['target']
        self.assertEqual('conflicting', status())
        effect['target'] = ''
        self.assertEqual('matched', status())
        machine['states']['start']['on']['dry']['guard']['params']['outcome'] = None
        self.assertEqual('unresolved', status())


class HttpBindingTests(unittest.TestCase):
    def test_multiple_outcomes_require_the_same_endpoint(self):
        from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_2_SPEC_READING_C83.SPECIFICATION_MODEL_C85._package__shared import _contract_operations

        binding = ", interface='api', transport='http', route='POST /db', operation='query')"
        ready = CONTRACT[:-1] + binding
        failed = ("declare_trace_contract(action='admit', output='failed', "
                  "forbid_effect=('kernel',)" + binding)
        claims = [('python trace', ready), ('python trace', failed)]

        profile = _contract_operations(claims)
        self.assertEqual('POST /db', profile['endpoint'])
        self.assertEqual(['ready', 'failed'], [case['output'] for case in profile['cases']])
        for changed in (failed.replace('/db', '/other'), failed.removesuffix(binding) + ')'):
            with self.subTest(changed=changed), self.assertRaisesRegex(ValueError, 'share one binding'):
                _contract_operations([claims[0], ('python trace', changed)])

    def test_binding_literals_are_all_or_none(self):
        fields = ", interface='database_api', route='query', transport='http', operation='POST /database'"
        self.assertEqual('query', parse_trace_contract(CONTRACT[:-1] + fields + ')')['route_name'])
        for suffix in (", interface='api'", fields.replace("'http'", "'cli'"),
                       fields.replace("'query'", "''"), fields.replace("'query'", 'name')):
            with self.subTest(suffix=suffix), self.assertRaises(ValueError):
                parse_trace_contract(CONTRACT[:-1] + suffix + ')')

    def test_binding_comparison(self):
        from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_4_SPEC_COMPARISON_C88._package__shared import _binding_directions

        lean = os.environ.get('ANECHOIC_TEST_LEAN') or shutil.which('lean')
        if lean is None:
            self.skipTest('Lean unavailable')
        contract = dict(interface='database_api', endpoint='POST /database',
                        transport='http', route_name='query')
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
        expect['detail']['endpoint'] = 'POST /database'
        self.assertEqual('unresolved', statuses()['contract_solution'])
        del expect['detail']['endpoint']
        transitions.append({'expect': {'kind': 'trigger'}})
        self.assertEqual('conflicting', statuses()['contract_solution'])
        claims['manifest']['boundaries']['io']['server'] = 'unsupported'
        self.assertEqual('unresolved', statuses()['manifest_contract'])

    def test_bound_trace_combines_endpoint_and_effect_scope(self):
        from unittest.mock import patch
        from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_4_SPEC_COMPARISON_C88._package__shared import check_trace_spec

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
        model['solution']['claims'] = [('python', '')]
        compiled = {'claims': {'manifest': manifest, 'contract': contract, 'solution': workflow},
                    'issues': [], 'unresolved': []}
        with patch('FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_2_SPEC_READING_C83._package__shared.load_boundary_model', return_value=model), \
             patch('FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_3_LEAN_TRANSLATOR_C84._package__shared.compile_lean', return_value=compiled):
            report = check_trace_spec(None, 'C1', None, None, None, lean=lean)
            self.assertEqual('matched', report['status'])
            workflow['states'][1]['transitions'][0]['expect']['target'] = 'wrong'
            report = check_trace_spec(None, 'C1', None, None, None, lean=lean)
            self.assertEqual('conflicting', report['directions']['contract_solution']['status'])
