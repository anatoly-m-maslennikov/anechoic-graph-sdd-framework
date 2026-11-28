"""Content declarations apply to admitted Role/Form serializations."""

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import yaml


from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import (
    ContentSchema,
    DeclarationSource,
    compile_content_schema,
)
from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import HeaderRule
from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import HeaderColumn
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.content.content__shared import (
    carrier_read_view,
)
from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import registry_contribution
from IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IWE_CONSOLE_BACKEND.FEATURE_IWE_CONSOLE_BACKEND__shared import (
    SourceReader,
)
from IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IWE_CONSOLE_BACKEND.FEATURE_IWE_CONSOLE_BACKEND__tests.sources._source_reader_fixture import (
    SourceReaderFixture,
)
from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared import (
    write_scope_unit_declarations,
)
from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared import (
    source_path,
    write_atom,
    write_settings,
)

from IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IWE_CONSOLE_BACKEND.FEATURE_IWE_CONSOLE_BACKEND__tests.schema.content_schema_fixture import (
    python_claim_body,
)


from .content_role_cases import ContentRoleCases, WILDCARD_CONTENT, atom


METHOD_PROSE = (
    "property_rule(address='Atom/(.Header.Role := Method)/(.Header.Form := Direct Policy)"
    ".Content.Claim.Prose Claim', values='1')"
)


class CarrierSerializationTests(
    ContentRoleCases, unittest.TestCase, SourceReaderFixture
):
    def test_encoded_relation_declaration_is_admitted_without_changing_header(
        self,
    ):
        header = {
            "context": {"role": "requirement", "form": "relation_definition"}
        }
        row = atom(
            "requirement",
            "relation_definition",
            python_claim_body(
                'subject_path(address="Relation//RELATES_TO")',
            ),
        ) | {
            "source_path": "model.md",
            "id": "CA-R-1",
            "version": 1,
            "header_json": header,
        }
        self.assertIn("RELATES_TO", registry_contribution(row).names)
        self.assertEqual(
            header,
            {
                "context": {
                    "role": "requirement",
                    "form": "relation_definition",
                }
            },
        )
        row["form"] = "Relation_Definition"
        self.assertFalse(registry_contribution(row).names)

    def test_current_model_presentation_headings_do_not_create_columns(self):
        model = Path(__file__).resolve().parents[6] / (
            "FEATURE_PROGRAMMATIC/FEATURE_TOOLS/FEATURE_TOOLS__tests/assets/"
            "lifecycle_schema_declarations/04_requirement"
        )
        declarations = []
        for identifier in ("2498", "2499"):
            path = next(model.rglob(f"CA-R-{identifier}-*.md"))
            _, head, body = path.read_text().split("---", 2)
            header = carrier_read_view(yaml.safe_load(head))
            declarations.append(atom(header["role"], header["form"], body))
        source = atom(
            "Method", "Decision", "## Summary\n\nTop.\n\n### Note\n\nKeep.\n"
        )
        schema = compile_content_schema([*declarations, source])
        self.assertNotIn("content.summary.note", schema.names)
        self.assertIn("### Note", schema.values(source)["content.summary"])

    def test_literal_child_declaration_does_not_invent_siblings(self):
        declaration = atom(
            "Requirement",
            "Declaration",
            python_claim_body(
                "children(address='Atom.Content', occurrences='0+', name_format='string', recursive=True)\n"
                "children(address='Atom.Content.Summary', occurrences='0')\n"
                "property_rule(address='Atom.Content.Summary.Allowed', values='1')",
            ),
        )
        source = atom(
            "Method",
            "Decision",
            "## Summary\n\n### Allowed\n\nYes.\n\n### Other\n\nNo.\n",
        )
        schema = compile_content_schema([declaration, source])
        self.assertIn("content.summary.allowed", schema.names)
        self.assertNotIn("content.summary.other", schema.names)

    def test_validation_does_not_extract_all_content_columns(self):
        SourceReaderFixture.setUp(self)
        self._write_atom(
            "MAIN",
            "04_requirement",
            "CA-R-8-model.md",
            atom_id="CA-R-8",
            form="Declaration",
            body=python_claim_body(
                "children(address='Atom.Content', occurrences='0+', name_format='string')\n"
                "property_rule(address='Atom.Content.Objective', values='1')",
            ),
        )
        source = self._write_atom(
            "MAIN",
            "03_plan",
            "CA-P-1-plan.md",
            atom_id="CA-P-1",
            form="Plan",
            body="## Objective\n\nOne.\n\n## Objective\n\nTwo.\n",
        )
        source.write_text(
            source.read_text().replace('role: "Requirement"', 'role: "Plan"')
        )
        with patch.object(
            ContentSchema,
            "values",
            side_effect=AssertionError("validation extracted every column"),
        ):
            rows, _, diagnostics = self._capture()
        self.assertNotIn("CA-P-1", {row["id"] for row in rows})
        self.assertIn(source.relative_to(self.root).as_posix(), diagnostics)
        self.assertIn("duplicate", diagnostics.casefold())

    def test_mode_one_header_rule_matches_serialized_role_and_form(self):
        rule = HeaderRule(
            ("custom",),
            "VARCHAR",
            frozenset({"Method"}),
            frozenset({"Direct Policy"}),
            DeclarationSource("CA-R-1", 1, "model.md"),
        )
        column = HeaderColumn(
            ("custom",), "header.custom", "VARCHAR", True, rules=(rule,)
        )
        self.assertTrue(
            column.applies({"role": "method", "form": "direct_policy"})
        )
        self.assertFalse(
            column.applies({"role": "method", "form": "solution"})
        )

    def test_serialized_role_and_form_match_business_spelling(self):
        declaration = atom(
            "requirement",
            "entity_definition",
            python_claim_body(METHOD_PROSE),
        )
        schema = compile_content_schema([declaration])
        body = "## Claim\n\n### Prose Claim\n\nThe method.\n"
        self.assertEqual(
            {"content.claim.prose_claim": "The method."},
            schema.values(atom("method", "direct_policy", body)),
        )
        self.assertEqual(
            {"content.claim.prose_claim": None},
            schema.values(atom("Method", "Solution", body)),
        )

    def test_observed_headings_do_not_change_wildcard_schema(self):
        SourceReaderFixture.setUp(self)
        self._write_atom(
            "MAIN",
            "04_requirement",
            "CA-R-8-model.md",
            atom_id="CA-R-8",
            form="Declaration",
            body=python_claim_body(WILDCARD_CONTENT),
        )
        first = "## Objective\n\nShip.\n"
        source = self._write_atom(
            "MAIN",
            "03_plan",
            "CA-P-1-plan.md",
            atom_id="CA-P-1",
            form="Plan",
            body=first,
        )
        raw = source.read_text().replace('role: "Requirement"', 'role: "Plan"')
        source.write_text(raw)
        self.reader.capture()
        self.assertIn(
            ("*",), {rule.path for rule in self.reader.content_schema.rules}
        )
        shape = self.reader.content_schema.shape
        relative = source.relative_to(self.root).as_posix()
        for body in (
            "## Objective\n\nShip later.\n",
            first + "\n## Scope\n\nAll.\n",
            first,
        ):
            source.write_text(raw.replace(first, body))
            rows, _ = self.reader.capture(
                [{"operation": "update", "new_path": relative}]
            )
            self.assertIn("CA-P-1", {row["id"] for row in rows})
            self.assertIsNotNone(self.reader.capture_delta)
            self.assertEqual(shape, self.reader.content_schema.shape)

    def _write_mode_model(self, declarations):
        model = source_path(
            declarations, "ENGINE", "04_requirement", "CA-R-900.md"
        )
        write_atom(
            model,
            "CA-R-900",
            body=python_claim_body(METHOD_PROSE),
        )
        model.write_text(
            model.read_text().replace(
                'form: "Definition"', 'form: "entity_definition"'
            )
        )

    def _write_mode_methods(self, declarations):
        for version, directory_name in ((1, ""), (2, "draft")):
            path = source_path(
                declarations,
                "ENGINE",
                "05_method",
                str(
                    Path(directory_name)
                    / f"CA-M-514{'@2-draft' if version == 2 else ''}.md"
                ),
            )
            write_atom(
                path,
                "CA-M-514",
                status="Draft" if version == 2 else "Active",
                version=version,
                body="## Claim\n\n### Prose Claim\n\nMethod text.\n",
            )
            path.write_text(
                path.read_text()
                .replace('role: "Requirement"', 'role: "method"')
                .replace(
                    'form: "Definition"',
                    'form: "direct_policy"',
                )
            )

    def test_current_and_draft_in_both_schema_modes(self):
        temporary_root = (
            Path.cwd() / ".anechoic_tmp" / "APP_IWE_CONSOLE__tests"
        )
        temporary_root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=temporary_root) as directory:
            root = Path(directory)
            control = write_settings(root)
            declarations = write_scope_unit_declarations(
                root,
                (
                    {
                        "scope_unit_name": "ENGINE",
                        "scope_unit_label": "FEATURE",
                    },
                ),
                control_root=control,
            )
            self._write_mode_model(declarations)
            self._write_mode_methods(declarations)
            for mode in (1, 2):
                reader = SourceReader(root, control, schema_mode=mode)
                rows, _ = reader.capture()
                candidates = [row for row in rows if row["id"] == "CA-M-514"]
                self.assertEqual(
                    {"Current", "Draft"},
                    {row["status_group"] for row in candidates},
                )
                self.assertEqual(
                    {"Method text."},
                    {
                        reader.content_schema.values(row)[
                            "content.claim.prose_claim"
                        ]
                        for row in candidates
                    },
                )


if __name__ == "__main__":
    unittest.main()
