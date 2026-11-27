"""Exercise the pinned Manifest's HTTP payloads and OpenAPI export."""

import unittest
from importlib.util import find_spec
from pathlib import Path

from jsonschema import Draft202012Validator, ValidationError

from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75._package__shared import export_openapi
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_2_SPEC_READING_C83._package__shared import load_manifest
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_2_SPEC_READING_C83.SPECIFICATION_MODEL_C85._package__shared import parse_contract


PIN = {'path': 'openapi_manifest.md', 'atom_id': 'AN-S-999999', 'version': 1,
       'status': 'draft', 'container_component': 'C45'}


class OpenAPIPilotTests(unittest.TestCase):
    def setUp(self):
        self.manifest = load_manifest(Path(__file__).parent, 'C45', PIN)
        self.document = export_openapi(self.manifest)
        self.operation = self.document['paths']['/tools']['post']

    def test_schema_and_payloads(self):
        request = self.operation['requestBody']['content']['application/json']['schema']
        payload = {'name': 'query_run', 'arguments': {'sql': 'SELECT 1'}, 'instance_id': 'test',
                   'session_id': None, 'public_base_url': None, 'asserted_project_root': None}
        validator = Draft202012Validator(request)
        validator.validate(payload)
        for invalid in ({**payload, 'session_id': ''}, {**payload, 'extra': 1},
                        {**payload, 'arguments': {'sql': None}},
                        {**payload, 'arguments': {'sql': 'SELECT 1', 'name': 'x'}}):
            with self.subTest(invalid=invalid), self.assertRaises(ValidationError):
                validator.validate(invalid)
        examples = {'200': {'result': {'value': {}, 'text': None}},
                    '400': {'error': {'code': 'tool_input_invalid', 'message': 'bad',
                                      'tool_result': {'outcome': 'rejected', 'diagnostics': []}}},
                    '500': {'error': {'code': 'internal', 'message': 'Backend Tool operation failed',
                                      'tool_result': {'outcome': 'failed', 'diagnostics': []}}}}
        for status, example in examples.items():
            schema = self.operation['responses'][status]['content']['application/json']['schema']
            Draft202012Validator(schema).validate(example)
            with self.assertRaises(ValidationError):
                Draft202012Validator(schema).validate({**example, 'extra': True})

    @unittest.skipUnless(find_spec('openapi_spec_validator'), 'OpenAPI validator is not installed')
    def test_openapi_document(self):
        from openapi_spec_validator import validate
        validate(self.document)

    def test_invalid_pin_and_outcome_fail(self):
        with self.assertRaises(ValueError):
            load_manifest(Path(__file__).parent, 'C45', {**PIN, 'version': 2})
        language, source = self.manifest['contract']['claims'][0]
        source = source.replace("(400, 'typed_error')", "(401, 'typed_error')")
        self.manifest['contract']['claims'][0] = (language, source)
        with self.assertRaises(ValueError):
            export_openapi(self.manifest)

    def test_requires_a_declared_endpoint(self):
        del self.manifest['fields']['boundaries']['io']['server']['tools']
        with self.assertRaisesRegex(ValueError, "HTTP server 'tools'"):
            export_openapi(self.manifest)

    def test_declared_private_binding_and_shared_status(self):
        server = self.manifest['fields']['boundaries']['io']['server']
        server['private_tools'] = {
            'transport': 'http', 'routes': {'PUT /private-tools': 'dispatch'},
        }
        outcomes = {'success': (200, 'result'),
                    'blocked': (200, 'typed_error'),
                    'missing': (200, 'typed_error')}
        success = {'type': 'object', 'required': ['result'],
                   'additionalProperties': False, 'properties': {'result': {}}}
        failure = {'type': 'object', 'required': ['error'],
                   'additionalProperties': False, 'properties': {'error': {}}}
        schemas = {'success': success, 'blocked': failure, 'missing': failure}
        request = {'type': 'object', 'required': ['name'],
                   'properties': {'name': {'const': 'run'}}}
        source = ("declare_http_contract(interface='private_tools', "
                  "action='run', endpoint='PUT /private-tools', "
                  "route_name='dispatch', "
                  f"outcomes={outcomes!r}, request_schema={request!r}, "
                  f"response_schemas={schemas!r})")
        self.manifest['contract']['claims'] = [('python contract', source)]
        document = export_openapi(self.manifest)
        operation = document['paths']['/private-tools']['put']
        self.assertEqual(operation['operationId'], 'run')
        response = operation['responses']['200']
        self.assertEqual(response['description'], 'success, blocked, missing')
        schema = response['content']['application/json']['schema']
        self.assertEqual(schema, {'oneOf': [success, failure]})
        validator = Draft202012Validator(schema)
        validator.validate({'result': {}})
        validator.validate({'error': {}})
        with self.assertRaises(ValidationError):
            validator.validate({'result': {}, 'error': {}})
        server['private_tools']['routes']['PUT /private-tools'] = 'other'
        with self.assertRaisesRegex(ValueError, "route 'dispatch'"):
            export_openapi(self.manifest)

    def test_action_selector(self):
        language, source = self.manifest['contract']['claims'][0]
        self.manifest['contract']['claims'].append(
            (language, source.replace('query_run', 'other'))
        )
        with self.assertRaisesRegex(ValueError, 'Select one declared HTTP'):
            export_openapi(self.manifest)
        document = export_openapi(self.manifest, action='other')
        operation = document['paths']['/tools']['post']
        self.assertEqual(operation['operationId'], 'other')

    def test_http_200_typed_error_excludes_reserved_and_legacy_outcomes(self):
        source = ("declare_http_contract(interface='tools', action='run', "
                  "endpoint='POST /tools', route_name='invoke', "
                  "outcomes={%r: (%d, 'typed_error')})")
        self.assertEqual(parse_contract(source % ('blocked', 200))['outcomes'],
                         [('blocked', 200, 'typed_error')])
        for name, status in (('invalid_input', 200), ('internal_error', 200),
                             ('blocked', 201)):
            with self.subTest(name=name, status=status):
                with self.assertRaises(ValueError):
                    parse_contract(source % (name, status))
        legacy = ("declare_tool_api_contract(operation='POST /tools', "
                  "outcomes={'success': (200, 'typed_error'), "
                  "'invalid_input': (400, 'typed_error'), "
                  "'internal_error': (500, 'typed_error')})")
        with self.assertRaises(ValueError):
            parse_contract(legacy)

    def test_ordinary_http_unchanged_and_schema_errors_rejected(self):
        source = ("declare_http_contract(interface='tools', action='run', route='invoke', "
                  "operation='POST /tools', outcomes={'success': (200, 'result')})")
        claim = parse_contract(source)
        self.assertNotIn('request_schema', claim)
        self.assertEqual([('success', 200, 'result')], claim['outcomes'])
        language, source = self.manifest['contract']['claims'][0]
        for modified in (source.replace("'type': 'object'", "'type': 'nonsense'", 1),
                         source.replace("'internal_error': (500, 'typed_error')", "'other': (500, 'typed_error')"),
                         source.replace("action='query_run'", "action='other'")):
            with self.subTest(source=modified[:100]):
                self.manifest['contract']['claims'][0] = (language, modified)
                with self.assertRaises(ValueError):
                    export_openapi(self.manifest)
