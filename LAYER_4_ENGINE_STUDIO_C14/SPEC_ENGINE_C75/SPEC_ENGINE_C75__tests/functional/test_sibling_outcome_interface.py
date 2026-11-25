import os
import shutil
import tempfile
import unittest
from pathlib import Path

from SPEC_ENGINE_C75.LAYER_5_DELEGATION_VERIFICATION_C89.trace_delegation__pub import check_sibling_outcome
from SPEC_ENGINE_C75.LAYER_5_DELEGATION_VERIFICATION_C89.sibling_delegation__pub import (
    _declares_client, check_sibling_binding,
)
from SPEC_ENGINE_C75.SPEC_ENGINE_C75__tests.functional.test_cli_spec import _carrier
from SPEC_ENGINE_C75.SPEC_ENGINE_C75__tests.functional.test_in_process_delegation import (
    BINDING, INTERFACE, carriers,
)
from SPEC_ENGINE_C75.SPEC_ENGINE_C75__tests.functional.test_trace_child_delegation import (
    CONTRACT, MANIFEST, PARENT, pins,
)


class SiblingOutcomeInterfaceTests(unittest.TestCase):
    def setUp(self):
        self.lean = os.environ.get('ANECHOIC_TEST_LEAN') or shutil.which('lean')
        if not self.lean:
            self.skipTest('Lean executable unavailable')
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        _, self.provider = pins(self.root)
        manifest = MANIFEST.replace("component_id='C2'", "component_id='C3'").replace(
            "'server': {'render': {", "'client': {'render': {'component': 'C2', "
            "'interface': 'render'}, 'unrelated': {'component': 'C2', "
            "'interface': 'unrelated'}}, 'server': {'render': {")
        solution = PARENT.replace("component='C1'", "component='C3'").replace(
            "'output': 'succeeded'", "'output': 'succeeded', 'interface': 'render'")
        self.caller = (
            _carrier(self.root, 'AN-S-5', 'component_manifest', 'C1', '{}', manifest),
            _carrier(self.root, 'AN-S-6', 'component_contract', 'C3', '{ANSWERS: [AN-S-5]}',
                     CONTRACT.replace("action='render'", "action='run'")),
            _carrier(self.root, 'AN-S-7', 'decision', 'C3', '{IS_SOLUTION_FOR: [AN-S-6@1]}', solution),
        )

    def check(self, interface='render'):
        return check_sibling_outcome(self.root, self.caller, 'C2', self.provider,
                                     event='render', interface=interface, lean=self.lean)

    def test_matching_client_event_and_provider(self):
        result = self.check()
        self.assertEqual({'matched'}, {row['status'] for row in result['directions'].values()})

    def test_outcome_check_accepts_http_client(self):
        path = self.root / self.caller[0]['path']
        path.write_text(path.read_text().replace(
            "'interface': 'render'", "'interface': 'render', 'transport': 'http', 'routes': ['POST /render']"))
        result = self.check()
        self.assertEqual({'matched'}, {row['status'] for row in result['directions'].values()})

    def test_selected_event_must_use_requested_interface(self):
        path = self.root / self.caller[2]['path']
        path.write_text(path.read_text().replace("'interface': 'render'", "'interface': 'unrelated'"))
        with self.assertRaisesRegex(ValueError, 'selected event does not use interface render'):
            self.check()

    def test_missing_event_interface_is_rejected(self):
        path = self.root / self.caller[2]['path']
        path.write_text(path.read_text().replace(", 'interface': 'render'", ''))
        with self.assertRaisesRegex(ValueError, 'selected event does not use interface render'):
            self.check()

    def test_provider_must_offer_requested_interface(self):
        with self.assertRaisesRegex(ValueError, 'C2 does not declare server unrelated'):
            self.check('unrelated')

    def test_outcome_must_belong_to_selected_provider_interface(self):
        provider = self.root / self.provider[0]['path']
        provider.write_text(provider.read_text().replace(
            "'server': {'render':", "'server': {'unrelated': {}, 'render':"))
        caller = self.root / self.caller[2]['path']
        caller.write_text(caller.read_text().replace("'interface': 'render'", "'interface': 'unrelated'"))
        result = self.check('unrelated')
        self.assertEqual('unresolved', result['directions']['caller_manifest']['status'])
        self.assertNotEqual('matched', result['status'])

    def test_explicit_provider_contract_interface_must_match(self):
        path = self.root / self.provider[1]['path']
        path.write_text(path.read_text().replace(
            "action='render'", "action='render', interface='unrelated', "
            "transport='in_process', entry='Renderer.render'"))
        with self.assertRaisesRegex(ValueError, 'provider Contract does not use interface render'):
            self.check()

    def test_explicit_provider_solution_interface_must_match(self):
        path = self.root / self.provider[2]['path']
        path.write_text(path.read_text().replace(
            "'start': {'on': {'show':", "'start': {'on': {'request': {'target': 'running', "
            "'guard': {'type': 'matchesTrace', 'params': {'kind': 'trigger', 'target': 'unrelated', "
            "'detail': {'transport': 'in_process', 'entry': 'Renderer.render'}}}}}}, "
            "'running': {'on': {'show':"))
        with self.assertRaisesRegex(ValueError, 'provider Solution does not use interface render'):
            self.check()

    def test_matching_explicit_provider_interfaces(self):
        contract = self.root / self.provider[1]['path']
        contract.write_text(contract.read_text().replace(
            "action='render'", "action='render', interface='render', "
            "transport='in_process', entry='Renderer.render'"))
        solution = self.root / self.provider[2]['path']
        solution.write_text(solution.read_text().replace(
            "'start': {'on': {'show':", "'start': {'on': {'request': {'target': 'running', "
            "'guard': {'type': 'matchesTrace', 'params': {'kind': 'trigger', 'target': 'render', "
            "'detail': {'transport': 'in_process', 'entry': 'Renderer.render'}}}}}}, "
            "'running': {'on': {'show':"))
        self.assertEqual({'matched'}, {row['status'] for row in self.check()['directions'].values()})


class SiblingTransportTests(unittest.TestCase):
    def test_multiple_declarations_allow_a_compatible_client(self):
        clients = [
            {'component': 'C3', 'interface': INTERFACE, 'transport': 'http'},
            {'component': 'C3', 'interface': INTERFACE, 'transport': 'in_process'},
        ]
        self.assertTrue(_declares_client(clients, 'C3', INTERFACE, None, in_process=True))

    def test_http_only_client_cannot_select_in_process_binding(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            caller = carriers(root, 'C2', 1, {'client': [{
                'component': 'C3', 'interface': INTERFACE, 'transport': 'http', 'routes': ['POST /only'],
            }]}, {'kind': 'trigger', 'target': 'caller'}, {
                'kind': 'effect', 'target': 'C3', 'outcome': 'called',
                'detail': {'interface': INTERFACE, **BINDING},
            })
            provider = carriers(root, 'C3', 4, {'server': {INTERFACE: BINDING}},
                                {'kind': 'trigger', 'target': INTERFACE, 'detail': BINDING},
                                {'kind': 'effect', 'target': 'C3', 'outcome': 'called'},
                                ", interface='compiler_worker', transport='in_process', "
                                "entry='Orchestrator.run_worker'")
            with self.assertRaisesRegex(ValueError, 'does not declare client'):
                check_sibling_binding(root, caller, 'C3', provider, event='invoke', interface=INTERFACE)
