"""Focused checks for conservative Python state-effect lowering."""

import importlib.util
import pathlib
import unittest


MODULE = pathlib.Path(__file__).resolve().parents[2] / (
    "STATE_ANALYSIS/python_state_cases.py"
)
SPEC = importlib.util.spec_from_file_location("python_state_cases", MODULE)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class PythonStateCasesTest(unittest.TestCase):
    def test_named_registry_read(self):
        (case,) = MOD.python_state_cases(
            (
                "from sys import modules as registry\ndef lookup():\n    "
                "return registry.get('example')\n"
            )
        )
        self.assertTrue(case["complete"])
        self.assertEqual(
            [("read", "SYS_MODULES"), ("output", "")],
            [(event["kind"], event["name"]) for event in case["events"]],
        )

    def test_local_writes_restore_and_output_are_ordered(self):
        case = MOD.python_state_cases("""\
class Owner:
    def action(self):
        old = self._value
        self._value = 2
        self._value = old
        return old
""")[0]
        self.assertEqual(case["action"], "Owner.action")
        self.assertEqual(case["input"], {})
        self.assertTrue(case["complete"])
        self.assertEqual(
            [
                (e["kind"], e["target"], e["name"], e["line"])
                for e in case["events"]
            ],
            [
                ("read", "local", "$owner", 3),
                ("write", "local", "$owner", 4),
                ("write", "local", "$owner", 5),
                ("output", "", "", 6),
            ],
        )

    def test_context_alias_token_and_environment(self):
        case = MOD.python_state_cases("""\
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
""")[0]
        self.assertTrue(case["complete"])
        self.assertEqual(
            [(e["kind"], e["name"]) for e in case["events"]],
            [
                ("write", "REQUEST_CTX"),
                ("read", "REQUEST_CTX"),
                ("write", "REQUEST_CTX"),
                ("write", "ENV"),
                ("read", "ENV"),
                ("output", ""),
            ],
        )

    def test_thread_local_and_exception(self):
        case = MOD.python_state_cases("""\
import threading as t
storage = t.local()
def action():
    storage.value = 1
    raise ValueError('failure')
""")[0]
        self.assertTrue(case["complete"])
        self.assertEqual(
            [(e["kind"], e["name"]) for e in case["events"]],
            [("write", "threading.local:storage"), ("output", "")],
        )

    def test_quiet_and_unresolved_actions(self):
        cases = MOD.python_state_cases("""\
def quiet():
    pass
def conditional():
    if False:
        return 1
def unknown():
    call()
def parameter(flag):
    pass
""")
        self.assertTrue(cases[0]["complete"])
        self.assertEqual(cases[0]["events"], [])
        for case in cases[1:]:
            self.assertFalse(case["complete"])
            self.assertIsNone(case["input"])
            self.assertEqual(case["events"], [])
            self.assertTrue(case["reachable"])

    def test_ambiguous_binding_and_unsupported_call_are_unresolved(self):
        cases = MOD.python_state_cases("""\
from contextvars import ContextVar
ctx = ContextVar('REQUEST_CTX')
def action():
    ctx.set(1)
    unknown()
def shadow():
    ctx = other
""")
        self.assertTrue(
            all(not case["complete"] and not case["events"] for case in cases)
        )

    def test_terminated_code_is_not_evaluated(self):
        case = MOD.python_state_cases("""\
def action():
    return 1
    unknown()
""")[0]
        self.assertTrue(case["complete"])
        self.assertEqual([e["kind"] for e in case["events"]], ["output"])

    def test_module_initialization(self):
        cases = MOD.python_state_cases("_CACHE = {}\ndef quiet():\n    pass\n")
        self.assertEqual(cases[0]["action"], "<module>")
        self.assertTrue(cases[0]["complete"])
        self.assertEqual(
            [(e["kind"], e["name"]) for e in cases[0]["events"]],
            [("write", "$owner")],
        )
        unresolved = MOD.python_state_cases("import mystery\n_CACHE = {}\n")[0]
        self.assertFalse(unresolved["complete"])
        self.assertEqual(unresolved["events"], [])

    def test_graph_calls_and_unresolved_calls(self):
        source = "def action():\n    target()\n    return target()\n"
        (case,) = MOD.python_state_cases(
            source, {(2, 4): "unit", (3, 11): "unit"}
        )
        self.assertTrue(case["inlineable"])
        self.assertEqual(case["column"], 0)
        self.assertEqual(
            case["events"],
            [
                dict(
                    kind="call", target="", name="unit", line=2, forward=False
                ),
                dict(
                    kind="call", target="", name="unit", line=3, forward=True
                ),
            ],
        )
        self.assertFalse(MOD.python_state_cases(source, {})[0]["complete"])
        self.assertFalse(
            MOD.python_state_cases(
                "def f():\n    target(1)\n", {(2, 4): "unit"}
            )[0]["complete"]
        )
        self.assertFalse(
            MOD.python_state_cases(
                "def f():\n    x = target()\n", {(2, 8): "unit"}
            )[0]["complete"]
        )

    def test_graph_event_kinds_and_callable_shape(self):
        source = (
            "def f():\n    print()\n    return 1\ndef g():\n    raise "
            "ValueError()\nclass C:\n    def m(self):\n        pass\n"
        )
        f, g, method = MOD.python_state_cases(source, {(2, 4): "other"})
        self.assertEqual(
            [event["kind"] for event in f["events"]], ["output", "return"]
        )
        self.assertEqual([event["kind"] for event in g["events"]], ["raise"])
        self.assertFalse(method["inlineable"])

    def test_invalid_source(self):
        (case,) = MOD.python_state_cases("def broken(")
        self.assertEqual(case["action"], "<parse_error>")
        self.assertFalse(case["complete"])


if __name__ == "__main__":
    unittest.main()
