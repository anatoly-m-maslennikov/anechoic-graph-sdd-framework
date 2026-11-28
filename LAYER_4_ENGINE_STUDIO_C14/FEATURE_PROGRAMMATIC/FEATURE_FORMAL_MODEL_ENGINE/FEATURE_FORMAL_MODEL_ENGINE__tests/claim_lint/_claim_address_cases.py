"""Tests for the static Python Claim lint entry point."""

from pathlib import Path

from FEATURE_PROGRAMMATIC.FEATURE_FORMAL_MODEL_ENGINE.FEATURE_FORMAL_MODEL_ENGINE__shared import (
    lint_python_model_claim,
)

TOOLS = Path(__file__).resolve().parents[2]


class ClaimAddressCases:
    def test_graph_proven_short_and_exact_qualified_addresses(self):
        workflow = "Atom/(.Header.Context.Role:=Operations)/Workflow"
        step = "Atom/(.Header.Context.Role:=Operations)/Step"
        projected = workflow + ".Header.Context.Form"
        addresses = [
            "Atom",
            "Atom.Header.Context.Role",
            workflow,
            step,
            projected,
            "Workflow Run",
        ]
        source = (
            "subject_path(address='Atom/(.Header.Context.Role in (Operations))/Workflow')\n"
            "allowed_values(address='Workflow.Header.Context.Form', values=('Workflow',), occurrences='1')\n"
            "relation(source='Workflow//$workflow', name='CONTAINS', target='Step//$step', source_count='1+')\n"
            "relation(source='Workflow Run//$run', name='CONTAINS', target='Workflow//$workflow')"
        )
        kwargs = dict(
            declared_addresses=addresses,
            relation_names=["CONTAINS"],
            python_class_bindings={},
            address_bindings={"Workflow": workflow, "Step": step},
        )
        self.assertEqual((), lint_python_model_claim(source, **kwargs))
        self.assertEqual(
            (),
            lint_python_model_claim(
                source,
                declared_addresses=addresses,
                relation_names=["CONTAINS"],
                address_bindings={"Workflow": workflow, "Step": step},
            ),
        )
        self.assertTrue(
            lint_python_model_claim(
                source,
                declared_addresses=addresses,
                relation_names=["CONTAINS"],
                python_class_bindings={},
            )
        )
        self._check_unknown_graph_addresses(kwargs)

    def _check_unknown_graph_addresses(self, kwargs):
        self.assertTrue(
            lint_python_model_claim(
                "subject_path(address='Workflow.Header.Missing')", **kwargs
            )
        )
        self.assertTrue(
            lint_python_model_claim(
                (
                    "subject_path(address='Atom/(.Header.Context.Role in "
                    "(Method))/Workflow')"
                ),
                **kwargs,
            )
        )
        self.assertTrue(
            lint_python_model_claim(
                (
                    "subject_path(address='Atom/(.Header.Context.Role in "
                    "(Operations, Method))/Workflow')"
                ),
                **kwargs,
            )
        )
        self.assertTrue(
            lint_python_model_claim(
                (
                    "subject_path(address='Atom/(.Header.Context."
                    "Role:=Operations)/Missing')"
                ),
                **kwargs,
            )
        )

    def test_qualified_catalog_entry_requires_declared_qualifier_property(
        self,
    ):
        qualified = "Atom/(.Missing:=X)/Workflow"
        options = dict(
            declared_addresses=["Atom", qualified],
            relation_names=[],
            address_bindings={"Workflow": qualified},
        )
        for reference in (
            qualified,
            "Workflow",
            "Atom/(.Missing in (X))/Workflow//$x",
        ):
            result = lint_python_model_claim(
                f"subject_path(address={reference!r})", **options
            )
            self.assertIn(
                "unknown qualifier Property: Atom.Missing", result[0]
            )
        chain = "Atom <+ " + qualified
        options["declared_addresses"].append(chain)
        result = lint_python_model_claim(
            f"subject_path(address={chain!r})", **options
        )
        self.assertIn("unknown qualifier Property: Atom.Missing", result[0])
        options["declared_addresses"].append("Atom.Missing")
        self.assertEqual(
            (),
            lint_python_model_claim(
                f"subject_path(address={qualified!r})", **options
            ),
        )

    def test_graph_bindings_keep_variable_identity_and_local_property(self):
        workflow = "Atom/(.Header.Context.Role:=Operations)/Workflow"
        step = "Atom/(.Header.Context.Role:=Operations)/Step"
        addresses = [
            "Atom",
            "Atom.Header.Context.Role",
            workflow,
            step,
            workflow + ".Content.Claim",
            "Workflow.Content.Claim",
        ]
        kwargs = dict(
            declared_addresses=addresses,
            relation_names=[],
            python_class_bindings={},
            address_bindings={"Workflow": workflow, "Step": step},
        )
        for source in (
            "subject_path(address='Workflow//$x')\n"
            "subject_path(address='Atom/(.Header.Context.Role:=Operations)/Workflow//$x')",
            "subject_path(address='Atom/(.Header.Context.Role:=Operations)/Workflow//$x')\n"
            "subject_path(address='Workflow//$x')",
        ):
            self.assertEqual((), lint_python_model_claim(source, **kwargs))
        self.assertEqual(
            (),
            lint_python_model_claim(
                "subject_path(address='Workflow.Content.Claim')", **kwargs
            ),
        )
        mismatch = (
            "subject_path(address='Workflow//$x')\n"
            "subject_path(address='Step//$x')"
        )
        self.assertIn(
            "inconsistent binding",
            lint_python_model_claim(mismatch, **kwargs)[0],
        )

    def test_graph_bindings_fail_closed_for_missing_and_conflicting_aliases(
        self,
    ):
        workflow = "Atom/(.Header.Context.Role:=Operations)/Workflow"
        options = dict(
            declared_addresses=["Atom", workflow],
            relation_names=[],
            python_class_bindings={},
        )
        claim = "subject_path(address='Workflow')"
        self.assertTrue(lint_python_model_claim(claim, **options))
        self.assertTrue(
            lint_python_model_claim(
                claim, address_bindings={"Workflow": "Missing"}, **options
            )
        )
        self.assertTrue(
            lint_python_model_claim(
                claim,
                address_bindings={"Workflow": workflow},
                declared_addresses=["Atom", workflow, "Workflow"],
                relation_names=[],
                python_class_bindings={},
            )
        )
        self.assertTrue(
            lint_python_model_claim(
                claim, address_bindings={"Workflow": ["bad"]}, **options
            )
        )
