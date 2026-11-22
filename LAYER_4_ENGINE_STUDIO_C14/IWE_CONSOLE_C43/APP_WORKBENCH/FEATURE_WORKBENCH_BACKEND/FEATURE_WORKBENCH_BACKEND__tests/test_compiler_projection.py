"""Workbench projection parity for native compiler claims."""

from pathlib import Path
import unittest

WORKBENCH = Path(__file__).resolve().parents[2]
PROGRAMMATIC = WORKBENCH.parents[1] / "FEATURE_PROGRAMMATIC"

from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared import (
    CONTENT_PROPERTY, RECURSIVE_CONTENT, NESTED_CONTENT, NESTED_HEADER, ROLE_HEADER, ROLE, INSTANCE_CHECK,
)
from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import compile_content_schema, declaration_statements
from KERNEL_MIXER_C59.declared_header_rules import header_declaration_rules
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import compile_role_folders


def _row(statements):
    body = "## Claim\n\n### Formal Claim\n\n```CFEL\n" + ";\n".join(statements) + ";\n```\n"
    return {"id": "CA-R-1", "ref": "CA-R-1", "version": 1, "source_path": "source.md",
            "status_group": "Current", "role": "Requirement", "form": "Declaration",
            "_content_bytes": body.encode(), "content_markdown": body}


def _native_row(source):
    row = _row(())
    body = f"## Claim\n### Formal Claim\n```python\n{source}\n```\n"
    return row | {"_content_bytes": body.encode(), "content_markdown": body}


class CompilerProjectionTests(unittest.TestCase):
    def test_content_property_contributes_same_roles_and_cardinalities(self):
        old = _row(("Atom/(.Header.Context.Role in RMED).Content.Semantics :: {::0..1}",
                    "Atom/(.Header.Context.Role in RMED).Content.Semantics.*[]{::0}"))
        self.assertEqual(compile_content_schema([old]), compile_content_schema([_native_row(CONTENT_PROPERTY)]))

    def test_recursive_content_and_role_scoped_ordering(self):
        prefix = "Atom/(.Header.Context.Role in RMED).Content"
        legacy = ("Atom.Content{::1} :: []{::0}", "Atom.Content.*[string]{::0+}",
                  "Atom.Content.**[string]{::0+}", "Atom.Content.** :: [markdown]",
                  f"{prefix}.Summary ;> {prefix}.Claim", f"{prefix}.Claim ;> {prefix}.Semantics",
                  f"{prefix}.Semantics ;> {prefix}.Details")
        self.assertEqual(compile_content_schema([_row(legacy)]), compile_content_schema([_native_row(RECURSIVE_CONTENT)]))

    def test_nested_content_property_preserves_role_selection(self):
        old = _row(("Atom/(.Header.Context.Role in RMED).Content.Claim.Prose Claim:: {::0..1}",
                    "Atom/(.Header.Context.Role in RMED).Content.Claim.Prose Claim.*[]{::0}"))
        self.assertEqual(compile_content_schema([old]), compile_content_schema([_native_row(NESTED_CONTENT)]))

    def test_nested_header_constraints_and_wildcard_formats(self):
        old = _row(("Atom.Header.Destination.File{::1} :: []{::0}",
                    "Atom.Header.Destination.File.*[in (Name, Path)]{::2}",
                    "Atom.Header.Destination.File.* :: [string]"))
        self.assertEqual(header_declaration_rules(old), header_declaration_rules(_native_row(NESTED_HEADER)))

    def test_nested_header_property_preserves_single_role(self):
        old = _row(("Atom/(.Header.Context.Role in (Plan)).Header.Context.Plan{::0..1} :: []{::0}",
                    "Atom/(.Header.Context.Role in (Plan)).Header.Context.Plan.*"
                    "[in (Work Sequence Number, AI Agent Confidence Threshold)]{::1..2}"))
        self.assertEqual(header_declaration_rules(old), header_declaration_rules(_native_row(ROLE_HEADER)))

    def test_role_order_and_form_are_qualified_by_role(self):
        expected = _row(("Atom.Header.Context.Role :: Method",
                         "Atom/(.Header.Context.Role := Method) >| (Role Order Number == 5)"))
        self.assertEqual(compile_role_folders(declaration_statements(expected)),
                         compile_role_folders(declaration_statements(_native_row(ROLE))))

    def test_instance_check_cannot_be_silently_dropped(self):
        with self.assertRaisesRegex(ValueError, "instance_check requires a typed validator"):
            compile_content_schema([_native_row(INSTANCE_CHECK)])


if __name__ == "__main__":
    unittest.main()
