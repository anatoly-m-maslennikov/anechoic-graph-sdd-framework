---
atom_id: CA-R-2755
ref_id: CA-R-2755
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: ANECHOIC_MODEL <+ Event
tier: 3
status: active
version: 1
updated_at: 2026-11-05 01:38:59 +0400
carrier_destination:
  file:
    name: CA-R-2755-CORE_META_MODEL-DECLARATION--declare-event.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2755-CORE_META_MODEL-DECLARATION--declare-event.md
  source_atom_id: CA-R-2755
  source_atom_revision: 1
  source_sha256: aaba484cdc9e14d98817510df1505cffccaec143bbdd3f3e464503b4cfbcadb9
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Declare Event

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity, Cardinality
from anechoic.model import Occurrent

class Event(Occurrent):
    pass

declare_entity(
    entity_class=Event,
    entity_name='Event',
    instance_relation_constraints={
        'IS_RECORDED_BY': {"target_entity_paths": ('Event Record',), "targets_per_source": Cardinality(minimum=0, maximum=None)},
        'IS_PRODUCED_BY': {"target_entity_paths": ('Execution',), "targets_per_source": Cardinality(minimum=1, maximum=None)},
    },
)
```

## Semantics

An Event is an occurrence produced by an Execution.
