from __future__ import annotations

from pathlib import Path
import unittest



APP_ROOT = Path(__file__).resolve().parents[3]
ASSETS = Path(__file__).resolve().parent / "assets" / "content_declaration_schema"
SEALED_MODEL = APP_ROOT.parent / "FEATURE_PROGRAMMATIC/FEATURE_TOOLS/FEATURE_TOOLS__tests/assets/lifecycle_schema_declarations/04_requirement"


from KERNEL_MIXER_C59.content_columns import content_columns  # noqa: E402
from KERNEL_MIXER_C59.content_schema import (  # noqa: E402
    compile_content_schema,
)


from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.FEATURE_WORKBENCH_BACKEND__tests.content_schema_fixture import ContentSchemaFixture


class ContentDeclarationSchemaTests(ContentSchemaFixture):
    def test_cfel_outside_formal_claim_does_not_contribute(self) -> None:
        declaration = self.declaration("CA-R-1", "Atom.Content.Summary{::1}:: {::1};")
        declaration["content_markdown"] = "## Claim\n\n```CFEL\nAtom.Content.Summary{::1}:: {::1};\n```\n"
        self.assertEqual((), compile_content_schema([declaration]).names)


    def test_declaration_changes_add_remove_and_rename_columns(self) -> None:
        summary = self.declaration("CA-R-1", "Atom.Content.Summary{::1}:: {::1};")
        renamed = self.declaration("CA-R-1", "Atom.Content.Title{::1}:: {::1};")

        self.assertEqual(("content.summary",), compile_content_schema([summary]).names)
        self.assertEqual(("content.title",), compile_content_schema([renamed]).names)
        self.assertEqual((), compile_content_schema([{
            **summary, "status_group": "Draft",
        }]).names)


    def test_role_and_form_gate_the_declared_value(self) -> None:
        declaration = self.declaration(
            "CA-R-2",
            "Atom/(.Header.Role := Plan)/(.Header.Form := Epic).Content.Objective:: {::1};",
        )
        schema = compile_content_schema([declaration])
        plan = self.atom("CA-P-1", role="Plan", form="Epic", body="## Objective\n\nShip it.\n")
        task = self.atom("CA-P-2", role="Plan", form="Task", body="## Objective\n\nDo not expose.\n")

        self.assertEqual({"content.objective": "Ship it."}, content_columns(plan, schema))
        self.assertEqual({"content.objective": None}, content_columns(task, schema))


    def test_colon_and_literal_list_filters_are_not_global(self) -> None:
        declaration = self.declaration(
            "CA-R-2",
            "Atom/(.Header.Role: Plan).Content.Objective:: {::1};\n"
            "Atom/(.Header.Role in (Plan, Concern)).Content.Scope:: {::0..1};",
        )
        schema = compile_content_schema([declaration])
        plan = self.atom("CA-P-1", role="Plan", body="## Objective\n\nShip.\n\n## Scope\n\nAll.\n")
        concern = self.atom("CA-C-1", role="Concern", body="## Objective\n\nHidden.\n\n## Scope\n\nOnly this.\n")
        other = self.atom("CA-R-1", body="## Objective\n\nHidden.\n\n## Scope\n\nHidden.\n")

        self.assertEqual(
            {"content.objective": "Ship.", "content.scope": "All."}, content_columns(plan, schema),
        )
        self.assertEqual(
            {"content.objective": None, "content.scope": "Only this."}, content_columns(concern, schema),
        )
        self.assertEqual(
            {"content.objective": None, "content.scope": None}, content_columns(other, schema),
        )


    def test_context_role_and_form_filters_match_the_prepared_header_layout(self) -> None:
        declaration = self.declaration(
            "CA-R-2",
            "Atom/(.Header.Context.Role in RMED)/(.Header.Context.Form: Policy).Content.Objective:: {::1};",
        )
        schema = compile_content_schema([declaration])
        policy = self.atom("CA-M-1", role="Method", form="Policy", body="## Objective\n\nUse it.\n")
        rule = self.atom("CA-R-1", role="Requirement", form="Rule", body="## Objective\n\nDo not use it.\n")

        self.assertEqual({"content.objective": "Use it."}, content_columns(policy, schema))
        self.assertEqual({"content.objective": None}, content_columns(rule, schema))


    def test_unsupported_filter_refuses_to_widen_applicability(self) -> None:
        declaration = self.declaration(
            "CA-R-2",
            "Atom/(.Header.Role != Plan).Content.Objective:: {::1};",
        )

        with self.assertRaisesRegex(ValueError, "unsupported Content declaration Header.Role filter"):
            compile_content_schema([declaration])


    def test_unsupported_selector_refuses_to_widen_applicability(self) -> None:
        declaration = self.declaration(
            "CA-R-2",
            "Atom/(.Header.Status := Active).Content.Objective:: {::1};",
        )

        with self.assertRaisesRegex(ValueError, "unsupported Content declaration selector"):
            compile_content_schema([declaration])


    def test_hyphenated_declarations_and_headings_share_one_key(self) -> None:
        declaration = self.declaration(
            "CA-R-2", "Atom.Content.Formal-Claim:: {::1};",
        )
        schema = compile_content_schema([declaration])
        atom = self.atom("CA-R-3", body="## Formal Claim\n\nFormal content.\n")

        self.assertEqual(("content.formal_claim",), schema.names)
        self.assertEqual({"content.formal_claim": "Formal content."}, content_columns(atom, schema))


    def test_finite_list_and_observed_headings_do_not_declare_children(self) -> None:
        declaration = self.declaration(
            "CA-R-3",
            "Atom.Content.Claim{::1}:: []{::0};\n"
            "Atom.Content.Claim.*[string, in (Formal Claim, Prose Claim)]{::1..2};",
        )
        atom = self.atom("CA-R-4", body="## Claim\n### Formal Claim\nText.\n### Prose Claim\nMore.\n")
        self.assertEqual((), compile_content_schema([declaration, atom]).names)


    def test_named_kind_claim_requires_proven_form_membership(self) -> None:
        ancestry = self.declaration("CA-R-5", "Atom/(.Header.Role := Operations)/Workflow;")
        property_rule = self.declaration("CA-R-6", "Workflow.Content.Mermaid Scheme:: {::1};")
        form_binding = self.declaration("CA-R-7", "Workflow.Header.Form:: [in (Workflow)]{::1};")
        workflow = self.atom(
            "CA-O-1", role="Operations", form="Workflow", body="## Mermaid Scheme\n\nflowchart LR\n",
        )
        action = {**workflow, "form": "Action"}
        path = "content.mermaid_scheme"

        unbound = compile_content_schema([ancestry, property_rule])
        self.assertEqual((path,), unbound.names)
        self.assertEqual({path: None}, content_columns(workflow, unbound))

        bound = compile_content_schema([ancestry, property_rule, form_binding])
        self.assertEqual({path: "flowchart LR"}, content_columns(workflow, bound))
        self.assertEqual({path: None}, content_columns(action, bound))

if __name__ == "__main__":
    unittest.main()
