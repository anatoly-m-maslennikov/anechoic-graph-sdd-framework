"""Workbench projections from native compiler claims."""

import unittest

from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.\
    FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared \
    import (
        CONTENT_PROPERTY,
        RECURSIVE_CONTENT,
        NESTED_CONTENT,
        NESTED_HEADER,
        ROLE_HEADER,
        ROLE,
        INSTANCE_CHECK,
    )  # fmt: skip
from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import (
    DeclarationSource,
    compile_content_schema,
    declaration_statements,
    header_declaration_rules,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.content.content__shared import (
    compile_role_folders,
)
from IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IWE_CONSOLE_BACKEND.\
    FEATURE_IWE_CONSOLE_BACKEND__tests.schema.content_schema_fixture \
    import python_claim_body  # fmt: skip


SOURCE = DeclarationSource("CA-R-1", 1, "source.md")
RMED_ROLES = frozenset({"Requirement", "Method", "Evaluation", "Delivery"})


def _native_row(source):
    return {
        "id": SOURCE.reference,
        "ref": SOURCE.reference,
        "version": SOURCE.version,
        "source_path": SOURCE.source_path,
        "status_group": "Current",
        "role": "Requirement",
        "form": "Declaration",
        "content_markdown": python_claim_body(source),
    }


class CompilerProjectionTests(unittest.TestCase):
    def test_content_property_contributes_roles_and_cardinalities(self):
        schema = compile_content_schema([_native_row(CONTENT_PROPERTY)])

        self.assertEqual(("content.semantics",), schema.names)
        self.assertEqual((SOURCE,), schema.sources)
        field, children = schema.rules
        self.assertTrue(field.value_bearing)
        self.assertEqual(RMED_ROLES, field.roles)
        self.assertEqual(("semantics", "*"), children.path)
        self.assertTrue(children.prohibited)
        self.assertEqual(RMED_ROLES, children.roles)

    def test_recursive_content_and_role_scoped_ordering(self):
        row = _native_row(RECURSIVE_CONTENT)
        schema = compile_content_schema([row])
        prefix = (
            "Atom/(.Header.Context.Role in (Requirement, Method, Evaluation, "
            "Delivery)).Content"
        )
        statements = [
            statement for statement, _ in declaration_statements(row)
        ]

        self.assertEqual((), schema.names)
        self.assertEqual(
            (("*",), ("**",)), tuple(rule.path for rule in schema.rules)
        )
        self.assertEqual(
            [
                f"{prefix}.Summary ;> {prefix}.Claim",
                f"{prefix}.Claim ;> {prefix}.Semantics",
                f"{prefix}.Semantics ;> {prefix}.Details",
            ],
            [statement for statement in statements if ";>" in statement],
        )

    def test_nested_content_property_preserves_role_selection(self):
        schema = compile_content_schema([_native_row(NESTED_CONTENT)])

        self.assertEqual(("content.claim.prose_claim",), schema.names)
        body = {"content_markdown": "## Claim\n\n### Prose Claim\n\nText.\n"}
        self.assertEqual(
            {"content.claim.prose_claim": "Text."},
            schema.values({**body, "role": "Method"}),
        )
        self.assertEqual(
            {"content.claim.prose_claim": None},
            schema.values({**body, "role": "Plan"}),
        )

    def test_nested_header_constraints_and_wildcard_formats(self):
        row = _native_row(NESTED_HEADER)
        (rule,) = header_declaration_rules(row)

        self.assertEqual(("destination", "file", "*"), rule.path)
        self.assertEqual("VARCHAR", rule.format)
        self.assertIn(
            ("Atom.Header.Destination.File.*[in (Name, Path)]{::2}", SOURCE),
            declaration_statements(row),
        )

    def test_nested_header_property_preserves_single_role(self):
        row = _native_row(ROLE_HEADER)
        self.assertEqual(
            (
                (
                    (
                        "Atom/(.Header.Context.Role in "
                        "(Plan)).Header.Context.Plan{::0..1} :: []{::0}"
                    ),
                    SOURCE,
                ),
                (
                    "Atom/(.Header.Context.Role in (Plan)).Header.Context."
                    "Plan."
                    "*[in (Work Sequence Number, AI Agent Confidence "
                    "Threshold)]{::1..2}",
                    SOURCE,
                ),
            ),
            declaration_statements(row),
        )

    def test_role_order_defines_folder(self):
        self.assertEqual(
            {"Method": ("05_method", SOURCE)},
            compile_role_folders(declaration_statements(_native_row(ROLE))),
        )

    def test_instance_check_cannot_be_silently_dropped(self):
        with self.assertRaisesRegex(
            ValueError, "instance_check requires a typed validator"
        ):
            compile_content_schema([_native_row(INSTANCE_CHECK)])


if __name__ == "__main__":
    unittest.main()
