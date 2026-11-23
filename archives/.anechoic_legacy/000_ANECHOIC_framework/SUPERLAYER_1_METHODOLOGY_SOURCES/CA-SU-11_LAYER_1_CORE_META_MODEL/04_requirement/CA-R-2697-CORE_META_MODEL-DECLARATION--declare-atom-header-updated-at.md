---
atom_id: CA-R-2697
ref_id: CA-R-2697
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: ANECHOIC_MODEL <+ Atom.Header.State.Updated At
tier: 3
status: active
version: 2
updated_at: '2026-11-13T22:53:30.315950+00:00'
carrier_destination:
  file:
    name: CA-R-2697-CORE_META_MODEL-DECLARATION--declare-atom-header-updated-at.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
---
## Summary

Declare Atom.Header.Updated At

## Claim

### Prose Claim

The Updated At value equals the maximum happened_at among Event Records whose single object_output has a version, has this Atom ID and current Version, and has action create or update.

### Formal Claim

```python
from datetime import datetime
from anechoic.formal_claims import declare_entity

declare_entity(
    entity_name='Updated At',
    relation_name="IS_PROPERTY_OF",
    base_path='Atom.Header.State',
    property_occurrence_cardinality=1, value_format=datetime, value_cardinality=1, dependent_property_cardinality=0,
)
```

