---
identity:
  atom_id: AN-S-2511
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: active
  version: 1
  updated_at: '2026-11-13T19:02:07.182336+00:00'
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