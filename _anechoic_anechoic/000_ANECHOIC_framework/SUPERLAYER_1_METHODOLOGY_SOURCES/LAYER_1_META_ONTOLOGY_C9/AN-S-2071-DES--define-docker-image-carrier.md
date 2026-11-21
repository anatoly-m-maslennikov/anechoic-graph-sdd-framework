---
atom_family: SPEC
atom_id: AN-S-2071
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

Define Docker Image Carrier

## Claim

### Prose Claim

A Docker Image is an immutable, addressable Carrier of packaged Implementation.
### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Carrier

class DockerImage(Carrier):
    pass

declare_entity(entity_class=DockerImage, entity_name='Docker Image')
```

