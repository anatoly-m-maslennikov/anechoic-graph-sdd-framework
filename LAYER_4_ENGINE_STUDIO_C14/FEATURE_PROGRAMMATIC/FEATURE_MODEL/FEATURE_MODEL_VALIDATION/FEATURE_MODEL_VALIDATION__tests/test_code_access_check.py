import unittest
from collections import namedtuple

from FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_MODEL_VALIDATION.FEATURE_MODEL_VALIDATION__shared import check_code_access
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.realization_ownership__pub import CodeAccessOwnership
CodeAccessOccurrence = namedtuple('CodeAccessOccurrence', 'source_path target_path target_kind unit written line column status')


class CheckTests(unittest.TestCase):
    def test_test_package_imports_require_a_test_source(self):
        entries = {'root': {'id': 'root', 'parent': None, 'path': '.', 'kind': 'component', 'fields': {}}}
        ownership = CodeAccessOwnership(entries, {'.': 'root'})
        target = 'pkg/pkg__tests/nested/helper.py'
        site = CodeAccessOccurrence('pkg/main.py', target, 'module', '*', 'helper', 1, 0, 'internal')
        package = site._replace(target_path='pkg/pkg__tests', target_kind='package', unit=None)
        asset = site._replace(target_path='pkg/pkg__tests/data.json', target_kind='asset', status='asset')
        for occurrence in (site, package, asset):
            self.assertEqual([(finding.status, finding.reason) for finding in
                              check_code_access(ownership, {}, [occurrence])],
                             [('denied', 'non-test import from Test Package')])
        for occurrence in (site._replace(source_path='peer/peer__tests/test_main.py'),
                           site._replace(target_path='pkg/pkg__tests_support/helper.py'),
                           asset._replace(source_path='peer/peer__tests/test_main.ts'),
                           asset._replace(target_path='pkg/runtime.json')):
            self.assertEqual((), check_code_access(ownership, {}, [occurrence]))

    def test_imports_and_entry_bypasses(self):
        entries = {
            'root': {'id': 'root', 'parent': None, 'path': '.', 'kind': 'component', 'fields': {}},
            'a': {'id': 'a', 'parent': 'root', 'path': 'a', 'kind': 'component', 'fields': {'layer': 2}},
            'b': {'id': 'b', 'parent': 'root', 'path': 'b', 'kind': 'component', 'fields': {'layer': 1}},
            'pkg': {'id': 'pkg', 'parent': 'b', 'path': 'b/lib', 'kind': 'package', 'fields': {}},
        }
        ownership = CodeAccessOwnership(entries, {v['path']: k for k, v in entries.items()})
        def result(target, unit=None, bypass=False):
            site = CodeAccessOccurrence('a/x.py', target, 'module', unit, target, 1, 0, 'internal')
            return check_code_access(ownership, {}, [site], include_entry_bypasses=bypass)
        self.assertEqual((), result('b/lib/api__shared.py'))
        self.assertEqual((), result('b/lib/api__public.py', bypass=True))
        self.assertEqual('denied', result('b/lib/api.py', 'run')[0].status)
        entries['a']['fields']['boundaries'] = {'code': {'imports': ['b']}}
        self.assertEqual('denied', result('b/lib/api.py', 'run')[0].status)
        entries['a']['fields']['boundaries']['code']['imports'] = ['b.lib.api.run']
        self.assertEqual('declared_bypass', result('b/lib/api.py', 'run', True)[0].status)
        self.assertEqual('uncertain', result('b/lib/api.py', '*')[0].status)
        entries['a']['fields']['boundaries']['code']['imports'] = {'only': []}
        self.assertEqual('denied', result('b/lib/api__shared.py')[0].status)
        entries['a']['fields']['boundaries']['code']['imports'] = ['b.lib.api']
        self.assertEqual('declared_bypass', result('b/lib/api.py', 'run', True)[0].status)
        entries['b']['fields']['layer'] = 2
        self.assertEqual('sibling layer order', result('b/lib/api.py', 'run')[0].reason)

    def test_shared_entry_grant_outside_sibling_and_package_structure(self):
        entries = {
            'root': {'id': 'root', 'parent': None, 'path': '.', 'kind': 'component', 'fields': {}},
            'a': {'id': 'a', 'parent': 'root', 'path': 'a', 'kind': 'component', 'fields': {}},
            'b': {'id': 'b', 'parent': 'root', 'path': 'b', 'kind': 'component', 'fields': {}},
            'nested': {'id': 'nested', 'parent': 'b', 'path': 'b/nested', 'kind': 'component', 'fields': {}},
            'pkg': {'id': 'pkg', 'parent': 'nested', 'path': 'b/nested/lib', 'kind': 'package', 'fields': {}},
            'peer': {'id': 'peer', 'parent': 'nested', 'path': 'b/nested/peer', 'kind': 'package', 'fields': {}},
        }
        ownership = CodeAccessOwnership(entries, {v['path']: k for k, v in entries.items()})
        target = 'b/nested/lib/api__shared.py'
        site = CodeAccessOccurrence('a/x.py', target, 'module', None, target, 1, 0, 'internal')
        self.assertEqual('denied', check_code_access(ownership, {}, [site])[0].status)
        entries['a']['fields']['boundaries'] = {'code': {'imports': ['nested']}}
        self.assertEqual((), check_code_access(ownership, {}, [site]))
        self.assertEqual((), check_code_access(ownership, {}, [site._replace(source_path='b/nested/peer/a.py')]))
        self.assertEqual((), check_code_access(ownership, {}, [site._replace(source_path='b/nested/a.py')]))

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
