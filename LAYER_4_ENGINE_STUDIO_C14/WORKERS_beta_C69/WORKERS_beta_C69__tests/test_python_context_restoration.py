import unittest
from textwrap import dedent

from WORKERS_beta_C69.WORKERS_beta_C69__shared import (
    python_context_restoration,
)


class ContextRestorationTests(unittest.TestCase):
    def check_source(self, body):
        source = (
            'from contextvars import ContextVar\nctx = ContextVar("ctx")\n'
            + dedent(body)
        )
        return python_context_restoration({"example.py": source})

    def test_conditional_reset_has_witnessed_normal_exit(self):
        findings = self.check_source("""\
            def run(flag: bool):
                token = ctx.set(1)
                if flag:
                    ctx.reset(token)
        """)
        self.assertEqual(
            [(x[1], x[2], x[4]) for x in findings], [(4, 4, "confirmed")]
        )

    def test_repeated_condition_keeps_the_same_boolean_witness(self):
        self.assertEqual(
            self.check_source("""\
            def run(flag: bool):
                if flag:
                    token = ctx.set(1)
                if flag:
                    ctx.reset(token)
        """),
            [],
        )

    def test_finally_restores_after_unknown_call(self):
        self.assertEqual(
            self.check_source("""\
            def run():
                token = ctx.set(1)
                try:
                    work()
                finally:
                    ctx.reset(token)
        """),
            [],
        )

    def test_direct_reset_and_persistent_set(self):
        self.assertEqual(
            self.check_source("""\
            def run():
                token = ctx.set(1)
                ctx.reset(token)
            def persistent():
                ctx.set(2)
        """),
            [],
        )

    def test_unknown_call_before_reset_is_unresolved(self):
        findings = self.check_source("""\
            def run():
                token = ctx.set(1)
                work()
                ctx.reset(token)
        """)
        self.assertEqual([x[4] for x in findings], ["unresolved"])

    def test_return_before_reset_is_confirmed(self):
        findings = self.check_source("""\
            def run(flag: bool):
                token = ctx.set(1)
                if flag:
                    return
                ctx.reset(token)
        """)
        self.assertEqual([x[4] for x in findings], ["confirmed"])

    def test_unrelated_set_and_nested_reset_do_not_establish_intent(self):
        self.assertEqual(
            self.check_source("""\
            def run(other):
                token = other.set(1)
                other.reset(token)
                saved = ctx.set(1)
                def nested():
                    ctx.reset(saved)
        """),
            [],
        )

    def test_constant_true_reset_has_no_unreachable_leak(self):
        self.assertEqual(
            self.check_source("""\
            def run():
                token = ctx.set(1)
                if True:
                    ctx.reset(token)
        """),
            [],
        )

    def test_unknown_condition_is_unresolved(self):
        findings = self.check_source("""\
            def run(flag):
                token = ctx.set(1)
                if flag:
                    ctx.reset(token)
        """)
        self.assertEqual([x[4] for x in findings], ["unresolved"])

    def test_rebound_receiver_and_other_scope_do_not_prove_context(self):
        self.assertEqual(
            self.check_source("""\
            def run(flag: bool):
                ctx = other
                token = ctx.set(1)
                if flag:
                    ctx.reset(token)
        """),
            [],
        )
        source = """\
            from contextvars import ContextVar
            def other():
                ctx = ContextVar("ctx")
            def run(flag: bool):
                token = ctx.set(1)
                if flag:
                    ctx.reset(token)
        """
        self.assertEqual(
            python_context_restoration({"x.py": dedent(source)}), []
        )

    def test_replaced_token_is_unresolved(self):
        findings = self.check_source("""\
            def run(flag: bool):
                token = ctx.set(1)
                token = other
                if flag:
                    ctx.reset(token)
        """)
        self.assertEqual([x[4] for x in findings], ["unresolved"])
