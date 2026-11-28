"""Small header schema boundary cases."""

from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import (
    DeclarationSource,
    HeaderRule,
    declared_header_schema,
    compile_header_rules,
)
from ..workbench_schema_fixture import atom


class WorkbenchSchemaSmallCases:
    def test_equal_header_validation_shapes_ignore_distinct_provenance(
        self,
    ) -> None:
        occurrence = DeclarationSource("CA-R-PROPERTY", 1, "property.md")
        first = DeclarationSource("CA-R-PARENT-1", 1, "parent-1.md")
        second = DeclarationSource("CA-R-PARENT-2", 1, "parent-2.md")
        rule = HeaderRule(
            ("context", "label"),
            "VARCHAR",
            frozenset({"Operations"}),
            frozenset({"Workflow"}),
            occurrence,
            provenance=(first,),
        )
        another = HeaderRule(
            ("context", "label"),
            "VARCHAR",
            frozenset({"Operations"}),
            frozenset({"Workflow"}),
            occurrence,
            provenance=(second,),
        )
        single = declared_header_schema((rule,))
        both = declared_header_schema((rule, another))
        self.assertEqual(single.shape, both.shape)
        self.assertEqual(2, len(both.asset()["header_columns"][0]["rules"]))

    def test_header_selector_without_a_literal_header_path_does_not_become_a_column(
        self,
    ) -> None:
        selector = atom(
            "CA-R-2464",
            form="Declaration",
            body="""## Claim

### Formal Claim

```python
subject_path(address="Atom/(.Header.Role: Operations)/Workflow")
```
""",
        )
        self.assertEqual((), compile_header_rules([selector]))

    def _assert_initial_header_schema(self, schema, row):
        self.assertIn("header.identity.atom_id", schema.names)
        self.assertIn("header.context.role", schema.names)
        self.assertIn("header.state.updated_at", schema.names)
        self.assertNotIn("header.context.label", schema.names)
        self.assertNotIn("header.unknown_residue", schema.names)
        self.assertEqual(
            "Requirement",
            next(
                schema.value(row, column)
                for column in schema.columns
                if column.name == "header.context.role"
            ),
        )
