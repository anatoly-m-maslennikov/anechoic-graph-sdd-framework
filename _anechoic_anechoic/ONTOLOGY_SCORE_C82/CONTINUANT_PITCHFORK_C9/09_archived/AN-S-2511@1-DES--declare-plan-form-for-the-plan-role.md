---
atom_family: SPEC
atom_id: AN-S-2511
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 1
  updated_at: "2026-11-25T22:48:40.411349+00:00"
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