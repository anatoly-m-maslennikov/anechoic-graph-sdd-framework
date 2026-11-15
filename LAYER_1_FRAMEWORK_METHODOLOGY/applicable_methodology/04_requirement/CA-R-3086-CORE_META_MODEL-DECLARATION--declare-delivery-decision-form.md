---
identity:
  atom_id: CA-R-3086
  ref_id: CA-R-3086
context:
  role: requirement
  form: declaration
  container:
    scope_unit: CA-SU-11
  tier: 3
  topics:
    main_subject: CAPRMEDIO_MODEL <+ Atom/(.Header.Context.Role := Delivery)/(.Header.Context.Form
      := Decision)
state:
  version: 1
  status: active
  updated_at: '2026-11-12T12:33:04.158402+00:00'
destination:
  file:
    name: CA-R-3086-CORE_META_MODEL-DECLARATION--declare-delivery-decision-form.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
relations:
  IS_REPLACEMENT_FOR:
  - CA-R-3005
projection:
  source_carrier_path: ../../../.caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-3086-CORE_META_MODEL-DECLARATION--declare-delivery-decision-form.md
  source_atom_id: CA-R-3086
  source_atom_revision: 1
  source_sha256: de12d98513286ef2247bea4c77cc4481720ef2ae4093ff593a3d25c2242a99aa
  original_relations_sha256: 5eb0e6a71cbedc1e8fde306ed59bb834f74835dad854742925b8b3d247b4c419
---

## Summary

Declare Delivery Decision Form

## Claim

### Formal Claim

```python
from caprmedio.formal_claims import declare_entity
from caprmedio.model import Delivery

class DeliveryDecision(Delivery):
    pass

declare_entity(
    entity_class=DeliveryDecision,
    entity_name='Decision',
    qualification_property_path='Atom.Header.Context.Form',
)
```

## Semantics

A Decision records a particular local choice. Applicable governing constraints continue to apply.
