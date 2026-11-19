---
identity:
  atom_id: CA-R-3139
  ref_id: CA-R-3139
context:
  role: requirement
  form: declaration
  container:
    scope_unit: CA-SU-11
  tier: 3
  topics:
    main_subject: ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Method)/(.Header.Context.Form
      := Spec Policy)
relations:
  IS_REPLACEMENT_FOR:
  - CA-R-3122
state:
  version: 1
  status: active
  updated_at: '2026-11-13T15:39:37.258710+00:00'
destination:
  file:
    name: CA-R-3139-CORE_META_MODEL-DECLARATION--declare-method-spec-policy-form.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-3139-CORE_META_MODEL-DECLARATION--declare-method-spec-policy-form.md
  source_atom_id: CA-R-3139
  source_atom_revision: 1
  source_sha256: 7dc9453edd5df73d440d5a282e372e4afd6aab9b91bb8fddc7768d81c81e8a33
  original_relations_sha256: cd57199b6c95d01fb34375ace936fcaf99bdbcd0a037390664e052d76d10a6da
---
## Summary

Declare Method Spec Policy Form

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Method

class MethodSpecPolicy(Method):
    pass

declare_entity(
    entity_class=MethodSpecPolicy,
    entity_name='Spec Policy',
    qualification_property_path='Atom.Header.Context.Form',
)
```

## Semantics

A Spec Policy governs how to write and review Atoms of the same Role whose main subject is its own main subject or a descendant.