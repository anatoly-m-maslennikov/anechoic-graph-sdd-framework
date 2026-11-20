"""Check resolved Code Access decisions."""

from pathlib import Path
import sys
import unittest

PROGRAMMATIC = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROGRAMMATIC))

from FEATURE_MODEL.FEATURE_MODEL_VALIDATION.code_access import allows_import, parse_code_access


class CodeAccessTests(unittest.TestCase):
    def setUp(self):
        self.provider = {'id': 'billing', 'parent': 'root'}
        self.parent = {'id': 'root', 'parent': None}
        self.sibling = {'id': 'sales', 'parent': 'root'}
        self.outsider = {'id': 'C43', 'parent': 'elsewhere'}
        self.entry = 'billing.api.run'

    def allows(self, caller, exports=None, **kwargs):
        return allows_import(self.entry, caller, self.provider, exports, **kwargs)

    def test_default_and_consumer_selectors(self):
        for exports in (None, {self.entry: (None, None)}):
            self.assertTrue(self.allows(self.parent, exports))
            self.assertTrue(self.allows(self.sibling, exports))
            self.assertFalse(self.allows(self.outsider, exports))
        for mode in ('public', 'internal'):
            self.assertTrue(self.allows(self.outsider, {self.entry: (mode, {'C43'})}))
            self.assertFalse(self.allows(self.sibling, {self.entry: (mode, {'C43'})}))
            self.assertFalse(self.allows(self.parent, {self.entry: (mode, set())}))
        self.assertTrue(self.allows(self.parent, {self.entry: ('internal', {'parent'})}))
        self.assertFalse(self.allows(self.sibling, {self.entry: ('internal', {'parent'})}))
        self.assertTrue(self.allows(self.sibling, {self.entry: ('internal', {'siblings'})}))
        self.assertFalse(self.allows(self.parent, {self.entry: ('internal', {'siblings'})}))

    def test_markers_and_explicit_exports(self):
        self.assertTrue(self.allows(self.outsider, marked_only=True, marker='public'))
        self.assertFalse(self.allows(self.outsider, marked_only=True, marker='internal'))
        self.assertFalse(self.allows(self.sibling, marked_only=True))
        self.assertTrue(self.allows(self.sibling))
        self.assertFalse(self.allows(self.sibling, {}))
        self.assertTrue(self.allows(self.outsider, {self.entry: ('public', None)}, marked_only=True))
        self.assertFalse(allows_import('billing.api', self.outsider, self.provider,
                                       {self.entry: ('public', None)}))
        self.assertFalse(allows_import('billing.api.other', self.outsider, self.provider,
                                       {self.entry: ('public', None)}))
        self.assertTrue(allows_import('billing.api', self.outsider, self.provider,
                                      {'billing.api': ('public', None)}))

    def test_inherited_rules_and_order(self):
        public = {self.entry: ('public', None)}
        self.assertTrue(self.allows(self.outsider, public, inherited_imports=[{'billing'}, {self.entry}]))
        self.assertFalse(self.allows(self.outsider, public, inherited_imports=[{'billing'}, set()]))
        self.assertTrue(self.allows(self.sibling, public, inherited_imports=[{'siblings'}]))
        self.assertTrue(self.allows(self.parent, public, inherited_imports=[{'billing'}]))
        self.assertTrue(self.allows(self.sibling, public, ordered_layers=(2, 1)))
        self.assertFalse(self.allows(self.sibling, public, ordered_layers=(1, 2)))
        self.assertFalse(self.allows(self.sibling, public, ordered_layers=(1, 1)))
        self.assertTrue(allows_import(self.entry, self.provider, self.provider, {},
                                      inherited_imports=[set()], ordered_layers=(1, 1)))
        self.assertTrue(allows_import(self.entry, self.provider, self.parent,
                                      {self.entry: ('public', None)}, inherited_imports=[{'parent'}]))


class ParseCodeAccessTests(unittest.TestCase):
    def test_normalizes_rules_and_preserves_empty_maps(self):
        self.assertEqual(parse_code_access(None), (None, None))
        self.assertEqual(parse_code_access({'code_access': None}), (None, None))
        self.assertEqual(parse_code_access({'code_access': {'imports': [], 'exports': {}}}),
                         (set(), {}))
        self.assertEqual(parse_code_access({'code_access': {
            'imports': ['parent', 'C43'],
            'exports': {'billing.api.run': 'public', 'billing.api': {'internal': ['C43']},
                        'billing.other': None, 'billing.empty': {'public': []}},
        }}), ({'parent', 'C43'}, {'billing.api.run': ('public', None),
                                 'billing.api': ('internal', {'C43'}),
                                 'billing.other': (None, None),
                                 'billing.empty': ('public', set())}))

    def test_rejects_invalid_authored_values(self):
        for access in (
            {'unknown': []}, {'imports': 'parent'}, {'imports': ['']},
            {'imports': ['x', 'x']}, {'imports': [1]}, {'exports': []},
            {'exports': {'': 'public'}}, {'exports': {1: 'public'}},
            {'exports': {'x': 'private'}}, {'exports': {'x': {'public': 'C43'}}},
            {'exports': {'x': {'public': ['C43', 'C43']}}},
            {'exports': {'x': {'public': [], 'internal': []}}},
        ):
            with self.subTest(access=access), self.assertRaises(ValueError):
                parse_code_access({'code_access': access})


if __name__ == '__main__':
    unittest.main()
