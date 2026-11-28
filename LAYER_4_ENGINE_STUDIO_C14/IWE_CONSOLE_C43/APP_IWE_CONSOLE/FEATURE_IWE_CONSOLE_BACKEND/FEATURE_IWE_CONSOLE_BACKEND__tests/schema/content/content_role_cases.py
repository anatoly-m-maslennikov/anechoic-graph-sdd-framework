"""Content schema wildcard cases."""

from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import compile_content_schema
from ..content_schema_fixture import python_claim_body

WILDCARD_CONTENT = (
    "children(address='Atom.Content', occurrences='0+', name_format='string')"
)


def atom(role, form, body):
    return {
        "role": role,
        "form": form,
        "status_group": "Current",
        "content_markdown": body,
    }


class ContentRoleCases:
    def test_wildcard_constraints_do_not_declare_secret(self):
        declaration = atom(
            "Requirement",
            "Declaration",
            python_claim_body(
                "children(address='Atom.Content', occurrences='0+', name_format='string')\n"
                "property_rule(address='Atom/(.Header.Role := Method).Content.Secret', value_format='', values='0')",
            ),
        )
        method = atom("Method", "Solution", "## Secret\n\nHidden.\n")
        plan = atom("Plan", "Plan", "## Secret\n\nVisible.\n")
        schema = compile_content_schema([declaration, method, plan])
        self.assertIn(("*",), {rule.path for rule in schema.rules})
        self.assertNotIn("content.secret", schema.names)

    def test_filtered_wildcard_preserves_fences_and_role_boundaries(self):
        declaration = atom(
            "Requirement",
            "Declaration",
            python_claim_body(
                "children(address='Atom/(.Header.Role in (Plan, Concern)).Content',\n"
                "    occurrences='0+', name_format='string', recursive=True)\n"
                "property_rule(address='Atom/(.Header.Role in (Plan, Concern)).Content.Project Objective.Nested Scope',"
                " values='1')",
            ),
        )
        plan = atom(
            "plan",
            "Plan",
            "## Project Objective\n\nText.\n\n"
            "```md\n### Not A Heading\n```\n\n### Nested Scope\n\nInside.\n",
        )
        method = atom(
            "Method",
            "Solution",
            plan["content_markdown"] + "\n## Private Note\n\nHidden.\n",
        )
        schema = compile_content_schema([declaration, plan, method])
        self.assertIn("content.project_objective.nested_scope", schema.names)
        self.assertNotIn("content.private_note", schema.names)
        self.assertNotIn(
            "content.project_objective.not_a_heading", schema.names
        )
        self.assertEqual(
            "Inside.",
            schema.values(plan)["content.project_objective.nested_scope"],
        )
        self.assertIsNone(
            schema.values(method)["content.project_objective.nested_scope"]
        )

    def test_generic_declaration_exposes_content_for_every_role_and_new_role(
        self,
    ):
        examples = [
            ("Concern", "Problem", "Concern"),
            ("Analysis & Advisory", "Analysis Report", "Report"),
            ("Plan", "Plan", "Objective"),
            ("Requirement", "Definition", "Summary"),
            ("Method", "Decision", "Method"),
            ("Evaluation", "Eval Case", "Evaluation"),
            ("Delivery", "Decision", "Delivery"),
            ("Operations", "Action", "Operation"),
            ("Example New Role", "New Form", "New Section"),
        ]
        properties = "\n".join(
            f"property_rule(address='Atom.Content.{heading}', values='1')"
            for _, _, heading in examples
        )
        declaration = atom(
            "Requirement",
            "Declaration",
            python_claim_body(f"{WILDCARD_CONTENT}\n{properties}"),
        )
        rows = [
            atom(role, form, f"## {heading}\n\nValue.\n")
            for role, form, heading in examples
        ]
        schema = compile_content_schema([declaration, *rows])
        for row, (_, _, heading) in zip(rows, examples):
            name = "content." + heading.casefold().replace(" ", "_")
            self.assertEqual("Value.", schema.values(row)[name])

    def test_wildcards_do_not_expose_observed_paths_or_split_prose(self):
        declaration = atom(
            "Requirement",
            "Declaration",
            python_claim_body(
                "children(address='Atom.Content', occurrences='0+', name_format='string')\n"
                "children(address='Atom.Content', occurrences='0+', name_format='string', recursive=True)\n"
                "property_rule(address='Atom.Content.Claim', value_format='', values='0')\n"
                "property_rule(address='Atom/(.Header.Role in RMED).Content.Claim.Prose Claim', values='1')",
            ),
        )
        prose = atom(
            "Method",
            "Direct Policy",
            (
                "## Claim\n\n### Prose Claim\n\nText.\n\n#### Note\n\nStill "
                "prose.\n"
            ),
        )
        legacy = atom(
            "Requirement",
            "Rule",
            "## Claim\n\nText.\n\n### Note\n\nStill prose.\n",
        )
        plan = atom(
            "Plan", "Plan", "## Objective\n\nShip.\n\n### Scope\n\nInside.\n"
        )
        schema = compile_content_schema([declaration, prose, legacy, plan])
        self.assertNotIn("content.objective", schema.names)
        self.assertNotIn("content.objective.scope", schema.names)
        self.assertNotIn("content.claim", schema.names)
        self.assertNotIn("content.claim.prose_claim.note", schema.names)
        self.assertNotIn("content.claim.note", schema.names)
        self.assertIn(
            "#### Note", schema.values(prose)["content.claim.prose_claim"]
        )
        self.assertIn(
            "### Note", schema.values(legacy)["content.claim.prose_claim"]
        )
