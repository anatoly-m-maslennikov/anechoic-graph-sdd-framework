---
identity:
  atom_id: CA-R-3114
  ref_id: CA-R-3114
context:
  role: requirement
  form: declaration
  container:
    scope_unit: CA-SU-11
  topics:
    main_subject: ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Delivery)/(.Header.Context.Form
      := Solution)
  tier: 3
relations:
  is_replacement_for:
  - CA-R-3002
state:
  version: 1
  status: active
  updated_at: '2026-11-12T20:07:37.995608+00:00'
destination:
  file:
    name: CA-R-3114-CORE_META_MODEL-DECLARATION--declare-delivery-solution-form.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-3114-CORE_META_MODEL-DECLARATION--declare-delivery-solution-form.md
  source_atom_id: CA-R-3114
  source_atom_revision: 1
  source_sha256: 76869156613f6347fc4f043e00d795e5799b321577b4c65cbef7d2f8ac0dd5be
  original_relations_sha256: c3f65131a1877f9018993b3df7fa417a88da6def2921c99fedb5a962c4deddcd
---

## Summary

Declare Delivery Solution Form

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Delivery

class DeliverySolution(Delivery):
    pass

declare_entity(
    entity_class=DeliverySolution,
    entity_name='Solution',
    qualification_property_path='Atom.Header.Context.Form',
)
```

## Semantics

A Solution specifies the contribution that realizes a Scope Unit’s responsibility across the unit and its descendants. Its Role identifies the contribution.
