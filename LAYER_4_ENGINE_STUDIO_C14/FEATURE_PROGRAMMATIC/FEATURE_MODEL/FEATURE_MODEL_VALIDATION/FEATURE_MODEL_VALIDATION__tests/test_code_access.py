"""Check imports-only Code Access decisions."""

import unittest

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.code_access_rules__pub import module_visibility, parse_code_access
from FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_MODEL_VALIDATION.code_access import allows_import


class CodeAccessTests(unittest.TestCase):
    def test_rules(self):
        caller = {'id': 'sales', 'parent': 'root'}
        provider = {'id': 'billing', 'parent': 'root'}
        def allowed(**kwargs):
            return allows_import('billing.api.run', caller, provider, **kwargs)
        self.assertTrue(allowed(marker='shared', sibling=True))
        self.assertFalse(allowed(marker='shared'))
        self.assertTrue(allowed(marker='shared', inherited_imports=[(False, {'billing'})]))
        self.assertTrue(allowed(marker='public'))
        self.assertFalse(allowed(inherited_imports=[(False, {'billing'})]))
        self.assertTrue(allowed(exact=True, inherited_imports=[(False, {'billing.api.run'})]))
        self.assertFalse(allowed(marker='public', inherited_imports=[(True, set())]))
        self.assertTrue(allowed(marker='public', inherited_imports=[(True, {'billing'})]))
        self.assertFalse(allowed(marker='public', ordered_layers=(1, 1)))
        self.assertTrue(allowed(marker='public', ordered_layers=(2, 1)))
        self.assertTrue(allows_import('x', provider, provider, ordered_layers=(1, 1)))

    def test_markers(self):
        for name in ('x__shared', 'x__family_pub', 'x__internal'):
            self.assertEqual(module_visibility(name), 'shared')
        for name in ('x__public', 'x__pub'):
            self.assertEqual(module_visibility(name), 'public')

    def test_parser(self):
        self.assertIsNone(parse_code_access(None))
        self.assertEqual(parse_code_access({'code': {'imports': []}}), (False, set()))
        self.assertEqual(parse_code_access({'code': {'imports': {'only': ['a']}}, 'process': {}, 'state': {}, 'io': {}}),
                         (True, {'a'}))
        for access in ({'imports': 'x'}, {'imports': {'only': ['x', 'x']}},
                       {'imports': {'other': []}}, {'exports': {}}, {'other': []}):
            with self.subTest(access=access), self.assertRaises(ValueError):
                parse_code_access({'code': access})
        self.assertIsNone(parse_code_access({'process': {}}))
        for boundaries in ({'code_access': {}}, {'runtime': {}},
                           {'process': None}, {'process': []}):
            with self.subTest(boundaries=boundaries), self.assertRaises(ValueError):
                parse_code_access(boundaries)


if __name__ == '__main__':
    unittest.main()
