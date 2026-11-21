---
atom_family: SPEC
atom_id: AN-S-2059
structure:
  container:
    component: C9
  tier: 3
context:
  lens: DES
state:
  status: active
  version: 7
  updated_at: '2026-11-12T17:23:54+00:00'
---
## Summary

Declare Term Definition as a Method Form

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Method

class TermDefinition(Method):
    pass

declare_entity(entity_class=TermDefinition, entity_name='Term Definition', qualification_property_path="Atom.Header.Context.Form")
```
