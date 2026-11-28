"""Both Workbench schema modes and their deterministic generated asset."""

from __future__ import annotations

import json
from pathlib import Path
import unittest

from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import (  # noqa: E402
    compile_header_rules,
)
from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import WorkbenchUnavailableError  # noqa: E402
from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import (  # noqa: E402
    declared_header_schema,
)
from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import QueryStore  # noqa: E402
from IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IWE_CONSOLE_BACKEND.FEATURE_IWE_CONSOLE_BACKEND__shared import (
    SourceReader,
)  # noqa: E402
from IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IWE_CONSOLE_BACKEND.FEATURE_IWE_CONSOLE_BACKEND__tests.sources._source_reader_fixture import (
    SourceReaderFixture,
)  # noqa: E402
from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared import (
    extension_directory,
)  # noqa: E402

from IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IWE_CONSOLE_BACKEND.FEATURE_IWE_CONSOLE_BACKEND__tests.schema.workbench_schema_fixture import (
    WorkbenchSchemaFixture,
    atom,
)


from .workbench_schema_small_cases import WorkbenchSchemaSmallCases


APP_ROOT = Path(__file__).resolve().parents[5]


class WorkbenchSchemaAssetTests(
    WorkbenchSchemaSmallCases, WorkbenchSchemaFixture, SourceReaderFixture
):
    def test_mode_one_uses_canonical_adapter_paths_and_alias_reads_only(
        self,
    ) -> None:
        declaration = atom(
            "CA-R-DECL",
            form="Declaration",
            body="""## Claim

### Formal Claim

```python
property_rule(address="Atom.Header.ID", value_format="atom id", values="1")
property_rule(address="Atom.Header.Context.Role", value_format="string", values="1")
property_rule(address="Atom.Header.Status", value_format="string", values="1")
property_rule(address="Atom.Header.Updated At", value_format="datetime", values="1")
```
""",
        )
        row = atom(
            header={
                "atom_id": "CA-R-1",
                "content_role": "Requirement",
                "type": "Definition",
                "status": "Active",
                "label": "known adapter field",
                "version": 1,
                "updated_at": "2026-11-09 00:00:00 +0000",
                "unknown residue": "not a model column",
            }
        )
        rules = compile_header_rules([declaration])
        schema = declared_header_schema(rules)

        self._assert_initial_header_schema(schema, row)

        store = QueryStore(
            extension_directory=extension_directory(APP_ROOT.parents[1]),
            database_path=self.database,
            schema_mode=1,
        )
        self.addCleanup(store.close)
        store.replace([row], [], header_schema=schema)
        self.assertEqual(
            [["CA-R-1", "Requirement", "Active"]],
            store.run(
                'SELECT "header.identity.atom_id", "header.context.role", "header.state.status" FROM atoms'
            )["rows"],
        )

        self._assert_declared_schema_changes(row, store, schema, rules)

    def _assert_declared_schema_changes(self, row, store, schema, rules):
        changed = atom(
            header={**row["header_json"], "unknown residue": "changed"},
            version=2,
        )
        self.assertFalse(
            store.apply(
                [changed], [], relation_types=set(), header_schema=schema
            )
        )
        self.assertFalse(store.schema_changed)

        declared_change = declared_header_schema(
            (
                *rules,
                *compile_header_rules(
                    [
                        atom(
                            "CA-R-DECL-2",
                            form="Declaration",
                            body="""## Claim

### Formal Claim

```python
property_rule(address="Atom.Header.Declared Later", value_format="string", values="1")
```
""",
                        )
                    ]
                ),
            )
        )
        self.assertTrue(
            store.apply(
                [changed],
                [],
                relation_types=set(),
                header_schema=declared_change,
            )
        )
        self.assertTrue(store.schema_changed)

    def _assert_header_declaration_collision(self):
        conflicting = [
            atom(
                "CA-R-INT",
                form="Declaration",
                body="""## Claim

### Formal Claim

```python
property_rule(address="Atom.Header.Version", value_format="int", values="1")
```
""",
            ),
            atom(
                "CA-R-TEXT",
                form="Declaration",
                body="""## Claim

### Formal Claim

```python
property_rule(address="Atom.Header.Version", value_format="string", values="1")
```
""",
            ),
        ]
        with self.assertRaisesRegex(ValueError, "declaration collision"):
            declared_header_schema(compile_header_rules(conflicting))

    def test_mode_one_rejects_conflicting_aliases(self) -> None:
        schema = declared_header_schema(
            compile_header_rules(
                [
                    atom(
                        "CA-R-DECL",
                        form="Declaration",
                        body="""## Claim

### Formal Claim

```python
property_rule(address="Atom.Header.Context.Role", value_format="string", values="1")
```
""",
                    )
                ]
            )
        )
        with self.assertRaisesRegex(ValueError, "Conflicting Header aliases"):
            schema.value(
                atom(header={"role": "Requirement", "content_role": "Method"}),
                schema.columns[0],
            )
        self._assert_header_declaration_collision()

    def _assert_header_type_change(
        self, reader, path, original, change, initial_shape
    ):
        path.write_text(
            original.replace("version: 1", "version: 3").replace(
                "value_format=int", "value_format=str"
            )
        )
        reader.capture(change)
        self.assertIsNone(reader.capture_delta)
        self.assertEqual("VARCHAR", reader.header_schema.columns[0].format)
        self.assertNotEqual(initial_shape, reader.header_schema.shape)

    def test_mode_one_declaration_changes_are_the_schema_boundary(
        self,
    ) -> None:
        SourceReaderFixture.setUp(self)
        reader = SourceReader(self.root, schema_mode=1)
        path = self._write_atom(
            "MAIN",
            "04_requirement",
            "CA-R-3-header.md",
            atom_id="CA-R-3",
            form="Declaration",
            body="""## Claim

### Formal Claim

```python
from anechoic.formal_claims import Cardinality, declare_entity
declare_entity(entity_name="Example", relation_name="IS_PROPERTY_OF", base_path="Atom.Header",
               value_format=int, value_cardinality=Cardinality(minimum=0, maximum=1))
```
""",
        )
        reader.capture()
        self.assertEqual("BIGINT", reader.header_schema.columns[0].format)
        initial_shape = reader.header_schema.shape
        change = [
            {
                "operation": "update",
                "new_path": path.relative_to(self.root).as_posix(),
            }
        ]
        original = path.read_text()
        path.write_text(original.replace("version: 1", "version: 2"))
        reader.capture(change)
        self.assertIsNotNone(reader.capture_delta)
        self.assertEqual(initial_shape, reader.header_schema.shape)
        self.assertEqual(
            2, reader.header_schema.columns[0].rules[0].source.version
        )
        self._assert_header_type_change(
            reader, path, original, change, initial_shape
        )

    def test_mode_one_same_shape_declaration_provenance_writes_after_commit(
        self,
    ) -> None:
        declaration = atom(
            "CA-R-DECL",
            form="Declaration",
            body="""## Claim

### Formal Claim

~~~python
from anechoic.formal_claims import declare_entity
declare_entity(entity_name="Tier", relation_name="IS_PROPERTY_OF", base_path="Atom.Header",
               value_format=int, value_cardinality=1)
~~~
""",
        )
        header = declared_header_schema(compile_header_rules([declaration]))
        row = atom(header={"tier": 1})
        store = QueryStore(
            extension_directory=extension_directory(APP_ROOT.parents[1]),
            database_path=self.database,
            schema_mode=1,
        )
        self.addCleanup(store.close)
        store.replace([row], [], header_schema=header)
        changed = declared_header_schema(
            compile_header_rules([dict(declaration, version=2)])
        )
        self.assertFalse(
            store.apply(
                [dict(row, version=2)],
                [],
                relation_types=set(),
                header_schema=changed,
            )
        )
        payload = json.loads(
            (self.database.parent / "projection-schema.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(
            2, payload["header_columns"][0]["rules"][0]["source"]["version"]
        )

    def test_mode_one_rejects_legacy_type_and_naive_timestamp_without_coercion(
        self,
    ) -> None:
        declaration = atom(
            "CA-R-DECL",
            form="Declaration",
            body="""## Claim

### Formal Claim

```python
property_rule(address="Atom.Header.Tier", value_format="int", values="1")
property_rule(address="Atom.Header.Updated At", value_format="datetime", values="1")
```
""",
        )
        schema = declared_header_schema(compile_header_rules([declaration]))
        naive = atom(header={"updated_at": "2026-11-09 00:00:00"})
        updated_at = next(
            column
            for column in schema.columns
            if column.reader == "updated_at"
        )
        with self.assertRaisesRegex(ValueError, "offset-bearing"):
            schema.value(naive, updated_at)
        store = QueryStore(
            extension_directory=extension_directory(APP_ROOT.parents[1]),
            database_path=self.database,
            schema_mode=1,
        )
        self.addCleanup(store.close)
        with self.assertRaises(WorkbenchUnavailableError):
            store.replace(
                [atom(header={"tier": "principle"})], [], header_schema=schema
            )


if __name__ == "__main__":
    unittest.main()
