---
identity:
  atom_id: AN-S-2072
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

Define Git Commit Carrier

## Claim

### Prose Claim

A Git Commit is an immutable Carrier representing a committed repository snapshot and its commit metadata.

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Carrier

class GitCommit(Carrier):
    pass

declare_entity(entity_class=GitCommit, entity_name='Git Commit')
```

## Semantics

Its native identity is interpreted within its repository context. Author, signer and source facts remain provenance.
