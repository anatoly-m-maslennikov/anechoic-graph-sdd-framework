---
identity:
  atom_id: CA-R-3111
  ref_id: CA-R-3111
context:
  role: requirement
  form: declaration
  container:
    scope_unit: CA-SU-11
  topics:
    main_subject: ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Requirement)/(.Header.Context.Form
      := Solution)
  tier: 3
relations:
  is_replacement_for:
  - CA-R-3002
state:
  version: 1
  status: active
  updated_at: '2026-11-12T20:07:28.479112+00:00'
destination:
  file:
    name: CA-R-3111-CORE_META_MODEL-DECLARATION--declare-requirement-solution-form.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-3111-CORE_META_MODEL-DECLARATION--declare-requirement-solution-form.md
  source_atom_id: CA-R-3111
  source_atom_revision: 1
  source_sha256: 4b776231e7e1dbd43870473f9edabc29f611537c252ab87e92958aa1a0ef5500
  original_relations_sha256: c3f65131a1877f9018993b3df7fa417a88da6def2921c99fedb5a962c4deddcd
---

## Summary

Declare Requirement Solution Form

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Requirement

class RequirementSolution(Requirement):
    pass

declare_entity(
    entity_class=RequirementSolution,
    entity_name='Solution',
    qualification_property_path='Atom.Header.Context.Form',
)
```

## Semantics

A Solution specifies the contribution that realizes a Scope Unit’s responsibility across the unit and its descendants. Its Role identifies the contribution.
