"""Source discovery asset test cases."""

import json

from ...schema.content_schema_fixture import SUMMARY_CLAIM, python_claim_body
from ...schema.workbench_schema_fixture import generate_asset


class SourceDiscoveryAssetCases:
    def test_image_compilers_use_formal_declarations_outside_scope_inventory(
        self,
    ):
        declaration = self.source(
            "native-model/content.md",
            "CA-R-795",
            body=python_claim_body(SUMMARY_CLAIM),
        )
        relation = self.source(
            "native-model/relation.md",
            "CA-R-796",
            form="Relation Declaration",
            body="""## Claim

### Formal Claim

```python
relation(source="Relation//DIRECT", name="HAS_INVERSE", target="Relation//INVERSE")
```
""",
        )
        relation.write_text(
            relation.read_text().replace(
                "subjects: {}", "subjects:\n  active: CFEL <+ Relation//DIRECT"
            )
        )
        inverse = self.source(
            "native-model/inverse.md",
            "CA-R-797",
            form="Relation Declaration",
            body="""## Claim

### Formal Claim

```python
relation(source="Relation//INVERSE", name="HAS_INVERSE", target="Relation//DIRECT", reverse=True)
```
""",
        )
        inverse.write_text(
            inverse.read_text().replace(
                "subjects: {}",
                "subjects:\n  active: CFEL <+ Relation//INVERSE",
            )
        )
        self._assert_native_assets(declaration)

    def _assert_native_assets(self, declaration):
        schema_data = generate_asset(self.root, "generate_workbench_schema.py")
        self.assertEqual(
            schema_data,
            generate_asset(self.root, "generate_workbench_schema.py"),
        )
        schema = json.loads(schema_data)
        columns = schema["modes"]["2"]["content"]["content_columns"]
        self.assertEqual(
            ["content.summary"], [column["name"] for column in columns]
        )
        self.assertIn(
            declaration.relative_to(self.root).as_posix(),
            {item["path"] for item in schema["sources"]},
        )
        registry_data = generate_asset(
            self.root, "generate_relation_registry.py"
        )
        self.assertEqual(
            registry_data,
            generate_asset(self.root, "generate_relation_registry.py"),
        )
        registry = json.loads(registry_data)
        self.assertEqual(["DIRECT", "INVERSE"], registry["registered_names"])
        self.assertEqual(
            [{"direct": "DIRECT", "inverse": "INVERSE"}],
            registry["inverse_bindings"],
        )
        self.assertEqual(
            {"CA-R-796", "CA-R-797"},
            {item["atom_id"] for item in registry["sources"]},
        )

    def test_installed_model_feeds_asset_compilers_but_not_public_capture(
        self,
    ):
        installed = "000_ANECHOIC_framework/SUPERLAYER_1_METHODOLOGY_SOURCES/04_requirement"
        declaration = self.source(
            f"{installed}/content.md",
            "CA-R-795",
            body=python_claim_body(SUMMARY_CLAIM),
        )
        relation = self.source(
            f"{installed}/relation.md",
            "CA-R-796",
            form="Relation Declaration",
            body="""## Claim

### Formal Claim

```python
relation(source="Relation//DIRECT", name="HAS_INVERSE", target="Relation//INVERSE")
```
""",
        )
        relation.write_text(
            relation.read_text().replace(
                "subjects: {}", "subjects:\n  active: CFEL <+ Relation//DIRECT"
            )
        )
        projected = self.source(
            "_projection/relation.md",
            "CA-R-797",
            form="Relation Declaration",
            body="""## Claim

### Formal Claim

```python
relation(source="Relation//PROJECTED", name="HAS_INVERSE", target="Relation//COPY")
```
""",
        )
        projected.write_text(
            projected.read_text().replace(
                "subjects: {}",
                "subjects:\n  active: CFEL <+ Relation//PROJECTED",
            )
        )

        self._assert_installed_assets(declaration)

    def _assert_installed_assets(self, declaration):
        atoms, _, _ = self.fixture._capture()
        self.assertFalse(
            {"CA-R-795", "CA-R-796", "CA-R-797"} & {row["id"] for row in atoms}
        )

        schema = json.loads(
            generate_asset(self.root, "generate_workbench_schema.py")
        )
        columns = schema["modes"]["2"]["content"]["content_columns"]
        self.assertEqual(
            ["content.summary"], [column["name"] for column in columns]
        )
        self.assertIn(
            declaration.relative_to(self.root).as_posix(),
            {item["path"] for item in schema["sources"]},
        )
        registry = json.loads(
            generate_asset(self.root, "generate_relation_registry.py")
        )
        self.assertEqual(["DIRECT", "INVERSE"], registry["registered_names"])
        self.assertEqual(
            {"CA-R-796"}, {item["atom_id"] for item in registry["sources"]}
        )

    def test_registry_prefers_current_declared_scope_source_over_earlier_copy(
        self,
    ):
        copied = self.source(
            "000_copy/record.md",
            "CA-R-810",
            form="Relation Declaration",
            body="""## Claim

### Formal Claim

```python
subject_path(address="Relation//STALE")
```
""",
        )
        native = self.fixture._write_atom(
            "MAIN",
            "04_requirement",
            "native.md",
            atom_id="CA-R-810",
            version=2,
            form="Relation Declaration",
            body="""## Claim

### Formal Claim

```python
subject_path(address="Relation//CURRENT")
```
""",
        )
        atoms, _, _ = self.fixture._capture()
        self.assertEqual(
            str(copied.relative_to(self.root)),
            next(
                row["source_path"] for row in atoms if row["id"] == "CA-R-810"
            ),
        )
        registry = json.loads(
            generate_asset(self.root, "generate_relation_registry.py")
        )
        self.assertIn("CURRENT", registry["registered_names"])
        self.assertNotIn("STALE", registry["registered_names"])
        self._assert_current_registry_pin(registry, native)

    def _assert_current_registry_pin(self, registry, native):
        pin = next(
            row for row in registry["sources"] if row["atom_id"] == "CA-R-810"
        )
        self.assertEqual(
            (2, native.relative_to(self.root).as_posix()),
            (pin["version"], pin["path"]),
        )

    def test_schema_prefers_current_declared_scope_source_over_earlier_copy(
        self,
    ):
        old = python_claim_body(
            SUMMARY_CLAIM.replace(".Summary", ".Old Field")
        )
        current = python_claim_body(
            SUMMARY_CLAIM.replace(".Summary", ".Current Field")
        )
        self.source("000_copy/record.md", "CA-R-809", body=old)
        native = self.fixture._write_atom(
            "MAIN",
            "04_requirement",
            "native.md",
            atom_id="CA-R-809",
            version=2,
            form="Declaration",
            body=current,
        )
        schema = json.loads(
            generate_asset(self.root, "generate_workbench_schema.py")
        )
        for mode in ("1", "2"):
            columns = schema["modes"][mode]["content"]["content_columns"]
            self.assertEqual(
                ["content.current_field"],
                [column["name"] for column in columns],
            )
        pins = {
            (row["version"], row["path"])
            for row in schema["sources"]
            if row["atom_id"] == "CA-R-809"
        }
        self.assertIn((2, native.relative_to(self.root).as_posix()), pins)

    def test_registry_skips_invalid_duplicate_scope_data(self):
        self.source("000_copy/record.md", "CA-R-811", form="Rule")
        self.fixture._write_atom(
            "MAIN",
            "04_requirement",
            "invalid.md",
            atom_id="CA-R-811",
            form="Rule",
            body="## Summary\n\nInvalid ordinary data.\n",
        )
        self.source(
            "loose/relation.md",
            "CA-R-812",
            form="Relation Declaration",
            body="""## Claim

### Formal Claim

```python
subject_path(address="Relation//VALID")
```
""",
        )
        registry = json.loads(
            generate_asset(self.root, "generate_relation_registry.py")
        )
        self.assertIn("VALID", registry["registered_names"])
