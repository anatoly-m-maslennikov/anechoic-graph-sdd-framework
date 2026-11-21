---
atom_family: SPEC
atom_id: AN-S-2206
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 2
  updated_at: '2026-11-13T05:09:05.360312+00:00'
---
## Summary

Declare Scope Unit Declaration Form

## Claim

### Prose Claim

Scope Unit Declaration is a Requirement Form. Its active Subject identifies one Scope Unit within the Project. Its Formal Claim states the unit’s stable ID, Name and ordering state. It states order.number when ordered. Label is optional. A non-Project Declaration states the unit’s direct Parent. The Project Declaration identifies the Project root and its unordered state.

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Requirement

class ScopeUnitDeclaration(Requirement):
    pass

declare_entity(
    entity_name="Scope Unit Declaration",
    entity_class=ScopeUnitDeclaration,
    qualification_property_path="Atom.Header.Context.Form",
    instance_relation_constraints={"HAS_ACTIVE_SUBJECT": {"target_entity_paths": ("Scope Unit",)}},
)
```
