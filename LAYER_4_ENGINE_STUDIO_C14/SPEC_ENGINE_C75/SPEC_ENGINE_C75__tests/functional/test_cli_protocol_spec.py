import shutil
import tempfile
from pathlib import Path
import unittest

from SPEC_ENGINE_C75.cli_spec__pub import _outcome_stdout, _workflow_facts, check_cli_spec
from SPEC_ENGINE_C75.SPEC_ENGINE_C75__tests.functional.test_cli_spec import (
    _carrier, _CONTRACT, _MANIFEST, _SOLUTION,
)
from SPEC_ENGINE_C75.contract_model__pub import parse_cli_contract


class CliProtocolTests(unittest.TestCase):
    def test_protocol_literals_and_all_terminal_outputs(self):
        claim = parse_cli_contract("declare_cli_contract(interface='hook', action='run', runner='uv', "
                                   "path='hook.py', stdin='event', stdout='result')")
        self.assertEqual(('event', 'result'), (claim['stdin'], claim['stdout']))
        with self.assertRaises(ValueError):
            parse_cli_contract("declare_cli_contract(interface='hook', action='run', runner='uv', "
                               "path='hook.py', stdin=event)")
        workflow = {'action': 'run', 'initial': 'idle', 'states': [
            {'name': 'idle', 'final': False, 'transitions': [
                {'target': 'running', 'expect': {'kind': 'trigger', 'target': 'hook',
                                                'detail': {'stdin': 'event'}}}]},
            {'name': 'running', 'final': False, 'transitions': [
                {'target': 'done', 'expect': {'kind': 'output', 'detail': {'stdout': 'result'}}},
                {'target': 'done', 'expect': {'kind': 'output', 'detail': {'stdout': 'wrong'}}}]},
            {'name': 'done', 'final': True, 'transitions': []}]}
        facts = _workflow_facts(workflow, 'C2')
        self.assertEqual('event', facts['stdin'])
        self.assertEqual(['result', 'wrong'], facts['stdout'])
        workflow['states'][1]['transitions'][1]['expect']['detail'] = {}
        self.assertNotIn('stdout', _workflow_facts(workflow, 'C2'))
        workflow['states'][0]['transitions'].append(
            {'target': 'done', 'expect': {'kind': 'output', 'detail': {'stdout': 'result'}}})
        self.assertNotIn('stdin', _workflow_facts(workflow, 'C2'))

    def test_outcome_stdout_parser(self):
        prefix = "declare_cli_contract(interface='hook', action='run', runner='uv', path='hook.py', "
        self.assertEqual('result', parse_cli_contract(prefix + "stdout={'succeeded': 'result'})")['stdout.succeeded'])
        for value in ("{}", "{'succeeded': ''}", "{'succeeded': 'a', 'succeeded': 'b'}", "{'succeeded': result}"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                parse_cli_contract(prefix + f"stdout={value})")

    def test_outcome_stdout_ambiguity(self):
        def edge(outcome, detail):
            return ('state', {'expect': {'kind': 'output', 'outcome': outcome, 'detail': detail}})
        good = edge('succeeded', {'stdout': 'receipt'})
        wrong = edge('succeeded', {'stdout': 'wrong'})
        missing = edge('succeeded', {})
        wildcard = edge(None, {'stdout': 'receipt'})
        self.assertEqual({'stdout.succeeded': ['receipt', 'wrong']}, _outcome_stdout([good, wrong]))
        self.assertNotIn('stdout.succeeded', _outcome_stdout([wrong, missing]))
        self.assertNotIn('stdout.succeeded', _outcome_stdout([good, wildcard]))
        self.assertEqual({}, _outcome_stdout([wildcard]))

    @unittest.skipUnless(shutil.which('lean'), 'Lean executable unavailable')
    def test_outcome_stdout_chain(self):
        manifest = _MANIFEST.replace("'path': 'suite.py'", "'path': 'suite.py', 'output': {'succeeded': 'receipt'}")
        contract = _CONTRACT.replace("outcomes={", "stdout={'succeeded': 'receipt'}, outcomes={")
        solution = _SOLUTION.replace("'exit_status_class': 'zero'", "'exit_status_class': 'zero', 'stdout': 'receipt'")
        solution = solution.replace("'exit_status_class': 'nonzero'", "'exit_status_class': 'nonzero', 'stderr': 'error'")
        cases = ((solution, 'matched'), (solution.replace("'stdout': 'receipt'", "'stdout': 'wrong'"), 'conflicting'),
                 (solution.replace(", 'stdout': 'receipt'", ''), 'unresolved'),
                 (solution.replace("'outcome': 'failed',", ''), 'unresolved'))
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest_pin = _carrier(root, 'AN-S-1', 'component_manifest', 'C1', '{}', manifest)
            contract_pin = _carrier(root, 'AN-S-2', 'component_contract', 'C2', '{ANSWERS: [AN-S-1]}', contract)
            for body, status in cases:
                solution_pin = _carrier(root, 'AN-S-3', 'decision', 'C2', '{IS_SOLUTION_FOR: [AN-S-2@1]}', body)
                report = check_cli_spec(root, 'C2', manifest_pin, contract_pin, solution_pin, interface='suite')
                for direction in ('manifest_solution', 'contract_solution'):
                    fact = next(f for f in report['directions'][direction]['facts'] if f['key'] == 'stdout.succeeded')
                    self.assertEqual(status, fact['status'])
                fact = next(f for f in report['directions']['manifest_contract']['facts'] if f['key'] == 'stdout.succeeded')
                self.assertEqual('matched', fact['status'])

    @unittest.skipUnless(shutil.which("lean"), "Lean executable unavailable")
    def test_wrong_protocols_conflict(self):
        from SPEC_ENGINE_C75.top_down__pub import compare_obligations

        sources = dict.fromkeys(('manifest', 'contract', 'solution'), {})
        declared = {'stdin': 'event', 'stdout': 'result'}
        report = compare_obligations(sources, {'manifest': declared, 'contract': declared,
                                               'solution': {'stdin': 'wrong', 'stdout': 'wrong'}})
        facts = report['directions']['contract_solution']['facts']
        self.assertEqual({'stdin': 'conflicting', 'stdout': 'conflicting'},
                         {fact['key']: fact['status'] for fact in facts})
