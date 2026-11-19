---
atom_id: CA-R-2762
ref_id: CA-R-2762
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: ANECHOIC_MODEL <+ Relation//IS_BLOCKED_BY
tier: 1
status: active
version: 3
updated_at: 2026-11-05 18:23:39 +0400
carrier_destination:
  file:
    name: CA-R-2762-CORE_META_MODEL-DECLARATION--declare-is-blocked-by.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2762-CORE_META_MODEL-DECLARATION--declare-is-blocked-by.md
  source_atom_id: CA-R-2762
  source_atom_revision: 3
  source_sha256: 98386d47ede6e6b5650e64fae70ea12ec0bf294f6fa1e9644cc8b412424542c3
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---

## Summary

Declare IS_BLOCKED_BY

## Claim

### Prose Claim

A dependent Plan may start only after each Plan it is blocked by is Done. BLOCKS is the inverse alias: the prerequisite is written before the dependent.

### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name="IS_BLOCKED_BY",
    inverse_alias="BLOCKS",
    endpoint_pairs=(
        {"source_endpoint": {"level": "instances", "entity_paths": ("Atom/(.Header.Context.Role:=Plan)",)},
         "target_endpoint": {"level": "instances", "entity_paths": ("Atom/(.Header.Context.Role:=Plan)",)}},
    ),
)
```

## Semantics

IS_BLOCKED_BY relates a dependent Plan to a prerequisite Plan.
