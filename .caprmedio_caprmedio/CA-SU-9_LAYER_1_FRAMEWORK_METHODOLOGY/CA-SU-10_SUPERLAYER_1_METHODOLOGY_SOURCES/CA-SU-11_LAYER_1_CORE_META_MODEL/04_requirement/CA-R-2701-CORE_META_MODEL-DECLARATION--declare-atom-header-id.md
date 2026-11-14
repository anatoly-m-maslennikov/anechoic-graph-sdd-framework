---
atom_id: CA-R-2701
ref_id: CA-R-2701
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: CAPRMEDIO_MODEL <+ Atom.Header.Identity.ID
tier: 3
status: active
version: 3
updated_at: '2026-11-13T22:53:30.315950+00:00'
carrier_destination:
  file:
    name: CA-R-2701-CORE_META_MODEL-DECLARATION--declare-atom-header-id.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
---
## Summary

Declare Atom.Header.ID

## Claim

### Prose Claim

The ID is immutable when the Atom Status belongs to Current, Backlog, or Archived Status Group.

### Formal Claim

```python
from caprmedio.formal_claims import declare_entity

declare_entity(
    entity_name='ID',
    relation_name="IS_PROPERTY_OF",
    base_path='Atom.Header.Identity',
    property_occurrence_cardinality=1, value_format=str, value_cardinality=1, dependent_property_cardinality=0,
)
```

