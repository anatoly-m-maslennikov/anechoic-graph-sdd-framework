import unittest

from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_2_SPEC_READING_C83.SPECIFICATION_MODEL_C85._package__shared import (
    http_routes,
    parse_contract,
    parse_trace_contract,
)


class HttpAuthoringVocabularyTests(unittest.TestCase):
    def test_both_contracts_normalize_to_one_binding(self):
        bindings = ("endpoint='GET /items', route_name='list'",
                    "route='GET /items', operation='list'",
                    "route='list', operation='GET /items'")
        keys = ('interface', 'transport', 'endpoint', 'route_name')
        expected = dict(zip(keys, ('api', 'http', 'GET /items', 'list')))
        for binding in bindings:
            with self.subTest(binding=binding):
                http = parse_contract("declare_http_contract(interface='api', action='run', "
                                      + binding + ", outcomes={'ok': (200, 'result')})")
                trace = parse_trace_contract("declare_trace_contract(interface='api', transport='http', "
                                             "action='run', output='ok', must_effect=(('db', 'read'),), "
                                             + binding + ")")
                for claim in (http, trace):
                    self.assertEqual(expected, {key: claim[key] for key in keys})
                    self.assertFalse({'route', 'operation'} & claim.keys())
                    self.assertEqual(claim['route_name'], http_routes({'GET /items': 'list'})[claim['endpoint']])

    def test_rejects_mixed_incomplete_and_invalid_bindings(self):
        bindings = ("endpoint='GET /items', route_name='list', route='list'",
                    "endpoint='GET /items'", "route_name='list'",
                    "endpoint='get /items', route_name='list'",
                    "endpoint='GET /items', route_name='two words'",
                    "endpoint='GET /items', route_name=''",
                    "endpoint=1, route_name='list'",
                    "route='GET /items'", "route='GET /items', operation='POST /items'",
                    "route='list', operation='items'")
        for binding in bindings:
            with self.subTest(binding=binding):
                with self.assertRaises(ValueError):
                    parse_contract("declare_http_contract(interface='api', action='run', " + binding
                                   + ", outcomes={'ok': (200, 'result')})")
                with self.assertRaises(ValueError):
                    parse_trace_contract("declare_trace_contract(interface='api', transport='http', "
                                         "action='run', output='ok', must_effect=(('db', 'read'),), " + binding + ")")
        with self.assertRaises(ValueError):
            parse_trace_contract("declare_trace_contract(interface='api', transport='in_process', "
                                 "entry='run', action='run', output='ok', must_effect=(('db', 'read'),), "
                                 "endpoint='GET /items', route_name='list')")
