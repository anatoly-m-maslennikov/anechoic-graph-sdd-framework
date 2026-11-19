---
identity:
  atom_id: CA-R-3143
  ref_id: CA-R-3143
context:
  role: requirement
  form: declaration
  container:
    scope_unit: CA-SU-11
  tier: 3
  topics:
    main_subject: ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Evaluation)/(.Header.Context.Form
      := Eng Standard)
relations:
  IS_REPLACEMENT_FOR:
  - CA-R-3118
state:
  version: 1
  status: active
  updated_at: '2026-11-13T15:39:56.937089+00:00'
destination:
  file:
    name: CA-R-3143-CORE_META_MODEL-DECLARATION--declare-evaluation-eng-standard-form.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-3143-CORE_META_MODEL-DECLARATION--declare-evaluation-eng-standard-form.md
  source_atom_id: CA-R-3143
  source_atom_revision: 1
  source_sha256: ca7434965e74a8becf6d9520d7480d6e2e5662c056c896ffeb9aea2e8f600a8a
  original_relations_sha256: c6f1c5a02542467f0cbb63263e25611253e4a005e424ba6e0dcfc2433c623a21
---
## Summary

Declare Evaluation Eng Standard Form

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Evaluation

class EvaluationEngStandard(Evaluation):
    pass

declare_entity(
    entity_class=EvaluationEngStandard,
    entity_name='Eng Standard',
    qualification_property_path='Atom.Header.Context.Form',
)
```

## Semantics

An Eng Standard applies directly to implementation within its owning Scope Unit and descendant Scope Units where its Claim applies.