import unittest
from dataclasses import replace

from FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_MODEL_VALIDATION.FEATURE_MODEL_VALIDATION__shared import check_code_access
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import CodeAccessOwnership

from .FEATURE_MODEL_VALIDATION__tests__shared import CodeAccessOccurrence


class CheckTests(unittest.TestCase):
    def test_test_package_imports_require_a_test_source(self):
        entries = {'root': {'id': 'root', 'parent': None, 'path': '.', 'kind': 'component', 'fields': {}}}
        ownership = CodeAccessOwnership(entries, {'.': 'root'})
        target = 'pkg/pkg__tests/nested/helper.py'
        site = CodeAccessOccurrence('pkg/main.py', target, 'module', '*', 'helper', 1, 0, 'internal')
        package = replace(site, target_path='pkg/pkg__tests', target_kind='package', unit=None)
        asset = replace(site, target_path='pkg/pkg__tests/data.json', target_kind='asset', status='asset')
        for occurrence in (site, package, asset):
            self.assertEqual([(finding.status, finding.reason) for finding in
                              check_code_access(ownership, {}, [occurrence])],
                             [('denied', 'non-test import from Test Package')])
        for occurrence in (replace(site, source_path='peer/peer__tests/test_main.py'),
                           replace(site, target_path='pkg/pkg__tests_support/helper.py'),
                           replace(asset, source_path='peer/peer__tests/test_main.ts'),
                           replace(asset, target_path='pkg/runtime.json')):
            self.assertEqual((), check_code_access(ownership, {}, [occurrence]))

    def test_entry_bypass_requires_both_exact_declarations(self):
        target = 'app/src/lib/parse.ts'
        selector = 'src.lib.parse.run'
        code = {'imports': [selector], 'exports': {selector: {'private': ['app/tests']}}}
        entries = {
            'C46': {'id': 'C46', 'parent': None, 'path': 'app', 'kind': 'component',
                    'fields': {'boundaries': {'code': code}}},
            'app/src/lib': {'id': 'app/src/lib', 'parent': 'C46', 'path': 'app/src/lib',
                            'kind': 'package', 'fields': {}},
            'app/tests': {'id': 'app/tests', 'parent': 'C46', 'path': 'app/tests',
                          'kind': 'package', 'fields': {}},
        }
        ownership = CodeAccessOwnership(entries, {value['path']: key for key, value in entries.items()})
        site = CodeAccessOccurrence('app/tests/run.ts', target, 'module', 'run', target, 1, 0, 'internal')

        def status(occurrence=site):
            return [finding.status for finding in check_code_access(
                ownership, {}, [occurrence], include_entry_bypasses=True,
            )]

        self.assertEqual(['declared_bypass'], status())
        self.assertEqual(['uncertain'], status(replace(site, unit='*')))
        code['imports'] = ['siblings']
        self.assertEqual(['undeclared_bypass'], status())
        code['imports'] = {'only': []}
        self.assertEqual(['denied'], status())
        code['imports'] = [selector]
        del code['exports'][selector]
        self.assertEqual(['denied'], status())

    def test_component_declares_a_nested_package_export(self):
        code = {'imports': {'only': ['src.lib.lib__shared']},
                'exports': {'src.lib.lib__shared': {'private': ['app/tests']}}}
        ownership = CodeAccessOwnership(
            {'C46': {'id': 'C46', 'parent': None, 'path': 'app', 'kind': 'component',
                     'fields': {'boundaries': {'code': code}}},
             'app/src/lib': {'id': 'app/src/lib', 'parent': 'C46', 'path': 'app/src/lib',
                             'kind': 'package', 'fields': {}},
             'app/tests': {'id': 'app/tests', 'parent': 'C46', 'path': 'app/tests',
                           'kind': 'package', 'fields': {}}},
            {'app': 'C46', 'app/src/lib': 'app/src/lib', 'app/tests': 'app/tests'},
        )
        target = 'app/src/lib/lib__shared.ts'
        site = CodeAccessOccurrence('app/tests/run.ts', target, 'module', None, target, 1, 0, 'internal')
        self.assertEqual((), check_code_access(ownership, {}, [site]))
        self.assertEqual((), check_code_access(ownership, {}, [site], include_entry_bypasses=True))
        code['exports']['src.lib.lib__shared'] = {'private': ['unrelated']}
        self.assertEqual('denied', check_code_access(ownership, {}, [site])[0].status)

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
        entries['provider']['fields'] = {'boundaries': {'code': {'exports': {'billing.api.run': 'public'}}}}
        self.assertEqual([p.written for p in check_code_access(ownership, sources, sites)], ['alias'])
        entries['provider']['fields']['boundaries']['code']['exports'] = {}
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
        for target in ('billing/api__shared.py', 'billing/api__family_pub.py', 'billing/api__internal.py'):
            for source in ('billing/a.py', 'root.py', 'sales/a.py'):
                self.assertTrue(allowed(source, target), (source, target))
            for source in ('billing/child/a.py', 'sales/sub/a.py', 'billing/child/other/a.py'):
                self.assertFalse(allowed(source, target), (source, target))
        for target in ('billing/api__pub.py', 'billing/api__public.py'):
            self.assertTrue(allowed('sales/sub/a.py', target))
        self.assertFalse(allowed('sales/a.py', 'billing/api.py'))
        self.assertTrue(allowed('billing/a.py', 'billing/api.py'))
        self.assertFalse(allowed('sales/a.py', 'billing/nested/api__family_pub.py'))
        entries['provider']['fields'] = {'boundaries': {'code': {'exports': {'billing.api': 'public'}}}}
        self.assertTrue(allowed('sales/sub/a.py', 'billing/api.py'))
        self.assertFalse(allowed('sales/a.py', 'billing/api__pub.py'))

    def test_inherited_rules_and_uncertain_imports(self):
        entries = {
            'root': {'id': 'root', 'parent': None, 'path': '.', 'kind': 'component', 'fields': {'boundaries': {'code': {'imports': {'only': []}}}}},
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

    def test_nested_divergent_component_lineage(self):
        entries = {
            'root': {'id': 'root', 'parent': None, 'path': '.', 'kind': 'component', 'fields': {}},
            'a': {'id': 'a', 'parent': 'root', 'path': 'a', 'kind': 'component', 'fields': {'layer': 2}},
            'b': {'id': 'b', 'parent': 'root', 'path': 'b', 'kind': 'component', 'fields': {'layer': 1}},
            'a1': {'id': 'a1', 'parent': 'a', 'path': 'a/sub', 'kind': 'component', 'fields': {'layer': 1}},
            'b1': {'id': 'b1', 'parent': 'b', 'path': 'b/sub', 'kind': 'component', 'fields': {'layer': 9}},
            'pkg': {'id': 'pkg', 'parent': 'b1', 'path': 'b/sub/p', 'kind': 'package', 'fields': {}},
        }
        ownership = CodeAccessOwnership(entries, {v['path']: k for k, v in entries.items()})
        target = 'b/sub/p/open__public.py'
        site = CodeAccessOccurrence('a/sub/x.py', target, 'module', None, target, 1, 0, 'internal')
        self.assertEqual(check_code_access(ownership, {}, [site]), ())
        entries['b']['fields']['layer'] = 2
        self.assertEqual(check_code_access(ownership, {}, [site])[0].reason, 'sibling layer order')


if __name__ == '__main__':
    unittest.main()
