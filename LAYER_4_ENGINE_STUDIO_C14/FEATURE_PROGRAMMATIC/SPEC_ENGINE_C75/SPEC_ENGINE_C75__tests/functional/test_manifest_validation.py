import unittest

from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_2_SPEC_READING_C83.SPECIFICATION_MODEL_C85._package__shared import validate_manifest


class ManifestValidationTests(unittest.TestCase):
    def test_valid_and_malformed_are_source_linked(self):
        source = {'path': 'manifest.md', 'atom_id': 'AN-S-1', 'version': 1}
        boundaries = {'code': {'imports': {'only': ['C2']}}, 'io': {'server': 'API'}}
        fields = {'component_id': 'C1', 'name': 'One', 'boundaries': boundaries}
        result = validate_manifest({'source': source, 'fields': fields, 'boundaries': boundaries})
        self.assertEqual([], result['issues'])
        self.assertEqual({'boundaries.io', 'boundaries.code.imports'},
                         {item['field'] for item in result['unresolved']})
        malformed = {'component_id': '', 'name': 'One', 'boundaries': {'code': {'exports': []}}}
        result = validate_manifest({'source': source, 'fields': malformed, 'boundaries': malformed['boundaries']})
        self.assertEqual({'component_id', 'boundaries'}, {item['field'] for item in result['issues']})
        self.assertTrue(all(item['source'] == source for item in result['issues']))

    def test_state_lists_and_empty_imports(self):
        source = {'path': 'manifest.md', 'atom_id': 'AN-S-1', 'version': 1}

        def validate(boundaries):
            fields = {'component_id': 'C1', 'name': 'One', 'boundaries': boundaries}
            return validate_manifest({'source': source, 'fields': fields, 'boundaries': boundaries})

        for imports in ([], (), {'only': []}, {'only': ()}):
            with self.subTest(imports=imports):
                result = validate({'code': {'imports': imports}, 'state': {'reads': [], 'writes': []}})
                self.assertEqual({'issues': [], 'unresolved': []}, result)
        result = validate({'state': {'reads': ['input'], 'writes': ['output']}})
        self.assertEqual([], result['issues'])
        self.assertEqual(['boundaries.state'], [item['field'] for item in result['unresolved']])
        for state in ({'reads': 'input'}, {'writes': [' ', 1]}, {'reads': None}):
            with self.subTest(state=state):
                result = validate({'state': state})
                self.assertEqual(1, len(result['issues']))
                self.assertEqual(f'boundaries.state.{next(iter(state))}', result['issues'][0]['field'])
                self.assertEqual(source, result['issues'][0]['source'])
                self.assertEqual('boundaries.state', result['unresolved'][0]['field'])
        for state in ({}, {'reads': [], 'writes': [], 'channels': {}}, 'local'):
            with self.subTest(state=state):
                self.assertEqual('boundaries.state', validate({'state': state})['unresolved'][0]['field'])
        for boundaries in (None, {}):
            with self.subTest(boundaries=boundaries):
                self.assertEqual('boundaries', validate(boundaries)['unresolved'][0]['field'])
        self.assertEqual([], validate({'code': {'imports': []}})['unresolved'])
        self.assertEqual({'issues': [], 'unresolved': []}, validate({'io': {'server': {}}}))
        self.assertEqual('boundaries.code.exports',
                         validate({'code': {'exports': {'api': 'public'}}})['unresolved'][0]['field'])
        self.assertEqual('boundaries.code.imports',
                         validate({'code': {'imports': ['C2']}})['unresolved'][0]['field'])
