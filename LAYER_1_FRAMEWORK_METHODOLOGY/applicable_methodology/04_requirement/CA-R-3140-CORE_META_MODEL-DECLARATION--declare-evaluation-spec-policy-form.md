---
identity:
  atom_id: CA-R-3140
  ref_id: CA-R-3140
context:
  role: requirement
  form: declaration
  container:
    scope_unit: CA-SU-11
  tier: 3
  topics:
    main_subject: CAPRMEDIO_MODEL <+ Atom/(.Header.Context.Role := Evaluation)/(.Header.Context.Form
      := Spec Policy)
relations:
  IS_REPLACEMENT_FOR:
  - CA-R-3123
state:
  version: 1
  status: active
  updated_at: '2026-11-13T15:39:40.855648+00:00'
destination:
  file:
    name: CA-R-3140-CORE_META_MODEL-DECLARATION--declare-evaluation-spec-policy-form.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
projection:
  source_carrier_path: ../../../.caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-3140-CORE_META_MODEL-DECLARATION--declare-evaluation-spec-policy-form.md
  source_atom_id: CA-R-3140
  source_atom_revision: 1
  source_sha256: 9dadf1a23d99863f7fe9b555983f17e4188f12804275cd39724c5419bcb7ba6c
  original_relations_sha256: eb426a3de66f55bcf31a15d6c06d27e7345f4dc7a1919e5a7da92953f29a598a
---
## Summary

Declare Evaluation Spec Policy Form

## Claim

### Formal Claim

```python
from caprmedio.formal_claims import declare_entity
from caprmedio.model import Evaluation

class EvaluationSpecPolicy(Evaluation):
    pass

declare_entity(
    entity_class=EvaluationSpecPolicy,
    entity_name='Spec Policy',
    qualification_property_path='Atom.Header.Context.Form',
)
```

## Semantics

A Spec Policy governs how to write and review Atoms of the same Role whose main subject is its own main subject or a descendant.