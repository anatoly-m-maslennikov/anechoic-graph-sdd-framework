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
    main_subject: ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Plan)/(.Header.Context.Form
      := Plan)
state:
  version: 1
  status: active
  updated_at: '2026-11-13T19:02:07.182336+00:00'
destination:
  file:
    name: CA-R-3155-CORE_META_MODEL-DECLARATION--declare-plan-form-for-the-plan-role.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
---
## Summary

Declare Plan Form for the Plan Role

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Plan

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