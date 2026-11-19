---
identity:
  atom_id: CA-R-3138
  ref_id: CA-R-3138
context:
  role: requirement
  form: declaration
  container:
    scope_unit: CA-SU-11
  tier: 3
  topics:
    main_subject: ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Requirement)/(.Header.Context.Form
      := Spec Policy)
relations:
  IS_REPLACEMENT_FOR:
  - CA-R-3121
state:
  version: 1
  status: active
  updated_at: '2026-11-13T15:39:16.008887+00:00'
destination:
  file:
    name: CA-R-3138-CORE_META_MODEL-DECLARATION--declare-requirement-spec-policy-form.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-3138-CORE_META_MODEL-DECLARATION--declare-requirement-spec-policy-form.md
  source_atom_id: CA-R-3138
  source_atom_revision: 1
  source_sha256: 8b5374daffea81eadbeaab5b4974f21b9475387b7e76b66cbf653dd4ec05b0fd
  original_relations_sha256: 034df0399be9e3322d7ee83ae5c0739a03b1fdc1244a52317f52dcafbf413500
---
## Summary

Declare Requirement Spec Policy Form

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Requirement

class RequirementSpecPolicy(Requirement):
    pass

declare_entity(
    entity_class=RequirementSpecPolicy,
    entity_name='Spec Policy',
    qualification_property_path='Atom.Header.Context.Form',
)
```

## Semantics

A Spec Policy governs how to write and review Atoms of the same Role whose main subject is its own main subject or a descendant.