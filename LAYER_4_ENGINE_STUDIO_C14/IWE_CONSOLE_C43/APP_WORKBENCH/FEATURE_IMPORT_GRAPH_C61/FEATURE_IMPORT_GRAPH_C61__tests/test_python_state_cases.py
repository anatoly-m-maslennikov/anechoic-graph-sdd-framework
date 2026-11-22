"""Focused checks for conservative Python state-effect lowering."""

import importlib.util
import pathlib
import unittest


MODULE = pathlib.Path(__file__).resolve().parents[1] / 'python_state_cases.py'
SPEC = importlib.util.spec_from_file_location('python_state_cases', MODULE)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class PythonStateCasesTest(unittest.TestCase):
    def test_local_writes_restore_and_output_are_ordered(self):
        case = MOD.python_state_cases('''\
class Owner:
    def action(self):
        old = self._value
        self._value = 2
        self._value = old
        return old
''')[0]
        self.assertEqual(case['action'], 'Owner.action')
        self.assertEqual(case['input'], {})
        self.assertTrue(case['complete'])
        self.assertEqual([(e['kind'], e['target'], e['name'], e['line']) for e in case['events']], [
            ('read', 'local', '$owner', 3), ('write', 'local', '$owner', 4),
            ('write', 'local', '$owner', 5), ('output', '', '', 6)])

    def test_context_alias_token_and_environment(self):
        case = MOD.python_state_cases('''\
from contextvars import ContextVar as CV
import os as operating
ctx = CV('REQUEST_CTX')
def action():
    alias = ctx
    token = alias.set(1)
    alias.get()
    alias.reset(token)
    operating.environ['A'] = 'x'
    return operating.environ.get('A')
''')[0]
        self.assertTrue(case['complete'])
        self.assertEqual([(e['kind'], e['name']) for e in case['events']], [
            ('write', 'REQUEST_CTX'), ('read', 'REQUEST_CTX'), ('write', 'REQUEST_CTX'),
            ('write', 'ENV'), ('read', 'ENV'), ('output', '')])

    def test_thread_local_and_exception(self):
        case = MOD.python_state_cases('''\
import threading as t
storage = t.local()
def action():
    storage.value = 1
    raise ValueError('failure')
''')[0]
        self.assertTrue(case['complete'])
        self.assertEqual([(e['kind'], e['name']) for e in case['events']],
                         [('write', 'threading.local:storage'), ('output', '')])

    def test_quiet_and_unresolved_actions(self):
        cases = MOD.python_state_cases('''\
def quiet():
    pass
def conditional():
    if False:
        return 1
def unknown():
    call()
def parameter(flag):
    pass
''')
        self.assertTrue(cases[0]['complete'])
        self.assertEqual(cases[0]['events'], [])
        for case in cases[1:]:
            self.assertFalse(case['complete'])
            self.assertIsNone(case['input'])
            self.assertEqual(case['events'], [])
            self.assertTrue(case['reachable'])

    def test_ambiguous_binding_and_unsupported_call_are_unresolved(self):
        cases = MOD.python_state_cases('''\
from contextvars import ContextVar
ctx = ContextVar('REQUEST_CTX')
def action():
    ctx.set(1)
    unknown()
def shadow():
    ctx = other
''')
        self.assertTrue(all(not case['complete'] and not case['events'] for case in cases))

    def test_terminated_code_is_not_evaluated(self):
        case = MOD.python_state_cases('''\
def action():
    return 1
    unknown()
''')[0]
        self.assertTrue(case['complete'])
        self.assertEqual([e['kind'] for e in case['events']], ['output'])

    def test_module_initialization(self):
        cases = MOD.python_state_cases("_CACHE = {}\ndef quiet():\n    pass\n")
        self.assertEqual(cases[0]['action'], '<module>')
        self.assertTrue(cases[0]['complete'])
        self.assertEqual([(e['kind'], e['name']) for e in cases[0]['events']], [('write', '$owner')])
        unresolved = MOD.python_state_cases("import mystery\n_CACHE = {}\n")[0]
        self.assertFalse(unresolved['complete'])
        self.assertEqual(unresolved['events'], [])

    def test_invalid_source(self):
        self.assertEqual(MOD.python_state_cases('def broken('), [])


if __name__ == '__main__':
    unittest.main()
