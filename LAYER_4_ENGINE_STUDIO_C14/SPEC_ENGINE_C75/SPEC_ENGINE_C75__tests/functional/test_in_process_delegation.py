import os
import shutil
import tempfile
import unittest
from pathlib import Path

from SPEC_ENGINE_C75.sibling_delegation__pub import check_sibling_binding
from SPEC_ENGINE_C75.SPEC_ENGINE_C75__tests.functional.test_cli_spec import _carrier


MANIFEST = """## Formal Manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest
declare_entity(entity_name='Component Manifest', instance=ComponentManifest(
    component_id={component!r}, name='Example', boundaries={{'io': {io!r}}}))
```
"""
CONTRACT = """## Claim

### Formal Claim

```python trace
declare_trace_contract(action='run', output='ready', must_effect=(('C3', 'called'),){binding})
```
"""
SOLUTION = """## Claim

### Formal Claim

```python
component_workflow(component={component!r}, action='run', machine={{
    'id': 'run', 'initial': 'start', 'states': {{
        'start': {{'on': {{'start': {{'target': 'running', 'guard': {{'type': 'matchesTrace',
            'params': {trigger!r}}}}}}}}},
        'running': {{'on': {{'invoke': {{'target': 'returning', 'guard': {{'type': 'matchesTrace',
            'params': {effect!r}}}}}}}}},
        'returning': {{'on': {{'return': {{'target': 'done', 'guard': {{'type': 'matchesTrace',
            'params': {{'kind': 'output', 'outcome': 'ready'}}}}}}}}}},
        'done': {{'type': 'final'}}}}}})
```
"""
BINDING = {'transport': 'in_process', 'entry': 'Orchestrator.run_worker'}
INTERFACE = 'compiler_worker'


def carriers(root, component, offset, io, trigger, effect, binding=''):
    manifest, contract, solution = (f'AN-S-{offset + n}' for n in range(3))
    return (
        _carrier(root, manifest, 'component_manifest', 'C1', '{}',
                 MANIFEST.format(component=component, io=io)),
        _carrier(root, contract, 'component_contract', component, f'{{ANSWERS: [{manifest}]}}',
                 CONTRACT.format(binding=binding)),
        _carrier(root, solution, 'decision', component, f'{{IS_SOLUTION_FOR: [{contract}@1]}}',
                 SOLUTION.format(component=component, trigger=trigger, effect=effect)),
    )


class InProcessDelegationTests(unittest.TestCase):
    def setUp(self):
        self.lean = os.environ.get('ANECHOIC_TEST_LEAN') or shutil.which('lean')
        if not self.lean:
            self.skipTest('Lean executable unavailable')
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        caller_effect = {'kind': 'effect', 'target': 'C3', 'outcome': 'called',
                         'detail': {'interface': INTERFACE, **BINDING}}
        self.caller = carriers(self.root, 'C2', 1,
                               {'client': [{'component': 'C3', 'interface': INTERFACE}]},
                               {'kind': 'trigger', 'target': 'caller'}, caller_effect)
        self.provider = carriers(self.root, 'C3', 4, {'server': {INTERFACE: BINDING}},
                                 {'kind': 'trigger', 'target': INTERFACE, 'detail': BINDING},
                                 {'kind': 'effect', 'target': 'C3', 'outcome': 'called'},
                                 ", interface='compiler_worker', transport='in_process', "
                                 "entry='Orchestrator.run_worker'")

    def check(self):
        return check_sibling_binding(self.root, self.caller, 'C3', self.provider,
                                        event='invoke', interface=INTERFACE, lean=self.lean)

    def statuses(self):
        return {name: direction['status'] for name, direction in self.check()['directions'].items()}

    def test_provider_declarations_match_and_solution_entry_conflicts(self):
        matched = {'caller_manifest': 'matched', 'caller_contract': 'matched', 'caller_solution': 'matched'}
        self.assertEqual(matched, self.statuses())
        path = self.root / self.provider[2]['path']
        path.write_text(path.read_text().replace('Orchestrator.run_worker', 'Orchestrator.other'))
        self.assertEqual({**matched, 'caller_solution': 'conflicting'}, self.statuses())

    def test_missing_caller_detail_is_unresolved(self):
        path = self.root / self.caller[2]['path']
        path.write_text(path.read_text().replace("'interface': 'compiler_worker', ", ''))
        self.assertTrue(all(status == 'unresolved' for status in self.statuses().values()))

    def test_rejects_non_sibling_and_undeclared_dependency(self):
        path = self.root / self.provider[0]['path']
        original = path.read_text()
        path.write_text(original.replace('container: {component: C1}', 'container: {component: C9}'))
        self.provider[0]['container_component'] = 'C9'
        with self.assertRaises(ValueError):
            self.check()
        path.write_text(original)
        self.provider[0]['container_component'] = 'C1'
        path = self.root / self.caller[0]['path']
        path.write_text(path.read_text().replace("'component': 'C3'", "'component': 'C4'"))
        with self.assertRaises(ValueError):
            self.check()


class HttpSiblingBindingTests(unittest.TestCase):
    def test_named_call_selects_only_its_provider_operation(self):
        lean = os.environ.get('ANECHOIC_TEST_LEAN') or shutil.which('lean')
        if not lean:
            self.skipTest('Lean executable unavailable')
        route = 'POST /tools'
        binding = {'transport': 'http', 'route': route}
        effect = {'kind': 'effect', 'target': 'C3', 'outcome': 'called',
                  'detail': {'interface': 'tools', 'action': 'run', **binding}}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            caller = carriers(root, 'C2', 1, {'client': {'tools': {
                'component': 'C3', 'transport': 'http', 'routes': [route]}}},
                {'kind': 'trigger', 'target': 'caller'}, effect)
            provider = carriers(root, 'C3', 4, {'server': {'tools': {
                'transport': 'http', 'routes': [route, 'POST /other']}}},
                {'kind': 'trigger', 'target': 'tools', 'detail': {'operation': 'run', **binding}},
                {'kind': 'effect', 'target': 'C3', 'outcome': 'called'},
                ", interface='tools', transport='http', route='POST /tools', operation='run'")
            for pin in provider[1:]:
                path = root / pin['path']
                original = path.read_text()
                second = original[original.index('```'):].replace("'run'", "'other'")
                path.write_text(original + '\n' + second.replace(route, 'POST /other'))

            def check(action):
                return check_sibling_binding(root, caller, 'C3', provider, event='invoke',
                                             interface='tools', route=route, action=action, lean=lean)

            self.assertEqual('matched', check('run')['status'])
            self.assertEqual('unresolved', check('other')['status'])
            solution = root / provider[2]['path']
            solution.write_text(solution.read_text().replace(route, 'POST /other'))
            self.assertEqual('conflicting', check('run')['directions']['caller_solution']['status'])

    def test_http_route_and_unsupported_caller_route(self):
        lean = os.environ.get('ANECHOIC_TEST_LEAN') or shutil.which('lean')
        if not lean:
            self.skipTest('Lean executable unavailable')
        route = 'POST /jobs/build'
        detail = {'interface': 'jobs', 'transport': 'http', 'route': route}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            caller = carriers(root, 'C2', 1, {'client': {'jobs': {
                'component': 'C3', 'transport': 'http', 'routes': [route]}}},
                {'kind': 'trigger', 'target': 'caller'},
                {'kind': 'effect', 'target': 'C3', 'outcome': 'called', 'detail': detail})
            provider = carriers(root, 'C3', 4, {'server': {'jobs': {
                'transport': 'http', 'routes': [route]}}},
                {'kind': 'trigger', 'target': 'jobs', 'detail': {
                    'transport': 'http', 'route': route, 'operation': 'run'}},
                {'kind': 'effect', 'target': 'C3', 'outcome': 'called'},
                ", interface='jobs', transport='http', route='POST /jobs/build', operation='run'")

            def check():
                return check_sibling_binding(root, caller, 'C3', provider, event='invoke',
                                             interface='jobs', route=route, lean=lean)

            def statuses():
                return {name: row['status'] for name, row in check()['directions'].items()}

            matched = {'caller_manifest': 'matched', 'caller_contract': 'matched',
                       'caller_solution': 'matched'}
            self.assertEqual(matched, statuses())
            self.assertTrue(any('response' in item.lower() for item in check()['unmodeled']))
            solution = root / provider[2]['path']
            original = solution.read_text()
            solution.write_text(original.replace(route, 'POST /jobs/other'))
            self.assertEqual({**matched, 'caller_solution': 'conflicting'}, statuses())
            solution.write_text(original)
            manifest = root / caller[0]['path']
            manifest.write_text(manifest.read_text().replace(route, 'POST /jobs/other'))
            with self.assertRaises(ValueError):
                check()
