---
identity:
  atom_id: AN-S-2073
context:
  container:
    component: C9
  tier: 1
  lens: DES
state:
  status: active
  version: 8
  updated_at: '2026-11-12T17:23:54+00:00'
---
## Summary

Define Git Branch Carrier

## Claim

### Prose Claim

A Git Branch is a repository-owned Carrier identifying a branch head.

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Carrier

class GitBranch(Carrier):
    pass

declare_entity(entity_class=GitBranch, entity_name='Git Branch')
```

## Semantics

A Git Repository contains its Git Branches; this is containment, not specialization.
