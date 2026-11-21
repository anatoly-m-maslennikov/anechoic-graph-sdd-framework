---
atom_family: SPEC
atom_id: AN-S-2074
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: active
  version: 8
  updated_at: '2026-11-12T17:23:54+00:00'
---
## Summary

Define Pull Request Carrier

## Claim

### Prose Claim

A Pull Request is a repository-hosted Carrier of a proposed change and its review state.
### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Carrier

class PullRequest(Carrier):
    pass

declare_entity(entity_class=PullRequest, entity_name='Pull Request')
```

