---
atom_family: SPEC
atom_id: AN-S-1997
structure:
  container:
    component: C9
  tier: 3
context:
  lens: DES
state:
  status: active
  version: 14
  updated_at: '2026-11-12T17:23:54+00:00'
---
## Summary

Define Entity/Carrier/Directory Carrier

## Claim

### Prose Claim

A Directory Carrier uses a directory to represent its carried Object; containing files alone does not make it a Directory Carrier.
### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Carrier

class Directory(Carrier):
    pass

declare_entity(entity_class=Directory, entity_name='Directory')
```

