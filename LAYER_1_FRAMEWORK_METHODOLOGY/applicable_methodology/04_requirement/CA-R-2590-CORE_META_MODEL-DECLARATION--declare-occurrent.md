---
atom_id: CA-R-2590
ref_id: CA-R-2590
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: ANECHOIC_MODEL <+ Node/Occurrent
tier: 3
status: active
version: 4
updated_at: '2026-11-12T17:40:07+00:00'
carrier_destination:
  file:
    name: CA-R-2590-CORE_META_MODEL-DECLARATION--declare-occurrent.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2590-CORE_META_MODEL-DECLARATION--declare-occurrent.md
  source_atom_id: CA-R-2590
  source_atom_revision: 4
  source_sha256: 24d0ee409263c9c92c2a8f365ec97845f68ed79e686e03c310cc5023b2fa5fb1
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---

## Summary

Declare Occurrent

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Node

class Occurrent(Node):
    pass

declare_entity(entity_class=Occurrent, entity_name='Occurrent')
```

## Semantics

An Occurrent is an actual occurrence unfolding in time. A record describes an occurrence; it is distinct from the occurrence itself.
