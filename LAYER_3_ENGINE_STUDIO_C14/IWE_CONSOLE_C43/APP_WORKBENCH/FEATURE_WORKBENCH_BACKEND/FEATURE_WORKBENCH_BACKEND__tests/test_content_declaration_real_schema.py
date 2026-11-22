from __future__ import annotations

import json
from pathlib import Path
import unittest



APP_ROOT = Path(__file__).resolve().parents[3]
ASSETS = Path(__file__).resolve().parent / "assets" / "content_declaration_schema"
SEALED_MODEL = APP_ROOT.parent / "FEATURE_PROGRAMMATIC/FEATURE_TOOLS/FEATURE_TOOLS__tests/assets/lifecycle_schema_declarations/04_requirement"


from KERNEL_MIXER_C59.content_columns import content_columns  # noqa: E402
from KERNEL_MIXER_C59.content_schema import (  # noqa: E402
    compile_content_schema,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.markdown_content__pub import parse_content  # noqa: E402
from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.source_content_schema import SourceContentSchema  # noqa: E402


from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.FEATURE_WORKBENCH_BACKEND__tests.content_schema_fixture import ContentSchemaFixture


class ContentDeclarationSchemaTests(ContentSchemaFixture):
    def test_ancestry_only_changes_trigger_content_shape_comparison(self) -> None:
        property_rule = self.declaration("CA-R-8", "Workflow.Content.Mermaid Scheme:: {::1};")
        ancestry = self.declaration("CA-R-9", "Atom/(.Header.Role := Operations)/Workflow;")
        state = SourceContentSchema()
        state.rebuild([property_rule])
        self.assertTrue(state.changes_schema({ancestry["source_path"]: ancestry}))
        state.rebuild([property_rule, ancestry])
        self.assertTrue(state.changes_schema({ancestry["source_path"]: None}))


    def test_declared_children_produce_rmed_claim_columns_and_keep_legacy_prose(self) -> None:
        declaration = self.declaration(
            "CA-R-3",
            "Atom/(.Header.Role in RMED).Content.Claim{::1}:: []{::0};\n"
            "Atom/(.Header.Role in RMED).Content.Claim.*[string, in (Formal Claim, Prose Claim)]{::1..2};\n"
            "Atom/(.Header.Role in RMED).Content.Claim.Formal Claim:: {::1};\n"
            "Atom/(.Header.Role in RMED).Content.Claim.Prose Claim:: {::1};",
        )
        schema = compile_content_schema([declaration])
        atom = self.atom(
            "CA-R-4",
            body="## Claim\n\nFirst line.\n### Unregistered heading\n\nSecond line.\n",
        )

        self.assertEqual(
            ("content.claim.formal_claim", "content.claim.prose_claim"), schema.names,
        )
        self.assertEqual(
            {
                "content.claim.formal_claim": None,
                "content.claim.prose_claim": "First line.\n### Unregistered heading\n\nSecond line.",
            },
            content_columns(atom, schema),
        )


    def test_prose_claim_keeps_undeclared_children_and_uses_exact_declared_spans(self) -> None:
        declaration = self.declaration(
            "CA-R-3",
            "Atom/(.Header.Role in RMED).Content.Claim.Prose Claim:: {::1};\n"
            "Atom/(.Header.Role in RMED).Content.Claim.Prose Claim.Structured Section:: {::0..1};",
        )
        schema = compile_content_schema([declaration])
        atom = self.atom(
            "CA-R-4",
            body="""## Claim

### Prose Claim

Intro.

```text
#### Structured Section
Must remain in the code fence.
```

#### Presentation Context

Keep this heading.

#### Structured Section

Expose separately.
""",
        )

        values = content_columns(atom, schema)
        self.assertEqual(
            """Intro.

```text
#### Structured Section
Must remain in the code fence.
```

#### Presentation Context

Keep this heading.""",
            values["content.claim.prose_claim"],
        )
        self.assertEqual("Expose separately.", values["content.claim.prose_claim.structured_section"])


    def test_generic_property_keeps_undeclared_children_and_separates_declared_child(self) -> None:
        body = (
            "## Operation\r\n\r\nPrepare.\r\n\r\n### Action\r\n\r\nRun it.\r\n\r\n"
            "### Steps\r\n\r\n1. Verify.\r\n"
        )
        operation = self.declaration("CA-R-3", "Atom.Content.Operation:: {::1};")
        declared_action = self.declaration(
            "CA-R-3",
            "Atom.Content.Operation:: {::1};\nAtom.Content.Operation.Action:: {::1};",
        )

        self.assertEqual(
            {"content.operation": "Prepare.\r\n\r\n### Action\r\n\r\nRun it.\r\n\r\n### Steps\r\n\r\n1. Verify."},
            content_columns(self.atom("CA-R-4", body=body), compile_content_schema([operation])),
        )
        self.assertEqual(
            {
                "content.operation": "Prepare.\r\n\r\n### Steps\r\n\r\n1. Verify.",
                "content.operation.action": "Run it.",
            },
            content_columns(self.atom("CA-R-4", body=body), compile_content_schema([declared_action])),
        )


    def test_generic_property_reconstructs_no_span_public_records(self) -> None:
        body = "## Operation\r\n\r\nPrepare.\r\n\r\n### Presentation\r\n\r\nKeep it.\r\n"
        row = self.atom("CA-R-4", body=body)
        row["content_properties_json"] = parse_content(body)
        schema = compile_content_schema([
            self.declaration("CA-R-3", "Atom.Content.Operation:: {::1};"),
        ])

        self.assertEqual(
            {"content.operation": "Prepare.\r\n\r\n### Presentation\r\n\r\nKeep it."},
            content_columns(row, schema),
        )


    def test_prose_claim_with_only_declared_child_keeps_empty_parent(self) -> None:
        schema = compile_content_schema([self.declaration(
            "CA-R-3",
            "Atom/(.Header.Role in RMED).Content.Claim.Prose Claim:: {::1};\n"
            "Atom/(.Header.Role in RMED).Content.Claim.Prose Claim.Structured Section:: {::1};",
        )])
        body = "## Claim\r\n\r\n### Prose Claim\r\n\r\n#### Structured Section\r\n\r\nOnly child.\r\n"

        self.assertEqual(
            {
                "content.claim.prose_claim": None,
                "content.claim.prose_claim.structured_section": "Only child.",
            },
            content_columns(self.atom("CA-R-4", body=body), schema),
        )


    def test_undeclared_headings_stay_inside_markdown_and_normalized_declared_duplicates_fail(self) -> None:
        declaration = self.declaration("CA-R-5", "Atom.Content.Summary{::1}:: {::1};")
        schema = compile_content_schema([declaration])
        ordinary = self.atom("CA-R-6", body="## Summary\n\nOne\n\n## Unregistered Heading\n\nTwo\n")
        duplicate = self.atom("CA-R-7", body="## Summary\n\nOne\n\n## Summary\n\nTwo\n")

        self.assertEqual({"content.summary": "One"}, content_columns(ordinary, schema))
        with self.assertRaisesRegex(ValueError, "duplicate declared content property: summary"):
            content_columns(duplicate, schema)
        self.assertEqual({"content.summary": "One"}, content_columns({**duplicate, "status_group": "Archived"}, schema))


    def test_real_current_model_declarations_compile_and_record_provenance(self) -> None:
        rows = self._current_model_rows()
        requirement = self.atom(
            "CA-R-fixture", form="Rule",
            body="## Summary\n\nOne.\n### Presentation heading\n\nStill Summary.\n"
                 "## Claim\n\n### Prose Claim\n\nText.\n#### Prose heading\n\nStill prose.\n"
                 "```text\n## Fenced heading\n```\n",
        )
        schema = self._compile_model_rows([*rows, requirement])
        self.assertTrue(
            {
                "content.claim.formal_claim", "content.claim.prose_claim", "content.details",
                "content.semantics", "content.summary",
            }.issubset(schema.names),
        )
        self.assertEqual(self._compile_model_rows(rows).names, schema.names)
        self.assertNotIn("content.summary.presentation_heading", schema.names)
        self.assertNotIn("content.claim.prose_claim.prose_heading", schema.names)
        self.assertNotIn("content.fenced_heading", schema.names)
        self.assertIn("### Presentation heading", schema.values(requirement)["content.summary"])
        self.assertIn("#### Prose heading", schema.values(requirement)["content.claim.prose_claim"])
        asset = schema.asset()
        self.assertGreaterEqual(len(asset["content_declaration_sources"]), 6)
        self.assertIn("CA-R-2500", {source["reference"] for source in asset["content_declaration_sources"]})
        self.assertEqual("VARCHAR", next(
            item["format"] for item in asset["content_columns"] if item["name"] == "content.claim.formal_claim"
        ))
        json.dumps(asset)


    def test_prepared_header_grouping_keeps_the_real_content_schema(self) -> None:
        rows = self._current_model_rows()
        before = self._compile_model_rows(rows)
        transform = self._prepared_reference_transform()
        prepared = []
        for row in rows:
            body = transform(row["content_markdown"])
            prepared.append({
                **row,
                "content_markdown": body,
                "_content_bytes": body.encode("utf-8"),
                "content_properties_json": parse_content(body, tolerate_duplicate_siblings=True),
            })

        after = self._compile_model_rows(prepared)
        claim_rules = [rule for rule in after.rules if rule.source.reference == "CA-R-2500"]
        self.assertTrue(claim_rules)
        self.assertEqual(
            {frozenset({"Requirement", "Method", "Evaluation", "Delivery"})},
            {rule.roles for rule in claim_rules},
        )
        self.assertEqual(before.shape, after.shape)


    def test_declaration_provenance_does_not_change_the_schema_shape(self) -> None:
        first = self.declaration("CA-R-1", "Atom.Content.Summary{::1}:: {::1};")
        later = {**first, "version": 2, "source_path": "model/renamed.md"}
        original = compile_content_schema([first])
        replaced = compile_content_schema([later])

        self.assertEqual(original.shape, replaced.shape)
        self.assertNotEqual(original.asset(), replaced.asset())

if __name__ == "__main__":
    unittest.main()
