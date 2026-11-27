import os
import shutil
import tempfile
import unittest
from pathlib import Path

from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.\
    LAYER_2_SPEC_READING_C83._package__shared \
    import load_boundary_model  # fmt: skip
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.\
    LAYER_3_LEAN_TRANSLATOR_C84._package__shared \
    import compile_lean  # fmt: skip
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.\
    LAYER_4_SPEC_COMPARISON_C88.DELEGATION_VERIFICATION_C89._package__shared \
    import check_child_outcome  # fmt: skip
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.\
    LAYER_4_SPEC_COMPARISON_C88._package__shared \
    import check_trace_spec  # fmt: skip
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.SPEC_ENGINE_C75__tests.functional.\
    test_trace_child_delegation \
    import (
        CONTRACT,
        PARENT,
        SOLUTION,
        pins,
    )  # fmt: skip


def add_operation(root, child):
    manifest = root / child[0]["path"]
    source = manifest.read_text()
    source = source.replace(
        "'server': {'render': {",
        "'server': {'inspect': {'outcomes': {'succeeded': "
        "{'must_effect': [('audit_log', 'written')]}}}, 'render': {",
    )
    manifest.write_text(source)
    for pin, body in ((child[1], CONTRACT), (child[2], SOLUTION)):
        path = root / pin["path"]
        second = body.replace("action='render'", "action='inspect'").replace(
            "workbench_display", "audit_log"
        )
        second = second.replace(
            "'outcome': 'shown'", "'outcome': 'written'"
        ).replace("'shown'", "'written'")
        path.write_text(path.read_text() + "\n" + second)


class TraceOperationsTests(unittest.TestCase):
    def setUp(self):
        self.lean = os.environ.get("ANECHOIC_TEST_LEAN") or shutil.which(
            "lean"
        )
        if not self.lean:
            self.skipTest("Lean executable unavailable")
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.parent, self.child = pins(self.root)
        add_operation(self.root, self.child)

    def test_operations_are_independent_and_keep_equal_outputs(self):
        model = load_boundary_model(self.root, "C2", *self.child)
        claims = compile_lean(model)["claims"]
        for role in ("contract", "solution"):
            self.assertEqual(
                {"render", "inspect"}, set(claims[role]["operations"])
            )

        def report():
            return check_trace_spec(
                self.root, "C2", *self.child, lean=self.lean
            )

        result = report()
        for action in ("render", "inspect"):
            self.assertEqual(
                "matched",
                result["operations"][action]["contract_solution"]["status"],
            )
        path = self.root / self.child[2]["path"]
        path.write_text(
            path.read_text().replace(
                "'target': 'audit_log'", "'target': 'wrong'"
            )
        )
        result = report()
        self.assertEqual(
            "matched",
            result["operations"]["render"]["contract_solution"]["status"],
        )
        self.assertEqual(
            "conflicting",
            result["operations"]["inspect"]["contract_solution"]["status"],
        )

    def test_child_outcome_uses_the_selected_operation_on_both_sides(self):
        parent = self.root / self.parent["path"]
        second = PARENT.replace("action='run'", "action='alternate'").replace(
            "'render':", "'other':"
        )
        parent.write_text(parent.read_text() + "\n" + second)

        def check():
            return check_child_outcome(
                self.root,
                self.parent,
                "C2",
                self.child,
                event="render",
                lean=self.lean,
            )

        self.assertEqual(
            {"matched"},
            {row["status"] for row in check()["directions"].values()},
        )
        path = self.root / self.child[2]["path"]
        path.write_text(
            path.read_text().replace(
                "'target': 'audit_log'", "'target': 'wrong'"
            )
        )
        self.assertEqual(
            {"matched"},
            {row["status"] for row in check()["directions"].values()},
        )
