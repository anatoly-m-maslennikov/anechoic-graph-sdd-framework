"""Both Workbench schema modes and their deterministic generated asset."""

from __future__ import annotations

import json
from pathlib import Path
import unittest


APP_ROOT = Path(__file__).resolve().parents[3]

from KERNEL_MIXER_C59.content_schema import (DeclarationSource)  # noqa: E402
from KERNEL_MIXER_C59.declared_header_rules import HeaderRule, compile_header_rules  # noqa: E402
from KERNEL_MIXER_C59.errors import WorkbenchUnavailableError  # noqa: E402
from KERNEL_MIXER_C59.header_columns import (  # noqa: E402
    declared_header_schema,
)
from KERNEL_MIXER_C59.query_store import QueryStore  # noqa: E402
from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.source_header_schema import SourceHeaderSchema  # noqa: E402
from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.FEATURE_PROJECT_TOOLS__tests.smalltest_support__pub import extension_directory  # noqa: E402


from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.FEATURE_WORKBENCH_BACKEND__tests.workbench_schema_fixture import WorkbenchSchemaFixture, atom


class WorkbenchSchemaAssetTests(WorkbenchSchemaFixture):
    def test_mode_one_uses_canonical_adapter_paths_and_alias_reads_only(self) -> None:
        declaration = atom(
            "CA-R-DECL", form="Declaration", body="""## Claim

### Formal Claim

```CFEL
Atom.Header.ID:: [atom id]{::1};
Atom.Header.Context.Role:: [string]{::1};
Atom.Header.Status:: [string]{::1};
Atom.Header.Updated At:: [datetime]{::1};
```
""",
        )
        row = atom(header={
            "atom_id": "CA-R-1", "content_role": "Requirement", "type": "Definition",
            "status": "Active", "label": "known adapter field", "version": 1,
            "updated_at": "2026-11-09 00:00:00 +0000",
            "unknown residue": "not a model column",
        })
        rules = compile_header_rules([declaration])
        schema = declared_header_schema(rules)

        self.assertIn("header.identity.atom_id", schema.names)
        self.assertIn("header.context.role", schema.names)
        self.assertIn("header.state.updated_at", schema.names)
        self.assertNotIn("header.context.label", schema.names)
        self.assertNotIn("header.unknown_residue", schema.names)
        self.assertEqual("Requirement", next(
            schema.value(row, column)
            for column in schema.columns if column.name == "header.context.role"
        ))

        store = QueryStore(
            extension_directory=extension_directory(APP_ROOT.parents[1]), database_path=self.database,
            schema_mode=1,
        )
        self.addCleanup(store.close)
        store.replace([row], [], header_schema=schema)
        self.assertEqual([["CA-R-1", "Requirement", "Active"]], store.run(
            'SELECT "header.identity.atom_id", "header.context.role", "header.state.status" FROM atoms'
        )["rows"])

        self._assert_declared_schema_changes(row, store, schema, rules)

    def _assert_declared_schema_changes(self, row, store, schema, rules):
        changed = atom(header={**row["header_json"], "unknown residue": "changed"}, version=2)
        self.assertFalse(store.apply([changed], [], relation_types=set(), header_schema=schema))
        self.assertFalse(store.schema_changed)

        declared_change = declared_header_schema((*rules, *compile_header_rules([atom(
            "CA-R-DECL-2", form="Declaration", body="""## Claim

### Formal Claim

```CFEL
Atom.Header.Declared Later:: [string]{::1};
```
""",
        )])))
        self.assertTrue(store.apply([changed], [], relation_types=set(), header_schema=declared_change))
        self.assertTrue(store.schema_changed)


    def test_mode_one_rejects_conflicting_aliases(self) -> None:
        schema = declared_header_schema(compile_header_rules([atom(
            "CA-R-DECL", form="Declaration", body="""## Claim

### Formal Claim

```CFEL
Atom.Header.Context.Role:: [string]{::1};
```
""",
        )]))
        with self.assertRaisesRegex(ValueError, "Conflicting Header aliases"):
            schema.value(atom(header={"role": "Requirement", "content_role": "Method"}), schema.columns[0])
        conflicting = [
            atom("CA-R-INT", form="Declaration", body="""## Claim

### Formal Claim

```CFEL
Atom.Header.Version:: [int]{::1};
```
"""),
            atom("CA-R-TEXT", form="Declaration", body="""## Claim

### Formal Claim

```CFEL
Atom.Header.Version:: [string]{::1};
```
"""),
        ]
        with self.assertRaisesRegex(ValueError, "declaration collision"):
            declared_header_schema(compile_header_rules(conflicting))


    def test_mode_one_declaration_changes_are_the_schema_boundary(self) -> None:
        original = atom("CA-R-DECL", form="Declaration", body="""## Claim

### Formal Claim

```CFEL
Atom.Header.Version:: [int]{::1};
```
""")
        state = SourceHeaderSchema()
        state.rebuild([original])
        assert state.schema is not None
        original_schema = state.schema
        same_shape = dict(original, version=2)
        self.assertFalse(state.update({same_shape["source_path"]: same_shape}))
        assert state.schema is not None
        self.assertEqual(2, state.schema.columns[0].rules[0].source.version)
        changed_body = """## Claim

### Formal Claim

```CFEL
Atom.Header.Version:: [string]{::1};
```
"""
        type_changed = dict(
            same_shape, version=3, content_markdown=changed_body, _content_bytes=changed_body.encode("utf-8"),
        )
        self.assertTrue(state.update({type_changed["source_path"]: type_changed}))
        self.assertEqual(original_schema.shape, state.schema.shape)


    def test_equal_header_validation_shapes_ignore_distinct_provenance(self) -> None:
        occurrence = DeclarationSource("CA-R-PROPERTY", 1, "property.md")
        first = DeclarationSource("CA-R-PARENT-1", 1, "parent-1.md")
        second = DeclarationSource("CA-R-PARENT-2", 1, "parent-2.md")
        rule = HeaderRule(("context", "label"), "VARCHAR", frozenset({"Operations"}),
                          frozenset({"Workflow"}), occurrence, provenance=(first,))
        another = HeaderRule(("context", "label"), "VARCHAR", frozenset({"Operations"}),
                             frozenset({"Workflow"}), occurrence, provenance=(second,))
        single = declared_header_schema((rule,))
        both = declared_header_schema((rule, another))
        self.assertEqual(single.shape, both.shape)
        self.assertEqual(2, len(both.asset()["header_columns"][0]["rules"]))


    def test_mode_one_same_shape_declaration_provenance_writes_after_commit(self) -> None:
        declaration = atom("CA-R-DECL", form="Declaration", body="""## Claim

### Formal Claim

~~~CFEL
Atom.Header.Tier:: [int]{::1};
~~~
""")
        header = declared_header_schema(compile_header_rules([declaration]))
        row = atom(header={"tier": 1})
        store = QueryStore(
            extension_directory=extension_directory(APP_ROOT.parents[1]), database_path=self.database,
            schema_mode=1,
        )
        self.addCleanup(store.close)
        store.replace([row], [], header_schema=header)
        changed = declared_header_schema(compile_header_rules([dict(declaration, version=2)]))
        self.assertFalse(store.apply(
            [dict(row, version=2)], [], relation_types=set(), header_schema=changed,
        ))
        payload = json.loads((self.database.parent / "projection-schema.json").read_text(encoding="utf-8"))
        self.assertEqual(2, payload["header_columns"][0]["rules"][0]["source"]["version"])


    def test_header_selector_without_a_literal_header_path_does_not_become_a_column(self) -> None:
        selector = atom("CA-R-2464", form="Declaration", body="""## Claim

### Formal Claim

```CFEL
Atom/(.Header.Role: Operations)/Workflow;
```
""")
        self.assertEqual((), compile_header_rules([selector]))


    def test_mode_one_rejects_legacy_type_and_naive_timestamp_without_coercion(self) -> None:
        declaration = atom("CA-R-DECL", form="Declaration", body="""## Claim

### Formal Claim

```CFEL
Atom.Header.Tier:: [int]{::1};
Atom.Header.Updated At:: [datetime]{::1};
```
""")
        schema = declared_header_schema(compile_header_rules([declaration]))
        naive = atom(header={"updated_at": "2026-11-09 00:00:00"})
        updated_at = next(column for column in schema.columns if column.reader == "updated_at")
        with self.assertRaisesRegex(ValueError, "offset-bearing"):
            schema.value(naive, updated_at)
        store = QueryStore(
            extension_directory=extension_directory(APP_ROOT.parents[1]), database_path=self.database,
            schema_mode=1,
        )
        self.addCleanup(store.close)
        with self.assertRaises(WorkbenchUnavailableError):
            store.replace([atom(header={"tier": "principle"})], [], header_schema=schema)

if __name__ == "__main__":
    unittest.main()
