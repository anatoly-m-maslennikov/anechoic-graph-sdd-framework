---
atom_family: SPEC
atom_id: AN-S-2205
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 4
  updated_at: "2026-11-25T22:48:40.712484+00:00"
---
## Summary

Declare Requirement Form

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Requirement


class RequirementForm(Requirement):
    pass


declare_entity(
    entity_name="Requirement",
    entity_class=RequirementForm,
    qualification_property_path="Atom.Header.Context.Form",
)
```

## Semantics

A Requirement Form states a local required outcome, behavior, property or constraint.
