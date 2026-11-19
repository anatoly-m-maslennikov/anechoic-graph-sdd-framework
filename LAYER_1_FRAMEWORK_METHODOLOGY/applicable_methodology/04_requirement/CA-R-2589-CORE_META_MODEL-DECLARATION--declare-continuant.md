---
atom_id: CA-R-2589
ref_id: CA-R-2589
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: ANECHOIC_MODEL <+ Node/Continuant
tier: 3
status: active
version: 4
updated_at: '2026-11-12T17:40:07+00:00'
carrier_destination:
  file:
    name: CA-R-2589-CORE_META_MODEL-DECLARATION--declare-continuant.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2589-CORE_META_MODEL-DECLARATION--declare-continuant.md
  source_atom_id: CA-R-2589
  source_atom_revision: 4
  source_sha256: 74dbb0a4f0cbd6616deb09a7ccdbf10d708f5c7e27ab9ef27154a262f605b672
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---

## Summary

Declare Continuant

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Node

class Continuant(Node):
    pass

declare_entity(entity_class=Continuant, entity_name='Continuant')
```

## Semantics

A Continuant persists as an identifiable thing.
