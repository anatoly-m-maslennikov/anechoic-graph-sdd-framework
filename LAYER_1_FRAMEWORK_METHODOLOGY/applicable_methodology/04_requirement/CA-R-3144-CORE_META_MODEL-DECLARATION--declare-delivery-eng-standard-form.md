---
identity:
  atom_id: CA-R-3144
  ref_id: CA-R-3144
context:
  role: requirement
  form: declaration
  container:
    scope_unit: CA-SU-11
  tier: 3
  topics:
    main_subject: CAPRMEDIO_MODEL <+ Atom/(.Header.Context.Role := Delivery)/(.Header.Context.Form
      := Eng Standard)
relations:
  IS_REPLACEMENT_FOR:
  - CA-R-3119
state:
  version: 1
  status: active
  updated_at: '2026-11-13T15:40:01.174594+00:00'
destination:
  file:
    name: CA-R-3144-CORE_META_MODEL-DECLARATION--declare-delivery-eng-standard-form.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
projection:
  source_carrier_path: ../../../.caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-3144-CORE_META_MODEL-DECLARATION--declare-delivery-eng-standard-form.md
  source_atom_id: CA-R-3144
  source_atom_revision: 1
  source_sha256: 5963fede3f5a69a301996b8bd78d76fdaca8670f5231fdf9500def04a526403b
  original_relations_sha256: 8ab87e7061e83bc9fc3e7b2a2129844bf470311ca89cd72a6afa4b18c370dccd
---
## Summary

Declare Delivery Eng Standard Form

## Claim

### Formal Claim

```python
from caprmedio.formal_claims import declare_entity
from caprmedio.model import Delivery

class DeliveryEngStandard(Delivery):
    pass

declare_entity(
    entity_class=DeliveryEngStandard,
    entity_name='Eng Standard',
    qualification_property_path='Atom.Header.Context.Form',
)
```

## Semantics

An Eng Standard applies directly to implementation within its owning Scope Unit and descendant Scope Units where its Claim applies.