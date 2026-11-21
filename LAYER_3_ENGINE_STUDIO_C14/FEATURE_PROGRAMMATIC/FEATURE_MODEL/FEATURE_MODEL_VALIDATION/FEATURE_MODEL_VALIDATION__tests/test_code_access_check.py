import unittest

from LAYER_3_ENGINE_STUDIO_C14.FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_MODEL_VALIDATION.code_access_check import check_code_access
from LAYER_3_ENGINE_STUDIO_C14.FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_MODEL_VALIDATION.code_access_ownership import CodeAccessOwnership
from LAYER_3_ENGINE_STUDIO_C14.FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_MODEL_VALIDATION.code_access_occurrences import CodeAccessOccurrence


class CheckTests(unittest.TestCase):
    def test_marker_opt_in_and_spec_override(self):
        entries = {
            'root': {'id': 'root', 'parent': None, 'path': '.', 'kind': 'component', 'fields': {}},
            'caller': {'id': 'caller', 'parent': 'root', 'path': 'caller', 'kind': 'package', 'fields': {}},
            'provider': {'id': 'provider', 'parent': 'root', 'path': 'billing', 'kind': 'package', 'fields': {}},
            'other': {'id': 'other', 'parent': 'caller', 'path': 'caller/other', 'kind': 'package', 'fields': {}},
        }
        ownership = CodeAccessOwnership(entries, {v['path']: k for k, v in entries.items()})
        def occurrence(target, unit=None):
            return CodeAccessOccurrence('caller/other/a.py', target, 'module', unit, 'alias', 1, 0, 'internal')
        sites = [occurrence('billing/api.py', 'run'), occurrence('billing/open__public.py')]
        sources = {'billing/api.py': None, 'billing/open__public.py': None}
        self.assertEqual([p.written for p in check_code_access(ownership, sources, sites)], ['alias'])
        entries['provider']['fields'] = {'boundaries': {'code_access': {'exports': {'billing.api.run': 'public'}}}}
        self.assertEqual([p.written for p in check_code_access(ownership, sources, sites)], ['alias'])
        entries['provider']['fields']['boundaries']['code_access']['exports'] = {}
        self.assertEqual(len(check_code_access(ownership, sources, sites)), 2)
        entries['provider']['fields'] = {}
        self.assertEqual(len(check_code_access(ownership, {'billing/api.py': None}, sites[:1])), 1)
        entries['other']['parent'] = 'root'
        self.assertEqual(len(check_code_access(ownership, {'billing/api.py': None}, sites[:1])), 1)

    def test_direct_visibility_is_provider_relative(self):
        entries = {
            'root': {'id': 'root', 'parent': None, 'path': '.', 'kind': 'component', 'fields': {}},
            'provider': {'id': 'provider', 'parent': 'root', 'path': 'billing', 'kind': 'package', 'fields': {}},
            'child': {'id': 'child', 'parent': 'provider', 'path': 'billing/child', 'kind': 'package', 'fields': {}},
            'sibling': {'id': 'sibling', 'parent': 'root', 'path': 'sales', 'kind': 'package', 'fields': {}},
            'descendant': {'id': 'descendant', 'parent': 'sibling', 'path': 'sales/sub', 'kind': 'package', 'fields': {}},
            'other': {'id': 'other', 'parent': 'child', 'path': 'billing/child/other', 'kind': 'package', 'fields': {}},
        }
        ownership = CodeAccessOwnership(entries, {v['path']: k for k, v in entries.items()})
        def allowed(source, target):
            site = CodeAccessOccurrence(source, target, 'module', None, target, 1, 0, 'internal')
            return not check_code_access(ownership, {target: None}, [site])
        for target in ('billing/api__family_pub.py', 'billing/api__internal.py'):
            for source in ('billing/a.py', 'root.py', 'sales/a.py'):
                self.assertTrue(allowed(source, target), (source, target))
            for source in ('billing/child/a.py', 'sales/sub/a.py', 'billing/child/other/a.py'):
                self.assertFalse(allowed(source, target), (source, target))
        for target in ('billing/api__pub.py', 'billing/api__public.py'):
            self.assertTrue(allowed('sales/sub/a.py', target))
        self.assertFalse(allowed('sales/a.py', 'billing/api.py'))
        self.assertTrue(allowed('billing/a.py', 'billing/api.py'))
        self.assertFalse(allowed('sales/a.py', 'billing/nested/api__family_pub.py'))
        entries['provider']['fields'] = {'boundaries': {'code_access': {'exports': {'billing.api': 'public'}}}}
        self.assertTrue(allowed('sales/sub/a.py', 'billing/api.py'))
        self.assertFalse(allowed('sales/a.py', 'billing/api__pub.py'))

    def test_inherited_rules_and_uncertain_imports(self):
        entries = {
            'root': {'id': 'root', 'parent': None, 'path': '.', 'kind': 'component', 'fields': {'boundaries': {'code_access': {'imports': []}}}},
            'a': {'id': 'a', 'parent': 'root', 'path': 'a', 'kind': 'package', 'fields': {}},
            'b': {'id': 'b', 'parent': 'root', 'path': 'b', 'kind': 'package', 'fields': {}},
        }
        ownership = CodeAccessOwnership(entries, {v['path']: k for k, v in entries.items()})
        sites = [CodeAccessOccurrence('a/x.py', 'b/open__public.py', 'module', None, 'b.open__public', 2, 0, 'internal'),
                 CodeAccessOccurrence('a/x.py', None, None, None, 'missing', 3, 0, 'unresolved')]
        result = check_code_access(ownership, {'b/open__public.py': None}, sites)
        self.assertEqual([(p.status, p.line) for p in result], [('denied', 2), ('uncertain', 3)])

    def test_layers_apply_to_packages_in_sibling_components(self):
        entries = {
            'root': {'id': 'root', 'parent': None, 'path': '.', 'kind': 'component', 'fields': {}},
            'a': {'id': 'a', 'parent': 'root', 'path': 'a', 'kind': 'component', 'fields': {'layer': 1}},
            'b': {'id': 'b', 'parent': 'root', 'path': 'b', 'kind': 'component', 'fields': {'layer': 2}},
            'pkg': {'id': 'pkg', 'parent': 'b', 'path': 'b/p', 'kind': 'package', 'fields': {}},
        }
        ownership = CodeAccessOwnership(entries, {v['path']: k for k, v in entries.items()})
        target = 'b/p/open__public.py'
        site = CodeAccessOccurrence('a/x.py', target, 'module', None, 'b.p.open__public', 1, 0, 'internal')
        self.assertEqual([p.reason for p in check_code_access(ownership, {target: None}, [site])],
                         ['sibling layer order'])
        entries['b']['fields'] = {}
        self.assertEqual(check_code_access(ownership, {target: None}, [site]), ())


if __name__ == '__main__':
    unittest.main()
