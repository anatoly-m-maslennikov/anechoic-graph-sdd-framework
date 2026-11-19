---
atom_id: CA-R-2515
ref_id: CA-R-2515
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Delivery)
tier: 3
status: active
version: 7
updated_at: '2026-11-12T12:33:04.158402+00:00'
carrier_destination:
  file:
    name: CA-R-2515-CORE_META_MODEL-DECLARATION--declare-atom-role-delivery.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2515-CORE_META_MODEL-DECLARATION--declare-atom-role-delivery.md
  source_atom_id: CA-R-2515
  source_atom_revision: 7
  source_sha256: 18e30e4e99135d69bbb71716625a4ff2090cb6a0591d8e6bf7f6a811cc3b2d99
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---

## Summary

Declare Atom/(.Role := Delivery)

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Atom

class Delivery(Atom):
    pass

declare_entity(
    entity_class=Delivery,
    entity_name='Delivery',
    qualification_property_path='Atom.Header.Context.Role',
    classifications={'Role Order Number': 7},
)
```

## Semantics

A Delivery specifies how results are represented, packaged, stored and made available through their Carriers at their intended destinations.
