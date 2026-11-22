from __future__ import annotations

import unittest
from pathlib import Path

import yaml

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.scope_carrier__pub import ScopeDeclarationError, has_scope_declaration_form
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.scope_declaration_parse__pub import parse_scope_unit_declaration
from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared import PROJECT
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.scope_unit_declarations__pub import read_scope_unit_declarations
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__tests.scope_unit_declaration_test_support import ScopeUnitFixture

TOOLS = Path(__file__).resolve().parents[1]


class ScopeUnitDeclarationReaderTests(ScopeUnitFixture, unittest.TestCase):
    def test_prose_only_delegation_has_no_inferred_pairs(self) -> None:
        _, source, _ = self.complete_tree()
        raw = source.read_text(encoding="utf-8").replace("form: Scope Unit Declaration", "form: Scope Delegation")
        start = raw.index("### Formal Claim")
        raw = (raw[:start] + "### Prose Claim\n\nRequirement / Rule is described here.\n").replace(
            "---\n", "---\ncontainer:\n  scope_unit: CA-SU-00\n", 1)
        delegation = source.parent / "prose.md"
        delegation.write_text(raw.replace("CA-R-2", "CA-R-8"), encoding="utf-8")
        result = read_scope_unit_declarations(self.root, self.control.name)
        self.assertEqual((), result.by_name["PARENT"].delegations[0].admitted_role_forms)
        delegation.write_text(delegation.read_text().replace("CA-SU-00", "CA-SU-99"), encoding="utf-8")
        with self.assertRaises(ScopeDeclarationError):
            read_scope_unit_declarations(self.root, self.control.name)

    def test_split_delegations_keep_sources_and_require_direct_parent(self) -> None:
        _, _, child = self.complete_tree()
        raw = child.read_text().replace("form: Scope Unit Declaration", "form: Scope Delegation")
        raw = raw[:raw.index("### Formal Claim")] + "### Prose Claim\n\nDelegated responsibility.\n"
        raw = raw.replace("---\n", "---\ncontainer:\n  scope_unit: CA-SU-1\n", 1)
        paths = [child.parent / "delegation1.md", child.parent / "delegation2.md"]
        for number, path in enumerate(paths, start=4):
            path.write_text(raw.replace("CA-R-3", f"CA-R-{number}"))
        result = read_scope_unit_declarations(self.root, self.control.name)
        self.assertEqual(set(paths), {item.source for item in result.by_name["CHILD"].delegations})
        digest = result.digest
        paths[1].write_text(paths[1].read_text().replace("responsibility", "work"))
        self.assertNotEqual(digest, read_scope_unit_declarations(self.root, self.control.name).digest)
        paths[0].write_text(paths[0].read_text().replace("CA-SU-1", "CA-SU-9"))
        with self.assertRaisesRegex(ScopeDeclarationError, "declared parent"):
            read_scope_unit_declarations(self.root, self.control.name)

    def test_structural_form_reader_accepts_valid_header_indentation_and_flow_style(self) -> None:
        for serializer in (
            lambda value: yaml.safe_dump(value, sort_keys=False, indent=4),
            lambda value: yaml.safe_dump(value, sort_keys=False, default_flow_style=True),
        ):
            with self.subTest(serializer=serializer):
                _, parent_source, _ = self.complete_tree()
                _, frontmatter, body = parent_source.read_text(encoding="utf-8").split("---", 2)
                header = yaml.safe_load(frontmatter)
                header.setdefault("context", {})["form"] = "Scope Unit Declaration"
                header.pop("form", None)
                parent_source.write_text("---\n" + serializer(header) + "---" + body, encoding="utf-8")

                declarations = read_scope_unit_declarations(self.root, self.control.name)

                self.assertEqual("Scope Unit Declaration", declarations.by_name["PARENT"].form)

    def test_nested_non_header_form_is_not_a_structural_candidate(self) -> None:
        raw = b"""---
context:
  role: Requirement
  form: Policy
parameters:
  form: Scope Delegation
---
"""

        self.assertFalse(has_scope_declaration_form(raw))

    def test_structural_prefilter_accepts_folded_and_escaped_yaml_values(self) -> None:
        for value in ('>-\n  Scope Unit\n  Declaration', r'"\x53cope Delegation"'):
            with self.subTest(value=value):
                self.assertTrue(has_scope_declaration_form(f"---\nform: {value}\n---\n".encode()))

    def test_malformed_canonical_flow_form_fails_closed(self) -> None:
        for context in (
            "context: {form: Scope Delegation, role: Requirement",
            "context: {role: Requirement, form: Scope Delegation",
        ):
            with self.subTest(context=context):
                raw = f"---\n{context}\n---\n".encode()
                self.assertTrue(has_scope_declaration_form(raw))

        unrelated = b"---\nparameters: {form: Scope Delegation\n---\n"
        self.assertFalse(has_scope_declaration_form(unrelated))

    def test_project_root_scope_delegation_refuses(self) -> None:
        source = self.declaration("demo", "CA-R-1", source=self.control / "CA-R-1-demo.md", project=True)
        source.write_text(source.read_text(encoding="utf-8").replace(
            "form: Scope Unit Declaration", "form: Scope Delegation",
        ), encoding="utf-8")

        with self.assertRaises(ScopeDeclarationError):
            parse_scope_unit_declaration(source.read_bytes(), source)
        with self.assertRaises(ScopeDeclarationError):
            read_scope_unit_declarations(self.root, self.control.name)

    def test_parser_rejects_order_number_for_unordered_scope_unit(self) -> None:
        source = self.declaration("UNIT", "CA-R-2", scope_id="CA-SU-2", parent=PROJECT)
        source.write_text(source.read_text(encoding="utf-8").replace(
            "ordered=False", "ordered=False, order_number=1",
        ), encoding="utf-8")

        with self.assertRaisesRegex(ScopeDeclarationError, "required only"):
            parse_scope_unit_declaration(source.read_bytes(), source)

    def test_duplicate_scope_unit_name_refuses(self) -> None:
        self.declaration("demo", "CA-R-1", source=self.control / "CA-R-1-demo.md", project=True)
        self.declaration("UNIT", "CA-R-2", scope_id="CA-SU-2", parent=PROJECT)
        self.declaration(
            "UNIT", "CA-R-3", source=self.control / "04_requirement" / "duplicate.md",
            scope_id="CA-SU-3", parent=PROJECT,
        )

        with self.assertRaisesRegex(ScopeDeclarationError, "names and IDs"):
            read_scope_unit_declarations(self.root, self.control.name)

    def test_duplicate_scope_unit_id_refuses(self) -> None:
        self.declaration("demo", "CA-R-1", source=self.control / "CA-R-1-demo.md", project=True)
        self.declaration("FIRST", "CA-R-2", scope_id="TEST-SU-1", parent=PROJECT)
        self.declaration("SECOND", "CA-R-3", scope_id="TEST-SU-1", parent=PROJECT)

        with self.assertRaisesRegex(ScopeDeclarationError, "names and IDs"):
            read_scope_unit_declarations(self.root, self.control.name)

    def test_unsafe_control_root_refuses(self) -> None:
        with self.assertRaisesRegex(ScopeDeclarationError, "direct Project control"):
            read_scope_unit_declarations(self.root, "../.anechoic_demo")

    def test_non_ca_scope_id_and_spaced_project_name_remain_declaration_data(self) -> None:
        (self.control / "anechoic_project_settings.toml").write_text(
            '[project]\nname = "Friendly Demo"\n[paths]\ncontrol_root = ".anechoic_demo"\n', encoding="utf-8",
        )
        self.declaration("Friendly Demo", "CA-R-1", source=self.control / "CA-R-1-demo.md", project=True)
        self.declaration("UNIT", "CA-R-2", scope_id="TEST-SU-1", parent="Friendly Demo")

        result = read_scope_unit_declarations(self.root, self.control.name)
        self.assertEqual(result.root.name, "Friendly Demo")
        self.assertEqual(result.by_name["UNIT"].scope_unit_id, "TEST-SU-1")


if __name__ == "__main__":
    unittest.main()
