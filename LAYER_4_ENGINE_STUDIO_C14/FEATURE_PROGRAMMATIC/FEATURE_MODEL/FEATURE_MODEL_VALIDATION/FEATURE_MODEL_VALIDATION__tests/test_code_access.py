"""Check resolved Code Access decisions."""

from pathlib import Path
import unittest

PROGRAMMATIC = Path(__file__).resolve().parents[3]

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.code_access_rules__pub import parse_code_access
from FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_MODEL_VALIDATION.code_access import allows_import


class CodeAccessTests(unittest.TestCase):
    def setUp(self):
        self.provider = {'id': 'billing', 'parent': 'root'}
        self.parent = {'id': 'root', 'parent': None}
        self.sibling = {'id': 'sales', 'parent': 'root'}
        self.outsider = {'id': 'C43', 'parent': 'elsewhere'}
        self.entry = 'billing.api.run'

    def allows(self, caller, exports=None, **kwargs):
        return allows_import(self.entry, caller, self.provider, exports, **kwargs)

    def test_visibility_and_import_rules(self):
        shared = {self.entry: ('shared', None)}
        public = {self.entry: ('public', None)}
        private = {self.entry: ('private', {'C43'})}
        self.assertFalse(self.allows(self.sibling))
        self.assertFalse(self.allows(self.sibling, {}))
        self.assertTrue(self.allows(self.parent, shared))
        self.assertTrue(self.allows(self.sibling, shared))
        self.assertFalse(self.allows(self.outsider, shared))
        self.assertTrue(self.allows(self.outsider, public))
        self.assertFalse(self.allows(self.outsider, private))
        self.assertTrue(self.allows(self.outsider, private, inherited_imports=[(False, {'billing'})]))
        self.assertTrue(self.allows(self.outsider, private, inherited_imports=[(True, {'billing'})]))
        self.assertFalse(self.allows(self.sibling, private, inherited_imports=[(False, {'billing'})]))
        self.assertFalse(self.allows(self.sibling, public, inherited_imports=[(True, set())]))
        self.assertTrue(self.allows(self.sibling, public, inherited_imports=[(True, {'billing'})]))
        self.assertFalse(self.allows(self.sibling, shared, inherited_imports=[(False, set()), (True, set())]))
        self.assertFalse(self.allows(self.sibling, public, ordered_layers=(1, 1)))
        self.assertTrue(self.allows(self.sibling, public, ordered_layers=(2, 1)))
        self.assertTrue(allows_import(self.entry, self.provider, self.provider, {}, ordered_layers=(1, 1)))

    def test_markers(self):
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.code_access_rules__pub import module_visibility
        for name in ('x__shared', 'x__family_pub', 'x__internal'):
            self.assertEqual(module_visibility(name), 'shared')
        for name in ('x__public', 'x__pub'):
            self.assertEqual(module_visibility(name), 'public')


class ParseCodeAccessTests(unittest.TestCase):
    def test_normalizes_rules_and_preserves_empty_maps(self):
        self.assertEqual(parse_code_access(None), (None, None))
        self.assertEqual(parse_code_access({'code': {'imports': [], 'exports': {}}}), ((False, set()), {}))
        self.assertEqual(parse_code_access({'code': {'imports': {'only': []}, 'exports': {
            'a': None, 'b': 'private', 'c': {'shared': ['C43']}, 'd': 'public',
        }}, 'state': {}, 'io': {'client': {}, 'server': {}}}),
            ((True, set()), {'a': ('shared', None), 'b': ('private', None),
                             'c': ('shared', {'C43'}), 'd': ('public', None)}))

    def test_rejects_invalid_authored_values(self):
        for access in ({'imports': 'x'}, {'imports': {'only': ['x', 'x']}},
                       {'imports': {'other': []}}, {'exports': []},
                       {'exports': {'x': {'shared': 'C43'}}}, {'exports': {'x': 'internal'}}):
            with self.subTest(access=access), self.assertRaises(ValueError):
                parse_code_access({'code': access})
        with self.assertRaises(ValueError):
            parse_code_access({'code_access': {}})


if __name__ == '__main__':
    unittest.main()
