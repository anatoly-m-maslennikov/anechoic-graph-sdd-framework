---
atom_id: CA-R-2542
ref_id: CA-R-2542
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: ANECHOIC_MODEL <+ Actor
tier: 3
status: active
version: 3
updated_at: '2026-11-12T17:40:07+00:00'
carrier_destination:
  file:
    name: CA-R-2542-CORE_META_MODEL-DECLARATION--declare-actor.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2542-CORE_META_MODEL-DECLARATION--declare-actor.md
  source_atom_id: CA-R-2542
  source_atom_revision: 3
  source_sha256: a7028d4add5c8ffb09ab9f5af42ecbe3af37cb473e9b919a3e8c174d026a4249
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Declare Actor

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Continuant

class Actor(Continuant):
    pass

declare_entity(entity_class=Actor, entity_name='Actor')
```

## Semantics

An Actor participates in Project work.
