---
atom_family: SPEC
atom_id: AN-S-1998
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 14
  updated_at: "2026-11-25T19:32:47.527524+00:00"
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

