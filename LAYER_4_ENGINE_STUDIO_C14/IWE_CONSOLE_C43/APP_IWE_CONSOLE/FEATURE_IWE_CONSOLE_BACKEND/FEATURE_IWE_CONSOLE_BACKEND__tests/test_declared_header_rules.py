from __future__ import annotations

from pathlib import Path
import unittest

from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import DeclarationSource  # noqa: E402
from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import (  # noqa: E402
    compile_header_rules,
    header_declaration_rules,
    resolve_header_rules,
)
from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import declared_header_schema  # noqa: E402

from IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IWE_CONSOLE_BACKEND.\
    FEATURE_IWE_CONSOLE_BACKEND__tests.content_schema_fixture \
    import python_claim_body  # fmt: skip


APP_ROOT = Path(__file__).resolve().parents[3]


FILE_LAYOUT = (
    "property_rule(address='Atom.Header.Carrier Destination.File', value_format='', occurrences='1', values='0')\n"
    "allowed_children(address='Atom.Header.Carrier Destination.File', names=('Name', 'Path'), occurrences='2')\n"
    "property_rule(address='Atom.Header.Carrier Destination.File.*', value_format='string')"
)


class DeclaredHeaderRulesTests(unittest.TestCase):
    @staticmethod
    def declaration(
        reference: str,
        source: str,
        *,
        status_group: str = "Current",
        role: str = "Requirement",
        form: str = "Declaration",
        version: int = 1,
    ) -> dict:
        return {
            "ref": reference,
            "id": reference,
            "version": version,
            "source_path": f"model/{reference}.md",
            "status_group": status_group,
            "role": role,
            "form": form,
            "content_markdown": python_claim_body(source),
        }

    def test_python_outside_formal_claim_does_not_contribute(self) -> None:
        source = "property_rule(address='Atom.Header.Priority', value_format='string', values='1')"
        declaration = self.declaration("CA-R-1", source)
        declaration["content_markdown"] = (
            f"## Claim\n\n```python\n{source}\n```\n"
        )
        self.assertEqual((), compile_header_rules([declaration]))

    def test_declared_paths_replace_the_handwritten_property_list(
        self,
    ) -> None:
        rules = compile_header_rules(
            [
                self.declaration(
                    "CA-R-1",
                    "property_rule(address='Atom.Header.Review State', value_format='bool', values='1')",
                ),
            ]
        )

        self.assertEqual(
            ((("review_state",), "BOOLEAN"),),
            tuple((rule.path, rule.format) for rule in rules),
        )
        self.assertNotIn(
            ("label", "VARCHAR"),
            tuple((rule.path, rule.format) for rule in rules),
        )

    def test_role_and_form_selectors_remain_on_the_rule(self) -> None:
        rules = header_declaration_rules(
            self.declaration(
                "CA-R-2",
                "property_rule(address='Atom/(.Header.Context.Role in RMED)/(.Header.Context.Form: Policy)"
                ".Header.Priority', value_format='string', values='1')",
            )
        )

        self.assertEqual(1, len(rules))
        self.assertEqual(
            frozenset({"Requirement", "Method", "Evaluation", "Delivery"}),
            rules[0].roles,
        )
        self.assertEqual(frozenset({"Policy"}), rules[0].forms)

    def test_grouped_and_flat_alias_declarations_share_one_sql_column(
        self,
    ) -> None:
        rules = compile_header_rules(
            [
                self.declaration(
                    "CA-R-8",
                    (
                        "property_rule(address='Atom.Header.Role', value_format='string', values='1')\n"
                        "property_rule(address='Atom.Header.Context.Role', value_format='string', values='1')"
                    ),
                )
            ]
        )
        schema = declared_header_schema(rules)
        self.assertEqual(("header.context.role",), schema.names)
        column = schema.columns[0]
        for header in ({"role": "method"}, {"context": {"role": "method"}}):
            self.assertEqual(
                "method", schema.value({"header_json": header}, column)
            )

    def test_scalar_collection_grouping_and_updated_at_formats(self) -> None:
        rules = compile_header_rules(
            [
                self.declaration(
                    "CA-R-3",
                    "property_rule(address='Atom.Header.Version', value_format='int', values='1')\n"
                    "property_rule(address='Atom.Header.Enabled', value_format='bool', values='1')\n"
                    "property_rule(address='Atom.Header.Container.atom', value_format='atom id', values='0..1')\n"
                    "property_rule(address='Atom.Header.Topics', value_format='', occurrences='1', values='0')\n"
                    "property_rule(address='Atom.Header.Topics.Dependencies', value_format='string', values='0+')\n"
                    "property_rule(address='Atom.Header.Topics.Limited', value_format='string', values='0..2')\n"
                    "property_rule(address='Atom.Header.Updated At', value_format='datetime', values='1')",
                )
            ]
        )

        self.assertEqual(
            {
                ("version",): "BIGINT",
                ("enabled",): "BOOLEAN",
                ("container", "atom"): "VARCHAR",
                ("topics", "dependencies"): "JSON",
                ("topics", "limited"): "JSON",
                ("updated_at",): "TIMESTAMPTZ",
            },
            {rule.path: rule.format for rule in rules},
        )

    def test_wildcard_format_types_explicit_children_without_emitting_wildcard(
        self,
    ) -> None:
        rules = compile_header_rules(
            [
                self.declaration(
                    "CA-R-4",
                    FILE_LAYOUT + "\n"
                    "property_rule(address='Atom.Header.Carrier Destination.File.Name', values='1')\n"
                    "property_rule(address='Atom.Header.Carrier Destination.File.Path', values='1')",
                )
            ]
        )

        self.assertEqual(
            {
                ("carrier_destination", "file", "name"): "VARCHAR",
                ("carrier_destination", "file", "path"): "VARCHAR",
            },
            {rule.path: rule.format for rule in rules},
        )

    def test_cross_source_wildcard_format_resolves_raw_child_contributions(
        self,
    ) -> None:
        wildcard = self.declaration(
            "CA-R-2716",
            FILE_LAYOUT,
            version=2,
        )
        name = self.declaration(
            "CA-R-2717",
            "property_rule(address='Atom.Header.Carrier Destination.File.Name', values='1')",
            version=3,
        )
        path = self.declaration(
            "CA-R-2718",
            "property_rule(address='Atom.Header.Carrier Destination.File.Path', values='1')",
            version=3,
        )

        raw_name = header_declaration_rules(name)
        self.assertEqual(None, raw_name[0].format)
        self.assertEqual(
            DeclarationSource("CA-R-2717", 3, "model/CA-R-2717.md"),
            raw_name[0].source,
        )
        self.assertEqual(
            {
                ("carrier_destination", "file", "name"): "VARCHAR",
                ("carrier_destination", "file", "path"): "VARCHAR",
            },
            {
                rule.path: rule.format
                for rule in compile_header_rules([wildcard, name, path])
            },
        )
        self.assertEqual(
            compile_header_rules([wildcard, name, path]),
            resolve_header_rules(
                (
                    *header_declaration_rules(wildcard),
                    *raw_name,
                    *header_declaration_rules(path),
                )
            ),
        )

    def test_explicit_format_does_not_replace_an_inherited_wildcard_constraint(
        self,
    ) -> None:
        rules = compile_header_rules(
            [
                self.declaration(
                    "CA-R-1",
                    "property_rule(address='Atom.Header.Details.*', value_format='string')",
                ),
                self.declaration(
                    "CA-R-2",
                    "property_rule(address='Atom.Header.Details.Note', value_format='string')",
                ),
            ]
        )
        self.assertEqual(
            {
                ("CA-R-2", None, ("details", "note"), "VARCHAR"),
                ("CA-R-2", "CA-R-1", ("details", "note"), "VARCHAR"),
            },
            {
                (
                    rule.source.reference,
                    rule.format_source.reference
                    if rule.format_source
                    else None,
                    rule.path,
                    rule.format,
                )
                for rule in rules
            },
        )
        self.assertEqual(2, len(rules))

    def test_ignores_non_model_prose_formula_relations_and_noncurrent_sources(
        self,
    ) -> None:
        row = self.declaration(
            "CA-R-5",
            (
                "minimum_value(address='Atom.Header.ID', minimum=1)\n"
                "property_rule(address='Atom.Header.Relations', value_format='string', values='1')\n"
                "property_rule(address='Atom.Header.ID', value_format='string', values='1')"
            ),
        )
        row["content_markdown"] += (
            "\nproperty_rule(address='Atom.Header.Escaped', value_format='string')\n"
        )

        self.assertEqual(
            (("id",),),
            tuple(rule.path for rule in header_declaration_rules(row)),
        )
        self.assertEqual(
            (), header_declaration_rules({**row, "status_group": "Draft"})
        )
        self.assertEqual((), header_declaration_rules({**row, "role": "Plan"}))

    def test_source_pin_is_preserved_exactly(self) -> None:
        row = self.declaration(
            "CA-R-2701",
            "property_rule(address='Atom.Header.ID', value_format='string', values='1')",
            version=7,
        )

        self.assertEqual(
            DeclarationSource("CA-R-2701", 7, "model/CA-R-2701.md"),
            header_declaration_rules(row)[0].source,
        )


if __name__ == "__main__":
    unittest.main()
