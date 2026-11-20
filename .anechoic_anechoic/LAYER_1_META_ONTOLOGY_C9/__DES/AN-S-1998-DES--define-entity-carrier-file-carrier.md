---
atom_family: SPEC
atom_id: AN-S-1998
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

Define Entity/Carrier/File Carrier

## Claim

### Prose Claim

A File Carrier represents content in a file.
### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Carrier

class File(Carrier):
    pass

declare_entity(entity_class=File, entity_name='File')
```

