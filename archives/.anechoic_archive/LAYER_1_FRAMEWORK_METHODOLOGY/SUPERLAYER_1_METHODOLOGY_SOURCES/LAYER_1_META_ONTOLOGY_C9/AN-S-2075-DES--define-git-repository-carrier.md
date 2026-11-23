---
atom_family: SPEC
atom_id: AN-S-2075
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: active
  version: 9
  updated_at: '2026-11-12T17:23:54+00:00'
---
## Summary

Define Git Repository Carrier

## Claim

### Prose Claim

A Git Repository is a Carrier of versioned content and Git references.

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Carrier

class GitRepository(Carrier):
    pass

declare_entity(entity_class=GitRepository, entity_name='Git Repository')
```

## Semantics

Git Repository contains Git Branches; this is containment, not specialization.
