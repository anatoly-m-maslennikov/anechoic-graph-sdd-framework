---
identity:
  atom_id: CA-R-3155
  ref_id: CA-R-3155
context:
  role: requirement
  form: declaration
  container:
    scope_unit: CA-SU-11
  tier: 3
  topics:
    main_subject: CAPRMEDIO_MODEL <+ Atom/(.Header.Context.Role := Plan)/(.Header.Context.Form
      := Plan)
state:
  version: 1
  status: active
  updated_at: '2026-11-13T19:02:07.182336+00:00'
destination:
  file:
    name: CA-R-3155-CORE_META_MODEL-DECLARATION--declare-plan-form-for-the-plan-role.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
projection:
  source_carrier_path: ../../../.caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-3155-CORE_META_MODEL-DECLARATION--declare-plan-form-for-the-plan-role.md
  source_atom_id: CA-R-3155
  source_atom_revision: 1
  source_sha256: 82164b1358b22f3a9f49ce0c657b543f1931eb398625ac8f7f7faeb15427d519
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Declare Plan Form for the Plan Role

## Claim

### Formal Claim

```python
from caprmedio.formal_claims import declare_entity
from caprmedio.model import Plan

class PlanForm(Plan):
    pass

declare_entity(
    entity_class=PlanForm,
    entity_name='Plan',
    qualification_property_path='Atom.Header.Context.Form',
)
```

## Semantics

Plan is the Form for intended work or an intended outcome. Labels distinguish Plans such as Epics and Tasks.