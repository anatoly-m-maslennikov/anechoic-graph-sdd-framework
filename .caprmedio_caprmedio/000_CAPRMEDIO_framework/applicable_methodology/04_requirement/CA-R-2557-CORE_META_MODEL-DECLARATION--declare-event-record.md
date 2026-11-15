---
atom_id: CA-R-2557
ref_id: CA-R-2557
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: CAPRMEDIO_MODEL <+ Event Record
tier: 3
status: active
version: 5
updated_at: 2026-11-05 13:47:13 +0400
carrier_destination:
  file:
    name: CA-R-2557-CORE_META_MODEL-DECLARATION--declare-event-record.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
projection:
  source_carrier_path: ../../../.caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2557-CORE_META_MODEL-DECLARATION--declare-event-record.md
  source_atom_id: CA-R-2557
  source_atom_revision: 5
  source_sha256: 820f2d734c4c7f26fcd3b386e84cc2f19e7e641b8ed8729c9ffe02e24a24b79c
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Declare Event Record

## Claim

### Prose Claim


An Event Record is immutable.


### Formal Claim

```python
from caprmedio.formal_claims import declare_entity
from caprmedio.model import Continuant

class EventRecord(Continuant):
    pass

declare_entity(
    entity_class=EventRecord,
    entity_name="Event Record",
    model_relation_constraints={"IS_PROPERTY_OF": {"targets_per_source": 0}},
    instance_relation_constraints={
        "IS_CONTAINED_BY": {"target_entity_paths": ("Journal",), "targets_per_source": 1},
        "RECORDS": {"target_entity_paths": ("Event",), "targets_per_source": 1},
    },
)
```

## Semantics

An Event Record is a persistent description of an event and its recorded evidence.
