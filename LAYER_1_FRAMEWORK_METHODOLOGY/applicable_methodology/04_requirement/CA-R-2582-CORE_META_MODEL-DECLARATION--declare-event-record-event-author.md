---
atom_id: CA-R-2582
ref_id: CA-R-2582
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: ANECHOIC_MODEL <+ Event Record.Relations.HAS_EVENT_AUTHOR
tier: 3
status: active
version: 3
updated_at: '2026-11-13T22:53:30.315950+00:00'
carrier_destination:
  file:
    name: CA-R-2582-CORE_META_MODEL-DECLARATION--declare-event-record-event-author.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2582-CORE_META_MODEL-DECLARATION--declare-event-record-event-author.md
  source_atom_id: CA-R-2582
  source_atom_revision: 3
  source_sha256: 1665badf97cf4263c0a195b89823f0817c01f55f11ca26a094220bba8edbaf46
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Declare Event Record.Relations.HAS_EVENT_AUTHOR

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Actor

declare_entity(
    entity_name="HAS_EVENT_AUTHOR",
    relation_name="IS_PROPERTY_OF",
    base_path="Event Record.Relations",
    property_occurrence_cardinality=1,
    value_format=Actor,
    value_cardinality=1,
    dependent_property_cardinality=0,
)
```

